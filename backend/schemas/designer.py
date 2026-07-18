from pydantic import BaseModel, Field


class UpcycleOption(BaseModel):
    title: str = Field(description="Name for the upcycled garment")
    description: str = Field(description="Brief explanation of the style")
    techniques: list[str] = Field(description="List of sewing/crafting techniques needed")
    difficulty: str = Field(description="easy, medium, or hard")


class DesignerResponse(BaseModel):
    options: list[UpcycleOption] = Field(
        description="Exactly 3 upcycling options",
        min_length=3,
        max_length=3,
    )
