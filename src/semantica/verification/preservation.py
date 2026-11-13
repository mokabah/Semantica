"""Structural checks and the top-level :func:`verify` entry point.

This module deliberately does not import :mod:`semantica.paraphrase`: the component that
judges a candidate must stay independent of the component that produces candidates.
"""

from __future__ import annotations

from collections.abc import Sequence

from semantica.core.context import Context
from semantica.core.status import CHECK_SEVERITY, CheckStatus, OverallStatus
from semantica.integrations.model_interface import (
    FluencyModel,
    SimilarityModel,
    validated_score,
)
from semantica.linguistics import lexicon as lx
from semantica.linguistics.lexical import (
    PhraseMatch,
    compare_phrases,
    compare_signatures,
    exclusive_group,
)
from semantica.semantics.proposition import compare_propositions
from semantica.semantics.representation import TextRepresentation, UnitRepresentation, analyze
from semantica.verification.contradiction import contradiction_screen, negation_preservation
from semantica.verification.entailment import (
    claim_strength_preservation,
    modality_preservation,
    modifier_preservation,
    quantifier_preservation,
)
from semantica.verification.result import CheckResult, VerificationResult

#: Checks that need an external model. A missing model never blocks the overall status.
MODEL_CHECKS = ("semantic_similarity", "linguistic_fluency")

SIMILARITY_THRESHOLD = 0.80
FLUENCY_THRESHOLD = 0.50


# ---------------------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------------------


def proposition_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare agent, action and patient of the main clauses."""
    pa, pb = a.proposition, b.proposition
    if pa is None and pb is None:
        match = compare_phrases(a.main_tokens, b.main_tokens)
        status = {
            PhraseMatch.EQUAL: CheckStatus.PASSED,
            PhraseMatch.PARTIAL: CheckStatus.CAUTION,
            PhraseMatch.DIFFERENT: CheckStatus.REQUIRES_REVIEW,
        }[match]
        return CheckResult(
            "proposition_preservation",
            status,
            "No predicate from the built-in verb lexicon was found in either "
            f"unit, so content words were compared instead ({match.value}).",
            {"fallback": "content_words"},
        )
    if pa is None or pb is None:
        return CheckResult(
            "proposition_preservation",
            CheckStatus.REQUIRES_REVIEW,
            "No predicate could be extracted from one of the units, so the "
            "proposition cannot be compared.",
        )
    cmp = compare_propositions(pa, pb)
    details: dict[str, object] = {
        "source": pa.to_dict(),
        "candidate": pb.to_dict(),
        "subject": cmp.subject.value,
        "predicate": cmp.predicate,
        "object": cmp.object.value,
    }
    if cmp.swapped:
        return CheckResult(
            "proposition_preservation",
            CheckStatus.FAILED,
            "Agent and patient are exchanged between source and candidate.",
            details,
        )
    changed: list[str] = []
    if cmp.subject is PhraseMatch.DIFFERENT:
        changed.append("subject")
    if cmp.predicate != "equal":
        changed.append("action")
    if cmp.object is PhraseMatch.DIFFERENT:
        changed.append("object")
    if cmp.subject_missing and "subject" not in changed:
        changed.append("subject")
    details["changed"] = changed
    if changed:
        return CheckResult(
            "proposition_preservation",
            CheckStatus.REQUIRES_REVIEW,
            f"The {', '.join(changed)} of the proposition differs and no equivalence is "
            "recorded in the lexicon; a human reader should decide whether it is a paraphrase.",
            details,
        )
    if PhraseMatch.PARTIAL in (cmp.subject, cmp.object):
        return CheckResult(
            "proposition_preservation",
            CheckStatus.CAUTION,
            "Subject or object overlaps but is not identical, for example a "
            "modifier was added or dropped.",
            details,
        )
    return CheckResult(
        "proposition_preservation",
        CheckStatus.PASSED,
        "Subject, action and object are identical or recorded synonyms.",
        details,
    )


def relation_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare causal, conditional and concessive relations including direction."""
    ra, rb = a.relation, b.relation
    if ra is None and rb is None:
        return CheckResult(
            "relation_preservation",
            CheckStatus.PASSED,
            "Neither unit contains a connective-marked relation.",
        )
    if ra is None or rb is None:
        present = rb if ra is None else ra
        other = a if ra is None else b
        assert present is not None
        predicate = other.proposition.predicate if other.proposition else None
        if present.kind == "causal" and predicate in lx.CAUSAL_VERBS:
            return CheckResult(
                "relation_preservation",
                CheckStatus.REQUIRES_REVIEW,
                "One unit states the causal relation with a connective and the "
                "other with a causal verb; direction cannot be verified.",
            )
        side = "candidate" if ra is None else "source"
        return CheckResult(
            "relation_preservation",
            CheckStatus.FAILED,
            f"A {present.kind} relation appears only in the {side}.",
            {"relation": present.to_dict()},
        )
    details: dict[str, object] = {"source": ra.to_dict(), "candidate": rb.to_dict()}
    if ra.kind != rb.kind:
        return CheckResult(
            "relation_preservation",
            CheckStatus.FAILED,
            f"Relation type changed from {ra.kind} to {rb.kind}.",
            details,
        )
    if ra.negated != rb.negated:
        return CheckResult(
            "relation_preservation",
            CheckStatus.FAILED,
            "A condition was converted between 'if' and 'unless'.",
            details,
        )
    ante = compare_signatures(ra.antecedent_signature, rb.antecedent_signature)
    cons = compare_signatures(ra.consequent_signature, rb.consequent_signature)
    rev_a = compare_signatures(ra.antecedent_signature, rb.consequent_signature)
    rev_c = compare_signatures(ra.consequent_signature, rb.antecedent_signature)
    if (
        ante is PhraseMatch.DIFFERENT
        and cons is PhraseMatch.DIFFERENT
        and rev_a is PhraseMatch.EQUAL
        and rev_c is PhraseMatch.EQUAL
    ):
        return CheckResult(
            "relation_preservation",
            CheckStatus.FAILED,
            "The direction of the relation is reversed (cause and effect, or "
            "condition and result, are exchanged).",
            details,
        )
    if (
        ra.antecedent_negations % 2 != rb.antecedent_negations % 2
        or ra.consequent_negations % 2 != rb.consequent_negations % 2
    ):
        return CheckResult(
            "relation_preservation",
            CheckStatus.FAILED,
            "Negation inside the antecedent or consequent differs.",
            details,
        )
    if ante is PhraseMatch.EQUAL and cons is PhraseMatch.EQUAL:
        return CheckResult(
            "relation_preservation",
            CheckStatus.PASSED,
            f"The {ra.kind} relation and its direction are preserved.",
            details,
        )
    return CheckResult(
        "relation_preservation",
        CheckStatus.REQUIRES_REVIEW,
        "Relation type and direction agree but the related clauses are not recorded as equivalent.",
        details,
    )


