from typing import Any

import pytest
from anthropic.types import MessageParam

import message
from message import add_assistant_message, add_user_message


def test_add_user_message_appends_user_role() -> None:
    messages: list[MessageParam] = []

    add_user_message(messages, "hello")

    assert messages == [{"role": "user", "content": "hello"}]


def test_add_assistant_message_appends_assistant_role() -> None:
    messages: list[MessageParam] = []

    add_assistant_message(messages, "hi there")

    assert messages == [{"role": "assistant", "content": "hi there"}]


def test_messages_preserve_conversation_order() -> None:
    messages: list[MessageParam] = []

    add_user_message(messages, "question")
    add_assistant_message(messages, "answer")
    add_user_message(messages, "follow-up")

    assert messages == [
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": "answer"},
        {"role": "user", "content": "follow-up"},
    ]


def test_add_user_message_does_not_mutate_existing_entries() -> None:
    messages: list[MessageParam] = [{"role": "assistant", "content": "prior"}]

    add_user_message(messages, "new")

    assert messages[0] == {"role": "assistant", "content": "prior"}
    assert messages[1] == {"role": "user", "content": "new"}


def test_ask_delegates_to_chat_with_a_single_user_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, list[MessageParam]] = {}
    sentinel = object()

    def fake_chat(messages: list[MessageParam]) -> Any:
        captured["messages"] = messages
        return sentinel

    monkeypatch.setattr(message, "chat", fake_chat)

    result = message.ask("hello")

    assert captured["messages"] == [{"role": "user", "content": "hello"}]
    assert result is sentinel
