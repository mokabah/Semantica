"""Robustness, determinism and sensitivity (defect-injection) tests."""

import json
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

from semantica import verify
from semantica.core.status import CheckStatus, OverallStatus
from semantica.errors import InputError
from semantica.evaluation.benchmark import load_cases, run_benchmark, summarize
from semantica.linguistics import lexicon as lx
from semantica.verification import preservation
from semantica.verification.result import CheckResult

ROOT = Path(__file__).resolve().parent.parent

ODD_INPUTS = [
    "!!!",
    "...",
    "?",
    "123",
    "%",
    "a",
    "A.",
    "éèê 你好",
    "The the the the.",
    "may may may.",
    "not not not not.",
    "If, because, unless.",
    "According to, .",
    "Experts say.",
    "x" * 5000,
    "word " * 3000,
    "Tab\tseparated\nlines here.",
    "Mr. Smith e.g. arrived.",
]


@pytest.mark.parametrize("text", ODD_INPUTS)
def test_odd_inputs_never_raise(text: str) -> None:
    result = verify(text, text)
    assert all(c.explanation for c in result.checks)
    other = verify(text, "The treatment is effective.")
    assert other.overall in set(OverallStatus)


def test_empty_input_is_rejected_with_a_clear_error() -> None:
    for bad in ("", "   ", "\n"):
        with pytest.raises(InputError):
            verify(bad, "text")
        with pytest.raises(InputError):
            verify("text", bad)


def test_random_sentences_never_raise_and_are_symmetric_in_failure_of_identity() -> None:
    rng = random.Random(20260)
    vocab = (
        list(lx.MODAL_CLASS)
        + list(lx.QUANTIFIER_CLASS)
        + list(lx.NEGATION_TOKENS)
        + ["influence", "affects", "people", "media", "because", "if", "unless", "but", "and"]
        + ["the", "a", "of", "by", "was", "is", "Paris", "Monday", "three", "50", "she", "it"]
        + [".", ",", ";", "?"]
    )
    for _ in range(400):
        a = " ".join(rng.choice(vocab) for _ in range(rng.randint(1, 14)))
        b = " ".join(rng.choice(vocab) for _ in range(rng.randint(1, 14)))
        if not a.strip(" .,;?") or not b.strip(" .,;?"):
            continue
        r = verify(a, b)
        assert r.explanation
        # A text compared with itself must never be reported as a meaning shift.
        assert verify(a, a).overall is not OverallStatus.MEANING_SHIFT_DETECTED, a


def test_report_is_deterministic_across_hash_seeds() -> None:
    code = (
        f"import sys;sys.path.insert(0, {str(ROOT / 'src')!r});"
        "from semantica import build_report;"
        "r=build_report('Experts say that social media may influence 3 people in May, but "
        "the effect is small.','Social media determines how people think because of it.');"
        "print(r.to_json())"
    )
    outputs = set()
    for seed in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True
        )
        outputs.add(proc.stdout)
    assert len(outputs) == 1
    json.loads(outputs.pop())


def _always_pass(name: str):
    def check(*_args: object, **_kwargs: object) -> CheckResult:
        return CheckResult(name, CheckStatus.PASSED, "disabled for the sensitivity test")

    return check


@pytest.mark.parametrize(
    ("check", "source", "candidate"),
    [
        ("negation_preservation", "The treatment is effective.", "The treatment is not effective."),
        ("modality_preservation", "The drug may help.", "The drug helps."),
        (
            "claim_strength_preservation",
            "Smoking is linked to cancer.",
            "Smoking causes cancer.",
        ),
        ("quantifier_preservation", "Some students passed.", "All students passed."),
        ("entity_preservation", "The meeting is on Monday.", "The meeting is on Friday."),
        ("relation_preservation", "If it rains, we stay.", "Unless it rains, we stay."),
        ("attribution_preservation", "Experts say prices fell.", "Prices fell."),
    ],
)
def test_disabling_a_check_lets_its_defect_through(monkeypatch, check, source, candidate) -> None:
    """A test suite that cannot fail proves nothing: removing a check must change a verdict."""
    assert verify(source, candidate).overall is OverallStatus.MEANING_SHIFT_DETECTED
    monkeypatch.setattr(preservation, check, _always_pass(check))
    result = verify(source, candidate)
    assert result.status_of(check) is CheckStatus.PASSED
    assert result.overall is not OverallStatus.MEANING_SHIFT_DETECTED or any(
        c.status is CheckStatus.FAILED and c.name != check for c in result.checks
    )


def test_disabling_negation_check_is_caught_by_the_benchmark(monkeypatch) -> None:
    monkeypatch.setattr(
        preservation, "negation_preservation", _always_pass("negation_preservation")
    )
    summary = summarize(run_benchmark(load_cases(ROOT / "benchmarks" / "cases.json")))
    assert summary["undocumented_disagreements"] or summary["gold_check_agreement"]["mismatches"]  # type: ignore[index]
