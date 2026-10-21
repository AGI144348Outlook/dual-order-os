# 018 — GPT source blocks on an extendable month line

Recorded 2026-10-21. This follows report 017 and Timothy's decision to resume timeline work.

## Why the work changed direction

Timothy clarified the placement algorithm: the Vocabulary Matrix should inform assessment of all encountered information, just as the proposed definition-back cards distinguish understood and unqualified words. Observation and proposals come before structural change. Existing destinations are considered first; deciding to create a new Matrix folder is the last placement determiner.

He assigned Codex to assist him with a detailed conversation timeline and Echo to assist Codex as its vocabulary and agency develop. The immediate instruction was to place GPT export blocks evenly on an extendable line, use calendar months as an arbitrary metric, and work through blocks one at a time. His estimate of about eleven blocks was treated as a question for inventory, rather than a desired count.

## Implemented source arrangement

Group_Canvas branch `experiment/hierarchy-tower`, directory `experiments/month-timeline/`, now contains an isolated phone-oriented artifact:

https://group-canvas-month-line.agi144348.workers.dev/

Its anonymous view is explicitly fictional. With the existing cabinet operator code, it opens a compact private block/month manifest. Block cards are spaced equally across the rail. Calendar months also have equal widths, with six-month extension controls in either direction. The selected source has monthly counts, navigation controls, upload/index coverage and a manually saved review marker. The phone can swipe horizontally without making the whole page overflow.

Block positions are editorial arrangement, not assigned event dates. Actual monthly activity is derived from the preserved chronology's UTC message timestamps. A conversation spanning months retains those timestamps. All recorded GPT branches remain included; this is not a selected-branch-only persona dataset. Claude remains in the existing separate chronology.

The current cabinet inventory contains **12 GPT source slots: 10 complete/indexed and 2 incomplete**. The saved chronology contains **37,729 dated GPT records**, zero unresolved GPT timestamps, spanning **April 2024 through September 2026**. There are 26 months with recorded activity within that 30-month span. Unknown upload coverage is displayed as unknown, rather than as a completed empty block. These are current inventory/index observations, not a claim of complete export coverage.

## Private processing and persistence

The collector read the existing derived chronology and verified its SHA-256 against its saved provenance, then refreshed each source's upload status. It did not reread original exports or change them. The new 5,085-byte manifest was uploaded into the existing private **Conversation timeline · Echo index** collection as `echo-gpt-block-months.json`, downloaded and SHA-256 verified. No new source bucket was created.

The artifact Worker reaches the cabinet through an explicit service binding and retains operator authentication. Its browser API exposes only a read operation for this derived manifest. No raw transcript or private source identities are embedded in anonymous assets. The operator code is not persisted; only revision-scoped non-secret UI preferences are stored locally. Private metadata stays in the opened view and is cleared from that interface when closed. This is not a claim that browser memory can be forensically erased.

The CI evidence contains a fictional screenshot, aggregate summary, browser results and an owner-encrypted manifest. It contains no plaintext transcript. Reproduction instructions are in the artifact README.

## Tests, failure and correction

The prospective plan was published before testing:
https://github.com/AGI144348Outlook/Group_Canvas/issues/4

First code commit `40dd0c850e7363afc45a534f8e16ae75b5b1a744`, run:
https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39555943888

Nineteen synthetic tests passed and private manifest preparation/readback succeeded. Phone interaction reached the real authenticated loading check after passing preview, navigation/filtering, range extension/reset, preference restoration and pending-source handling. That request failed. The first run is therefore not reported as successful private integration.

A follow-up plan was added to the same issue before rerunning tests. The correction added the explicit cabinet Worker service binding, a regression check for its use, and separated the small timezone annotation visually within month cells. The evidence establishes that the binding correction resolved the access failure; the exact original platform-level fetch error was not recorded, so its cause is not claimed as proved.

Final code commit `899a1d7c00b3ebc109eeb70d32e56b6d72e91db5`, successful run:
https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39556167583

**20 synthetic tests passed**: month boundaries and rollover; range validity/extension; equal block gaps; pending/undated/unindexed coverage; source-reference deduplication; GPT/Claude separation; UTC offset handling; source sorting; block/month counting; revision-scoped preference restoration; identity checks; read-only/no-store API; authentication; fixed-origin ticket handling; rejection of external ticket paths; and deployed service-binding use.

**7 browser checks passed** at 390 × 844 with touch: fictional preview and page width; block/month selection; extension/reset; saved review restoration; pending-source handling; actual authenticated private manifest loading with no credential/private block ID persisted; and absence of client runtime errors. These are Chromium mobile-emulation checks, not physical Android-device testing.

## Echo's actual role and limits

This milestone uses the already-derived source chronology from the earlier preserved indexing work. It adds no new Echo semantic dispatch or learning trial and makes no autonomous comprehension claim. Named metadata operations, rendering and human review markers must not be described as Echo reading and understanding the original conversations.

**Implemented/tested:** private metadata preparation, verified persistence, month/block interface, authentication and phone interaction.

**Specified/proposed:** full-expression Vocabulary Matrix assessment, source/sense-scoped red/green markings, context-card capture, evidence-based existing-destination selection, and new-Matrix-last placement. No source word is marked understood by this view. No Matrix directory is created automatically. No model is trained and no external inference is invoked.

The ordering is preserved as PA-028, with PA-021 resumed and encounter/context/continuity documents updated in Dual Order commit `ed187e344cd9c2c0b1c354729cbec7ce9f65de66`.

Next content work is to select a complete block, retrieve source-linked passages in bounded segments, apply actual available vocabulary evidence, retain unresolved words/senses and context, and compare Echo's recorded proposals with an independent review. Unknown words must not become green merely through exposure, spelling matches or a manual progress marker. That semantic stage remains outstanding.
