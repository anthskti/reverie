from datetime import datetime

from sqlalchemy import Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserStats(Base):
    """Cumulative environmental impact stats per user.

    Keyed by user_id (string, matching Auth0 sub claim).
    No FK to a users table — this is a standalone counter that can exist
    before auth is wired up.
    """

    __tablename__ = "user_stats"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    water_saved_l: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    co2_offset_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    landfill_diverted_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
