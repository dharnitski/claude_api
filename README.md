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

## Quick example

```python
from anthropic import Anthropic
from anthropic.types import Message
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


def ask(prompt: str) -> Message:
    return client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )


if __name__ == "__main__":
    response = ask("Hello, Claude!")
    print(response.content[0].text)
```
