# claude_api

Experiments and tooling around the Claude API.

Based on the [Building with the Claude API](https://academy.claude.com/courses/building-with-the-claude-api) course.

## Setup

1. Check your Python version (3.7.1+ required):

   ```
   python --version
   ```

2. Install [pipenv](https://pipenv.pypa.io/) if you don't have it:

   ```
   pip install pipenv
   ```

3. Install dependencies:

   ```
   pipenv install
   ```

4. Get an API key from [console.anthropic.com](https://console.anthropic.com) (Settings → API Keys → Create Key).

5. Create a `.env` file in the project root:

   ```
   CLAUDE_MODEL="claude-sonnet-5"
   ANTHROPIC_API_KEY=put-your-api-key-here
   ```

6. Run scripts inside the pipenv environment:

   ```
   pipenv run python your_script.py
   ```

   The `anthropic` SDK automatically reads `ANTHROPIC_API_KEY` from the environment, so `Anthropic()` works without passing the key explicitly (once `.env` is loaded via `load_dotenv()`).

7. Run the example:

   ```
   make run
   ```

See [`message.py`](./message.py) for a minimal typed example.

## MCP CLI chatbot

[`mcp_chat.py`](./mcp_chat.py) is the [Building with the Claude API project](https://academy.claude.com/courses/building-with-the-claude-api/project-setup):
an interactive CLI chatbot that talks to Claude through an MCP client/server pair.

- [`mcp_server.py`](./mcp_server.py) exposes an in-memory document store as MCP tools (`read_doc_contents`,
  `edit_document`), resources (`docs://documents`, `docs://documents/{doc_id}`), and prompts (`format`, `summarize`).
- [`mcp_client.py`](./mcp_client.py) is a thin wrapper around the MCP `ClientSession` used to talk to that server.
- [`core/`](./core) holds the chat loop (`core/chat.py`), the Claude API wrapper (`core/claude.py`), tool dispatch
  (`core/tools.py`), and the interactive CLI (`core/cli.py`, `core/cli_chat.py`).

Run it with:

```
make mcp_chat
```

Usage once running:

- Type a message and press Enter to chat with Claude.
- Reference a document with `@`, e.g. `Tell me about @deposition.md`.
- Run a server-defined prompt with `/`, e.g. `/summarize deposition.md` (Tab-completes).

### Debugging the server with the MCP Inspector

To test `mcp_server.py`'s tools, resources, and prompts in isolation (without going through Claude or the CLI),
run the [MCP Inspector](https://academy.claude.com/courses/building-with-the-claude-api/the-server-inspector):

```
make mcp_inspector
```

This runs `mcp dev mcp_server.py`, which starts a local inspector UI (requires `node`/`npx`) and prints a URL to
open in your browser. Click **Connect** on the left to start the server, then use the Resources, Prompts, and
Tools tabs to list and invoke them individually and see raw results.

Notes on how this works:

- `mcp dev` always launches the server via `uv run` under the hood (regardless of this project's Pipenv setup),
  so it requires [uv](https://docs.astral.sh/uv/) to be installed separately (`brew install uv`).
- `uv run` needs `pyproject.toml`'s `[project]` dependencies (including `mcp[cli]`) to resolve; without them it
  fails with `Error: typer is required`.
- `UV_ISOLATED=1` makes uv use a throwaway environment for this run instead of writing a persistent `.venv` at
  the project root. **Don't drop it or run bare `uv run`/`uv sync` in this repo**: if uv ever creates `.venv` here,
  Pipenv silently switches to using it instead of its own managed environment, breaking `make fix`/`make test`
  until you `rm -rf .venv`.

## Tests

```
make test
```

`tests/integration/test_message.py` hits the real Anthropic API and requires `ANTHROPIC_API_KEY` (via `.env` or the environment); it's skipped otherwise.

## Code quality

```
make fix
```

Formats with ruff, autofixes lint issues, and type-checks with mypy.
