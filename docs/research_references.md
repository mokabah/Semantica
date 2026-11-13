# Research references

All six sources were checked against their records in the ACL Anthology (title, author list,
venue, pages and DOI). The descriptions below restate what the authors report in their
abstracts; they are not an independent assessment, and none of the methods in these papers is
implemented in Semantica v0.1.0. Where a statement is a design decision of this project, it
is labelled as such.

## Bibliography (APA 7)

Agrawal, S., & Carpuat, M. (2024). Do text simplification systems preserve meaning? A human
evaluation via reading comprehension. *Transactions of the Association for Computational
Linguistics, 12*, 432–448. https://doi.org/10.1162/tacl_a_00653

Bandel, E., Aharonov, R., Shmueli-Scheuer, M., Shnayderman, I., Slonim, N., & Ein-Dor, L.
(2022). Quality controlled paraphrase generation. In *Proceedings of the 60th Annual Meeting
of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 596–609).
https://doi.org/10.18653/v1/2022.acl-long.45

Bhagat, R., & Hovy, E. (2013). Squibs: What is a paraphrase? *Computational Linguistics,
39*(3), 463–472. https://doi.org/10.1162/COLI_a_00166

Elgaar, M., & Amiri, H. (2025). Linguistically-controlled paraphrase generation. In
*Findings of the Association for Computational Linguistics: EMNLP 2025* (pp. 20842–20864).
https://doi.org/10.18653/v1/2025.findings-emnlp.1137

Shen, L., Liu, L., Jiang, H., & Shi, S. (2022). On the evaluation metrics for paraphrase
generation. In *Proceedings of the 2022 Conference on Empirical Methods in Natural Language
Processing* (pp. 3178–3190). https://doi.org/10.18653/v1/2022.emnlp-main.208

Sousa, A., & Lopes Cardoso, H. (2025). PAM: Paraphrase AMR-centric evaluation metric. In
*Findings of the Association for Computational Linguistics: ACL 2025* (pp. 17106–17121).
https://doi.org/10.18653/v1/2025.findings-acl.879

## Publication types

| Source | Type |
| --- | --- |
| Bhagat & Hovy (2013) | Journal article (squib), *Computational Linguistics* |
| Agrawal & Carpuat (2024) | Journal article, *Transactions of the ACL* |
| Bandel et al. (2022) | Conference paper, ACL main proceedings |
| Shen et al. (2022) | Conference paper, EMNLP main proceedings |
| Sousa & Lopes Cardoso (2025) | Findings paper, ACL 2025 |
| Elgaar & Amiri (2025) | Findings paper, EMNLP 2025 |

Findings papers appear in the Findings volumes of their conferences, which are distinct from
the main proceedings.

## What each source reports, and how it relates to Semantica

**Bhagat & Hovy (2013).** The authors observe that a paraphrase is commonly defined as two
expressions that convey the same meaning in different wording, whereas linguistics accepts a
broader notion of approximate equivalence, which they call quasi-paraphrase. They list 25
operations that generate quasi-paraphrases and validate them on two public paraphrase
corpora.
*Relation (design decision):* Semantica treats equivalence as approximate. For that reason its
overall statuses distinguish `preserved`, `possible_shift` and `requires_human_review`, and
it never reports "equivalent".

**Bandel et al. (2022).** The authors propose QCPG, a quality-guided controlled paraphrase
generation model that controls quality dimensions directly, and report paraphrases that keep
the meaning while achieving higher diversity than an uncontrolled baseline.
*Relation (design decision):* Semantica's roadmap places controlled generation at v0.7. In
v0.1.0 the generator only builds test candidates, and it is separated from the verifier.

**Shen et al. (2022).** The authors report that reference-free metrics outperform
reference-based ones for paraphrase evaluation, that commonly used metrics align poorly with
human annotation, and they propose ParaScore.
*Relation (design decision):* Semantica reports surface-overlap numbers separately and never
uses them to decide a status, and it states that any similarity score from a user-supplied
model is evidence to review, not a verdict.

**Agrawal & Carpuat (2024).** The authors introduce a human evaluation framework that uses
reading-comprehension questions to test whether simplified texts preserve meaning. Nine
automatic systems were evaluated, and the best supervised system still left at least 14% of
the questions unanswerable from the simplified text.
*Relation (design decision):* This motivates the human-evaluation path named in the
roadmap (v0.9) and the `requires_human_review` status.

**Sousa & Lopes Cardoso (2025).** The authors propose PAM, a paraphrase evaluation metric
built on Abstract Meaning Representation graphs. They report that it is robust to syntactic
and lexical variation and that it improves correlation with human semantic scores on STS
datasets compared with other AMR-based metrics.
*Relation (design decision):* Semantica v0.1.0 does not use AMR. Its shallow proposition
triples are a much simpler structure, and richer representations are planned for v0.2.

**Elgaar & Amiri (2025).** The authors introduce LingConv, an encoder-decoder framework that
controls 40 linguistic attributes, and report up to 34% lower attribute error than existing
models, with a quality-control mechanism adding a further 14% reduction.
*Relation (design decision):* Linguistic control is outside the scope of v0.1.0. The linguistic
layer here only supplies lexical resources and a shallow clause analysis.

## Notes on use

* The figures quoted above are the authors' own reported results. They were not reproduced
  here and should not be read as results of Semantica.
* Statements about theory in other documents (for example the five-layer framework) are
  methodological design choices of this project, not claims of an established standard.
