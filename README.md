# Semantica

**Semantic Understanding & Meaning-Preserving Paraphrase Toolkit**

[![CI](https://github.com/meworo/Semantica/actions/workflows/ci.yml/badge.svg)](https://github.com/meworo/Semantica/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

Semantica is an open-source Python research toolkit for asking one question about a
paraphrase: *did the meaning survive?* It analyses a source text along semantic, contextual,
pragmatic, epistemic and linguistic layers, compares a candidate against it, and reports, check
by check, what was preserved, what changed and what could not be verified.

The guiding principle is **meaning first, linguistic transformation second**.

```text
Source:    Social media may influence behavior.
Candidate: Social media determines behavior.

  modality_preservation        failed
  claim_strength_preservation  failed
  negation_preservation        passed
  proposition_preservation     requires_review
  semantic_similarity          requires_model

Overall: meaning_shift_detected
```

## Why

A grammatical rewrite is not necessarily a faithful one. *May influence* and *determines*
differ in certainty and in the strength of the claim, yet the two sentences share most of
their words. Semantica makes such differences visible, keeps generation and verification
separate, and states plainly when a case needs a model or a human reader.

## Install

```bash
git clone https://github.com/meworo/Semantica.git
cd Semantica
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

The runtime has **no third-party dependencies** and needs no network, no paid service and no
model. Python 3.11 or later is required.

## Quick start

```python
from semantica import build_report

source = "Social media may influence how individuals interpret information."

a = build_report(source, "Social media can affect the way people understand information.")
b = build_report(source, "Social media determines how people think.")

print(a.result.overall.value)  # preserved
print(b.result.overall.value)  # meaning_shift_detected
print(b.result.status_of("modality_preservation").value)  # failed
print(b.result.status_of("claim_strength_preservation").value)  # failed
print(b.to_json()[:60])
```

`preserved` means that no implemented check found a difference. It is **not** a claim of
equivalence.

### Command line

```bash
semantica compare "It may rain." "It rains."
semantica compare "She said it was fine." "The manager said the report was fine." \
    --context "The manager read the report." --json
semantica analyze "Experts say that prices may fall."
semantica benchmark benchmarks/cases.json
```

### Using your own model

Similarity and fluency need a model, and Semantica ships none. Any object with a
`similarity(source, candidate) -> float` or `fluency(text) -> float` method works; scores
must lie in [0, 1]. See `examples/custom_model.py`.

## What is checked

| Layer | Checks |
| --- | --- |
| Semantic | proposition (agent, action, patient), relation direction, entity and number substitution, antonym screen, quantifiers, negation |
| Contextual | pronoun alternation, with or without supplied context |
| Pragmatic | speech act, evaluative polarity, discourse connectives |
| Epistemic | modality, claim strength of the predicate, attribution |
| Linguistic | lexical resources, shallow clause structure; fluency through an optional model |

Each check returns `passed`, `failed`, `caution`, `requires_model`, `requires_review` or
`insufficient_context`, with an explanation. The overall status is one of `preserved`,
`possible_shift`, `meaning_shift_detected`, `insufficient_context`, `requires_model` and
`requires_human_review`. **No combined score is computed.** Details are in
[docs/methodology.md](docs/methodology.md).

## Benchmark

`benchmarks/cases.json` holds 63 hand-written cases covering negation, modality, quantifiers,
entity substitution, subject and object changes, causal relations, attribution and
context-dependent meaning. On the current version the system agrees with the developer's gold
overall status on 57 of 63 cases, misses none of the 36 gold shifts and raises 2 false alarms
on 18 gold-preserved cases. These figures need careful reading: the labels come from a single
annotator, the set was used while developing the checks, and the six disagreements are
documented limitations. See [docs/evaluation.md](docs/evaluation.md) before citing any number.

## Limitations

Semantica v0.1.0 is a small, rule-based baseline with a hand-written lexicon. It does not
resolve coreference, disambiguate word senses, parse long-distance dependencies or interpret
irony, and it is English only. See [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Repository layout

```text
src/semantica/    core, linguistics, epistemics, pragmatics, semantics,
                  paraphrase, verification, evaluation, integrations, cli
tests/            unit, integration, benchmark, documentation and example tests
benchmarks/       cases.json (hand-labelled)
examples/         runnable scripts
docs/             specification, methodology, architecture, evaluation, references,
                  limitations, roadmap, QA report
```

## Development

```bash
ruff check . && ruff format --check .
mypy
pytest
```

## Roadmap

v0.1 basic semantic preservation evaluation (this release), then advanced propositions,
contextual meaning, pragmatics and discourse, epistemic fidelity, advanced verification,
controlled generation, multilingual analysis, a human evaluation framework and a stable v1.0.
See [docs/ROADMAP.md](docs/ROADMAP.md).

## Research references

The design draws on published work on paraphrase theory and evaluation. The full APA 7
bibliography, verified against the ACL Anthology, is in
[docs/research_references.md](docs/research_references.md). None of those papers' methods is
implemented in v0.1.0.

## Citation

See [CITATION.cff](CITATION.cff).

## License

MIT. See [LICENSE](LICENSE).
