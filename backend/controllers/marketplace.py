"""
Marketplace controller — mounted at /api/marketplace.
All endpoints delegate business logic processing to the MarketplaceService.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from core.auth import verify_token
from schemas.marketplace import (
    CheckoutResponse,
    ListingCreatedResponse,
    ListingResponse,
    ListItemRequest,
    SettleResponse,
    UpdateListingRequest,
)
from services.marketplace import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _serialize_listing_row(row) -> ListingResponse:
    # Handle dict (returned by browse_listings) or MarketplaceListing model instance
    if isinstance(row, dict):
        return ListingResponse(**row)

    return ListingResponse(
        listing_id=str(row.id),
        item_id=str(row.item_id) if row.item_id else None,
        seller_id=row.seller_id,
        buyer_id=row.buyer_id,
        title=row.title,
        description=row.description,
        category=row.category,
        price_usdc=float(row.price_usdc),
        status=row.status,
        transaction_id=row.transaction_id,
        created_at=row.created_at.isoformat() if row.created_at else None,
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
    """List an item for sale on the marketplace."""
    seller_id = token_payload["sub"]
    service = MarketplaceService()
    listing_id = await service.list_item(
        seller_id=seller_id,
        title=body.title,
        category=body.category,
        price_usdc=body.price_usdc,
        description=body.description,
        item_id=body.item_id,
    )
    return ListingCreatedResponse(listing_id=listing_id)


# PATCH /marketplace/{listing_id}
@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: str,
    body: UpdateListingRequest,
    token_payload: dict = Depends(verify_token),
):
    """Update title, price, description, or status of a listing (seller only)."""
    seller_id = token_payload["sub"]
    service = MarketplaceService()
    listing = await service.update_listing(
        listing_id=listing_id, seller_id=seller_id, body=body
    )
    return _serialize_listing_row(listing)


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
    """Fetch all active listings."""
    service = MarketplaceService()
    rows = await service.browse_listings(category=category, q=q)
    return [_serialize_listing_row(row) for row in rows]


# GET /marketplace/{listing_id}
@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: str):
    """Fetch details of a specific listing (no auth required)."""
    service = MarketplaceService()
    listing = await service.get_listing(listing_id)
    return _serialize_listing_row(listing)


# POST /marketplace/checkout/{listing_id}
@router.post("/checkout/{listing_id}", response_model=CheckoutResponse)
async def checkout(
    listing_id: str,
    token_payload: dict = Depends(verify_token),
):
    """Initiate a Unifold Sandbox checkout session as the buyer."""
    buyer_id = token_payload["sub"]
    service = MarketplaceService()
    checkout_url = await service.checkout(
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
    """Mark as received and trigger escrow payout to the seller (buyer only)."""
    buyer_id = token_payload["sub"]
    service = MarketplaceService()
    await service.settle_purchase(listing_id=listing_id, buyer_id=buyer_id)
    return SettleResponse(
        listing_id=listing_id,
        status="sold",
        message="Settlement successful. Payout initiated to seller.",
    )
