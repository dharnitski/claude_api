from anthropic import Anthropic
from anthropic.types import Message

client = Anthropic()
model = "claude-sonnet-4-5"


def ask(prompt: str) -> Message:
    return client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )


if __name__ == "__main__":
    message = ask("What is quantum computing? Answer in one sentence")
    print(message.content[0].text)
