from pydantic import BaseModel, Field

from schemas.designer import UpcycleOption


class ExecutionRequest(BaseModel):
    item_id: str
    selected_concept: UpcycleOption
    fabric_type: str = Field(description="Fabric type, e.g. cotton, polyester, denim")
    weight_kg: float = Field(description="Garment weight in kilograms")


class ExecutionResponse(BaseModel):
    project_id: str | None = None
    sewing_guide: str
    environmental_impact: str
    environmental_data: dict | None = Field(
        default=None,
        description="Structured metrics: water_saved_liters, co2_offset_kg, landfill_diverted_kg",
    )
    mockup_url: str | None = None

