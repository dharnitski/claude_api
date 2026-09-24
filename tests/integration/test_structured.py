from structured import generate_event_bridge_rule


def test_generate_event_bridge_rule_stops_at_stop_sequence() -> None:
    text = generate_event_bridge_rule()

    assert isinstance(text, str)
    assert len(text) > 0
    assert "```" not in text
