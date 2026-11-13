"""Speech-act classification and evaluative polarity."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from semantica.linguistics import lexicon as lx
from semantica.linguistics.lexical import lemma

_INDIRECT = re.compile(r"^(could|can|would|will) you\b", re.IGNORECASE)
_COMMISSIVE = re.compile(r"^(i|we) (will|shall|promise|guarantee|commit)\b", re.IGNORECASE)
_EXPRESSIVE = re.compile(
    r"\b(thank you|thanks|i am sorry|i apologi[sz]e|congratulations|well done)\b", re.IGNORECASE
)


@dataclass(frozen=True)
class Intent:
    """Speech act of a unit: assertion, question, directive, commissive or expressive."""

    act: str
    indirect: bool = False


def classify_intent(text: str, tokens: Sequence[str]) -> Intent:
    stripped = text.strip()
    if _INDIRECT.match(stripped):
        return Intent("directive", indirect=True)
    if _COMMISSIVE.match(stripped):
        return Intent("commissive")
    if _EXPRESSIVE.search(stripped):
        return Intent("expressive")
    if stripped.endswith("?"):
        return Intent("question")
    if tokens:
        if tokens[0] == "please":
            return Intent("directive")
        entry = lx.VERB_FORMS.get(tokens[0])
        if tokens[0] == "do" and len(tokens) > 2 and tokens[1] == "not":
            return Intent("directive")
        if entry is not None and entry[1] == 0 and len(tokens) > 1:
            return Intent("directive")
    return Intent("assertion")


def evaluative_polarity(tokens: Sequence[str], negations: int) -> int:
    """Return +1, -1 or 0 from the sign of the summed evaluative words, flipped by negation."""
    score = 0
    for token in tokens:
        base = lemma(token)
        if token in lx.POSITIVE_WORDS or base in lx.POSITIVE_WORDS:
            score += 1
        elif token in lx.NEGATIVE_WORDS or base in lx.NEGATIVE_WORDS:
            score -= 1
    sign = (score > 0) - (score < 0)
    return -sign if negations % 2 else sign
