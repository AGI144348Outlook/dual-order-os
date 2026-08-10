# Mashet Code Generator

Implements the generative pipeline from "Mashet as Operational Practice": concept description
-> required substrates -> candidate letters -> optimal coverage -> constructed word ->
executable function. Self-contained, standard-library only — runs directly in Pydroid3, no
dependencies.

LETTER_SUBSTRATES drawn from this session's actual dictionary work (210 Aleph-Zayin entries +
10 Het entries) and the earlier ISA opcode table, not invented fresh for this generator.

## Two real bugs found and fixed before this was trustworthy enough to ship

1. **Substring over-matching:** original concept-analysis used loose substring containment
   ('a' in 'matrix' → True), which matched 66 substrates from a 14-word sentence. Fixed with
   stopword filtering + exact/stemmed matching.
2. **Under-stemming:** naive single-suffix stripping turned "perceives" into "perceiv", which
   didn't match the tag "perceive" — silently dropping perception from a concept that was
   centrally about perceiving a threat. Fixed by checking multiple stem variants per word.

## Validated test result

Concept: "A mechanism that perceives an external threat and seals the boundary permanently in
response" → 6 substrates matched cleanly (boundary, external, perceive, response, seal,
threat), each traceable to a specific word → גזחערת (Gazache'oret): Gimel(external) +
Zayin(threat) + Het(boundary) + Ayin(perceive) + Resh(response) + Tav(seal).

## Honest limitation

Does NOT verify constructed words against real Hebrew vocabulary — same caveat as the
hand-authored dictionary entries. Designed to be unlikely to collide with real words, not
verified not to.
