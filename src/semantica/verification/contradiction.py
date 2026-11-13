"""Checks that look for contradiction: negation parity, antonyms and opposed modifiers."""

from __future__ import annotations

from semantica.core.status import CheckStatus
from semantica.linguistics.lexical import are_antonyms, canonical
from semantica.semantics.representation import UnitRepresentation
from semantica.verification.result import CheckResult


def negation_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare the parity of negation in the main clauses."""
    details: dict[str, object] = {
        "source_negations": a.negations,
        "candidate_negations": b.negations,
    }
    if a.negations % 2 == b.negations % 2:
        return CheckResult(
            "negation_preservation",
            CheckStatus.PASSED,
            "Negation parity is the same in source and candidate.",
            details,
        )
    direction = "introduced" if b.negations % 2 else "removed"
    return CheckResult(
        "negation_preservation",
        CheckStatus.FAILED,
        f"Negation was {direction}; the polarity of the main clause differs.",
        details,
    )


def contradiction_screen(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Look for word-level antonym substitution between source and candidate."""
    a_canon = {canonical(t) for t in a.body_tokens}
    b_canon = {canonical(t) for t in b.body_tokens}
    pairs: list[tuple[str, str]] = []
    for ta in dict.fromkeys(a.body_tokens):
        if canonical(ta) in b_canon:
            continue
        for tb in dict.fromkeys(b.body_tokens):
            if canonical(tb) in a_canon:
                continue
            if are_antonyms(ta, tb):
                pairs.append((ta, tb))
    details: dict[str, object] = {"antonym_pairs": [list(p) for p in pairs]}
    if not pairs:
        return CheckResult(
            "contradiction_screen",
            CheckStatus.PASSED,
            "No antonym substitution from the built-in lexicon was found. "
            "This does not prove the absence of contradiction.",
            details,
        )
    if a.negations % 2 != b.negations % 2:
        return CheckResult(
            "contradiction_screen",
            CheckStatus.REQUIRES_REVIEW,
            "An antonym pair and a negation change co-occur; they may cancel out or compound.",
            details,
        )
    shown = ", ".join(f"{x} / {y}" for x, y in pairs)
    return CheckResult(
        "contradiction_screen",
        CheckStatus.FAILED,
        f"Antonym substitution detected: {shown}.",
        details,
    )
