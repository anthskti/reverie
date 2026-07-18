"""Thin async wrapper around the Unifold Payout & Commerce API.

When UNIFOLD_API_URL is not set the client operates in offline/no-op mode so
the full pipeline can run locally without a live Unifold account.
"""

from __future__ import annotations

import os

import httpx

_UNIFOLD_API_URL = os.getenv("UNIFOLD_API_URL", "")
_UNIFOLD_API_KEY = os.getenv("UNIFOLD_API_KEY", "")

# How long (seconds) to wait for Unifold API responses before timing out.
_TIMEOUT = 15.0


def _is_configured() -> bool:
    return bool(_UNIFOLD_API_URL)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_UNIFOLD_API_KEY}",
        "Content-Type": "application/json",
    }


async def create_checkout(
    listing_id: str,
    buyer_id: str,
    seller_id: str,
    amount_usdc: float,
) -> str:
    """Create a Unifold Sandbox checkout session.

    Returns the checkout URL that the buyer should be redirected to.
    In offline mode, returns a stub URL so the flow can be exercised locally.

    Unifold will POST back to ``/api/webhooks/unifold`` with
    ``event_type == 'deposit.settled'`` once the buyer pays, passing
    ``listing_id`` and ``buyer_id`` inside the ``metadata`` block.
    """
    if not _is_configured():
        stub_url = (
            f"https://sandbox.unifold.io/checkout/stub"
            f"?listing_id={listing_id}&amount={amount_usdc}"
        )
        return stub_url

    url = f"{_UNIFOLD_API_URL.rstrip('/')}/checkout"
    payload = {
        "amount_usdc": amount_usdc,
        "seller_id": seller_id,
        "metadata": {
            "listing_id": listing_id,
            "buyer_id": buyer_id,
        },
        # Webhook callback — Unifold will POST deposit.settled here
        "webhook_url": os.getenv("APP_BASE_URL", "") + "/api/webhooks/unifold",
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=_headers())
        response.raise_for_status()
        data = response.json()
        return data["checkout_url"]


async def trigger_payout(
    listing_id: str,
    seller_id: str,
    amount_usdc: float,
) -> dict:
    """Instruct Unifold to disburse escrowed funds to the seller.

    Returns the raw Unifold response body as a dict, or a stub dict when
    the service is unconfigured (offline mode).

    Unifold will POST back to ``/api/webhooks/unifold`` with
    ``event_type == 'payout.settled'`` once the transfer completes.
    """
    if not _is_configured():
        return {
            "status": "offline_noop",
            "listing_id": listing_id,
            "seller_id": seller_id,
            "amount_usdc": amount_usdc,
            "message": "Unifold API not configured — payout skipped in offline mode.",
        }

    url = f"{_UNIFOLD_API_URL.rstrip('/')}/payouts"
    payload = {
        "listing_id": listing_id,
        "seller_id": seller_id,
        "amount_usdc": amount_usdc,
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=_headers())
        response.raise_for_status()
        return response.json()
