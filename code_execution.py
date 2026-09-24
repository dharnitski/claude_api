import anthropic
from anthropic.types import MessageParam, ToolUnionParam

client = anthropic.Anthropic()
model = "claude-opus-5"

PROMPT = "Calculate PI to the 50th decimal place. Use your code execution tool."

TOOLS: list[ToolUnionParam] = [
    {"type": "code_execution_20260521", "name": "code_execution"}
]


def calculate_pi() -> None:
    messages: list[MessageParam] = [{"role": "user", "content": PROMPT}]

    response = client.messages.create(
        model=model,
        max_tokens=16000,
        messages=messages,
        tools=TOOLS,
    )

    for block in response.content:
        if block.type == "server_tool_use":
            print(f"--- {block.name} ---")
            print(block.input.get("command", block.input))
        elif block.type == "bash_code_execution_tool_result":
            result = block.content
            if result.type == "bash_code_execution_result":
                print(f"--- result ---\n{result.stdout}")
            else:
                print(f"--- error ---\n{result.error_code}")
        elif block.type == "text":
            print(f"--- text ---\n{block.text}")


if __name__ == "__main__":
    calculate_pi()
