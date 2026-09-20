import os

import pytest
from dotenv import load_dotenv

from message import MessageParam, add_user_message, text_from_message
from tool_functions import run_conversation

load_dotenv()


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY"
)
def test_run_conversation_calls_tool_and_answers() -> None:
    messages: list[MessageParam] = []
    add_user_message(messages, "What is the exact time, formatted as HH:MM:SS?")

    final_response = run_conversation(messages)

    assert final_response.stop_reason != "tool_use"
    assert len(text_from_message(final_response)) > 0
    assert any(m["role"] == "assistant" for m in messages)
