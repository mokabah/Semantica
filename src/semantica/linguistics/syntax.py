"""Shallow clause analysis: main verb, subject, object, voice and negation count.

This is a rule-based approximation, not a parser. It handles simple declarative clauses with
one main verb. Relative clauses, coordination inside a clause, ellipsis and long-distance
dependencies are not supported and are documented in docs/methodology.md.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from semantica.linguistics import lexicon as lx

_VERB_BLOCKERS = frozenset((lx.DETERMINERS | lx.PREPOSITIONS | lx.RELATIVIZERS) - {"to"})
_PRE_VERB_STOP = frozenset(
    set(lx.MODAL_CLASS)
    | set(lx.BE_FORMS)
    | set(lx.HAVE_FORMS)
    | set(lx.DO_FORMS)
    | {"not", "never"}
    | set(lx.ADVERB_MODALS)
    | {w for w, c in lx.QUANTIFIER_CLASS.items() if w.endswith("ly")}
    | set(lx.DEGREE_WORDS)
    | {"also", "only", "just", "appears", "appear", "seems", "seem", "tends", "tend"}
)


@dataclass(frozen=True)
class ParsedClause:
    """Result of :func:`parse_clause`."""

    subject: tuple[str, ...]
    predicate: str | None
    object: tuple[str, ...]
    voice: str
    negations: int


def count_negations(tokens: Sequence[str]) -> int:
    """Count tokens that carry explicit or implicit negation."""
    return sum(1 for token in tokens if token in lx.NEGATION_TOKENS)


def _find_main_verb(tokens: Sequence[str]) -> int | None:
    candidates: list[int] = []
    for i, token in enumerate(tokens):
        if token not in lx.VERB_FORMS:
            continue
        if i > 0 and tokens[i - 1] in _VERB_BLOCKERS:
            continue
        candidates.append(i)
    for i in candidates:
        if i >= 1:
            return i
    return candidates[0] if candidates else None


def _prev_skipping_adverbs(tokens: Sequence[str], index: int) -> str | None:
    j = index - 1
    while j >= 0 and (
        tokens[j] in lx.NEGATION_TOKENS or tokens[j] in lx.DEGREE_WORDS or tokens[j].endswith("ly")
    ):
        j -= 1
    return tokens[j] if j >= 0 else None


def parse_clause(tokens: Sequence[str]) -> ParsedClause:
    """Extract a normalised (agent, predicate, patient) triple from one clause."""
    toks = list(tokens)
    negations = count_negations(toks)
    verb_index = _find_main_verb(toks)
    if verb_index is None:
        copula = next((i for i, t in enumerate(toks) if t in lx.BE_FORMS), None)
        if copula is None:
            return ParsedClause((), None, tuple(toks), "active", negations)
        subject = _subject(toks[:copula])
        return ParsedClause(subject, "be", tuple(toks[copula + 1 :]), "active", negations)

    verb = toks[verb_index]
    lemma_, slot = lx.VERB_FORMS[verb]
    pre = toks[:verb_index]
    post = toks[verb_index + 1 :]
    before = _prev_skipping_adverbs(toks, verb_index)
    passive = before in lx.BE_FORMS and verb in lx.PARTICIPLE_FORMS and slot in (2, 3)

    if passive:
        patient = _subject(pre)
        if "by" in post:
            cut = post.index("by")
            agent = tuple(post[cut + 1 :])
            return ParsedClause(agent, lemma_, patient, "passive", negations)
        return ParsedClause((), lemma_, patient, "passive", negations)
    return ParsedClause(_subject(pre), lemma_, tuple(post), "active", negations)


def _subject(pre: Sequence[str]) -> tuple[str, ...]:
    subject: list[str] = []
    for token in pre:
        if token in _PRE_VERB_STOP:
            break
        subject.append(token)
    return tuple(subject)
