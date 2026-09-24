from mcp.types import ImageContent, PromptMessage, TextContent

from core.cli_chat import (
    convert_prompt_message_to_message_param,
    convert_prompt_messages_to_message_params,
)


def test_convert_text_message_keeps_role_and_text() -> None:
    message = PromptMessage(role="user", content=TextContent(type="text", text="hello"))

    result = convert_prompt_message_to_message_param(message)

    assert result == {"role": "user", "content": "hello"}


def test_convert_assistant_role_message() -> None:
    message = PromptMessage(
        role="assistant", content=TextContent(type="text", text="hi there")
    )

    result = convert_prompt_message_to_message_param(message)

    assert result["role"] == "assistant"


def test_convert_non_text_content_falls_back_to_empty_string() -> None:
    message = PromptMessage(
        role="user",
        content=ImageContent(type="image", data="abc", mimeType="image/png"),
    )

    result = convert_prompt_message_to_message_param(message)

    assert result == {"role": "user", "content": ""}


def test_convert_prompt_messages_preserves_order() -> None:
    messages = [
        PromptMessage(role="user", content=TextContent(type="text", text="first")),
        PromptMessage(
            role="assistant", content=TextContent(type="text", text="second")
        ),
    ]

    result = convert_prompt_messages_to_message_params(messages)

    assert result == [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "second"},
    ]
