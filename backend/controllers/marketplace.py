"""Marketplace controller — mounted at /api/marketplace.

Endpoints
---------
POST   /api/marketplace/list                    List an item for sale
PATCH  /api/marketplace/{listing_id}            Update a listing (seller only)
GET    /api/marketplace                         Browse active listings
GET    /api/marketplace/{listing_id}            Fetch a single listing
POST   /api/marketplace/checkout/{listing_id}   Initiate Unifold checkout (buyer)
POST   /api/marketplace/settle/{listing_id}     Mark as received, release escrow (buyer)

Status lifecycle
----------------
active → pending_payment → locked_in_escrow → sold
       ↘ cancelled (seller cancels before any payment)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.auth import verify_token
from repositories.inventory_repository import InventoryRepository
from repositories.marketplace_repository import MarketplaceRepository
from schemas.marketplace import (
    CheckoutResponse,
    ListingCreatedResponse,
    ListingResponse,
    ListItemRequest,
    SettleResponse,
    UpdateListingRequest,
    VALID_CATEGORIES,
)
from services import unifold as unifold_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

_inventory_repo = InventoryRepository()
_marketplace_repo = MarketplaceRepository()

# Statuses a seller may set directly via PATCH (all other transitions are
# driven by the checkout / webhook / settle flow).
_SELLER_ALLOWED_STATUSES = {"cancelled"}



# Helpers
def _listing_to_response(listing) -> ListingResponse:
    return ListingResponse(
        listing_id=str(listing.id),
        item_id=str(listing.item_id) if listing.item_id else None,
        seller_id=listing.seller_id,
        buyer_id=listing.buyer_id,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        price_usdc=float(listing.price_usdc),
        status=listing.status,
        transaction_id=listing.transaction_id,
        created_at=listing.created_at.isoformat() if listing.created_at else None,
    )


# POST /marketplace/list
@router.post(
    "/list",
    response_model=ListingCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def list_item(
    body: ListItemRequest,
    token_payload: dict = Depends(verify_token),
):
    """List an item for sale on the marketplace.

    **Category rules:**

    * ``upcycled_clothing`` — requires a valid ``item_id`` that the seller
      owns in their inventory. The QC verification score is informational
      only and does **not** gate listing eligibility.
    * ``material`` / ``tool`` — ``item_id`` is optional; these listings
      represent raw supplies and bypass inventory checks entirely.
    """
    seller_id = token_payload["sub"]

    # Validate category
    if body.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{body.category}'. Must be one of: {sorted(VALID_CATEGORIES)}.",
        )

    item_id: str | None = None

    if body.category == "upcycled_clothing":
        if not body.item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="item_id is required for upcycled_clothing listings.",
            )
        # Ownership check: the item must belong to the requesting user.
        item = await _inventory_repo.get_item(body.item_id, seller_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found or does not belong to you.",
            )
        item_id = body.item_id
    # material / tool: no inventory item required

    listing_id = await _marketplace_repo.create_listing(
        seller_id=seller_id,
        title=body.title,
        category=body.category,
        price_usdc=body.price_usdc,
        description=body.description,
        item_id=item_id,
    )

    return ListingCreatedResponse(listing_id=listing_id)


# PATCH /marketplace/{listing_id}
@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: str,
    body: UpdateListingRequest,
    token_payload: dict = Depends(verify_token),
):
    """Update title, price, description, or status of a listing.

    Only the seller who created the listing may call this endpoint.
    The only status value a seller may set directly is ``cancelled``.
    """
    seller_id = token_payload["sub"]

    if body.status is not None and body.status not in _SELLER_ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status '{body.status}'. "
                f"Sellers may only set: {_SELLER_ALLOWED_STATUSES}."
            ),
        )

    listing = await _marketplace_repo.update_listing(
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

    return _listing_to_response(listing)


# GET /marketplace
@router.get("", response_model=list[ListingResponse])
async def browse_listings(
    category: str | None = Query(
        default=None,
        description="Filter by category: upcycled_clothing | material | tool",
    ),
    q: str | None = Query(
        default=None,
        description="Full-text search across listing title and description",
    ),
):
    """Fetch all active listings.

    ``status == 'sold'`` items are excluded; the frontend can badge
    ``pending_payment`` and ``locked_in_escrow`` items appropriately.
    """
    rows = await _marketplace_repo.list_listings(category=category, q=q)
    return [ListingResponse(**row) for row in rows]


# GET /marketplace/{listing_id}
@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: str):
    """Fetch details of a specific listing (no auth required)."""
    listing = await _marketplace_repo.get_listing(listing_id)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found.",
        )
    return _listing_to_response(listing)


# POST /marketplace/checkout/{listing_id}
@router.post("/checkout/{listing_id}", response_model=CheckoutResponse)
async def checkout(
    listing_id: str,
    token_payload: dict = Depends(verify_token),
):
    """Initiate a Unifold Sandbox checkout session as the buyer.

    1. Verifies the listing is ``active``.
    2. Generates a Unifold checkout URL / invoice for ``price_usdc``.
    3. Locks in the buyer and advances listing to ``pending_payment``.

    The buyer is then redirected to the returned ``checkout_url`` to complete
    payment. Once paid, Unifold fires ``deposit.settled`` to our webhook which
    advances the listing to ``locked_in_escrow`` — signalling the seller to ship.
    """
    buyer_id = token_payload["sub"]

    listing = await _marketplace_repo.get_listing(listing_id)
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
        logger.error("Unifold checkout creation failed for listing %s: %s", listing_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create checkout session: {exc}",
        ) from exc

    # Record the buyer and advance status atomically
    await _marketplace_repo.record_checkout(
        listing_id=listing_id, buyer_id=buyer_id
    )

    return CheckoutResponse(
        listing_id=listing_id,
        checkout_url=checkout_url,
        status="pending_payment",
    )


# POST /marketplace/settle/{listing_id}
@router.post("/settle/{listing_id}", response_model=SettleResponse)
async def settle_purchase(
    listing_id: str,
    token_payload: dict = Depends(verify_token),
):
    """Called by the buyer after the physical item has arrived.

    1. Verifies the listing is in ``locked_in_escrow`` status.
    2. Verifies the calling user is the recorded buyer.
    3. Triggers the Unifold Payout API to release escrowed USDC to the seller.
    4. Marks the listing as ``sold``.

    Note: item ownership in the inventory is **not** transferred — the
    verified QC score is an independent grading feature, not a transfer gate.
    """
    buyer_id = token_payload["sub"]

    listing = await _marketplace_repo.get_listing(listing_id)
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

    # Trigger payout — non-fatal if Unifold is offline; webhook will confirm later.
    try:
        await unifold_service.trigger_payout(
            listing_id=listing_id,
            seller_id=listing.seller_id,
            amount_usdc=float(listing.price_usdc),
        )
    except Exception as exc:
        logger.error("Unifold payout failed for listing %s: %s", listing_id, exc)
        # Don't block the buyer — payout can be retried via the webhook.

    await _marketplace_repo.set_listing_status(listing_id, "sold")

    return SettleResponse(
        listing_id=listing_id,
        status="sold",
        message="Settlement successful. Payout initiated to seller.",
    )
