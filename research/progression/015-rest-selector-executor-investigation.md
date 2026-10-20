# 015 — Rest experiment selection and execution: repository investigation

Date: 2026-10-20. Research and local verification only; no runtime integration or deployment.

Principal source links: [composition search](https://github.com/AGI144348Outlook/Echo_Green_Future/blob/8311da62ba90ce547a61b27d2c2836b8f89550a9/code_library_registry/modules/MOD-0002-bounded-composition-search/generalized/bounded_composition_search.py), [static inspection](https://github.com/AGI144348Outlook/Echo_Green_Future/blob/8311da62ba90ce547a61b27d2c2836b8f89550a9/code_library_registry/modules/MOD-0006-static-python-flow-outline/generalized/static_python_flow_outline.py), [schedule gate](https://github.com/AGI144348Outlook/Echo_Green_Future/blob/8311da62ba90ce547a61b27d2c2836b8f89550a9/code_library_registry/modules/MOD-0008/generalized/schedule_gate.py), [KSM Recess](https://github.com/AGI144348Outlook/Echo_Green_Future/blob/82810112a959dc094dcf40238419cffca6863670/echo/canvas/ks_recess.py), and [configuration lab](https://github.com/AGI144348Outlook/Echo_Green_Future/blob/43612d0b2b171f0001f2fad17ec9474d20c292c7/experiments/nve-d/configuration_lab.py).

Timothy defined Recess as Echo's Rest state: consolidate experience, hypothesize, and try algorithm-block combinations against accessible material when no external task is active. He requested a Code Library search first, then a search across the accessible repositories.

## Assessment and correction

Several useful mechanisms already exist. The earlier statement that Echo has no selection mechanism was too broad. The integrated Genesis source already includes A-101 action selection and A-113 outcome/checkpoint handling. What the latest recess experiment lacked was a connection from those mechanisms to the current glyph-block catalog, sense cards, permissions, and experiment goals. No complete, currently integrated, task-idle Rest controller was found.

The strongest practical combination is existing observation/question records + an explicit experiment-objective policy + bounded composition search + a typed executor + the existing persistent card catalog. Choosing an action, constructing a composition, executing it, and establishing its usefulness remain separate responsibilities.

## Scope and evidence discipline

Inventoried all **30 accessible repositories** under AGI144348Outlook and **98 branch trees**, including all **42 Echo_Green_Future branches**, four Dual Order branches, and both Group Canvas branches. The returned inventories were not truncated. Selected relevant source and tests were read in detail; this is not a claim that every file, archive, PDF, or historical conversation was inspected. No private R2 data was accessed. Private source documents are not reproduced in this public report.

The Code Library branch was examined first, pinned at `8311da62ba90ce547a61b27d2c2836b8f89550a9`. Other principal snapshots:

| Repository / branch | Commit inspected |
| --- | --- |
| Echo_Green_Future / autonomous-agency | `608f3346070926645b955a349acd44170ce8ba60` |
| Echo_Green_Future / ksm-recess-wholesale | `82810112a959dc094dcf40238419cffca6863670` |
| Echo_Green_Future / library-source-transcriptions | `43612d0b2b171f0001f2fad17ec9474d20c292c7` |
| Echo_Green_Future / resh-lattice-agency | `2c7616485dc670745433e8647d9467d7fc3b732b` |
| LVT / main | `122aeae062604c2128c9d3fa1a5beb3d64d0ca0a` |
| Lhea-Tema / main | `22ae6f5d307bffe56c4fcb6f9707d76c644655ff` |
| Group_Canvas / main | `36d1b1a311c55cdf1ebeec3ef7499945f56186e8` |

Implemented means executable behavior was inspected. Tested below means a fresh local execution with recorded results. Specified means a documented design, not demonstrated behavior. Proposed means a new integration possibility.

## Code Library findings

All paths in this section are relative to `Echo_Green_Future/code-library-registry`.

### 1. MOD-0002: a real composition-search engine

**Implemented and freshly tested.** `code_library_registry/modules/MOD-0002-bounded-composition-search/generalized/bounded_composition_search.py`, class `BoundedCompositionSearch`, methods `find` and `_key`, plus `replay`.

It searches caller-supplied named operations breadth-first, deduplicates states, records operation failures and rejected outcomes, and limits search depth and operation attempts. It finds a shortest admitted path within the explored space, not an optimal algorithm under every cost model.

Fresh example: supplied `double` and `increment`, start 3, target 11. It found `increment → increment → double → increment` in 26 attempted operations; replay returned 11. The solution sequence was searched rather than supplied. The target, operations, ordering, and predicate were supplied. This is composition synthesis from known primitives, not invention of arbitrary Python or self-selection of a research question.

Its seven original tests passed. Additional boundary probes showed that an operation can mutate the source object even when its returned outcome is rejected; an initial state already satisfying the goal is accepted before `admit_state` is called. The search bounds operation count, not the runtime or side effects of each callable. `replay` itself has no admission, permission, or invariant checks. Use immutable states or isolated copies and an independently gated executor. This module is not a security sandbox.

### 2. MOD-0006: observation without executing unfamiliar Python

**Implemented and freshly tested.** `code_library_registry/modules/MOD-0006-static-python-flow-outline/generalized/static_python_flow_outline.py`, `outline_source`.

Uses Python's AST to describe a selected function or method, with node and output bounds. Useful for the proposed ע portfolio: inspect the structure of an available block before trying it. It does not establish code safety, semantics, dependency completeness, runtime reachability, or correctness. Its own documentation explicitly distinguishes a structural outline from a complete executable control-flow graph. Seven tests passed.

### 3. MOD-0008: when a scheduled opportunity is due

**Implemented and freshly tested.** `code_library_registry/modules/MOD-0008/generalized/schedule_gate.py`, `parse_schedule` and `decide`; associated `CONTRACT.md`.

Supports interval, daily, weekly, timezone-aware and off rules. Nine tests passed. It deliberately performs no execution or sleeping. Its contract leaves durable state, mutual exclusion, retries, and execution to the caller. A due time is not evidence that no user task is active. Rest still needs task-idle detection, a single-owner lease, interruption, and a persistent checkpoint.

### 4. Other usable parts

| Module | Verified contribution | Fresh tests | Boundary |
| --- | --- | --- | --- |
| MOD-0001 `generalized/verified_resource_gate.py` | Staged resource creation, layout verification, storage admission and audit records | 5 Python | Process-local checks, not authentication or execution isolation |
| MOD-0003 `generalized/structured_workspace.py` | Collections, relations, index bindings, provider-optional lookup and atomic JSON saves | 5 Python | Does not choose experiments or replace existing card revision history |
| MOD-0004 `generalized/safe_relative_entry_writer.mjs` | Validated relative paths and streaming file writes | 6 JavaScript | Tests use fake handles; no Android browser storage compatibility was established |
| MOD-0005 `generalized/bounded_affinity_admission.py` | Bounded candidate admission, queue scanning and tie accounting | 7 Python | Caller-supplied numeric affinity, not Timothy's Generalized Evaluators or a truth test |
| MOD-0007 `generalized/actor_scoped_command_admission.mjs` | Pure human/agent command admission with ownership and geometry rules | 8 JavaScript | Principal labels must come from a trusted authenticated caller; decision only, not executor |

The design note `code_library_registry/design_notes/neuroplasticity-candidate-algorithms.md` is **specified/proposed** and explicitly says its alternatives are not implemented. Particularly relevant are D1 exploration/exploitation, D2 candidate lifecycle, F2 concept-token formation, F6 recursive consolidation, and G1/G2 rest and higher-order return. Those sections describe choices we can test; they cannot be counted as existing operational Rest behavior.

## Echo branches: important surprises

### A-101 and A-113 are already in preserved Genesis

**Implemented and freshly probed.** `vendor/echo-genesis/src/echo_governor_skeleton.py` in the Dual Order integration contains `AlgorithmMatrix.bandit_select` near line 968, `record_outcome` near 988, and `checkpoint_generation` near 1006. The original source blob remains `63eb982989b4f3478d649430b555c8f4ba755c27`.

A-101 selects from supplied action names using unexplored-first ordering, then UCB1. A-113 buffers current-generation outcomes and either incorporates or discards them at a checkpoint. These are executable selection and feedback mechanisms. They need a supplied action set and supplied success signal; they do not inspect the current card catalog to resolve executable glyph blocks.

A fresh fixture selected `INTRODUCE` four times while outcomes were buffered; after a successful checkpoint, it selected `ALIGN`. This matters: attempted-arm exploration and trusted performance history currently share the same anchored table. Rejecting a generation can leave an arm perpetually treated as untried. The UCB1 numeric policy is legacy behavior, not a newly adopted project invariant or an implementation of the relational evaluator proposal.

### KSM Canvas Recess connects selection to actual activities

**Implemented; historical result inspected, not rerun end to end.** On `ksm-recess-wholesale`, `echo/canvas/ks_recess.py`, class `KSRecess`, especially `run`, selects `INTRODUCE`, `ALIGN`, `CONTAIN`, or `MANIFOLD`, calls an activity, records its outcome, and checkpoints. `experiments/e12_ks_canvas_recess.py` supplies WordNet relationships, language parsing/auditing, and Canvas operation records.

Its saved `experiments/e12_recess_log.json` contains 120 activity turns: 20 INTRODUCE, 20 ALIGN, 80 CONTAIN, and no MANIFOLD. Six checkpoints include two ANCHORED and four DISCARDED. This is recorded historical output, not a fresh demonstration. It illustrates the selection trap above: repeatedly rejected CONTAIN results leave MANIFOLD unexplored. The saved text includes `An over is a division.` despite an audit label of PASS; labels should not be mistaken for independent grammatical or semantic proof.

This branch is a valuable working ancestor for visible Rest activity. Its four activities are fixed implementations, not arbitrary glyph-program synthesis. Its WordNet, language, kernel, and rendering dependencies require deliberate adaptation to the current sense-card interface.

### A-168 RecessAgent and A-173 question records

**Implemented; inspected, not freshly run.** On `autonomous-agency`, `ECHO_AutonomousAgency/src/echo_recess.py` includes `RecessAgent._select_activity`, `_activity_meet`, `_activity_compose`, and `run_session`. It chooses from seven fixed activities using weighted random selection and a recent-activity boost. MEET proposes a description from shared glyph/name features; COMPOSE selects three glyphs and describes their alleged operations. Neither builds and tests a new executable composition.

`ECHO_AutonomousAgency/src/echo_question.py`, `QuestionFormulationEngine`, turns mirror gaps, missing knowledge, pending proposals, meetings and other inputs into structured questions. This is a useful source of experiment candidates. Receiver labels such as DRIVE or WORDNET do not themselves implement external tool access. Historical צ=HUNT and ר=GOVERN labels are source context; they must not overwrite Timothy's newer paperclip and identification portfolios.

Important weaknesses: broad exceptions in `run_session` suppress activity failures; confidence/novelty values are heuristics rather than verification; `review_session` uses approval counts to increase trust. Its printed supervision messages are not sufficient evidence of enforced write permissions. Those policies should not be imported wholesale.

`ECHO_AutonomousAgency/docs/RESEARCH_HANDOFF_2026-09-25.md` already records a closely related negative result: the earlier school-day trial varied glyph identities while registry operations were null. It explicitly distinguishes glyph selection from executed algorithm and scripted sequences from autonomous concept models. That historical diagnosis agrees with our new card/block observation.

### NVE-D already has a configuration-testing scaffold

**Implemented and freshly tested as a scaffold.** On `library-source-transcriptions`, `experiments/nve-d/configuration_lab.py` provides canonical hashed configurations, parent links, tested-set serialization, a test budget, seeded random/sparse/adaptive arms, provisional letter-labeled moves, and two differently structured judge implementations. Its nine tests passed locally.

This is useful for recording distinct trials and reducing repetition. Its objective is a synthetic count of non-open relation pairs, not meaning, comprehension, or useful algorithm discovery. Its own output says `evidence_level: NONE`. The judges do not implement the full requested Governor relation. Registry manifests are shape-checked rather than independently resolved upstream, and the CLI does not automatically persist/load tested sets across Rest cycles. Letter-move semantics are explicitly proposed and include ת as terminal; they cannot replace the current stamping portfolio.

### Resh lattice runner is an inspect → choose → execute → retest ancestor

**Implemented; inspected only.** On `resh-lattice-agency`, `experiments/resh_lattice_agency_runner.py` diagnoses certain missing-module/file errors, selects bounded search-path or working-directory changes, and reruns a discovered Python entry point with subprocess timeouts. It records repeated ineffective strategies.

The transferable part is the explicit observation/action/result loop and stopping when evidence does not justify a repair. It is a narrow programmed repair policy, not general reasoning. Its disposable-workspace description is not an OS sandbox; it executes code and mutates local runtime context. It was not imported or run during this investigation.

## Other repositories

- **Group_Canvas — implemented:** `src/commands/index.js` applies known commands with authenticated-principal checks, revisions, receipts and recorded events. `src/jobs/index.js` provides Python job lifecycle and leases, but explicitly restricts claiming Python execution to the author's human session. `src/agents/index.js` requires a person to request a provider turn. These are useful execution-boundary patterns; they do not currently authorize background Echo Python execution. No paid calls were made.
- **Lhea-Tema — implemented but not runtime-tested here:** `lhea-tema-kernel.js` contains `executeISATriplet` and `runEBAInternal`: registry-backed triplet handling, context records, traversal counters and migration between storage layers. Its numeric weights and repetition-based CORE promotion do not establish correctness, and it is not a general function dispatcher for new glyph programs. It needs Cloudflare database bindings; no databases or deployed services were changed.
- **LVT — specified or minimal executable stub:** `kernel/executive_mode_switching.md` defines LEXICAL, SPATIAL and STORAGE purposes, not an operational Run/Rest scheduler. `kernel/symbolic_judgement_engine.py` is a small threshold comparison plus a canned operation result. Its name does not establish a general evaluator/executor.
- **JurisDictionary- — implemented source on the Claude connection branch:** `src/jurisdictionary/core.py` has token activate/suspend/revoke states, exclusive locks, conditional gates and `commit_turn`. These may inform typed eligibility rules. Its domain rules and template sentences are not a ready-made experimental selector, and were not tested or adopted here.
- **Dual Order — implemented current foundation:** `libraries/catalog_box.py`, `libraries/echo_workspace.py`, and `libraries/echo_sentence_cards.py` already provide persistent revisioned cards, governed trusted calls, relation provenance and bounded transformations. The separate `echo-grammar-recursive-sentencing` branch has a bounded `RecursiveSentencePipeline`, but repeated expression/reflection does not by itself implement general hypothesis testing or suspended continuations.
- **Other inventories:** earlier Mashet kernels and browser word builders contain registries/UI logic, while many other repositories contain conceptual documents, placeholders, mirrors, workflows or inert worker scaffolds. No further complete Rest selector/composer/executor was verified. Static architecture descriptions and artifact assessments remain separate from recoverable executable implementations.

## Proposed integration, without changing glyph definitions

```text
No external task active + Rest lease + available budget
                         ↓
ע observation portfolio: inspect accessible snapshots, gaps and prior trials
                         ↓
Experiment candidates: unresolved question + material refs + testable predicate
                         ↓
Selector: choose a candidate and eligible typed blocks
                         ↓
MOD-0002: search bounded block compositions on isolated candidate state
                         ↓
Executor: resolve allowed implementations; check input types, permissions,
          invariants, runtime limits and cancellation; retain actual trace
                         ↓
Evaluate against declared evidence → retain / revise / reject / unresolved
                         ↓
CatalogBox: candidate algorithm card, source revisions, tests, outcomes,
            reusable template and checkpoint
```

This is a **proposal**, not an already connected system. ע is the proposed observation/inspection portfolio in this process; it need not absorb all planning, selection and execution authority into one permanent glyph meaning. No new Algorithm 000 authority is inferred.

The missing objective policy must say what makes an experiment useful: resolve a recorded gap, distinguish conflicting hypotheses, test an untried compatible composition, or check whether an earlier result transfers. For a minimal deterministic policy, unresolved evidence gaps and untried compatible compositions could precede stable replay, with a rotating slot to prevent starvation. This avoids pretending that an unexplained decimal novelty score is Timothy's evaluator system. It is still a programmed policy and must be reported as such.

## Recommended order

1. Bind a small set of existing blocks to typed implementation references. Preserve glyph identities and versioned portfolios separately from operation IDs.
2. Reuse MOD-0002 for composition and CatalogBox for trial/candidate records. Add state isolation and executor permission checks before calling any operation.
3. Select experiments from recorded gaps and failed/untried trials. Reuse A-173's question-record idea, with deduplication and explicit evidence status.
4. Test a transparent selection policy, including starvation and repeat-failure controls. Keep attempted exploration history separate from trusted successful evidence before reusing A-101/A-113 as-is.
5. Add idle-triggered, interruptible Rest scheduling. MOD-0008 can advise when to revisit work; it cannot detect idle tasks or enforce mutual exclusion.
6. Compare actual useful outcomes, coverage, repeated failures, source preservation and reproducibility. A trial's successful execution must remain distinct from successful reasoning or factual validation.

## Fresh test evidence and limits

**63 test cases passed locally:** 40 Python cases across six Code Library Python modules; 14 JavaScript cases across the two JavaScript modules; nine Python cases for NVE-D. Source and test Git blobs for the eight Code Library modules were checked against the fetched tree before the final rerun. Two JavaScript files were run directly with Node's test API so the results count their individual cases, not just successful file launches.

Additional small probes demonstrate composition/replay, mutable-state/admission boundaries, and A-101/A-113 checkpoint selection behavior. They are explicitly supplied fixtures. See `reports/echo-rest-investigation/test-results.json`, `boundary-probes.json`, `bandit-probe.json`, and `module-source-manifest.json`.

No complete autonomous Rest capability was tested or claimed. No implementation was integrated, no source repository runtime files were changed, no background workflow was enabled, and no external computation or deployment was initiated. Only this research report and its small evidence records are added to the integration branch.
