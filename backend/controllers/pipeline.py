from fastapi import APIRouter, Depends, File, Form, UploadFile

from core.auth import verify_token
from schemas.execution import ExecutionRequest, ExecutionResponse
from schemas.ideation import IdeationResponse
from schemas.verification import VerificationResponse
from services.pipeline import PipelineService

router = APIRouter(prefix="/upcycle", tags=["upcycle"])


@router.post("/ideate", response_model=IdeationResponse)
async def ideate(
    image: UploadFile = File(...),
    style: str = Form(...),
    difficulty: str = Form(...),
    fabric_type: str = Form(default=None),
    weight_kg: float = Form(default=None),
    tools_available: str = Form(default='["scissors", "sewing machine"]'),
    generate_mockups: bool = Form(default=False),
    token_payload: dict = Depends(verify_token),
):
    """Phase 1: upload a garment image and generate 3 upcycling concepts."""
    user_id = token_payload.get("sub")
    image_bytes = await image.read()
    mime_type = image.content_type or "image/jpeg"

    service = PipelineService()
    result = await service.run_ideation(
        user_id=user_id,
        image_bytes=image_bytes,
        style=style,
        difficulty=difficulty,
        tools_available_str=tools_available,
        mime_type=mime_type,
        generate_mockups=generate_mockups,
        fabric_type=fabric_type,
        weight_kg=weight_kg,
    )
    return IdeationResponse(**result)


@router.post("/execute", response_model=ExecutionResponse)
async def execute(
    body: ExecutionRequest,
    token_payload: dict = Depends(verify_token),
):
    """Phase 2: generate sewing guide and environmental impact for a selected concept."""
    user_id = token_payload.get("sub")
    service = PipelineService()
    result = await service.run_execution(
        user_id=user_id,
        item_id=body.item_id,
        selected_concept=body.selected_concept.model_dump(),
        fabric_type=body.fabric_type,
        weight_kg=body.weight_kg,
    )
    return ExecutionResponse(**result)


@router.post("/{item_id}/verify", response_model=VerificationResponse)
async def verify(
    item_id: str,
    image: UploadFile = File(...),
    token_payload: dict = Depends(verify_token),
):
    """Phase 3: verify a completed garment against the original design and instructions."""
    image_bytes = await image.read()
    mime_type = image.content_type or "image/jpeg"

    service = PipelineService()
    result = await service.run_verification(
        item_id=item_id,
        completion_image_bytes=image_bytes,
        mime_type=mime_type,
    )
    return VerificationResponse(**result)


