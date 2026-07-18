import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from agents.workflow import get_workflow
from schemas.execution import ExecutionRequest, ExecutionResponse
from schemas.ideation import IdeationResponse
from schemas.verification import VerificationResponse

router = APIRouter(prefix="/upcycle", tags=["upcycle"])


@router.post("/ideate", response_model=IdeationResponse)
async def ideate(
    image: UploadFile = File(...),
    user_id: str = Form(...),
    style: str = Form(...),
    difficulty: str = Form(...),
    fabric_type: str = Form(default=None),
    weight_kg: float = Form(default=None),
    tools_available: str = Form(default='["scissors", "sewing machine"]'),
    generate_mockups: bool = Form(default=False),
):
    """Phase 1: upload a garment image and generate 3 upcycling concepts."""
    # Parse robustly: support JSON array or fallback to comma-separated values
    tools_available_clean = tools_available.strip()
    if tools_available_clean.startswith("[") and tools_available_clean.endswith("]"):
        try:
            tools = json.loads(tools_available_clean)
            if not isinstance(tools, list):
                raise ValueError("tools_available must be a list")
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON array for tools_available: {exc}") from exc
    else:
        # Fallback for comma-separated lists (e.g. from automatic form serialization)
        tools = [t.strip() for t in tools_available_clean.split(",") if t.strip()]

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
            fabric_type=fabric_type,
            weight_kg=weight_kg,
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
            fabric_type=body.fabric_type,
            weight_kg=body.weight_kg,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Execution failed: {exc}") from exc

    return ExecutionResponse(**result)


@router.post("/{item_id}/verify", response_model=VerificationResponse)
async def verify(
    item_id: str,
    image: UploadFile = File(...),
):
    """Phase 3: verify a completed garment against the original design and instructions."""
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image upload")

    mime_type = image.content_type or "image/jpeg"
    workflow = get_workflow()

    try:
        result = await workflow.run_verification(
            item_id=item_id,
            completion_image_bytes=image_bytes,
            mime_type=mime_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Verification failed: {exc}") from exc

    return VerificationResponse(**result)

