import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    original_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    style: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String, nullable=True)
    fabric_type: Mapped[str | None] = mapped_column(String, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    item_type: Mapped[str] = mapped_column(
        String, nullable=False, server_default="finished_garment"
    )
    is_market_eligible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (Index("idx_items_user_id", "user_id"),)

