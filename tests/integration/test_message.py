from message import MessageParam, add_user_message, chat, text_from_message


def test_chat_returns_response_from_api() -> None:
    messages: list[MessageParam] = []
    add_user_message(messages, "Reply with exactly one word: pong")

    response = chat(messages)
    text = text_from_message(response)

    assert isinstance(text, str)
    assert len(text) > 0
