from __future__ import annotations

from typing import Any
from repositories.upcycle_repository import UpcycleRepository


class ProjectService:
    def __init__(self, repository: UpcycleRepository | None = None) -> None:
        self.repository = repository or UpcycleRepository(storage_client=None)

    async def list_projects(self, user_id: str) -> list[dict[str, Any]]:
        """List persisted projects for a user."""
        return await self.repository.list_projects(user_id)
