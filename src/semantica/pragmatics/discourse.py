"""Discourse functions of sentence-initial and coordinating connectives."""

from __future__ import annotations

from semantica.linguistics import lexicon as lx

_MARKERS = sorted(lx.DISCOURSE_MARKERS, key=len, reverse=True)


def strip_leading_marker(text: str) -> tuple[str | None, str]:
    """Remove a sentence-initial connective such as "However," and return its function."""
    low = text.lstrip().lower()
    for marker in _MARKERS:
        if low.startswith(marker) and (len(low) == len(marker) or not low[len(marker)].isalnum()):
            rest = text.lstrip()[len(marker) :].lstrip(" ,")
            return lx.DISCOURSE_MARKERS[marker], rest
    return None, text
