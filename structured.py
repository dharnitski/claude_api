from anthropic.types import MessageParam

from message import add_assistant_message, add_user_message, chat, text_from_message


def generate_event_bridge_rule() -> str:
    messages: list[MessageParam] = []

    add_user_message(messages, "Generate a very short event bridge rule as json")
    add_assistant_message(messages, "```json")

    return text_from_message(chat(messages, stop_sequences=["```"]))


if __name__ == "__main__":
    print(generate_event_bridge_rule())
