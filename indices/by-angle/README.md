# by-angle

The EVE layer's actual job: given a direction (angle/coordinate) from the shared (0,0,0)
anchor, resolve which NVE occupies it. This is the Index-of-Matrices operation for any EVE —
lookup-first, not content-first.

Implemented as `LexiconalEVE.nearest(x, y, z, k)` in `/libraries/eve/lexicon_eve.py`.
