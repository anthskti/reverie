from __future__ import annotations

import json
from typing import Any
from fastapi import HTTPException, status

from agents.workflow import get_workflow


class PipelineService:
    def __init__(self, workflow=None) -> None:
        self.workflow = workflow or get_workflow()

    def parse_tools(self, tools_available: str) -> list[str]:
        """Robustly parse tools JSON array or fall back to comma-separated list."""
        tools_available_clean = tools_available.strip()
        if tools_available_clean.startswith("[") and tools_available_clean.endswith("]"):
            try:
                tools = json.loads(tools_available_clean)
                if not isinstance(tools, list):
                    raise ValueError("tools_available must be a list")
                return tools
            except (json.JSONDecodeError, ValueError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid JSON array for tools_available: {exc}"
                ) from exc
        else:
            return [t.strip() for t in tools_available_clean.split(",") if t.strip()]

    async def run_ideation(
        self,
        user_id: str,
        image_bytes: bytes,
        style: str,
        difficulty: str,
        tools_available_str: str,
        mime_type: str,
        generate_mockups: bool,
        fabric_type: str | None,
        weight_kg: float | None,
    ) -> dict[str, Any]:
        """Phase 1 logic: Parse tools, check for empty image, and execute ideation."""
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image upload"
            )

        tools = self.parse_tools(tools_available_str)

        try:
            return await self.workflow.run_phase_1_ideation(
                user_id=user_id,
                image_bytes=image_bytes,
                style=style,
                difficulty=difficulty,
                tools_available=tools,
                mime_type=mime_type,
                generate_mockups=generate_mockups,
                fabric_type=fabric_type,
                weight_kg=weight_kg,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Ideation failed: {exc}") from exc

    async def run_execution(
        self,
        user_id: str,
        item_id: str,
        selected_concept: dict[str, Any],
        fabric_type: str,
        weight_kg: float,
    ) -> dict[str, Any]:
        """Phase 2 logic: run the sewing guide and environmental impact generation."""
        try:
            return await self.workflow.run_phase_2_execution(
                user_id=user_id,
                item_id=item_id,
                selected_concept=selected_concept,
                fabric_type=fabric_type,
                weight_kg=weight_kg,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Execution failed: {exc}") from exc

    async def run_verification(
        self,
        item_id: str,
        completion_image_bytes: bytes,
        mime_type: str,
    ) -> dict[str, Any]:
        """Phase 3 logic: Run visual comparison against design mockup."""
        if not completion_image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image upload"
            )

        try:
            return await self.workflow.run_verification(
                item_id=item_id,
                completion_image_bytes=completion_image_bytes,
                mime_type=mime_type,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Verification failed: {exc}") from exc
