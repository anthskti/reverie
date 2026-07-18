from fastapi import APIRouter

from repositories.inventory_repository import InventoryRepository
from schemas.inventory import GlobalStatsResponse

router = APIRouter(prefix="/stats", tags=["analytics"])


@router.get("/global", response_model=GlobalStatsResponse)
async def get_global_stats():
    """Retrieve aggregate environmental savings across all users."""
    repository = InventoryRepository()
    stats = await repository.get_global_stats()
    return GlobalStatsResponse(**stats)
