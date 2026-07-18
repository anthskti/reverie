import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    selected_concept: Mapped[dict] = mapped_column(JSONB, nullable=False)
    sewing_guide: Mapped[str | None] = mapped_column(Text, nullable=True)
    environmental_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    environmental_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        Index("idx_projects_user_id", "user_id"),
        Index("idx_projects_item_id", "item_id"),
    )

