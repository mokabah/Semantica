# Contributing

Contributions are welcome: bug reports, documentation, tests, benchmark cases and new
analysers.

## Development setup

```bash
git clone https://github.com/meworo/Semantica.git
cd Semantica
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks that must pass

```bash
ruff check .
ruff format --check .
mypy
pytest
```

## Guidelines

* Keep changes focused and add tests. Expected values should be derived by hand from the
  linguistic phenomenon, not copied from the output of the code under test.
* **Benchmark cases.** Give the phenomenon, source, candidate, a gold status and a note
  explaining the label. Never change a gold label to make the system agree; if the system is
  wrong, fix the system or mark the case `known_limitation` with an explanation.
* **Lexicon changes.** Entries are hand-written. State why a synonym or antonym pair is
  justified. Members of one synonym class must share a claim-strength tier.
* **References.** Add only sources you have read and checked, with the full author list,
  venue and DOI. Do not add results that have not been verified.
* Keep generation and verification separate: `verification` must not import `paraphrase`.
* Do not describe a rule-based check as understanding, and do not report a result without its
  denominator and its caveats.
* Keep runtime dependencies to a minimum; justify any addition in the pull request.
* Update `CHANGELOG.md` and the documentation for user-visible changes.

## Pull requests

Describe the motivation, summarise the change and state which checks were run.
Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
