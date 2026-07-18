"""Persistence for the upcycling pipeline.

- Image storage uses Supabase Storage when a client is configured, otherwise
  it returns local placeholder URLs so the pipeline stays runnable offline.
- Structured data (items, projects) is persisted to Postgres through the
  session pooler via async SQLAlchemy sessions.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from supabase import Client

from database import SessionLocal
from models import Item, Project
from models.user_stats import UserStats


class UpcycleRepository:
    def __init__(self, storage_client: Client | None):
        self.storage_client = storage_client

    @property
    def storage_enabled(self) -> bool:
        return self.storage_client is not None

    @property
    def db_enabled(self) -> bool:
        return SessionLocal is not None

    # Storage (Supabase, sync)

    def upload_inventory_image(
        self,
        user_id: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> tuple[str, str]:
        """Upload an inventory image. Returns (item_id, public_url_or_path)."""
        item_id = str(uuid.uuid4())
        extension = "jpg" if mime_type == "image/jpeg" else mime_type.split("/")[-1]
        
        if not self.storage_client:
            import os
            # Save to local static directory
            static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
            os.makedirs(os.path.join(static_dir, "inventory", user_id), exist_ok=True)
            file_path = os.path.join(static_dir, "inventory", user_id, f"{item_id}.{extension}")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            return item_id, f"/static/inventory/{user_id}/{item_id}.{extension}"

        path = f"{user_id}/{item_id}.{extension}"
        self.storage_client.storage.from_("inventory").upload(
            path,
            image_bytes,
            file_options={"content-type": mime_type, "upsert": "false"},
        )
        public_url = self.storage_client.storage.from_("inventory").get_public_url(path)
        return item_id, public_url

    def upload_mockup(
        self,
        user_id: str,
        item_id: str,
        index: int,
        image_bytes: bytes,
    ) -> str:
        if not self.storage_client:
            import os
            # Save to local static directory
            static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
            os.makedirs(os.path.join(static_dir, "mockups", user_id, item_id), exist_ok=True)
            file_path = os.path.join(static_dir, "mockups", user_id, item_id, f"{index}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            return f"/static/mockups/{user_id}/{item_id}/{index}.jpg"

        path = f"{user_id}/{item_id}/mockup_{index}.jpg"
        self.storage_client.storage.from_("mockups").upload(
            path,
            image_bytes,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
        return self.storage_client.storage.from_("mockups").get_public_url(path)

    # Database (Postgres via pooler, async)

    async def create_item(
        self,
        item_id: str,
        user_id: str,
        original_image_url: str | None,
        style: str | None,
        difficulty: str | None,
        fabric_type: str | None = None,
        weight_kg: float | None = None,
        item_type: str = "finished_garment",
    ) -> str:
        if SessionLocal is None:
            return item_id

        async with SessionLocal() as session:
            item = Item(
                id=uuid.UUID(item_id),
                user_id=user_id,
                original_image_url=original_image_url,
                style=style,
                difficulty=difficulty,
                fabric_type=fabric_type,
                weight_kg=weight_kg,
                item_type=item_type,
            )
            session.add(item)
            await session.commit()
            return str(item.id)

    async def get_item(self, item_id: str) -> Item | None:
        """Fetch a single item by ID."""
        if SessionLocal is None:
            return None

        async with SessionLocal() as session:
            result = await session.execute(
                select(Item).where(Item.id == uuid.UUID(item_id))
            )
            return result.scalar_one_or_none()

    async def update_item_eligibility(
        self, item_id: str, is_eligible: bool
    ) -> None:
        """Set the is_market_eligible flag on an item."""
        if SessionLocal is None:
            return

        async with SessionLocal() as session:
            await session.execute(
                update(Item)
                .where(Item.id == uuid.UUID(item_id))
                .values(is_market_eligible=is_eligible)
            )
            await session.commit()

    async def create_project(
        self,
        user_id: str,
        item_id: str,
        selected_concept: dict[str, Any],
        sewing_guide: str,
        environmental_impact: str,
        environmental_data: dict[str, Any] | None = None,
    ) -> str | None:
        if SessionLocal is None:
            return str(uuid.uuid4())

        async with SessionLocal() as session:
            project = Project(
                item_id=_maybe_uuid(item_id),
                user_id=user_id,
                selected_concept=selected_concept,
                sewing_guide=sewing_guide,
                environmental_impact=environmental_impact,
                environmental_data=environmental_data,
            )
            session.add(project)
            await session.commit()
            return str(project.id)

    async def get_project_for_item(self, item_id: str) -> Project | None:
        """Fetch the most recent project for an item (used by verification)."""
        if SessionLocal is None:
            return None

        async with SessionLocal() as session:
            result = await session.execute(
                select(Project)
                .where(Project.item_id == uuid.UUID(item_id))
                .order_by(Project.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

    async def list_projects(self, user_id: str) -> list[dict[str, Any]]:
        if SessionLocal is None:
            return []

        async with SessionLocal() as session:
            result = await session.execute(
                select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
            )
            return [
                {
                    "id": str(p.id),
                    "item_id": str(p.item_id) if p.item_id else None,
                    "selected_concept": p.selected_concept,
                    "sewing_guide": p.sewing_guide,
                    "environmental_impact": p.environmental_impact,
                    "environmental_data": p.environmental_data,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in result.scalars().all()
            ]

    async def upsert_user_stats(
        self,
        user_id: str,
        water_saved_l: float,
        co2_offset_kg: float,
        landfill_diverted_kg: float,
    ) -> None:
        """Atomically increment cumulative user stats (insert if first time)."""
        if SessionLocal is None:
            return

        async with SessionLocal() as session:
            existing = await session.get(UserStats, user_id)
            if existing:
                existing.water_saved_l += water_saved_l
                existing.co2_offset_kg += co2_offset_kg
                existing.landfill_diverted_kg += landfill_diverted_kg
            else:
                session.add(
                    UserStats(
                        user_id=user_id,
                        water_saved_l=water_saved_l,
                        co2_offset_kg=co2_offset_kg,
                        landfill_diverted_kg=landfill_diverted_kg,
                    )
                )
            await session.commit()


def _maybe_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return None