def attribution_preservation(
    a: UnitRepresentation, b: UnitRepresentation, context: Context
) -> CheckResult:
    """Compare who is said to hold the claim and how the report is framed."""
    xa, xb = a.attribution, b.attribution
    if xa is None and xb is None:
        return CheckResult(
            "attribution_preservation",
            CheckStatus.PASSED,
            "Neither unit attributes the claim to a source.",
        )
    if xa is None or xb is None:
        side = "candidate" if xa is None else "source"
        return CheckResult(
            "attribution_preservation",
            CheckStatus.FAILED,
            f"Attribution appears only in the {side}; the commitment of the speaker changes.",
        )
    details: dict[str, object] = {"source": xa.to_dict(), "candidate": xb.to_dict()}
    if _is_pronoun_source(xa.source) != _is_pronoun_source(xb.source):
        if context.is_empty:
            return CheckResult(
                "attribution_preservation",
                CheckStatus.INSUFFICIENT_CONTEXT,
                "One source is a pronoun and the other a noun phrase; the "
                "referent cannot be checked without context.",
                details,
            )
        return CheckResult(
            "attribution_preservation",
            CheckStatus.REQUIRES_REVIEW,
            "One source is a pronoun and the other a noun phrase; coreference is "
            "not implemented, so a human reader must confirm the referent.",
            details,
        )
    match = compare_signatures(xa.source_signature, xb.source_signature)
    if xa.source == xb.source:
        match = PhraseMatch.EQUAL
    if match is PhraseMatch.DIFFERENT:
        return CheckResult(
            "attribution_preservation",
            CheckStatus.FAILED,
            "The attributed source differs.",
            details,
        )
    if match is PhraseMatch.PARTIAL:
        return CheckResult(
            "attribution_preservation",
            CheckStatus.REQUIRES_REVIEW,
            "The attributed source overlaps but is not identical.",
            details,
        )
    if {xa.verb_class, xb.verb_class} == {"tentative", "finding"}:
        return CheckResult(
            "attribution_preservation",
            CheckStatus.FAILED,
            f"Same source, but the reporting frame changed from "
            f"'{xa.verb_class}' to '{xb.verb_class}'; the strength of the "
            "reported claim differs.",
            details,
        )
    if xa.verb_class != xb.verb_class:
        return CheckResult(
            "attribution_preservation",
            CheckStatus.REQUIRES_REVIEW,
            f"Same source, but the reporting frame changed from "
            f"'{xa.verb_class}' to '{xb.verb_class}'.",
            details,
        )
    return CheckResult(
        "attribution_preservation",
        CheckStatus.PASSED,
        "Source and reporting frame are preserved.",
        details,
    )


