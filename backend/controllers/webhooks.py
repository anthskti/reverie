"""Webhooks controller — mounted at /api/webhooks.

Endpoint
--------
POST /api/webhooks/unifold

Verifies Unifold's HMAC-SHA256 cryptographic signature, then dispatches on
``event_type``:

  deposit.settled  — buyer paid the smart contract → listing: locked_in_escrow
                     (safe for seller to ship the physical item)

  payout.settled   — funds hit the seller's wallet → record the transaction hash

Always return 200 OK — a non-200 causes Unifold to aggressively retry.

Signature scheme
----------------
Unifold signs the raw request body with HMAC-SHA256 using UNIFOLD_WEBHOOK_SECRET
and sends the hex digest in the ``X-Unifold-Signature`` header.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os

from fastapi import APIRouter, HTTPException, Request, status

from repositories.marketplace_repository import MarketplaceRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_marketplace_repo = MarketplaceRepository()

_WEBHOOK_SECRET = os.getenv("UNIFOLD_WEBHOOK_SECRET", "")

# Signature verification
def _verify_unifold_signature(raw_body: bytes, signature_header: str | None) -> None:
    """Raise HTTP 401 if the HMAC-SHA256 signature does not match.

    When UNIFOLD_WEBHOOK_SECRET is not set (offline/dev mode) the check is
    skipped with a warning so local development is not blocked.
    """
    if not _WEBHOOK_SECRET:
        logger.warning(
            "UNIFOLD_WEBHOOK_SECRET not configured, skipping signature verification."
        )
        return

    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Unifold-Signature header.",
        )

    expected = hmac.new(
        _WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    # Constant time comparison guards against timing attacks.
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )


# Webhook endpoint

@router.post("/unifold", status_code=status.HTTP_200_OK)
async def unifold_webhook(request: Request):
    """Handle inbound Unifold payment events.

    Expected payload shape::

        {
            "event_type": "deposit.settled" | "payout.settled",
            "transaction_id": "<unifold-tx-hash>",
            "metadata": {
                "listing_id": "<uuid>",
                "buyer_id": "<auth0-sub>"   // present on deposit.settled
            }
        }
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Unifold-Signature")

    _verify_unifold_signature(raw_body, signature)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        )

    event_type: str = payload.get("event_type", "")
    transaction_id: str | None = payload.get("transaction_id")
    metadata: dict = payload.get("metadata", {})
    listing_id: str | None = metadata.get("listing_id")

    if not listing_id:
        # Return 200: malformed metadata should not trigger retries
        logger.error("Unifold webhook missing metadata.listing_id: %s", payload)
        return {"status": "ok", "message": "Missing listing_id in metadata, ignored."}

    # deposit.settled: buyer paid; funds locked in smart contract
    if event_type == "deposit.settled":
        listing = await _marketplace_repo.get_listing(listing_id)
        if listing is None:
            logger.warning(
                "deposit.settled: listing %s not found — ignoring.", listing_id
            )
            return {"status": "ok", "message": "Listing not found, ignoring."}

        await _marketplace_repo.set_listing_status(listing_id, "locked_in_escrow")
        logger.info(
            "deposit.settled: listing %s → locked_in_escrow (tx: %s)",
            listing_id,
            transaction_id,
        )

    # payout.settled: funds disbursed to seller's wallet
    elif event_type == "payout.settled":
        if transaction_id:
            await _marketplace_repo.record_payout(
                listing_id=listing_id, transaction_id=transaction_id
            )
            logger.info(
                "payout.settled: listing %s, tx_hash=%s recorded.",
                listing_id,
                transaction_id,
            )
        else:
            logger.warning(
                "payout.settled received without transaction_id for listing %s.",
                listing_id,
            )

    # Unknown event: log and ack so Unifold doesn't retry
    else:
        logger.info(
            "Unifold webhook: unhandled event_type '%s' for listing %s — ignoring.",
            event_type,
            listing_id,
        )

    # Always 200 OK: prevents Unifold retry storms
    return {"status": "ok"}
