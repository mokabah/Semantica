"""Neutral, pluggable interfaces for optional scoring models.

Semantica does not bundle, download or call any model. A user may supply any object that
satisfies one of the protocols below, for example a wrapper around a sentence encoder or an
entailment classifier of their own choosing. When no object is supplied, the corresponding
checks are reported as ``requires_model``.

Scores returned by a model are treated as *evidence to be reviewed*. A high similarity score
never proves that two sentences mean the same thing.
"""

from __future__ import annotations

import math
from typing import Protocol, runtime_checkable

from semantica.errors import ConfigurationError


@runtime_checkable
class SimilarityModel(Protocol):
    """Returns a similarity in ``[0, 1]`` for a source/candidate pair."""

    def similarity(self, source: str, candidate: str) -> float: ...


@runtime_checkable
class FluencyModel(Protocol):
    """Returns a fluency score in ``[0, 1]`` for a single text."""

    def fluency(self, text: str) -> float: ...


def validated_score(value: object, *, name: str) -> float:
    """Return ``value`` as a float after checking that it is finite and within ``[0, 1]``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigurationError(f"{name} must return a number, got {type(value).__name__}")
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ConfigurationError(f"{name} must return a finite value in [0, 1], got {score!r}")
    return score
