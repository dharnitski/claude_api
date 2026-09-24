from collections.abc import Generator

import pytest

from mcp_server import (
    docs,
    edit_document,
    fetch_doc,
    format_document,
    list_docs,
    read_document,
    summarize_document,
)


@pytest.fixture(autouse=True)
def _restore_docs() -> Generator[None]:
    original = dict(docs)
    yield
    docs.clear()
    docs.update(original)


def test_read_document_returns_contents() -> None:
    assert read_document("plan.md") == docs["plan.md"]


def test_read_document_rejects_unknown_id() -> None:
    with pytest.raises(ValueError, match="Doc with id missing.md not found"):
        read_document("missing.md")


def test_edit_document_replaces_matching_text() -> None:
    edit_document("plan.md", old_str="implementation", new_str="rollout")

    assert "rollout" in docs["plan.md"]
    assert "implementation" not in docs["plan.md"]


def test_edit_document_rejects_unknown_id() -> None:
    with pytest.raises(ValueError, match="Doc with id missing.md not found"):
        edit_document("missing.md", old_str="a", new_str="b")


def test_list_docs_returns_all_ids() -> None:
    assert list_docs() == list(docs.keys())


def test_fetch_doc_returns_contents() -> None:
    assert fetch_doc("spec.txt") == docs["spec.txt"]


def test_fetch_doc_rejects_unknown_id() -> None:
    with pytest.raises(ValueError, match="Doc with id missing.md not found"):
        fetch_doc("missing.md")


def test_format_document_prompt_references_doc_id() -> None:
    messages = format_document("plan.md")

    assert len(messages) == 1
    assert "plan.md" in messages[0].content.text


def test_summarize_document_prompt_references_doc_id() -> None:
    messages = summarize_document("outlook.pdf")

    assert len(messages) == 1
    assert "outlook.pdf" in messages[0].content.text
