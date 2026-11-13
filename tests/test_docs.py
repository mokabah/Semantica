"""Documentation must run, must not contain broken links and must match the benchmark."""

import re
from pathlib import Path

import pytest

from semantica.evaluation.benchmark import load_cases, run_benchmark, summarize

ROOT = Path(__file__).resolve().parent.parent
MD_FILES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


@pytest.mark.parametrize("path", MD_FILES, ids=lambda p: p.name)
def test_python_blocks_execute(path: Path) -> None:
    for i, block in enumerate(FENCE.findall(path.read_text(encoding="utf-8"))):
        exec(compile(block, f"{path.name}[block {i}]", "exec"), {"__name__": "__doc__"})


@pytest.mark.parametrize("path", [*MD_FILES, ROOT / "CONTRIBUTING.md"], ids=lambda p: p.name)
def test_relative_links_resolve(path: Path) -> None:
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        assert (path.parent / target).resolve().exists(), f"{path.name}: broken link {target}"


def test_at_least_one_runnable_block_exists() -> None:
    total = sum(len(FENCE.findall(p.read_text(encoding="utf-8"))) for p in MD_FILES)
    assert total >= 1


def test_published_benchmark_numbers_match_the_code() -> None:
    summary = summarize(run_benchmark(load_cases(ROOT / "benchmarks" / "cases.json")))
    agree, missed, alarms = (
        summary["exact_agreement"],
        summary["missed_shifts"],
        summary["false_alarms"],
    )
    readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
    evaluation = " ".join((ROOT / "docs" / "evaluation.md").read_text(encoding="utf-8").split())
    assert f"{agree['count']} of {agree['of']}" in readme  # type: ignore[index]
    assert f"misses none of the {missed['of']}" in readme  # type: ignore[index]
    assert missed["count"] == 0  # type: ignore[index]
    assert f"{alarms['count']} false alarms on {alarms['of']}" in readme  # type: ignore[index]
    assert f"{agree['count']} / {agree['of']}" in evaluation  # type: ignore[index]
    assert f"{alarms['count']} / {alarms['of']}" in evaluation  # type: ignore[index]
    assert f"{summary['cases']} hand-written cases" in evaluation


def test_readme_example_report_matches_actual_output() -> None:
    from semantica import verify

    r = verify("Social media may influence behavior.", "Social media determines behavior.")
    block = (ROOT / "README.md").read_text(encoding="utf-8").split("```text")[1]
    for name in ("modality_preservation", "claim_strength_preservation", "negation_preservation"):
        assert f"{name}" in block and r.status_of(name).value in block
    assert r.overall.value in block
