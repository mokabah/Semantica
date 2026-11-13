"""Meaning-change report: construction, JSON export and plain-text rendering."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from semantica import __version__
from semantica.core.context import Context
from semantica.errors import ReportingError
from semantica.evaluation.fidelity import dimension_summary
from semantica.evaluation.semantic_metrics import surface_metrics
from semantica.integrations.model_interface import FluencyModel, SimilarityModel
from semantica.semantics.representation import analyze
from semantica.verification.preservation import verify_representations
from semantica.verification.result import VerificationResult

SCHEMA_VERSION = "1"

CAVEATS = (
    "Statuses come from hand-written rules and a small hand-written lexicon.",
    "An overall status of 'preserved' means no difference was detected, not that the texts are "
    "equivalent.",
    "Checks marked requires_model were not evaluated; no model was used unless one was supplied.",
    "Surface metrics describe wording overlap and were not used to decide any status.",
)


@dataclass(frozen=True)
class MeaningChangeReport:
    """Serialisable record of one comparison."""

    result: VerificationResult
    dimensions: dict[str, dict[str, object]]
    surface: dict[str, float]
    representation: dict[str, dict[str, object]] | None = None

    def to_dict(self) -> dict[str, object]:
        r = self.result
        out: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "tool": {"name": "semantica", "version": __version__},
            "source": r.source,
            "candidate": r.candidate,
            "checks": {c.name: c.status.value for c in r.checks},
            "check_details": [c.to_dict() for c in r.checks],
            "overall_status": r.overall.value,
            "explanation": r.explanation,
            "unverified": list(r.unverified),
            "dimensions": self.dimensions,
            "surface_metrics": self.surface,
            "caveats": list(CAVEATS),
        }
        if self.representation is not None:
            out["representation"] = self.representation
        return out

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, sort_keys=False)

    def write_json(self, path: str | Path) -> Path:
        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(self.to_json() + "\n", encoding="utf-8")
        except OSError as exc:
            raise ReportingError(f"cannot write report to {target}: {exc}") from exc
        return target

    def render_text(self) -> str:
        r = self.result
        lines = [f"Source:    {r.source}", f"Candidate: {r.candidate}", ""]
        width = max(len(c.name) for c in r.checks)
        for c in r.checks:
            lines.append(f"  {c.name:<{width}}  {c.status.value}")
        lines += ["", f"Overall: {r.overall.value}", f"  {r.explanation}"]
        if r.unverified:
            lines.append(f"Unverified (no model supplied): {', '.join(r.unverified)}")
        shown = [c for c in r.checks if c.status.value not in ("passed", "requires_model")]
        if shown:
            lines += ["", "Findings:"]
            lines += [f"  - [{c.status.value}] {c.name}: {c.explanation}" for c in shown]
        return "\n".join(lines)


def build_report(
    source: str,
    candidate: str,
    *,
    context: Sequence[str] | None = None,
    similarity_model: SimilarityModel | None = None,
    fluency_model: FluencyModel | None = None,
    include_representation: bool = False,
) -> MeaningChangeReport:
    """Analyse, verify and package one source/candidate pair."""
    ctx = Context.from_texts(context)
    src, cand = analyze(source, ctx), analyze(candidate, ctx)
    result = verify_representations(
        src, cand, similarity_model=similarity_model, fluency_model=fluency_model
    )
    representation = (
        {"source": src.to_dict(), "candidate": cand.to_dict()} if include_representation else None
    )
    return MeaningChangeReport(
        result, dimension_summary(result), surface_metrics(source, candidate), representation
    )
