"""Prompt templates for the upcycling agents."""

DESIGNER_SYSTEM = (
    "You are an expert sustainable fashion designer. "
    "Only suggest concepts that are physically possible with the provided tools."
)


def designer_user_prompt(style: str, difficulty: str, tools_available: list[str]) -> str:
    return (
        "Act as an expert sustainable fashion designer. Based on the uploaded image, "
        f"generate 3 upcycling options. Style target: {style}. Max difficulty: {difficulty}. "
        f"Available tools: {tools_available}."
    )


def style_mockup_prompt(original_image_desc: str, concept: str) -> str:
    return (
        "A realistic fashion photography shot of a 2D clothing model wearing an upcycled garment. "
        f"Original base: {original_image_desc}. Upcycle modifications: {concept}. "
        "High quality, studio lighting."
    )


def sewing_guide_prompt(concept: dict) -> str:
    return (
        f"Write a step-by-step markdown tutorial for this upcycle project: {concept}. "
        "Assume the user has basic sewing tools. Focus on clear, practical steps."
    )


def environmental_impact_prompt(item_metadata: str) -> str:
    return (
        f"Extract the weight and fabric type from this item description: {item_metadata}. "
        "Then call calculate_environmental_impact to get the exact metrics and summarize them."
    )
