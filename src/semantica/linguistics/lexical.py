"""Lemmatisation, synonym classes, antonyms and phrase comparison."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from enum import StrEnum

from semantica.linguistics import lexicon as lx

_SYNONYM_REP: dict[str, str] = {}
for _group in lx.SYNONYM_CLASSES:
    _rep = sorted(_group)[0]
    for _word in _group:
        _SYNONYM_REP[_word] = _rep
del _group, _rep, _word

_NO_STRIP_SUFFIXES = ("ss", "us", "is", "ics")
_NO_STRIP_WORDS = frozenset({"news", "media", "series", "species", "this", "has", "was", "is"})

STOP_WORDS = frozenset(
    set(lx.DETERMINERS)
    | set(lx.PREPOSITIONS)
    | set(lx.BE_FORMS)
    | set(lx.HAVE_FORMS)
    | set(lx.DO_FORMS)
    | set(lx.MODAL_CLASS)
    | set(lx.NEGATION_TOKENS)
    | set(lx.QUANTIFIER_CLASS)
    | set(lx.DEGREE_WORDS)
    | set(lx.EXCLUSIVITY_WORDS)
    | set(lx.ADVERB_MODALS)
    | set(lx.FILLER_WORDS)
    | {"who", "which", "whom", "whose", "what", "to", "so", "than", "very"}
)


def singularize(token: str) -> str:
    """Strip a plural ending with a deliberately small set of rules."""
    if token in _NO_STRIP_WORDS or len(token) <= 3:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith(("ches", "shes", "sses", "xes")):
        return token[:-2]
    if token.endswith("s") and not token.endswith(_NO_STRIP_SUFFIXES):
        return token[:-1]
    return token


def lemma(token: str) -> str:
    """Return the verb lemma if ``token`` is a known verb form, else a singular form."""
    if token in lx.VERB_FORMS:
        return lx.VERB_FORMS[token][0]
    return singularize(token)


def canonical(token: str) -> str:
    """Return the representative of the token's synonym class, or its lemma."""
    if token in lx.NUMBER_WORDS:
        return lx.NUMBER_WORDS[token]
    if token in _SYNONYM_REP:
        return _SYNONYM_REP[token]
    base = lemma(token)
    return _SYNONYM_REP.get(base, base)


def are_synonyms(a: str, b: str) -> bool:
    return canonical(a) == canonical(b)


_ANTONYMS: set[frozenset[str]] = {
    frozenset({canonical(a), canonical(b)}) for a, b in lx.ANTONYM_PAIRS
}


def are_antonyms(a: str, b: str) -> bool:
    return frozenset({canonical(a), canonical(b)}) in _ANTONYMS


def exclusive_group(token: str) -> frozenset[str] | None:
    for group in lx.EXCLUSIVE_SETS:
        if token in group:
            return group
    return None


def content_tokens(tokens: Iterable[str]) -> list[str]:
    """Drop function words, negation, quantifiers and degree words."""
    return [t for t in tokens if t not in STOP_WORDS]


def signature(tokens: Iterable[str]) -> frozenset[str]:
    """Return the set of canonical content words of a phrase."""
    return frozenset(canonical(t) for t in content_tokens(tokens))


class PhraseMatch(StrEnum):
    EQUAL = "equal"
    PARTIAL = "partial"
    DIFFERENT = "different"


def compare_signatures(a: frozenset[str], b: frozenset[str]) -> PhraseMatch:
    """Compare two content signatures.

    ``PARTIAL`` means that at least half of the union is shared, as when a modifier was added
    or dropped. Two empty phrases are equal.
    """
    if a == b:
        return PhraseMatch.EQUAL
    union = a | b
    if union and len(a & b) / len(union) >= 0.5:
        return PhraseMatch.PARTIAL
    return PhraseMatch.DIFFERENT


def compare_phrases(a: Sequence[str], b: Sequence[str]) -> PhraseMatch:
    return compare_signatures(signature(a), signature(b))


_GROUP_OF: dict[str, frozenset[str]] = {
    word: group for group in lx.SYNONYM_CLASSES for word in group
}


def synonym_group(word: str) -> frozenset[str] | None:
    """Return the synonym class that contains ``word`` exactly, or ``None``."""
    return _GROUP_OF.get(word)
