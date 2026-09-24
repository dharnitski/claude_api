.PHONY: run mcp_chat mcp_inspector test test_unit fix lint

run:
	pipenv run python message.py

mcp_chat:
	pipenv run python mcp_chat.py

mcp_inspector:
	UV_ISOLATED=1 pipenv run mcp dev mcp_server.py

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
