from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    """Structured output schema for the QC verification agent."""

    score: int = Field(
        description="Quality score from 0 to 100 comparing the finished garment to the instructions"
    )
    feedback: str = Field(
        description="Detailed feedback on craftsmanship, accuracy to the design, and areas for improvement"
    )


class VerificationResponse(BaseModel):
    """API response for the verification endpoint."""

    score: int
    is_eligible: bool = Field(
        description="True if score >= 70 and the item qualifies for marketplace listing"
    )
    feedback: str
