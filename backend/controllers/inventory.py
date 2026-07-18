from fastapi import APIRouter, Depends, HTTPException, status

from core.auth import verify_token
from schemas.inventory import ItemResponse, UserStatsResponse
from services.inventory import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(token_payload: dict = Depends(verify_token)):
    """Fetch or lazily create a user's environmental stats."""
    user_id = token_payload.get("sub")
    service = InventoryService()
    stats = await service.get_user_stats(user_id)
    return stats


@router.get("/me", response_model=list[ItemResponse])
async def get_my_items(token_payload: dict = Depends(verify_token)):
    """Fetch all physical items belonging to the authenticated user."""
    user_id = token_payload.get("sub")
    service = InventoryService()
    items = await service.get_user_items(user_id)
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, token_payload: dict = Depends(verify_token)):
    """Fetch a specific item ensuring the authenticated user owns it."""
    user_id = token_payload.get("sub")
    service = InventoryService()
    try:
        item = await service.get_item_or_raise(item_id, user_id)
        return item
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

