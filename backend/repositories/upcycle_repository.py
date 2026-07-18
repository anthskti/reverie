"""Persistence for the upcycling pipeline.

- Image storage uses Supabase Storage when a client is configured, otherwise
  it returns local placeholder URLs so the pipeline stays runnable offline.
- Structured data (items, projects) is persisted to Postgres through the
  session pooler via async SQLAlchemy sessions.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from supabase import Client

from database import SessionLocal
from models import Item, Project


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
        if not self.storage_client:
            return item_id, f"local://inventory/{user_id}/{item_id}"

        extension = "jpg" if mime_type == "image/jpeg" else mime_type.split("/")[-1]
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
            return f"local://mockups/{user_id}/{item_id}/{index}.jpg"

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
            )
            session.add(item)
            await session.commit()
            return str(item.id)

    async def create_project(
        self,
        user_id: str,
        item_id: str,
        selected_concept: dict[str, Any],
        sewing_guide: str,
        environmental_impact: str,
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
            )
            session.add(project)
            await session.commit()
            return str(project.id)

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
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in result.scalars().all()
            ]


def _maybe_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return None
