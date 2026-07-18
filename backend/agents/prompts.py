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
        "Use the search_sewing_materials tool to find purchase links for any specific "
        "hardware or fabric needed (zippers, dye, patches, etc.). "
        "Assume the user has basic sewing tools. Focus on clear, practical steps."
    )


def environmental_impact_prompt(weight_kg: float, fabric_type: str) -> str:
    return (
        f"The garment weighs {weight_kg} kg and is made of {fabric_type}. "
        "Call the calculate_environmental_impact tool with these values, "
        "then summarize the environmental savings in a user-friendly format."
    )


# --- QC Verification Agent ---

VERIFICATION_SYSTEM = (
    "You are a quality control expert for upcycled fashion. "
    "Compare the completed garment photo against the original design concept and "
    "sewing instructions. Evaluate craftsmanship, accuracy to the design, and "
    "overall quality. Be encouraging but honest."
)


def verification_prompt(
    concept_title: str,
    concept_description: str,
    sewing_guide: str,
) -> str:
    return (
        "Evaluate the completed upcycled garment shown in the photo.\n\n"
        f"**Original Design:** {concept_title}\n"
        f"**Description:** {concept_description}\n\n"
        f"**Instructions that were followed:**\n{sewing_guide}\n\n"
        "Score the result from 0 to 100 based on:\n"
        "- Accuracy to the original design concept (40%)\n"
        "- Craftsmanship and finish quality (40%)\n"
        "- Creativity and personal touches (20%)\n\n"
        "Provide detailed, constructive feedback."
    )

