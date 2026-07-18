"""Local Unifold sandbox — no live payments, no external API calls.

Mirrors the Connect deposit shape from https://demo.unifold.io/demo/customize
so the marketplace buy flow can be exercised end-to-end locally.
"""

from __future__ import annotations

import uuid
from typing import Any

# Demo destination matching Unifold Connect sandbox examples (Base USDC).
_SANDBOX_RECIPIENT = "0x606C49ca2Fa4982F07016265040F777eD3DA3160"
_SANDBOX_CHAIN_TYPE = "ethereum"
_SANDBOX_CHAIN_ID = "8453"
_SANDBOX_TOKEN_ADDRESS = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
_SANDBOX_TOKEN_SYMBOL = "USDC"


def create_deposit_session(
    listing_id: str,
    buyer_id: str,
    seller_id: str,
    amount_usdc: float,
) -> dict[str, Any]:
    """Build a local sandbox deposit session (Connect-compatible fields).

    The frontend opens a sandbox checkout UI with these params. Completing
    payment calls ``POST /api/marketplace/confirm-payment/{listing_id}``,
    which simulates Unifold's ``deposit.settled`` webhook.
    """
    return {
        "mode": "sandbox",
        "session_id": f"uf_sandbox_{uuid.uuid4().hex[:16]}",
        "external_user_id": buyer_id,
        "recipient_address": _SANDBOX_RECIPIENT,
        "destination_chain_type": _SANDBOX_CHAIN_TYPE,
        "destination_chain_id": _SANDBOX_CHAIN_ID,
        "destination_token_address": _SANDBOX_TOKEN_ADDRESS,
        "destination_token_symbol": _SANDBOX_TOKEN_SYMBOL,
        "amount_usdc": amount_usdc,
        "listing_id": listing_id,
        "seller_id": seller_id,
        "metadata": {
            "listing_id": listing_id,
            "buyer_id": buyer_id,
        },
    }


def sandbox_deposit_transaction_id(listing_id: str) -> str:
    """Deterministic-looking fake tx hash for sandbox deposit settlement."""
    return f"0xsandbox_deposit_{listing_id.replace('-', '')[:24]}"


def trigger_payout(
    listing_id: str,
    seller_id: str,
    amount_usdc: float,
) -> dict[str, Any]:
    """Sandbox payout — no external transfer; records a fake settlement id."""
    tx_id = f"0xsandbox_payout_{listing_id.replace('-', '')[:24]}"
    return {
        "status": "sandbox_settled",
        "listing_id": listing_id,
        "seller_id": seller_id,
        "amount_usdc": amount_usdc,
        "transaction_id": tx_id,
        "message": "Sandbox payout settled locally (no real transfer).",
    }
