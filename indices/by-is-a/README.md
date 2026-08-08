# by-is-a

A relationship BETWEEN words (taxonomic kind-relations), not content a word holds — so this
lives in /indices, separate from and complementary to /indices/by-angle (geometric position).
Built from real WordNet hypernym data for the 48-word test lexicon in
`/matrices/english-lexicon-eve`.

## Result

| Category | Shared ancestry depth | Deepest common ancestor |
|---|---|---|
| animal | 6 | organism |
| emotion | 3 | attribute |
| motion | 1 | entity |
| water | 1 | entity |
| fire | 1 | entity |
| time | 1 | entity |

Animal is a genuine, deep taxonomic kind. Emotion is real but shallow (shares "feeling," not
much else). Motion/water/fire/time bottom out at "entity" — no real taxonomic kinship, likely
because several of those words are verb-derived nominalizations rather than natural noun kinds.

**This is the honest complement to `/indices/by-angle`'s discovers-meaning test:** animal
clustered tightly under BOTH mechanisms (geometry and taxonomy). Emotion failed under both,
for a real, structural reason — affective similarity isn't a kind-relation, so is-a can't
capture it no matter how the math is tuned, and geometric ordering alone couldn't either.

## Three bugs found and fixed while building this — worth knowing before trusting the numbers

1. **spring** defaulted to WordNet's first sense (the season) instead of the water-source
   sense — sense ambiguity. Fixed via explicit synset pin.
2. **otter** defaulted to "otter fur" (a material) instead of the animal — same failure mode,
   second instance. Fixed via explicit synset pin.
3. **kindle** has no noun sense in WordNet at all — its default sense is the verb "to catch
   fire." Including it compared a verb's hypernym chain (a completely separate taxonomy with
   no "entity" root) against seven nouns' chains — a category error, not a distance
   measurement. Fixed by restricting lookups to noun senses only, excluding words with none.

Code: `/libraries/eve/by_is_a_index.py`, `/libraries/eve/discovers_meaning_test.py`
