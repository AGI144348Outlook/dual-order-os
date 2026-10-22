# 022 — Classroom as a reading-only documentary

Recorded 2026-10-22. Timothy clarified that the visual classroom is for reading experiments, with participation deferred. He wants Codex to conduct the actual teacher–student relationship with executable Echo; the classroom is the observation surface, not the project's operator.

## Correction of the experiment framing

The recorded sessions in reports 019–021 were scripted synthetic experiments, frozen checks and tool/controller demonstrations. Codex prepared and reviewed those experiments, but their fixture corrections and supplied question templates were not actual ongoing teacher–student dialogue between Codex and Echo. The results remain valid only within their stated limits. They are not relabeled as conversational teaching.

The reading page states that actual Codex–Echo teaching exchanges have not yet been archived. The [documentary protocol](../../experiments/echo-classroom/DOCUMENTARY-PROTOCOL.md) preserves the required next workflow: Codex gives an actual assignment, reads the executable learner's actual output, responds and supplies feedback, then checks subsequent behavior. Unsupported output remains unsupported; no student dialogue may be invented to fill the classroom.

## Implemented reading surface

The default classroom page now imports a pure evidence-mapping module and a viewer, rather than the learner/teacher/priority/tool execution modules. It reads existing JSON evidence by GET only.

Four visual chapters present the recorded material:
1. Reference-learning attempts and scripted fixture feedback.
2. Frozen retention/transfer records.
3. Priority-controller/Recess demonstration records.
4. Tool copying, expansion, attachment and supplied Who-question demonstration.

The indexboard and two desks show the saved input/output/feedback. Chapter and previous/next controls change only the viewed record. Expandable context/raw-record panels and exact source pointers support inspection. Narrative report links retain original provenance and limitations. No timestamps or teacher attribution are invented.

There are no teacher input fields, answer buttons, grading, practice, Recess execution, current-session export/reset or background learner loop in the reading page. It does not restore, read, modify or erase previous local practice state. The old participation HTML is archived outside public assets at `archive/interactive-index.html`; source implementations, historical tests and evidence remain preserved.

The earlier hosted JavaScript files remain archived source assets but are not imported by the default viewer. This is a read-only default interface, not a claim that a browser owner is technically prevented from executing unrelated downloaded code.

## Validation scope

Prospective entries:
- https://github.com/AGI144348Outlook/dual-order-os/issues/9
- https://github.com/AGI144348Outlook/Group_Canvas/issues/10

Only documentary verification is run in the updated publication workflow; the old teaching/parity suites are retained but not executed for this UI-only change. No new learning trial, model invocation, grading experiment or vocabulary admission is performed.

The first local documentary test launch failed on a typo in its test-file import.meta URL expression before the checks ran. The harness typo was corrected; subsequent results are recorded separately rather than treating that launch as a pass.

Checks cover exact source event counts/pointers, preserved numeric results, explicit scripted-teacher attribution, keeping the recorded question visible beside its reply, absence of evidence mutation and absence of participant/learner/storage imports. Phone QA checks reading/navigation, raw source access, GET-only requests, no participant inputs or learner modules, and zero storage-method calls by the page.

Canonical implementation: `5119345a0467a27f04ab0f6a42d22822c2bceb94`; mirror: `8610aa9cfc6bc5437fee47ee348797c06850c5b5`.

**6 documentary tests and 5 reading-only phone-browser checks passed.** The browser checks used a 390×844 touch viewport and instrumented storage calls and network methods. The page made no storage-method calls and loaded no learner/controller modules. This is mobile emulation, not physical Android testing. The saved phone screenshot was inspected.

Successful deployment/check run: https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39862826702 The live reading URL remains:
https://group-canvas-echo-classroom.agi144348.workers.dev/

## What remains separate

A real teaching-session capture pipeline and substitute participation are not claimed implemented by the viewer. Future chapters must be built from actual attributable assignments, returned outputs, teacher responses, state revisions and outcomes. Public records must avoid private reasoning or personal-source material. The protected original core, empty starter profile, earlier evidence, user's practice state, and existing tower/room/storage services are unchanged.
