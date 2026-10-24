# The logic rules, written out

Each rule set from the [logics index](INDEX.tsv), read from its source and written out in plain words.
Where a source states a rule in its own words, the words are quoted. Symbols are kept exactly as typed.
Read on 2026-10-23 at the commits in the index.

## LOG-0001 · EMEL grammar

EMEL is "ECHO's expression language". A statement is built like this (from `echo/language/parser.py`):

```text
statement := clause (('and' | 'but') clause)*
clause    := 'not' clause | core
core      := bounded '::' bounded '::' bounded      continued proportion |P1| ::|x|:: |P2|
           | term ':' term '::' term ':' term       proportion
           | term RELATION term                     is_a | includes | antonym_of
           | term '.' ATTRIBUTE '=' value           property
           | call                                   operator application
call      := (NAME | GLYPH | '%') '(' term (',' term)* ')'
term      := call | QUALIFIED | NAME | GLYPH | GLYPH_STRING | NUMBER | STRING
```

In words:

1. A statement is one or more clauses joined by **and** or **but**.
2. Any clause can be negated with **not**.
3. A clause says one of five things: that one thing **is a** kind of, **includes**, or **is the opposite of** another; that a thing's **property** has a value; that **a is to b as c is to d**; that a middle term **x sits between two analogies**; or that an **operator is applied** to terms.
4. A term can be qualified to say which substrate it belongs to: `word:dog`, `glyph:ל`, `result:C-05`, and also `math:`, `formula:`, `relation:`, `resident:`, `echo:`.
5. "A token's canonical id comes from resolution, never its spelling." A bare name is looked up; its meaning never comes from how it is written.
6. Several Hebrew letters written together are a glyph string: "candidate composites; their constituents keep their registered meanings."

## LOG-0002 · English grammar guide

The guide reads Echo's English back into meaning. "If English(tree) parses back to the same tree, the sentence says exactly what the tree means." Anything outside these forms "is reported, not guessed". The sentence forms it accepts:

| English form | Meaning |
| --- | --- |
| X is (not) a Y | X is a kind of Y |
| X includes / does not include Y | X contains Y as a kind |
| X is (not) the opposite of Y | X and Y are antonyms |
| the A of X is (not) V · its A is (not) V | property A of X has value V (its = the thing already in focus) |
| A is (not) to B as C is to D | proportion A:B::C:D |
| X is (not) between the analogy P1 and the analogy P2 | continued proportion with X in the middle |
| X is (not) the level between the analogy P1 and the analogy P2 | the same, read as a pivot |
| the analogy P1 and the analogy P2 both / do not both fall under X | the same, read as a common category |
| the analogy P1 and the analogy P2 turn / do not turn on X in the same sense | the same, read as a hinge |
| as the analogy P1 is (not) to the analogy X, so that analogy is to P2 | a proportion of proportions |
| OP is applied to A, B | operator application |
| ל (DIRECT) | a glyph operator, named with its operation |
| the glyph string אב | a glyph string |

Clauses join with ", and" or ", but"; "it is not the case that" negates a whole joined statement or an operation.

## LOG-0003 · English realizer rules

The realizer writes English from meaning "by grammar rules over the tree, not by filling a fixed sentence":

1. **Articles.** "an" before a vowel sound, "a" otherwise. Exceptions: "a" before uni-, use-, usu-, uti-, one, eu-, ur- ("a unit", "a one"); "an" before hour, honest, honor, heir.
2. **Noun phrases.** A glyph operator is written with its operation, `ל (DIRECT)`; a glyph string as "the glyph string …"; records, numbers and text without an article; other words with "a" or "an".
3. **Pronouns.** A small memory holds the thing in focus. The second property of the same thing says "its …" instead of repeating "the … of …".
4. **Negation.** "is not", "does not include", "do not both fall under", "do not turn"; a negated operation or joined clause becomes "it is not the case that …".
5. **Coordination.** Two clauses join as "left, and right" or "left, but right".
6. **Sentence.** The first letter is capitalized and a full stop added.
7. **Same meaning, second surface.** Every tree can also be written in EMEL notation, e.g. `dog is_a canine`, `dog:canine::cat:feline`, `|P1| ::|x|:: |P2|`, `ל(dog)`.

