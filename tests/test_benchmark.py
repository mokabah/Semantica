import json
from collections import Counter

import pytest

from semantica.errors import InputError
from semantica.evaluation.benchmark import load_cases, run_benchmark, summarize


@pytest.fixture(scope="module")
def outcomes(benchmark_path):
    return run_benchmark(load_cases(benchmark_path))


def test_benchmark_contains_required_phenomena(benchmark_path):
    phenomena = {c["phenomenon"] for c in load_cases(benchmark_path)}
    required = {
        "negation",
        "modality",
        "quantifier",
        "entity_substitution",
        "subject_object",
        "causal_relation",
        "attribution",
        "context_dependent",
        "paraphrase_preserving",
    }
    assert required <= phenomena


def test_specification_cases_are_present(benchmark_path):
    by_id = {c["id"]: c for c in load_cases(benchmark_path)}
    assert by_id["core-001"]["gold_status"] == "preserved"
    assert by_id["core-002"]["gold_status"] == "meaning_shift_detected"


def test_no_undocumented_disagreement(outcomes):
    summary = summarize(outcomes)
    assert summary["undocumented_disagreements"] == []


def test_gold_check_statuses_all_agree(outcomes):
    assert [o for o in outcomes if o.wrong_checks] == []


def test_no_missed_shift_on_this_set(outcomes):
    summary = summarize(outcomes)
    assert summary["missed_shifts"]["count"] == 0  # type: ignore[index]


def test_every_documented_limitation_has_a_note(benchmark_path):
    for case in load_cases(benchmark_path):
        if case.get("known_limitation"):
            assert case.get("limitation_note")


def test_summary_denominators(outcomes):
    summary = summarize(outcomes)
    gold = Counter(o.gold for o in outcomes)
    assert summary["missed_shifts"]["of"] == gold["meaning_shift_detected"]  # type: ignore[index]
    assert summary["false_alarms"]["of"] == gold["preserved"]  # type: ignore[index]
    assert summary["exact_agreement"]["of"] == len(outcomes)  # type: ignore[index]


def test_loader_validation(tmp_path):
    def write(payload) -> str:
        path = tmp_path / "b.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    good = {
        "id": "x",
        "phenomenon": "p",
        "source": "a",
        "candidate": "b",
        "gold_status": "preserved",
    }
    with pytest.raises(InputError):
        load_cases(write({"cases": []}))
    with pytest.raises(InputError):
        load_cases(write({"cases": [{"id": "x"}]}))
    with pytest.raises(InputError):
        load_cases(write({"cases": [{**good, "gold_status": "bogus"}]}))
    with pytest.raises(InputError):
        load_cases(write({"cases": [good, good]}))
    with pytest.raises(InputError):
        load_cases(tmp_path / "missing.json")
    assert len(load_cases(write({"cases": [good]}))) == 1
