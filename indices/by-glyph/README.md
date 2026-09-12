# by-glyph

Bidirectional, matching the dual-order principle applied to the index itself, not just the
repo's top-level structure:

- **Matrix-of-Indices direction:** glyph -> the roots/senses it governs
- **Index-of-Matrices direction:** root+sense -> the glyph that applies

Code implementing this bidirectional mechanism at proof-of-concept scale (4 entries, keyed on
root+sense rather than root alone — see below): `/libraries/eve/bidirectional_glyph_index.py`.

## Three unreconciled assemblies, not three versions

The-unicorn-estate's `topology/` folder built root-to-glyph pairings **three separate times**,
at three different scopes, and never reconciled them with each other. Rather than picking one
as "the" answer and discarding the other two, all three are preserved here as parallel,
equally-valid-until-decided assemblies over the same `matrices/latin-roots` and
`matrices/hebrew-glyphs` tables:

- **[`topology-v1-forced-even.md`](./topology-v1-forced-even.md)** — the first pass. All 22
  glyphs forced to exactly 3 roots each, establishing the pictograph-as-anchor pairing method.
- **[`topology-v2-shared-roots.md`](./topology-v2-shared-roots.md)** — a curated ~60-root
  revision. Profile sizes vary naturally (2–4 roots per glyph), and 8 roots (`cap-`, `circ-`,
  `man-`, `port-`, `prim-`, `reg-`, `sep-`, `spec-`) are explicitly identified as legitimately
  belonging to more than one glyph. Presented both root-first and glyph-first.
- **[`topology-v3-full-275.md`](./topology-v3-full-275.md)** — the full classical Latin base,
  all 275 roots (the entire `matrices/latin-roots/roots.json` set), each assigned to 2 glyphs.
  Much larger scope than v1/v2, and the glyph load ends up very uneven as a result (Hey: 49
  roots, Bet: 44, Nun: 38 vs. Dalet: 8, Tsade: 11, Pey: 15).

None of these three supersedes another. They disagree with each other in places (e.g. v1's
`Dalet` cluster vs. v3's 8 roots under Dalet aren't the same roots), and that disagreement is
left visible rather than silently resolved by picking a favorite.

## Why root+sense, not root alone

A single Latin root can resolve to DIFFERENT glyphs depending on which sense is active —
proven directly by `spring`, the same word that broke the WordNet is-a test elsewhere in this
repo. `spring` [natural flow of ground water] -> Mem (Flow/Transition). `spring` [the season of
growth] -> Qof (cyclical Order/Alignment). Same root text, different glyph, resolved by sense.
A root-only lookup would have silently forced one glyph for both meanings — the exact failure
mode that corrupted the water category in the by-is-a test before sense-pinning fixed it.
Keying on (root, sense) instead of root alone fixes this at the architecture level rather than
patching it case by case.

## Open questions before any of this goes into D1

Copied verbatim from `the-unicorn-estate/topology/README.md`, since these questions belong to
the source material, not something this repo should silently answer on its behalf:

- Which document is canonical — the curated ~60-root set (file 2) or the full 275-root set
  (file 3)? They're not currently reconciled with each other.
- Does the pictograph-as-anchor method (traditional paleo-Hebrew letter meanings) actually match
  what you remember of the original topology, or was there a different organizing principle?
  **Resolved as of this repo: the user has confirmed pictograph-as-anchor is correct and should
  be kept as-is.**
- Is Resh's density as a semantic hub (pulling in cap-, prim-, reg- across files 2–3) consistent
  with your memory, or should a different glyph be the hub? *(still open)*
- File 3's uneven glyph load (49 vs. 8 roots) — intended shape, or should it be rebalanced?
  *(still open)*

## Status

Three full-scale assemblies transcribed from the-unicorn-estate's topology drafts (up from the
earlier 4-entry proof-of-concept). The bidirectional (root+sense <-> glyph) *mechanism* is still
only demonstrated at small scale in `/libraries/eve/bidirectional_glyph_index.py` — extending
that code to run against the full 275-root v3 assembly is future work, not done here.