## LOG-0004 · EMEL audits

"They inform ECHO; they never write his sentences." Seven checks:

| Audit | Passes when |
| --- | --- |
| lexical | every term resolves; unresolved terms are reported as gaps; glyph strings are split into their registered glyphs |
| syntax | the EMEL parse succeeded |
| type | operands match the operator and relation signatures (LOG-0005) |
| discourse | "but" marks a real contrast; "but" joining two equal values fails ("there is no contrast") |
| semantic | the claim is SUPPORTED, CONTRADICTED or UNKNOWN against the Registry, WordNet or result records |
| provenance | the source that supports a supported claim is named |
| grammar | the English parses back to the same tree, and every word is a known word |

How the semantic audit decides:

1. **X is a Y** is SUPPORTED when an is-a path runs from X up to Y (in the Registry, else WordNet), with its spectrum depth; CONTRADICTED when both are indexed but no path exists; UNKNOWN when a term is not indexed.
2. **X is the opposite of Y** is SUPPORTED when WordNet lists them as antonyms.
3. **A property** is checked against the result record: no record or no such field is UNKNOWN.
4. **A:B::C:D** is SUPPORTED when both pairs have the same relation at the same spectrum depth.
5. **|P1| ::|x|:: |P2|** is SUPPORTED only when all three analogies are supported, have the same relation type, are evenly stepped in depth (P1 → x → P2), are not flat, and x shares terms with both P1 and P2 ("so it bridges something").
6. **An operation** is "NOT_A_CLAIM": an operation, not an assertion.
7. **not** flips SUPPORTED and CONTRADICTED; **and** is CONTRADICTED if either side is, SUPPORTED only if both are.

## LOG-0005 · Operator and relation signatures

What each operator takes and gives:

| Operator | Takes | Gives |
| --- | --- | --- |
| GENERALIZE | a resident and a quantity | a set of residents |
| SPECIFY | a resident and a quantity | a set of residents |
| PRESENTIATE | a resident | a manifestation |
| % (inversion) | anything | "the kind it was given" |
| every glyph operation (INITIALIZE … SEAL) | anything | an operation |

| Relation | Joins |
| --- | --- |
| is_a | resident to resident |
| includes | resident to resident |
| antonym_of | resident to resident |

"Every token's meaning comes from a registry, never from its surface": glyphs from the Hebrew Glyph Registry, words from Echo's Registry (and WordNet when installed), records from experiment results.

## LOG-0006 · Indexing formula query language

```text
formula := bounded ( '::' bounded )*        consecutive triples are continued proportions
bounded := '|' '{' ( formula | prop ) '}' '|' | '|' prop '|' | '|' term '|'
prop    := slot ':' slot '::' slot ':' slot
slot    := '(' inner ')' | inner             inner := term ( ('<' | '>' | '=') term )?
term    := '?' | single-letter variable | word
```

In words:

1. A slot is either an **entry** (a word or a variable) or a **boolean** (a comparison between two, with <, > or =).
2. A proportion of entries holds when the relation between the first pair equals the relation between the second: rel(s1,s2) == rel(s3,s4), with the relation supplied by the matrix being searched.
3. A proportion of booleans holds when both sides make "the same change": (s1 XOR s2) == (s3 XOR s4).
4. `|P1| :: |x| :: |P2|` holds when P1 : x :: x : P2 on their signatures.
5. Mixing entries and booleans inside one proportion fails VALIDATE.
6. Example forms: `|{א:ב::ג:x}|`, `|{(a<b):(c>d)::(e<d):(f>g)}|`, `|{P1}| :: |x| :: |{P2}|`.

## LOG-0007 · Python-native formula form

The same formula written as Python, "parsed by Python itself", for the same Governor:

