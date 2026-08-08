# by-glyph

Bidirectional, matching the dual-order principle applied to the index itself, not just the
repo's top-level structure. Both directions are first-class:

- **Matrix-of-Indices direction:** glyph -> the roots/senses it governs
- **Index-of-Matrices direction:** root+sense -> the glyph that applies

## Why root+sense, not root alone

A single Latin root can resolve to DIFFERENT glyphs depending on which sense is active —
proven directly by `spring`, the same word that broke the WordNet is-a test earlier this
session. `spring` [natural flow of ground water] -> Mem (Flow/Transition). `spring` [the
season of growth] -> Qof (cyclical Order/Alignment). Same root text, different glyph, resolved
by sense. A root-only lookup would have silently forced one glyph for both meanings — the
exact failure mode that corrupted the water category in the by-is-a test before sense-pinning
fixed it. Keying on (root, sense) instead of root alone fixes this at the architecture level
rather than patching it case by case.

## Status

Proof-of-concept scale (4 entries: spring x2 senses, colleg-, sec-), not yet the full 275-root
set. Demonstrates the mechanism works bidirectionally before scaling it up.

Code: `/libraries/eve/bidirectional_glyph_index.py`
