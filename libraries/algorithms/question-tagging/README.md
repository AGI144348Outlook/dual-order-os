# Question tagging and developmental curriculum

Pictures are deferred. This is a text/structured-record prototype, not a visual recognizer or free-text reader.

## Three separate layers

1. **Lexical sense**: the selected meaning and grammatical possibilities of a word. Do not merge bank-as-place and bank-as-financial-institution.
2. **Question affordance**: questions that this sense might help answer. Noun -> possible What is a broad default, not evidence of truth. Person -> Who/What, place -> Where/What, time interval -> When/What, manner/method -> How, cause/purpose -> Why, quantity -> How many/much. Category assignments need supplied provenance; definition keywords only create unapproved hints.
3. **Contextual binding**: which event's agent, patient, location, time, owner, manner, method, cause, purpose or quantity is explicitly recorded. Only these supplied facts can answer the structured question interface. Context and evidence are mandatory. The interface does not infer event roles from words or parse natural-language questions.

`morning` may answer When in "When did he leave?" and What in "What follows night?". `school` may answer Where in one event and What in another. A clock's definition mentions time, but that does not make the clock a temporal interval. No adverb -> How blanket rule. Whose requires possession evidence, Why requires cause/purpose evidence. Which needs a supplied alternative set and selection condition; it currently abstains. Quantity does not yet distinguish count vs mass units.

Tags are stored on separate annotation cards pinned to lexical-sense revisions. Displaying them as an entry suffix is a future UI view. Raw dictionary files remain unchanged. Updating a sense makes its old annotation detectably stale. New annotations preserve prior versions.

Code: `../../echo_question_tags.py`. Entry points: `candidate_tags`, `definition_hints`, `save_tags`, `tags_current`, `answer_role`.

## Identification through transfer

| Stage | Teaching material | Independent evidence required |
|---|---|---|
| Identification | Distinct sense cards and counterexamples | Select a sense for unseen examples without labels leaking answers |
| Structure | Agent/predicate/patient and contextual roles | Preserve role differences under word-order changes; do not treat actor as owner |
| Comprehension | Short passages plus explicit source facts | Answer supported questions with evidence; withhold missing or conflicting facts |
| Generalization | Supplied subtype paths, examples and counterexamples | Broaden positive existential statements without inferring universals |
| Inference | Explicit rules and premise cards | Return rule/premise trace; reject invalid and contradictory deductions |
| Composition | Position cards, agreement and morphology examples | Produce an appropriate supported sentence; preserve intent through revisions |
| Recursive Return | Open positions, continuations and revision history | Suspend/resume multiple branches and insert without losing originals; not implemented yet |
| Transfer | Frozen unseen words, names, situations and domains | Use the taught rule without changing it or reading expected answers |

For each stage: pretest -> recorded lesson/change -> guided practice -> frozen held-out test -> restart/retention -> transfer -> earlier-skill regression. These are separate sets. Test answers must not become runtime input. A developer editing code is an engineering intervention; a retained card update by an authorized learning procedure is adaptation. No automatic graduation or biological equivalence is asserted.

The included tests establish interface boundaries on structured fixtures. Renaming a supplied entity tests a narrow invariance, not general transfer comprehension. No sentence-to-facts parser or autonomous teaching/learning loop exists yet. Existing broad diagnostic failures remain.

## Evaluator proposal

Use explicitly documented outcomes: SUPPORTED, UNKNOWN, WITHHOLD, ABSTAIN. A proposed visual mapping to Timothy's evaluator vocabulary may use ✓ for meeting a frozen criterion, X for a demonstrated error, and ≈ for explicitly enumerated partial criteria. Do not treat these provisional mappings as changes to the Generalized Evaluators' authoritative definitions. Not tested and unknown remain distinct. Record exact failures rather than hiding them behind an aggregate score.