| Python | Formula | Meaning |
| --- | --- | --- |
| `G[a:b, c:d]` | a:b::c:d | look up a proportion |
| `G[(a<b):(c>d), (e<d):(f>g)]` | boolean proportion | the same change on both sides |
| `G[P[a:b, c:d], x, P[e:f, g:h]]` | \|P1\| :: \|x\| :: \|P2\| | P builds a proportion without running it |
| `G[...] = note` | STORE | "retain as a candidate (gated, never canonical)" |
| `del G[...]` | DELETE | "retract a retained candidate" |

Rules: single letters a to h and x are variables; `_` is an anonymous slot; other names are words, and Hebrew letters are legal names. Only these pieces of Python are allowed: expressions, subscripts, slices, tuples, names, comparisons (<, >, ==), constants, assignment and deletion. No calls, attributes or dunders. It "never runs code".

## LOG-0008 · LHEA letter operators

"The 22 letter operators as primitive transformation types":

| Letter | Operation | Letter | Operation |
| --- | --- | --- | --- |
| aleph | INITIALIZE | lamed | DIRECT |
| bet | CONTAIN | mem | FLOW |
| gimel | TRAVERSE | nun | INDIVIDUATE |
| dalet | FILTER | samekh | CYCLE |
| he | REVEAL | ayin | PERCEIVE |
| vav | CONNECT | pe | EXPRESS |
| zayin | TIMESTAMP | tsadi | HUNT |
| het | BOUND | qof | SCAN_PERIPHERY |
| tet | COIL | resh | GOVERN |
| yod | SEED | shin | TRANSFORM |
| kaf | CAPACITY | tav | SEAL |

How a Latin-script word becomes letters ("digraphs first; adjacent repeats collapse"):

- two-letter sounds first: sh → shin, ts → tsadi, th → tav, kh → het, ch → het
- then single letters: a → aleph, b → bet, v → vav, g → gimel, d → dalet, h → he, z → zayin, t → tet, y → yod, k → kaf, l → lamed, m → mem, n → nun, s → samekh, e → he, p → pe, f → pe, q → qof, r → resh, i → yod, o → ayin, u → vav
- the same letter twice in a row counts once; letters with no mapping (c, j, w, x) are skipped
- a word's gematria is the sum of its letters' values; its LHEA reading is its operations in order, e.g. INITIALIZE → CONTAIN → …
- two words balance at the highest-value letter they share (A-152 style equilibrium)

## LOG-0009 · Proportion forms

"A proportion holds under a relation R when R(a,b) == R(c,d) and is defined." For number proportions exactly eight arrangements stay true, "the ones that keep the extremes {a,d} and the means {b,c} as pairs":

| Form | Name |
| --- | --- |
| a:b::c:d | identity |
| c:d::a:b | symmetry |
| b:a::d:c | invertendo |
| d:c::b:a | inversion of both |
| a:c::b:d | alternando |
| c:a::d:b | (unnamed) |
| b:d::a:c | (unnamed) |
| d:b::c:a | (unnamed) |

"They form the symmetry group of a square (dihedral group of order 8), and every one of them is built from flips."

## LOG-0010 · DSL Registry seed

The 14 entries the canvas DSL starts with, as written:

| Symbol | Name | Meaning |
| --- | --- | --- |
| % | Inversion (alg-00%) | Step down: invert to an underside, an __init__, or a §Canvas. Enables Presentiation, not limited to it. |
| -% | Lift (alg-00%⁻¹) | Step back up one level; the presence rises at the next letter. |
| § | Presence (glove) | Infrastructural denotation of a presentiated occurring instance. Never a copy. |
| Presentiation | Presentiation | A higher-order instance: the very presence of the occurring instance, like fingers on a hand. |
| ↑ | Reach up | Read from the level above (e.g. the Matrix holding the Invariant). |
| ↓ | Reach down | Act on the level below. |
| → | Yields / applies to | Left side produces or is applied to the right side. |
| =T | True | A gate's condition holds. |
| =F | False | A gate's condition fails. |
| needs: | Logic line | What a node requires before it can act. |
| does: | Logic line | What a node does. |
| gives: | Logic line | What a node produces. |
| ר | Resh — Echo | 001, the Governor, the core formula. Echo is the presentiated 001. |
| alg- | Algorithm id | Prefix for registered algorithms, e.g. alg-003. |

