import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from agents.workflow import get_workflow
from schemas.execution import ExecutionRequest, ExecutionResponse
from schemas.ideation import IdeationResponse

router = APIRouter(prefix="/upcycle", tags=["upcycle"])


@router.post("/ideate", response_model=IdeationResponse)
async def ideate(
    image: UploadFile = File(...),
    user_id: str = Form(...),
    style: str = Form(...),
    difficulty: str = Form(...),
    tools_available: str = Form(default='["scissors", "sewing machine"]'),
    generate_mockups: bool = Form(default=False),
):
    """Phase 1: upload a garment image and generate 3 upcycling concepts."""
    try:
        tools = json.loads(tools_available)
        if not isinstance(tools, list):
            raise ValueError("tools_available must be a JSON array of strings")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid tools_available: {exc}") from exc

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image upload")

    mime_type = image.content_type or "image/jpeg"
    workflow = get_workflow()

    try:
        result = await workflow.run_phase_1_ideation(
            user_id=user_id,
            image_bytes=image_bytes,
            style=style,
            difficulty=difficulty,
            tools_available=tools,
            mime_type=mime_type,
            generate_mockups=generate_mockups,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ideation failed: {exc}") from exc

    return IdeationResponse(**result)


@router.post("/execute", response_model=ExecutionResponse)
async def execute(body: ExecutionRequest):
    """Phase 2: generate sewing guide and environmental impact for a selected concept."""
    workflow = get_workflow()

    try:
        result = await workflow.run_phase_2_execution(
            user_id=body.user_id,
            item_id=body.item_id,
            selected_concept=body.selected_concept,
            item_metadata=body.item_metadata,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Execution failed: {exc}") from exc

    return ExecutionResponse(**result)
