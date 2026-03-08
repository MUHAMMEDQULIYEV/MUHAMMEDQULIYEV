.PHONY: up down logs migrate shell-db reset-db test build

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

shell-db:
	docker compose exec db psql -U postgres productivity

reset-db:
	docker compose down -v && docker compose up --build -d

test:
	docker compose exec backend pytest

build:
	docker compose build
