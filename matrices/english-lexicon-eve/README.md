# english-lexicon-eve

The first populated matrix — no longer an empty shelf. 48 words across 6 categories
(animal, emotion, motion, water, fire, time), each an NVE positioned via golden-angle
Fibonacci sphere placement, anchored to a shared (0,0,0).

**Status:** test data, not canon vocabulary. Built specifically to run a controlled test
(grouped-order vs. alphabetical-order insertion) rather than as a real lexicon yet.

**Result of that test:** grouped (semantically-ordered) insertion produced tighter angular
clustering than alphabetical (meaningless) insertion in 4 of 6 categories — not a clean sweep.
The golden angle's azimuthal spacing deliberately scatters consecutive insertion indices around
the sphere (that's what prevents banding/spiral artifacts), so naive "insert in meaningful order"
doesn't trivially guarantee tight clusters. See `/libraries/eve/lexicon_eve.py` for the runnable
test and full reasoning.

**Open next step:** a third condition — insertion order derived independently of category
(e.g. real semantic embedding distance) — to test whether categories cluster anyway, without
being told to. That's the actual test for "the lattice discovered meaning" vs. "the math did
what it was told."
