# Semantica: project specification

*Version 0.1.0. Statements are labelled **[finding]** when they restate what published work
reports, and **[design]** when they are decisions of this project.*

## 1. Executive project specification

**Name.** Semantica: Semantic Understanding & Meaning-Preserving Paraphrase Toolkit.
**Type.** Open-source Python research toolkit. **License.** MIT. **Release.** v0.1.0.

**Purpose.** To investigate whether a transformed sentence preserves the semantic content,
contextual information, communicative intent and epistemic character of its source. The
guiding principle is *meaning first, linguistic transformation second*: the information that
must survive a rewrite is analysed before any judgement about the rewrite is made.

**Scope of v0.1.0.** A rule-based, dependency-free baseline that can

1. accept a source and a candidate text;
2. detect negation, modality, quantifiers, attribution and degree or exclusivity markers;
3. extract a shallow (agent, predicate, patient) proposition and compare subject, action
   and object;
4. compare causal, conditional and concessive relations including direction;
5. flag number, name and exclusive-set substitutions;
6. compare speech act and evaluative polarity;
7. report each check with a status and an explanation, aggregate them into one status
   without a score, and export the result as JSON;
8. run a hand-labelled benchmark and report agreement with the labels.

**Not in scope.** Coreference resolution, word-sense disambiguation, full parsing, learned
semantic similarity, entailment classification, multilingual analysis and paraphrase quality
control. Optional model interfaces are provided so a user can attach their own scorer; no
model is bundled and none is required.

**Acceptance criteria.** Every check returns a status and an explanation; the specification's
example report is reproduced; the test suite, static analysis and the wheel install pass;
known failure cases are documented in `docs/LIMITATIONS.md`; no result is reported without its
denominator.

## 2. Research motivation

A sentence can change its grammar without changing its meaning. Conversely, a candidate that
looks like a paraphrase can change the intention, the causal relation, the degree of certainty
or the scope of the claim of the source. The reference example is:

> Source: *Social media may influence how individuals interpret information.*
> Candidate A: *Social media can affect the way people understand information.*
> Candidate B: *Social media determines how people think.*

Moving from *may influence* to *determines* raises both the certainty and the strength of the
claim. A procedure that relies only on word overlap or sentence structure can fail to notice
such a change. Semantica therefore evaluates paraphrases along several independent
dimensions and keeps the generator of paraphrases separate from the component that judges
them.

**Primary research question.** How can computational systems analyse and preserve semantic,
contextual, pragmatic and epistemic information during paraphrase transformation?

Sub-questions (and where v0.1.0 addresses them):

| # | Question | v0.1.0 coverage |
| --- | --- | --- |
| 1 | How can sentence meaning be represented computationally? | Shallow propositions and a layered representation |
| 2 | How can semantic relations be identified and compared? | Connective-marked relations with direction |
| 3 | How does context influence interpretation? | Only pronoun alternation; coreference is unsupported |
| 4 | How can communicative intent be preserved? | Speech-act class and evaluative polarity |
| 5 | How can modality, uncertainty, negation and attribution be detected? | Lexicon-based detectors |
| 6 | How can meaning shifts be identified during paraphrase? | Per-aspect checks and a benchmark |
| 7 | How can quality be evaluated on independent dimensions? | Six reported dimensions, no combined score |

## 3. Literature review

The review is deliberately short and restricted to six sources that were checked against their
ACL Anthology records. Full references are in [research_references.md](research_references.md).

* **[finding]** Bhagat and Hovy (2013) contrast the common definition of a paraphrase (the
  same meaning in different wording) with the broader approximate equivalence accepted in
  linguistics, and catalogue 25 operations that generate quasi-paraphrases.
* **[finding]** Bandel et al. (2022) propose a quality-guided controlled generation model and
  report meaning-preserving paraphrases with higher diversity than an uncontrolled baseline.
* **[finding]** Shen et al. (2022) report that reference-free metrics outperform
  reference-based ones for paraphrase generation and that commonly used metrics align poorly
  with human annotation; they propose ParaScore.
