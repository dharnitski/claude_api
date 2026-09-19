from anthropic import Anthropic
from anthropic.types import Message, MessageParam

client = Anthropic()
model = "claude-sonnet-4-5"


def add_user_message(messages: list[MessageParam], text: str) -> None:
    user_message: MessageParam = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages: list[MessageParam], text: str) -> None:
    assistant_message: MessageParam = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages: list[MessageParam]) -> str:
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message.content[0].text

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
    # Start with an empty message list
    messages: list[MessageParam] = []

    # Add the initial user question
    add_user_message(messages, "Define quantum computing in one sentence")

    # Get Claude's response
    answer = chat(messages)

    # Add Claude's response to the conversation history
    add_assistant_message(messages, answer)

    # Add a follow-up question
    add_user_message(messages, "Write another sentence")

    # Get the follow-up response with full context
    final_answer = chat(messages)
    print(final_answer)
