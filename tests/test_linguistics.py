from semantica.linguistics import lexicon as lx
from semantica.linguistics.lexical import (
    PhraseMatch,
    are_antonyms,
    are_synonyms,
    canonical,
    compare_phrases,
    lemma,
    signature,
    singularize,
)
from semantica.linguistics.syntax import count_negations, parse_clause


def test_synonym_classes_are_disjoint():
    seen: dict[str, int] = {}
    for index, group in enumerate(lx.SYNONYM_CLASSES):
        for word in group:
            assert word not in seen, f"{word} appears in classes {seen[word]} and {index}"
            seen[word] = index


def test_no_antonym_pair_lies_inside_one_synonym_class():
    for a, b in lx.ANTONYM_PAIRS:
        assert canonical(a) != canonical(b), f"{a} and {b} are both antonyms and synonyms"


def test_verb_forms_and_lemma():
    assert lemma("influences") == "influence"
    assert lemma("criticized") == "criticize"
    assert lemma("wrote") == "write"
    assert lemma("cancelled") == "cancel"
    assert lemma("studies") == "study"
    assert lemma("people") == "people"


def test_singularize_guards():
    assert singularize("companies") == "company"
    assert singularize("boxes") == "box"
    assert singularize("news") == "news"
    assert singularize("class") == "class"
    assert singularize("media") == "media"


def test_synonyms_and_antonyms():
    assert are_synonyms("influence", "affects")
    assert are_synonyms("individuals", "people")
    assert are_synonyms("behaviors", "behavior")
    assert not are_synonyms("cause", "influence")
    assert are_antonyms("increased", "decrease")
    assert are_antonyms("increase", "reduces")
    assert are_antonyms("easy", "difficult")
    assert not are_antonyms("increase", "boost")


def test_numbers_are_canonicalised():
    assert canonical("fifty") == "50"
    assert signature(["fifty", "workers"]) == signature(["50", "workers"])


def test_phrase_comparison():
    assert (
        compare_phrases(
            ["the", "way", "people", "understand", "information"],
            ["how", "individuals", "interpret", "information"],
        )
        is PhraseMatch.EQUAL
    )
    assert compare_phrases(["red", "cars"], ["red", "fast", "cars"]) is PhraseMatch.PARTIAL
    assert compare_phrases(["red", "cars"], ["green", "boats"]) is PhraseMatch.DIFFERENT
    assert compare_phrases([], []) is PhraseMatch.EQUAL


def test_parse_active_clause():
    p = parse_clause(["social", "media", "may", "influence", "how", "people", "think"])
    assert p.subject == ("social", "media")
    assert p.predicate == "influence"
    assert p.object == ("how", "people", "think")
    assert p.voice == "active"


def test_parse_passive_with_and_without_agent():
    p = parse_clause(["the", "policy", "was", "criticized", "by", "experts"])
    assert (p.subject, p.predicate, p.object, p.voice) == (
        ("experts",),
        "criticize",
        ("the", "policy"),
        "passive",
    )
    q = parse_clause(["the", "policy", "was", "criticized"])
    assert q.subject == () and q.voice == "passive"


def test_parse_noun_verb_ambiguity_uses_determiner_rule():
    p = parse_clause(["the", "influence", "of", "media", "is", "large"])
    assert p.predicate == "be"
    assert p.subject[:2] == ("the", "influence")


def test_parse_relative_clause_does_not_capture_the_wrong_verb():
    p = parse_clause(["students", "who", "study", "hard", "pass", "the", "exam"])
    assert p.predicate == "pass"


def test_parse_phrase_modal_stops_subject():
    p = parse_clause(["the", "drug", "appears", "to", "reduce", "symptoms"])
    assert p.subject == ("the", "drug")
    assert p.predicate == "reduce"


def test_parse_without_predicate():
    p = parse_clause(["red", "cars"])
    assert p.predicate is None


def test_count_negations():
    assert count_negations(["it", "is", "not", "true"]) == 1
    assert count_negations(["nobody", "never", "came"]) == 2
    assert count_negations(["it", "is", "true"]) == 0
