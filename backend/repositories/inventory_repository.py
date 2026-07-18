import uuid
from typing import Any

from sqlalchemy import func, select

from database import SessionLocal
from models import Item
from models.user_stats import UserStats


class InventoryRepository:
    async def get_global_stats(self) -> dict[str, float]:
        """Aggregate stats across all users."""
        if SessionLocal is None:
            return {
                "total_water_saved_l": 0.0,
                "total_co2_offset_kg": 0.0,
                "total_landfill_diverted_kg": 0.0,
            }

        async with SessionLocal() as session:
            result = await session.execute(
                select(
                    func.sum(UserStats.water_saved_l),
                    func.sum(UserStats.co2_offset_kg),
                    func.sum(UserStats.landfill_diverted_kg),
                )
            )
            row = result.first()
            if not row:
                return {
                    "total_water_saved_l": 0.0,
                    "total_co2_offset_kg": 0.0,
                    "total_landfill_diverted_kg": 0.0,
                }
                
            return {
                "total_water_saved_l": float(row[0] or 0.0),
                "total_co2_offset_kg": float(row[1] or 0.0),
                "total_landfill_diverted_kg": float(row[2] or 0.0),
            }

    async def get_user_stats(self, user_id: str) -> UserStats:
        """Fetch or lazily create a user's stats row."""
        if SessionLocal is None:
            # Fallback for offline mode without a DB
            return UserStats(
                user_id=user_id,
                water_saved_l=0.0,
                co2_offset_kg=0.0,
                landfill_diverted_kg=0.0,
            )

        async with SessionLocal() as session:
            stats = await session.get(UserStats, user_id)
            if not stats:
                # Lazy creation of user profile/stats entry upon first fetch
                stats = UserStats(
                    user_id=user_id,
                    water_saved_l=0.0,
                    co2_offset_kg=0.0,
                    landfill_diverted_kg=0.0,
                )
                session.add(stats)
                await session.commit()
                # Refresh to get the generated updated_at timestamp
                await session.refresh(stats)
            return stats

    async def get_user_items(self, user_id: str) -> list[Item]:
        """Fetch all physical items belonging to a user."""
        if SessionLocal is None:
            return []

        async with SessionLocal() as session:
            result = await session.execute(
                select(Item).where(Item.user_id == user_id).order_by(Item.created_at.desc())
            )
            return list(result.scalars().all())

    async def get_item(self, item_id: str, user_id: str) -> Item | None:
        """Fetch a specific item belonging to a user."""
        if SessionLocal is None:
            return None

        try:
            parsed_uuid = uuid.UUID(item_id)
        except ValueError:
            return None

        async with SessionLocal() as session:
            result = await session.execute(
                select(Item).where(Item.id == parsed_uuid, Item.user_id == user_id)
            )
            return result.scalar_one_or_none()
