"""Reverie seed script.

Creates per-user:
  • 1 Auth0 account (via Management API — skipped gracefully if not authorized)
  • 1 inventory Item  (upcycled piece, original_image_url=None)
  • 3 MarketplaceListing rows  (tool + upcycled_clothing + material/accessory)
  • 1 UserStats row (realistic environmental impact numbers)

Usage
-----
    uv run python scripts/seeding.py [--clear-existing]

Auth0 Management API
--------------------
Set these in backend/.env (never commit real values):

    AUTH0_DOMAIN=...
    AUTH0_MGMT_CLIENT_ID=...      # Machine-to-Machine application
    AUTH0_MGMT_CLIENT_SECRET=...

Authorize that M2M app for the Auth0 Management API with create:users
(and read:users). If credentials are missing or unauthorized, the script
falls back to placeholder user IDs so DB rows are still created.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import delete

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from database.connection import SessionLocal, init_models, is_configured
from models.item import Item
from models.marketplace_listing import MarketplaceListing
from models.user_stats import UserStats

# ---------------------------------------------------------------------------
# Auth0 config — from env only (no secret defaults in source)
# ---------------------------------------------------------------------------

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_MGMT_CLIENT_ID = os.getenv("AUTH0_MGMT_CLIENT_ID")
AUTH0_MGMT_CLIENT_SECRET = os.getenv("AUTH0_MGMT_CLIENT_SECRET")


def _auth0_mgmt_configured() -> bool:
    return bool(AUTH0_DOMAIN and AUTH0_MGMT_CLIENT_ID and AUTH0_MGMT_CLIENT_SECRET)

# ---------------------------------------------------------------------------
# Seed personas
# ---------------------------------------------------------------------------


@dataclass
class Persona:
    name: str
    email: str
    password: str
    # Inventory item fields
    item_style: str
    item_fabric: str
    item_weight_kg: float
    item_difficulty: str
    item_title: str          # for the marketplace upcycled_clothing listing
    item_description: str
    item_price_usdc: float
    # Tool listing
    tool_title: str
    tool_description: str
    tool_price_usdc: float
    # Material/accessory listing
    material_title: str
    material_description: str
    material_price_usdc: float
    # Environmental impact
    water_saved_l: float
    co2_offset_kg: float
    landfill_diverted_kg: float


PERSONAS: list[Persona] = [
    Persona(
        name="Alex Chen",
        email="alex.chen@reverie-seed.dev",
        password="Reverie!Seed1",
        item_style="streetwear",
        item_fabric="denim",
        item_weight_kg=0.82,
        item_difficulty="medium",
        item_title="Upcycled Denim Patchwork Tote",
        item_description=(
            "Heavy-duty denim tote stitched from salvaged jacket panels. "
            "Raw-edge patchwork exterior with interior canvas pocket. "
            "One-of-a-kind carry companion."
        ),
        item_price_usdc=34.00,
        tool_title="Reliable Rotary Cutter Set",
        tool_description=(
            "45 mm Olfa rotary cutter with 3 replacement blades. "
            "Great for cutting clean curves through denim and heavy canvas. "
            "Lightly used, still sharp."
        ),
        tool_price_usdc=18.50,
        material_title="Antique Brass O-Ring & Chain Pack",
        material_description=(
            "10-piece set of antique-brass O-rings (25 mm) and matching "
            "12-inch curb chain — perfect for bag straps, keychains, or "
            "garment hardware. Unopened."
        ),
        material_price_usdc=9.00,
        water_saved_l=410.0,
        co2_offset_kg=3.1,
        landfill_diverted_kg=0.82,
    ),
    Persona(
        name="Maya Rivera",
        email="maya.rivera@reverie-seed.dev",
        password="Reverie!Seed2",
        item_style="boho",
        item_fabric="cotton",
        item_weight_kg=0.45,
        item_difficulty="easy",
        item_title="Cropped Floral Crop Top",
        item_description=(
            "Vintage oversized floral shirt transformed into a breezy "
            "boho crop top with knotted hem and flutter sleeves. "
            "Size M/L — runs slightly loose."
        ),
        item_price_usdc=22.00,
        tool_title="Mini Sewing Awl & Leather Punch Kit",
        tool_description=(
            "Speedy Stitcher sewing awl with 2 needles + a 6-hole leather "
            "punch. Ideal for hand-stitching bags, belts, and thick fabrics. "
            "Gently used."
        ),
        tool_price_usdc=14.00,
        material_title="Rit Dye Bundle — Cobalt & Mustard",
        material_description=(
            "Two 8 oz bottles of Rit All-Purpose liquid dye: one cobalt blue, "
            "one golden mustard. Never opened. Great for overdyeing cotton, "
            "linen, and rayon."
        ),
        material_price_usdc=12.50,
        water_saved_l=225.0,
        co2_offset_kg=1.7,
        landfill_diverted_kg=0.45,
    ),
    Persona(
        name="Jules Park",
        email="jules.park@reverie-seed.dev",
        password="Reverie!Seed3",
        item_style="vintage",
        item_fabric="corduroy",
        item_weight_kg=0.91,
        item_difficulty="medium",
        item_title="Corduroy Crossbody Bag",
        item_description=(
            "Repurposed corduroy trousers reshaped into a structured "
            "crossbody bag with a zip closure and card-slot interior pocket. "
            "Earthy brown colorway."
        ),
        item_price_usdc=41.00,
        tool_title="Janome HD1000 Heavy-Duty Machine",
        tool_description=(
            "Janome HD1000 mechanical sewing machine in excellent condition. "
            "Handles denim, canvas, and corduroy with ease. "
            "Includes all original attachments and manual."
        ),
        tool_price_usdc=195.00,
        material_title="YKK #5 Zipper Tape Roll — 3 m Black",
        material_description=(
            "3-metre roll of YKK #5 continuous zipper tape with 6 metal "
            "sliders included. Cut to any length. Perfect for bags, jackets, "
            "and cushions. Unused."
        ),
        material_price_usdc=8.00,
        water_saved_l=455.0,
        co2_offset_kg=3.4,
        landfill_diverted_kg=0.91,
    ),
    Persona(
        name="Nina Osei",
        email="nina.osei@reverie-seed.dev",
        password="Reverie!Seed4",
        item_style="minimalist",
        item_fabric="silk",
        item_weight_kg=0.22,
        item_difficulty="hard",
        item_title="Silk Patchwork Bi-fold Wallet",
        item_description=(
            "Hand-stitched wallet made from panels of three vintage silk "
            "blouses — each in a different muted tone. Holds 6 cards and "
            "cash. Lined with iron-on interfacing for structure."
        ),
        item_price_usdc=28.00,
        tool_title="Clover Iron-On Interfacing Sheets × 10",
        tool_description=(
            "10 sheets (28 × 43 cm) of Clover woven iron-on interfacing — "
            "medium weight, perfect for wallets, bag bases, and collar "
            "stiffening. Half the pack used."
        ),
        tool_price_usdc=7.50,
        material_title="Velcro Sew-On Tape — 2 m White & Black",
        material_description=(
            "2 metres each of hook-and-loop sew-on Velcro in white and "
            "black. 2 cm wide. Ideal for closures on bags, pouches, and "
            "children's clothing. Brand new."
        ),
        material_price_usdc=6.00,
        water_saved_l=110.0,
        co2_offset_kg=0.8,
        landfill_diverted_kg=0.22,
    ),
    Persona(
        name="Omar Hassan",
        email="omar.hassan@reverie-seed.dev",
        password="Reverie!Seed5",
        item_style="workwear",
        item_fabric="canvas",
        item_weight_kg=1.35,
        item_difficulty="hard",
        item_title="Reworked Canvas Cargo Pants",
        item_description=(
            "Heavily deconstructed canvas workwear trousers rebuilt with "
            "four cargo pockets, reinforced knee patches, and a drawstring "
            "ankle cuff. Size 32W / 30L. Sustainable luxury."
        ),
        item_price_usdc=68.00,
        tool_title="Seam Ripper + Tailor Chalk Set",
        tool_description=(
            "Clover seam ripper (3-pack) and a 6-piece tailor chalk set "
            "(white, blue, yellow). Essential unpicking and marking tools. "
            "All unused."
        ),
        tool_price_usdc=11.00,
        material_title="Cyanotype Fabric Dye Kit",
        material_description=(
            "Sun-print cyanotype kit for fabric — two 120 ml bottles "
            "(sensitizer A & B), squeegee, and instruction card. "
            "Creates stunning indigo-blue prints on natural fibres."
        ),
        material_price_usdc=19.00,
        water_saved_l=675.0,
        co2_offset_kg=5.1,
        landfill_diverted_kg=1.35,
    ),
]

# ---------------------------------------------------------------------------
# Auth0 Management API helpers
# ---------------------------------------------------------------------------


async def _get_mgmt_token() -> str | None:
    """Obtain a short-lived Management API token using client credentials.

    Returns None (with a printed warning) if credentials are missing or
    the M2M client isn't authorized for the Management API.
    """
    import httpx

    if not _auth0_mgmt_configured():
        missing = [
            name
            for name, value in (
                ("AUTH0_DOMAIN", AUTH0_DOMAIN),
                ("AUTH0_MGMT_CLIENT_ID", AUTH0_MGMT_CLIENT_ID),
                ("AUTH0_MGMT_CLIENT_SECRET", AUTH0_MGMT_CLIENT_SECRET),
            )
            if not value
        ]
        print(
            "  [Auth0] Missing env vars: "
            + ", ".join(missing)
            + ". Add them to backend/.env (M2M app credentials). "
            "Using placeholder user IDs instead.\n"
        )
        return None

    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AUTH0_MGMT_CLIENT_ID,
        "client_secret": AUTH0_MGMT_CLIENT_SECRET,
        "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        print(
            f"  [Auth0] Could not obtain Management API token "
            f"(HTTP {resp.status_code}). "
            "Authorize your M2M app for Auth0 Management API with "
            "create:users (and read:users). Using placeholder user IDs instead.\n"
        )
        return None

    return resp.json()["access_token"]


async def _create_auth0_user(token: str, persona: Persona) -> str | None:
    """Create one Auth0 user. Returns the user_id (sub) or None on failure."""
    import httpx

    url = f"https://{AUTH0_DOMAIN}/api/v2/users"
    payload = {
        "connection": "Username-Password-Authentication",
        "email": persona.email,
        "password": persona.password,
        "name": persona.name,
        "email_verified": True,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    data = resp.json()

    # 409 = already exists — fetch the existing user_id
    if resp.status_code == 409:
        print(f"  [Auth0] {persona.email} already exists — looking up user_id…")
        search_url = (
            f"https://{AUTH0_DOMAIN}/api/v2/users-by-email?email={persona.email}"
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            search = await client.get(search_url, headers=headers)
        users = search.json()
        if users:
            uid = users[0]["user_id"]
            print(f"  [Auth0] Found: {uid}")
            return uid
        return None

    if resp.status_code not in (200, 201):
        print(f"  [Auth0] Failed to create {persona.email}: {data.get('message', resp.text)}")
        return None

    uid = data["user_id"]
    print(f"  [Auth0] Created {persona.email} → {uid}")
    return uid


async def create_auth0_users(personas: list[Persona]) -> dict[str, str]:
    """Returns {persona.email: auth0_user_id}. Falls back to placeholder IDs."""
    print("\n[Step 1] Creating Auth0 users…")
    token = await _get_mgmt_token()

    result: dict[str, str] = {}

    if token is None:
        for i, p in enumerate(personas, start=1):
            fallback = f"auth0|seed-user-{p.name.split()[0].lower()}"
            result[p.email] = fallback
            print(f"  Fallback ID for {p.email}: {fallback}")
        return result

    for persona in personas:
        uid = await _create_auth0_user(token, persona)
        if uid is None:
            uid = f"auth0|seed-user-{persona.name.split()[0].lower()}"
            print(f"  Fallback ID for {persona.email}: {uid}")
        result[persona.email] = uid

    return result


# ---------------------------------------------------------------------------
# Database seeding
# ---------------------------------------------------------------------------


async def seed_database(
    personas: list[Persona],
    user_id_map: dict[str, str],
    clear_existing: bool = False,
) -> None:
    if not is_configured():
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set DATABASE_URL in backend/.env before running this script."
        )

    await init_models()

    if SessionLocal is None:
        raise RuntimeError("Database session factory is not available.")

    async with SessionLocal() as session:
        if clear_existing:
            print("\n[Step 2] Clearing existing data…")
            await session.execute(delete(MarketplaceListing))
            await session.execute(delete(Item))
            await session.execute(delete(UserStats))
            await session.commit()
            print("  Cleared marketplace_listings, items, user_stats.")

        print("\n[Step 2] Seeding database…")

        items_created: list[str] = []
        listings_created: list[str] = []
        stats_created: list[str] = []

        for persona in personas:
            user_id = user_id_map[persona.email]
            print(f"\n  → {persona.name} ({user_id})")

            # ----------------------------------------------------------------
            # 1. Inventory item (upcycled_clothing, no original image)
            # ----------------------------------------------------------------
            item = Item(
                user_id=user_id,
                original_image_url=None,   # user will import from Google
                style=persona.item_style,
                difficulty=persona.item_difficulty,
                fabric_type=persona.item_fabric,
                weight_kg=persona.item_weight_kg,
                item_type="finished_garment",
                is_market_eligible=True,
            )
            session.add(item)
            await session.flush()   # get item.id before creating listing
            items_created.append(str(item.id))
            print(f"    Item created:        {item.id}")

            # ----------------------------------------------------------------
            # 2a. Marketplace listing — upcycled_clothing (linked to item)
            # ----------------------------------------------------------------
            clothing_listing = MarketplaceListing(
                item_id=item.id,
                seller_id=user_id,
                title=persona.item_title,
                description=persona.item_description,
                category="upcycled_clothing",
                price_usdc=persona.item_price_usdc,
                status="active",
            )
            session.add(clothing_listing)

            # ----------------------------------------------------------------
            # 2b. Marketplace listing — tool (no item_id required)
            # ----------------------------------------------------------------
            tool_listing = MarketplaceListing(
                item_id=None,
                seller_id=user_id,
                title=persona.tool_title,
                description=persona.tool_description,
                category="tool",
                price_usdc=persona.tool_price_usdc,
                status="active",
            )
            session.add(tool_listing)

            # ----------------------------------------------------------------
            # 2c. Marketplace listing — material/accessory (no item_id)
            # ----------------------------------------------------------------
            material_listing = MarketplaceListing(
                item_id=None,
                seller_id=user_id,
                title=persona.material_title,
                description=persona.material_description,
                category="material",
                price_usdc=persona.material_price_usdc,
                status="active",
            )
            session.add(material_listing)
            await session.flush()  # populate listing IDs before printing

            listings_created.extend(
                [
                    str(clothing_listing.id),
                    str(tool_listing.id),
                    str(material_listing.id),
                ]
            )
            print(f"    Listing (clothing):  {clothing_listing.id}  ${persona.item_price_usdc:.2f}")
            print(f"    Listing (tool):      {tool_listing.id}  ${persona.tool_price_usdc:.2f}")
            print(f"    Listing (material):  {material_listing.id}  ${persona.material_price_usdc:.2f}")

            # ----------------------------------------------------------------
            # 3. UserStats
            # ----------------------------------------------------------------
            stats = UserStats(
                user_id=user_id,
                water_saved_l=persona.water_saved_l,
                co2_offset_kg=persona.co2_offset_kg,
                landfill_diverted_kg=persona.landfill_diverted_kg,
            )
            session.add(stats)
            stats_created.append(user_id)
            print(
                f"    Stats: {persona.water_saved_l} L water | "
                f"{persona.co2_offset_kg} kg CO₂ | "
                f"{persona.landfill_diverted_kg} kg landfill"
            )

        await session.commit()

    print(
        f"\n[Done] Seeded "
        f"{len(items_created)} items, "
        f"{len(listings_created)} listings, "
        f"{len(stats_created)} user_stats rows."
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed 5 Auth0 users + marketplace data into Reverie."
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Wipe marketplace_listings, items, and user_stats before inserting.",
    )
    parser.add_argument(
        "--skip-auth0",
        action="store_true",
        help="Skip Auth0 user creation and use placeholder IDs.",
    )
    args = parser.parse_args()

    async def run() -> None:
        if args.skip_auth0:
            print("[Step 1] Skipping Auth0 user creation (--skip-auth0).")
            user_id_map = {
                p.email: f"auth0|seed-user-{p.name.split()[0].lower()}"
                for p in PERSONAS
            }
        else:
            user_id_map = await create_auth0_users(PERSONAS)

        await seed_database(
            personas=PERSONAS,
            user_id_map=user_id_map,
            clear_existing=args.clear_existing,
        )

    asyncio.run(run())


if __name__ == "__main__":
    main()
