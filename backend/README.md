# Reverie Backend

FastAPI service Reverie 
Features:
- for the clothing upcycling AI pipeline (Designer → Style → Sewing / Environmental).
- Auth (not implemented)
- Marketplace (not implemented)

## Setup

```bash
cd backend
uv sync
cp .env.example .env
```

## Local database (Docker)

The dev stack mirrors Supabase's connection model:

- **Postgres** on `5432` — the direct connection (used for DDL / migrations).
- **PgBouncer** on `6543` — a session-mode pooler, the equivalent of
  Supabase's pooled connection (Supavisor). The app connects here at runtime.

```bash
make db-up        # start Postgres + pooler (docker compose up -d)
make db-logs      # tail logs
make psql         # open a psql shell
make db-reset     # wipe volume and recreate
make db-down      # stop
```

Connection strings (already in `.env.example`):

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:6543/postgres   # pooler
DIRECT_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres     # direct
```

Tables (`items`, `projects`) are created by `init_models()` on app startup from
the SQLAlchemy models in `models/`. Docker only runs Postgres + the pooler —
no SQL seed scripts. Session pooling supports connection-level features such as
prepared statements, so the app uses SQLAlchemy's normal async connection pool
(see `database/connection.py`).
