import ast
import json
import re
from collections.abc import Callable
from pathlib import Path
from statistics import mean
from typing import Literal, TypedDict

from anthropic.types import MessageParam

from message import add_assistant_message, add_user_message, chat, text_from_message

Format = Literal["python", "json", "regex"]


class EvalCase(TypedDict):
    task: str
    format: Format


class ModelGrade(TypedDict):
    strengths: list[str]
    weaknesses: list[str]
    reasoning: str
    score: int


class EvalResult(TypedDict):
    test_case: EvalCase
    output: str
    model_grade: ModelGrade
    syntax_score: int
    score: float


DATASET_JSON_PATH = Path("dataset.json")


def generate_dataset(count: int = 5) -> list[EvalCase]:
    prompt = f"""
    Generate an evaluation dataset for a prompt evaluation. The dataset will
    be used to evaluate prompts that generate Python, JSON, or Regex
    specifically for AWS-related tasks. Generate an array of JSON objects,
    each with a "task" field describing the task and a "format" field set to
    exactly one of "python", "json", or "regex".

    Example output:
    ```json
    [
      {{"task": "Description of task", "format": "python"}},
      ...additional
    ]
    ```

    * Focus on tasks that can be solved by writing a single Python function,
      a single JSON object, or a single regex
    * Focus on tasks that do not require writing much code

    Please generate {count} objects.
    """

    messages: list[MessageParam] = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = text_from_message(chat(messages, stop_sequences=["```"]))

    dataset: list[EvalCase] = json.loads(text)
    return dataset


def save_dataset_json(dataset: list[EvalCase], path: Path = DATASET_JSON_PATH) -> None:
    path.write_text(json.dumps(dataset, indent=2))


def load_dataset_json(path: Path = DATASET_JSON_PATH) -> list[EvalCase]:
    dataset: list[EvalCase] = json.loads(path.read_text())
    return dataset


def build_prompt(test_case: EvalCase) -> str:
    return f"""
    Please solve the following task. Respond only with {test_case["format"]},
    with no explanation, headers, or footers.

    Task: {test_case["task"]}
    """


def run_prompt(test_case: EvalCase) -> str:
    messages: list[MessageParam] = []
    add_user_message(messages, build_prompt(test_case))
    add_assistant_message(messages, "```code")
    return text_from_message(chat(messages, stop_sequences=["```"]))


def validate_json(text: str) -> int:
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text: str) -> int:
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text: str) -> int:
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


VALIDATORS: dict[Format, Callable[[str], int]] = {
    "json": validate_json,
    "python": validate_python,
    "regex": validate_regex,
}


def grade_syntax(output: str, test_case: EvalCase) -> int:
    return VALIDATORS[test_case["format"]](output)


def grade_by_model(test_case: EvalCase, output: str) -> ModelGrade:
    eval_prompt = f"""
    You are an expert code reviewer evaluating AI-generated {test_case["format"]}.
    Evaluate this solution.

    Task: {test_case["task"]}
    Solution: {output}

    Provide your evaluation as a structured JSON object with:
    - "strengths": an array of 1-3 key strengths
    - "weaknesses": an array of 1-3 key areas for improvement
    - "reasoning": a concise explanation of your assessment
    - "score": a number between 1 and 10
    """

    messages: list[MessageParam] = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")

    eval_text = text_from_message(chat(messages, stop_sequences=["```"]))
    grade: ModelGrade = json.loads(eval_text)
    return grade


def run_test_case(test_case: EvalCase) -> EvalResult:
    output = run_prompt(test_case)
    model_grade = grade_by_model(test_case, output)
    syntax_score = grade_syntax(output, test_case)
    score = (model_grade["score"] + syntax_score) / 2

    return {
        "test_case": test_case,
        "output": output,
        "model_grade": model_grade,
        "syntax_score": syntax_score,
        "score": score,
    }


def average_score(results: list[EvalResult]) -> float:
    return mean(result["score"] for result in results)


def run_eval(dataset: list[EvalCase]) -> list[EvalResult]:
    results = [run_test_case(test_case) for test_case in dataset]
    print(f"Average score: {average_score(results):.2f}")
    return results


if __name__ == "__main__":
    dataset: list[EvalCase] = [
        {
            "task": (
                "Write a Python function called `is_valid_s3_bucket_name` "
                "that returns True if a string is 3-63 characters long and "
                "contains only lowercase letters, digits, dots, and hyphens."
            ),
            "format": "python",
        },
        {
            "task": (
                "Write an IAM policy JSON object that allows the "
                "`s3:GetObject` action on all resources."
            ),
            "format": "json",
        },
        {
            "task": (
                "Write a regex that matches an AWS Lambda function ARN, e.g. "
                "arn:aws:lambda:us-east-1:123456789012:function:my-function"
            ),
            "format": "regex",
        },
    ]

    results = run_eval(dataset)

    for result in results:
        print(
            f"{result['test_case']['format']:6} "
            f"score={result['score']:.1f} "
            f"{result['test_case']['task']}"
        )