def entity_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare numbers, capitalised names and members of mutually exclusive sets."""
    details: dict[str, object] = {}
    failed: list[str] = []
    review: list[str] = []

    if a.numbers != b.numbers:
        details["numbers"] = {"source": sorted(a.numbers), "candidate": sorted(b.numbers)}
        (failed if a.numbers and b.numbers else review).append("numbers")
    if a.proper_nouns != b.proper_nouns:
        details["names"] = {"source": sorted(a.proper_nouns), "candidate": sorted(b.proper_nouns)}
        both_sides = bool(a.proper_nouns - b.proper_nouns) and bool(b.proper_nouns - a.proper_nouns)
        (failed if both_sides else review).append("names")
    substitutions: list[dict[str, list[str]]] = []
    for group in lx.EXCLUSIVE_SETS:
        ga = {t for t in a.exclusives if t in group}
        gb = {t for t in b.exclusives if t in group}
        if ga and gb and ga != gb:
            substitutions.append({"source": sorted(ga), "candidate": sorted(gb)})
            details["exclusive_substitutions"] = substitutions
            failed.append("exclusive_set")
        elif ga != gb and exclusive_group(next(iter(ga | gb))) is not None:
            review.append("exclusive_set")
    if failed:
        return CheckResult(
            "entity_preservation",
            CheckStatus.FAILED,
            f"Entity substitution detected in: {', '.join(dict.fromkeys(failed))}.",
            details,
        )
    if review:
        return CheckResult(
            "entity_preservation",
            CheckStatus.REQUIRES_REVIEW,
            f"Entities appear only on one side: {', '.join(dict.fromkeys(review))}.",
            details,
        )
    return CheckResult(
        "entity_preservation",
        CheckStatus.PASSED,
        "Numbers, names and exclusive-set members are identical.",
    )


def _is_pronoun_source(source: str) -> bool:
    return source in lx.PRONOUNS or source in {"i", "we", "you"}


def pragmatic_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare speech act and evaluative polarity."""
    details: dict[str, object] = {
        "source_act": a.intent.act,
        "candidate_act": b.intent.act,
        "source_polarity": a.polarity,
        "candidate_polarity": b.polarity,
    }
    if a.intent.act != b.intent.act:
        return CheckResult(
            "pragmatic_preservation",
            CheckStatus.FAILED,
            f"The speech act changed from {a.intent.act} to {b.intent.act}.",
            details,
        )
    if a.polarity * b.polarity < 0:
        return CheckResult(
            "pragmatic_preservation",
            CheckStatus.FAILED,
            "The evaluative polarity (favourable versus unfavourable) is reversed.",
            details,
        )
    if a.polarity != b.polarity:
        return CheckResult(
            "pragmatic_preservation",
            CheckStatus.CAUTION,
            "An evaluative word appears only on one side.",
            details,
        )
    return CheckResult(
        "pragmatic_preservation",
        CheckStatus.PASSED,
        "Speech act and evaluative polarity agree.",
        details,
    )


def discourse_preservation(a: UnitRepresentation, b: UnitRepresentation) -> CheckResult:
    """Compare discourse functions such as contrast, addition and result."""
    fa, fb = sorted(a.functions), sorted(b.functions)
    details: dict[str, object] = {"source": fa, "candidate": fb}
    if fa == fb:
        return CheckResult(
            "discourse_preservation",
            CheckStatus.PASSED,
            "Discourse functions are identical.",
            details,
        )
    return CheckResult(
        "discourse_preservation",
        CheckStatus.REQUIRES_REVIEW,
        "Discourse functions differ; the relation to the surrounding text may have changed.",
        details,
    )


