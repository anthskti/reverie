"""Orchestrates the upcycling pipeline phases (ideation → execution)."""

import asyncio
import os
from functools import lru_cache

from google import genai
from google.genai import types
from supabase import Client, create_client

from agents.runner import (
    generate_concepts,
    generate_mockup,
    generate_sewing_guide,
    process_environmental_impact,
)
from repositories import UpcycleRepository
from schemas.designer import DesignerResponse, UpcycleOption


class UpcycleWorkflow:
    def __init__(self, supabase_client: Client | None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is required")
        self.ai_client = genai.Client(api_key=api_key)
        self.db = UpcycleRepository(supabase_client)

    async def run_phase_1_ideation(
        self,
        user_id: str,
        image_bytes: bytes,
        style: str,
        difficulty: str,
        tools_available: list[str] | None = None,
        mime_type: str = "image/jpeg",
        generate_mockups: bool = False,
    ) -> dict:
        tools = tools_available or ["scissors", "sewing machine"]

        item_id, image_url = await asyncio.to_thread(
            self.db.upload_inventory_image,
            user_id,
            image_bytes,
            mime_type,
        )

        await self.db.create_item(
            item_id=item_id,
            user_id=user_id,
            original_image_url=image_url,
            style=style,
            difficulty=difficulty,
        )

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        concepts: DesignerResponse = await asyncio.to_thread(
            generate_concepts,
            self.ai_client,
            style,
            difficulty,
            tools,
            image_part,
        )

        mockup_urls: list[str | None] = []
        if generate_mockups:
            mockup_urls = await self._generate_mockups(
                user_id=user_id,
                item_id=item_id,
                options=concepts.options,
                original_image_desc=f"Uploaded garment image ({style} style target)",
            )

        return {
            "item_id": item_id,
            "options": concepts.options,
            "mockup_urls": mockup_urls,
            "original_image_url": image_url,
        }

    async def _generate_mockups(
        self,
        user_id: str,
        item_id: str,
        options: list[UpcycleOption],
        original_image_desc: str,
    ) -> list[str | None]:
        async def _one(index: int, option: UpcycleOption) -> str | None:
            try:
                concept_text = (
                    f"{option.title}: {option.description}. "
                    f"Techniques: {', '.join(option.techniques)}. "
                    f"Difficulty: {option.difficulty}."
                )
                image_bytes = await asyncio.to_thread(
                    generate_mockup,
                    self.ai_client,
                    original_image_desc,
                    concept_text,
                )
                return await asyncio.to_thread(
                    self.db.upload_mockup,
                    user_id,
                    item_id,
                    index,
                    image_bytes,
                )
            except Exception:
                return None

        return list(await asyncio.gather(*[_one(i, opt) for i, opt in enumerate(options)]))

    async def run_phase_2_execution(
        self,
        user_id: str,
        item_id: str,
        selected_concept: UpcycleOption | dict,
        item_metadata: str,
    ) -> dict:
        concept = (
            selected_concept.model_dump()
            if isinstance(selected_concept, UpcycleOption)
            else selected_concept
        )

        sewing_guide, environmental_impact = await asyncio.gather(
            asyncio.to_thread(generate_sewing_guide, self.ai_client, concept),
            asyncio.to_thread(
                process_environmental_impact,
                self.ai_client,
                item_metadata,
            ),
        )

        project_id = await self.db.create_project(
            user_id=user_id,
            item_id=item_id,
            selected_concept=concept,
            sewing_guide=sewing_guide,
            environmental_impact=environmental_impact,
        )

        return {
            "project_id": project_id,
            "sewing_guide": sewing_guide,
            "environmental_impact": environmental_impact,
        }


def get_supabase_client() -> Client | None:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


@lru_cache
def get_workflow() -> UpcycleWorkflow:
    return UpcycleWorkflow(get_supabase_client())
