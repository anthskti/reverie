"""Pydantic schemas for the marketplace subsystem."""

from __future__ import annotations

from pydantic import BaseModel, Field

VALID_CATEGORIES = {"upcycled_clothing", "material", "tool"}


# Request bodies

class ListItemRequest(BaseModel):
    title: str = Field(description="Display title for the listing")
    description: str | None = Field(
        default=None, description="Optional seller description"
    )
    price_usdc: float = Field(gt=0, description="Asking price in USDC")
    category: str = Field(
        description="One of: upcycled_clothing, material, tool"
    )
    # Required for upcycled_clothing; optional/ignored for material & tool
    item_id: str | None = Field(
        default=None,
        description="Inventory item UUID. Required when category is upcycled_clothing.",
    )

    def validate_category(self) -> None:
        if self.category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{self.category}'. Must be one of: {VALID_CATEGORIES}"
            )


class UpdateListingRequest(BaseModel):
    title: str | None = Field(default=None, description="Updated title")
    price_usdc: float | None = Field(
        default=None, gt=0, description="New asking price in USDC"
    )
    description: str | None = Field(
        default=None, description="Updated seller description"
    )
    # Sellers can only cancel a listing directly; all other transitions are
    # driven by the checkout / webhook / settle flow.
    status: str | None = Field(
        default=None,
        description="Set to 'cancelled' to withdraw the listing.",
    )


# Response shapes

class ListingCreatedResponse(BaseModel):
    listing_id: str


class DepositSession(BaseModel):
    """Connect-shaped deposit params for the local Unifold sandbox UI."""

    mode: str = "sandbox"
    session_id: str
    external_user_id: str
    recipient_address: str
    destination_chain_type: str
    destination_chain_id: str
    destination_token_address: str
    destination_token_symbol: str
    amount_usdc: float
    listing_id: str
    seller_id: str


class CheckoutResponse(BaseModel):
    listing_id: str
    status: str  # pending_payment
    mode: str = "sandbox"
    deposit: DepositSession


class ConfirmPaymentResponse(BaseModel):
    listing_id: str
    status: str  # locked_in_escrow
    transaction_id: str
    message: str


class ListingResponse(BaseModel):
    listing_id: str
    item_id: str | None = None
    seller_id: str
    buyer_id: str | None = None
    title: str
    description: str | None = None
    category: str
    price_usdc: float
    status: str
    transaction_id: str | None = None
    # Populated only for upcycled_clothing listings (from items JOIN)
    item_style: str | None = None
    item_type: str | None = None
    item_image_url: str | None = None
    created_at: str | None = None


class SettleResponse(BaseModel):
    listing_id: str
    status: str
    message: str
