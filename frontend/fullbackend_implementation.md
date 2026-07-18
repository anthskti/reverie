# FastAPI Endpoints & Architecture Specification

## 1. Directory Structure
```text
backend/
├── main.py                 # FastAPI application instance & router inclusion
├── core/
│   ├── auth.py             # Auth0 JWT verification dependency (JWKS verification)
│   └── config.py           # Environment variables (Unifold, Supabase, Auth0)
├── controllers/            # Thin Route Handlers (decode context, map models)
│   ├── analytics.py        # Global stats (mounted at /api/stats)
│   ├── inventory.py        # User wardrobe & profile (mounted at /api/inventory)
│   ├── pipeline.py         # Google GenAI Agent pipeline (mounted at /api/upcycle)
│   ├── projects.py         # User active projects (mounted at /api/projects)
│   ├── marketplace.py      # Unifold Commerce Marketplace (mounted at /api/marketplace)
│   └── webhooks.py         # Third-party webhook endpoints (mounted at /api/webhooks)
├── services/               # Core Business Logic Layer
│   ├── analytics.py        # Analytics stats calculations
│   ├── inventory.py        # Garment profiles and lazy stats synchronization
│   ├── projects.py         # User active projects queries
│   ├── pipeline.py         # Agentic workflows runner and parameters parsing
│   ├── marketplace.py      # Listing lifecycles, checkout session handling, and webhook dispatches
│   └── unifold.py          # Sandbox Checkout & Payout API wrapper
├── models/                 # SQLAlchemy DB Models (Item, Project, UserStats, MarketplaceListing)
└── repositories/           # SQLAlchemy DB Repositories (inventory, upcycle, marketplace)
```

## 2. Authentication Architecture (Auth0 JWT Validation)
All user-facing endpoints (except global stats and public marketplace feeds) are secured using the `verify_token` dependency found in `backend/core/auth.py`. 
* **Mechanics**: The backend extracts the bearer token from the `Authorization` header, dynamically fetches the JSON Web Key Set (JWKS) from Auth0's public `.well-known/jwks.json` endpoint, cryptographically validates the token's signature, and checks the expiration (`exp`) and audience (`aud`).
* **Anti-Spoofing Identity Control**: Clients **no longer** pass `user_id` as part of the request payload. Instead, the backend extracts the Auth0 User ID securely from the JWT's `sub` claim.
* **Testing Override**: If the environment variable `TESTING=True` is set, the JWKS check is bypassed, and a mock subject ID (`qa_test_user_123` or custom suffix `mock_token_{sub}`) is injected to facilitate offline/CI execution.

## 3. Subsystems Specification

### A. Analytics Subsystem (controllers/analytics.py & services/analytics.py)
No authentication required for global stats. Mounted at `/api/stats`.

#### GET /api/stats/global
* **Service Logic**: Aggregates `water_saved_l`, `co2_offset_kg`, and `landfill_diverted_kg` across all rows in the `user_stats` table.
* **Returns**: JSON object containing aggregated platform totals.

---

### B. Inventory & Profile Subsystem (controllers/inventory.py & services/inventory.py)
All endpoints require Auth0 JWT validation (`Depends(verify_token)`). Mounted at `/api/inventory`.

#### GET /api/inventory/me/stats
* **Service Logic**: Fetches the environmental impact row from the user_stats table where `user_id == token.sub`.

#### GET /api/inventory/me
* **Service Logic**: Fetches all physical garments from `items` where `user_id == token.sub`.

#### GET /api/inventory/{item_id}
* **Service Logic**: Fetches the specific item ensuring it belongs to `token.sub`.

---

### C. Agentic AI Pipeline Subsystem (controllers/pipeline.py & services/pipeline.py)
Supported on Vertex AI (GCP Service Account credentials) and Gemini AI Studio fallbacks. Requires Auth0 JWT validation. Mounted at `/api/upcycle`.

#### POST /api/upcycle/ideate
* **Payload**: `multipart/form-data` (Image file, style, difficulty, fabric_type, weight_kg, tools_available, generate_mockups).
* **Service Logic**:
  - Uploads base image to storage. Under local offline mode (when Supabase is unconfigured), it saves the image to a local `static/inventory` directory and returns a `/static/inventory/...` URL.
  - Triggers the Designer Agent using `gemini-2.5-flash-lite` to generate 3 upcycling concepts. Its system instructions enforce generating realistic variations that preserve the core garment type of the uploaded item.
  - If `generate_mockups` is True, triggers the Style Agent using `gemini-2.5-flash-image` to render mockups on a 2D silhouette mannequin.
  - Creates a row in the `items` table using the `user_id` extracted from the Auth0 token.