The boot map in the same file adds: "%(DSL) = א-DSL: the DSL is presentiated at א".

## LOG-0011 · LRM inference rules

How the Logic Reasoning Matrix (A-146) derives theorems from axioms:

| Rule | From → to |
| --- | --- |
| SPECIALIZE | abstract term → specific subtype |
| COMPOSE | two axioms + shared term → theorem |
| APPLY_LAW | axiom + algebraic law → quantitative theorem |
| CAUSAL_CHAIN | cause → effect chain from two axioms |
| CONDITIONAL | if-then form derived from an axiom pair |

Every theorem records the statement, which axioms or laws it came from, which rule produced it, a coherence score and the vocabulary used.

## LOG-0012 · Valid department sequences

The part-of-speech sequences A-126 SyntacticalValidator accepts, "grammar before VGM":

| Sequence | As commented |
| --- | --- |
| noun, verb, noun | entity changes state |
| noun, verb | entity changes |
| noun, verb, adjective | entity becomes abstract |
| noun, adjective | entity is abstract (copula implied) |
| noun, verb, noun, noun | entity relates noun to noun |

When a check fails, the validator says which part failed and why, so the generator can revise it.

## LOG-0013 · Required operation order

What must run before what, checked by A-128 "before any dependent operation runs":

1. index_dictionary_entry before run_orientation
2. run_orientation before compute_generality_scores
3. run_orientation before run_typed_study_groups
4. compute_generality_scores before populate_generality_matrix
5. run_typed_study_groups before run_discovery

The rule came from a real bug: compute_generality_scores ran before run_orientation, "giving all agents tie_score=0".

## LOG-0014 · Agentive role patterns

A definition that contains any of these is read as naming an agent (a doer): "one who", "someone who", "a person who", "a being who", "any person", "those who", "he who", "she who", "an individual who", "one that".

## LOG-0015 · Grammar registry

"Grammar constrains linguistic construction; it does not select ECHO intent and never mutates word-only matrices."

- Input: lexical handles and candidate relations. Output: a grammatical candidate/constraint report.
- Expression gate: G::פ. Governor: G::ר.
- Seven classes of constraint are named: constituency, dependency, agreement, word order, tense and aspect, reference, subject/object role.
- No rules are written yet (status "working-empty-ruleset").

## LOG-0016 · Mashet universal rules

Governor G::ר. "Examples teach capability but do not prescribe ECHO's tool choice on novel tasks." The eight rules:

1. Resolve operands before manipulation.
2. Resolution does not imply authorization.
3. Preserve source objects unless mutation is explicitly authorized.
4. New constructions require identity and provenance.
5. Relations do not imply identity.
6. Results do not auto-retain or auto-validate.
7. Unresolved dependencies fail closed.
8. Log selection, operands, algebraic action, output, provenance, validation.

The operator cards they govern:

| Card | Symbol | Role | Formal | State |
| --- | --- | --- | --- | --- |
| M::SUN | ☉ | Internal Dynamics / Self-Evolution | ☉_k := ⊕(admitted operator contributions at k) | WORKING |
| M::INPUT | ⇢◇ | External Forcing / Inputs | ⇢◇ : U_k -> admitted(U_k) | WORKING |
| M::MEMORY | ∫↺ | Memory / History / Integral Accumulation | ∫↺ : S_<k -> H_k | WORKING |
| M::COUPLE | ⧖ | Coupling / Network Interactions | ⧖ : X × Y -> relation(X,Y) | WORKING |
| M::NOISE | ≋ | Noise / Stochasticity | ≋ : (X,xi) -> X' | WORKING |
| M::CONSTRAIN | ⌖ | Constraints / Stability | ⌖_C(X) -> X_C | WORKING |
| M::EVALUATE | ⚖ | Energy / Fitness / Optimization | ⚖_q : X -> assessment_q(X) | WORKING |
| M::DESCEND | ⤓ | Selection / Adaptation | (none yet) | UNRESOLVED_ALGEBRA |
| M::COMPOSE | ⊕ | Summation / Composition | ⊕ : X^n -> X' | WORKING |
| M::RECURSE | ⟲ | Recursion / Iteration | ⟲_f^n(x) = f^n(x) | WORKING |

