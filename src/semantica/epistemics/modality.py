"""Detection of modal markers in a clause."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from semantica.linguistics import lexicon as lx

_MONTH_CONTEXT = frozenset(
    {
        "in",
        "of",
        "on",
        "during",
        "since",
        "until",
        "by",
        "early",
        "late",
        "mid",
        "last",
        "next",
        "this",
    }
)


@dataclass(frozen=True)
class ModalityProfile:
    """Modal classes found in a clause, with the marker words that triggered them."""

    classes: frozenset[str]
    markers: tuple[str, ...]

    @property
    def is_unmarked(self) -> bool:
        return not self.classes

    def to_dict(self) -> dict[str, object]:
        return {"classes": sorted(self.classes), "markers": list(self.markers)}


def _is_month_may(raw: Sequence[str], i: int) -> bool:
    if raw[i] != "May":
        return False
    if i > 0:
        return raw[i - 1].lower() in _MONTH_CONTEXT or raw[i - 1].isdigit()
    return i + 1 < len(raw) and raw[i + 1].isdigit()


def detect_modality(raw_tokens: Sequence[str]) -> ModalityProfile:
    """Find modal auxiliaries, modal phrases and modal adverbs.

    ``raw_tokens`` keep their capitalisation so that the month name "May" is not mistaken for
    the auxiliary.
    """
    low = [t.lower() for t in raw_tokens]
    classes: set[str] = set()
    markers: list[str] = []
    i = 0
    while i < len(low):
        matched = False
        for phrase, cls in lx.PHRASE_MODALS:
            n = len(phrase)
            if tuple(low[i : i + n]) == phrase:
                classes.add(cls)
                markers.append(" ".join(phrase))
                i += n
                matched = True
                break
        if matched:
            continue
        token = low[i]
        if token in lx.MODAL_CLASS and not _is_month_may(raw_tokens, i):
            classes.add(lx.MODAL_CLASS[token])
            markers.append(token)
        elif token in lx.ADVERB_MODALS:
            classes.add(lx.ADVERB_MODALS[token])
            markers.append(token)
        i += 1
    return ModalityProfile(frozenset(classes), tuple(markers))
