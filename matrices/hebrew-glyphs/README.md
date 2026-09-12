# hebrew-glyphs

The atomic Hebrew-glyph inventory — a **Matrix of Indices**: one table, one row per glyph,
**22 glyphs** total (the full paleo-Hebrew alphabet). This is the content-first shelf; root
pairings and the three alternate topology assemblies built on top of this table live in
`/indices/by-glyph/`, not here.

## Data

`glyphs.json` — a flat JSON array, 22 objects, one per glyph, in alphabet order:

```json
{
  "glyph": "א",
  "name": "Aleph",
  "gematria": 1,
  "pictograph_meaning": "Ox, strength, leader",
  "execution_role": "Initiation/origination primitive — the glyph that begins an execution chain or asserts primacy within a jurisdiction (pairs naturally with RFC-0002's \"Jurisdiction\" concept as the entity that opens one).",
  "source_doc": "the-unicorn-estate/topology/01-glyph-topology-draft.md"
}
```

- `glyph` — the Hebrew character.
- `name` — standard transliteration.
- `gematria` — the letter's standard numeric value (Aleph=1 ... Tav=400). Included because it's
  an inherent property of the letter, not because any current execution logic uses it — the
  source document is explicit that gematria isn't wired into the proposed execution roles yet.
- `pictograph_meaning` — the traditional paleo-Hebrew concrete meaning, which is the organizing
  **anchor** for the whole pairing method used across this repo and the-unicorn-estate's
  topology drafts. (The user has confirmed pictograph-as-anchor is the correct organizing
  principle — see `/indices/by-glyph/README.md`.)
- `execution_role` — the *proposed* symbolic/execution role for the glyph, as drafted in the
  source. This is explicitly marked in the source as a hypothesis, not a settled answer — kept
  verbatim rather than smoothed over into something more certain-sounding.

## Provenance

Extracted verbatim (mechanically parsed, not retyped) from
[`the-unicorn-estate/topology/01-glyph-topology-draft.md`](https://github.com/AGI144348Outlook/the-unicorn-estate/blob/main/topology/01-glyph-topology-draft.md) —
the first-pass draft that establishes all 22 glyphs with pictograph, gematria, and a proposed
execution role, before any Latin-root clustering decisions were layered on top (those clustering
decisions are what varies across the three `indices/by-glyph/` assemblies).
