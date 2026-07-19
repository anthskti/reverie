import uuid
from datetime import datetime

from sqlalchemy import Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

# Valid listing categories
LISTING_CATEGORIES = {"upcycled_clothing", "material", "tool"}

# Status lifecycle:
#   active → pending_payment → locked_in_escrow → sold
#                            ↘ cancelled (seller cancels before payment)


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # item_id is optional — material/tool listings don't require an inventory item
    item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    seller_id: Mapped[str] = mapped_column(String, nullable=False)
    # buyer_id is recorded at checkout time; null until then
    buyer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Direct image for tool/material listings (upcycled_clothing uses item join)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)  # see LISTING_CATEGORIES
    price_usdc: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="active"
    )
    # Unifold transaction hash recorded after payout.settled webhook
    transaction_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_marketplace_seller_id", "seller_id"),
        Index("idx_marketplace_item_id", "item_id"),
        Index("idx_marketplace_status", "status"),
        Index("idx_marketplace_category", "category"),
    )
