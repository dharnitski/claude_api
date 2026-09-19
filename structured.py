from anthropic.types import MessageParam

from message import add_assistant_message, add_user_message, chat

if __name__ == "__main__":
    messages: list[MessageParam] = []

    add_user_message(messages, "Generate a very short event bridge rule as json")
    add_assistant_message(messages, "```json")

    text = chat(messages, stop_sequences=["```"])

    print(text)
