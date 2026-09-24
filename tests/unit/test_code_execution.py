import pytest

from code_execution import safe_output_path


def test_safe_output_path_joins_filename_under_output_dir() -> None:
    result = safe_output_path("chart.png", output_dir="out")

    assert result == "out/chart.png"


def test_safe_output_path_strips_directory_components() -> None:
    result = safe_output_path("../../etc/passwd", output_dir="out")

    assert result == "out/passwd"


def test_safe_output_path_strips_absolute_path_components() -> None:
    result = safe_output_path("/etc/passwd", output_dir="out")

    assert result == "out/passwd"


@pytest.mark.parametrize("filename", ["", ".", ".."])
def test_safe_output_path_rejects_unsafe_filenames(filename: str) -> None:
    with pytest.raises(ValueError, match="Refusing to write unsafe filename"):
        safe_output_path(filename, output_dir="out")
