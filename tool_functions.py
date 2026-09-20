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

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

DURATION_UNITS = {
    "seconds": lambda amount: datetime.timedelta(seconds=amount),
    "minutes": lambda amount: datetime.timedelta(minutes=amount),
    "hours": lambda amount: datetime.timedelta(hours=amount),
    "days": lambda amount: datetime.timedelta(days=amount),
    "weeks": lambda amount: datetime.timedelta(weeks=amount),
}

def get_current_datetime(date_format: str = DATETIME_FORMAT) -> str:
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
                "default": DATETIME_FORMAT,
            }
        },
        "required": [],
    },
}

def add_duration_to_datetime(
    datetime_str: str,
    duration: float,
    unit: str,
    date_format: str = DATETIME_FORMAT,
) -> str:
    if unit not in DURATION_UNITS:
        raise ValueError(
            f"Invalid unit '{unit}'. Must be one of: {', '.join(DURATION_UNITS)}"
        )

    parsed = datetime.datetime.strptime(datetime_str, date_format)  # noqa: DTZ007
    result = parsed + DURATION_UNITS[unit](duration)
    return result.strftime(date_format)


add_duration_to_datetime_schema: ToolParam = {
    "name": "add_duration_to_datetime",
    "description": "Adds a duration to a datetime and returns the resulting datetime as a formatted string.",
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "The starting datetime, formatted as YYYY-MM-DD HH:MM:SS.",
            },
            "duration": {
                "type": "number",
                "description": "The amount of the unit to add. Use a negative number to subtract.",
            },
            "unit": {
                "type": "string",
                "enum": list(DURATION_UNITS),
                "description": "The unit that `duration` is measured in.",
            },
            "date_format": {
                "type": "string",
                "description": "A string specifying the format of `datetime_str` and the returned datetime. Uses Python's strftime format codes.",
                "default": DATETIME_FORMAT,
            },
        },
        "required": ["datetime_str", "duration", "unit"],
    },
}


def set_reminder(content: str, datetime_str: str) -> str:
    confirmation = f"Reminder set for {datetime_str}: {content}"
    print(confirmation)
    return confirmation


set_reminder_schema: ToolParam = {
    "name": "set_reminder",
    "description": "Sets a reminder for the given content at the given datetime by printing a confirmation. Does not persist the reminder anywhere.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "What the reminder is about.",
            },
            "datetime_str": {
                "type": "string",
                "description": "When to remind, formatted as YYYY-MM-DD HH:MM:SS.",
            },
        },
        "required": ["content", "datetime_str"],
    },
}

TOOLS: list[ToolParam] = [
    get_current_datetime_schema,
    add_duration_to_datetime_schema,
    set_reminder_schema,
]

TOOL_FUNCTIONS: dict[str, Any] = {
    "get_current_datetime": get_current_datetime,
    "add_duration_to_datetime": add_duration_to_datetime,
    "set_reminder": set_reminder,
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
                "content": f"Error: {e}",
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
    add_user_message(
        messages,
        "Set a reminder for my doctors appointment. Its 177 days after Jan 1st, 2050.",
    )

    final_response = run_conversation(messages)

    print(text_from_message(final_response))
