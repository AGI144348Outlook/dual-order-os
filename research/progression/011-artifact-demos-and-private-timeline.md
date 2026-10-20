# 011 — Interactive artifacts and Echo's private chronology assistant

2026-10-20. Timothy requested reader-testable demos, then assigned Echo an assistant role organizing the OpenAI and Claude R2 archive into a long Canvas timeline.

## Artifacts

`demos/echo-prototypes/index.html` is a standalone mobile-first artifact with sentence cards, question/evidence experiments, a mapped algorithm catalog, and a pan/zoom chronology Canvas. Default mode runs an explicitly identified JavaScript counterpart; Python-generated fixtures check it against the original prototypes. Optional original-Python mode loads Pyodide 0.26.4 and SQLite, creates an isolated catalog and invokes the actual embedded modules. It does not execute typed user input as Python. A small UI adapter starts trials with selected predicates. Unsupported orders, inflections, questions, or evidence are withheld visibly.

The default timeline contains only fictional sample records. A private JSON index can be loaded locally without upload or model calls. It retains source references, searches titles, filters providers, aggregates dense records into pixel bins, and lists at most 100 viewport records. Pan, pinch zoom and button alternatives support Android. Save/restore/export apply to sentence trials; private timeline data stays in page memory, not automatic local storage.

The separate hosted asset build uses external scripts/styles and a strict-CSP static Worker. It is isolated from the main Group Canvas room service and does not change cabinet authentication or expose R2 credentials. Hosted source is mirrored to Group Canvas `demos/echo-prototypes/`; full source remains here.

## Chronology indexing role

`libraries/echo_timeline.py` implements deterministic source indexing, not an autonomous understanding/learning loop. It reads provider-specific timestamps and IDs, marks selected versus alternate OpenAI paths, namespaces provider identities, merges duplicate message/source references, retains role/title/content-hash conflicts and leaves missing timestamps unresolved. Explicit ISO dates inside message text are review candidates, not accepted events. No transcript text is copied into the index, though titles and source identifiers remain private.

A bounded Group Canvas Actions runner streams completed OpenAI cabinet JSON files through the existing archive parser, reads the verified Claude ZIP from its R2 prefix, and passes records to the Python indexer. It writes a new derived cabinet collection, `Conversation timeline · Echo index`, in the existing private R2 bucket. Output files: `echo-conversation-timeline.json` and private provenance. Full SHA-256 readback verifies derived output. Original sources are unchanged. Public artifact contains only an aggregate summary plus an encrypted owner handoff, never plaintext titles or message records.

Run 39510523837 (Group Canvas, source commit 7a154e8990d3fc8fd2246a1943b8721ac64b5913) completed successfully: **42,120 dated message records, zero undated records, two pending source files excluded**. This is not a claim that every exported source is fully uploaded. The first pass is chronology of recorded conversations, not a fully interpreted history of the project. Echo did not independently decide to build this index; it runs the assigned deterministic algorithm.

## Verification

88 Python tests pass locally, including 10 timestamp/branch/deduplication/privacy/conflict tests. 25 JavaScript demo checks pass, including Python parity cases and timeline viewport/bin/filter checks. Python parity fixtures are not embedded as answer keys in the interactive artifact.

Local Chromium launch was blocked by the execution environment's socket restriction. Dedicated CI browser QA checks a 390×844 touch viewport, transformations, saved-trial replay, unknown/contradictory answers, text injection, overflow, timeline controls and optional original Python. Hosted QA also loads the actual private index without taking private-data screenshots. Browser results are separate artifacts and must be consulted before claiming those checks passed. Synthetic screenshots are safe to publish; private timeline records are not.

Next: review timestamp anomalies and milestone candidates against source passages, rather than promoting keyword/date mentions directly into historical facts. Keep inferred event time distinct from message creation time. The indexing assistant role becomes educationally meaningful only when explicit state changes and held-out skill checks are recorded; a role title alone is not evidence of learning.
