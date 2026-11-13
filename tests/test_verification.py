import pytest

from semantica.core.status import CheckStatus as C
from semantica.core.status import OverallStatus as O
from semantica.errors import ConfigurationError
from semantica.verification.preservation import verify

SOURCE = "Social media may influence how individuals interpret information."


def status(source: str, candidate: str, name: str, **kw) -> C:
    return verify(source, candidate, **kw).status_of(name)


def overall(source: str, candidate: str, **kw) -> O:
    return verify(source, candidate, **kw).overall


def test_specification_example_report():
    r = verify("Social media may influence behavior.", "Social media determines behavior.")
    assert r.status_of("semantic_similarity") is C.REQUIRES_MODEL
    assert r.status_of("modality_preservation") is C.FAILED
    assert r.status_of("negation_preservation") is C.PASSED
    assert r.status_of("proposition_preservation") is C.REQUIRES_REVIEW
    assert r.overall is O.MEANING_SHIFT_DETECTED
    assert r.unverified == ("semantic_similarity", "linguistic_fluency")


def test_candidate_a_is_preserved_and_candidate_b_is_not():
    a = verify(SOURCE, "Social media can affect the way people understand information.")
    assert a.overall is O.PRESERVED
    b = verify(SOURCE, "Social media determines how people think.")
    assert b.overall is O.MEANING_SHIFT_DETECTED
    assert b.status_of("claim_strength_preservation") is C.FAILED


def test_identical_text_is_preserved():
    assert overall(SOURCE, SOURCE) is O.PRESERVED


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        ("The treatment is effective.", "The treatment is not effective."),
        ("The committee approved the plan.", "The committee did not approve the plan."),
        ("Prices rose.", "Prices never rose."),
    ],
)
def test_negation_is_detected(source, candidate):
    assert status(source, candidate, "negation_preservation") is C.FAILED
    assert overall(source, candidate) is O.MEANING_SHIFT_DETECTED


def test_double_negation_parity_is_even():
    assert (
        status("It is not true that nobody came.", "Somebody came.", "negation_preservation")
        is C.PASSED
    )


def test_prefix_negation_is_not_counted_as_negation_but_antonym_screen_catches_it():
    assert status("It is true.", "It is untrue.", "negation_preservation") is C.PASSED
    assert status("It is true.", "It is untrue.", "contradiction_screen") is C.FAILED


@pytest.mark.parametrize(
    ("source", "candidate", "expected"),
    [
        ("The drug may reduce symptoms.", "The drug reduces symptoms.", C.FAILED),
        ("The drug may reduce symptoms.", "The drug can reduce symptoms.", C.PASSED),
        ("The drug might reduce symptoms.", "The drug could reduce symptoms.", C.PASSED),
        ("Prices might rise.", "Prices must rise.", C.FAILED),
        (
            "The policy is likely to reduce emissions.",
            "The policy will reduce emissions.",
            C.FAILED,
        ),
        ("Prices rise.", "Prices will rise.", C.REQUIRES_REVIEW),
        ("It would help.", "It helps.", C.REQUIRES_REVIEW),
    ],
)
def test_modality(source, candidate, expected):
    assert status(source, candidate, "modality_preservation") is expected


def test_month_may_does_not_trigger_modality():
    assert (
        status("The vote was held in May.", "The vote was held in May.", "modality_preservation")
        is C.PASSED
    )


def test_claim_strength_direction_is_reported():
    r = verify("Smoking is linked to cancer.", "Smoking causes cancer.")
    check = r.check("claim_strength_preservation")
    assert check.status is C.FAILED and check.details["direction"] == "strengthened"
    weaker = verify("Smoking causes cancer.", "Smoking is linked to cancer.")
    assert weaker.check("claim_strength_preservation").details["direction"] == "weakened"


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        ("Some students passed the exam.", "All students passed the exam."),
        ("Students sometimes miss class.", "Students always miss class."),
        ("Most voters agreed.", "Many voters agreed."),
    ],
)
def test_quantifier_shift(source, candidate):
    assert status(source, candidate, "quantifier_preservation") is C.FAILED


def test_quantifier_added_requires_review():
    assert (
        status("Students passed.", "Many students passed.", "quantifier_preservation")
        is C.REQUIRES_REVIEW
    )


