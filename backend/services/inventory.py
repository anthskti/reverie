from __future__ import annotations

from models import Item
from models.user_stats import UserStats
from repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, repository: InventoryRepository | None = None) -> None:
        self.repository = repository or InventoryRepository()

    async def get_user_stats(self, user_id: str) -> UserStats:
        """Fetch or lazily create a user's environmental stats."""
        return await self.repository.get_user_stats(user_id)

    async def get_user_items(self, user_id: str) -> list[Item]:
        """Fetch all physical items belonging to the user."""
        return await self.repository.get_user_items(user_id)

    async def get_item_or_raise(self, item_id: str, user_id: str) -> Item:
        """Fetch a specific item. Raises ValueError if not found or unauthorized."""
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            raise ValueError("Item not found or unauthorized")
        return item
