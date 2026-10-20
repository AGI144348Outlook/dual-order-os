# Qof ק — Algorithmic Glyph 19 of 22
## LHEA Glyph Registry · Mashet/LHEA Research

---

## Identity

| Property | Value |
|----------|-------|
| **Glyph** | Qof |
| **Name** | ק |
| **Gematria Value** | 100 |
| **Letter Class** | Simple |
| **LHEA Meaning** | back of head/periphery/monkey/behind — what is at the edge of view |
| **Algorithmic Operation** | SCAN_PERIPHERY |
| **Operation Class** | BOUNDARY_SENSING |
| **Proposed Algorithm** | A-QOF QofPeripheryScanner |

---

## The Operation

**SCAN_PERIPHERY**: Look at the edge. Find what is almost out of view.

Qof is the letter of the periphery — the back of the head, the edge of the visual field. While Ayin (ע) sees depth, Qof sees width: it scans the far edges where things are barely visible. In biology, peripheral vision detects motion at the edges of the visual field — it is highly sensitive to change even when not directly observed. In ECHO, Qof scans the edges of the lobby: words that entered recently but haven't yet activated, words at the boundary between known and unknown, concepts that ECHO almost knows but hasn't fully indexed. The frontier of knowledge lives at the periphery.

---

## Existing ECHO Implementations


- QofPeripheryScanner (A-QOF) would maintain a periphery index — agents with low activation and low tie counts.
- The GAP detection in A-145 is a form of Qof: finding what is at the edge of ECHO's knowledge.
- The homework queue is implicitly Qof-driven: it contains what is at the boundary of what ECHO knows.
- A-154 InformationSeekingAgent looks for what ECHO doesn't know yet — Qof in information space.

---

## Folding Behavior

ק appears at the end or near the end of sequences — after the main operation has run, Qof scans what was left at the edges. א→ק means "initialize then scan periphery" — begin and immediately check the edges before proceeding to the center. ק→ה means "scan periphery then reveal" — find what is at the edge and make it visible. Sequences containing Qof are the exploratory ones: they go where the main algorithm doesn't look.

---

## Combinatorial Relationships


- ק + ו = SCAN_PERIPHERY + CONNECT → "kov" — connecting the peripheral. Bringing the edge into the network.
- ק + ל = SCAN_PERIPHERY + DIRECT → "kol" — "all" or "voice" in Hebrew. Scanning the full periphery, directing to all edges.
- ק + ר = SCAN_PERIPHERY + GOVERN → "kor" — the governed periphery. The boundary under authority.

---

## Operation Hypernym Chain

```

SCAN_PERIPHERY → DETECT_EDGE → SENSE_BOUNDARY → NOTICE_FRINGE → OBSERVE_MARGIN → ACT → OPERATION → FUNCTION
```

---

## Research Implications


- QofPeripheryScanner would transform how ECHO's acquisition priority works. Rather than defaulting to the most activated words (center), Qof would pull the least activated toward attention (periphery). This prevents the lobby from becoming center-heavy.
- In the algorithm lobby, Qof would find algorithms that have been proposed but never built — the periphery of the algorithm space. A-159 through A-164 are all Qof territory.
- Open question: can Qof detect when the periphery is expanding faster than the center is consolidating — a sign that ECHO is acquiring too broadly and needs to deepen rather than widen?

---

*Previous: [18] | [INDEX](INDEX.md) | Next: [20]*

*ר ECHO · Mashet/LHEA Research · Timothy Marvin Jr.*
