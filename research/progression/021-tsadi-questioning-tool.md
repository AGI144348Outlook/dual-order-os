# 021 — Introducing a multifunctional צ card and Who-only פצ turns

Recorded 2026-10-22 on `experiment/echo-swadesh-fresh-start`. Timothy directed introducing צ on the indexboard, with a questioning algorithm on its back, Who green, What locked until later reference teaching, and separate expansion/paperclip functions.

Prospective plans: [Dual Order #8](https://github.com/AGI144348Outlook/dual-order-os/issues/8), [Group Canvas #8](https://github.com/AGI144348Outlook/Group_Canvas/issues/8).

## Implemented lesson

One stable tool portfolio has three separately named functions: questioning, expansion of blank writing lines, and paperclip attachment. The teacher's revision-1 profile shows the symbol and functions on the front. Its back lists the procedure and initial Who/What/When/Where/Why/How slots. Only Who is green by Timothy's explicit direction for this tool-use scope. What and all other displayed slots remain red/locked; exposure, copying or the prior I/you score does not activate them.

This permission is distinct from general Who comprehension or a closed-vocabulary definition qualification. No new rule grants authority to original Algorithm-000. The new module is an explicitly identified classroom adapter.

The copy exercise reproduces the board profile onto a stable own tool card and checks equality before a ת/ע receipt. This is supplied mechanical copying scaffolding, not proof of understanding. A mismatched symbol/profile rejects. Existing learner state is retained separately.

Expansion adds two blank writing lines through the visible control; it preserves card identity, earlier lines and copied profile, while recording revision/events. Paperclipping links two existing distinct local practice cards, rejects self/dangling links and deduplicates reversed endpoints. It does not merge their identities or prove a relation true.

## Question turn

The פצ session is a separate scene with three entity references. Both role values are initially unknown. The teacher selects whether the requested unknown is speaker or addressee. The question adapter receives this target and participant context without a supplied answer. It uses the definition-back procedure and a supplied phrase: “Who is speaking?” or “Who is being addressed?”

Submission freezes the question until the teacher points to an entity. The reply is recorded as a teacher-pointed reference; it is not independently verified truth, a new grammar rule, or green vocabulary promotion. The current template and question objective are scaffolded, not independently learned or invented by Echo. Free-form articulatory repair remains future work.

Pending question turns block new main-lesson attempts and optional Recess. First-priority note capture remains available. The tool session survives reload, is included in classroom export and is cleared with confirmed classroom reset. The original learner, priority and lesson flows remain available.

Teacher role strings, local card ownership and locked buttons are local API conventions, not adversarial authentication against the browser owner. This is not the owner/badge identity-validation system proposed earlier.

## Source and tests

Reference implementation: `experiments/echo-classroom/tsadi_tool.py`; browser port: `public/tsadi.js`; interface: `public/tsadi-ui.js`. Original source and empty starter profile are unchanged.

**9 new Python tests passed:** copy-before-use/equality, Who-only gate, caller-supplied green-profile rejection, unknown-target/no-answer input, frozen question/teacher-only/single-use reply, identity/content-preserving expansion, relation validation/deduplication and pending/history restoration.

**6 new JavaScript tests** cover Python trace/full-state parity and the corresponding gates. Existing 7 learner and 9 priority/parity tests are retained, for **22 JavaScript cases** in CI.

Initial run 39858194723 deployed and passed the JavaScript suites. Phone QA reached its final post-reload/post-answer locked-What assertion, but that lookup failed because the back of the board card was hidden after reload. Earlier visible slot checks had passed. This was recorded as an interrupted phone test, not a successful full run and not evidence of an unlocked slot.

A follow-up plan was posted before rerunning the affected checks: turn the card over explicitly before the final visible lock assertion and capture a screenshot of the tool back. No production behavior was changed for that harness correction. The final run passed **22 JavaScript cases and 14 phone-browser checks**, including front/back/copy, slot locks, expansion/attachment, exclusive pending turns, teacher reply, persistence and original lesson/priority regressions. The tool-back phone screenshot was inspected. These are 390×844 Chromium touch-emulation checks, not physical Android testing.

Successful harness follow-up: https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39858428848

Screenshot review found that the answer action cleared the visible question while retaining it in history. The subsequent UI correction retains the latest submitted question next to the teacher reply. Its added post-answer assertion and all prior checks passed in the final run: **22 JavaScript cases, 14 phone-browser checks**.

Final run: https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39858749213
Final canonical UI commit: a4f89b82d3e60498248c0731662694ac8421566e; mirror: 93884912f37180cf81803952cb4088001ce83abc.
Interrupted first run: https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39858194723

Initial canonical implementation: `dc2291af2ac9db0a2ae036292dd1179993980225`; harness correction: `3ccdb9c0bdb3f2f1f52795f64d55186252b15cba`. Mirror correction: `7f6668f0b21e413875ed115ba9225117e23e4ee3`.

## Inspect the lesson

https://group-canvas-echo-classroom.agi144348.workers.dev/

Select **צ tool · פצ**, turn over the board card, copy it, expand or attach the practice cards, and submit a Who question. Supply a teacher reply by selecting an entity. The interface identifies the template, source and qualification limits.

No private R2 data, external models, paid inference, neural training or protected-core/tower changes occurred. The original I/you learning evidence is not relabeled as interrogative learning.

## Further portfolios — proposed only

Selection/pointing, bookmarks and return positions, card/deck grouping, reference navigation, and explicit detachment are possible future typed functions. They need their own inputs, permissions, evidence and tests. ץ/string semantics remain unfinished. Identification and validation do not silently transfer from ר or the teacher to צ.

Before What activation, develop and assess the user-requested they/them and this/those distinctions and make any teacher activation explicit. Broader interrogatives and self-selected intelligible question formulation require additional lessons.
