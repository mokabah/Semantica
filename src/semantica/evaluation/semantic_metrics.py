"""Surface-overlap metrics.

These numbers describe *wording*, not meaning. They are provided because researchers often
want to report them next to verification results, and because a large gap between wording
overlap and verification outcome is itself informative (for example, high overlap with a
detected negation). They are never used to decide a verification status.
"""

from __future__ import annotations

from semantica.core.sentence import tokenize
from semantica.linguistics.lexical import canonical, content_tokens


def token_jaccard(source: str, candidate: str) -> float:
    """Jaccard overlap of lower-cased surface tokens."""
    a, b = set(tokenize(source)), set(tokenize(candidate))
    return len(a & b) / len(a | b) if a | b else 1.0


def canonical_jaccard(source: str, candidate: str) -> float:
    """Jaccard overlap of content words after synonym and lemma normalisation."""
    a = {canonical(t) for t in content_tokens(tokenize(source))}
    b = {canonical(t) for t in content_tokens(tokenize(candidate))}
    return len(a & b) / len(a | b) if a | b else 1.0


def length_ratio(source: str, candidate: str) -> float:
    """Candidate token count divided by source token count."""
    n = len(tokenize(source))
    return len(tokenize(candidate)) / n if n else 0.0


def surface_metrics(source: str, candidate: str) -> dict[str, float]:
    return {
        "token_jaccard": round(token_jaccard(source, candidate), 4),
        "canonical_content_jaccard": round(canonical_jaccard(source, candidate), 4),
        "length_ratio": round(length_ratio(source, candidate), 4),
    }
