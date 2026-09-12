# dual-order-os

Shared infrastructure for every framework (Mashet, LHEA, eve3/MashetEVE, JurisDictionary, and
whatever comes next) — built on the idea that breaking each framework down into elemental,
reusable parts lets those parts be recombined modularly into new models later, instead of
re-authoring the same kind of infrastructure from scratch each time.

**Status: mostly marked shelves, several now stocked.** A growing set of folders have real
content: `matrices/mashet-dictionary` (a 22-letter neo-glyphic dictionary, 8 letters drafted so
far), `matrices/english-lexicon-eve` and `libraries/eve` (a working test lexicon plus the Python
code that indexes and queries it), `design-notes` (adopted architectural principles), and — new
— `matrices/latin-roots` (275 roots), `matrices/hebrew-glyphs` (all 22 glyphs), `matrices/algorithms`
(14 cataloged algorithms + 1 design-draft), and `indices/by-glyph` (three full, unreconciled
root-glyph assemblies transcribed from the-unicorn-estate's topology drafts). Everything else is
still an empty, labeled shelf waiting for its framework's turn.

## The Dual-Ordering structure

Two complementary navigation directions over the same underlying parts:

- **`/matrices`** — Matrices of Indices. Content-first: pick a matrix (a table of one kind of
  elemental part — Latin roots, Hebrew glyph opcodes, affixes, etc.) and index into its rows.
- **`/indices`** — Indices of Matrices. Lookup-first: pick a key (a glyph, a jurisdiction, a
  framework name, a source document) and find which matrix/matrices hold what you're looking
  for, before you ever get to row level.

Every elemental part should eventually be reachable both ways — by knowing which table it's
in, or by knowing something about it and needing to find the table.

- **`/libraries`** — actual importable Python code built from the matrices/indices. No longer
  entirely empty: `/libraries/eve` holds the working modules behind the populated shelves
  above (glyph indexing, word-sense disambiguation, the Mashet-dictionary entry generator).
- **`/design-notes`** — architectural design rationale that doesn't belong inside any one
  matrix or index, but that future matrices/indices/libraries are expected to follow.

## Shelf index

### /design-notes
- `heavens-earth-duality.md` — the adopted principle that a coordinate/addressing space is
  defined complete and unchanging from the start, while only its *occupancy* (which NVE sits
  where) starts empty and is populated progressively.

### /matrices
- `latin-roots/` — the classical Latin root base, **275 roots** populated. One row per root
  (`root`, `core_meaning`, `source_doc`) extracted verbatim from the-unicorn-estate's topology
  drafts; no glyph pairing baked in (that's an assembly — see `indices/by-glyph/`). See
  `matrices/latin-roots/roots.json`.
- `hebrew-glyphs/` — the 22-glyph ISA opcode table, **all 22 glyphs** populated (glyph, name,
  gematria, pictograph_meaning, proposed execution_role). See `matrices/hebrew-glyphs/glyphs.json`.
- `algorithms/` — a different kind of elemental part: distinct algorithms already implemented
  across the ecosystem's code (EBA memory regulation, the ISA-triplet execution pipeline, the
  five-tick causal wave, golden-angle placement, and more). **14 algorithms cataloged + 1
  design-draft** (a proposed self-referential dispatcher that decides which algorithm runs next).
  See `matrices/algorithms/algorithms.json`.
- `affixes/` — Latin prefix/suffix profiles (the kind an Indus Icon like the Unicorn carries). Shelf reserved, no data populated yet.
- `legal-maxims/` — classical Latin legal maxims (brocards) used as structural/operational logic references. Shelf reserved, no data populated yet.
- `evolution-constants/` — physics-layer coefficients (myelination, scar, resonance, hardening thresholds — from the eve3/MashetEVE evolution equation). Shelf reserved, no data populated yet.
- `indus-icons/` — agent definitions (Unicorn and future icons). Shelf reserved, no data populated yet.
- `english-lexicon-eve/` — the first populated matrix: a 48-word test lexicon (6 categories)
  used to run a controlled geometric-clustering test. See its README for the test and result.
- `mashet-dictionary/` — a constructed, neo-glyphic Hebrew dictionary migrated from the source
  Google Doc. 210 entries complete across 7 letters (Aleph–Zayin), Het in progress, 14 letter
  families still to come.

### /indices
- `by-glyph/` — reverse lookup: given a glyph, what references it. Now holds **three full,
  unreconciled root-glyph assemblies** transcribed from the-unicorn-estate's topology drafts
  (forced-even 22-glyph, curated 60-root shared-root set, and the full 275-root set), plus the
  original 4-entry bidirectional (glyph<->root+sense) proof-of-concept code demo.
- `by-jurisdiction/` — reverse lookup: given a jurisdiction/context, what belongs to it. Shelf reserved, no data populated yet.
- `by-framework/` — reverse lookup: given a framework name, what parts belong to it. Now notes
  which matrices/indices trace back to which framework.
- `by-source-document/` — reverse lookup: given a part, which RFC/doc/Drive file it originated from. Now notes
  the-unicorn-estate/topology source documents behind latin-roots, hebrew-glyphs, and by-glyph.
- `by-angle/` — the EVE layer's core operation: given a direction/coordinate from the shared
  (0,0,0) anchor, resolve which NVE occupies it.
- `by-is-a/` — taxonomic kind-relations between words (WordNet hypernym data), complementary
  to `by-angle`'s geometric relation, run against the `english-lexicon-eve` test set.

### /libraries
- `eve/` — importable Python modules backing the populated shelves above: bidirectional glyph
  indexing, the `by-is-a` taxonomy index, the discovers-meaning test, the `LexiconalEVE`
  lexicon/lookup implementation, a Mashet-dictionary entry generator (`generator/`), and a
  word-sense-disambiguation toolkit (`wsd/`).

## License

MIT — see [LICENSE](./LICENSE).
