.PHONY: install run lint format typecheck sast audit test check docker

install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8080

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy app tests

sast:
	bandit -r app -c pyproject.toml

audit:
	pip-audit -r requirements.txt

test:
	pytest

check: lint typecheck sast test

docker:
	docker build -t skyhook:local .
