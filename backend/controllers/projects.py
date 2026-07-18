from fastapi import APIRouter

from repositories.upcycle_repository import UpcycleRepository

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/{user_id}")
async def list_projects(user_id: str):
    """List persisted projects for a user."""
    repository = UpcycleRepository(storage_client=None)
    return {"projects": await repository.list_projects(user_id)}
