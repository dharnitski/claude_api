import re

import pytest
from anthropic.types import Message, ToolUseBlock, Usage

from tool_functions import (
    TOOL_FUNCTIONS,
    TOOLS,
    add_duration_to_datetime,
    get_current_datetime,
    run_tool,
    run_tools,
    set_reminder,
)


def _tool_use(name: str, input_: dict, id_: str = "toolu_1") -> ToolUseBlock:
    return ToolUseBlock(id=id_, input=input_, name=name, type="tool_use")


def _message(content: list) -> Message:
    return Message(
        id="msg_1",
        content=content,
        model="claude-sonnet-4-5",
        role="assistant",
        stop_reason="tool_use",
        stop_sequence=None,
        type="message",
        usage=Usage(input_tokens=1, output_tokens=1),
    )


def test_get_current_datetime_uses_given_format() -> None:
    result = get_current_datetime("%H:%M:%S")

    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", result)


def test_get_current_datetime_rejects_empty_format() -> None:
    with pytest.raises(ValueError, match="date_format cannot be empty"):
        get_current_datetime("")


def test_add_duration_to_datetime_adds_days() -> None:
    result = add_duration_to_datetime("2050-01-01 00:00:00", 177, "days")

    assert result == "2050-06-27 00:00:00"


def test_add_duration_to_datetime_supports_negative_duration() -> None:
    result = add_duration_to_datetime("2050-01-01 00:00:00", -1, "days")

    assert result == "2049-12-31 00:00:00"


def test_add_duration_to_datetime_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError, match="Invalid unit"):
        add_duration_to_datetime("2050-01-01 00:00:00", 1, "months")


def test_set_reminder_prints_and_returns_confirmation(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = set_reminder("doctors appointment", "2050-06-27 00:00:00")

    assert result == "Reminder set for 2050-06-27 00:00:00: doctors appointment"
    assert capsys.readouterr().out.strip() == result


def test_run_tool_dispatches_by_name() -> None:
    tool_use = _tool_use("get_current_datetime", {"date_format": "%H:%M:%S"})

    result = run_tool(tool_use)

    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", result)


def test_run_tool_dispatches_add_duration_to_datetime() -> None:
    tool_use = _tool_use(
        "add_duration_to_datetime",
        {"datetime_str": "2050-01-01 00:00:00", "duration": 1, "unit": "days"},
    )

    result = run_tool(tool_use)

    assert result == "2050-01-02 00:00:00"


def test_run_tool_dispatches_set_reminder() -> None:
    tool_use = _tool_use(
        "set_reminder",
        {"content": "call the vet", "datetime_str": "2050-01-01 00:00:00"},
    )

    result = run_tool(tool_use)

    assert result == "Reminder set for 2050-01-01 00:00:00: call the vet"


def test_run_tool_raises_for_unknown_tool_name() -> None:
    tool_use = _tool_use("does_not_exist", {})

    with pytest.raises(KeyError):
        run_tool(tool_use)


def test_tools_schema_and_tool_functions_stay_in_sync() -> None:
    schema_names = {tool["name"] for tool in TOOLS}

    assert schema_names == set(TOOL_FUNCTIONS)


def test_run_tools_returns_success_result_per_tool_use_block() -> None:
    tool_use = _tool_use("get_current_datetime", {"date_format": "%H:%M:%S"})
    message = _message([tool_use])

    results = run_tools(message)

    assert len(results) == 1
    assert results[0]["type"] == "tool_result"
    assert results[0]["tool_use_id"] == "toolu_1"
    assert results[0]["is_error"] is False
    content = results[0]["content"]
    assert isinstance(content, str)
    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", content)


def test_run_tools_reports_error_without_raising() -> None:
    tool_use = _tool_use("get_current_datetime", {"date_format": ""})
    message = _message([tool_use])

    results = run_tools(message)

    assert len(results) == 1
    assert results[0]["is_error"] is True
    content = results[0]["content"]
    assert isinstance(content, str)
    assert "date_format cannot be empty" in content


def test_run_tools_handles_multiple_blocks_with_mixed_outcomes() -> None:
    ok_use = _tool_use(
        "get_current_datetime", {"date_format": "%H:%M:%S"}, id_="toolu_ok"
    )
    failing_use = _tool_use(
        "get_current_datetime", {"date_format": ""}, id_="toolu_fail"
    )
    message = _message([ok_use, failing_use])

    results = run_tools(message)

    assert [r["tool_use_id"] for r in results] == ["toolu_ok", "toolu_fail"]
    assert results[0]["is_error"] is False
    assert results[1]["is_error"] is True
