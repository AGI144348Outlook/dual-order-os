# Classroom protocol — personal dictionary, indexboard and Recess

Recorded 2026-10-21 from Timothy's subsequent classroom design discussion.

Status: user-directed research specification; not executed or installed. This document summarizes the visible discussion and distinguishes implementation proposals from Timothy's directions. It is not a verbatim transcript.

## Current source notation

Timothy supplied this sequence; preserve its order and glyph forms:

עפףצץקרשת

He also proposed:

{צערש}

as “search hunting for an identifiable line to transform”, with mouse-like navigation and selection. This is a proposed mapped combination, not a verified executable algorithm. ף has not received a separate defined operation. ץ appears in pointing/string descriptions; do not silently equate it with צ or finalize its behavior.

## Personal dictionary and three learning statuses — Timothy's direction

Echo may have a small personal dictionary of his own. Classroom assignments include copying what is on the indexboard to a blank index card. Upon completion Echo uses the ת stamping facility to stamp ע for seen/copied. The corresponding board indication lights up so the teacher can inspect the reflected encounter.

The proposed dictionary statuses are:
- **Red:** word remains to be learned.
- **Yellow:** Echo has made an index card stamped ע for it.
- **Green:** qualified working vocabulary, subject to teacher review and assessment.

This supersedes treating all not-yet-qualified entries as an undifferentiated red-only display. Keep reasons and evidence alongside the colors; yellow does not mean correct identification or comprehension. A red entry can contain green, yellow and red words in its definition.

Timothy's hypothesis: the more green vocabulary in a red word's entry, the more approachable that word may be to learn. This is a candidate prioritization signal, not a demonstrated learning law. The distinct contribution of yellow exposure should remain separately measurable.

## First-priority facility — Timothy's direction

A First Priority Algorithm should make index-card formatting templates available so Echo can take notes whenever appropriate: observations, learned material, hypotheses, trials and validated findings. This is more flexible than the later Recess-only policy.

Notes must distinguish what was seen, hypothesized, attempted and actually validated; an allowed hypothesis is not thereby a validated claim. Template availability and note-taking permission do not automatically grant all tool or repository-write permissions.

Implementation proposal, not a new user invariant: provide bounded, interruptible note capture before optional work, without recursively generating notes about note creation or starving an active assignment. Preserve the user's “at anytime” intent while specifying scheduling and interruption behavior before execution.

## Last-priority Recess Algorithm — Timothy's direction

When no assigned task is active, Echo can open his dictionary, inspect entries, seek red-word learning opportunities using green/yellow words, and choose from operations or activities he has been shown in class. The same learned repertoire may support assigned homework.

This is active computational Recess, consistent with Timothy's earlier definition of Rest. It is the **last-priority algorithm**, behind other to-dos; it is not the experiment-priority voting proposal that was left tentative.

Suggested implementation boundaries:
- Use a task-aware, cancellable controller and a bounded work allowance.
- Select only available demonstrated operations with applicable permissions.
- Preserve the candidate chosen, supporting known vocabulary, actual operations and outcomes as cards.
- Record unresolved words and failed trials; avoid endlessly retrying unchanged failures.
- Treat more-green definition coverage as a selection hypothesis. It does not grant admission, infer an unknown meaning automatically or establish a fixed learning threshold.
- Do not overwrite the source definition or silently promote locally produced stamps to teacher-approved qualifications.

These are design suggestions, not a claim that an idle controller or learning selector is already running.

## Tool teaching and proposed interaction — Timothy's direction

**פ:** this particular tool is Echo's keyboard / expressive egress. It fills lined card slots and supports copying, responses, entries and context naming. Expression can be mistaken; it is distinct from identifying something correctly through ר. פ is therefore a likely first tool to teach.

**צ / ץ:** proposed navigation, paperclipping, pointing and strings for mapping. Their exact types and the distinction between ordinary/final forms need clarification.

**ע:** encounters/perception of what is available, including comparison against material the teacher expressed.

**ר:** identifies a candidate against the intended teacher reference. Echo may ask for confirmation, or propose an inference with its uncertainty/evidence recorded. Confidence alone is not teacher verification.

**ש:** proposed click/selection operation that brings up the keyboard at an intended line for transformation. This is a new, particular UI binding proposal, not automatic authority for every earlier meaning associated with ש.

