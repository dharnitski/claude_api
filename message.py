from anthropic import Anthropic, Omit, omit
from anthropic.types import Message, MessageParam, ToolParam, ToolResultBlockParam

client = Anthropic()
model = "claude-sonnet-4-5"

UserContent = str | Message | list[ToolResultBlockParam]


def add_user_message(messages: list[MessageParam], message: UserContent) -> None:
    user_message: MessageParam = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)


def add_assistant_message(messages: list[MessageParam], message: str | Message) -> None:
    assistant_message: MessageParam = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)


def chat(
    messages: list[MessageParam],
    system: str | Omit = omit,
    stop_sequences: list[str] | Omit = omit,
    tools: list[ToolParam] | Omit = omit,
) -> Message:
    return client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
        system=system,
        stop_sequences=stop_sequences,
        tools=tools,
    )


def text_from_message(message: Message) -> str:
    return "\n".join([block.text for block in message.content if block.type == "text"])


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

    # With system prompt
    system = """
    You are a patient math tutor.
    Do not directly answer a student's questions.
    Guide them to a solution step by step.
    """

    # Get the follow-up response with full context
    final_answer = chat(messages, system=system)
    print(text_from_message(final_answer))
