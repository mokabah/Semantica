"""Write a JSON meaning-change report to disk."""

import tempfile
from pathlib import Path

from semantica import build_report


def main() -> None:
    report = build_report(
        "Social media may influence behavior.", "Social media determines behavior."
    )
    target = Path(tempfile.gettempdir()) / "semantica_report.json"
    report.write_json(target)
    print(f"report written to {target}")
    print(report.to_json()[:400], "...")


if __name__ == "__main__":
    main()