def contextual_consistency(
    a: UnitRepresentation, b: UnitRepresentation, context: Context
) -> CheckResult:
    """Detect pronoun alternation, which cannot be verified without coreference resolution."""
    details: dict[str, object] = {
        "source_pronouns": list(a.pronouns),
        "candidate_pronouns": list(b.pronouns),
    }
    if a.pronouns == b.pronouns:
        return CheckResult(
            "contextual_consistency",
            CheckStatus.PASSED,
            "Pronouns are identical; no context-dependent substitution was detected.",
            details,
        )
    if context.is_empty:
        return CheckResult(
            "contextual_consistency",
            CheckStatus.INSUFFICIENT_CONTEXT,
            "Pronouns were added, dropped or replaced and no context was "
            "supplied, so the referents cannot be checked.",
            details,
        )
    return CheckResult(
        "contextual_consistency",
        CheckStatus.REQUIRES_REVIEW,
        "Pronouns differ. Context was supplied, but coreference resolution is "
        "not implemented, so a human reader must confirm the referents.",
        details,
    )


# ---------------------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------------------

_UNIT_CHECKS = (
    "negation_preservation",
    "modality_preservation",
    "claim_strength_preservation",
    "quantifier_preservation",
    "modifier_preservation",
    "attribution_preservation",
    "proposition_preservation",
    "relation_preservation",
    "entity_preservation",
    "contradiction_screen",
    "pragmatic_preservation",
    "discourse_preservation",
    "contextual_consistency",
)


def _unit_checks(
    a: UnitRepresentation, b: UnitRepresentation, context: Context
) -> list[CheckResult]:
    return [
        negation_preservation(a, b),
        modality_preservation(a, b),
        claim_strength_preservation(a, b),
        quantifier_preservation(a, b),
        modifier_preservation(a, b),
        attribution_preservation(a, b, context),
        proposition_preservation(a, b),
        relation_preservation(a, b),
        entity_preservation(a, b),
        contradiction_screen(a, b),
        pragmatic_preservation(a, b),
        discourse_preservation(a, b),
        contextual_consistency(a, b, context),
    ]


def _merge(per_unit: Sequence[Sequence[CheckResult]]) -> list[CheckResult]:
    """Merge aligned units: each check keeps the most severe status among the units."""
    merged: list[CheckResult] = []
    for index, name in enumerate(_UNIT_CHECKS):
        results = [unit[index] for unit in per_unit]
        worst = max(results, key=lambda r: CHECK_SEVERITY[r.status])
        if len(results) == 1:
            merged.append(worst)
        else:
            position = results.index(worst) + 1
            suffix = (
                f" (unit {position} of {len(results)})"
                if worst.status is not CheckStatus.PASSED
                else ""
            )
            merged.append(
                CheckResult(name, worst.status, worst.explanation + suffix, worst.details)
            )
    return merged


def aggregate(checks: Sequence[CheckResult]) -> tuple[OverallStatus, str]:
    """Combine check statuses into one overall status by a fixed precedence.

    The result is a status, never a score. Checks in :data:`MODEL_CHECKS` do not influence it
    unless a similarity model was supplied and reported a low value.
    """
    core = [c for c in checks if c.name != "linguistic_fluency"]

    def names(status: CheckStatus) -> list[str]:
        return [c.name for c in core if c.status is status]

    failed = names(CheckStatus.FAILED)
    if failed:
        return (
            OverallStatus.MEANING_SHIFT_DETECTED,
            f"Failed checks: {', '.join(failed)}. At least one aspect of meaning differs.",
        )
    insufficient = names(CheckStatus.INSUFFICIENT_CONTEXT)
    if insufficient:
        return (
            OverallStatus.INSUFFICIENT_CONTEXT,
            f"Not enough context to decide: {', '.join(insufficient)}.",
        )
    review = names(CheckStatus.REQUIRES_REVIEW)
    if review:
        return (
            OverallStatus.REQUIRES_HUMAN_REVIEW,
            f"A human reader should review: {', '.join(review)}.",
        )
    blocking_model = [
        c.name
        for c in core
        if c.status is CheckStatus.REQUIRES_MODEL and c.name not in MODEL_CHECKS
    ]
    if blocking_model:
        return (
            OverallStatus.REQUIRES_MODEL,
            f"A model is required to decide: {', '.join(blocking_model)}.",
        )
    caution = names(CheckStatus.CAUTION)
    if caution:
        return (
            OverallStatus.POSSIBLE_SHIFT,
            f"No failure, but a possible shift was flagged by: {', '.join(caution)}.",
        )
    return (
        OverallStatus.PRESERVED,
        "No rule-based check found a difference. This is the absence of detected change, "
        "not a proof of equivalence.",
    )


