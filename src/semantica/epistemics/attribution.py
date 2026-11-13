"""Detection of attribution frames such as "according to X" or "X said that"."""

from __future__ import annotations

import re
from dataclasses import dataclass

from semantica.linguistics import lexicon as lx
from semantica.linguistics.lexical import signature

_ACCORDING = re.compile(r"^according to (?P<src>[^,]+?),\s*(?P<body>.+)$", re.IGNORECASE)
_IT_IS = re.compile(
    r"^it is (?P<verb>reported|said|stated|claimed|alleged|believed|thought|suggested|known|"
    r"shown) that (?P<body>.+)$",
    re.IGNORECASE,
)
_ADVERB = re.compile(r"\b(reportedly|allegedly|supposedly)\b,?\s*", re.IGNORECASE)

_SOURCE_BLOCK = frozenset(
    set(lx.MODAL_CLASS)
    | set(lx.BE_FORMS)
    | set(lx.HAVE_FORMS)
    | set(lx.DO_FORMS)
    | {"not", "never"}
)


@dataclass(frozen=True)
class Attribution:
    """Who is said to hold the embedded claim, and how the report is framed."""

    source: str
    source_signature: frozenset[str]
    verb_class: str

    def to_dict(self) -> dict[str, object]:
        return {"source": self.source, "verb_class": self.verb_class}


def strip_attribution(text: str) -> tuple[Attribution | None, str]:
    """Return the attribution frame (if any) and the embedded clause text."""
    stripped = text.strip().rstrip(".")
    match = _ACCORDING.match(stripped)
    if match:
        source = match.group("src").strip().lower()
        return (
            Attribution(source, signature(source.split()), "neutral"),
            _terminate(match.group("body"), text),
        )
    match = _IT_IS.match(stripped)
    if match:
        cls = lx.PASSIVE_REPORT_CLASS[match.group("verb").lower()]
        return (Attribution("unspecified", frozenset(), cls), _terminate(match.group("body"), text))
    found = _match_says(stripped)
    if found is not None:
        return found[0], _terminate(found[1], text)
    adverb = _ADVERB.search(stripped)
    if adverb:
        cls = lx.ADVERBIAL_ATTRIBUTION[adverb.group(1).lower()]
        body = _ADVERB.sub("", stripped, count=1)
        return Attribution("unspecified", frozenset(), cls), _terminate(body, text)
    return None, text


def _match_says(text: str) -> tuple[Attribution, str] | None:
    words = text.split()
    for idx in range(1, min(7, len(words) - 1)):
        entry = lx.VERB_FORMS.get(words[idx].lower())
        if entry is None or entry[0] not in lx.REPORTING_VERB_CLASS:
            continue
        if words[idx - 1].lower() in lx.DETERMINERS:
            continue
        source_words = words[:idx]
        if any(w.lower() in _SOURCE_BLOCK for w in source_words):
            continue
        rest = words[idx + 1 :]
        if rest[0].lower() == "that":
            rest = rest[1:]
        elif entry[0] not in lx.BARE_REPORTING_VERBS:
            continue
        if not rest:
            continue
        source = " ".join(source_words).lower()
        attribution = Attribution(
            source, signature(source.split()), lx.REPORTING_VERB_CLASS[entry[0]]
        )
        return attribution, " ".join(rest)
    return None


def _terminate(body: str, original: str) -> str:
    body = body.strip()
    if original.rstrip().endswith("?") and not body.endswith("?"):
        return body + "?"
    return body
