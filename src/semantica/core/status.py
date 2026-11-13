"""Status vocabularies shared by every layer of the toolkit."""

from __future__ import annotations

from enum import StrEnum


class CheckStatus(StrEnum):
    """Outcome of one individual check.

    ``caution`` marks a difference that is probably benign but cannot be ruled out, such as an
    added degree adverb.
    """

    PASSED = "passed"
    FAILED = "failed"
    CAUTION = "caution"
    REQUIRES_MODEL = "requires_model"
    REQUIRES_REVIEW = "requires_review"
    INSUFFICIENT_CONTEXT = "insufficient_context"


class OverallStatus(StrEnum):
    """Aggregate outcome. It is never a score and never a proof of equivalence."""

    PRESERVED = "preserved"
    POSSIBLE_SHIFT = "possible_shift"
    MEANING_SHIFT_DETECTED = "meaning_shift_detected"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    REQUIRES_MODEL = "requires_model"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"


#: Higher value means a more severe outcome when several units are merged into one check.
CHECK_SEVERITY: dict[CheckStatus, int] = {
    CheckStatus.PASSED: 0,
    CheckStatus.REQUIRES_MODEL: 1,
    CheckStatus.CAUTION: 2,
    CheckStatus.REQUIRES_REVIEW: 3,
    CheckStatus.INSUFFICIENT_CONTEXT: 4,
    CheckStatus.FAILED: 5,
}
