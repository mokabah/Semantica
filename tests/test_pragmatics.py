from semantica.core.sentence import tokenize
from semantica.pragmatics.discourse import strip_leading_marker
from semantica.pragmatics.intent import classify_intent, evaluative_polarity


def act(text: str) -> str:
    return classify_intent(text, tokenize(text)).act


def test_speech_acts():
    assert act("The report is finished.") == "assertion"
    assert act("Is the report finished?") == "question"
    assert act("Close the door.") == "directive"
    assert act("Please wait.") == "directive"
    assert act("Do not enter.") == "directive"
    assert act("I will send the file.") == "commissive"
    assert act("Thank you for your help.") == "expressive"


def test_indirect_directive_is_flagged():
    intent = classify_intent("Could you close the door?", tokenize("Could you close the door?"))
    assert intent.act == "directive" and intent.indirect


def test_evaluative_polarity_and_negation_flip():
    assert evaluative_polarity(tokenize("the service was excellent"), 0) == 1
    assert evaluative_polarity(tokenize("the service was terrible"), 0) == -1
    assert evaluative_polarity(tokenize("the service was not excellent"), 1) == -1
    assert evaluative_polarity(tokenize("the service was average"), 0) == 0
    assert evaluative_polarity(tokenize("the policy improved health"), 0) == 1


def test_leading_discourse_markers():
    assert strip_leading_marker("However, the plan failed.") == ("contrast", "the plan failed.")
    assert strip_leading_marker("For example, prices rose.") == ("exemplification", "prices rose.")
    assert strip_leading_marker("The plan failed.") == (None, "The plan failed.")
    assert strip_leading_marker("Thusly it ended.")[0] is None
