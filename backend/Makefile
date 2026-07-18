.PHONY: db-up db-down db-logs db-reset psql dev install

install:
	uv sync

db-up:
	docker compose up -d

db-down:
	docker compose down

db-reset:
	docker compose down -v && docker compose up -d

db-logs:
	docker compose logs -f

psql:
	docker compose exec db psql -U postgres -d postgres

dev:
	uv run fastapi dev main.py
