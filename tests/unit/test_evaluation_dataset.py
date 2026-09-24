from pathlib import Path

from evaluation import (
    EvalCase,
    EvalResult,
    average_score,
    build_prompt,
    load_dataset_json,
    save_dataset_json,
)


def test_build_prompt_includes_task_and_format() -> None:
    test_case: EvalCase = {"task": "Write a regex for ARNs", "format": "regex"}

    prompt = build_prompt(test_case)

    assert "Write a regex for ARNs" in prompt
    assert "regex" in prompt


def test_save_and_load_dataset_json_round_trip(tmp_path: Path) -> None:
    dataset: list[EvalCase] = [
        {"task": "Write a Python function", "format": "python"},
        {"task": "Write an IAM policy", "format": "json"},
    ]
    path = tmp_path / "dataset.json"

    save_dataset_json(dataset, path)
    loaded = load_dataset_json(path)

    assert loaded == dataset


def _result(score: float) -> EvalResult:
    test_case: EvalCase = {"task": "task", "format": "json"}
    return {
        "test_case": test_case,
        "output": "output",
        "model_grade": {
            "strengths": [],
            "weaknesses": [],
            "reasoning": "",
            "score": 0,
        },
        "syntax_score": 0,
        "score": score,
    }


def test_average_score_computes_mean_of_results() -> None:
    results = [_result(4), _result(6), _result(8)]

    assert average_score(results) == 6
