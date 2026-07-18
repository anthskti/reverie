from __future__ import annotations

from repositories.inventory_repository import InventoryRepository


class AnalyticsService:
    def __init__(self, repository: InventoryRepository | None = None) -> None:
        self.repository = repository or InventoryRepository()

    async def get_global_stats(self) -> dict[str, float]:
        """Retrieve aggregate environmental savings across all users."""
        return await self.repository.get_global_stats()
