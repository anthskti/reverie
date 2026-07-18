"""Thin Gemini runners — call models with prompts + schemas/tools."""

from google import genai
from google.genai import types

from agents import prompts
from agents.tools import calculate_environmental_impact
from schemas.designer import DesignerResponse


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
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return response.text


def process_environmental_impact(client: genai.Client, item_metadata: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompts.environmental_impact_prompt(item_metadata),
        config=types.GenerateContentConfig(
            tools=[calculate_environmental_impact],
            temperature=0.1,
        ),
    )
    return response.text
