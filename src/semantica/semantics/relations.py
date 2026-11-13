"""Causal, conditional and concessive relations signalled by connectives."""

from __future__ import annotations

import re
from dataclasses import dataclass

from semantica.core.sentence import tokenize
from semantica.linguistics.lexical import signature
from semantica.linguistics.syntax import count_negations

_PREFIX: tuple[tuple[re.Pattern[str], str, bool], ...] = (
    (
        re.compile(
            r"^(?:if|provided that|as long as|in case)\s+(?P<a>.+?),\s*(?:then\s+)?(?P<m>.+)$",
            re.IGNORECASE,
        ),
        "conditional",
        False,
    ),
    (re.compile(r"^unless\s+(?P<a>.+?),\s*(?P<m>.+)$", re.IGNORECASE), "conditional", True),
    (re.compile(r"^because(?: of)?\s+(?P<a>.+?),\s*(?P<m>.+)$", re.IGNORECASE), "causal", False),
    (
        re.compile(
            r"^(?:although|even though|though|whereas)\s+(?P<a>.+?),\s*(?P<m>.+)$", re.IGNORECASE
        ),
        "concessive",
        False,
    ),
)

_SUFFIX: tuple[tuple[re.Pattern[str], str, bool], ...] = (
    (
        re.compile(
            r"^(?P<m>.+?),?\s+(?:because(?: of)?|due to|owing to|as a result of|"
            r"since(?!\s+\d))\s+(?P<a>.+)$",
            re.IGNORECASE,
        ),
        "causal",
        False,
    ),
    (
        re.compile(r"^(?P<m>.+?),?\s+(?:if|provided that|as long as)\s+(?P<a>.+)$", re.IGNORECASE),
        "conditional",
        False,
    ),
    (re.compile(r"^(?P<m>.+?),?\s+unless\s+(?P<a>.+)$", re.IGNORECASE), "conditional", True),
    (
        re.compile(
            r"^(?P<m>.+?),?\s+(?:although|even though|though|whereas)\s+(?P<a>.+)$", re.IGNORECASE
        ),
        "concessive",
        False,
    ),
)

_RESULT = re.compile(
    r"^(?P<c>.+?),\s*(?:and\s+)?(?:therefore|thus|hence|consequently|so)\s*,?\s+(?P<e>.+)$",
    re.IGNORECASE,
)

_FRAGMENT_PUNCT = re.compile(r"[.?!]+$")


@dataclass(frozen=True)
class Relation:
    """``antecedent`` leads to, conditions or is conceded against ``consequent``."""

    kind: str
    antecedent: str
    consequent: str
    negated: bool

    @property
    def antecedent_signature(self) -> frozenset[str]:
        return signature(tokenize(self.antecedent))

    @property
    def consequent_signature(self) -> frozenset[str]:
        return signature(tokenize(self.consequent))

    @property
    def antecedent_negations(self) -> int:
        return count_negations(tokenize(self.antecedent))

    @property
    def consequent_negations(self) -> int:
        return count_negations(tokenize(self.consequent))

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "antecedent": self.antecedent,
            "consequent": self.consequent,
            "negated": self.negated,
        }


def split_relation(text: str) -> tuple[str, Relation | None]:
    """Return the main-clause text and the first relation found, if any.

    Only one relation per unit is extracted. Sentences with several connectives keep the
    remainder inside the main clause, which is documented as a limitation.
    """
    body = _FRAGMENT_PUNCT.sub("", text.strip())
    for pattern, kind, negated in _PREFIX:
        match = pattern.match(body)
        if match:
            main = match.group("m").strip()
            return main, Relation(kind, match.group("a").strip(), main, negated)
    match = _RESULT.match(body)
    if match:
        cause = match.group("c").strip()
        return cause, Relation("causal", cause, match.group("e").strip(), False)
    for pattern, kind, negated in _SUFFIX:
        match = pattern.match(body)
        if match:
            main = match.group("m").strip()
            antecedent = match.group("a").strip()
            if kind == "causal":
                return main, Relation("causal", antecedent, main, negated)
            return main, Relation(kind, antecedent, main, negated)
    return body, None
