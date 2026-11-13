"""Benchmark loading and agreement reporting.

Gold labels in ``benchmarks/cases.json`` were assigned by the toolkit developer. They have not
been validated by independent annotators; see docs/evaluation.md.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from semantica.core.status import OverallStatus
from semantica.errors import InputError
from semantica.verification.preservation import verify

_REQUIRED = ("id", "phenomenon", "source", "candidate", "gold_status")
_VALID_STATUS = {s.value for s in OverallStatus}
_SHIFT = OverallStatus.MEANING_SHIFT_DETECTED.value
_PRESERVED = OverallStatus.PRESERVED.value


@dataclass(frozen=True)
class CaseOutcome:
    case_id: str
    phenomenon: str
    gold: str
    predicted: str
    agrees: bool
    known_limitation: bool
    wrong_checks: tuple[str, ...]
    checked: int = 0


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a benchmark file."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read benchmark file {path}: {exc}") from exc
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        raise InputError("benchmark file must contain a non-empty 'cases' list")
    ids: set[str] = set()
    for case in cases:
        missing = [k for k in _REQUIRED if k not in case]
        if missing:
            raise InputError(f"case {case.get('id', '?')} is missing fields: {missing}")
        if case["gold_status"] not in _VALID_STATUS:
            raise InputError(f"case {case['id']} has an invalid gold_status")
        if case["id"] in ids:
            raise InputError(f"duplicate case id {case['id']}")
        ids.add(case["id"])
    return list(cases)


def run_benchmark(cases: list[dict[str, Any]]) -> list[CaseOutcome]:
    outcomes: list[CaseOutcome] = []
    for case in cases:
        result = verify(
            str(case["source"]),
            str(case["candidate"]),
            context=list(case.get("contexts", [])) or None,
        )
        gold_checks = dict(case.get("gold_checks", {}))
        wrong = tuple(
            sorted(
                name
                for name, status in gold_checks.items()
                if result.status_of(name).value != status
            )
        )
        predicted = result.overall.value
        outcomes.append(
            CaseOutcome(
                case_id=str(case["id"]),
                phenomenon=str(case["phenomenon"]),
                gold=str(case["gold_status"]),
                predicted=predicted,
                agrees=predicted == case["gold_status"],
                known_limitation=bool(case.get("known_limitation", False)),
                wrong_checks=wrong,
                checked=len(gold_checks),
            )
        )
    return outcomes


def summarize(outcomes: list[CaseOutcome]) -> dict[str, object]:
    """Compute agreement statistics. Rates use explicit denominators."""
    total = len(outcomes)
    agree = sum(o.agrees for o in outcomes)
    matrix: dict[str, Counter[str]] = defaultdict(Counter)
    per_phenomenon: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for o in outcomes:
        matrix[o.gold][o.predicted] += 1
        per_phenomenon[o.phenomenon][1] += 1
        per_phenomenon[o.phenomenon][0] += o.agrees
    gold_shift = [o for o in outcomes if o.gold == _SHIFT]
    gold_pres = [o for o in outcomes if o.gold == _PRESERVED]
    missed = [o for o in gold_shift if o.predicted == _PRESERVED]
    false_alarm = [o for o in gold_pres if o.predicted == _SHIFT]
    gold_check_total = sum(o.checked for o in outcomes)
    gold_check_wrong = sum(len(o.wrong_checks) for o in outcomes)
    return {
        "cases": total,
        "gold_check_agreement": {
            "annotated": gold_check_total,
            "mismatches": gold_check_wrong,
            "cases_with_mismatch": [o.case_id for o in outcomes if o.wrong_checks],
        },
        "exact_agreement": {
            "count": agree,
            "of": total,
            "rate": round(agree / total, 4) if total else None,
        },
        "missed_shifts": {
            "count": len(missed),
            "of": len(gold_shift),
            "ids": [o.case_id for o in missed],
        },
        "false_alarms": {
            "count": len(false_alarm),
            "of": len(gold_pres),
            "ids": [o.case_id for o in false_alarm],
        },
        "confusion_matrix": {g: dict(c) for g, c in sorted(matrix.items())},
        "per_phenomenon": {
            p: {"agree": a, "of": n} for p, (a, n) in sorted(per_phenomenon.items())
        },
        "disagreements": [
            {
                "id": o.case_id,
                "gold": o.gold,
                "predicted": o.predicted,
                "known_limitation": o.known_limitation,
            }
            for o in outcomes
            if not o.agrees
        ],
        "undocumented_disagreements": [
            o.case_id for o in outcomes if not o.agrees and not o.known_limitation
        ],
    }
