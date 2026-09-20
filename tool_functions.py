import datetime
from typing import Any

from anthropic.types import (
    Message,
    MessageParam,
    ToolParam,
    ToolResultBlockParam,
    ToolUseBlock,
)

from message import add_assistant_message, add_user_message, chat, text_from_message


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.datetime.now().strftime(date_format)  # noqa: DTZ005


get_current_datetime_schema: ToolParam = {
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S",
            }
        },
        "required": [],
    },
}

TOOLS: list[ToolParam] = [get_current_datetime_schema]

TOOL_FUNCTIONS: dict[str, Any] = {
    "get_current_datetime": get_current_datetime,
}


def run_tool(tool_use: ToolUseBlock) -> str:
    function = TOOL_FUNCTIONS[tool_use.name]
    return function(**tool_use.input)  # type: ignore[no-any-return]


def run_tools(message: Message) -> list[ToolResultBlockParam]:
    tool_requests = [block for block in message.content if block.type == "tool_use"]

    tool_result_blocks: list[ToolResultBlockParam] = []
    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request)
            tool_result_block: ToolResultBlockParam = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": str(tool_output),
                "is_error": False,
            }
        except Exception as e:  # noqa: BLE001
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": str(e),
                "is_error": True,
            }
        tool_result_blocks.append(tool_result_block)

    return tool_result_blocks


def run_conversation(messages: list[MessageParam]) -> Message:
    while True:
        response = chat(messages, tools=TOOLS)

        add_assistant_message(messages, response)

        if response.stop_reason != "tool_use":
            return response

        tool_result_blocks = run_tools(response)
        add_user_message(messages, tool_result_blocks)


if __name__ == "__main__":
    messages: list[MessageParam] = []
    add_user_message(messages, "What is the exact time, formatted as HH:MM:SS?")

    final_response = run_conversation(messages)

    print(text_from_message(final_response))
