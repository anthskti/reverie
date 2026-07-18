import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GlobalStatsResponse(BaseModel):
    total_water_saved_l: float
    total_co2_offset_kg: float
    total_landfill_diverted_kg: float


class UserStatsResponse(BaseModel):
    user_id: str
    water_saved_l: float
    co2_offset_kg: float
    landfill_diverted_kg: float
    updated_at: datetime


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    original_image_url: str | None
    style: str | None
    difficulty: str | None
    fabric_type: str | None
    weight_kg: float | None
    item_type: str
    is_market_eligible: bool
    created_at: datetime
