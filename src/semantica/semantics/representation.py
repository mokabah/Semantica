"""Layered representation of a text, built from the individual analysers.

The representation is a plain data structure. It does not contain a semantic vector, a truth
value or a score; it records what the rule-based analysers could extract, so that two
representations can be compared check by check.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from semantica.core.context import Context
from semantica.core.document import Document
from semantica.core.sentence import tokenize_raw
from semantica.epistemics.attribution import Attribution, strip_attribution
from semantica.epistemics.modality import ModalityProfile, detect_modality
from semantica.linguistics import lexicon as lx
from semantica.linguistics.syntax import count_negations, parse_clause
from semantica.pragmatics.discourse import strip_leading_marker
from semantica.pragmatics.intent import Intent, classify_intent, evaluative_polarity
from semantica.semantics.proposition import Proposition, extract_proposition
from semantica.semantics.relations import Relation, split_relation

_NUMBER = re.compile(r"^\d+(?:[.,]\d+)*$")
_BUT = re.compile(r",?\s+but\s+", re.IGNORECASE)
_AND = re.compile(r",\s+and\s+", re.IGNORECASE)


@dataclass(frozen=True)
class UnitRepresentation:
    """Analysis of one sentence or one coordinated clause."""

    text: str
    main_text: str
    main_tokens: tuple[str, ...]
    proposition: Proposition | None
    relation: Relation | None
    attribution: Attribution | None
    modality: ModalityProfile
    quantifiers: tuple[str, ...]
    negations: int
    intent: Intent
    polarity: int
    functions: tuple[str, ...]
    numbers: frozenset[str]
    proper_nouns: frozenset[str]
    exclusives: tuple[str, ...]
    pronouns: tuple[str, ...]
    degree_words: tuple[str, ...]
    exclusivity: tuple[str, ...]
    body_tokens: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "main_clause": self.main_text,
            "proposition": self.proposition.to_dict() if self.proposition else None,
            "relation": self.relation.to_dict() if self.relation else None,
            "attribution": self.attribution.to_dict() if self.attribution else None,
            "modality": self.modality.to_dict(),
            "quantifiers": list(self.quantifiers),
            "negations": self.negations,
            "intent": self.intent.act,
            "polarity": self.polarity,
            "discourse_functions": list(self.functions),
            "numbers": sorted(self.numbers),
            "proper_nouns": sorted(self.proper_nouns),
        }


@dataclass(frozen=True)
class TextRepresentation:
    """Analysis of a whole text: one :class:`UnitRepresentation` per unit."""

    text: str
    units: tuple[UnitRepresentation, ...]
    context: Context

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "units": [u.to_dict() for u in self.units],
            "context_sentences": len(self.context.sentences),
        }


def detect_quantifiers(tokens: Sequence[str]) -> tuple[str, ...]:
    """Return quantifier classes in order of appearance, consuming "not all" style bigrams."""
    found: list[str] = []
    i = 0
    while i < len(tokens):
        pair = tuple(tokens[i : i + 2])
        if pair in {("not", "all"), ("not", "every"), ("not", "always")}:
            found.append("not_all")
            i += 2
            continue
        if pair == ("a", "few"):
            found.append("some")
            i += 2
            continue
        cls = lx.QUANTIFIER_CLASS.get(tokens[i])
        if cls is not None:
            found.append(cls)
        i += 1
    return tuple(found)


def _numbers(tokens: Iterable[str]) -> frozenset[str]:
    out: set[str] = set()
    for token in tokens:
        if _NUMBER.match(token):
            out.add(token.replace(",", ""))
        elif token in lx.NUMBER_WORDS:
            out.add(lx.NUMBER_WORDS[token])
    return frozenset(out)


def _proper_nouns(raw: Sequence[str]) -> frozenset[str]:
    names: set[str] = set()
    for i, token in enumerate(raw):
        if not token[:1].isupper() or token == "I":
            continue
        if i > 0 or (len(raw) > 1 and raw[1][:1].isupper()):
            names.add(token.lower())
    return frozenset(names)


def _has_predicate(text: str) -> bool:
    parsed = parse_clause([t.lower() for t in tokenize_raw(text)])
    return parsed.predicate is not None


def split_units(sentence: str) -> list[tuple[str | None, str]]:
    """Split a sentence into coordinated clauses with the discourse function that links them."""
    units: list[tuple[str | None, str]] = []
    for piece in (p.strip() for p in sentence.split(";")):
        if not piece:
            continue
        link: str | None = "addition" if units else None
        parts = _split_coordination(piece)
        for k, (function, part) in enumerate(parts):
            units.append((function if k else link, part))
    return units


def _split_coordination(piece: str) -> list[tuple[str | None, str]]:
    """Split once at the first coordinator whose both sides contain a predicate."""
    for pattern, function in ((_BUT, "contrast"), (_AND, "addition")):
        match = pattern.search(piece)
        if match:
            left = piece[: match.start()].strip()
            right = piece[match.end() :].strip()
            if _has_predicate(left) and _has_predicate(right):
                return [
                    (None, left),
                    *[
                        (function if k == 0 else f, t)
                        for k, (f, t) in enumerate(_split_coordination(right))
                    ],
                ]
    return [(None, piece)]


def analyze_unit(text: str, link_function: str | None = None) -> UnitRepresentation:
    """Analyse one unit of text."""
    function, rest = strip_leading_marker(text)
    functions = tuple(f for f in (link_function, function) if f)
    attribution, body = strip_attribution(rest)
    main_text, relation = split_relation(body)
    raw_main = tokenize_raw(main_text)
    main = tuple(t.lower() for t in raw_main)
    raw_body = tokenize_raw(body)
    body_tokens = tuple(t.lower() for t in raw_body)
    negations = count_negations(main)
    return UnitRepresentation(
        text=text,
        main_text=main_text,
        main_tokens=main,
        proposition=extract_proposition(main),
        relation=relation,
        attribution=attribution,
        modality=detect_modality(raw_main),
        quantifiers=detect_quantifiers(body_tokens),
        negations=negations,
        intent=classify_intent(body, body_tokens),
        polarity=evaluative_polarity(main, negations),
        functions=functions,
        numbers=_numbers(body_tokens),
        proper_nouns=_proper_nouns(raw_body),
        exclusives=tuple(t for t in body_tokens if _is_exclusive(t)),
        pronouns=tuple(sorted(t for t in body_tokens if t in lx.PRONOUNS)),
        degree_words=tuple(sorted(t for t in body_tokens if t in lx.DEGREE_WORDS)),
        exclusivity=tuple(sorted(t for t in body_tokens if t in lx.EXCLUSIVITY_WORDS)),
        body_tokens=body_tokens,
    )


def _is_exclusive(token: str) -> bool:
    return any(token in group for group in lx.EXCLUSIVE_SETS)


def analyze(text: str, context: Context | None = None) -> TextRepresentation:
    """Analyse ``text`` sentence by sentence and clause by clause."""
    document = Document.from_text(text)
    units: list[UnitRepresentation] = []
    for sentence in document.sentences:
        for function, piece in split_units(sentence.text):
            units.append(analyze_unit(piece, function))
    return TextRepresentation(text=text, units=tuple(units), context=context or Context())
