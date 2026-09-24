import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.getenv("ANTHROPIC_API_KEY"):
        return

    integration_dir = Path(__file__).parent
    skip_marker = pytest.mark.skip(reason="requires ANTHROPIC_API_KEY")
    for item in items:
        if integration_dir in Path(str(item.fspath)).parents:
            item.add_marker(skip_marker)
