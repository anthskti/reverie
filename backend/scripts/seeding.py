from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import delete

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import asyncio

from database.connection import SessionLocal, init_models, is_configured
from models.item import Item

DEFAULT_AUTH0_USER_IDS = [
    "auth0|seed-user-alex",
    "auth0|seed-user-maya",
    "auth0|seed-user-jules",
    "auth0|seed-user-nina",
    "auth0|seed-user-omar",
]

SAMPLE_ITEMS: list[dict[str, object]] = [
    {
        "original_image_url": "https://example.com/inventory/alex-boho.jpg",
        "style": "boho",
        "difficulty": "easy",
        "fabric_type": "cotton",
        "weight_kg": 0.68,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/alex-tailored.jpg",
        "style": "tailored",
        "difficulty": "medium",
        "fabric_type": "linen",
        "weight_kg": 1.12,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/maya-streetwear.jpg",
        "style": "streetwear",
        "difficulty": "medium",
        "fabric_type": "denim",
        "weight_kg": 1.04,
        "item_type": "finished_garment",
        "is_market_eligible": False,
    },
    {
        "original_image_url": "https://example.com/inventory/maya-romantic.jpg",
        "style": "romantic",
        "difficulty": "hard",
        "fabric_type": "silk",
        "weight_kg": 0.47,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/jules-minimalist.jpg",
        "style": "minimalist",
        "difficulty": "easy",
        "fabric_type": "wool",
        "weight_kg": 0.73,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/jules-festival.jpg",
        "style": "festival",
        "difficulty": "medium",
        "fabric_type": "satin",
        "weight_kg": 0.59,
        "item_type": "finished_garment",
        "is_market_eligible": False,
    },
    {
        "original_image_url": "https://example.com/inventory/nina-retro.jpg",
        "style": "retro",
        "difficulty": "medium",
        "fabric_type": "corduroy",
        "weight_kg": 0.91,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/nina-artisan.jpg",
        "style": "artisan",
        "difficulty": "hard",
        "fabric_type": "canvas",
        "weight_kg": 1.38,
        "item_type": "finished_garment",
        "is_market_eligible": False,
    },
    {
        "original_image_url": "https://example.com/inventory/omar-oversized.jpg",
        "style": "oversized",
        "difficulty": "easy",
        "fabric_type": "jersey",
        "weight_kg": 0.82,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/omar-ecoluxe.jpg",
        "style": "eco-luxe",
        "difficulty": "hard",
        "fabric_type": "tweed",
        "weight_kg": 1.21,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/sage-coastal.jpg",
        "style": "coastal",
        "difficulty": "easy",
        "fabric_type": "viscose",
        "weight_kg": 0.55,
        "item_type": "finished_garment",
        "is_market_eligible": False,
    },
    {
        "original_image_url": "https://example.com/inventory/sage-editorial.jpg",
        "style": "editorial",
        "difficulty": "medium",
        "fabric_type": "polyester",
        "weight_kg": 0.95,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/tess-vintage.jpg",
        "style": "vintage",
        "difficulty": "medium",
        "fabric_type": "velvet",
        "weight_kg": 0.76,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
    {
        "original_image_url": "https://example.com/inventory/tess-workwear.jpg",
        "style": "workwear",
        "difficulty": "hard",
        "fabric_type": "denim",
        "weight_kg": 1.43,
        "item_type": "finished_garment",
        "is_market_eligible": False,
    },
    {
        "original_image_url": "https://example.com/inventory/zoe-sunset.jpg",
        "style": "sunset",
        "difficulty": "easy",
        "fabric_type": "cotton",
        "weight_kg": 0.63,
        "item_type": "finished_garment",
        "is_market_eligible": True,
    },
]


async def seed_items(
    count: int = 15,
    clear_existing: bool = False,
    user_ids: list[str] | None = None,
) -> list[str]:
    if not is_configured():
        raise RuntimeError(
            "DATABASE_URL is not configured. Set the backend environment variables before running the seed script."
        )

    await init_models()

    if SessionLocal is None:
        raise RuntimeError("Database session factory is not available")

    async with SessionLocal() as session:
        if clear_existing:
            await session.execute(delete(Item))

        resolved_user_ids = user_ids or DEFAULT_AUTH0_USER_IDS
        if not resolved_user_ids:
            raise ValueError("At least one user ID is required")

        items_to_create = [
            Item(
                user_id=resolved_user_ids[index % len(resolved_user_ids)],
                original_image_url=str(payload["original_image_url"]),
                style=str(payload["style"]),
                difficulty=str(payload["difficulty"]),
                fabric_type=str(payload["fabric_type"]),
                weight_kg=float(payload["weight_kg"]),
                item_type=str(payload["item_type"]),
                is_market_eligible=bool(payload["is_market_eligible"]),
            )
            for index, payload in enumerate(SAMPLE_ITEMS[:count])
        ]

        session.add_all(items_to_create)
        await session.commit()

        return [str(item.id) for item in items_to_create]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the inventory table with sample items")
    parser.add_argument("--count", type=int, default=15, help="Number of seed items to create")
    parser.add_argument(
        "--user-id",
        action="append",
        dest="user_ids",
        default=None,
        help="Auth0-style subject(s) to associate with the seeded items. Repeat the flag for multiple users.",
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Delete existing items before inserting the seed batch",
    )
    args = parser.parse_args()

    try:
        created_ids = asyncio.run(
            seed_items(
                count=args.count,
                clear_existing=args.clear_existing,
                user_ids=args.user_ids,
            )
        )
    except RuntimeError as exc:
        print(f"Seed failed: {exc}")
        raise SystemExit(1) from exc

    print(f"Created {len(created_ids)} items")
    for item_id in created_ids:
        print(item_id)


if __name__ == "__main__":
    main()

