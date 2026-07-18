"""Webhooks controller — mounted at /api/webhooks.

All endpoints delegate webhook processing and signature verification to WebhookService.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from services.marketplace import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/unifold", status_code=status.HTTP_200_OK)
async def unifold_webhook(request: Request):
    """Handle inbound Unifold payment events.

    Delegates signature verification and event parsing to WebhookService.
    Always returns HTTP 200 OK on completion.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Unifold-Signature")

    service = WebhookService()
    service.verify_signature(raw_body, signature)

    try:
        payload = await request.json()
    except Exception:
        # Webhook parsing errors are returned with 400 Bad Request
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        )

    return await service.handle_webhook(payload)
