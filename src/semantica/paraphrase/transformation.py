"""String-level transformations used to build test candidates.

Two families exist. *Preserving* transformations (synonym substitution, modal interchange)
are intended to keep the meaning. *Meaning-changing* transformations (negation insertion,
modality strengthening, quantifier shift, antonym swap, role swap, number change) are
deliberate mutations used to test whether a verifier notices a change.

All transformations are deterministic, rule-based and share the lexicon with the verifier.
That shared dependency means a verifier agreeing with these generators is *circular
evidence*; see docs/evaluation.md.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from semantica.linguistics import lexicon as lx
from semantica.linguistics.lexical import canonical, synonym_group

_WORD = re.compile(r"[A-Za-z]+")
_BLOCK_PREV = (lx.DETERMINERS | lx.PREPOSITIONS) - {"to"}

Transformation = Callable[[str], "str | None"]


def _match_case(original: str, new: str) -> str:
    return new.capitalize() if original[:1].isupper() else new


def _words(text: str) -> list[re.Match[str]]:
    return list(_WORD.finditer(text))


def _splice(text: str, edits: list[tuple[int, int, str]]) -> str:
    out: list[str] = []
    last = 0
    for start, end, new in sorted(edits):
        out.append(text[last:start])
        out.append(new)
        last = end
    out.append(text[last:])
    return "".join(out)


def _is_verb_use(words: list[str], i: int) -> bool:
    return words[i] in lx.VERB_FORMS and (i == 0 or words[i - 1] not in _BLOCK_PREV)


def _verb_form(lemma: str, slot: int) -> str:
    return lx.VERB_PARADIGMS[lemma][slot]


def _agree_present(words: list[str], subject_end: int, lemma: str) -> str:
    """Return a present-tense form of ``lemma`` agreeing loosely with the subject."""
    head = words[subject_end - 1] if subject_end > 0 else ""
    plural = (head.endswith("s") and not head.endswith("ss")) or head in {"people", "they", "we"}
    return _verb_form(lemma, 0 if plural else 1)


# ---------------------------------------------------------------------------------------
# Meaning-preserving transformations
# ---------------------------------------------------------------------------------------


def substitute_synonyms(text: str) -> str | None:
    """Replace words by the next member of their synonym class, keeping verb inflection."""
    matches = _words(text)
    words = [m.group().lower() for m in matches]
    edits: list[tuple[int, int, str]] = []
    for i, m in enumerate(matches):
        word = words[i]
        replacement: str | None = None
        if _is_verb_use(words, i):
            lemma, slot = lx.VERB_FORMS[word]
            group = synonym_group(lemma)
            if group:
                options = sorted(w for w in group if w != lemma and w in lx.VERB_PARADIGMS)
                if options:
                    replacement = _verb_form(options[0], slot)
        else:
            group = synonym_group(word)
            if group:
                options = sorted(w for w in group if w != word)
                if options:
                    replacement = options[0]
        if replacement:
            edits.append((m.start(), m.end(), _match_case(m.group(), replacement)))
    return _splice(text, edits) if edits else None


_MODAL_SWAP = {"may": "can", "might": "could", "can": "may", "could": "might"}


def swap_modal(text: str) -> str | None:
    """Exchange modal auxiliaries inside the possibility class (may/can, might/could)."""
    for m in _words(text):
        low = m.group().lower()
        if low in _MODAL_SWAP and m.group() != "May":
            return _splice(text, [(m.start(), m.end(), _match_case(m.group(), _MODAL_SWAP[low]))])
    return None


# ---------------------------------------------------------------------------------------
# Meaning-changing transformations
# ---------------------------------------------------------------------------------------


def insert_negation(text: str) -> str | None:
    """Insert "not" after the first modal or auxiliary, or negate the main verb."""
    matches = _words(text)
    words = [m.group().lower() for m in matches]
    for i, word in enumerate(words):
        if word in lx.MODAL_CLASS or word in lx.BE_FORMS or word in lx.HAVE_FORMS:
            if i + 1 < len(words) and words[i + 1] == "not":
                return None
            return _splice(text, [(matches[i].end(), matches[i].end(), " not")])
    for i, word in enumerate(words):
        if _is_verb_use(words, i) and i > 0:
            lemma, slot = lx.VERB_FORMS[word]
            aux = {0: "do", 1: "does", 2: "did"}.get(slot)
            if aux is None:
                continue
            return _splice(text, [(matches[i].start(), matches[i].end(), f"{aux} not {lemma}")])
    return None


def strengthen_modality(text: str) -> str | None:
    """Replace a possibility modal by "must"."""
    for m in _words(text):
        if m.group().lower() in {"may", "might", "could", "can"} and m.group() != "May":
            return _splice(text, [(m.start(), m.end(), _match_case(m.group(), "must"))])
    return None


def remove_modality(text: str) -> str | None:
    """Delete the first possibility modal so that the claim becomes a plain assertion."""
    matches = _words(text)
    words = [m.group().lower() for m in matches]
    for i, word in enumerate(words):
        if word in {"may", "might", "could", "can"} and matches[i].group() != "May":
            if i + 1 >= len(words) or words[i + 1] not in lx.VERB_FORMS:
                continue
            lemma = lx.VERB_FORMS[words[i + 1]][0]
            form = _agree_present(words, i, lemma)
            return _splice(text, [(matches[i].start(), matches[i + 1].end(), form)])
    return None


_STRENGTHEN = {
    "influence": "determine",
    "affect": "determine",
    "impact": "determine",
    "suggest": "prove",
    "indicate": "prove",
    "imply": "prove",
}


def strengthen_predicate(text: str) -> str | None:
    """Replace a weak causal or evidential verb by a strong one."""
    matches = _words(text)
    words = [m.group().lower() for m in matches]
    for i, word in enumerate(words):
        if _is_verb_use(words, i):
            lemma, slot = lx.VERB_FORMS[word]
            if lemma in _STRENGTHEN:
                return _splice(
                    text,
                    [
                        (
                            matches[i].start(),
                            matches[i].end(),
                            _match_case(matches[i].group(), _verb_form(_STRENGTHEN[lemma], slot)),
                        )
                    ],
                )
    return None


_QUANT_SHIFT = {
    "some": "all",
    "many": "all",
    "most": "all",
    "few": "many",
    "all": "some",
    "sometimes": "always",
    "often": "always",
    "always": "sometimes",
    "never": "always",
    "rarely": "often",
    "usually": "always",
}


def shift_quantifier(text: str) -> str | None:
    """Move the first quantifier or frequency word to a different class."""
    for m in _words(text):
        low = m.group().lower()
        if low in _QUANT_SHIFT:
            return _splice(text, [(m.start(), m.end(), _match_case(m.group(), _QUANT_SHIFT[low]))])
    return None


def _antonym_candidates(word: str) -> list[str]:
    out = [b for a, b in lx.ANTONYM_PAIRS if a == word] + [
        a for a, b in lx.ANTONYM_PAIRS if b == word
    ]
    return out


def swap_antonym(text: str) -> str | None:
    """Replace a word that has an entry in the antonym lexicon by its opposite."""
    matches = _words(text)
    words = [m.group().lower() for m in matches]
    for i, word in enumerate(words):
        if _is_verb_use(words, i):
            lemma, slot = lx.VERB_FORMS[word]
            for alt in _antonym_candidates(lemma):
                if alt in lx.VERB_PARADIGMS:
                    return _splice(
                        text,
                        [
                            (
                                matches[i].start(),
                                matches[i].end(),
                                _match_case(matches[i].group(), _verb_form(alt, slot)),
                            )
                        ],
                    )
        else:
            for alt in _antonym_candidates(word):
                if alt not in lx.VERB_PARADIGMS or alt in lx.POSITIVE_WORDS | lx.NEGATIVE_WORDS:
                    return _splice(
                        text,
                        [
                            (
                                matches[i].start(),
                                matches[i].end(),
                                _match_case(matches[i].group(), alt),
                            )
                        ],
                    )
    return None


def swap_roles(text: str) -> str | None:
    """Exchange subject and object of a simple active clause: "A verb B" becomes "B verb A"."""
    stripped = text.strip()
    punct = stripped[-1] if stripped[-1] in ".!?" else ""
    body = stripped[: len(stripped) - len(punct)] if punct else stripped
    matches = _words(body)
    words = [m.group().lower() for m in matches]
    for i, word in enumerate(words):
        if i >= 1 and _is_verb_use(words, i) and word not in lx.BE_FORMS:
            subject = body[: matches[i].start()].strip()
            verb = matches[i].group()
            obj = body[matches[i].end() :].strip()
            if not subject or not obj or len(obj.split()) > 4:
                return None
            if any(w in lx.PREPOSITIONS for w in obj.lower().split()):
                return None
            if any(w in lx.MODAL_CLASS or w in lx.BE_FORMS for w in subject.lower().split()):
                return None
            new_subject = obj[0].upper() + obj[1:]
            words_ = subject.split()
            proper = len(words_) > 1 and any(w[:1].isupper() for w in words_[1:])
            new_object = subject if proper or words_[0] == "I" else subject[0].lower() + subject[1:]
            return f"{new_subject} {verb} {new_object}{punct}"
    return None


def change_number(text: str) -> str | None:
    """Replace the first number (digits or word) by a different one."""
    inverse = {v: k for k, v in lx.NUMBER_WORDS.items() if v.isdigit()}
    for m in re.finditer(r"\b(\d+)\b|\b([A-Za-z]+)\b", text):
        if m.group(1):
            return _splice(text, [(m.start(), m.end(), str(int(m.group(1)) + 10))])
        word = m.group(2).lower()
        if word in lx.NUMBER_WORDS and lx.NUMBER_WORDS[word].isdigit():
            value = int(lx.NUMBER_WORDS[word])
            for step in (1, 2, 3):
                alt = inverse.get(str(value + step))
                if alt:
                    return _splice(text, [(m.start(), m.end(), _match_case(m.group(2), alt))])
    return None


def substitute_exclusive(text: str) -> str | None:
    """Replace a member of a mutually exclusive set (a day, a colour) by another member."""
    for m in _words(text):
        low = m.group().lower()
        for group in lx.EXCLUSIVE_SETS:
            if low in group:
                alt = sorted(w for w in group if w != low)[0]
                return _splice(text, [(m.start(), m.end(), _match_case(m.group(), alt))])
    return None


#: name -> (function, intended to preserve meaning)
TRANSFORMATIONS: dict[str, tuple[Transformation, bool]] = {
    "synonym_substitution": (substitute_synonyms, True),
    "modal_interchange": (swap_modal, True),
    "negation_insertion": (insert_negation, False),
    "modality_strengthening": (strengthen_modality, False),
    "modality_removal": (remove_modality, False),
    "predicate_strengthening": (strengthen_predicate, False),
    "quantifier_shift": (shift_quantifier, False),
    "antonym_swap": (swap_antonym, False),
    "role_swap": (swap_roles, False),
    "number_change": (change_number, False),
    "exclusive_substitution": (substitute_exclusive, False),
}

__all__ = ["TRANSFORMATIONS", "Transformation", "canonical"]
