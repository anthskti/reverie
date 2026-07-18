"""Unit tests for local Unifold sandbox + marketplace payment flow.

Run from the backend/ directory:
    uv run python -m pytest tests/test_unifold_sandbox.py -v
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import unifold as unifold_service
from services.marketplace import MarketplaceService, WebhookService


# ---------------------------------------------------------------------------
# Unifold sandbox helpers (pure, no I/O)
# ---------------------------------------------------------------------------


class TestCreateDepositSession:
    def test_returns_sandbox_mode_and_connect_shaped_fields(self):
        session = unifold_service.create_deposit_session(
            listing_id="listing-1",
            buyer_id="buyer-1",
            seller_id="seller-1",
            amount_usdc=24.5,
        )

        assert session["mode"] == "sandbox"
        assert session["session_id"].startswith("uf_sandbox_")
        assert session["external_user_id"] == "buyer-1"
        assert session["listing_id"] == "listing-1"
        assert session["seller_id"] == "seller-1"
        assert session["amount_usdc"] == 24.5
        assert session["destination_chain_id"] == "8453"
        assert session["destination_token_symbol"] == "USDC"
        assert session["recipient_address"].startswith("0x")
        assert session["metadata"] == {
            "listing_id": "listing-1",
            "buyer_id": "buyer-1",
        }

    def test_session_ids_are_unique(self):
        a = unifold_service.create_deposit_session("l", "b", "s", 1.0)
        b = unifold_service.create_deposit_session("l", "b", "s", 1.0)
        assert a["session_id"] != b["session_id"]


class TestSandboxTransactionIds:
    def test_deposit_tx_id_strips_hyphens(self):
        listing_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        tx = unifold_service.sandbox_deposit_transaction_id(listing_id)
        assert tx.startswith("0xsandbox_deposit_")
        assert "-" not in tx.removeprefix("0xsandbox_deposit_")

    def test_payout_returns_sandbox_settled(self):
        result = unifold_service.trigger_payout(
            listing_id="listing-xyz",
            seller_id="seller-1",
            amount_usdc=10.0,
        )
        assert result["status"] == "sandbox_settled"
        assert result["listing_id"] == "listing-xyz"
        assert result["seller_id"] == "seller-1"
        assert result["amount_usdc"] == 10.0
        assert result["transaction_id"].startswith("0xsandbox_payout_")


# ---------------------------------------------------------------------------
# MarketplaceService with mocked repository
# ---------------------------------------------------------------------------


def _listing(
    *,
    status: str = "active",
    seller_id: str = "seller-1",
    buyer_id: str | None = None,
    price_usdc: float = 15.0,
    listing_id: str = "11111111-1111-1111-1111-111111111111",
):
    return SimpleNamespace(
        id=listing_id,
        seller_id=seller_id,
        buyer_id=buyer_id,
        price_usdc=price_usdc,
        status=status,
    )


@pytest.fixture
def repo():
    mock = MagicMock()
    mock.get_listing = AsyncMock()
    mock.record_checkout = AsyncMock()
    mock.set_listing_status = AsyncMock()
    mock.record_payout = AsyncMock()
    return mock


@pytest.fixture
def service(repo):
    return MarketplaceService(marketplace_repo=repo, inventory_repo=MagicMock())


@pytest.mark.asyncio
class TestMarketplaceCheckout:
    async def test_checkout_creates_deposit_and_records_buyer(self, service, repo):
        listing = _listing()
        repo.get_listing.return_value = listing

        deposit = await service.checkout(listing.id, "buyer-1")

        assert deposit["mode"] == "sandbox"
        assert deposit["amount_usdc"] == 15.0
        assert deposit["external_user_id"] == "buyer-1"
        repo.record_checkout.assert_awaited_once_with(
            listing_id=listing.id, buyer_id="buyer-1"
        )

    async def test_checkout_rejects_missing_listing(self, service, repo):
        repo.get_listing.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.checkout("missing", "buyer-1")
        assert exc.value.status_code == 404

    async def test_checkout_rejects_non_active(self, service, repo):
        repo.get_listing.return_value = _listing(status="pending_payment")
        with pytest.raises(HTTPException) as exc:
            await service.checkout("listing-1", "buyer-1")
        assert exc.value.status_code == 409

    async def test_checkout_rejects_self_purchase(self, service, repo):
        repo.get_listing.return_value = _listing(seller_id="same-user")
        with pytest.raises(HTTPException) as exc:
            await service.checkout("listing-1", "same-user")
        assert exc.value.status_code == 400


@pytest.mark.asyncio
class TestConfirmSandboxPayment:
    async def test_confirm_moves_to_escrow(self, service, repo):
        listing = _listing(status="pending_payment", buyer_id="buyer-1")
        repo.get_listing.return_value = listing

        result = await service.confirm_sandbox_payment(listing.id, "buyer-1")

        assert result["status"] == "locked_in_escrow"
        assert result["transaction_id"].startswith("0xsandbox_deposit_")
        repo.set_listing_status.assert_awaited_once_with(
            listing.id, "locked_in_escrow"
        )

    async def test_confirm_rejects_wrong_buyer(self, service, repo):
        repo.get_listing.return_value = _listing(
            status="pending_payment", buyer_id="buyer-1"
        )
        with pytest.raises(HTTPException) as exc:
            await service.confirm_sandbox_payment("listing-1", "intruder")
        assert exc.value.status_code == 403

    async def test_confirm_rejects_wrong_status(self, service, repo):
        repo.get_listing.return_value = _listing(status="active", buyer_id="buyer-1")
        with pytest.raises(HTTPException) as exc:
            await service.confirm_sandbox_payment("listing-1", "buyer-1")
        assert exc.value.status_code == 409

    async def test_confirm_rejects_missing_listing(self, service, repo):
        repo.get_listing.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.confirm_sandbox_payment("missing", "buyer-1")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
class TestSettlePurchase:
    async def test_settle_records_payout_and_marks_sold(self, service, repo):
        listing = _listing(status="locked_in_escrow", buyer_id="buyer-1")
        repo.get_listing.return_value = listing

        await service.settle_purchase(listing.id, "buyer-1")

        repo.record_payout.assert_awaited_once()
        payout_kwargs = repo.record_payout.await_args.kwargs
        assert payout_kwargs["listing_id"] == listing.id
        assert payout_kwargs["transaction_id"].startswith("0xsandbox_payout_")
        repo.set_listing_status.assert_awaited_once_with(listing.id, "sold")

    async def test_settle_rejects_wrong_buyer(self, service, repo):
        repo.get_listing.return_value = _listing(
            status="locked_in_escrow", buyer_id="buyer-1"
        )
        with pytest.raises(HTTPException) as exc:
            await service.settle_purchase("listing-1", "intruder")
        assert exc.value.status_code == 403

    async def test_settle_rejects_before_escrow(self, service, repo):
        repo.get_listing.return_value = _listing(
            status="pending_payment", buyer_id="buyer-1"
        )
        with pytest.raises(HTTPException) as exc:
            await service.settle_purchase("listing-1", "buyer-1")
        assert exc.value.status_code == 409


@pytest.mark.asyncio
class TestFullSandboxHappyPath:
    async def test_checkout_confirm_settle(self, service, repo):
        listing_id = "22222222-2222-2222-2222-222222222222"
        listing = _listing(listing_id=listing_id)

        # checkout
        repo.get_listing.return_value = listing
        deposit = await service.checkout(listing_id, "buyer-1")
        assert deposit["mode"] == "sandbox"

        # confirm
        listing.status = "pending_payment"
        listing.buyer_id = "buyer-1"
        repo.get_listing.return_value = listing
        confirmed = await service.confirm_sandbox_payment(listing_id, "buyer-1")
        assert confirmed["status"] == "locked_in_escrow"

        # settle
        listing.status = "locked_in_escrow"
        repo.get_listing.return_value = listing
        await service.settle_purchase(listing_id, "buyer-1")
        repo.set_listing_status.assert_awaited_with(listing_id, "sold")


# ---------------------------------------------------------------------------
# WebhookService signature helpers
# ---------------------------------------------------------------------------


class TestWebhookSignature:
    def test_skips_when_secret_unset(self, monkeypatch):
        monkeypatch.delenv("UNIFOLD_WEBHOOK_SECRET", raising=False)
        service = WebhookService(marketplace_repo=MagicMock())
        service.webhook_secret = ""
        service.verify_signature(b'{"ok":true}', None)  # does not raise

    def test_rejects_missing_header_when_secret_set(self):
        service = WebhookService(marketplace_repo=MagicMock())
        service.webhook_secret = "test-secret"
        with pytest.raises(HTTPException) as exc:
            service.verify_signature(b'{"ok":true}', None)
        assert exc.value.status_code == 401

    def test_accepts_valid_hmac(self):
        import hashlib
        import hmac

        secret = "test-secret"
        body = b'{"event_type":"deposit.settled"}'
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        service = WebhookService(marketplace_repo=MagicMock())
        service.webhook_secret = secret
        service.verify_signature(body, signature)  # does not raise

    def test_rejects_invalid_hmac(self):
        service = WebhookService(marketplace_repo=MagicMock())
        service.webhook_secret = "test-secret"
        with pytest.raises(HTTPException) as exc:
            service.verify_signature(b'{"ok":true}', "deadbeef")
        assert exc.value.status_code == 401


@pytest.mark.asyncio
class TestWebhookHandle:
    async def test_deposit_settled_locks_escrow(self):
        repo = MagicMock()
        repo.get_listing = AsyncMock(return_value=_listing())
        repo.set_listing_status = AsyncMock()
        service = WebhookService(marketplace_repo=repo)

        result = await service.handle_webhook(
            {
                "event_type": "deposit.settled",
                "transaction_id": "0xabc",
                "metadata": {"listing_id": "listing-1"},
            }
        )
        assert result["status"] == "ok"
        repo.set_listing_status.assert_awaited_once_with(
            "listing-1", "locked_in_escrow"
        )

    async def test_payout_settled_records_tx(self):
        repo = MagicMock()
        repo.record_payout = AsyncMock()
        service = WebhookService(marketplace_repo=repo)

        await service.handle_webhook(
            {
                "event_type": "payout.settled",
                "transaction_id": "0xdef",
                "metadata": {"listing_id": "listing-1"},
            }
        )
        repo.record_payout.assert_awaited_once_with(
            listing_id="listing-1", transaction_id="0xdef"
        )

    async def test_missing_listing_id_ignored(self):
        service = WebhookService(marketplace_repo=MagicMock())
        result = await service.handle_webhook({"event_type": "deposit.settled"})
        assert "Missing listing_id" in result["message"]
