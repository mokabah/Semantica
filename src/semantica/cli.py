"""Command-line interface: ``semantica compare | analyze | benchmark``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from semantica import __version__
from semantica.errors import SemanticaError
from semantica.evaluation.benchmark import load_cases, run_benchmark, summarize
from semantica.evaluation.report import build_report
from semantica.semantics.representation import analyze

EXIT_OK, EXIT_USAGE, EXIT_ERROR = 0, 2, 1


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="semantica", description=__doc__)
    p.add_argument("--version", action="version", version=f"semantica {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compare", help="compare a candidate against a source text")
    c.add_argument("source")
    c.add_argument("candidate")
    c.add_argument("--context", action="append", default=[], help="preceding sentence (repeatable)")
    c.add_argument("--json", action="store_true", help="print the report as JSON")
    c.add_argument("--output", help="write the JSON report to this path")
    c.add_argument(
        "--representation",
        action="store_true",
        help="include the extracted representation in the JSON report",
    )

    a = sub.add_parser("analyze", help="print the extracted representation of one text")
    a.add_argument("text")

    b = sub.add_parser("benchmark", help="run a benchmark file and print an agreement report")
    b.add_argument("path")
    b.add_argument("--json", action="store_true")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "compare":
            report = build_report(
                args.source,
                args.candidate,
                context=args.context or None,
                include_representation=args.representation,
            )
            if args.output:
                report.write_json(args.output)
            print(report.to_json() if args.json else report.render_text())
        elif args.command == "analyze":
            print(json.dumps(analyze(args.text).to_dict(), indent=2, ensure_ascii=False))
        else:
            outcomes = run_benchmark(load_cases(args.path))
            summary = summarize(outcomes)
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                _print_summary(summary)
        return EXIT_OK
    except SemanticaError as exc:
        print(f"semantica: error: {exc}", file=sys.stderr)
        return EXIT_ERROR


def _print_summary(summary: dict[str, object]) -> None:
    agree = summary["exact_agreement"]
    missed = summary["missed_shifts"]
    alarms = summary["false_alarms"]
    assert isinstance(agree, dict) and isinstance(missed, dict) and isinstance(alarms, dict)
    print(f"Cases: {summary['cases']}")
    print(f"Exact agreement with gold status: {agree['count']}/{agree['of']}")
    print(f"Missed shifts (gold shift, predicted preserved): {missed['count']}/{missed['of']}")
    print(f"False alarms (gold preserved, predicted shift):  {alarms['count']}/{alarms['of']}")
    checks = summary["gold_check_agreement"]
    assert isinstance(checks, dict)
    print(f"Annotated check statuses: {checks['annotated']}, mismatches: {checks['mismatches']}")
    print("Disagreements:")
    for item in summary["disagreements"]:  # type: ignore[attr-defined]
        flag = " (documented limitation)" if item["known_limitation"] else ""
        print(f"  {item['id']}: gold={item['gold']} predicted={item['predicted']}{flag}")


if __name__ == "__main__":
    raise SystemExit(main())
