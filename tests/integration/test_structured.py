import os

import pytest
from dotenv import load_dotenv

from structured import generate_event_bridge_rule

load_dotenv()


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY"
)
def test_generate_event_bridge_rule_stops_at_stop_sequence() -> None:
    text = generate_event_bridge_rule()

    assert isinstance(text, str)
    assert len(text) > 0
    assert "```" not in text
