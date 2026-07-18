"""Orchestrates the upcycling pipeline phases (ideation → execution → verification)."""

import asyncio
import os
from functools import lru_cache

from google import genai
from google.genai import types
from supabase import Client, create_client

from agents.auth_vertex import setup_vertex_credentials
from agents.runner import (
    generate_concepts,
    generate_mockup,
    generate_sewing_guide,
    process_environmental_impact,
    verify_garment,
)
from agents.tools import calculate_environmental_impact
from repositories import UpcycleRepository
from schemas.designer import DesignerResponse, UpcycleOption
from schemas.verification import VerificationResult


class UpcycleWorkflow:
    def __init__(self, supabase_client: Client | None):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

        if project or creds_json:
            setup_vertex_credentials()
            self.ai_client = genai.Client(
                vertexai=True,
                project=project,
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            )
        else:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("Either GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT/GOOGLE_CREDENTIALS_JSON must be set.")
            self.ai_client = genai.Client(api_key=api_key)

        self.db = UpcycleRepository(supabase_client)

    # --- Phase 1: Ideation ---------------------------------------------------

    async def run_phase_1_ideation(
        self,
        user_id: str,
        image_bytes: bytes,
        style: str,
        difficulty: str,
        tools_available: list[str] | None = None,
        mime_type: str = "image/jpeg",
        generate_mockups: bool = False,
        fabric_type: str | None = None,
        weight_kg: float | None = None,
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
            fabric_type=fabric_type,
            weight_kg=weight_kg,
            item_type="finished_garment",
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

        # Attach mockup URLs to options if we generated them
        options = concepts.options
        if mockup_urls:
            for opt, url in zip(options, mockup_urls):
                opt.mockup_url = url

        return {
            "item_id": item_id,
            "options": options,
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
            except Exception as exc:
                import traceback
                print(f"Error generating mockup {index}: {exc}")
                traceback.print_exc()
                return None

        return list(await asyncio.gather(*[_one(i, opt) for i, opt in enumerate(options)]))

    # --- Phase 2: Execution ---------------------------------------------------

    async def run_phase_2_execution(
        self,
        user_id: str,
        item_id: str,
        selected_concept: UpcycleOption | dict,
        fabric_type: str,
        weight_kg: float,
    ) -> dict:
        concept = (
            selected_concept.model_dump()
            if isinstance(selected_concept, UpcycleOption)
            else selected_concept
        )

        sewing_guide, environmental_narrative = await asyncio.gather(
            asyncio.to_thread(generate_sewing_guide, self.ai_client, concept),
            asyncio.to_thread(
                process_environmental_impact,
                self.ai_client,
                weight_kg,
                fabric_type,
            ),
        )

        # Compute structured metrics directly via the tool function
        env_data = calculate_environmental_impact(weight_kg, fabric_type)

        project_id = await self.db.create_project(
            user_id=user_id,
            item_id=item_id,
            selected_concept=concept,
            sewing_guide=sewing_guide,
            environmental_impact=environmental_narrative,
            environmental_data=env_data,
        )

        # Accumulate user stats
        await self.db.upsert_user_stats(
            user_id=user_id,
            water_saved_l=env_data["water_saved_liters"],
            co2_offset_kg=env_data["co2_offset_kg"],
            landfill_diverted_kg=env_data["landfill_diverted_kg"],
        )

        return {
            "project_id": project_id,
            "sewing_guide": sewing_guide,
            "environmental_impact": environmental_narrative,
            "environmental_data": env_data,
            "mockup_url": concept.get("mockup_url"),
        }

    # --- Phase 3: QC Verification ---------------------------------------------

    async def run_verification(
        self,
        item_id: str,
        completion_image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """Run the QC verification agent on a completion photo."""
        # Load the item and its most recent project
        item = await self.db.get_item(item_id)
        if item is None:
            raise ValueError(f"Item {item_id} not found")

        if item.item_type != "finished_garment":
            raise ValueError(
                f"Only finished garments can undergo QC verification. "
                f"Item type is '{item.item_type}'."
            )

        project = await self.db.get_project_for_item(item_id)
        if project is None:
            raise ValueError(f"No project found for item {item_id}")

        completion_image = types.Part.from_bytes(
            data=completion_image_bytes, mime_type=mime_type
        )

        concept = project.selected_concept or {}
        mockup_url = concept.get("mockup_url")
        mockup_image_part = None

        if mockup_url:
            try:
                if mockup_url.startswith("/static/"):
                    import os
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    path = os.path.join(base_dir, mockup_url.lstrip("/"))
                    with open(path, "rb") as f:
                        mockup_bytes = f.read()
                    mockup_image_part = types.Part.from_bytes(
                        data=mockup_bytes, mime_type="image/jpeg"
                    )
                elif mockup_url.startswith("http"):
                    import httpx
                    async with httpx.AsyncClient() as client:
                        res = await client.get(mockup_url, timeout=10.0)
                        if res.status_code == 200:
                            mockup_image_part = types.Part.from_bytes(
                                data=res.content, mime_type="image/jpeg"
                            )
            except Exception as e:
                # Log error but don't fail verification if mockup loading fails
                print(f"Error loading mockup image for verification: {e}")

        result: VerificationResult = await asyncio.to_thread(
            verify_garment,
            self.ai_client,
            completion_image,
            mockup_image_part,
            concept.get("title", "Unknown"),
            concept.get("description", ""),
            project.sewing_guide or "",
        )

        is_eligible = result.score >= 50

        # Update marketplace eligibility
        await self.db.update_item_eligibility(item_id, is_eligible)

        return {
            "score": result.score,
            "is_eligible": is_eligible,
            "feedback": result.feedback,
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

