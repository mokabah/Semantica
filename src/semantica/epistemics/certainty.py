"""Certainty levels and claim strength of predicates."""

from __future__ import annotations

from enum import IntEnum

from semantica.epistemics.modality import ModalityProfile
from semantica.linguistics import lexicon as lx


class Certainty(IntEnum):
    IMPROBABLE = 0
    POSSIBLE = 1
    PROBABLE = 2
    ASSERTED = 3
    CERTAIN = 4


_FROM_LEVEL = {
    0: Certainty.IMPROBABLE,
    1: Certainty.POSSIBLE,
    2: Certainty.PROBABLE,
    3: Certainty.ASSERTED,
    4: Certainty.CERTAIN,
}


def certainty_of(profile: ModalityProfile) -> Certainty:
    """Map a modality profile to one ordinal level.

    With several markers the lowest level is used, because a hedge dominates the commitment of
    the whole clause.
    """
    if profile.is_unmarked:
        return Certainty.ASSERTED
    return _FROM_LEVEL[min(lx.CERTAINTY_LEVEL[c] for c in profile.classes)]


def claim_strength(predicate: str | None) -> int | None:
    """Return 1 (weak), 2 (moderate) or 3 (strong), or ``None`` if the verb is not rated."""
    if predicate is None:
        return None
    return lx.CLAIM_STRENGTH.get(predicate)


def strength_label(level: int | None) -> str:
    return "unrated" if level is None else lx.CLAIM_STRENGTH_LABEL[level]


def direction(source_level: int, candidate_level: int) -> str:
    """Return ``same``, ``strengthened`` or ``weakened`` for the candidate relative to source."""
    if candidate_level > source_level:
        return "strengthened"
    if candidate_level < source_level:
        return "weakened"
    return "same"
