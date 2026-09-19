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
   pipenv install anthropic python-dotenv
   ```

4. Get an API key from [console.anthropic.com](https://console.anthropic.com) (Settings → API Keys → Create Key).

5. Create a `.env` file in the project root with your key:

   ```
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

## Tests

```
make test
```

`test_message.py` hits the real Anthropic API and requires `ANTHROPIC_API_KEY` (via `.env` or the environment); it's skipped otherwise.

## Code quality

```
make fix
```

Formats with ruff, autofixes lint issues, and type-checks with mypy.
