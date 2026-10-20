# EMEL v0: ECHO's expression language, audits and realizer

ECHO writes in EMEL. The parser builds a typed syntax tree; English is generated from the tree
by grammar rules and must parse back to the same tree (the grammar guide). Audits inform, never author.

    dog is_a canine                 relation        C-05.verdict = VALID        property (literal value)
    dog:canine::cat:feline          proportion      ל(dog)  %(dog)  GENERALIZE(dog, 3)   operators
    not ...   ... and ...   ... but ...                              word:dog glyph:ל result:C-05  qualified

Glyph meanings come from data/hebrew_glyph_registry.json (authoritative, algebra branch).
Multi-glyph strings are candidate composites; their constituents keep their registered meanings.

Audits: lexical, syntax, type (operator signatures), discourse ('but' must mark a contrast),
semantic (SUPPORTED / CONTRADICTED / UNKNOWN vs Registry, WordNet or result records),
provenance (the source of a supported claim), grammar (parse-back + known words).

Run: `PYTHONPATH=. python3 experiments/e5_echo_writes.py` and `experiments/e6_audit_faults.py`.
Verified in CPython 3.12 (with WordNet) and Pyodide 0.28.3 / Python 3.13 (offline, Registry only).

Not yet: content selection beyond result records, verb phrases other than is/includes,
tense and plural agreement, a sense-disambiguating resolver, multi-paragraph planning.

## The indexing formula, two ways in (same tree, same Governor)

    EMEL:    |{א:ב::ג:x}|                        Python:  G[א:ב, ג:x]
             |{(a<b):(c>d)::(e<d):(f>g)}|                 G[(a<b):(c>d), (e<d):(f>g)]
             |{P1}| :: |x| :: |{P2}|                      G[P[..], x, P[..]]
             nesting: |{ |{..}| :: |x| :: |{..}| }|        nesting: P[P[..], x, P[..]]
                                                          G[..] = "note"   STORE (retained candidate, never canonical)
                                                          del G[..]        DELETE

`gov_index.Governor` runs IDENTIFY -> VALIDATE -> OPEN over any matrix adapter that supplies an order
(for < > =) and a relation (for a:b). Offline adapters: Hebrew Glyph Registry, ECHO Registry, I Ching.
The Python form is parsed by Python, checked against a whitelist (no calls, attributes or dunders), and
never executed as arbitrary code. `orbit.spin` reports signed direction: the order of two inversions
decides forward or backward. Verified: E11, 9/9 identical trees and results, CPython and Pyodide 0.28.3.