## LOG-0018 · Legend v0.1 grammar

Timothy's bracket notation for tagging a sentence, innermost evaluated first:

| Slot | Role |
| --- | --- |
| `[•]` | Noun: a state (operator or operand) |
| `{•}` | Adjective: property of a state |
| `\|•\|` | Anchor: this/that, here/there, now; articles, possessives |
| `(•)` | Verb: an operation |
| `<•>` | Adverb: magnitude or effect of an operation |
| `<•)` | Fused: magnitude opening into an operation (left mark modifies, right mark is head) |
| `/•/` `\•\` | Preposition forward D.O→I.O / backward I.O←D.O |
| `>•<` | Interrogative, the empty slot (?); also opens a nested clause |
| `/•\` `\•/` | Pair: join (and) / split (or) |
| `}•{` | Relation: same, different, like, as, than |
| `]•[` | Absence: no, not, none, never |
| `)•(` | Turned operation: passive or reflexive |
| `⟨…⟩` | Nested clause, parsed one level deeper |
| `^x` | Glyph catch (superscript) |

Sentence patterns are spelled with: S subject, V operation, Vᵖ passive, O object, C complement, A adverbial, ∃ existential "there", Q question, ! imperative (no subject), ∅ fragment (no operation), ⟨⟩ nested clause.

"Overarching principle (Timothy): Generalization → Specification."

## LOG-0017 · Mashet Rule Registry snapshot, 2026-10-08

51 rules as stored on 2026-10-08, exactly as typed: 26 DECLARED, 24 PROPOSED, 1 RETIRED. DECLARED means Timothy stated it; PROPOSED rules are readings Claude offered that wait on him. The live registry (D1 `echo_knowledge`) may have moved on since.


Grouped by family, in the order stored. Each rule is shown in a text block so every symbol stays as typed.

### CONT

**R-CONT-1** · DECLARED · DECLARED

```text
A run of closers at a line's end, ")))", means "continues until the end", like "…" in text; it is not counted as unbalanced.

example: /(_),(_),(_),(_)→)))
```

### SEED

**R-SEED-1** · DECLARED · DECLARED

```text
||::|| is the Formula's seed.

example: ||::||
```

**R-SEED-2** · DECLARED · DECLARED

```text
The seed filled with י expands with open slots on both sides: |י|::|י|__(=)__\
__\→|__י__|::|__י__|←

example: |י|::|י| → |__י__|::|__י__|←
```

**R-SEED-3** · DECLARED · DECLARED

```text
With the letters dropped, the expansion runs ||_|...|←|_|::|→|[|]::[|]::[|]::++++→|_|| ; the [|] frames repeat (++++), three is the smallest case written, not a limit.

example: [|]::[|]::[|]::++++
```

### CON

**R-CON-1** · DECLARED · DECLARED

```text
[|] is the most generalized way to condense something to its most absolute Condensity. Expanding out is [||].

example: [|] condensed · [||] expanded
```

**R-CON-2** · DECLARED · DECLARED

```text
Condensation cycle as written: __\¹_ש←[|]→ש_\²_[|ש|]_\³_[|_|]__\=\¹←\³= ; /³={_(|ש←||):(|=||)_}=\⁴{|ש=←||} ; |:Continuum:: Algorithm:/⁴{|ש|}
```

**R-CON-3** · PROPOSED · INFERRED

```text
A slot [|_|] is what remains when a specific is lifted out; it can take any interchangeable filler.

