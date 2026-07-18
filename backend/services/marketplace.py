from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Any
from fastapi import HTTPException, status

from repositories.inventory_repository import InventoryRepository
from repositories.marketplace_repository import MarketplaceRepository
from services import unifold as unifold_service
from schemas.marketplace import UpdateListingRequest, VALID_CATEGORIES

logger = logging.getLogger(__name__)


class MarketplaceService:
    def __init__(
        self,
        marketplace_repo: MarketplaceRepository | None = None,
        inventory_repo: InventoryRepository | None = None,
    ) -> None:
        self.marketplace_repo = marketplace_repo or MarketplaceRepository()
        self.inventory_repo = inventory_repo or InventoryRepository()

    async def list_item(
        self,
        seller_id: str,
        title: str,
        category: str,
        price_usdc: float,
        description: str | None,
        item_id: str | None,
    ) -> str:
        """Handle listing logic: category checks, ownership validation, creation."""
        if category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category '{category}'. Must be one of: {sorted(VALID_CATEGORIES)}.",
            )

        validated_item_id: str | None = None

        if category == "upcycled_clothing":
            if not item_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="item_id is required for upcycled_clothing listings.",
                )
            item = await self.inventory_repo.get_item(item_id, seller_id)
            if item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found or does not belong to you.",
                )
            validated_item_id = item_id

        return await self.marketplace_repo.create_listing(
            seller_id=seller_id,
            title=title,
            category=category,
            price_usdc=price_usdc,
            description=description,
            item_id=validated_item_id,
        )

    async def update_listing(
        self, listing_id: str, seller_id: str, body: UpdateListingRequest
    ) -> Any:
        """Update price, description, title, or status (cancelled) of a listing."""
        allowed_seller_statuses = {"cancelled"}
        if body.status is not None and body.status not in allowed_seller_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid status '{body.status}'. "
                    f"Sellers may only set: {allowed_seller_statuses}."
                ),
            )

        listing = await self.marketplace_repo.update_listing(
            listing_id=listing_id,
            seller_id=seller_id,
            price_usdc=body.price_usdc,
            description=body.description,
            title=body.title,
            status=body.status,
        )
        if listing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found or does not belong to you.",
            )
        return listing

    async def browse_listings(
        self, category: str | None, q: str | None
    ) -> list[dict[str, Any]]:
        """Fetch all active listings by category or search query."""
        return await self.marketplace_repo.list_listings(category=category, q=q)

    async def get_listing(self, listing_id: str) -> Any:
        """Retrieve details of a single listing."""
        listing = await self.marketplace_repo.get_listing(listing_id)
        if listing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found.",
            )
        return listing

    async def checkout(self, listing_id: str, buyer_id: str) -> str:
        """Generate a checkout session and advance listing status."""
        listing = await self.marketplace_repo.get_listing(listing_id)
        if listing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found.",
            )

        if listing.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Listing is in status '{listing.status}' and cannot be purchased. "
                    "Only active listings can be checked out."
                ),
            )

        if listing.seller_id == buyer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot purchase your own listing.",
            )

        try:
            checkout_url = await unifold_service.create_checkout(
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=listing.seller_id,
                amount_usdc=float(listing.price_usdc),
            )
        except Exception as exc:
            logger.error(
                "Unifold checkout creation failed for listing %s: %s",
                listing_id,
                exc,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to create checkout session: {exc}",
            ) from exc

        await self.marketplace_repo.record_checkout(
            listing_id=listing_id, buyer_id=buyer_id
        )
        return checkout_url

    async def settle_purchase(self, listing_id: str, buyer_id: str) -> None:
        """Mark item received and release escrowed payout to the seller."""
        listing = await self.marketplace_repo.get_listing(listing_id)
        if listing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found.",
            )

        if listing.status != "locked_in_escrow":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Listing is in status '{listing.status}'. "
                    "Settlement requires status 'locked_in_escrow' — "
                    "payment must complete first."
                ),
            )

        if listing.buyer_id != buyer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the buyer who initiated checkout may settle this listing.",
            )

        try:
            await unifold_service.trigger_payout(
                listing_id=listing_id,
                seller_id=listing.seller_id,
                amount_usdc=float(listing.price_usdc),
            )
        except Exception as exc:
            logger.error(
                "Unifold payout failed for listing %s: %s", listing_id, exc
            )

        await self.marketplace_repo.set_listing_status(listing_id, "sold")


class WebhookService:
    def __init__(
        self, marketplace_repo: MarketplaceRepository | None = None
    ) -> None:
        self.marketplace_repo = marketplace_repo or MarketplaceRepository()
        self.webhook_secret = os.getenv("UNIFOLD_WEBHOOK_SECRET", "")

    def verify_signature(
        self, raw_body: bytes, signature_header: str | None
    ) -> None:
        """Raise HTTP 401 if the HMAC-SHA256 signature does not match."""
        if not self.webhook_secret:
            logger.warning(
                "UNIFOLD_WEBHOOK_SECRET not configured, skipping signature verification."
            )
            return

        if not signature_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Unifold-Signature header.",
            )

        expected = hmac.new(
            self.webhook_secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected, signature_header):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature.",
            )

    async def handle_webhook(self, payload: dict[str, Any]) -> dict[str, str]:
        """Dispatch webhook events: deposit.settled, payout.settled."""
        event_type: str = payload.get("event_type", "")
        transaction_id: str | None = payload.get("transaction_id")
        metadata: dict = payload.get("metadata", {})
        listing_id: str | None = metadata.get("listing_id")

        if not listing_id:
            logger.error("Unifold webhook missing metadata.listing_id: %s", payload)
            return {
                "status": "ok",
                "message": "Missing listing_id in metadata, ignored.",
            }

        if event_type == "deposit.settled":
            listing = await self.marketplace_repo.get_listing(listing_id)
            if listing is None:
                logger.warning(
                    "deposit.settled: listing %s not found — ignoring.", listing_id
                )
                return {"status": "ok", "message": "Listing not found, ignoring."}

            await self.marketplace_repo.set_listing_status(
                listing_id, "locked_in_escrow"
            )
            logger.info(
                "deposit.settled: listing %s → locked_in_escrow (tx: %s)",
                listing_id,
                transaction_id,
            )

        elif event_type == "payout.settled":
            if transaction_id:
                await self.marketplace_repo.record_payout(
                    listing_id=listing_id, transaction_id=transaction_id
                )
                logger.info(
                    "payout.settled: listing %s, tx_hash=%s recorded.",
                    listing_id,
                    transaction_id,
                )
            else:
                logger.warning(
                    "payout.settled received without transaction_id for listing %s.",
                    listing_id,
                )
        else:
            logger.info(
                "Unifold webhook: unhandled event_type '%s' for listing %s — ignoring.",
                event_type,
                listing_id,
            )

        return {"status": "ok"}
