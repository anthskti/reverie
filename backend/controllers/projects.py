from fastapi import APIRouter, Depends

from core.auth import verify_token
from repositories.upcycle_repository import UpcycleRepository

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
async def list_projects(token_payload: dict = Depends(verify_token)):
    """List persisted projects for a user."""
    user_id = token_payload.get("sub")
    repository = UpcycleRepository(storage_client=None)
    return {"projects": await repository.list_projects(user_id)}
