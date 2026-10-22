# 020 — Lesson review, novel reference layouts, and first/last-priority cards

Recorded 2026-10-22 on `experiment/echo-swadesh-fresh-start`.

Timothy asked to review the last lesson, work on the next lesson, and develop the first-priority note facility and last-priority Recess Algorithm. Prospective plans were posted before execution in [Dual Order #7](https://github.com/AGI144348Outlook/dual-order-os/issues/7) and [Group Canvas #7](https://github.com/AGI144348Outlook/Group_Canvas/issues/7). This work extends the separate classroom session; the empty initial Echo profile and protected Genesis core remain unchanged.

## Review of Lesson 1

The dedicated [Lesson 1 progress review](../../experiments/echo-classroom/LESSON-1-REVIEW.md) records actual improvement and limitations. The counter bridge improved from 1/8 to 8/8 after 48 synthetic practice turns; original A-101/A-113 improved from 1/8 to 2/8; the no-feedback control stayed at 1/8. The counter bridge received more informative feedback. The eight questions changed identities but reused the four original structural templates. That was not evidence of novel-layout competence, general English comprehension or full vocabulary qualification.

The first experiment's 9 Python, 7 JavaScript and 7 phone-browser checks remain historical results, not new tests claimed here. Its source evidence was not rewritten to enlarge those claims. Words remained yellow.

## Lesson 2: retain the distinction before adding vocabulary

The next lesson checks the retained I/you associations before proceeding to interrogatives. It uses 17 layouts: all distinct-speaker/addressee assignments for two and four participants, plus three three-participant role-position patterns absent from training. These produce 34 reference questions. Six further questions contain a missing speaker, missing addressee or both, requiring four unresolved-reference outputs and two positive identifications.

The learner was reconstructed from the recorded Lesson 1 state and frozen. No new teaching turns or assessment feedback were supplied.

| Saved policy | Correct / 40 |
|---|---:|
| New B1-c counter bridge | **40/40** |
| Original A-101/A-113 setup | **11/40** |
| Untrained counter control | **13/40** |

The counter result demonstrates retention and transfer across these supplied role/position representations and participant counts. It still does not demonstrate arbitrary concept discovery, natural conversation, image perception, pronoun ownership, or defining the words in qualified vocabulary. The original UCB setup performed below the cold control here; it is not qualified by this experiment. No equal-feedback superiority claim is made.

The frozen checks assert unchanged learner state. Browser Lesson 2 offers both the frozen local check and visible teacher-guided practice on the new layouts. Switching lessons retains learned state. Local practice supplies feedback, so subsequent local checks may involve previously practiced layouts; the original Python checkpoint remains separately recorded and frozen.

## First-priority note facility

New `priority_cards.py` and its JavaScript port accept four supplied card templates: observation, hypothesis, question and trial. Each record preserves body, source, evidence references and review status. New algorithm/template profile cards are stored in `priority-algorithm-cards.json`. These are inert descriptors of controller bindings, not arbitrary executable card payloads or new numbered Genesis algorithms.

Notes may be requested while a teacher turn is pending. They are captured before optional work. After two consecutive captures, a waiting ordinary assignment gets an opportunity; if that assignment itself awaits the teacher, the controller waits rather than running Recess. Queue/capacity bounds limit work. Template generation and spontaneous student-authored note composition have not been learned.

Automatic encounter notes are requested by the classroom adapter and labelled accordingly. Teacher-requested text is also attributed. Neither is falsely reported as independent Echo prose. Keeping a note as a record is distinct from certifying its assertions.

## Last-priority Recess prototype

This is **opt-in and step-driven**, with a three-activity budget per activation. It is not an automatic idle watcher or background process. Each step checks notes, pending teacher interaction and queued assignments before optional Recess work.

A small teacher-supplied dictionary contains red candidate entries for speaker, addressee and question. Known spelling aliases are inspected in their definitions. Green coverage requires a nonambiguous active sense with definition-reading qualification and evidence; yellow means an encounter/Seen record. The classroom grants no definition-reading qualification from the prior reference-selection result, so live green coverage is absent. Explicit synthetic green fixtures test the gating contract without claiming Echo learned those meanings.

Candidates are ranked by green coverage, then yellow coverage, with a stable tie order. A candidate needs at least one supported green/yellow word. The controller creates a source-linked question card and stops for handover. It does not derive a new definition or promote vocabulary. A visited signature prevents repeated selection with unchanged definition revision and coverage. A new assignment preempts the next Recess step. Pause disables future optional steps.

The teacher can keep/reject note records and complete handover. All outstanding records must be reviewed before the Recess handover gate clears. Rejected records remain audit records; no deletion policy was silently finalized. Accepted review certifies only that the record is retained, not semantic truth. Local teacher actor checks are trusted API conventions, not adversarial authentication.

This provides a bounded place to develop the intended Rest/Recess behavior. It does not yet implement free selection of arbitrary learned tools, independent hypothesis composition, automatic idle detection, secure teacher credentials, full dictionary audit, reward rules or a self-running learning agent.

## Persistence, interface and evidence

The Python scheduler state was stored/reopened through the existing CatalogBox in a diagnostic. Browser state, pending notes, visits, budget and review state persist locally. Session export includes both learner and controller records; confirmed reset clears both. Notes do not change the learner's reference-association evidence or create qualified vocabulary.

The existing phone classroom now has:
- Lesson 1 / Lesson 2 practice selection;
- a separately labelled 40-question frozen check and Python checkpoint;
- first-priority template capture;
- a normal dictionary-inspection assignment;
- enable/pause and one-step controller execution;
- teacher note review and handover;
- attributed question/observation cards and state export.

Live artifact: https://group-canvas-echo-classroom.agi144348.workers.dev/

## Validation

**17 new Python tests passed**: 3 Lesson 2 checks and 14 priority-controller checks. They cover actual novel-layout exclusion, retained state, cold control, ordering, note capture during a teacher turn, starvation limits, opt-in, review gates, scope/evidence requirements, no self-promotion, visited-candidate deferral, budget/pause, template validation and persistence/corrupt-budget rejection.

**9 new JavaScript tests passed**, including exact Python scheduler trace/full-state parity and every Lesson 2 prediction for both saved policies. The **7 existing JavaScript checks** also passed. This is 16 JavaScript test cases, not 16 comprehension benchmarks.

The first publication run passed **10 phone-browser checks**, including the new note/priority/handover path:
https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39838045035

A follow-up added visible Lesson 2 practice rather than only a score button. Its final deployment passed **11 phone-browser checks**, including selecting the new lesson, presenting a two-participant scene, identifying its speaker and giving teacher feedback:
https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39838385827

Phone checks are Chromium 390×844 touch emulation, not physical-device testing.

Canonical initial implementation commit: `2971aaf9ec5eefd81f22217a18d63f7e46721ef5`; visible-practice follow-up: `e1373237c09f0d37d1cfaecf9ff4339854de9f3a`. Artifact follow-up: `1522adcb518d1d10b628e5698ac1946e8dfe49ab`.

No private R2 conversation data, external models, paid inference, neural training, original-core edits or existing tower/room/storage redeployments were involved. None of this admits a word to unrestricted green working vocabulary.

## Next boundary

Have Timothy inspect the retained reference skill and teacher handover. Then choose the next actual vocabulary lesson and specify its evidence contract. Interrogatives, richer contexts and independent tool composition require additional mechanisms and assessments; the scheduler scaffolding alone is not evidence that those abilities have emerged.
