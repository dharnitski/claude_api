from evaluation import (
    EvalCase,
    grade_syntax,
    validate_json,
    validate_python,
    validate_regex,
)


def test_validate_json_accepts_valid_json() -> None:
    assert validate_json('{"key": "value"}') == 10


def test_validate_json_rejects_invalid_json() -> None:
    assert validate_json("{not json}") == 0


def test_validate_python_accepts_valid_syntax() -> None:
    assert validate_python("def add(a, b):\n    return a + b") == 10


def test_validate_python_rejects_invalid_syntax() -> None:
    assert validate_python("def add(a, b)\n    return a + b") == 0


def test_validate_regex_accepts_valid_pattern() -> None:
    assert validate_regex(r"^\d{3}-\d{4}$") == 10


def test_validate_regex_rejects_invalid_pattern() -> None:
    assert validate_regex(r"(unclosed") == 0


def test_grade_syntax_dispatches_by_format() -> None:
    json_case: EvalCase = {"task": "make json", "format": "json"}
    python_case: EvalCase = {"task": "make python", "format": "python"}
    regex_case: EvalCase = {"task": "make regex", "format": "regex"}

    assert grade_syntax('{"a": 1}', json_case) == 10
    assert grade_syntax("not json", json_case) == 0
    assert grade_syntax("def f(): pass", python_case) == 10
    assert grade_syntax(r"^ok$", regex_case) == 10
    assert grade_syntax(r"(unclosed", regex_case) == 0
