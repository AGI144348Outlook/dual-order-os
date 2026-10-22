# 019 — First bounded correction-learning test and turn-based classroom

Recorded 2026-10-22 on `experiment/echo-swadesh-fresh-start`. This experiment follows Timothy's index-card classroom, pronoun curriculum, teacher-held reference scale and Neuroplasticity discussion. He authorized testing and requested a phone interface in which he can watch output and sometimes take a teacher turn.

## Outcome

An isolated interactive classroom is deployed at:
https://group-canvas-echo-classroom.agi144348.workers.dev/

It contains an indexboard, teacher/learner desks, encounter cards, entity references, feedback scale, dictionary statuses and visible attempt/feedback records. Interactive mode runs a JavaScript port **locally in the browser**. A separate Python-record view replays the actual completed Python experiment. Neither view is a live stream of remote Codex execution or private model reasoning.

The implementation and synthetic evidence are in `experiments/echo-classroom/`. Canonical code commit: `100a19bf4f6c7a186be50a736490c76903b34f3e`. Artifact mirror commit: Group_Canvas `2f71f3125055a9257b5ef4d036b5a5154acc5225`.

## What “Neuroplasticity” actually supplied

The recovered Code Library source, `code_library_registry/design_notes/neuroplasticity-candidate-algorithms.md` on Echo_Green_Future `code-library-registry`, explicitly marks its mechanisms **proposed, not implemented**. The supplied code does not constitute a complete installed language learner.

Existing executable Genesis mechanisms include A-101 UCB selection and A-113 monitored outcomes/anchored generations. This experiment calls their preserved Python implementations through the existing pinned loader. Original source blob remains `63eb982989b4f3478d649430b555c8f4ba755c27`; no protected core was edited.

A new teaching bridge additionally implements B1-c-inspired saturating evidence counters, 0–3. Four supplied hypotheses resolve a contextual reference: first entity, last entity, speaker and addressee. They are structural priors. The learner acquires a label-to-selector association, rather than inventing a new relational language or learning English from arbitrary text.

The teacher's fixture maps I/you to the expected reference; that mapping is absent from the predictor. Prediction receives only the word and participant context. Teacher feedback is supplied afterward. Arbitrary opaque labels and reversed I/you conventions were also taught successfully in diagnostics, helping rule out a hard-coded lexical answer.

## Procedure and observations

Fresh lesson states were initialized separately from the empty starter profile. Two labels were exposed as candidates. Before correction, the tied initial policy selected the first-listed participant. In the first scene, for example, the learner selected Timothy for I even though Echo was speaking. Teacher-labelled reference feedback corrected that attempt.

Each policy received 48 practice turns: six repetitions of four scene templates with two labels. Eight held-out questions used different entity IDs on those same scene templates, with changed speakers/ordering across the templates. This establishes transfer to new identities within a supplied representation; it does **not** establish transfer to wholly new relational structures or natural conversation.

| Policy | Before practice | After practice |
|---|---:|---:|
| Preserved A-101/A-113, chosen-arm binary outcomes | 1/8 | 2/8 |
| New B1-c teaching bridge, teacher-labelled referents | 1/8 | 8/8 |
| No-feedback B1-c control | 1/8 | 1/8 |

The feedback conditions differ. The counter bridge evaluates all four hypotheses against the teacher's correct referent, while the UCB pathway receives the outcome of its chosen hypothesis. These results are **not a controlled algorithm-superiority comparison**. The low UCB result is an actual limitation of that setup, not a pass for comprehension.

Prediction and frozen assessment do not update the learner. The no-feedback control remained unchanged. The existing CatalogBox stored 96 synthetic attempt/feedback cards and one state card; reopening reconstructed equal learner state. The generated SQLite database remains a local output; public JSON evidence contains the synthetic run and database checksum.

## Live interaction

Present card → learner attempt → frozen teacher turn → select the correct entity → feedback → next scene.

The user can pause the guided fixture and take the teacher turn, inspect hypothesis counters, run a frozen eight-question check, export the local session, and reset only after confirmation. Pending teacher turns survive reload. Guided practice stops after eight grades per activation; it is not an autonomous Recess controller. Mode changes require resetting/exporting an existing session.

The UI's copy/Seen receipt is supplied mechanical scaffolding. It demonstrates reproduction of the assigned word in the adapter, not visual perception or comprehension. Glyph labels describe adapter actions; they do not activate new authority in original Genesis. Human-readable entity names in output are presentation of selected IDs, not independently acquired name vocabulary.

Entries remain yellow after exposure. The narrow score does not automatically grant green working-vocabulary admission. The restricted “define this using only qualified working vocabulary” test has not been implemented or passed. No pronoun is claimed comprehended in all uses.

The scale currently shows matching (=), mismatching (<), or pending feedback (?). A richer directional/improvement model and the > state remain unspecified here. Local teacher actor checks separate API paths but are not cryptographic authentication; the browser owner can alter local state/code. This is not an adversarially secure exam.

## Tests and publication

Prospective plans:
- https://github.com/AGI144348Outlook/dual-order-os/issues/6
- https://github.com/AGI144348Outlook/Group_Canvas/issues/6

**9 Python diagnostics passed:** correction/identity transfer, arbitrary/reversed labels, frozen control, teacher/pending/single-use grading, persistence including pending turns, answer-field rejection and unexposed labels, missing-reference abstention, corrupt counters, and actual preserved UCB/checkpoint calls.

**7 JavaScript tests passed in CI:** both policy ports match all 48 Python attempts, final evidence and held-out scores; no-feedback assessment stays frozen; teacher turns and duplicate grading are gated; state restores; answer injection is rejected; corrupt counters and missing references are handled.

**7 mobile-browser checks passed** at 390×844 with touch: page width/two desks/board, pause-before-grade, reload and correction, second turn/export, Python record replay, confirmed reset/guided practice/frozen check/no automatic green, and no client runtime errors. This is Chromium mobile emulation, not a physical Android test. The fictional screenshot was inspected after execution.

Successful deployment and QA run:
https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39835183059

The Sites local publishing helper was unavailable; no Sites project was created. Publication used the established Cloudflare artifact workflow, isolated from production tower, rooms and storage. No private R2 sources, model/API keys, paid inference or neural training were used.

## Next development boundaries

Before broadening this lesson, add assessments with genuinely new relational structures and distinguish one successful mapping from general comprehension. Further work includes audited vocabulary admission, richer contextual ambiguity/quotation, the first/last-priority learning facilities, multi-tool execution and teacher handover. Preserve these actual failures and limits as the curriculum advances.
