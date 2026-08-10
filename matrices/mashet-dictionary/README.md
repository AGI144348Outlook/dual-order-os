# Mashet Dictionary/Library

Migrated from Google Drive (source doc: "משת Dictionary/Library"), since that doc can only be
read, not edited, from here — everything going forward lives in GitHub instead so nothing stays
trapped in a document this repo can't write to.

## Constraint (intentional, carried over from the source)

Every entry is a constructed, **neo-glyphic** combination — never an existing Hebrew word.
This is deliberate: reusing a real word would import pre-loaded meaning/connotation from
outside the system. Each entry has to derive its meaning purely from its constituent letters'
established operator-roles within this dictionary, one glyph at a time.

## Status

| Letter | File | Status |
|---|---|---|
| א Aleph | 01-aleph.md | Complete — 30 entries |
| ב Bet | 02-bet.md | Complete — 30 entries |
| ג Gimel | 03-gimel.md | Complete — 30 entries |
| ד Dalet | 04-dalet.md | Complete — 30 entries |
| ה He | 05-he.md | Complete — 30 entries |
| ו Vav | 06-vav.md | Complete — 30 entries |
| ז Zayin | 07-zayin.md | Complete — 30 entries |
| ח Het | 08-het.md | **In progress — 5 of 30 entries** |
| ט Tet – ת Tav | 09–22 | Empty, not yet drafted |

210 entries complete (Aleph–Zayin), 5 new entries drafted for Het, 25 more needed to reach
parity with the completed families, then 14 more letter families after that.

## Format (settled convention, as of the Het entries)

Each entry: Hebrew neo-word + transliteration, Functional Translation, Structural Logic
(letter-by-letter derivation), State Shift (continuous per-letter-family count — resets to S_0
at the start of each letter, then increments straight through all 30 entries rather than
resetting per entry), Depth & Application, Signal (a sensory/visual description of the
operation).

## Relevance beyond vocabulary

This directly answers a composition-grammar question left open earlier in the LHEA work
(RFC-0013, Hebrew Execution Calculus): whether multi-letter glyph strings should be read as
operator-instructions or as result-states. These entries demonstrate glyph strings as
**sequential derivation chains** — each letter transforming the state left by the one before
it, with the transition tracked explicitly via the State Shift notation. This is also the
concrete target for eve3's generative capability: given a target meaning, eve3 should
eventually be able to construct an entry like these itself, rather than only executing
pre-authored strings.
