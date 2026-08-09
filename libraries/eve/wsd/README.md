# Word Sense Disambiguation — Lin similarity

Real bug hunt across three architectures, all sharing one root cause: raw hypernym-overlap
COUNT over-rewards generic shared ancestry (two unrelated concrete objects both being "an
artifact" scores higher than a correct, specific match). Confirmed three separate times
(sequential, joint sentence-matrix, two-stage grammar) before being traced to the metric, not
to WordNet's underlying data — validated by testing Lin similarity (information-content based)
against the exact failing case: 0.621 vs 0.338, a decisive margin, versus raw overlap's wrong
6-vs-4 verdict and Wu-Palmer's fragile 0.02-margin partial fix.

## Status

- `sequential_wsd.py` — WORKING, validated with strong margins on real sentences
- `sentence_matrix.py` — WORKING for 2 simultaneous ambiguous words (bank+spring)
- `two_stage_grammar.py` — Stage 2 (verb resolution via derivational noun-bridge) WORKING.
  Stage 1 (noun designation) has an OPEN BUG: 3+ simultaneous ambiguous words can land on a
  wrong local optimum in the joint collapse even when the correct combination is available
  and scores lower than a spurious alternative. Not yet diagnosed.

## Architecture note

`two_stage_grammar.py` implements the ASL R-loci-inspired design: nouns are "designated" first
(jointly, isolated from verb noise), then verbs are resolved via WordNet's derivational
noun-bridge against the now-fixed nouns — mirroring how ASL verb movement is determined by the
spatial loci of already-established referents, not chosen independently.
