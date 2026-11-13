# QA report: Semantica v0.1.0

This report lists what was run, on what, and what was **not** verified.

## Environment

* Python 3.13 on Linux. Runtime dependencies: none. Dev tools: pytest 9, ruff, mypy 2.3.

## Checks performed

| Check | Result |
| --- | --- |
| `ruff check .` | clean |
| `ruff format --check .` | clean |
| `mypy` (strict, `src/`) | no issues in 39 source files |
| `pytest` with warnings treated as errors | 192 passed |
| Wheel built with `pip wheel --no-build-isolation` and installed in a clean virtual environment | installs; `py.typed` present; `semantica` console script runs |
| Full test suite run against the installed wheel (not the source tree) | 192 passed |
| Cross-process determinism (three `PYTHONHASHSEED` values) | identical JSON reports |
| Benchmark run (`semantica benchmark benchmarks/cases.json`) | 63 cases; 57 agree; 0 of 36 gold shifts missed; 2 of 18 false alarms; every disagreement carries a documented limitation |
| Documentation code blocks executed; relative links resolved | pass |
| Published benchmark figures compared with a fresh run | pass (`tests/test_docs.py`) |
| Examples executed | pass |
| Sensitivity: disabling each of seven checks lets its defect through | pass |
| Robustness: 18 odd inputs and 400 seeded random sentence pairs | no exception |
| Scrub for assistant, tool or vendor names and tracking parameters | none found |

## What the tests do and do not show

* Expected values in unit tests were derived by hand from the linguistic phenomenon.
* The sensitivity tests show that the suite fails when a check is removed, which is evidence
  that the tests exercise the checks.
* The generator-to-verifier test is **circular** (both use one lexicon) and is not validation.
* The benchmark agreement figure comes from a set used during development with
  single-annotator labels; it is not an estimate of accuracy on unseen text.

## Not verified

* **Test coverage was not measured** (no coverage tool was available in the environment).
* **Python 3.11 and 3.12** are declared in `pyproject.toml` and the CI matrix but were not run.
* **The hosted CI workflow has not run**; its YAML was not executed on GitHub.
* **No human evaluation**, no independent annotators and no held-out benchmark.
* **No performance measurement.** Inputs are capped at 20,000 characters; behaviour on larger
  inputs is untested.
* The `.github` templates were not rendered by GitHub.
