from fastapi import APIRouter, Depends, HTTPException

from core.auth import verify_token
from repositories.inventory_repository import InventoryRepository
from schemas.inventory import ItemResponse, UserStatsResponse

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(token_payload: dict = Depends(verify_token)):
    """Fetch or lazily create a user's environmental stats."""
    user_id = token_payload.get("sub")
    repository = InventoryRepository()
    stats = await repository.get_user_stats(user_id)
    return stats


@router.get("/me", response_model=list[ItemResponse])
async def get_my_items(token_payload: dict = Depends(verify_token)):
    """Fetch all physical items belonging to the authenticated user."""
    user_id = token_payload.get("sub")
    repository = InventoryRepository()
    items = await repository.get_user_items(user_id)
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, token_payload: dict = Depends(verify_token)):
    """Fetch a specific item ensuring the authenticated user owns it."""
    user_id = token_payload.get("sub")
    repository = InventoryRepository()
    item = await repository.get_item(item_id, user_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")
        
    return item
