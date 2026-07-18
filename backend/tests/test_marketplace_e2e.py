import sys
import uuid
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def run_marketplace_tests():
    print("=" * 60)
    print("STARTING E2E QA TESTING FOR MARKETPLACE SUBSYSTEM")
    print("=" * 60)

    # Initialize two clients to simulate different users
    seller_client = httpx.Client(base_url=BASE_URL, timeout=10.0, headers={"Authorization": "Bearer mock_token_seller_user"})
    buyer_client = httpx.Client(base_url=BASE_URL, timeout=10.0, headers={"Authorization": "Bearer mock_token_buyer_user"})

    material_listing_id = None
    garment_listing_id = None
    dummy_item_id = str(uuid.uuid4())

    try:
        # 0. Health check
        print("\n[Step 0] Verifying Health Check...")
        res = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        print("Health status:", data)
        assert data["database_configured"] is True, "Database must be configured for E2E tests"

        # 1. Seller lists a raw material (bypasses QC check, item_id optional)
        print("\n[Step 1] Seller lists a material...")
        material_data = {
            "title": "Vintage Denim Fabric",
            "description": "2 yards of high quality 90s denim",
            "price_usdc": 15.5,
            "category": "material"
        }
        res = seller_client.post("/api/marketplace/list", json=material_data)
        assert res.status_code == 201, f"Material listing failed: {res.text}"
        material_listing_id = res.json()["listing_id"]
        print(f"Passed: Material listed successfully with ID: {material_listing_id}")

        # 2. Browse marketplace to ensure the material appears
        print("\n[Step 2] Browse marketplace (unauthenticated)...")
        res = httpx.get(f"{BASE_URL}/api/marketplace")
        assert res.status_code == 200, f"Browse failed: {res.text}"
        listings = res.json()
        print(f"Passed: Fetched {len(listings)} active listings.")
        found = next((l for l in listings if l["listing_id"] == material_listing_id), None)
        assert found is not None, "Newly created material listing not found in marketplace!"
        print(f"Passed: Material listing is visible in the marketplace.")

        # 3. Browse with filter
        print("\n[Step 3] Browse marketplace with category filter...")
        res = httpx.get(f"{BASE_URL}/api/marketplace?category=material")
        assert res.status_code == 200
        filtered_listings = res.json()
        assert all(l["category"] == "material" for l in filtered_listings), "Filter failed"
        print("Passed: Category filter works correctly.")

        # 4. Buyer initiates checkout
        print("\n[Step 4] Buyer initiates checkout...")
        res = buyer_client.post(f"/api/marketplace/checkout/{material_listing_id}")
        assert res.status_code == 200, f"Checkout failed: {res.text}"
        checkout_data = res.json()
        print(f"Checkout URL generated: {checkout_data['checkout_url']}")
        assert checkout_data["status"] == "pending_payment"
        print("Passed: Checkout session created, listing status -> pending_payment.")

        # Verify listing no longer shows in active browse
        res = httpx.get(f"{BASE_URL}/api/marketplace")
        active_ids = [l["listing_id"] for l in res.json()]
        assert material_listing_id not in active_ids, "Pending payment listing should not be in active browse"
        print("Passed: pending_payment listing hidden from marketplace.")

        # 5. Simulate Unifold deposit.settled Webhook (Buyer pays)
        print("\n[Step 5] Simulate Unifold Webhook (deposit.settled)...")
        # In testing mode, the webhook ignores signature verification when secret is missing,
        # but let's test the endpoint logic anyway.
        webhook_payload = {
            "event_type": "deposit.settled",
            "transaction_id": "0xABC123",
            "metadata": {
                "listing_id": material_listing_id,
                "buyer_id": "mock_token_buyer_user"
            }
        }
        res = httpx.post(f"{BASE_URL}/api/webhooks/unifold", json=webhook_payload)
        assert res.status_code == 200, f"Webhook failed: {res.text}"
        print("Passed: deposit.settled webhook accepted.")

        # Verify listing status is now locked_in_escrow
        res = httpx.get(f"{BASE_URL}/api/marketplace/{material_listing_id}")
        assert res.status_code == 200
        assert res.json()["status"] == "locked_in_escrow"
        print("Passed: Listing status updated to locked_in_escrow.")

        # 6. Buyer Settles Purchase
        print("\n[Step 6] Buyer Settles Purchase (Item Received)...")
        res = buyer_client.post(f"/api/marketplace/settle/{material_listing_id}")
        assert res.status_code == 200, f"Settle failed: {res.text}"
        settle_data = res.json()
        assert settle_data["status"] == "sold"
        print("Passed: Settle successful, listing status -> sold.")

        # 7. Simulate Unifold payout.settled Webhook
        print("\n[Step 7] Simulate Unifold Webhook (payout.settled)...")
        webhook_payload_payout = {
            "event_type": "payout.settled",
            "transaction_id": "0xDEF456",
            "metadata": {
                "listing_id": material_listing_id
            }
        }
        res = httpx.post(f"{BASE_URL}/api/webhooks/unifold", json=webhook_payload_payout)
        assert res.status_code == 200, f"Webhook failed: {res.text}"
        print("Passed: payout.settled webhook accepted.")

        # Verify transaction ID is recorded
        res = httpx.get(f"{BASE_URL}/api/marketplace/{material_listing_id}")
        assert res.json()["transaction_id"] == "0xDEF456"
        print("Passed: Transaction hash recorded on listing.")

        # 8. Test Seller Cannot Buy Own Item
        print("\n[Step 8] Test seller cannot buy own item...")
        tool_data = {
            "title": "Sewing Machine",
            "price_usdc": 100.0,
            "category": "tool"
        }
        res = seller_client.post("/api/marketplace/list", json=tool_data)
        assert res.status_code == 201
        tool_listing_id = res.json()["listing_id"]
        
        res = seller_client.post(f"/api/marketplace/checkout/{tool_listing_id}")
        assert res.status_code == 400
        print(f"Passed: Seller blocked from self-checkout ({res.json()['detail']})")

        print("\n" + "=" * 60)
        print("ALL MARKETPLACE E2E QA TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except AssertionError as e:
        print("\n" + "!" * 60)
        print(f"QA TEST ASSERTION FAILURE: {e}")
        print("!" * 60)
        sys.exit(1)
    except Exception as e:
        print("\n" + "!" * 60)
        print(f"QA TEST UNEXPECTED ERROR: {e}")
        print("!" * 60)
        sys.exit(1)

if __name__ == "__main__":
    run_marketplace_tests()
