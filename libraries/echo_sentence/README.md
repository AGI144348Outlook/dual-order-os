# Echo grammar and recursive sentence integration

Migrated from Echo_Green_Future's early autonomous-agency implementation (September 23 introduction; source snapshot b164bb66850ee946a1b60c9e554172c7af2c639b).

Located components:
- A-144 PeComposer: base expression composer.
- HypernymGrammarModule: chain-derived sentence patterns, documented as A-144 augmentation/A-165 application.
- A-145 MirrorStep: processes expressed sentences again, finds vocabulary gaps, records homework and proposes VGM candidates.

These are source-extracted in legacy.py without changing their method bodies. PROVENANCE.json records source files, hashes and line ranges. No separately named RecursiveSentencing algorithm was confirmed in the examined branches; MirrorStep is the located recursive self-expression component, not proof that it is Timothy's exact intended algorithm. Existing dual-order-os WSD grammar modules are retained; they guide word-sense analysis, distinct from this output composition path.

runtime.py is a new integration adapter. GrammarGuide -> existing MirrorStep -> bounded return. Stable output stops repetition; a round budget caps execution. There is no automatic vocabulary acquisition or semantic validation inside this loop. Original legacy behavior is retained separately for comparison.

Migration corrections in GrammarGuide:
- Reject ambiguous words unless a specific WordNet sense is selected. A real test of heron otherwise selected Hero the mathematician.
- Keep cache entries separate by word, POS and selected sense.
- Correct reversed parent/child claims in legacy speak_chain: child is a kind of parent, not the reverse.
- Keep complete definitions instead of 70-character truncation.
- Unknown inputs return unresolved rather than asserting that an unknown entity exists.
- Dependency injection avoids import-time network downloads and hardcoded /home/claude paths.

This remains constrained lexical sentence construction, not a general English grammar checker or learned fluent articulation. MirrorStep's noun/verb checks do not establish factual truth. Four distinct definitions of one sense are a subsequent task; these components alone do not establish that capability.

Run tests from repository root:
python3 -m unittest libraries.echo_sentence.test_runtime -v

Real lexical usage (requires nltk and installed WordNet corpus):
from nltk.corpus import wordnet
from libraries.echo_sentence import GrammarGuide
print(GrammarGuide(wordnet, sense='heron.n.02').speak_chain('heron', depth=3))

Validation: 10 unit tests pass; real WordNet bird-sense smoke test passed and unresolved ambiguity check passed. No deployment or original-source deletion performed. Extraction migrates shared code without breaking Echo's existing monolithic source consumers.
