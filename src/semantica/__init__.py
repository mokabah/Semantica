"""Semantica: Semantic Understanding & Meaning-Preserving Paraphrase Toolkit."""

__version__ = "0.1.0"

from semantica.evaluation.report import build_report
from semantica.verification.preservation import verify

__all__ = ["__version__", "build_report", "verify"]
