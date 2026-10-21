# Encounter and context-card protocol — candidate design

Status: proposed, derived from Timothy's 2026-10-21 clarification. No new glyph operation or vocabulary authority is installed by this document. Proposal links: PA-001 through PA-010, PA-017, PA-018, PA-020.

## Record boundaries

1. **Source record:** original artifact identity, hash, permissions and immutable reference.
2. **Occurrence card:** exact symbol/word span, surrounding expression, source/page/message/branch, speaker and time if supplied. Preserve the original spelling and Unicode; normalized lookup aliases are separately labeled.
3. **Word/symbol index:** stable identity and references to candidate senses, active meaning-slot assignment and context cards. A multiword expression can have its own identity; do not split every meaning into isolated tokens.
4. **Definition-back card:** literal source definition, source/author attribution, selected sense or unresolved alternatives. If no definition is available, leave it unresolved rather than generate a definition and label it sourced.
5. **Context/use-case card:** exact occurrence/example, proposed interpretation, relation to an existing sense revision, evidence type, exceptions/contradictions/questions and revision history. An example printed in a dictionary is a supplied example, not a successful observed trial.
6. **Qualification card:** named test, task/sense scope, held-out inputs, reference judgment, actual result, limitations, time and versioned implementation. This is separate from the definition and from the count of times it was encountered.

## Candidate algorithm

```text
receive permitted source
  → preserve source and occurrence identity
  → ע encounter/perception record
  → ר attempt to recognize an established index/sense
       recognized: retrieve the currently slotted interpretation
                   and relevant צ-linked context/contradiction cards
       unfamiliar: צ allocate candidate word index + blank definition-back card
                   attach a sourced definition when one can be located
  → annotate definition tokens against the Vocabulary Matrix
  → process the occurrence using explicit available operations
  → if new use/context/exception/question:
       fill a candidate context card
       proposed ת record provenance/status
       צ attach to the word index stack and relevant sense revision
     if repeated evidence:
       retain a new occurrence reference without inventing independent support
  → retain alternatives and unresolved relationships
```

This is a desired workflow. Existing paperclip, associative stamp, catalog and adapter methods implement only parts of it. Do not portray this pseudocode as already executed by Echo.

## Red/green definition display

Timothy requests green for words understood and located in the Matrix, red for words still needing learning. Store the underlying fields separately:

- `matrix_presence`: source-linked identity/sense exists, absent, or unresolved.
- `qualification`: evidence-backed allowed uses, test references and revision; or unassessed/failed/outdated.
- `context_sense`: resolved sense or explicit alternatives.

Green requires the relevant sense to be present and qualified for the intended use; raw spelling presence, a copied definition, a self-issued confidence value, or a passing storage test is insufficient. Red keeps the reason visible: absent definition, unassessed use, contradicted interpretation, stale evidence, or unresolved sense. Add text/icons so color alone is not required. These implementation details are proposals and must not fabricate pass thresholds Timothy has not settled.

Definition-word acquisition can recurse, so record a bounded dependency graph with visited nodes, cycles, budgets and suspended unresolved branches. Unknown words in definitions must not cause an endless expansion or prevent retaining the original candidate.

## Admission and repository management

Indexing an occurrence and preserving a hypothesis can happen before semantic admission. Qualification for recognition, source retrieval, sentence construction, inference or executable use is granted separately. Failed trials remain useful context; suspend an invalid assignment without deleting source history.

Repository files/functions/registries/matrices also need structural entity cards. A word stack about a component is not the component's file identity, implementation or write permission. Proposed repository changes require their own affected-entity references, permission checks, tests and before/after issue records.

## Expected tests before implementation claims

Unknown encounter creates one stable candidate; repeated encounter adds provenance without duplicate identities; source definitions remain literal; green requires the relevant qualification; unknown definition words stay red; ambiguous senses remain unresolved; contradictory context remains retrievable; new slot versions preserve old contexts; red-word dependency cycles stop within budget; failed/cancelled operations do not corrupt the stack; restoring saved state preserves the exact assignments and evidence.

These tests are planned criteria, not results of this documentation work.