# ---------------------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------------------


def _model_checks(
    source: str,
    candidate: str,
    similarity_model: SimilarityModel | None,
    fluency_model: FluencyModel | None,
) -> list[CheckResult]:
    if similarity_model is None:
        sim = CheckResult(
            "semantic_similarity",
            CheckStatus.REQUIRES_MODEL,
            "No similarity model was supplied. Surface overlap is not used as a "
            "substitute, because lexical overlap is not meaning.",
        )
    else:
        score = validated_score(
            similarity_model.similarity(source, candidate), name="SimilarityModel.similarity"
        )
        if score >= SIMILARITY_THRESHOLD:
            sim = CheckResult(
                "semantic_similarity",
                CheckStatus.PASSED,
                f"The supplied model reports similarity {score:.2f}, at or above "
                f"{SIMILARITY_THRESHOLD}. Similarity is evidence, not entailment.",
                {"score": score, "threshold": SIMILARITY_THRESHOLD},
            )
        else:
            sim = CheckResult(
                "semantic_similarity",
                CheckStatus.REQUIRES_REVIEW,
                f"The supplied model reports similarity {score:.2f}, below {SIMILARITY_THRESHOLD}.",
                {"score": score, "threshold": SIMILARITY_THRESHOLD},
            )
    if fluency_model is None:
        flu = CheckResult(
            "linguistic_fluency",
            CheckStatus.REQUIRES_MODEL,
            "No fluency model was supplied. Fluency is reported separately and "
            "does not affect the meaning-preservation status.",
        )
    else:
        score = validated_score(fluency_model.fluency(candidate), name="FluencyModel.fluency")
        status = CheckStatus.PASSED if score >= FLUENCY_THRESHOLD else CheckStatus.REQUIRES_REVIEW
        flu = CheckResult(
            "linguistic_fluency",
            status,
            f"The supplied model reports fluency {score:.2f}. Fluency is not meaning preservation.",
            {"score": score, "threshold": FLUENCY_THRESHOLD},
        )
    return [sim, flu]


def verify_representations(
    source: TextRepresentation,
    candidate: TextRepresentation,
    *,
    similarity_model: SimilarityModel | None = None,
    fluency_model: FluencyModel | None = None,
) -> VerificationResult:
    """Verify two already-analysed texts."""
    context = Context(source.context.sentences + candidate.context.sentences)
    checks: list[CheckResult] = []
    if len(source.units) != len(candidate.units):
        checks.append(
            CheckResult(
                "unit_alignment",
                CheckStatus.REQUIRES_REVIEW,
                f"The source has {len(source.units)} clause(s) and the candidate has "
                f"{len(candidate.units)}. Clause alignment is not implemented, so the texts "
                "cannot be compared clause by clause.",
                {"source_units": len(source.units), "candidate_units": len(candidate.units)},
            )
        )
    else:
        per_unit = [
            _unit_checks(a, b, context) for a, b in zip(source.units, candidate.units, strict=True)
        ]
        checks.extend(_merge(per_unit))
    checks.extend(_model_checks(source.text, candidate.text, similarity_model, fluency_model))

    # A supplied similarity model that reports a low value must be able to block `preserved`.
    overall, explanation = aggregate(
        [
            c
            for c in checks
            if c.name != "semantic_similarity" or c.status is CheckStatus.REQUIRES_REVIEW
        ]
    )
    unverified = tuple(
        c.name for c in checks if c.name in MODEL_CHECKS and c.status is CheckStatus.REQUIRES_MODEL
    )
    return VerificationResult(
        source.text, candidate.text, tuple(checks), overall, explanation, unverified
    )


def verify(
    source: str,
    candidate: str,
    *,
    context: Sequence[str] | None = None,
    similarity_model: SimilarityModel | None = None,
    fluency_model: FluencyModel | None = None,
) -> VerificationResult:
    """Compare ``candidate`` against ``source`` with the rule-based checks.

    Parameters
    ----------
    source, candidate:
        The original text and the text claimed to preserve its meaning.
    context:
        Optional preceding sentences. Used only to decide whether context-dependent
        differences can be reviewed.
    similarity_model, fluency_model:
        Optional user-supplied objects that satisfy the protocols in
        :mod:`semantica.integrations.model_interface`.
    """
    ctx = Context.from_texts(context)
    return verify_representations(
        analyze(source, ctx),
        analyze(candidate, ctx),
        similarity_model=similarity_model,
        fluency_model=fluency_model,
    )