def test_modifier_checks():
    assert status("Only teachers came.", "Teachers came.", "modifier_preservation") is C.FAILED
    assert (
        status(
            "The policy significantly reduced costs.",
            "The policy reduced costs.",
            "modifier_preservation",
        )
        is C.CAUTION
    )
    assert (
        overall("The policy significantly reduced costs.", "The policy reduced costs.")
        is O.POSSIBLE_SHIFT
    )


def test_agent_patient_swap():
    r = verify("Dogs chase cats.", "Cats chase dogs.")
    assert r.status_of("proposition_preservation") is C.FAILED
    assert "exchanged" in r.check("proposition_preservation").explanation


def test_passive_and_active_are_equivalent():
    assert (
        status(
            "A student wrote the essay.",
            "The essay was written by a student.",
            "proposition_preservation",
        )
        is C.PASSED
    )


def test_action_change_requires_review_and_antonym_fails():
    assert (
        status(
            "Teachers praised the plan.", "Teachers described the plan.", "proposition_preservation"
        )
        is C.REQUIRES_REVIEW
    )
    assert (
        status(
            "The company hired the engineer.",
            "The company fired the engineer.",
            "contradiction_screen",
        )
        is C.FAILED
    )


def test_antonym_with_negation_change_requires_review():
    assert (
        status("The test was easy.", "The test was not difficult.", "contradiction_screen")
        is C.REQUIRES_REVIEW
    )


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        ("The meeting is on Monday.", "The meeting is on Friday."),
        ("Three students passed.", "Four students passed."),
        ("The car is red.", "The car is blue."),
        ("The mayor met Maria in Paris.", "The mayor met Maria in London."),
    ],
)
def test_entity_substitution(source, candidate):
    assert status(source, candidate, "entity_preservation") is C.FAILED


def test_number_formats_are_equivalent_and_missing_number_is_reviewed():
    assert (
        status(
            "The company hired 50 workers.",
            "The company hired fifty workers.",
            "entity_preservation",
        )
        is C.PASSED
    )
    assert (
        status("Three students passed.", "Some students passed.", "entity_preservation")
        is C.REQUIRES_REVIEW
    )


def test_relation_direction_and_type():
    assert (
        status(
            "Prices rose because demand increased.",
            "Demand increased because prices rose.",
            "relation_preservation",
        )
        is C.FAILED
    )
    assert (
        status(
            "If it rains, the match will be cancelled.",
            "Unless it rains, the match will be cancelled.",
            "relation_preservation",
        )
        is C.FAILED
    )
    assert (
        status(
            "If it rains, the match will be cancelled.",
            "The match will be cancelled if it rains.",
            "relation_preservation",
        )
        is C.PASSED
    )
    assert (
        status(
            "Prices rose because demand increased.",
            "Prices rose due to increased demand.",
            "relation_preservation",
        )
        is C.PASSED
    )


def test_added_relation_fails_but_causal_verb_is_reviewed():
    assert (
        status(
            "The policy reduced costs.",
            "The policy reduced costs because of automation.",
            "relation_preservation",
        )
        is C.FAILED
    )
    assert status(
        "Rain caused flooding.", "Flooding happened because rain fell.", "relation_preservation"
    ) in (C.FAILED, C.REQUIRES_REVIEW)


def test_condition_negation_inside_antecedent():
    assert (
        status(
            "If it rains, the match ends.",
            "If it does not rain, the match ends.",
            "relation_preservation",
        )
        is C.FAILED
    )


def test_attribution():
    assert (
        status(
            "Experts say that social media may influence behavior.",
            "Social media may influence behavior.",
            "attribution_preservation",
        )
        is C.FAILED
    )
    assert (
        status(
            "According to the report, emissions fell.",
            "The report states that emissions fell.",
            "attribution_preservation",
        )
        is C.PASSED
    )
    assert (
        status(
            "Officials said the plan is safe.",
            "Officials claimed the plan is safe.",
            "attribution_preservation",
        )
        is C.REQUIRES_REVIEW
    )
    assert (
        status("Experts say prices fell.", "Analysts say prices fell.", "attribution_preservation")
        is C.FAILED
    )
    assert (
        status(
            "The study suggests that exercise helps.",
            "The study proves that exercise helps.",
            "attribution_preservation",
        )
        is C.FAILED
    )


