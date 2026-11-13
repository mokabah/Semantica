# Methodology

This document defines what each analyser and check does, the resources it depends on, and the
rules that turn check outcomes into an overall status. Everything described here is a
**design decision** of the project; none of it is presented as established linguistic
consensus.

## 1. Pipeline

1. **Normalisation.** Whitespace is collapsed, curly quotes are unified and common
   contractions are expanded (`can't` → `can not`).
2. **Segmentation.** Text is split into sentences with a regular-expression rule and a short
   abbreviation list. Sentences are then split further at `;`, `but` and `, and` when both
   sides contain a predicate. Each piece is a *unit*; units carry the discourse function of
   the connective that introduced them.
3. **Unit analysis.** For each unit, in order: sentence-initial connective, attribution
   frame, causal or conditional relation, main clause, then proposition, modality,
   quantifiers, negation count, speech act, evaluative polarity, numbers, names and pronouns.
4. **Alignment.** Source and candidate are compared unit by unit. If the number of units
   differs, only `unit_alignment` (`requires_review`) is reported for the structural checks,
   because clause alignment is not implemented.
5. **Checks.** Thirteen structural checks run per unit pair, and two model-dependent checks
   (`semantic_similarity`, `linguistic_fluency`) run once per text. For multi-unit texts, each
   structural check keeps its most severe status over the units.
6. **Aggregation.** See section 4.

## 2. Resources

All resources live in `semantica/linguistics/lexicon.py` and were written by hand. They were
not extracted from a corpus. In particular:

* **Verb lexicon.** 273 verb lemmas with regular or listed irregular inflection. A verb
  that is not in the lexicon is invisible to the proposition extractor.
* **Synonym classes.** 61 small sets treated as interchangeable (`influence / affect / impact`,
  `people / individuals / persons / humans`, `understand / interpret / comprehend / grasp`).
  Several are debatable; for example, *interpret* and *understand* are not identical in
  every use. Members of one class share a claim-strength tier so that substituting within a
  class never changes the strength rating.
* **Antonym pairs and exclusive sets.** Used to detect substitution of an opposite (increase /
  decrease) or of another member of a closed set (days, colours, months, directions).
* **Modal, quantifier, degree and evaluative lexicons.** Described below.

## 3. Checks

| Check | Passes when | Fails when | Otherwise |
| --- | --- | --- | --- |
| `negation_preservation` | parity of negation tokens (`not`, `no`, `never`, `none`, `nobody`, `nothing`, `neither`, `nor`, `nowhere`) matches | parity differs | – |
| `modality_preservation` | modal classes are identical | classes differ and neither side is context dependent | `requires_review` if `would`, `should`, `ought` or a bare `will` is involved |
| `claim_strength_preservation` | both predicates fall in the same tier (weak: *influence, affect, link*; moderate: *lead, drive, promote*; strong: *cause, determine, prove*) or are unrated | tiers differ | – |
| `quantifier_preservation` | quantifier and frequency classes match | both sides have quantifiers and they differ | `requires_review` if only one side has a quantifier |
| `modifier_preservation` | degree and exclusivity words match | an exclusivity word (*only, solely, just*) differs | `caution` if a degree word (*significantly, slightly*) differs |
| `attribution_preservation` | source and reporting-verb class match, or neither side is attributed | attribution added or dropped, source differs, or *tentative* is exchanged with *finding* | `requires_review` for other frame changes or a partially overlapping source |
| `proposition_preservation` | subject, action and object are equal or synonymous after voice normalisation | agent and patient are exchanged | `requires_review` when any slot differs without a recorded equivalence; `caution` on partial overlap |
| `relation_preservation` | relation type, direction, polarity and clauses agree | type, direction, `if`/`unless` or inner negation differ, or a relation is added or dropped | `requires_review` when only the content of the clauses differs |
| `entity_preservation` | numbers, capitalised names and exclusive-set members agree | a number, a name or a set member is replaced by another | `requires_review` when an item appears on one side only |
| `contradiction_screen` | no antonym substitution from the lexicon | an antonym pair is found | `requires_review` if a negation change co-occurs |
| `pragmatic_preservation` | speech act and polarity agree | speech act differs or polarity is reversed | `caution` if an evaluative word is on one side only |
| `discourse_preservation` | discourse functions match | – | `requires_review` otherwise |
| `contextual_consistency` | pronouns are identical | – | `insufficient_context` without context, `requires_review` with context |
| `semantic_similarity` | a supplied model reports at least 0.80 | – | `requires_model` without a model; `requires_review` below 0.80 |
| `linguistic_fluency` | a supplied model reports at least 0.50 | – | `requires_model` without a model; `requires_review` below 0.50 |

The 0.80 and 0.50 thresholds are arbitrary defaults of this project, not calibrated values.

### Modality and certainty

Modal classes: *possibility* (may, might, could, can), *necessity* (must, have to),
*prediction* (will, shall), *advisability* (should), *ambiguous* (would), plus phrase markers
(*is likely to*, *tends to*, *appears to*) and adverbs (*possibly*, *probably*,
*certainly*). The ordinal certainty scale is improbable < possible < probable < asserted <
certain; it is used to state the *direction* of a change (strengthened or weakened), not to
decide the status. The month name *May* is excluded using capitalisation.

### Claim strength

The predicate tiers are a hand-assigned reading of how strongly each verb commits the speaker
to a causal or evidential claim. They are a design decision and are not derived from data.

### Quantifier classes

none < few < some < many < majority < universal, plus `not_all`. Frequency adverbs share the
classes (*always* = universal, *often* = many). *Not all* and *some … not* are logically
related but are **not** recorded as equivalent, which is a documented limitation.

### Attribution

Recognised frames: *according to X, …*; *X says / claimed / reported (that) …*; *it is
reported that …*; *reportedly / allegedly*. Reporting verbs are grouped into *neutral*,
*finding*, *distancing* and *tentative*. When the frame is removed the embedded clause is
analysed, so that a dropped attribution is visible as a difference.

## 4. Aggregation

The overall status follows a fixed precedence over the check statuses. It is **not a score**.

1. any `failed` → `meaning_shift_detected`;
2. else any `insufficient_context` → `insufficient_context`;
3. else any `requires_review` → `requires_human_review`;
4. else any blocking `requires_model` → `requires_model`;
5. else any `caution` → `possible_shift`;
6. else `preserved`.

`semantic_similarity` and `linguistic_fluency` never block when absent: they are listed as
`unverified`. A supplied similarity model that reports a low value does block `preserved`
(it yields `requires_human_review`) but never overrides a failure. Fluency never affects the
overall status.

**No combined score is produced.** A weighted total would require a weighting with an
empirical basis, which this version does not have. The six evaluation dimensions are
reported side by side (see `evaluation/fidelity.py`).

## 5. Reporting uncertainty

* Every check carries an explanation, and the report lists caveats.
* `preserved` is worded as "no difference detected", never as "equivalent".
* Surface-overlap numbers are reported but never used for a status.
* Unsupported phenomena are listed in [LIMITATIONS.md](LIMITATIONS.md).

## 6. Human evaluation

Human judgement is the intended validation method for this toolkit. A practical design is a
reading-comprehension protocol in the style of Agrawal and Carpuat (2024), or paired
annotation of aspect-level labels (modality, negation, relation, attribution) by independent
annotators with an agreement statistic. No human evaluation has been carried out for v0.1.0.
