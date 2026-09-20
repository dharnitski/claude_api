import os

import pytest
from dotenv import load_dotenv

from message import MessageParam, add_user_message, chat, text_from_message

load_dotenv()


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY"
)
def test_chat_returns_response_from_api() -> None:
    messages: list[MessageParam] = []
    add_user_message(messages, "Reply with exactly one word: pong")

    response = chat(messages)
    text = text_from_message(response)

    assert isinstance(text, str)
    assert len(text) > 0
