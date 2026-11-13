"""Exception hierarchy for Semantica."""

from __future__ import annotations


class SemanticaError(Exception):
    """Base class for all errors raised deliberately by Semantica."""


class InputError(SemanticaError, ValueError):
    """Raised when text input is missing, malformed or too large."""


class ConfigurationError(SemanticaError, ValueError):
    """Raised when a parameter or an external model interface is invalid."""


class ReportingError(SemanticaError):
    """Raised when results cannot be serialised or written."""
