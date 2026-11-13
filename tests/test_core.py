import pytest

from semantica.core import Context, Document, normalize, split_sentences, tokenize
from semantica.errors import InputError


def test_normalize_expands_contractions_and_whitespace():
    assert normalize("It  isn't   true.") == "It is not true."
    assert normalize("They won't go.") == "They will not go."
    assert normalize("He can't stay and she cannot either.") == (
        "He can not stay and she can not either."
    )


def test_tokenize_keeps_numbers_and_hyphens():
    assert tokenize("A well-known 3.5% rise") == ("a", "well-known", "3.5", "%", "rise")


def test_split_sentences_basic_and_abbreviation():
    assert split_sentences("It rained. The match ended.") == ["It rained.", "The match ended."]
    assert split_sentences("Dr. Smith arrived. He sat.") == ["Dr. Smith arrived.", "He sat."]


def test_split_sentences_question_and_exclamation():
    assert split_sentences("Is it true? Yes! Fine.") == ["Is it true?", "Yes!", "Fine."]


def test_document_rejects_bad_input():
    with pytest.raises(InputError):
        Document.from_text("   ")
    with pytest.raises(InputError):
        Document.from_text(123)  # type: ignore[arg-type]
    with pytest.raises(InputError):
        Document.from_text("a" * 50, max_chars=10)


def test_document_sentences_have_tokens():
    doc = Document.from_text("Social media may help. It can't hurt.")
    assert len(doc) == 2
    assert doc.sentences[1].tokens == ("it", "can", "not", "hurt")
    assert doc.sentences[0].raw_tokens[0] == "Social"


def test_context_from_texts():
    ctx = Context.from_texts(["The manager read the report. It was long."])
    assert len(ctx.sentences) == 2
    assert Context.from_texts(None).is_empty
    with pytest.raises(InputError):
        Context.from_texts([1])  # type: ignore[list-item]
