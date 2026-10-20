# 009 — Sentence cards and dictionary observation

Date: 2026-10-20. Integration branch only. Requested by Timothy: mapped algorithm library, adaptable sentence cards, dictionary plus available algorithm blocks, and observation without a sentence task.

## What changed

`libraries/echo_sentence_cards.py` separates lexical-sense identities from stable sentence-position identities. It preserves all supplied senses, uses explicitly supplied noun-subtype evidence, supports positive-existential generalization and candidate specialization, preserves alternatives and revisions, reorders positions without silently exchanging semantic roles, and provides six explicit singular predicate forms. Unsupported inflection or order abstains. No source glyph role, Algorithm 000 rule, or protected Genesis source was changed. These are trusted Python interfaces with a read-only option, not authentication, a secure runtime sandbox, a complete grammar, or an autonomous agent.

`libraries/algorithms/mapped-combinations/` catalogs 14 combinations with status, relative code paths and callable references. Proposed Recursive Return and DSL inversion have no executable references. MirrorStep's adapter remains on its separate branch. The catalog itself is inert; recipe functions require explicit calls.

## Data and protocol

Source: exact `core-lexicon.zip` preserved in `vendor/echo-genesis/integration-inbox/core-lexicon/`, Git blob `370e23a301badb6362eac29682afc5bba9e8d5a4`. Read `words.json` as data only: 1,000 spellings and 1,491 sense cards. No Python or JavaScript from the archive is executed. Every sense and its source role/definition remain distinct. Legacy Genesis receives the first listed sense per spelling because its index is spelling-keyed; that lossy projection is disclosed, not treated as sense resolution. No mixed-POS Chinese specialization edges are imported.

**Idle availability:** place the sense cards and 14 inert block records into the catalog and inspect state without invoking a work runner. No events or state changes occur. This is a call-boundary inspection, not a timed background-agent trial. There is no autonomous dispatcher, so giving blocks to the process does not activate them.

**Explicit starts, no sentence goal:** standard dictionary ingestion, orientation, typed study groups, generality scoring, neighborhood proposal/scrutiny/commit; then the existing A-120 evolution runner (two generations maximum, eight wrapped commit calls maximum); then the existing UnderstandingGenerator (40 candidate attempts maximum). The order, budgets and startup are experimenter choices. Word selection and acceptance inside the routines follow their existing programmed policies. New recorder code mirrors outputs into index cards; this is not evidence that Genesis independently chose to call the card API.

An initial local run omitted generality scoring and neighborhood initialization and produced an empty pool. This was a harness omission, not an Echo capability result. The complete runs below restore the documented order and retain default thresholds.

## Actual complete-run observations

Two runs used Python hash seeds 42 and 7, with random seed 42. Both produced identical candidate sequences and logical final-card hashes.

- 1,000 WordAgents, 2,713 ties.
- Zero proposed neighborhoods and zero committed neighborhoods under default rules.
- Consequently A-120 performs zero recruit/refine/split/merge commits; no threshold was relaxed to manufacture activity.
- Generality pool: 95 words.
- Forty accepted candidate statements, all persisted as `heuristic-acceptance-not-proof`.
- First candidates include `An time place`, `An time come`, `An time cause`, `An time use`.
- Forty accepted candidates from forty attempts demonstrates over-permissive heuristic validation, not sound general logic or grammatical completeness.
- 1,545 final cards: 1,491 lexical senses + 14 block records + 40 statement candidates.
- Catalog content survives closing and reopening the SQLite database.
- No self-chosen sentence goal, algorithm invention, independent block composition, spontaneous sentence-frame construction, or self-initiated card manipulation was observed.

The new renderer is exercised separately in tests. Those directed fixtures are not outputs of the observation. Likewise, arranging words, returning to an index, and generalizing a proposition are different operations. This prototype does not implement suspended continuations or branching Recursive Return.

## Tests

61 Python tests pass locally: 43 existing tests, 17 sentence-card tests, one mapped-code reference test. New checks cover sense separation, idempotent intake, multihop evidence, original revision preservation, specialization status, unrelated substitution rejection, directional constraints, universal/negative scope refusal, role/POS mismatch, reorder/restore, stale writes, restart persistence, changed-sense edge invalidation, read-only calls, unsupported conjugation, `have -> has`, archive identity rejection, and actual relative callable references (separate branches explicitly marked).

Existing language/reasoning diagnostic failures are not repaired by these passing storage/transform tests. Countability and unrestricted morphology remain unresolved. The catalog's subtype edges are supplied assumptions, not independent semantic proofs. Existing A-120 numeric scores are legacy behavior, not an implementation of Timothy's Generalized Evaluators.

## Next implementation boundary

A dispatcher capable of choosing among blocks and operating sentence cards remains absent. Building one would require an explicit scheduling/selection policy, action budgets, permission gates, and provenance linking decisions to card revisions. Report its programmed policy plainly; do not portray a manually orchestrated pipeline as unprompted agency. Strengthen candidate validation before any candidate becomes authoritative logic.
