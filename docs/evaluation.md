# Evaluation

## Dimensions

Semantica reports six dimensions independently and **does not combine them into a single
score**. Combining them would require a weighting methodology with empirical support, which
this version does not have.

| Dimension | Fed by |
| --- | --- |
| Semantic similarity | `semantic_similarity` (optional model; `requires_model` otherwise) |
| Proposition preservation | proposition, relation, entity, contradiction, negation, quantifier and modifier checks |
| Contextual consistency | `contextual_consistency`, `unit_alignment` |
| Pragmatic preservation | `pragmatic_preservation`, `discourse_preservation` |
| Epistemic preservation | modality, claim-strength and attribution checks |
| Linguistic fluency | `linguistic_fluency` (optional model) |

A dimension carries the strictest status among its checks. Overall statuses are `preserved`,
`possible_shift`, `meaning_shift_detected`, `insufficient_context`, `requires_model` and
`requires_human_review`, and every status is accompanied by an explanation.

Two distinctions are enforced in the code: similarity is not entailment, and fluency is not
preservation. Surface overlap (Jaccard) is reported next to the verdict for context only.

## The benchmark

`benchmarks/cases.json` is the *Meaning Preservation Evaluation Benchmark*. It contains 63
hand-written cases. Each case records an identifier, the phenomenon, source, candidate, optional
context sentences, a gold overall status, optional gold per-check statuses, notes and, where
the system is known to disagree, a `known_limitation` flag with a note.

Phenomena: preserving paraphrase, negation, modality, quantifier, entity substitution,
numbers, subject/object change, action change, causal relation, conditional relation,
claim strength, attribution, context-dependent meaning, antonym, modifier, pragmatic,
discourse and known failures. The two reference candidates from the project brief are
`core-001` (Candidate A, gold `preserved`) and `core-002` (Candidate B, gold
`meaning_shift_detected`).

Run it with `semantica benchmark benchmarks/cases.json`.

### Provenance of the labels

**All gold labels were assigned by the developer.** They have not been checked by independent
annotators, so they encode one person's reading of each pair. Some are debatable (for example
`neg-005`, litotes, where the gold label is itself `requires_human_review`). The set is small
and was written to exercise each check, not to be representative of any text population.

### Results on the current version

| Quantity | Value |
| --- | --- |
| Cases | 63 |
| Exact agreement with the gold overall status | 57 / 63 |
| Missed shifts (gold `meaning_shift_detected`, predicted `preserved`) | 0 / 36 |
| False alarms (gold `preserved`, predicted `meaning_shift_detected`) | 2 / 18 |
| Annotated per-check statuses that agree | 59 / 59 |

Gold status distribution: 36 `meaning_shift_detected`, 18 `preserved`, 6
`requires_human_review`, 2 `insufficient_context`, 1 `possible_shift`.

The six disagreements are all flagged `known_limitation` and explained in the case file:

| Case | Gold | Predicted | Reason |
| --- | --- | --- | --- |
| `par-008` | preserved | requires_human_review | *hire* and *employ* are not recorded as synonyms |
| `neg-005` | requires_human_review | meaning_shift_detected | litotes (*not unlikely*) is compared mechanically |
| `qua-004` | preserved | meaning_shift_detected | *not all* and *some … not* are not recorded as equivalent |
| `prg-001` | preserved | meaning_shift_detected | *could you* is read as a possibility modal |
| `prg-004` | preserved | requires_human_review | sarcasm is not supported |
| `kfl-001` | meaning_shift_detected | possible_shift | *and* versus *or* is visible only as partial overlap |

### How to read these numbers

* **The benchmark was used during development.** After the first run, four disagreements were
  traced to real defects (a missing verb, number words not normalised, a subject that swallowed
  a phrase modal, a noun mistaken for a reporting verb) and the *system* was corrected, never the
  gold labels. The 63 cases therefore function as a development set, and the agreement figure
  is an optimistic estimate. A held-out set has not been built.
* **A zero miss rate on 36 cases is not evidence of reliability.** It shows that the checks
  fire on the phenomena they were written for. The cases were authored with the checks in
  mind.
* **Rates are given with denominators** because several categories have very few cases.

## Circularity of generated candidates

`paraphrase/generator.py` shares the lexicon with the verifier. The test that generates
candidates and verifies them (`tests/test_paraphrase.py`) confirms that the two components are
mutually consistent; it does **not** show that the verifier works on text it was not built
for. Do not cite generator-verifier agreement as validation.

## Recommended validation (not yet done)

1. Build a held-out set of source/candidate pairs drawn from text the authors did not write.
2. Have at least two independent annotators label each aspect (modality, negation, relation,
   attribution, overall) and report an agreement statistic.
3. Report precision and recall of `meaning_shift_detected` against the annotators, per
   phenomenon, with confidence intervals.
4. Complement with a reading-comprehension protocol (Agrawal & Carpuat, 2024).
