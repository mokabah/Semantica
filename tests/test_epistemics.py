from semantica.core.sentence import tokenize_raw
from semantica.epistemics.attribution import strip_attribution
from semantica.epistemics.certainty import Certainty, certainty_of, claim_strength, direction
from semantica.epistemics.modality import detect_modality


def classes(text: str) -> frozenset[str]:
    return detect_modality(tokenize_raw(text)).classes


def test_modal_auxiliaries():
    assert classes("Social media may influence behavior") == {"possibility"}
    assert classes("It might rain") == {"possibility"}
    assert classes("She could leave") == {"possibility"}
    assert classes("He must leave") == {"necessity"}
    assert classes("It will rain") == {"prediction"}
    assert classes("It would help") == {"ambiguous"}
    assert classes("It rains") == frozenset()


def test_phrase_and_adverb_modals():
    assert classes("It is likely to rain") == {"probability"}
    assert classes("The drug appears to work") == {"appearance"}
    assert classes("Prices tend to rise") == {"tendency"}
    assert classes("It is possible that prices rise") == {"possibility"}
    assert classes("Prices will probably rise") == {"prediction", "probability"}
    assert classes("This is certainly true") == {"certainty"}
    assert classes("This is unlikely") == {"improbability"}


def test_month_may_is_not_a_modal():
    assert classes("The vote was held in May") == frozenset()
    assert classes("May 5 was a Monday") == frozenset()
    assert classes("May influence behavior") == {"possibility"}


def test_certainty_levels():
    assert certainty_of(detect_modality(tokenize_raw("It rains"))) is Certainty.ASSERTED
    assert certainty_of(detect_modality(tokenize_raw("It may rain"))) is Certainty.POSSIBLE
    assert certainty_of(detect_modality(tokenize_raw("It is likely to rain"))) is Certainty.PROBABLE
    assert certainty_of(detect_modality(tokenize_raw("It must rain"))) is Certainty.CERTAIN
    assert certainty_of(detect_modality(tokenize_raw("It is unlikely"))) is Certainty.IMPROBABLE


def test_claim_strength_tiers():
    assert claim_strength("influence") == 1
    assert claim_strength("lead") == 2
    assert claim_strength("cause") == 3
    assert claim_strength("walk") is None
    assert claim_strength(None) is None


def test_direction():
    assert direction(1, 3) == "strengthened"
    assert direction(3, 1) == "weakened"
    assert direction(2, 2) == "same"


def test_attribution_according_to():
    attribution, body = strip_attribution("According to the report, emissions fell.")
    assert attribution is not None
    assert attribution.source == "the report"
    assert body == "emissions fell"


def test_attribution_says_that_and_bare_verbs():
    attribution, body = strip_attribution("Experts say that social media may influence behavior.")
    assert attribution is not None and attribution.source == "experts"
    assert attribution.verb_class == "neutral"
    assert body == "social media may influence behavior"
    attribution, body = strip_attribution("Officials claimed the plan is safe.")
    assert attribution is not None and attribution.verb_class == "distancing"
    assert body == "the plan is safe"


def test_attribution_requires_that_for_non_speech_verbs():
    attribution, _ = strip_attribution("Social media shows people what they like.")
    assert attribution is None
    attribution, _ = strip_attribution("The study shows that exercise helps.")
    assert attribution is not None and attribution.verb_class == "finding"


def test_attribution_passive_and_adverbial():
    attribution, body = strip_attribution("It is reported that prices fell.")
    assert attribution is not None and attribution.source == "unspecified"
    assert body == "prices fell"
    attribution, body = strip_attribution("The company reportedly lost money.")
    assert attribution is not None and attribution.verb_class == "neutral"
    assert body == "The company lost money"
    attribution, _ = strip_attribution("The company allegedly lost money.")
    assert attribution is not None and attribution.verb_class == "distancing"


def test_attribution_absent_and_noun_use_of_report():
    assert strip_attribution("Social media may influence behavior.")[0] is None
    assert strip_attribution("The report states that emissions fell.")[0].source == "the report"  # type: ignore[union-attr]
