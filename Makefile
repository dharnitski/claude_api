.PHONY: run mcp_chat mcp_inspector test test_unit fix lint

run:
	uv run python message.py

mcp_chat:
	uv run python mcp_chat.py

mcp_inspector:
	uv run mcp dev mcp_server.py

test:
	uv run pytest

test_unit:
	uv run pytest tests/unit

fix:
	uv run ruff format .
	uv run ruff check --fix .
	uv run mypy .

lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy .
