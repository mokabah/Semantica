"""Propositions: shallow (agent, predicate, patient) triples with polarity."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from semantica.linguistics.lexical import (
    PhraseMatch,
    are_antonyms,
    are_synonyms,
    compare_signatures,
    signature,
)
from semantica.linguistics.syntax import ParsedClause, parse_clause


@dataclass(frozen=True)
class Proposition:
    """A normalised clause. For passives the agent is stored as ``subject``."""

    subject: tuple[str, ...]
    predicate: str
    object: tuple[str, ...]
    voice: str
    negations: int

    @property
    def subject_signature(self) -> frozenset[str]:
        return signature(self.subject)

    @property
    def object_signature(self) -> frozenset[str]:
        return signature(self.object)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": " ".join(self.subject),
            "predicate": self.predicate,
            "object": " ".join(self.object),
            "voice": self.voice,
            "negations": self.negations,
        }


def extract_proposition(tokens: Sequence[str]) -> Proposition | None:
    """Return the proposition of the main clause, or ``None`` if no predicate was found."""
    parsed: ParsedClause = parse_clause(tokens)
    if parsed.predicate is None:
        return None
    return Proposition(
        parsed.subject, parsed.predicate, parsed.object, parsed.voice, parsed.negations
    )


@dataclass(frozen=True)
class PropositionComparison:
    """Slot-by-slot comparison of two propositions."""

    subject: PhraseMatch
    predicate: str  # "equal" | "antonym" | "different"
    object: PhraseMatch
    swapped: bool
    subject_missing: bool

    @property
    def all_equal(self) -> bool:
        return (
            self.subject is PhraseMatch.EQUAL
            and self.predicate == "equal"
            and self.object is PhraseMatch.EQUAL
            and not self.swapped
        )


def compare_propositions(a: Proposition, b: Proposition) -> PropositionComparison:
    if are_synonyms(a.predicate, b.predicate):
        predicate = "equal"
    elif are_antonyms(a.predicate, b.predicate):
        predicate = "antonym"
    else:
        predicate = "different"
    subject = compare_signatures(a.subject_signature, b.subject_signature)
    obj = compare_signatures(a.object_signature, b.object_signature)
    cross_subject = compare_signatures(a.subject_signature, b.object_signature)
    cross_object = compare_signatures(a.object_signature, b.subject_signature)
    swapped = (
        bool(a.subject_signature)
        and bool(a.object_signature)
        and subject is PhraseMatch.DIFFERENT
        and obj is PhraseMatch.DIFFERENT
        and cross_subject is PhraseMatch.EQUAL
        and cross_object is PhraseMatch.EQUAL
    )
    missing = bool(a.subject) != bool(b.subject)
    return PropositionComparison(subject, predicate, obj, swapped, missing)
