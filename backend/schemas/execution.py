from pydantic import BaseModel, Field

from schemas.designer import UpcycleOption


class ExecutionRequest(BaseModel):
    user_id: str
    item_id: str
    selected_concept: UpcycleOption
    item_metadata: str = Field(
        description="Free-text description including weight and fabric type when known",
    )


class ExecutionResponse(BaseModel):
    project_id: str | None = None
    sewing_guide: str
    environmental_impact: str
