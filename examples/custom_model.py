"""Plug a user-supplied similarity model into the verifier.

``ToyOverlapModel`` is a placeholder that measures word overlap. It is NOT a measure of
meaning; it only demonstrates the interface. Replace it with a model you have validated.
"""

from semantica import build_report
from semantica.evaluation.semantic_metrics import token_jaccard


class ToyOverlapModel:
    def similarity(self, source: str, candidate: str) -> float:
        return token_jaccard(source, candidate)


def main() -> None:
    report = build_report(
        "The treatment is effective.",
        "The treatment is not effective.",
        similarity_model=ToyOverlapModel(),
    )
    print(report.render_text())
    # Overlap is high, yet the negation check still reports a meaning shift.


if __name__ == "__main__":
    main()
