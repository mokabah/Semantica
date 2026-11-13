from semantica.core.sentence import tokenize
from semantica.linguistics.lexical import PhraseMatch
from semantica.semantics.proposition import compare_propositions, extract_proposition
from semantica.semantics.relations import split_relation
from semantica.semantics.representation import analyze, detect_quantifiers, split_units


def prop(text: str):
    p = extract_proposition(tokenize(text))
    assert p is not None
    return p


def test_extract_proposition_active():
    p = prop("The committee approved the proposal")
    assert p.predicate == "approve"
    assert p.subject == ("the", "committee")
    assert p.object == ("the", "proposal")


def test_compare_identical_and_synonymous():
    a = prop("social media may influence how individuals interpret information")
    b = prop("social media can affect the way people understand information")
    assert compare_propositions(a, b).all_equal


def test_compare_detects_subject_object_and_action_changes():
    base = prop("dogs chase cats")
    swapped = compare_propositions(base, prop("cats chase dogs"))
    assert swapped.swapped
    action = compare_propositions(
        prop("the company hired the engineer"), prop("the company fired the engineer")
    )
    assert action.predicate == "antonym"
    subject = compare_propositions(
        prop("teachers praised the plan"), prop("parents praised the plan")
    )
    assert subject.subject is PhraseMatch.DIFFERENT and subject.predicate == "equal"
    obj = compare_propositions(
        prop("teachers praised the plan"), prop("teachers praised the speech")
    )
    assert obj.object is PhraseMatch.DIFFERENT


def test_compare_partial_overlap():
    cmp = compare_propositions(
        prop("the policy reduced costs"), prop("the policy reduced fixed costs")
    )
    assert cmp.object is PhraseMatch.PARTIAL


def test_no_proposition_without_predicate():
    assert extract_proposition(tokenize("red cars")) is None


def test_relations_conditional_causal_and_direction():
    main, rel = split_relation("If it rains, the match will be cancelled.")
    assert rel is not None and rel.kind == "conditional"
    assert rel.antecedent == "it rains" and main == "the match will be cancelled"
    main, rel = split_relation("Prices rose because demand increased.")
    assert rel is not None and rel.kind == "causal"
    assert (rel.antecedent, rel.consequent) == ("demand increased", "Prices rose")
    main, rel = split_relation("Demand increased, therefore prices rose.")
    assert rel is not None and (rel.antecedent, rel.consequent) == (
        "Demand increased",
        "prices rose",
    )
    _, rel = split_relation("The match will be cancelled unless it rains.")
    assert rel is not None and rel.negated
    _, rel = split_relation("Prices rose since 2020.")
    assert rel is None
    _, rel = split_relation("Prices rose.")
    assert rel is None


def test_quantifiers():
    assert detect_quantifiers(tokenize("all students passed")) == ("universal",)
    assert detect_quantifiers(tokenize("not all students passed")) == ("not_all",)
    assert detect_quantifiers(tokenize("a few students passed")) == ("some",)
    assert detect_quantifiers(tokenize("students never pass")) == ("none",)
    assert detect_quantifiers(tokenize("students pass")) == ()


def test_split_units_only_when_both_sides_have_predicates():
    assert [u for _, u in split_units("The plan is cheap, but it is risky.")] == [
        "The plan is cheap",
        "it is risky.",
    ]
    assert split_units("The plan is cheap, but it is risky.")[1][0] == "contrast"
    assert len(split_units("Red, green, and blue cars.")) == 1
    assert len(split_units("It rained; the match ended.")) == 2


def test_representation_fields():
    rep = analyze("Experts say that social media may not influence 3 people in May.")
    unit = rep.units[0]
    assert unit.attribution is not None and unit.attribution.source == "experts"
    assert unit.negations == 1
    assert unit.modality.classes == {"possibility"}
    assert unit.numbers == {"3"}
    assert unit.polarity == 0
    assert rep.to_dict()["units"]
