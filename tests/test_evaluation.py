import json

import pytest

from semantica.errors import ReportingError
from semantica.evaluation.fidelity import DIMENSIONS, dimension_summary
from semantica.evaluation.report import CAVEATS, SCHEMA_VERSION, build_report
from semantica.evaluation.semantic_metrics import (
    canonical_jaccard,
    length_ratio,
    surface_metrics,
    token_jaccard,
)
from semantica.verification.preservation import verify

SRC = "Social media may influence behavior."
CAND = "Social media determines behavior."


def test_surface_metrics_are_wording_only():
    assert token_jaccard("a b c", "a b c") == 1.0
    assert token_jaccard("a b", "c d") == 0.0
    assert token_jaccard("", "") == 1.0
    assert length_ratio("a b", "a b c d") == 2.0
    assert length_ratio("", "a") == 0.0
    # High wording overlap does not imply preservation: negation barely changes the surface.
    assert token_jaccard("The treatment is effective.", "The treatment is not effective.") > 0.7
    assert canonical_jaccard("people think", "individuals think") == 1.0
    assert set(surface_metrics(SRC, CAND)) == {
        "token_jaccard",
        "canonical_content_jaccard",
        "length_ratio",
    }


def test_report_json_schema_and_content():
    report = build_report(SRC, CAND)
    data = json.loads(report.to_json())
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["overall_status"] == "meaning_shift_detected"
    assert data["checks"]["modality_preservation"] == "failed"
    assert data["checks"]["semantic_similarity"] == "requires_model"
    assert data["unverified"] == ["semantic_similarity", "linguistic_fluency"]
    assert data["caveats"] == list(CAVEATS)
    assert "score" not in json.dumps(data["dimensions"]).replace("semantic", "")
    assert all(d["explanation"] for d in data["check_details"])


def test_report_has_no_combined_score():
    data = build_report(SRC, CAND).to_dict()
    assert not any(key in data for key in ("score", "total", "overall_score"))


def test_report_round_trip_to_file(tmp_path):
    path = build_report(SRC, CAND, include_representation=True).write_json(
        tmp_path / "r" / "x.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "representation" in data and data["representation"]["source"]["units"]


def test_report_write_failure_is_wrapped(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(ReportingError):
        build_report(SRC, CAND).write_json(blocker / "sub" / "r.json")


def test_text_rendering_lists_findings():
    text = build_report(SRC, CAND).render_text()
    assert "Overall: meaning_shift_detected" in text
    assert "[failed] modality_preservation" in text
    assert "Unverified (no model supplied)" in text


def test_dimension_summary_uses_strictest_status():
    summary = dimension_summary(verify(SRC, CAND))
    assert set(summary) == set(DIMENSIONS)
    assert summary["epistemic_preservation"]["status"] == "failed"
    assert summary["semantic_similarity"]["status"] == "requires_model"
    assert summary["linguistic_fluency"]["status"] == "requires_model"
    assert summary["pragmatic_preservation"]["status"] == "passed"


def test_report_with_context_changes_context_status():
    without = build_report("She said it was fine.", "The manager said the report was fine.")
    with_ctx = build_report(
        "She said it was fine.",
        "The manager said the report was fine.",
        context=["The manager read the report."],
    )
    assert without.result.overall.value == "insufficient_context"
    assert with_ctx.result.overall.value == "requires_human_review"
