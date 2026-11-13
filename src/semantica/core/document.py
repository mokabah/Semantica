"""Sentence segmentation and the :class:`Document` container."""

from __future__ import annotations

import re
from dataclasses import dataclass

from semantica.core.sentence import Sentence
from semantica.errors import InputError
from semantica.linguistics.lexicon import AMBIGUITY_ABBREVIATIONS

MAX_CHARS = 20_000
_BOUNDARY = re.compile(r"([.!?]+[\"')\]]*)(\s+)(?=[\"'(\[]?[A-Z0-9])")


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into sentences with a conservative regular-expression rule.

    Abbreviations from a short hand-written list do not end a sentence. Quotations that span
    several sentences and unusual punctuation are not handled.
    """
    pieces: list[str] = []
    start = 0
    for match in _BOUNDARY.finditer(text):
        head = text[start : match.start(1)]
        last_word = head.rsplit(None, 1)[-1].lower().strip("\"'([") if head.split() else ""
        if match.group(1).startswith(".") and last_word in AMBIGUITY_ABBREVIATIONS:
            continue
        pieces.append(text[start : match.end(1)].strip())
        start = match.end()
    tail = text[start:].strip()
    if tail:
        pieces.append(tail)
    return [piece for piece in pieces if piece]


@dataclass(frozen=True)
class Document:
    """An ordered collection of sentences."""

    text: str
    sentences: tuple[Sentence, ...]

    @classmethod
    def from_text(cls, text: str, max_chars: int = MAX_CHARS) -> Document:
        if not isinstance(text, str):
            raise InputError(f"text must be a string, got {type(text).__name__}")
        if not text.strip():
            raise InputError("text is empty")
        if len(text) > max_chars:
            raise InputError(f"text has {len(text)} characters; the limit is {max_chars}")
        sentences = tuple(Sentence.from_text(piece) for piece in split_sentences(text))
        return cls(text=text, sentences=sentences)

    def __len__(self) -> int:
        return len(self.sentences)
