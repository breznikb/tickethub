.PHONY: install run lint test migrate sync docker-build docker-up docker-down

install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn tickethub.main:app --reload --app-dir src

migrate:
	alembic upgrade head

sync:
	PYTHONPATH=src python3.11 -m tickethub.services.sync

lint:
	flake8 src tests

test:
	pytest -v

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
