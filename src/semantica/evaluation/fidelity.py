"""Summary of the six evaluation dimensions.

The dimensions are reported side by side. **No weighted total is computed**: any single number
would require a weighting that has no empirical justification in this version. Each dimension
carries the strictest status of the checks that feed it.
"""

from __future__ import annotations

from semantica.core.status import CHECK_SEVERITY, CheckStatus
from semantica.verification.result import VerificationResult

DIMENSIONS: dict[str, tuple[str, ...]] = {
    "semantic_similarity": ("semantic_similarity",),
    "proposition_preservation": (
        "proposition_preservation",
        "relation_preservation",
        "entity_preservation",
        "contradiction_screen",
        "negation_preservation",
        "quantifier_preservation",
        "modifier_preservation",
    ),
    "contextual_consistency": ("contextual_consistency", "unit_alignment"),
    "pragmatic_preservation": ("pragmatic_preservation", "discourse_preservation"),
    "epistemic_preservation": (
        "modality_preservation",
        "claim_strength_preservation",
        "attribution_preservation",
    ),
    "linguistic_fluency": ("linguistic_fluency",),
}


def dimension_summary(result: VerificationResult) -> dict[str, dict[str, object]]:
    """Return, per dimension, the strictest check status and the checks that contributed."""
    by_name = {c.name: c for c in result.checks}
    summary: dict[str, dict[str, object]] = {}
    for dimension, names in DIMENSIONS.items():
        present = [by_name[n] for n in names if n in by_name]
        if not present:
            summary[dimension] = {"status": "not_evaluated", "checks": []}
            continue
        worst: CheckStatus = max((c.status for c in present), key=lambda s: CHECK_SEVERITY[s])
        summary[dimension] = {"status": worst.value, "checks": [c.name for c in present]}
    return summary