def test_context_dependence():
    source, candidate = "She said it was fine.", "The manager said the report was fine."
    assert overall(source, candidate) is O.INSUFFICIENT_CONTEXT
    with_context = verify(source, candidate, context=["The manager read the report."])
    assert with_context.overall is O.REQUIRES_HUMAN_REVIEW


def test_pragmatic_checks():
    assert (
        status("Is the report finished?", "The report is finished.", "pragmatic_preservation")
        is C.FAILED
    )
    assert (
        status("The service was excellent.", "The service was terrible.", "pragmatic_preservation")
        is C.FAILED
    )
    assert (
        status("The service was excellent.", "The service was average.", "pragmatic_preservation")
        is C.CAUTION
    )


def test_discourse_connective_dropped_requires_review():
    assert (
        status("However, the plan failed.", "The plan failed.", "discourse_preservation")
        is C.REQUIRES_REVIEW
    )
    assert (
        overall("The plan is cheap, but it is risky.", "The plan is cheap, and it is risky.")
        is O.REQUIRES_HUMAN_REVIEW
    )


def test_unit_alignment_mismatch_requires_review():
    r = verify("It rained. The match ended.", "The match ended.")
    assert r.status_of("unit_alignment") is C.REQUIRES_REVIEW
    assert r.overall is O.REQUIRES_HUMAN_REVIEW


def test_multi_sentence_pairs_are_checked_unit_by_unit():
    r = verify("The drug may help. It is safe.", "The drug may help. It is not safe.")
    assert r.status_of("negation_preservation") is C.FAILED
    assert "unit 2 of 2" in r.check("negation_preservation").explanation


def test_unknown_verbs_fall_back_to_content_word_comparison():
    r = verify("It rained.", "It rained.")
    assert r.status_of("proposition_preservation") is C.PASSED
    assert r.overall is O.PRESERVED
    assert (
        status("Rain fell heavily.", "Snow drifted lightly.", "proposition_preservation")
        is C.REQUIRES_REVIEW
    )


def test_overall_precedence():
    failing = verify("Prices might rise.", "Prices must rise, but they are cheap.")
    assert failing.overall in (O.MEANING_SHIFT_DETECTED, O.REQUIRES_HUMAN_REVIEW)
    assert overall("It rained.", "It rained.") is O.PRESERVED


def test_every_check_has_an_explanation():
    r = verify(SOURCE, "Social media determines how people think.")
    assert all(c.explanation.strip() for c in r.checks)
    assert r.explanation


class FixedSimilarity:
    def __init__(self, value: float) -> None:
        self.value = value

    def similarity(self, source: str, candidate: str) -> float:
        return self.value


class FixedFluency:
    def __init__(self, value: float) -> None:
        self.value = value

    def fluency(self, text: str) -> float:
        return self.value


def test_similarity_model_can_pass_or_block():
    high = verify(SOURCE, SOURCE, similarity_model=FixedSimilarity(0.95))
    assert high.status_of("semantic_similarity") is C.PASSED and high.unverified == (
        "linguistic_fluency",
    )
    low = verify(SOURCE, SOURCE, similarity_model=FixedSimilarity(0.2))
    assert low.status_of("semantic_similarity") is C.REQUIRES_REVIEW
    assert low.overall is O.REQUIRES_HUMAN_REVIEW


def test_similarity_never_overrides_a_detected_failure():
    r = verify(
        "The treatment is effective.",
        "The treatment is not effective.",
        similarity_model=FixedSimilarity(0.99),
    )
    assert r.overall is O.MEANING_SHIFT_DETECTED


def test_fluency_is_reported_separately_from_preservation():
    r = verify(SOURCE, SOURCE, fluency_model=FixedFluency(0.1))
    assert r.status_of("linguistic_fluency") is C.REQUIRES_REVIEW
    assert r.overall is O.PRESERVED


def test_invalid_model_scores_are_rejected():
    for bad in (1.5, -0.1, float("nan"), float("inf"), True, "0.5"):
        with pytest.raises(ConfigurationError):
            verify(SOURCE, SOURCE, similarity_model=FixedSimilarity(bad))  # type: ignore[arg-type]


def test_verifier_does_not_import_the_generator():
    import importlib
    import sys

    for name in [m for m in sys.modules if m.startswith("semantica")]:
        del sys.modules[name]
    importlib.import_module("semantica.verification.preservation")
    assert not any(m.startswith("semantica.paraphrase") for m in sys.modules)
