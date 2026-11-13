"""Directional checks: does the candidate assert more or less than the source?

These checks are heuristics about *strength of commitment*. They are not logical entailment.
"""

from __future__ import annotations

from semantica.core.status import CheckStatus
from semantica.epistemics.certainty import (
    certainty_of,
    claim_strength,
    direction,
    strength_label,
)
from semantica.linguistics import lexicon as lx
from semantica.semantics.representation import UnitRepresentation
from semantica.verification.result import CheckResult

_NON_COMMITTAL = frozenset({"ambiguous", "advisability"})
_HEDGES = frozenset({"possibility", "probability", "improbability", "tendency", "appearance"})


def modality_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare modal classes (possibility, necessity, probability, ...)."""
    details: dict[str, object] = {"source": a.modality.to_dict(), "candidate": b.modality.to_dict()}
    if a.modality.classes == b.modality.classes:
        text = (
            "Both units carry the same modal class."
            if a.modality.classes
            else "Neither unit carries a modal marker."
        )
        return CheckResult("modality_preservation", CheckStatus.PASSED, text, details)
    shift = direction(certainty_of(a.modality), certainty_of(b.modality))
    details["direction"] = shift
    pair = (a.modality.classes, b.modality.classes)
    prediction_vs_hedge = any(
        "prediction" in x and y and y <= _HEDGES for x, y in (pair, pair[::-1])
    )
    if (a.modality.classes | b.modality.classes) & _NON_COMMITTAL or (
        ("prediction" in a.modality.classes or "prediction" in b.modality.classes)
        and not prediction_vs_hedge
    ):
        return CheckResult(
            "modality_preservation",
            CheckStatus.REQUIRES_REVIEW,
            "Modal classes differ and at least one marker (would, should, will) is context "
            "dependent, so the effect on meaning cannot be decided by rule.",
            details,
        )
    return CheckResult(
        "modality_preservation",
        CheckStatus.FAILED,
        f"Modal classes differ ({_fmt(a.modality.classes)} vs {_fmt(b.modality.classes)}); "
        f"the candidate is {shift} in epistemic commitment.",
        details,
    )


def claim_strength_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare the epistemic force of the predicates (influence < lead < cause)."""
    pa = a.proposition.predicate if a.proposition else None
    pb = b.proposition.predicate if b.proposition else None
    sa, sb = claim_strength(pa), claim_strength(pb)
    details: dict[str, object] = {
        "source_predicate": pa,
        "candidate_predicate": pb,
        "source_strength": strength_label(sa),
        "candidate_strength": strength_label(sb),
    }
    if sa is None or sb is None:
        return CheckResult(
            "claim_strength_preservation",
            CheckStatus.PASSED,
            "At least one predicate is not rated for claim strength; the check does not apply.",
            details,
        )
    if sa == sb:
        return CheckResult(
            "claim_strength_preservation",
            CheckStatus.PASSED,
            "Both predicates have the same claim strength.",
            details,
        )
    shift = direction(sa, sb)
    details["direction"] = shift
    return CheckResult(
        "claim_strength_preservation",
        CheckStatus.FAILED,
        f"Predicate '{pa}' ({strength_label(sa)}) became '{pb}' ({strength_label(sb)}); "
        f"the claim is {shift}.",
        details,
    )


def quantifier_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare quantifier and frequency classes (none < few < some < many < majority < all)."""
    qa, qb = sorted(a.quantifiers), sorted(b.quantifiers)
    details: dict[str, object] = {"source": list(a.quantifiers), "candidate": list(b.quantifiers)}
    if qa == qb:
        return CheckResult(
            "quantifier_preservation",
            CheckStatus.PASSED,
            "Quantifiers are identical." if qa else "No quantifier in either unit.",
            details,
        )
    if qa and qb:
        ra = max(lx.QUANTIFIER_RANK[q] for q in qa)
        rb = max(lx.QUANTIFIER_RANK[q] for q in qb)
        shift = direction(ra, rb)
        details["direction"] = shift
        return CheckResult(
            "quantifier_preservation",
            CheckStatus.FAILED,
            f"Quantifiers differ ({', '.join(qa)} vs {', '.join(qb)}); "
            f"the candidate quantifies {shift}.",
            details,
        )
    side = "candidate" if qb else "source"
    return CheckResult(
        "quantifier_preservation",
        CheckStatus.REQUIRES_REVIEW,
        f"A quantifier appears only in the {side}; generic and quantified "
        "statements are not interchangeable by default.",
        details,
    )


def modifier_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare degree words and exclusivity markers (only, solely, significantly, ...)."""
    details: dict[str, object] = {
        "source_degree": list(a.degree_words),
        "candidate_degree": list(b.degree_words),
        "source_exclusivity": list(a.exclusivity),
        "candidate_exclusivity": list(b.exclusivity),
    }
    if a.exclusivity != b.exclusivity:
        return CheckResult(
            "modifier_preservation",
            CheckStatus.FAILED,
            "An exclusivity marker (only, solely, just) was added, dropped or replaced.",
            details,
        )
    if a.degree_words != b.degree_words:
        return CheckResult(
            "modifier_preservation",
            CheckStatus.CAUTION,
            "A degree word (significantly, slightly, ...) was added, dropped "
            "or replaced; the strength of the claim may have shifted.",
            details,
        )
    return CheckResult(
        "modifier_preservation",
        CheckStatus.PASSED,
        "Degree and exclusivity markers are identical.",
        details,
    )


def _fmt(classes: frozenset[str]) -> str:
    return ", ".join(sorted(classes)) if classes else "unmarked"
