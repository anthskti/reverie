"""Integration test: verify generate_sewing_guide returns the full sewing guide.

The bug was that response.text only returned text from the LAST model turn
after a tool call. This test confirms _collect_full_text fixes that by checking
that all major sections of the guide are present in the output.

Run from the backend/ directory:
    uv run python -m pytest tests/test_sewing_guide_full_text.py -v -s
"""

import os
import re
import sys

import pytest

# Ensure backend root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env so Vertex / Gemini credentials are available
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def make_client():
    from google import genai
    from agents.auth_vertex import setup_vertex_credentials

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    api_key = os.getenv("GEMINI_API_KEY")

    if project or creds_json:
        setup_vertex_credentials()
        return genai.Client(
            vertexai=True,
            project=project,
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    elif api_key:
        return genai.Client(api_key=api_key)
    else:
        pytest.skip("No Gemini credentials found — set GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT")


# A realistic concept dict similar to what the workflow passes in
SAMPLE_CONCEPT = {
    "title": "Cropped Stripe Dress",
    "description": (
        "Transform a striped button-down shirt into a chic cropped dress "
        "by lengthening the hem with a contrasting fabric panel and adding "
        "a tie belt at the waist."
    ),
    "techniques": ["cutting", "hemming", "adding fabric panel", "tie belt"],
    "difficulty": "medium",
    "mockup_url": None,
}


def test_generate_sewing_guide_is_complete():
    """The guide must contain multiple numbered steps, not just the final one."""
    from agents.runner import generate_sewing_guide

    client = make_client()
    guide = generate_sewing_guide(client, SAMPLE_CONCEPT)

    print("\n--- SEWING GUIDE OUTPUT ---")
    print(guide)
    print("--- END ---\n")
    print(f"Total characters: {len(guide)}")

    # Basic completeness checks
    assert guide, "Guide should not be empty"
    assert len(guide) > 300, (
        f"Guide is suspiciously short ({len(guide)} chars) — likely truncated. "
        "Check _collect_full_text is working."
    )

    # The guide should have multiple step markers (##, Step, or numbered list)
    step_markers = re.findall(r"(?:^|\n)(?:#{1,3}\s*Step\s*\d|Step\s*\d|\d+\.\s)", guide)
    print(f"Step markers found: {step_markers}")
    assert len(step_markers) >= 2, (
        f"Expected at least 2 step markers, found {len(step_markers)}. "
        "The guide may be missing early steps due to the tool-call truncation bug."
    )


def test_collect_full_text_falls_back_to_response_text():
    """_collect_full_text should return response.text when no history is present."""
    from agents.runner import _collect_full_text

    class FakeResponse:
        text = "Hello world"
        automatic_function_calling_history = []

    result = _collect_full_text(FakeResponse())
    assert result == "Hello world"


def test_collect_full_text_uses_history_when_present():
    """_collect_full_text should prefer history text over response.text."""
    from agents.runner import _collect_full_text

    class FakePart:
        def __init__(self, text):
            self.text = text

    class FakeMessage:
        def __init__(self, role, texts):
            self.role = role
            self.parts = [FakePart(t) for t in texts]

    class FakeResponse:
        text = "Only final step"
        automatic_function_calling_history = [
            FakeMessage("model", ["Step 1: Do this\n\nStep 2: Do that\n\n"]),
            FakeMessage("user", []),   # tool result — should be skipped
            FakeMessage("model", ["Step 3: Finishing touches"]),
        ]

    result = _collect_full_text(FakeResponse())
    print(f"\n_collect_full_text result:\n{result}")

    assert "Step 1" in result, "Step 1 should be included from first model turn"
    assert "Step 2" in result, "Step 2 should be included from first model turn"
    assert "Step 3" in result, "Step 3 should be included from final model turn"
    assert "Only final step" not in result, "response.text should not be used when history has content"
