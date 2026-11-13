import pytest

from semantica.errors import ConfigurationError
from semantica.integrations import FluencyModel, SimilarityModel, validated_score


class Good:
    def similarity(self, source: str, candidate: str) -> float:
        return 0.5

    def fluency(self, text: str) -> float:
        return 0.5


def test_protocols_are_runtime_checkable():
    assert isinstance(Good(), SimilarityModel)
    assert isinstance(Good(), FluencyModel)
    assert not isinstance(object(), SimilarityModel)


def test_validated_score_accepts_bounds():
    assert validated_score(0, name="m") == 0.0
    assert validated_score(1, name="m") == 1.0


@pytest.mark.parametrize("bad", [-0.01, 1.01, float("nan"), float("inf"), None, "0.5", True])
def test_validated_score_rejects(bad):
    with pytest.raises(ConfigurationError):
        validated_score(bad, name="m")
