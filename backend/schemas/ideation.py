from pydantic import BaseModel, Field

from schemas.designer import UpcycleOption


class IdeationResponse(BaseModel):
    item_id: str
    options: list[UpcycleOption]
    mockup_urls: list[str | None] = Field(default_factory=list)
    original_image_url: str | None = None
