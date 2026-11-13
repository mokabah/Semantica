# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-13

### Added
- Text processing: normalisation, sentence segmentation, clause splitting, structured
  `Document`, `Sentence` and `Context` objects.
- Rule-based analysers: shallow propositions with voice normalisation, causal, conditional and
  concessive relations, quantifiers, negation parity, modality and certainty, claim strength,
  attribution, speech act, evaluative polarity, discourse connectives, numbers and names.
- Verification with fifteen named checks, status aggregation without a combined score,
  and per-check explanations.
- Optional `SimilarityModel` and `FluencyModel` protocols (no model is bundled).
- Rule-based candidate generator (test data only, separate from verification).
- JSON and text meaning-change reports; `semantica` command-line interface.
- Meaning Preservation Evaluation Benchmark: 63 hand-labelled cases with documented known
  limitations, and an agreement report.
- Documentation, examples and a test suite including documentation and example execution.
