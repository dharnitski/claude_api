.PHONY: run test fix

run:
	pipenv run python main.py

test:
	pipenv run pytest

fix:
	pipenv run ruff format .
	pipenv run ruff check --fix .
	pipenv run mypy .
