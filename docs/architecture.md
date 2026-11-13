# Architecture

```
src/semantica/
├── core/            document.py  sentence.py  context.py  status.py
├── linguistics/     lexicon.py  lexical.py  syntax.py
├── epistemics/      modality.py  certainty.py  attribution.py
├── pragmatics/      intent.py  discourse.py
├── semantics/       proposition.py  relations.py  representation.py
├── paraphrase/      transformation.py  generator.py        (test-data generation only)
├── verification/    entailment.py  contradiction.py  preservation.py  result.py
├── evaluation/      semantic_metrics.py  fidelity.py  report.py  benchmark.py
├── integrations/    model_interface.py
├── cli.py  errors.py
```

## Layers and dependencies

Dependencies point downward only.

| Package | Responsibility | Depends on |
| --- | --- | --- |
| `core` | Text objects, normalisation, status vocabularies | `linguistics.lexicon` (abbreviations only) |
| `linguistics` | Lexical resources, synonym and antonym lookup, shallow clause parser | `core.sentence` is **not** imported here |
| `epistemics` | Modality, certainty, attribution | `linguistics` |
| `pragmatics` | Speech act, polarity, discourse markers | `linguistics` |
| `semantics` | Propositions, relations, combined representation | all analysers above |
| `verification` | Checks and aggregation | `semantics`, `integrations` |
| `evaluation` | Metrics, dimension summary, reports, benchmark | `verification` |
| `paraphrase` | Candidate generation for tests | `linguistics` only |
| `integrations` | Model protocols | none |

## Separation of generation and verification

`verification` does not import `paraphrase`, and a test asserts it by inspecting
`sys.modules` after importing the verifier in a fresh interpreter state. The generator
nevertheless shares the lexicon with the verifier. That shared dependency is a deliberate
trade-off for a baseline with no external resources, and it means that agreement between the
two is circular evidence (see [evaluation.md](evaluation.md)).

## Data flow

`analyze(text)` → `TextRepresentation` (a tuple of `UnitRepresentation`) → pairwise
`CheckResult`s → `aggregate` → `VerificationResult` → `MeaningChangeReport`
(JSON, text, dimension summary, surface metrics).

## Extension points

* **Models.** Any object with `similarity(source, candidate) -> float` or
  `fluency(text) -> float` satisfies the protocols in `integrations/model_interface.py`.
  Scores are validated to be finite and within [0, 1].
* **Lexicon.** Add entries to `linguistics/lexicon.py`; the tests check that synonym classes
  are disjoint and that no antonym pair lies inside a single synonym class.
* **Checks.** A check is a function `(UnitRepresentation, UnitRepresentation) -> CheckResult`
  registered in `verification/preservation.py`.

## Error handling

Invalid input raises `InputError`; invalid model scores raise `ConfigurationError`; report
write failures raise `ReportingError`. All derive from `SemanticaError`, and the command-line
interface turns them into a non-zero exit code and a message on standard error.
