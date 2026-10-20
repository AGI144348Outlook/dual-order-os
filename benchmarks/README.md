# Echo diagnostic batteries

These are small, transparent software diagnostics, not standardized intelligence scores. They do not establish fluency, general comprehension, learned grammar, or subjective understanding.

- `diagnostics.py`: 50 cases against the interfaces present at integration commit `768e5b7`. Baseline: 25 PASS, 18 FAIL, 7 UNSUPPORTED. Grammar cases supply POS labels; ordinary-English expectations deliberately exceed the original generalization validator's narrower contract.
- `branch_diagnostics.py`: 18 additional cases for recovered, bounded language interfaces. Initial results: 15 PASS, 3 FAIL. The three failures expose mass nouns, irregular verbs, and phonetic articles in the recovered trial-011 inflector.
- `tools/run_echo_benchmarks.py`: reruns the baseline through the same original interfaces, evaluates the new interfaces separately, verifies adopted source hashes, and writes a comparison. A successful runner means the investigation completed, not that every diagnostic passed.

```sh
python benchmarks/diagnostics.py
python benchmarks/branch_diagnostics.py
python tools/run_echo_benchmarks.py
python -m unittest discover -s tests -v
```

`reports/echo-benchmarks/baseline.json` preserves the pre-adoption run. The after-import file evaluates the same task names and original paths. New interface results are not substituted to inflate the original score. Expected outcomes were authored by the evaluator. The new source-trial examples were inspected, so separate fox/hen/sparrow cases were used as limited hold-outs; these small, related examples are not an independent scientific evaluation.

The battery covers sentence structure, inference, narrow fact retrieval, role-sensitive queries, lexical matching, raw glyph input, mathematics, verification boundaries, operation ordering, persistence and identity. Pronoun resolution, Hebrew morphology, broad paraphrase equivalence, quantifier proof systems and intervention-based causal reasoning remain unsupported. Full external benchmark suites were not downloaded or run.

Synthetic performance smoke tests measure 10 and 100 sequential vocabulary-card insertions with Python allocation tracing. They expose the cost of rebuilding the index per insertion; they do not establish Android performance, total process RAM, or production throughput. No performance threshold has been approved.
