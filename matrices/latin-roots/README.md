# latin-roots

The atomic Latin-root inventory — a **Matrix of Indices**: one table, one row per root, no
glyph pairing baked in. This is the content-first shelf; if you already know a root and want
its glyph assignment(s), that's an assembly and lives in `/indices/by-glyph/` instead (three
separate, unreconciled assemblies — see that index's README for why there are three).

## Data

`roots.json` — a flat JSON array, **275 roots**, one object per row:

```json
{
  "root": "Fluere",
  "core_meaning": "flow",
  "source_doc": "the-unicorn-estate/topology/03-full-root-assignments-275.md"
}
```

- `root` — the Latin root/word as it appears in the source document.
- `core_meaning` — the gloss given alongside it in the source.
- `source_doc` — always the same value here, kept per-row so a row is self-describing if it's
  ever exported or joined elsewhere.

No `semantic_vector` or category field is included: the source document (file 3, the full
275-root pass) doesn't carry one per root — only a root/meaning/glyphs table. Nothing has been
invented to fill that gap.

## Provenance

Extracted verbatim (mechanically parsed, not retyped) from
[`the-unicorn-estate/topology/03-full-root-assignments-275.md`](https://github.com/AGI144348Outlook/the-unicorn-estate/blob/main/topology/03-full-root-assignments-275.md) —
the fullest of that repo's three topology drafts, assigning the *entire* classical Latin base
(as opposed to the smaller curated sets in drafts 1 and 2). That source document is itself
still marked **draft, not yet reconciled** against the other two topology files — see
`/indices/by-glyph/README.md` for the open questions that follow from that.
