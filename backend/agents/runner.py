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
        model="gemini-2.5-flash",
        contents=[image_part, prompts.designer_user_prompt(style, difficulty, tools_available)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DesignerResponse,
            system_instruction=prompts.DESIGNER_SYSTEM,
        ),
    )
    return response.parsed


def generate_mockup(
    client: genai.Client,
    original_image_desc: str,
    concept: str,
) -> bytes:
    result = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompts.style_mockup_prompt(original_image_desc, concept),
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/jpeg",
            aspect_ratio="3:4",
        ),
    )
    return result.generated_images[0].image.image_bytes


def generate_sewing_guide(client: genai.Client, concept: dict) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompts.sewing_guide_prompt(concept),
        config=types.GenerateContentConfig(
            tools=[search_sewing_materials],
            temperature=0.2,
        ),
    )
    return response.text


def process_environmental_impact(
    client: genai.Client,
    weight_kg: float,
    fabric_type: str,
) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompts.environmental_impact_prompt(weight_kg, fabric_type),
        config=types.GenerateContentConfig(
            tools=[calculate_environmental_impact],
            temperature=0.1,
        ),
    )
    return response.text


def verify_garment(
    client: genai.Client,
    completion_image: types.Part,
    concept_title: str,
    concept_description: str,
    sewing_guide: str,
) -> VerificationResult:
    """QC verification agent — scores a completed garment against instructions."""
    prompt = prompts.verification_prompt(concept_title, concept_description, sewing_guide)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[completion_image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VerificationResult,
            system_instruction=prompts.VERIFICATION_SYSTEM,
        ),
    )
    return response.parsed

