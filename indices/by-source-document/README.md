# by-source-document

Reverse lookup: given a part in this repo, which external RFC/doc/Drive file it originated
from. Not yet a general index over every populated matrix — populated so far only for the parts
brought in from a single external source this session.

## the-unicorn-estate/topology/*.md

Three sibling documents in `AGI144348Outlook/the-unicorn-estate`, under `topology/`, are the
source for several parts of this repo:

| Source document | What it fed into here |
|---|---|
| `topology/01-glyph-topology-draft.md` | `matrices/hebrew-glyphs/glyphs.json` (all 22 glyphs: pictograph, gematria, proposed execution role) and `indices/by-glyph/topology-v1-forced-even.md` |
| `topology/02-glyph-topology-v2-shared-roots.md` | `indices/by-glyph/topology-v2-shared-roots.md` |
| `topology/03-full-root-assignments-275.md` | `matrices/latin-roots/roots.json` (all 275 roots) and `indices/by-glyph/topology-v3-full-275.md` |
| `topology/README.md` | The "open questions before any of this goes into D1" section, copied verbatim into `indices/by-glyph/README.md` |

All three topology documents are themselves marked **draft, not yet reconciled** in
the-unicorn-estate — see `indices/by-glyph/README.md` for the open questions that follow from
that (which document is canonical, Resh as a semantic hub, the uneven glyph load). This repo
does not resolve those questions on the source repo's behalf; it preserves the disagreement
rather than picking a winner.

## Everything else

Every other populated matrix/index in this repo (mashet-dictionary, english-lexicon-eve,
by-angle, by-is-a, design-notes) has its provenance documented in its own README rather than
here — this index currently tracks only the-unicorn-estate topology imports. Extending it to
cover every matrix's source is future work.
