import os

import pytest
from dotenv import load_dotenv

from message import MessageParam, add_user_message, chat

load_dotenv()


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY"
)
def test_chat_returns_response_from_api() -> None:
    messages: list[MessageParam] = []
    add_user_message(messages, "Reply with exactly one word: pong")

    response = chat(messages)

    assert isinstance(response, str)
    assert len(response) > 0
