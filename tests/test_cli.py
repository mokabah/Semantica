import json

import pytest

from semantica.cli import main


def test_compare_text_output(capsys):
    assert (
        main(
            ["compare", "Social media may influence behavior.", "Social media determines behavior."]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "Overall: meaning_shift_detected" in out


def test_compare_json_and_output_file(capsys, tmp_path):
    target = tmp_path / "report.json"
    assert main(["compare", "It may rain.", "It rains.", "--json", "--output", str(target)]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["checks"]["modality_preservation"] == "failed"
    assert json.loads(target.read_text(encoding="utf-8")) == printed


def test_compare_with_context(capsys):
    assert (
        main(
            [
                "compare",
                "She said it was fine.",
                "The manager said the report was fine.",
                "--context",
                "The manager read the report.",
                "--json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["overall_status"] == "requires_human_review"


def test_analyze(capsys):
    assert main(["analyze", "Experts say that prices may fall."]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["units"][0]["attribution"]["source"] == "experts"


def test_input_errors_return_nonzero_exit_code(capsys):
    assert main(["compare", "", "text"]) == 1
    assert "error" in capsys.readouterr().err


def test_missing_benchmark_file(capsys):
    assert main(["benchmark", "/nonexistent/cases.json"]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_benchmark_command(capsys, benchmark_path):
    assert main(["benchmark", str(benchmark_path)]) == 0
    assert "Exact agreement" in capsys.readouterr().out
    assert main(["benchmark", str(benchmark_path), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["cases"] >= 40


def test_usage_error_exits_with_code_2():
    with pytest.raises(SystemExit) as info:
        main([])
    assert info.value.code == 2


def test_version(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0
    assert "0.1.0" in capsys.readouterr().out
