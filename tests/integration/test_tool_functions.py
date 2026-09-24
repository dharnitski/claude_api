from anthropic.types import MessageParam

from message import add_user_message, text_from_message
from tool_functions import run_conversation


def test_run_conversation_calls_tool_and_answers() -> None:
    messages: list[MessageParam] = []
    add_user_message(messages, "What is the exact time, formatted as HH:MM:SS?")

    final_response = run_conversation(messages)

    assert final_response.stop_reason != "tool_use"
    assert len(text_from_message(final_response)) > 0
    assert any(m["role"] == "assistant" for m in messages)