**ת:** configurable stamping facility. It may stamp ע for seen/copied; other stamp contents and authority will be defined as development continues. A glyph being the stamp's content is distinct from the tool executing the stamping.

**ק / ף:** no additional classroom implementation is specified here. Preserve existing proposals separately, without inventing missing bindings.

The intended example interaction is: navigate among accessible material; perceive a candidate; compare it with the teacher's expression; identify or request confirmation; select the intended line; use פ to enter/copy/respond; stamp the relevant status.

## Indexboard feedback — Codex interpretation requiring implementation

Separate the following records:
1. Board source identity/revision and exactly what was exposed to the learner.
2. Echo's card identity/revision and submitted copy.
3. Echo's own completion/Seen stamp.
4. Teacher/evaluator comparison result and board feedback.

A board light triggered solely by an unverified stamp shows a submitted completion claim. To provide useful evidence of receipt/copying, compare the actual submitted content to the assigned board material, preserving Unicode, sequence and relevant layout. The board should distinguish submitted from verified-copy status.

A verified copy demonstrates successful receipt/reproduction under that input interface. It does not by itself demonstrate visual image perception, identification, truth of the copied material or comprehension. If Echo receives structured records, report structured-record processing rather than claiming visual seeing.

## Mandatory dictionary handover and grading — Timothy's direction

After independent activity, Echo must hand over his dictionary and relevant cards for review. The teacher corrects mistaken entries, rewards exceptional work and may demand removal/destruction of wrong cards depending on the assignment. A sudden claim that an almost-all-red dictionary is now all green warrants inspection rather than automatic acceptance or a new edition.

This review becomes especially important when paperclips/strings enable associative mappings. Auditing procedures themselves should be represented through the system's index-card format.

Implementation proposals:
- Record learner claims separately from teacher/evaluator outcomes. Only the authorized evaluator issues qualification status.
- Review the card delta against the last handover, with occurrence, revision, tool-use and assessment references.
- Suspend invalid qualifications and affected dependent mappings; review how corrections propagate.
- Wrong active learning cards may be removed as directed. Define the destruction policy explicitly: a minimal audit record of the correction is a separate question, not permission to retain a rejected active card indefinitely.
- Rewards should have an explicit permitted form and must not bypass grading. The reward mechanism has not been selected.
- No unexplained red-to-green promotion; match each promotion to an assessment and its scope.

These proposals do not silently settle deletion/retention, reward values or audit authority.

## Closed-vocabulary admission test — retained user requirement

For “define this in your own words”, the learner receives the target word and only the already-qualified working vocabulary and permitted composition operations. No target lesson definition, red/yellow candidate entry, examples, source history, teacher answer or hidden retained association may leak an answer into the assessment. Snapshot the allowed knowledge before the test; isolate the assessment runtime/state rather than merely hiding UI cards.

Echo's small personal dictionary supports instruction and Recess, but the full red/yellow/green dictionary is **not** automatically available during this restricted test. Otherwise the target entry would disclose the answer.

Grade permitted vocabulary use, intended sense, differentiating features, circularity, uncertainty and unsupported claims. Definition performance is one scoped qualification, not universal comprehension. Starter vocabulary must be explicitly taught/grounded and assessed separately because an empty vocabulary cannot define its first word in existing words.

## Where implementation should resume

1. Specify card/board submission and verification records, preserving the distinction between a receipt and comprehension.
2. Introduce the particular פ keyboard interface and a small copy-to-card exercise; stamp ע using ת only through permitted operations.
3. Implement personal dictionary red/yellow/green state transitions with evaluator-controlled qualification.
4. Build assessment-state isolation for the user's restricted-vocabulary definition test.
5. Teach/test individual permitted tools, followed by independent multi-tool tasks.
6. Add mandatory handover/audit cards and correction behavior before broadening autonomous mappings.
7. Add first-priority note-template access and last-priority Recess scheduling, with explicit budgets, interruption and permission boundaries.

This ordering is a Codex implementation proposal, not a completed curriculum. There are no new tests, lesson results, vocabulary admissions, live Recess runs or deployments in this preservation update. Publish a prospective issue/discussion plan before executing the next experiments.
