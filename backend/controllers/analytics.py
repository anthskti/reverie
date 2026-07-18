from fastapi import APIRouter

from schemas.inventory import GlobalStatsResponse
from services.analytics import AnalyticsService

router = APIRouter(prefix="/stats", tags=["analytics"])


@router.get("/global", response_model=GlobalStatsResponse)
async def get_global_stats():
    """Retrieve aggregate environmental savings across all users."""
    service = AnalyticsService()
    stats = await service.get_global_stats()
    return GlobalStatsResponse(**stats)

