"""Generate test candidates with the rule-based generator and verify each of them.

The generator and the verifier share one lexicon, so agreement between them is circular
evidence. See docs/evaluation.md.
"""

from semantica import verify
from semantica.paraphrase.generator import ParaphraseGenerator

SOURCE = "Social media may influence how individuals interpret information."


def main() -> None:
    for candidate in ParaphraseGenerator().generate(SOURCE):
        result = verify(SOURCE, candidate.text)
        intent = "preserving" if candidate.intended_preserving else "changing"
        print(f"{candidate.transformation:<24} intended={intent:<10} -> {result.overall.value}")
        print(f"    {candidate.text}")


if __name__ == "__main__":
    main()
