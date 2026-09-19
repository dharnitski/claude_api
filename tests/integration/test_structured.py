import os

import pytest
from dotenv import load_dotenv

from message import MessageParam, add_assistant_message, add_user_message, chat

load_dotenv()


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY"
)
def test_chat_stops_at_stop_sequence() -> None:
    messages: list[MessageParam] = []
    add_user_message(messages, "Generate a very short event bridge rule as json")
    add_assistant_message(messages, "```json")

    text = chat(messages, stop_sequences=["```"])

    assert isinstance(text, str)
    assert len(text) > 0
    assert "```" not in text
