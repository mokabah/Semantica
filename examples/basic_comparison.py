"""Compare two candidate paraphrases against one source and print the reports.

Run with ``python examples/basic_comparison.py``.
"""

from semantica import build_report

SOURCE = "Social media may influence how individuals interpret information."
CANDIDATES = {
    "A": "Social media can affect the way people understand information.",
    "B": "Social media determines how people think.",
}


def main() -> None:
    for label, candidate in CANDIDATES.items():
        report = build_report(SOURCE, candidate)
        print(f"--- Candidate {label} ---")
        print(report.render_text())
        print()


if __name__ == "__main__":
    main()
