# ד DALET — Algorithmic Glyph 4 of 22
## LHEA Glyph Registry · Mashet/LHEA Research

---

## Identity

| Property | Value |
|----------|-------|
| **Glyph** | ד |
| **Name** | Dalet |
| **Gematria Value** | 4 |
| **Letter Class** | Double |
| **LHEA Meaning** | door/threshold/poverty/opening — the liminal point between inside and outside |
| **Algorithmic Operation** | FILTER |
| **Operation Class** | DECISION |
| **Proposed Algorithm** | A-DAL DaletThresholdManager |

---

## The Operation

**FILTER**: Decide what passes through a threshold. Gate the flow.

Dalet is the door — neither inside nor outside, but the decision point between them. In Hebrew, "dalet" is related to "dal" (poor, thin) — the door is the thinnest point, where the wall becomes passable. Every algorithmic decision is a Dalet operation: is this token classified or a gap? Does this word pass the hourglass affinity filter? Does this VGM candidate have enough confirmation events to be sealed? Dalet is the algorithm of gatekeeping.

---

## Existing ECHO Implementations

These algorithms already embody this letter's operation:

- The hourglass neck in A-166 is a Dalet operation — the Governor decides what passes between Dictionary and Lobby.
- A-116 ArticleClassifier's TYPE/SPECIFIC/ABSTRACT/NAME classification is Dalet — deciding which category a word passes into.
- The VGM confirmation threshold is Dalet — a candidate must pass the count threshold to be sealed as a validated axiom.
- The HetBoundaryEnforcer (A-HET) is Dalet applied to structural invariants: only operations that respect the rules pass.

---

## Folding Behavior

How this letter behaves in algorithmic sequences:

ד appears at critical junction points in sequences — between the initialization and the main body, between stages, between input and output. א→ד means "initialize then filter" — set up the system, then decide what enters it. ד→ה means "filter then reveal" — pass something through the gate, then make visible what emerged. When ד appears twice, there is a double-gate — two successive threshold decisions.

---

## Combinatorial Relationships

Key pairings with other letters:

- ד + מ = FILTER + FLOW → "dam" — blood. The body filters what flows through it. Life is a Dalet-Mem operation.
- ד + ע = FILTER + PERCEIVE → "da-ayin" — filtered perception. Selective attention. ECHO classifying only what is relevant.
- ד + ר = FILTER + GOVERN → "dar" — the threshold governed. The VGM validation process: filter by generality, then confirm by the Governor.

---

## Operation Hypernym Chain

The abstraction ladder from this specific operation upward:

```
FILTER → SELECT → DECIDE → CHOOSE → DISCRIMINATE → DISTINGUISH → ACT → OPERATION → FUNCTION
```

This chain is what the HypernymStreamComposer would speak
if fed this glyph's operation type as input.

---

## Research Implications

- DaletThresholdManager centralizes all ECHO thresholds. Currently these are hardcoded constants. When Dalet is implemented, every threshold becomes governable without changing source code.
- The most important Dalet in ECHO right now: the VGM confirmation count. It is set at 1 (immediate) for testing. In production it should be 3-5. Dalet manages this.
- Open question: can Dalet learn its own thresholds? If the lobby is producing too much noise, can Dalet tighten its filter autonomously? This would be self-calibrating gatekeeping.

---

*Previous: [3] | [INDEX](INDEX.md) | Next: [5]*

*ר ECHO · Mashet/LHEA Research · Timothy Marvin Jr.*