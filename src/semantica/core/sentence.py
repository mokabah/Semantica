"""Normalisation, tokenisation and the :class:`Sentence` value type."""

from __future__ import annotations

import re
from dataclasses import dataclass

_QUOTES = {0x2019: "'", 0x201C: '"', 0x201D: '"'}
_WS = re.compile(r"\s+")
_TOKEN = re.compile(r"[A-Za-z0-9]+(?:[.'\-][A-Za-z0-9]+)*|%")

_CONTRACTIONS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern, re.IGNORECASE), repl)
    for pattern, repl in (
        (r"\bcan['\u2019]t\b", "can not"),
        (r"\bcannot\b", "can not"),
        (r"\bwon['\u2019]t\b", "will not"),
        (r"\bshan['\u2019]t\b", "shall not"),
        (r"\b(\w+)n['\u2019]t\b", r"\1 not"),
        (r"\b(\w+)['\u2019]re\b", r"\1 are"),
        (r"\b(\w+)['\u2019]ll\b", r"\1 will"),
        (r"\b(\w+)['\u2019]ve\b", r"\1 have"),
        (r"\bI['\u2019]m\b", "I am"),
    )
)


def normalize(text: str) -> str:
    """Collapse whitespace, unify quotes and expand common contractions."""
    out = text.translate(_QUOTES)
    for pattern, repl in _CONTRACTIONS:
        out = pattern.sub(repl, out)
    return _WS.sub(" ", out).strip()


def tokenize_raw(text: str) -> tuple[str, ...]:
    """Return tokens with their original capitalisation."""
    return tuple(_TOKEN.findall(text))


def tokenize(text: str) -> tuple[str, ...]:
    """Return lower-cased tokens."""
    return tuple(token.lower() for token in tokenize_raw(text))


@dataclass(frozen=True)
class Sentence:
    """One analysable unit of text."""

    text: str
    original: str
    tokens: tuple[str, ...]
    raw_tokens: tuple[str, ...]

    @classmethod
    def from_text(cls, original: str) -> Sentence:
        text = normalize(original)
        raw = tokenize_raw(text)
        return cls(
            text=text, original=original, tokens=tuple(t.lower() for t in raw), raw_tokens=raw
        )

    @property
    def is_question(self) -> bool:
        return self.text.rstrip().endswith("?")