* **Returns**: Generated Item ID, the 3 concept options, and generated mockup URLs.

#### POST /api/upcycle/execute
* **Payload**: `JSON` (item_id, selected_concept, fabric_type, weight_kg).
* **Service Logic**:
  - Concurrently triggers Sewing Guide Agent (`gemini-2.5-flash-lite`) and Environmental Impact Agent (`gemini-2.5-flash-lite`).
  - Structured metrics (`water_saved_liters`, `co2_offset_kg`, `landfill_diverted_kg`) are computed locally.
  - Creates a row in the `projects` table and updates environmental impact statistics for the user in `user_stats`.
* **Returns**: Created Project ID, sewing guide markdown, environmental narrative, structured impact data, and the selected mockup URL.

#### POST /api/upcycle/{item_id}/verify
* **Payload**: `multipart/form-data` (Image of the completed physical garment).
* **Service Logic**:
  - Loads the item and its active project, including the associated mockup image.
  - Triggers the QC Verification Agent (`gemini-2.5-flash-lite`) to perform a visual multimodal comparison evaluating design accuracy to the mockup and craftsmanship.
  - Calculates verification score. (Informational only — does not restrict listing items on the marketplace).
* **Returns**: Validation score and detailed constructive feedback.

---

### D. Marketplace Subsystem (controllers/marketplace.py & services/marketplace.py)
Mounted at `/api/marketplace`. Secure endpoints require Auth0 JWT validation.

#### POST /api/marketplace/list
* **Payload**: `JSON` (title, description, price_usdc, category, item_id [optional]).
* **Categories**: `upcycled_clothing`, `material`, `tool`.
* **Service Logic**:
  - If category is `upcycled_clothing`: Requires an `item_id` and verifies the user owns that item.
  - If category is `material` or `tool`: Bypasses inventory checking (`item_id` is optional).
  - Creates a row in `marketplace_listings` with status = `'active'`.
* **Returns**: `listing_id`.

#### PATCH /api/marketplace/{listing_id}
* **Payload**: `JSON` (optional title, price_usdc, description, status).
* **Service Logic**: Updates listing columns. Only the owning seller can call this. Sellers can only set status directly to `'cancelled'`.

#### GET /api/marketplace
* **Service Logic**: Fetches active listings. Supports category filtering (`?category=`) and keyword search (`?q=`).

#### GET /api/marketplace/{listing_id}
* **Service Logic**: Fetches details for a specific listing (no auth required).

#### POST /api/marketplace/checkout/{listing_id}
* **Service Logic**: Called by the buyer to purchase an active item.
  - Verifies listing status is `'active'` and the buyer is not the seller.
  - Creates a Unifold checkout session using the seller's wallet destination.
  - Transitions listing status to `'pending_payment'` and records the `buyer_id`.
* **Returns**: `checkout_url`.

#### POST /api/marketplace/settle/{listing_id}
* **Service Logic**: Called by the buyer when the physical item arrives.
  - Verifies the listing status is `'locked_in_escrow'` and caller matches the recorded `buyer_id`.
  - Triggers Unifold Payout API to disburse escrowed funds to the seller (protected with an `Idempotency-Key` based on the `listing_id`).
  - Sets listing status to `'sold'`.

---

### E. Webhooks Subsystem (controllers/webhooks.py & services/marketplace.py)
Mounted at `/api/webhooks`. No Auth0 token required, but uses cryptographic signature verification.

#### POST /api/webhooks/unifold
* **Payload**: `JSON` from Unifold containing event context, signature header `X-Unifold-Signature`.
* **Service Logic**:
  - Validates the signature header against the payload using `UNIFOLD_WEBHOOK_SECRET` via HMAC-SHA256.
  - If `event_type == 'deposit.settled'`: Updates `marketplace_listings` status to `'locked_in_escrow'` (signaling it is safe for the seller to ship).
  - If `event_type == 'payout.settled'`: Records the payment transaction hash (`transaction_id`) on the listing.
  - Always returns `200 OK` to ensure webhooks are successfully acknowledged.