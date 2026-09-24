import os

import anthropic
from anthropic.types import FileMetadata, MessageParam, ToolUnionParam

client = anthropic.Anthropic()
model = "claude-sonnet-5"

DATA_FILE = "streaming.csv"
OUTPUT_DIR = "claude_outputs"

ANALYSIS_PROMPT = """Run a detailed analysis to determine major drivers of churn.
Your final output should include at least one detailed plot summarizing your findings."""

TOOLS: list[ToolUnionParam] = [
    {"type": "code_execution_20260521", "name": "code_execution"}
]


def upload(path: str) -> FileMetadata:
    with open(path, "rb") as file:
        return client.files.upload(file=(os.path.basename(path), file, "text/csv"))


def safe_output_path(filename: str, output_dir: str = OUTPUT_DIR) -> str:
    safe_name = os.path.basename(filename)
    if not safe_name or safe_name in (".", ".."):
        raise ValueError(f"Refusing to write unsafe filename: {filename}")
    return os.path.join(output_dir, safe_name)


def download_file(file_id: str) -> str:
    metadata = client.files.retrieve_metadata(file_id)
    output_path = safe_output_path(metadata.filename)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client.files.download(file_id).write_to_file(output_path)
    return output_path


def analyze_churn() -> None:
    file_metadata = upload(DATA_FILE)

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": ANALYSIS_PROMPT},
                {
                    "type": "container_upload",
                    "file_id": file_metadata.id,
                    "cache_control": {"type": "ephemeral"},
                },
            ],
        }
    ]

    response = client.messages.create(
        model=model,
        max_tokens=16000,
        messages=messages,
        tools=TOOLS,
    )

    for block in response.content:
        if block.type == "text":
            print(f"--- text ---\n{block.text}")
        elif block.type == "server_tool_use":
            print(f"--- {block.name} ---")
            print(block.input.get("command", block.input))
        elif block.type == "bash_code_execution_tool_result":
            result = block.content
            if result.type == "bash_code_execution_result":
                if result.stdout:
                    print(f"--- stdout ---\n{result.stdout}")
                if result.stderr:
                    print(f"--- stderr ---\n{result.stderr}")
                for output in result.content:
                    saved_path = download_file(output.file_id)
                    print(f"Downloaded: {saved_path}")
            else:
                print(f"--- error ---\n{result.error_code}")

    print(f"--- usage ---\n{response.usage}")


if __name__ == "__main__":
    analyze_churn()
