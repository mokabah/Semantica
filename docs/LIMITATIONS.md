# Limitations

Semantica v0.1.0 is a small rule-based baseline. The following are known and should be
assumed whenever a result is interpreted.

## Scope of the method

* **A status of `preserved` is not a proof of equivalence.** It means that no implemented check
  detected a difference.
* **No learned component.** Similarity and fluency are `requires_model` unless the user
  supplies a scorer, and a supplied score is treated as evidence to review.
* **Hand-written lexicon.** Coverage is small (273 verbs, 61 synonym classes, 66 antonym
  pairs). Words outside it are ignored by the proposition extractor, which falls back to
  comparing content words.
* **English only.** Nothing is multilingual.

## Unsupported linguistic phenomena

| Phenomenon | Effect |
| --- | --- |
| Coreference | Pronoun alternation yields `insufficient_context` or `requires_review`; referents are never resolved |
| Word-sense ambiguity | Not detected; polysemous words are compared by form |
| Relative clauses, long-distance dependencies | The main-verb heuristic may pick the wrong verb |
| Coordination inside a clause | Only `;`, `but` and `, and` between predicate-bearing clauses are split; `and` versus `or` inside a phrase is seen only as partial overlap |
| Multiple connectives in one sentence | Only the first relation is extracted |
| Scope of negation and quantifiers | Negation is a parity count; scope is not modelled |
| Prefix negation (*un-*, *in-*) | Not counted as negation; only antonym pairs in the lexicon are caught |
| Litotes, irony, sarcasm, implicature | Not interpreted |
| Presupposition, tense and aspect | Ignored (tense is dropped when forms are normalised) |
| Verb-particle and idiomatic expressions | Not recognised |
| Sentence-initial proper names | Not recognised as names |
| Clause alignment when counts differ | Reported as `requires_review` only |
| Indirect speech acts | *Could you …* is read as a possibility modal |
| Metaphor, figurative language | Read literally |

## Methodological caveats

* The synonym classes and claim-strength tiers are debatable judgements by one author.
* The default thresholds for supplied models (0.80, 0.50) are not calibrated.
* The benchmark labels come from a single annotator, the set was used during development,
  and no held-out evaluation exists (see [evaluation.md](evaluation.md)).
* The generator and the verifier share one lexicon.
* No human evaluation has been performed.
* The code was tested on Python 3.13 locally; 3.11 and 3.12 are declared in the continuous
  integration matrix but were not run before release.
