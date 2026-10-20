# Progression 008 — Diagnostic checkpoint and branch-derived language components

Recorded 2026-10-20. Timothy requested a series of tests for sentence structuring, grammatical completeness, inference, reasoning, comprehension and other applicable capabilities, followed by inspection of Echo Green Future's other branches for useful implementations.

## The checkpoint before new components

The evaluated baseline was Dual Order OS integration commit `768e5b744224732e42f128db887287108093611f`, with unchanged Genesis source. A fixed battery of 50 small synthetic diagnostics produced **25 passes, 18 failures and seven unsupported capabilities**. These are not MMLU/GLUE or comparable standardized scores. No external model, training, or expensive corpus processing was used.

| Area | PASS | FAIL | UNSUPPORTED |
|---|---:|---:|---:|
| Sentence structure | 6 | 5 | 2 |
| Inference | 2 | 4 | 2 |
| Narrow comprehension/retrieval | 2 | 4 | 3 |
| Mathematics | 6 | 2 | 0 |
| Verification | 0 | 3 | 0 |
| Operation-order governance | 2 | 0 | 0 |
| Integrated catalog/identity behavior | 7 | 0 | 0 |

The original syntactic validator accepts caller-supplied department sequences, not unrestricted English. It accepted subject/verb agreement errors, a missing copula, an inappropriate object after an intransitive verb, and gibberish given plausible POS labels. Those are limits relative to the broader task requested, not proof that its narrower generalization contract was implemented incorrectly in every case.

The LRM accepted contradictory composition and unrelated causal/conditional sentences, and did not derive the expected transitive subtype conclusion. Retrieval returned lexical matches without subject/object-sensitive answering. Raw Hebrew glyphs and the short word `pe` were discarded by the old tokenizer. Substring matching remained too broad. Mathematical positives passed, but unary negation encountered eager evaluation with a None operand and division by zero returned a nonfinite value. Verification accepted empty tests and NaN results; the generic invariant validator remained permissive.

Unsupported cases include Hebrew morphology, coreference, broad paraphrase equivalence, formal quantifier/rule proving and causal interventions. Unavailability of those interfaces was recorded, not filled by the assistant answering on Echo's behalf.

## Branch inventory and selection

All **42 visible branch heads** were inventoried. Six share a commit with another branch, leaving **36 unique snapshots**. Trees were nontruncated. This is a tree/source inventory, not an exhaustive audit of every file or claimed experiment. The machine-readable inventory records names, commits, code paths and sizes.

The most direct language candidates were recovered from autonomous-agency and ksm-recess-wholesale. The first contains an evidence-bound articulation trial: it realizes an asserted agent/action/patient graph or abstains. The second has typed syntax, English rendering and reverse parsing, with independent audit functions. These fill a narrower, testable gap rather than pretending that all original inference is repaired.

Ten selected source files were preserved unchanged. Their provenance is pinned in the integration matrix. The adapter adds explicit role-ambiguity guards, registry-only lexical resolution independent of ambient WordNet, and open-world handling: no known path means UNKNOWN rather than false. Claims are supported relative to explicitly supplied records and subtype assumptions, not universally verified truth. Paperclip and stamp associations do not become proof edges.

The integrated read interface now exposes bounded `language` and `articulate` operations. Callers can retain explicit subtype assumptions as versioned relation cards; conclusions cite the traversed links. A rendered sentence must parse back and pass the applicable checks before appearing as accepted English. Diagnostic candidates are separated from accepted output.

Not adopted wholesale: the specialized KSM result-report composer, its WordNet-dependent sense resolver, arbitrary glyph execution, older governor implementations, network crawlers, and business/LLM routing experiments. These would either introduce unrelated dependencies, change semantics, or exceed the demonstrated contracts. No project invariant was redefined, and no conventional AI framework replaced Echo.

## New tests and persistent gaps

The local regression suite expanded from 27 to **43 passing tests**, including 16 new language-interface cases. An additional 18-case diagnostic challenge produced **15 passes and three failures**. It checked held-out vocabulary for transitive paths, preserved role reversal, contradiction withholding, missing-role abstention, grammar round trips and provenance. The recovered inflector still emitted “A person drinks a water,” “A person haves a book,” and “A hour changes a plan.” These are recorded English failures, not accepted as grammatical successes.

The original 50 cases were rerun through their original interfaces after adoption: **25 PASS, 18 FAIL, seven UNSUPPORTED**, with no changed outcomes. The new bounded interfaces are evaluated separately; their successes are not substituted into the old score. This distinction prevents capability inflation through a changed task or test route.

Synthetic performance checks cover 10 and 100 sequential vocabulary-card insertions with Python allocation tracing. The 100-card case is substantially slower because the adapter rebuilds its index after every insertion. These measurements are diagnostic observations without an approved speed/memory target and are not actual Android measurements. Batch ingestion and on-device evaluation remain priorities.

## Presentiation source recovered during the search

The algebra branch contains `discussions/recursive_inversion_presentiation_semantics.md` at commit `ad8efcea9a5a5d6aa38497360bb7cc7b58a6aef0`. Its opening section is labeled a **backfilled discussion context — 2026-09-26**. It describes Presentiation as the same canonical identity made present at another locus, distinguishes duplication, and later corrects reverse dictionary matching into symbol occurrence → registry-index connection → optional semantic presentiation (around lines 380–412).

This is an earlier dated source context than the October 6 plasticity reference found by the previous narrower search. Because it is a backfilled record, the label alone does not independently establish the date of the original conversation. The discovery corrects the scope of that earlier search; it does not establish that a `%` parser or configuration graph implements the intended §DSL§ inversion. No inversion algorithm was inferred merely from a source label.

## Evidence and next priorities

- [Baseline cases and outcomes](../../reports/echo-benchmarks/baseline.json)
- [After-import outcomes](../../reports/echo-benchmarks/after-branch-import.json)
- [New component diagnostics](../../reports/echo-benchmarks/branch-components.json)
- [Summary](../../reports/echo-benchmarks/summary.json)
- [Branch inventory](../../reports/echo-benchmarks/branch-inventory.json)
- [Diagnostic methodology](../../benchmarks/README.md)
- [Language interface and source provenance](../../components/echo-integration/LANGUAGE.md)

Next priorities are fixing the finite-verification boundary, handling irregular/mass-noun English explicitly, expanding independently evaluated inference contracts, and batching index reconstruction. Broad comprehension, a universal grammar, production permissions and finalized inversion remain unproven. Work remains isolated on the integration branch; source Genesis, the other source branches, live R2 and deployments are unchanged. A dated addendum should record the completed combined CI run and post-adoption source verification.