* **[finding]** Agrawal and Carpuat (2024) evaluate meaning preservation in text simplification
  with reading-comprehension questions, and report that the best supervised system among nine
  still leaves at least 14% of the questions unanswerable from the simplified text.
* **[finding]** Sousa and Lopes Cardoso (2025) propose PAM, an AMR-based metric reported to be
  robust to syntactic and lexical variation and to correlate better with human semantic
  scores than other AMR-based metrics on STS datasets.
* **[finding]** Elgaar and Amiri (2025) present a framework that controls 40 linguistic
  attributes and report lower attribute error than existing models.

Other relevant areas named in the project brief (natural language inference, textual
entailment, negation detection, evidentiality, discourse context) were not reviewed in this
version; no claim about them is made.

## 4. Research gaps addressed by this project

These are the *scope choices* of Semantica. They are not a claim that no other work addresses
them.

1. **Aspect-level diagnosis.** A transparent report of *which* aspect of meaning appears to
   have shifted (modality, claim strength, negation, relation direction, attribution), rather
   than only an overall number. **[design]**
2. **Explicit uncertainty.** Statuses such as `requires_model`, `insufficient_context` and
   `requires_human_review` make unverifiable cases visible instead of forcing a verdict.
   **[design]**
3. **Structural separation of generator and verifier.** The verification package does not
   import the generation package, and the limits of that separation are documented.
   **[design]**
4. **A reproducible baseline without learned components.** A deterministic, inspectable
   baseline with documented failure cases that later model-based components can be compared
   against. **[design]**
5. **Documented unsupported phenomena.** Each limitation is listed rather than hidden.
   **[design]**

## 5. Theoretical framework

**[design]** The framework has five layers. It is a methodological construction of this
project and not a claim that these five layers form a standard in linguistics. Each layer has
an operational definition and a test.

| Layer | Operational definition in v0.1.0 | Tested by |
| --- | --- | --- |
| Semantic | Agent, predicate and patient of the main clause; relations marked by connectives; numbers, names and exclusive-set members | `proposition_preservation`, `relation_preservation`, `entity_preservation`, `contradiction_screen`, `quantifier_preservation` |
| Contextual | Pronoun alternation between source and candidate, with or without supplied context | `contextual_consistency` |
| Pragmatic | Speech-act class, evaluative polarity, discourse function of connectives | `pragmatic_preservation`, `discourse_preservation` |
| Epistemic | Modal class, certainty level, claim strength of the predicate, attribution frame | `modality_preservation`, `claim_strength_preservation`, `attribution_preservation` |
| Linguistic | Lexical resources and shallow clause structure; fluency only via an optional model | `linguistic_fluency` (model required) |

Three distinctions are built into the framework:

* **Similarity is not entailment.** `semantic_similarity` is evidence supplied by a model; it
  never decides a status on its own and never overrides a detected failure.
* **Fluency is not preservation.** `linguistic_fluency` is reported separately and does not
  influence the meaning-preservation status.
* **Equivalence is approximate.** The strongest positive outcome is `preserved`, which means
  that no difference was detected by the available checks.

## 6. Conceptual architecture

```
 source ──┐                                       ┌─ per-check CheckResult (status + why)
          ├─ analysis ─ layered representation ──┤
candidate ┘   (semantic, contextual, pragmatic,   └─ aggregate status (no score)
               epistemic, linguistic)                         │
                                                              ▼
 generator (separate) ──► candidates              report: JSON / text / dimensions
```

Generation and verification are connected only through plain text. The verifier receives a
source and a candidate and has no knowledge of how the candidate was produced.

## 7. Software architecture

See [architecture.md](architecture.md) for the module-by-module description. The packages
are `core`, `semantics`, `pragmatics`, `epistemics`, `linguistics`, `paraphrase`,
`verification`, `evaluation` and `integrations`. The runtime has no third-party dependencies.
