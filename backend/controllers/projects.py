from fastapi import APIRouter, Depends

from core.auth import verify_token
from services.projects import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
async def list_projects(token_payload: dict = Depends(verify_token)):
    """List persisted projects for a user."""
    user_id = token_payload.get("sub")
    service = ProjectService()
    return {"projects": await service.list_projects(user_id)}

