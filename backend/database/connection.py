"""Database connection — Sequelize-style entrypoint.

Local Docker:
  DATABASE_URL -> session pooler on :6543
  DIRECT_URL   -> Postgres on :5432 (DDL / migrations)

Cloud Supabase:
  same env vars, just point at the Supabase pooler / direct hosts.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DIRECT_URL = os.getenv("DIRECT_URL") or DATABASE_URL


def _to_asyncpg(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


def _create_engine(url: str) -> AsyncEngine:
    return create_async_engine(_to_asyncpg(url), pool_pre_ping=True)


engine: AsyncEngine | None = (
    _create_engine(DATABASE_URL) if DATABASE_URL else None
)
direct_engine: AsyncEngine | None = (
    _create_engine(DIRECT_URL) if DIRECT_URL else None
)

# Like `const sequelize = new Sequelize(...)` — one shared connection factory.
SessionLocal: async_sessionmaker[AsyncSession] | None = (
    async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    if engine is not None
    else None
)


def is_configured() -> bool:
    return SessionLocal is not None


async def get_session() -> AsyncIterator[AsyncSession]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with SessionLocal() as session:
        yield session


async def init_models() -> None:
    """Create tables if missing (dev convenience). Uses DIRECT_URL when set."""
    from models.base import Base
    import models  # noqa: F401 — register Item, Project

    target = direct_engine or engine
    if target is None:
        return
    async with target.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engines() -> None:
    if engine is not None:
        await engine.dispose()
    if direct_engine is not None and direct_engine is not engine:
        await direct_engine.dispose()
