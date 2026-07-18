"""Thin Gemini runners — call models with prompts + schemas/tools."""

from google import genai
from google.genai import types

from agents import prompts
from agents.tools import calculate_environmental_impact, search_sewing_materials
from schemas.designer import DesignerResponse
from schemas.verification import VerificationResult


def generate_concepts(
    client: genai.Client,
    style: str,
    difficulty: str,
    tools_available: list[str],
    image_part: types.Part,
) -> DesignerResponse:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[image_part, prompts.designer_user_prompt(style, difficulty, tools_available)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DesignerResponse,
            system_instruction=prompts.DESIGNER_SYSTEM,
        ),
    )
    return response.parsed


def generate_mockup(client: genai.Client, original_image_desc: str, concept: str) -> bytes:
    prompt = prompts.style_mockup_prompt(original_image_desc, concept)
    
    # 1. Use generate_content, NOT generate_images
    response = client.models.generate_content(
        model='gemini-2.5-flash-image', # Highly recommended over the lite version for better fashion details
        contents=prompt,
        config=types.GenerateContentConfig(
            # 2. Force the model to return an image
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="3:4"
            )
        )
    )
    
    # 3. Extract the raw bytes from the response parts
    for part in response.parts:
        if part.inline_data:
            return part.inline_data.data
            
    raise ValueError("No image data returned from the model.")


def _collect_full_text(response) -> str:
    """Reconstruct the full model output across automatic-function-calling turns.

    When a tool is called mid-generation, ``response.text`` only contains the
    text from the *final* model turn.  Earlier text (before the tool call) lives
    in ``response.automatic_function_calling_history``.  This helper gathers
    text from every model turn so nothing is lost.
    """
    history = getattr(response, "automatic_function_calling_history", None) or []
    if history:
        parts: list[str] = []
        for message in history:
            if getattr(message, "role", None) == "model":
                for part in getattr(message, "parts", []):
                    text = getattr(part, "text", None)
                    if text:
                        parts.append(text)
        if parts:
            return "\n".join(parts)
    return response.text or ""


def generate_sewing_guide(client: genai.Client, concept: dict) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompts.sewing_guide_prompt(concept),
        config=types.GenerateContentConfig(
            tools=[search_sewing_materials],
            temperature=0.2,
        ),
    )
    return _collect_full_text(response)


def process_environmental_impact(
    client: genai.Client,
    weight_kg: float,
    fabric_type: str,
) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompts.environmental_impact_prompt(weight_kg, fabric_type),
        config=types.GenerateContentConfig(
            tools=[calculate_environmental_impact],
            temperature=0.1,
        ),
    )
    return _collect_full_text(response)


def verify_garment(
    client: genai.Client,
    completion_image: types.Part,
    mockup_image: types.Part | None,
    concept_title: str,
    concept_description: str,
    sewing_guide: str,
) -> VerificationResult:
    """QC verification agent — scores a completed garment against instructions."""
    prompt = prompts.verification_prompt(
        concept_title,
        concept_description,
        sewing_guide,
        has_mockup=(mockup_image is not None)
    )
    contents = [completion_image]
    if mockup_image is not None:
        contents.append(mockup_image)
    contents.append(prompt)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VerificationResult,
            system_instruction=prompts.VERIFICATION_SYSTEM,
        ),
    )
    return response.parsed

