import pytest

from semantica.core.status import OverallStatus as O
from semantica.errors import InputError
from semantica.paraphrase.generator import ParaphraseGenerator
from semantica.paraphrase.transformation import (
    change_number,
    insert_negation,
    remove_modality,
    shift_quantifier,
    strengthen_modality,
    strengthen_predicate,
    substitute_exclusive,
    substitute_synonyms,
    swap_antonym,
    swap_modal,
    swap_roles,
)
from semantica.verification.preservation import verify

SOURCE = "Social media may influence how individuals interpret information."


def test_synonym_substitution_keeps_inflection():
    assert substitute_synonyms("The company increased prices.") == "The business boosted prices."
    assert substitute_synonyms("Experts criticize it.") is not None
    assert substitute_synonyms("Red cars.") is None


def test_noun_use_of_verb_form_is_not_inflected():
    out = substitute_synonyms("The increase was large.")
    assert out is not None and "increased" not in out


def test_modal_interchange_skips_month_may():
    assert swap_modal("It may rain.") == "It can rain."
    assert swap_modal("In May it rains.") is None


def test_negation_insertion_variants():
    assert insert_negation("It may rain.") == "It may not rain."
    assert insert_negation("The committee approved the plan.") == (
        "The committee did not approve the plan."
    )
    assert insert_negation("It is not true.") is None


def test_modality_changes():
    assert strengthen_modality("It may rain.") == "It must rain."
    assert remove_modality("Social media may influence behavior.") == (
        "Social media influences behavior."
    )
    assert remove_modality("Students may fail.") == "Students fail."


def test_predicate_quantifier_and_antonym_changes():
    assert strengthen_predicate("Media may influence behavior.") == (
        "Media may determine behavior."
    )
    assert shift_quantifier("Some students passed.") == "All students passed."
    assert swap_antonym("The company increased prices.") == "The company decreased prices."
    assert swap_antonym("The test was easy.") == "The test was difficult."


def test_role_swap_and_number_and_exclusive():
    assert swap_roles("Dogs chase cats.") == "Cats chase dogs."
    assert swap_roles("Dogs chase cats in the park.") is None
    assert change_number("Three students passed.") == "Four students passed."
    assert change_number("There are 5 students.") == "There are 15 students."
    assert substitute_exclusive("The meeting is on Monday.") == "The meeting is on Friday."


def test_generator_outputs_are_distinct_and_labelled():
    candidates = ParaphraseGenerator().generate(SOURCE)
    texts = [c.text for c in candidates]
    assert len(texts) == len(set(texts)) and SOURCE not in texts
    assert {c.intended_preserving for c in candidates} == {True, False}
    assert all(c.to_dict()["transformation"] for c in candidates)


def test_generator_validates_input():
    with pytest.raises(InputError):
        ParaphraseGenerator(["no_such_transformation"])
    with pytest.raises(InputError):
        ParaphraseGenerator().generate("   ")


def test_verifier_accepts_generated_preserving_candidates():
    gen = ParaphraseGenerator()
    for source in (SOURCE, "The company will increase prices.", "Researchers examine the data."):
        for candidate in gen.preserving(source):
            assert verify(source, candidate.text).overall is O.PRESERVED, candidate


def test_verifier_flags_generated_changing_candidates():
    gen = ParaphraseGenerator()
    sources = (
        SOURCE,
        "The company will increase prices.",
        "Many students passed on Monday.",
        "Dogs chase cats.",
    )
    missed = []
    for source in sources:
        for candidate in gen.changing(source):
            if verify(source, candidate.text).overall is O.PRESERVED:
                missed.append((source, candidate))
    assert not missed
