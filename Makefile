.PHONY: run test test_unit fix lint

run:
	pipenv run python message.py

test:
	pipenv run pytest

test_unit:
	pipenv run pytest tests/unit

fix:
	pipenv run ruff format .
	pipenv run ruff check --fix .
	pipenv run mypy .

lint:
	pipenv run ruff format --check .
	pipenv run ruff check .
	pipenv run mypy .
