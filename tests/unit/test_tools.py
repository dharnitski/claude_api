from typing import Any

import pytest
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage
from mcp.types import CallToolResult, TextContent, Tool

from core.tools import ToolManager
from mcp_client import MCPClient


class FakeMCPClient(MCPClient):
    def __init__(
        self, tools: list[Tool], call_result: CallToolResult | Exception | None = None
    ) -> None:
        super().__init__(command="fake", args=[])
        self._tools = tools
        self._call_result = call_result

    async def list_tools(self) -> list[Tool]:
        return self._tools

    async def call_tool(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> CallToolResult:
        if isinstance(self._call_result, Exception):
            raise self._call_result
        assert self._call_result is not None
        return self._call_result


def _tool(name: str, description: str | None = "desc") -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={"type": "object", "properties": {}},
    )


def _tool_use(name: str, tool_use_id: str = "toolu_1") -> ToolUseBlock:
    return ToolUseBlock(id=tool_use_id, input={}, name=name, type="tool_use")


def _message(blocks: list[Any]) -> Message:
    return Message(
        id="msg_1",
        content=blocks,
        model="claude-sonnet-5",
        role="assistant",
        stop_reason="tool_use",
        stop_sequence=None,
        type="message",
        usage=Usage(input_tokens=1, output_tokens=1),
    )


async def test_get_all_tools_merges_tools_across_clients() -> None:
    clients: dict[str, MCPClient] = {
        "a": FakeMCPClient([_tool("read_doc")]),
        "b": FakeMCPClient([_tool("edit_doc", description=None)]),
    }

    tools = await ToolManager.get_all_tools(clients)

    assert {t["name"] for t in tools} == {"read_doc", "edit_doc"}
    assert all(isinstance(t["description"], str) for t in tools)


async def test_execute_tool_requests_returns_success_result() -> None:
    call_result = CallToolResult(
        content=[TextContent(type="text", text="ok")], isError=False
    )
    clients: dict[str, MCPClient] = {
        "a": FakeMCPClient([_tool("read_doc")], call_result=call_result)
    }
    message = _message([_tool_use("read_doc")])

    results = await ToolManager.execute_tool_requests(clients, message)

    assert len(results) == 1
    assert results[0]["is_error"] is False
    assert results[0]["content"] == '["ok"]'


async def test_execute_tool_requests_marks_tool_error_result() -> None:
    call_result = CallToolResult(
        content=[TextContent(type="text", text="boom")], isError=True
    )
    clients: dict[str, MCPClient] = {
        "a": FakeMCPClient([_tool("read_doc")], call_result=call_result)
    }
    message = _message([_tool_use("read_doc")])

    results = await ToolManager.execute_tool_requests(clients, message)

    assert results[0]["is_error"] is True


async def test_execute_tool_requests_reports_missing_tool() -> None:
    clients: dict[str, MCPClient] = {"a": FakeMCPClient([_tool("read_doc")])}
    message = _message([_tool_use("does_not_exist")])

    results = await ToolManager.execute_tool_requests(clients, message)

    assert results[0]["is_error"] is True
    assert results[0]["content"] == "Could not find that tool"


async def test_execute_tool_requests_reports_client_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    clients: dict[str, MCPClient] = {
        "a": FakeMCPClient(
            [_tool("read_doc")], call_result=RuntimeError("connection lost")
        )
    }
    message = _message([_tool_use("read_doc")])

    results = await ToolManager.execute_tool_requests(clients, message)

    assert results[0]["is_error"] is True
    assert "connection lost" in str(results[0]["content"])


async def test_execute_tool_requests_ignores_non_tool_use_blocks() -> None:
    clients: dict[str, MCPClient] = {}
    text_block = TextBlock(type="text", text="hello")
    message = _message([text_block])

    results = await ToolManager.execute_tool_requests(clients, message)

    assert results == []
