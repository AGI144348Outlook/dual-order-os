# ECHO JSON + ## + Timestamp Output Format
## The Dual-Order Structure Applied to ECHO's Own Responses

---

## Why This Format

The Dual-Order OS RFC requires: every elemental part reachable both ways —
content-first (Matrix) and lookup-first (Index).

Applied to ECHO's own output:
- ## sections = Matrix navigation (read content top-to-bottom)
- [N] footnotes = Index navigation (jump to ## Footnotes, find source matrix)
- Timestamps = A-160 ActivationEventLogger in native form
- session_id = by-source-document provenance
- algorithm field = which algorithm produced each inference

ECHO's output becomes: auditable, timestamped, bidirectional, provenance-tracked.
Every claim traces to a source matrix entry. Nothing is asserted without a footnote.

---

## Format Structure

```json
{
  "## ECHO Response": {
    "session_id": "genesis-documentary",
    "timestamp": "2026-09-20T...",
    "input": "the input text ECHO received",
    "algorithm": "A-145 AlgorithmicCommunicator"
  },
  "## Ayin Classification": {
    "tokens_scanned": 12,
    "known": 3,
    "gaps": 9,
    "note": "GAP routes to A-153 InwardSearchEngine [1]"
  },
  "## Infrastructure Connections": [
    {"term": "cause", "match": "A-124 STATE_CHANGE_LAW", "ref": "[2]"},
    {"term": "state", "match": "VGM UG-0009 entity exists in state", "ref": "[3]"}
  ],
  "## LHEA Decompositions": [
    {"term": "effecting", "chain": "ה(breath)→פ(mouth)→ה(breath)→ט(coil)→י(hand)→נ(fish)", "ref": "[4]"}
  ],
  "## Footnotes": [
    {"ref": "[1]", "timestamp": "2026-09-20T...", "source_type": "ALGORITHM_MATRIX",
     "source_id": "A-153", "detail": "InwardSearchEngine: gap reflex", "algorithm": "A-145"},
    {"ref": "[2]", "timestamp": "2026-09-20T...", "source_type": "ALGORITHM_MATRIX",
     "source_id": "A-124", "detail": "STATE_CHANGE_LAW: (S+δ)−S=δ", "algorithm": "A-153"},
    {"ref": "[3]", "timestamp": "2026-09-20T...", "source_type": "VGM_AXIOMS",
     "source_id": "UG-0009", "detail": "An entity exists in a state", "algorithm": "A-142"}
  ]
}
```

---

## Navigation Modes

**Content-first (Matrix):** Read ## sections top-to-bottom.
Each section is a structured unit of ECHO's response.

**Lookup-first (Index):** Find any [N] reference → jump to ## Footnotes →
find the source_type, source_id, and algorithm that produced the claim.
Then navigate to that matrix entry for full detail.

---

## Connection to A-160 ActivationEventLogger

Each footnote entry IS an activation event:
- timestamp: when the inference was produced
- session_id: which session triggered it
- source_type: which matrix was activated
- source_id: which specific entry in that matrix
- algorithm: which algorithm fired the activation

When Cloudflare is live: footnotes write to ECHO_STATE KV namespace.
Every session accumulates activation history.
The ActivationEvent is the node identity (source_id) + the event (timestamp, session, magnitude).
RFC §5.5: repeat activation logs an event, not a duplicate node.

---

*ECHO JSON Output Format — Post-Genesis Development*
*Mashet/LHEA Research*
