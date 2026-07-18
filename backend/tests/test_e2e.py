import sys
import io
import json
import uuid
import httpx
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def create_dummy_image(color="red") -> bytes:
    """Load the user's specific mockimage.jpg to simulate garment upload."""
    try:
        with open("/Users/anthonypham/Work/reverie/backend/static/mockups/mockup1/mockimage.jpg", "rb") as f:
            return f.read()
    except Exception as e:
        # Fallback to dummy if file not found
        img = Image.new("RGB", (128, 128), color=color)
        byte_arr = io.BytesIO()
        img.save(byte_arr, format="JPEG")
        return byte_arr.getvalue()

def run_tests():
    print("=" * 60)
    print("STARTING END-TO-END QA TESTING FOR REVERIE BACKEND")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=60.0, headers={"Authorization": "Bearer mock_token"})
    item_id = None
    selected_concept = None
    project_id = None

    try:
        # 0. Health check
        print("\n[Step 0] Verifying Health Check...")
        res = client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        print("Health status:", data)
        assert data["database_configured"] is True, "Database must be configured for E2E tests"

        # 1. Phase 1: Ideation (Happy Path)
        print("\n[Step 1] Phase 1: Ideation (Happy Path)...")
        dummy_image = create_dummy_image("blue")
        files = {
            "image": ("garment.jpg", dummy_image, "image/jpeg")
        }
        data = {
            "style": "vintage 90s streetwear",
            "difficulty": "medium",
            "fabric_type": "denim",
            "weight_kg": "0.75",
            "tools_available": '["scissors", "sewing machine", "fabric paint"]',
            "generate_mockups": "true"
        }
        res = client.post("/upcycle/ideate", data=data, files=files)
        assert res.status_code == 200, f"Ideation failed: {res.text}"
        ideation_data = res.json()
        print("Ideation response status code: 200")
        assert "item_id" in ideation_data
        assert "options" in ideation_data
        assert len(ideation_data["options"]) == 3
        
        item_id = ideation_data["item_id"]
        selected_concept = ideation_data["options"][0]
        
        print(f"Generated Item ID: {item_id}")
        print("Suggested Concepts:")
        for idx, option in enumerate(ideation_data["options"]):
            print(f"  {idx + 1}. {option['title']} (Difficulty: {option['difficulty']})")
            print(f"     Description: {option['description']}")
            print(f"     Techniques: {', '.join(option['techniques'])}")

        # 2. Phase 1: Ideation (Negative Paths / Edge Cases)
        print("\n[Step 2] Testing Ideation Edge Cases...")
        
        # 2a. Invalid JSON in tools_available
        print("  - Case A: Invalid JSON in tools_available")
        bad_data = data.copy()
        bad_data["tools_available"] = "[invalid json]"
        res = client.post("/upcycle/ideate", data=bad_data, files=files)
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        print(f"    Passed: 400 Bad Request returned: {res.json()['detail']}")

        # 2b. Empty image upload
        print("  - Case B: Empty image upload")
        empty_files = {
            "image": ("garment.jpg", b"", "image/jpeg")
        }
        res = client.post("/upcycle/ideate", data=data, files=empty_files)
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        print(f"    Passed: 400 Bad Request returned: {res.json()['detail']}")

        # 3. Phase 2: Execution (Happy Path)
        print("\n[Step 3] Phase 2: Execution (Happy Path)...")
        exec_payload = {
            "item_id": item_id,
            "selected_concept": selected_concept,
            "fabric_type": "denim",
            "weight_kg": 0.75
        }
        res = client.post("/upcycle/execute", json=exec_payload)
        assert res.status_code == 200, f"Execution failed: {res.text}"
        exec_data = res.json()
        print("Execution response status code: 200")
        assert "project_id" in exec_data
        assert "sewing_guide" in exec_data
        assert "environmental_impact" in exec_data
        assert "environmental_data" in exec_data
        
        project_id = exec_data["project_id"]
        sewing_guide = exec_data["sewing_guide"]
        env_data = exec_data["environmental_data"]

        print(f"Created Project ID: {project_id}")
        print(f"Water Saved: {env_data.get('water_saved_liters')} Liters")
        print(f"CO2 Offset: {env_data.get('co2_offset_kg')} kg")
        print(f"Sewing Guide sample:\n{sewing_guide[:200]}...")

        # 4. Phase 2: Execution Edge Cases
        print("\n[Step 4] Testing Execution Edge Cases...")
        # 4a. Missing fields (validation error)
        print("  - Case A: Missing selected_concept")
        bad_payload = {
            "item_id": item_id,
            "fabric_type": "denim",
            "weight_kg": 0.75
        }
        res = client.post("/upcycle/execute", json=bad_payload)
        assert res.status_code == 422, f"Expected 422, got {res.status_code}"
        print("    Passed: 422 Unprocessable Entity returned.")

        # 5. Phase 3: Verification (Happy Path)
        print("\n[Step 5] Phase 3: Verification (Happy Path)...")
        completed_image = create_dummy_image("green")
        files_verification = {
            "image": ("completed.jpg", completed_image, "image/jpeg")
        }
        res = client.post(f"/upcycle/{item_id}/verify", files=files_verification)
        assert res.status_code == 200, f"Verification failed: {res.text}"
        verification_data = res.json()
        print("Verification response status code: 200")
        assert "score" in verification_data
        assert "is_eligible" in verification_data
        assert "feedback" in verification_data
        print(f"QC Score: {verification_data['score']}")
        print(f"Marketplace Eligible: {verification_data['is_eligible']}")
        print(f"Feedback: {verification_data['feedback']}")

        # 6. Phase 3: Verification Edge Cases
        print("\n[Step 6] Testing Verification Edge Cases...")
        
        # 6a. Non-existent item_id
        print("  - Case A: Non-existent item_id")
        fake_item_id = str(uuid.uuid4())
        res = client.post(f"/upcycle/{fake_item_id}/verify", files=files_verification)
        assert res.status_code == 404, f"Expected 404, got {res.status_code}: {res.text}"
        print(f"    Passed: 404 Not Found returned: {res.json()['detail']}")

        # 6b. Verification without execution first
        print("  - Case B: Verification on item with no execution project")
        # Run ideation to get a new item_id
        dummy_image_c = create_dummy_image("yellow")
        files_c = {"image": ("garment.jpg", dummy_image_c, "image/jpeg")}
        res = client.post("/upcycle/ideate", data=data, files=files_c)
        assert res.status_code == 200
        new_item_id = res.json()["item_id"]
        # Try to verify right away
        res = client.post(f"/upcycle/{new_item_id}/verify", files=files_verification)
        assert res.status_code == 404, f"Expected 404, got {res.status_code}: {res.text}"
        print(f"    Passed: 404 Not Found returned: {res.json()['detail']}")

        # 7. Project Listing for User
        print("\n[Step 7] Checking Project Listing for user...")
        res = client.get("/projects/")
        assert res.status_code == 200, f"Listing projects failed: {res.text}"
        list_data = res.json()
        print(f"Projects returned: {len(list_data['projects'])}")
        assert len(list_data["projects"]) > 0
        found_project = False
        for p in list_data["projects"]:
            if p["id"] == project_id:
                found_project = True
                assert p["item_id"] == item_id
                assert p["selected_concept"]["title"] == selected_concept["title"]
                assert p["environmental_data"]["water_saved_liters"] == env_data["water_saved_liters"]
                break
        assert found_project, "The created project was not found in the user's project list"
        print("    Passed: User project list verified successfully.")

        # 8. Stats & Inventory Listing
        print("\n[Step 8] Checking Global Stats & Inventory Profile...")
        
        # 8a. Global Stats
        res = client.get("/stats/global")
        assert res.status_code == 200, f"Global stats failed: {res.text}"
        print("    Passed: Global Stats fetched successfully")
        
        # 8b. User Stats (Lazy Creation Sync test)
        res = client.get("/inventory/me/stats")
        assert res.status_code == 200, f"User stats failed: {res.text}"
        print("    Passed: User Stats fetched successfully (lazy sync triggered)")
        
        # 8c. User Items
        res = client.get("/inventory/me")
        assert res.status_code == 200, f"User items failed: {res.text}"
        items_list = res.json()
        print(f"    Passed: User Items fetched successfully: found {len(items_list)} items")

        print("\n" + "=" * 60)
        print("ALL END-TO-END QA TESTS COMPLETED SUCCESSFULLY!")
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
    run_tests()
