# algorithms

A **Matrix of Indices** over a different kind of elemental part than the other matrices: not a
root, a glyph, or a dictionary entry, but a distinct *algorithm* already implemented somewhere
in the ecosystem (or, for exactly one row, proposed but not yet built). The point is the same
as everywhere else in dual-order-os — break each framework's code down into its elemental,
reusable pieces so they can be indexed, compared, and eventually recombined, instead of staying
locked inside one framework's source file where nothing else can reference them.

This directly serves the idea the user raised: an algorithm matrix that keeps track of every
algorithm an algorithmic index would use — including, as its own row, the algorithm that
decides which algorithm runs next.

## Data

`algorithms.json` — a flat JSON array, **15 rows**: **14 real algorithms**, read out of actual
committed code across four repositories, plus **exactly 1 design-draft row**
(`sequential-agency-dispatcher`) that is explicitly *not* extracted from existing code — its
`status` field says so, and it's called out separately below.

Fields per row: `id`, `name`, `category`, `summary`, `inputs`, `outputs`, `triggers` (other
algorithm ids this one calls, where determinable from the code), `triggered_by` (the reverse),
and `source` (`repo`, `path`, `function_or_class`). `triggers`/`triggered_by` are left as empty
arrays wherever the code doesn't establish a direct algorithm-to-algorithm call — most rows here
are invoked from an HTTP route or another script, not from another cataloged algorithm, and
that's recorded honestly rather than guessed at.

## The 14 real algorithms

| id | Category | What it does | Source |
|---|---|---|---|
| `eba-memory-shedding-damping-ejection` | memory-management | Eigenvalue-based damping/shedding/ejection of TEMA Core context droplets | `Lhea-Tema/lhea-tema-kernel.js` — `runEBAInternal` |
| `isa-triplet-execution-pipeline` | execution | 7-phase pipeline executing a (root, glyph, icon) triplet | `Lhea-Tema/lhea-tema-kernel.js` — `executeISATriplet` |
| `root-myelination-hardening` | placement | Increments myelination count, hardens a root into a CORE_NODE at the threshold | `Lhea-Tema/lhea-tema-kernel.js` — `executeISATriplet` (Phase 7) |
| `ocean-circulation-cave-precipitation` | memory-management | Circulates OCEAN droplets, precipitates long-lived ones into permanent CAVE stalactites | `Lhea-Tema/lhea-tema-kernel.js` — `getTEMAOcean` |
| `jurisdiction-emergence-detection` | sequencing | Detects whether >= 3 root nodes cohere into a valid emergent jurisdiction | `Lhea-Tema/lhea-tema-kernel.js` — `checkJurisdiction` |
| `five-tick-causal-wave-pipeline` | execution | Runs a symbolic expression through 5 execution ticks against a jurisdiction | `echo-prototype/src/runtime/five-tick-engine.js` — `runFiveTick` |
| `supernova-compiler-reconciliation` | execution | Checks an operator's semantic character against a jurisdiction's forbids | `echo-prototype/src/runtime/five-tick-engine.js` — `reconcile` |
| `golden-angle-sphere-placement` | placement | Places a word/entity on the unit sphere via the golden-angle Fibonacci spiral | `dual-order-os/libraries/eve/lexicon_eve.py` — `NVE.place` |
| `eve-angular-nearest-neighbor-lookup` | lookup | Resolves a direction to its k nearest occupying word(s) | `dual-order-os/libraries/eve/lexicon_eve.py` — `LexiconalEVE.nearest` |
| `category-tightness-clustering-metric` | evaluation | Average pairwise angular distance within a category, for cluster-tightness comparison | `dual-order-os/libraries/eve/lexicon_eve.py` — `LexiconalEVE.category_tightness` |
| `bidirectional-glyph-root-index` | lookup | Both-directions (root,sense)<->glyph index, keyed on sense to avoid ambiguous-root collisions | `dual-order-os/libraries/eve/bidirectional_glyph_index.py` — `BidirectionalGlyphRootIndex` |
| `by-is-a-taxonomic-index-builder` | lookup | Builds WordNet hypernym (is-a) ancestry chains per word, with manual sense overrides | `dual-order-os/libraries/eve/by_is_a_index.py` — `build_is_a_index` |
| `deepest-common-ancestor-finder` | evaluation | Finds how deep a set of is-a chains share a common ancestor | `dual-order-os/libraries/eve/by_is_a_index.py` — `find_deepest_common_ancestor` |
| `wordnet-greedy-nn-ordering` | sequencing | Builds an insertion order via greedy nearest-neighbor walk through WordNet similarity | `dual-order-os/libraries/eve/discovers_meaning_test.py` — `build_wordnet_order` |

`the-unicorn-estate/runtime/worker.js` was also read for this matrix and contributed no
additional row: it's explicitly a data-layer-only endpoint ("no execution/propagation logic
yet — RFC-0007 not implemented"), serving reads over `/roots`, `/glyphs`, and a static
`/genesis` stage description with no algorithm of its own.

## The 1 design-draft row: `sequential-agency-dispatcher`

**This one is not extracted from existing code anywhere — it does not exist yet.** It's a
design proposal responding directly to the user's stated idea: an algorithm matrix should be
able to track "the algorithm of itself for triggering sequential algorithms of agency." The row
models a meta-algorithm that would decide which of the 14 real algorithms above runs next,
given the current state and the previous algorithm's output — and it lists itself in its own
`triggers` array, since after it runs, it (or its logical successor) would run again to pick
the *next* next step. Its `status` field says `"design-draft — not yet implemented anywhere"`
so this can never be mistaken for a description of real running behavior. Building it is future
work, awaiting review, not something this repo currently does.
