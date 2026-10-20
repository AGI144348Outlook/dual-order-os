# Integrated Echo workspace — integration branch

This branch combines the preserved Genesis Documentary snapshot with Dual Order OS's catalog and a new tested adapter. **Complete source copy: 128 files verified. Tests: 27 Python + 62 archived cabinet tests passed.** Two original Genesis programs completed; five historical runs remain blocked by missing corpus data. Known Genesis validation/reasoning limitations remain recorded.

- [Start here: component and usage guide](components/echo-integration/README.md)
- [Complete preserved Genesis snapshot](vendor/echo-genesis/)
- [Combined results](reports/echo-integration/results.json) and [restored-workspace demonstration](reports/echo-integration/demo.json)
- [Integration Matrix](matrices/echo-integration/) and [progression report](research/progression/007-unified-echo-integration.md)

Run locally in Python: `python -m libraries.echo_demo`. No model API, training or cloud deployment is required. There is no newly hosted Canvas UI. This work is isolated on `integration/echo-genesis-unified`; the source Genesis branch and Dual Order main remain unchanged by this integration.

The original project overview below predates later populated libraries and matrices; its “empty shelves” statements are historical and are superseded by the live component catalog and integration results above.

---

# dual-order-os

Shared infrastructure for every framework (Mashet, LHEA, eve3/MashetEVE, JurisDictionary, and
whatever comes next) — built on the idea that breaking each framework down into elemental,
reusable parts lets those parts be recombined modularly into new models later, instead of
re-authoring the same kind of infrastructure from scratch each time.

**Status: empty, marked shelves.** This is the library shelving, not the books yet — folder
structure and labels only, no data populated. Content gets added deliberately, framework by
framework, once you're ready.

## The Dual-Ordering structure

Two complementary navigation directions over the same underlying parts:

- **`/matrices`** — Matrices of Indices. Content-first: pick a matrix (a table of one kind of
  elemental part — Latin roots, Hebrew glyph opcodes, affixes, etc.) and index into its rows.
- **`/indices`** — Indices of Matrices. Lookup-first: pick a key (a glyph, a jurisdiction, a
  framework name, a source document) and find which matrix/matrices hold what you're looking
  for, before you ever get to row level.

Every elemental part should eventually be reachable both ways — by knowing which table it's
in, or by knowing something about it and needing to find the table.

- **`/libraries`** — actual importable Python code built from the matrices/indices, once
  they're populated. Empty for now.

## Shelf index

### /matrices
- `latin-roots/` — the classical Latin root base (275 roots drafted so far)
- `hebrew-glyphs/` — the 22-glyph ISA opcode table
- `affixes/` — Latin prefix/suffix profiles (the kind an Indus Icon like the Unicorn carries)
- `legal-maxims/` — classical Latin legal maxims (brocards) used as structural/operational logic references
- `evolution-constants/` — physics-layer coefficients (myelination, scar, resonance, hardening thresholds — from the eve3/MashetEVE evolution equation)
- `indus-icons/` — agent definitions (Unicorn and future icons)

### /indices
- `by-glyph/` — reverse lookup: given a glyph, what references it
- `by-jurisdiction/` — reverse lookup: given a jurisdiction/context, what belongs to it
- `by-framework/` — reverse lookup: given a framework name, what parts belong to it
- `by-source-document/` — reverse lookup: given a part, which RFC/doc/Drive file it originated from

### /libraries
Empty. Reserved for compiled, importable Python modules built from the matrices/indices above.
