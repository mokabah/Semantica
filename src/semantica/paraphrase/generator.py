"""Candidate generation for tests and for building annotation material.

The generator is *not* used by the verifier. It exists to produce correct and incorrect
paraphrases for experiments. Because it shares the lexicon with the verifier, its outputs are
circular evidence about verifier quality; use the hand-written benchmark for validation.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantica.errors import InputError
from semantica.paraphrase.transformation import TRANSFORMATIONS


@dataclass(frozen=True)
class Candidate:
    """A generated text together with the transformation that produced it."""

    text: str
    transformation: str
    intended_preserving: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "transformation": self.transformation,
            "intended_preserving": self.intended_preserving,
        }


class ParaphraseGenerator:
    """Apply each registered transformation once and collect distinct candidates."""

    def __init__(self, transformations: list[str] | None = None) -> None:
        names = transformations if transformations is not None else list(TRANSFORMATIONS)
        unknown = [n for n in names if n not in TRANSFORMATIONS]
        if unknown:
            raise InputError(f"unknown transformation(s): {', '.join(unknown)}")
        self.names = names

    def generate(self, source: str) -> list[Candidate]:
        if not isinstance(source, str) or not source.strip():
            raise InputError("source must be a non-empty string")
        seen = {source}
        out: list[Candidate] = []
        for name in self.names:
            func, preserving = TRANSFORMATIONS[name]
            text = func(source)
            if text is None or text in seen:
                continue
            seen.add(text)
            out.append(Candidate(text, name, preserving))
        return out

    def preserving(self, source: str) -> list[Candidate]:
        return [c for c in self.generate(source) if c.intended_preserving]

    def changing(self, source: str) -> list[Candidate]:
        return [c for c in self.generate(source) if not c.intended_preserving]
