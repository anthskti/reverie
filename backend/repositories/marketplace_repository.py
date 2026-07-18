"""Persistence layer for the marketplace subsystem."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update

from database import SessionLocal
from models import Item, MarketplaceListing


class MarketplaceRepository:
    @property
    def db_enabled(self) -> bool:
        return SessionLocal is not None

    # ------------------------------------------------------------------ #
    # Listings                                                             #
    # ------------------------------------------------------------------ #

    async def create_listing(
        self,
        seller_id: str,
        title: str,
        category: str,
        price_usdc: float,
        description: str | None = None,
        item_id: str | None = None,
    ) -> str:
        """Insert a new active listing. Returns the new listing UUID string."""
        listing_id = str(uuid.uuid4())
        if SessionLocal is None:
            return listing_id

        async with SessionLocal() as session:
            listing = MarketplaceListing(
                id=uuid.UUID(listing_id),
                item_id=uuid.UUID(item_id) if item_id else None,
                seller_id=seller_id,
                title=title,
                category=category,
                price_usdc=price_usdc,
                status="active",
                description=description,
            )
            session.add(listing)
            await session.commit()
            return str(listing.id)

    async def get_listing(self, listing_id: str) -> MarketplaceListing | None:
        """Fetch a listing by ID (no ownership filter)."""
        if SessionLocal is None:
            return None

        async with SessionLocal() as session:
            result = await session.execute(
                select(MarketplaceListing).where(
                    MarketplaceListing.id == uuid.UUID(listing_id)
                )
            )
            return result.scalar_one_or_none()

    async def get_listing_owned_by(
        self, listing_id: str, seller_id: str
    ) -> MarketplaceListing | None:
        """Fetch a listing only if it belongs to seller_id."""
        if SessionLocal is None:
            return None

        async with SessionLocal() as session:
            result = await session.execute(
                select(MarketplaceListing).where(
                    MarketplaceListing.id == uuid.UUID(listing_id),
                    MarketplaceListing.seller_id == seller_id,
                )
            )
            return result.scalar_one_or_none()

    async def list_listings(
        self,
        category: str | None = None,
        q: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return active listings with optional filters.

        Filters:
        - category: one of upcycled_clothing | material | tool
        - q: text search across title + description

        A LEFT OUTER JOIN is used so material/tool listings (which have no
        item_id) are still returned.
        """
        if SessionLocal is None:
            return []

        async with SessionLocal() as session:
            stmt = (
                select(MarketplaceListing, Item)
                .outerjoin(Item, MarketplaceListing.item_id == Item.id)
                .where(MarketplaceListing.status == "active")
            )

            if category:
                stmt = stmt.where(MarketplaceListing.category == category)
            if q:
                stmt = stmt.where(
                    MarketplaceListing.title.ilike(f"%{q}%")
                    | MarketplaceListing.description.ilike(f"%{q}%")
                )

            result = await session.execute(
                stmt.order_by(MarketplaceListing.created_at.desc())
            )
            rows = result.all()

        return [_serialize_listing(listing, item) for listing, item in rows]

    async def update_listing(
        self,
        listing_id: str,
        seller_id: str,
        price_usdc: float | None = None,
        description: str | None = None,
        title: str | None = None,
        status: str | None = None,
    ) -> MarketplaceListing | None:
        """PATCH a listing. Only the owning seller may update it.

        Returns the updated listing, or None if not found / not owned.
        """
        if SessionLocal is None:
            return None

        async with SessionLocal() as session:
            listing = (
                await session.execute(
                    select(MarketplaceListing).where(
                        MarketplaceListing.id == uuid.UUID(listing_id),
                        MarketplaceListing.seller_id == seller_id,
                    )
                )
            ).scalar_one_or_none()

            if listing is None:
                return None

            if price_usdc is not None:
                listing.price_usdc = price_usdc
            if description is not None:
                listing.description = description
            if title is not None:
                listing.title = title
            if status is not None:
                listing.status = status

            await session.commit()
            await session.refresh(listing)
            return listing

    async def set_listing_status(self, listing_id: str, status: str) -> None:
        """Unconditionally set status (used by webhook & settle)."""
        if SessionLocal is None:
            return

        async with SessionLocal() as session:
            await session.execute(
                update(MarketplaceListing)
                .where(MarketplaceListing.id == uuid.UUID(listing_id))
                .values(status=status)
            )
            await session.commit()

    async def record_checkout(self, listing_id: str, buyer_id: str) -> None:
        """Lock in the buyer and move the listing to pending_payment.

        Called immediately after a Unifold checkout session is created so we
        know who initiated payment before the webhook fires.
        """
        if SessionLocal is None:
            return

        async with SessionLocal() as session:
            await session.execute(
                update(MarketplaceListing)
                .where(MarketplaceListing.id == uuid.UUID(listing_id))
                .values(buyer_id=buyer_id, status="pending_payment")
            )
            await session.commit()

    async def record_payout(self, listing_id: str, transaction_id: str) -> None:
        """Persist the Unifold transaction hash after payout.settled fires."""
        if SessionLocal is None:
            return

        async with SessionLocal() as session:
            await session.execute(
                update(MarketplaceListing)
                .where(MarketplaceListing.id == uuid.UUID(listing_id))
                .values(transaction_id=transaction_id)
            )
            await session.commit()

# Helpers
def _serialize_listing(
    listing: MarketplaceListing, item: Item | None
) -> dict[str, Any]:
    return {
        "listing_id": str(listing.id),
        "item_id": str(listing.item_id) if listing.item_id else None,
        "seller_id": listing.seller_id,
        "buyer_id": listing.buyer_id,
        "title": listing.title,
        "description": listing.description,
        "category": listing.category,
        "price_usdc": float(listing.price_usdc),
        "status": listing.status,
        "transaction_id": listing.transaction_id,
        # item fields — only present for upcycled_clothing listings
        "item_style": item.style if item else None,
        "item_type": item.item_type if item else None,
        "item_image_url": item.original_image_url if item else None,
        "created_at": (
            listing.created_at.isoformat() if listing.created_at else None
        ),
    }