example: [|ש|] → [|_|]
```

### GEN

**R-GEN-1** · DECLARED · DECLARED

```text
#, |#| and x are used interchangeably for the same thing: the meta-specification, as a counter to biasing impositions, enables semantic interchangeability (interchangeability in general), which is the difference between Specifications and Generalizations.

example: x ↔ |#| ↔ #
```

**R-GEN-2** · PROPOSED · INFERRED

```text
A specification fills a slot; it is recorded as a declaration and can be undone. A generalization keeps the slot open.
```

### STRATA

**R-STRATA-1** · DECLARED · DECLARED

```text
The Suprastrate and the Substrate are connected at the IETF (0,0,0) and the Relational Formula's |x|, as an agentically employable Harness wrapped around the Datastrate.
```

### SPEC

**R-SPEC-1** · DECLARED · DECLARED

```text
The parsing framework accounts for the whole spectrum: from data in a language whose semantic mechanics are already understood, to an undeciphered language like the IVS, or one met on another planet.
```

**R-SPEC-2** · PROPOSED · INFERRED

```text
The pipeline stays the same at every point on the spectrum; only the declarations change.
```

**R-SPEC-3** · PROPOSED · INFERRED

```text
At the undeciphered end, segmentation and reading direction are hypotheses, never inputs; "one symbol" is first a candidate in Registry −0.
```

### GOV

**R-GOV-1** · DECLARED · DECLARED

```text
Governor/Auditor formula (revision in progress): [_{(?):(?)}::{(?):(?)}_]א_|ת→א|י|::|י|א←ת|_א[_{(?):(?)}::{(?):(?)}_] ; kernel ]א_|ת→א|י|::|י|א←ת|_א[ is the Formula's (0,0,0) in practicality; [_{(?):(?)}::{(?):(?)}_]__(=)__[|] ; |'||::||'|←__(=)__|[א]::[|]::[|]::[|]::←[ת]|ת|| ; bounded at the ends with ||ת|→
```

**R-GOV-2** · DECLARED · DECLARED

```text
(?) can = (?±?) where [±] = {<,>,=,}

example: (a<b)
```

**R-GOV-3** · RETIRED · INFERRED

```text
Each [|] in an expansion is one full frame of 4 comparisons.
```

**R-GOV-4** · PROPOSED · INFERRED

```text
The kernel is mirror-symmetric around :: (element order reversed, arrow direction kept: ת→א on the left, א←ת on the right).
```

**R-GOV-5** · PROPOSED · INFERRED

```text
Removing every letter from the kernel leaves the seed ||::||.
```

**R-GOV-6** · PROPOSED · INFERRED

```text
The empty fourth member of {<,>,=,} is the "not compared / open" relation (written 0 by GPT).
```

### ROLE

**R-ROLE-1** · DECLARED · DECLARED

```text
IVS ≈ [Nouns]:{people,places,things}
```

**R-ROLE-2** · DECLARED · DECLARED

```text
Hebrew ≈ (verbs
```

**R-ROLE-3** · DECLARED · DECLARED

```text
Latin ≈ {Logic} profiles__/ __/({•})=(•)←{•,•,•}→[•]=[{•}]
```

**R-ROLE-4** · DECLARED · DECLARED

```text
Chinese Cuneiform ≈ |__[(ש)←{Words}→(ש)]__(=)__{•}__| (whether one role or split into whole-word signs and component signs is open)
```

**R-ROLE-5** · DECLARED · DECLARED

```text
English: English/{•}←[|]→{•}\Cuniform
```

**R-ROLE-6** · DECLARED · DECLARED

```text
English Dictionary: §•~§•~§•~§•~§• Hypernyming Laterally and Vertically
```

**R-ROLE-7** · DECLARED · DECLARED

```text
[I-Ching] ≈ Ordering {∆} and Syntaxing {¥}
```

**R-ROLE-8** · DECLARED · DECLARED

```text
|[{(|)}]| for Structuring
```

**R-ROLE-9** · DECLARED · DECLARED

```text
__|[{(|)}]|_/_{•}←[|]→{•}_/_[{¥}+{∆}
```

**R-ROLE-10** · DECLARED · DECLARED

```text
Punctuation ≈ Compiling (•)ⁿ→{•:•::•:•}←[•]ⁿ ; Hypernyming §•~§•~§•;
```

**R-ROLE-11** · DECLARED · DECLARED

```text
Numerators = Math/Science
```

**R-ROLE-12** · DECLARED · DECLARED

```text
Continuum ≈ Algorithms ; (ש|ש) = |ש| = ||
```

**R-ROLE-13** · DECLARED · DECLARED

```text
96 ≈ the neurons and their neuroplasticity: even the physically hard constraint of the skull still allows an exponential set of possible arrangements amongst a finite limitation.
```

**R-ROLE-14** · DECLARED · DECLARED

```text
Developing Notation ≈ Generalization: __/t⁰/__{•}__/¹.|(ש)→{•}←(ש)__/²{
__\²{ש}←[•]__\³{_}__\⁴__{_}→(ש)→[•ⁿ]__\⁵{
__\⁵{ש}__\⁶{•ⁿ}.|__
```

**R-ROLE-15** · DECLARED · DECLARED

```text
Slot 9 is left open: the place an undeciphered script lands.
```

**R-ROLE-16** · PROPOSED · INFERRED

```text
A system's role is a declaration and removable; underneath it, role-like behaviour is still measured.

example: IVS as nouns stays declared until its signs show noun-like positions in scans
```

**R-ROLE-17** · PROPOSED · INFERRED

```text
An unknown script gets no roles; each role is a hypothesis it must earn.
```

### NEU

**R-NEU-1** · PROPOSED · INFERRED

```text
The 96 are fixed; their relations are plastic.
```

**R-NEU-2** · PROPOSED · INFERRED

```text
An IETF node holds one arrangement of the 96 (who relates to whom, and how), not a new symbol.
```

### DET

**R-DET-1** · PROPOSED · DECLARED

```text
I-Ching as determinatives (proposed by Timothy, under consideration).
```

**R-DET-2** · PROPOSED · INFERRED

```text
A determinative is silent: it marks a sign's category but is not read as a word.

example: ☲ before a Hebrew root marks its category, adding no letter
```

**R-DET-3** · PROPOSED · INFERRED

```text
Trigram = simple category (8); hexagram = inner category under outer category (64).
```

**R-DET-4** · PROPOSED · INFERRED

```text
∆ on a determinative = one line flipped = a category moving one step.
```

**R-DET-5** · PROPOSED · INFERRED

```text
Determinative category contents start empty; traditional trigram associations are declarations, removable.
```

### REG

**R-REG-1** · PROPOSED · INFERRED

```text
Every registry entry gets an ID that never changes or is reused.

example: ⧫ is two entries, MS-025 and MS-059
```

**R-REG-2** · PROPOSED · INFERRED

```text
The registry is the source of truth; entries are added, never overwritten.
```

### MAT

**R-MAT-1** · PROPOSED · INFERRED

```text
A matrix's axes may only use registry IDs; an unregistered symbol goes to Registry −0 first.
```

**R-MAT-2** · PROPOSED · INFERRED

```text
Each matrix cell records its count and the scan run it came from.

example: [⊕,⧖] = 14, run 7
```

**R-MAT-3** · PROPOSED · INFERRED

```text
A matrix is derived: delete it, rescan, and you get it back; a registry cannot be rebuilt that way.
```

### IVS

**R-IVS-1** · PROPOSED · INFERRED

```text
Every position and pair names its order: listed (as stored, left to right in the mayig corpus) or read (right to left).

example: pair P122→P385 listed = P385→P122 read
```

**R-IVS-2** · PROPOSED · INFERRED

```text
A sign with nonzero damage or uncertainty is registered but flagged; pairs touching it are counted separately from clean pairs.
```

### BD

**R-BD-1** · PROPOSED · INFERRED

```text
Every stored line has two readings: logical order (authoritative) and visual order (derived, recomputed on each keystroke, never written back).

example: typed [ש..... stays [ש..... in storage
```
