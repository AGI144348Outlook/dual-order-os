# Topology v3 — Full 275-Root Assignment

**Assembly, not canon.** One of three unreconciled root-glyph assemblies over the same
underlying matrices — see `../README.md` for why all three are kept side by side rather than
picking one. This file transcribes
`the-unicorn-estate/topology/03-full-root-assignments-275.md`, the largest-scope draft: it
assigns the **entire classical Latin root base extracted into `matrices/latin-roots/roots.json`
(275 roots)**, each to **2 glyphs** (occasionally a root could arguably span a 3rd, but the
source deliberately kept every row at exactly 2 to stay legible). Root text below matches
`matrices/latin-roots/roots.json`'s `root` field exactly, so the two can be joined directly
(unlike v1/v2, which use classical stem-dash forms from an older source). Glyph names match
`matrices/hebrew-glyphs/glyphs.json`'s `name` field.

## Glyph load is uneven by design

Out of 275 roots × 2 assignments = 550 total slots, per-glyph load is far from even:

| Glyph | Root count |
|---|---|
| Aleph | 28 |
| Bet | 44 |
| Gimel | 21 |
| Dalet | 8 |
| Hey | 49 |
| Vav | 28 |
| Zayin | 22 |
| Het | 33 |
| Tet | 22 |
| Yod | 23 |
| Kaf | 17 |
| Lamed | 19 |
| Mem | 19 |
| Nun | 38 |
| Samekh | 32 |
| Ayin | 20 |
| Pey | 15 |
| Tsade | 11 |
| Qof | 36 |
| Resh | 18 |
| Shin | 19 |
| Tav | 28 |
| **Total slots** | **550** |

**Heaviest:** Hey (49 roots), Bet (44), Nun (38), Qof (36), Het (33), Samekh (32) — pictographs
(window/perception, house/containment, life, time/cycle, boundary, support) broad enough to
attract a wide swath of vocabulary.
**Lightest:** Dalet (8), Tsade (11), Pey (15) — narrower, more specific concepts (threshold,
pursuit, speech) that fewer roots naturally connect to.

The source document is explicit that this 49-vs-8 imbalance is **flagged, not resolved** — see
`../README.md`'s open questions; this is one of the points the user has not yet weighed in on
(unlike pictograph-as-anchor, which is now confirmed correct — see that README).

## Full root → glyph assignments (275 roots)

Every root below is a row in `matrices/latin-roots/roots.json`; its `core_meaning` lives there,
not repeated here, to avoid two sources of truth for the same fact.

| Root (see `matrices/latin-roots/roots.json`) | Assigned Glyphs (see `matrices/hebrew-glyphs/glyphs.json`) |
|---|---|
| Acer | Zayin, Shin |
| Aev | Qof, Nun |
| Ager | Het, Bet |
| Agmen | Mem, Gimel |
| Altus | Resh, Qof |
| Amare | Vav, Bet |
| Anima | Hey, Nun |
| Annus | Qof, Samekh |
| Aqua | Mem, Nun |
| Arbor | Nun, Tet |
| Audire | Hey, Ayin |
| Avis | Gimel, Hey |
| Bellum | Zayin, Shin |
| Bonus | Tsade, Tav |
| Brevis | Zayin, Het |
| Caput | Resh, Aleph |
| Carbo | Shin, Tet |
| Caro | Bet, Nun |
| Cavus | Bet, Tet |
| Cedere | Gimel, Samekh |
| Cera | Tav, Tet |
| Cilium | Ayin, Hey |
| Civis | Bet, Lamed |
| Clarus | Hey, Ayin |
| Cor | Nun, Hey |
| Corpus | Bet, Nun |
| Credere | Ayin, Tav |
| Crux | Tav, Vav |
| Culpa | Shin, Tsade |
| Cura | Samekh, Lamed |
| Cursus | Gimel, Qof |
| Dens | Shin, Zayin |
| Deus | Aleph, Resh |
| Dexter | Yod, Kaf |
| Dignus | Tsade, Tav |
| Dominus | Aleph, Lamed |
| Domus | Bet, Het |
| Donum | Yod, Vav |
| Dormire | Samekh, Hey |
| Ductus | Aleph, Lamed |
| Durus | Het, Aleph |
| Ego | Resh, Aleph |
| Equus | Gimel, Vav |
| Errare | Gimel, Samekh |
| Faber | Yod, Lamed |
| Facere | Yod, Tav |
| Fama | Pey, Hey |
| Femina | Bet, Nun |
| Ferrum | Zayin, Het |
| Fides | Tav, Vav |
| Finis | Tav, Dalet |
| Flamma | Shin, Pey |
| Flos | Nun, Hey |
| Fluere | Mem, Gimel |
| Folium | Nun, Tet |
| Forma | Tet, Bet |
| Frater | Bet, Vav |
| Frons | Resh, Aleph |
| Fructus | Nun, Tsade |
| Fumus | Shin, Hey |
| Fundus | Bet, Samekh |
| Gelus | Mem, Het |
| Genus | Nun, Resh |
| Germen | Nun, Hey |
| Globus | Qof, Tet |
| Gradus | Gimel, Qof |
| Gratia | Pey, Yod |
| Grex | Bet, Gimel |
| Habere | Kaf, Bet |
| Haerere | Vav, Kaf |
| Herba | Nun, Het |
| Homo | Resh, Yod |
| Hospes | Bet, Dalet |
| Humus | Het, Aleph |
| Ignis | Shin, Hey |
| Imago | Hey, Ayin |
| Insula | Het, Bet |
| Jecur | Bet, Nun |
| Jocus | Pey, Shin |
| Judex | Lamed, Tsade |
| Jugum | Lamed, Vav |
| Junctus | Vav, Tav |
| Jus | Lamed, Tsade |
| Labor | Yod, Lamed |
| Lapis | Het, Tav |
| Latus | Het, Qof |
| Laus | Pey, Hey |
| Lex | Lamed, Tav |
| Liber | Hey, Pey |
| Ligo | Vav, Tav |
| Limen | Dalet, Het |
| Lingua | Pey, Ayin |
| Littera | Tav, Pey |
| Locus | Bet, Het |
| Longe | Gimel, Qof |
| Lux | Hey, Ayin |
| Luna | Qof, Hey |
| Machina | Yod, Vav |
| Magister | Lamed, Aleph |
| Magnus | Aleph, Resh |
| Malus | Shin, Zayin |
| Manus | Yod, Kaf |
| Mare | Mem, Qof |
| Mater | Bet, Nun |
| Materia | Bet, Tet |
| Medicus | Samekh, Yod |
| Medius | Samekh, Qof |
| Memor | Ayin, Hey |
| Mens | Ayin, Lamed |
| Merx | Kaf, Bet |
| Miles | Zayin, Yod |
| Mirari | Ayin, Hey |
| Modus | Qof, Lamed |
| Mons | Resh, Aleph |
| Mors | Shin, Tav |
| Movere | Gimel, Samekh |
| Multus | Mem, Nun |
| Mundus | Qof, Bet |
| Mutare | Shin, Samekh |
| Nasci | Nun, Hey |
| Nates | Samekh, Bet |
| Navis | Gimel, Mem |
| Nervus | Vav, Kaf |
| Nix | Mem, Tet |
| Nomen | Tav, Pey |
| Norma | Lamed, Qof |
| Novus | Nun, Aleph |
| Nox | Qof, Het |
| Nubes | Mem, Hey |
| Nudus | Hey, Bet |
| Numerus | Qof, Tav |
| Oculus | Ayin, Hey |
| Odor | Hey, Ayin |
| Omne | Qof, Tav |
| Opus | Yod, Lamed |
| Orbis | Qof, Tet |
| Ordo | Lamed, Qof |
| Os | Pey, Samekh |
| Ovum | Nun, Qof |
| Panis | Bet, Nun |
| Pars | Zayin, Vav |
| Pater | Aleph, Bet |
| Pati | Samekh, Het |
| Pax | Tav, Vav |
| Pectus | Bet, Hey |
| Pecus | Aleph, Kaf |
| Pellis | Tet, Het |
| Pendere | Samekh, Qof |
| Pes | Gimel, Samekh |
| Petere | Tsade, Zayin |
| Picus | Zayin, Pey |
| Piscis | Nun, Mem |
| Planta | Nun, Gimel |
| Plicare | Tet, Kaf |
| Pondus | Samekh, Qof |
| Populus | Bet, Resh |
| Portare | Gimel, Dalet |
| Portus | Dalet, Mem |
| Potens | Aleph, Mem |
| Pratum | Nun, Het |
| Pretium | Kaf, Tsade |
| Primus | Aleph, Resh |
| Probus | Tsade, Tav |
| Proprius | Bet, Kaf |
| Pugnus | Kaf, Zayin |
| Punctum | Yod, Tav |
| Purus | Hey, Tav |
| Quatere | Zayin, Samekh |
| Quercus | Nun, Het |
| Quies | Samekh, Hey |
| Radix | Nun, Aleph |
| Ramus | Nun, Vav |
| Ratio | Ayin, Qof |
| Regere | Lamed, Resh |
| Regnum | Lamed, Resh |
| Ritus | Tav, Qof |
| Rivus | Mem, Gimel |
| Rota | Qof, Samekh |
| Ruptus | Zayin, Shin |
| Sacer | Tav, Het |
| Sal | Tet, Shin |
| Salus | Samekh, Het |
| Sanus | Samekh, Nun |
| Sapiens | Ayin, Lamed |
| Saxum | Het, Aleph |
| Scientia | Ayin, Hey |
| Scindere | Zayin, Shin |
| Scribere | Tav, Yod |
| Secare | Zayin, Shin |
| Sedes | Samekh, Bet |
| Senex | Resh, Qof |
| Sentire | Ayin, Hey |
| Sequi | Gimel, Vav |
| Serere | Vav, Nun |
| Signum | Tav, Hey |
| Silva | Nun, Het |
| Similis | Vav, Tet |
| Socius | Vav, Bet |
| Sol | Qof, Hey |
| Solus | Aleph, Het |
| Somnus | Samekh, Hey |
| Sonus | Pey, Hey |
| Soror | Bet, Vav |
| Spatium | Het, Qof |
| Specere | Hey, Ayin |
| Sperare | Hey, Qof |
| Spiritus | Hey, Nun |
| Stare | Samekh, Aleph |
| Stella | Qof, Hey |
| Stirps | Nun, Aleph |
| Stringere | Vav, Het |
| Struere | Bet, Yod |
| Sudor | Yod, Hey |
| Sumere | Kaf, Yod |
| Tactus | Kaf, Yod |
| Talis | Vav, Qof |
| Taurus | Aleph, Zayin |
| Tegere | Kaf, Tet |
| Tempus | Qof, Samekh |
| Tendere | Vav, Kaf |
| Tenebrae | Het, Qof |
| Tenere | Kaf, Yod |
| Terminus | Dalet, Tav |
| Terra | Bet, Het |
| Testis | Ayin, Pey |
| Texere | Tet, Vav |
| Timere | Het, Zayin |
| Tollere | Yod, Aleph |
| Torquere | Tet, Samekh |
| Totus | Tav, Qof |
| Trahere | Yod, Gimel |
| Tremere | Zayin, Samekh |
| Tribus | Bet, Resh |
| Trudere | Yod, Zayin |
| Tuber | Tet, Bet |
| Unda | Mem, Samekh |
| Unus | Aleph, Resh |
| Urbs | Bet, Het |
| Urina | Mem, Bet |
| Usus | Yod, Kaf |
| Uxor | Bet, Vav |
| Vacare | Bet, Het |
| Vadus | Mem, Dalet |
| Vagari | Gimel, Samekh |
| Valere | Aleph, Het |
| Vapor | Mem, Hey |
| Vas | Bet, Tet |
| Vegetare | Nun, Hey |
| Velum | Hey, Tet |
| Vena | Mem, Vav |
| Venter | Bet, Nun |
| Ventus | Hey, Mem |
| Verbum | Pey, Tav |
| Veritas | Hey, Ayin |
| Vertere | Samekh, Qof |
| Vesper | Qof, Het |
| Via | Dalet, Gimel |
| Vicare | Shin, Samekh |
| Vicinus | Bet, Vav |
| Vincere | Zayin, Aleph |
| Vinculum | Vav, Het |
| Vinus | Nun, Bet |
| Vir | Resh, Aleph |
| Virtus | Aleph, Tsade |
| Viscus | Bet, Nun |
| Vita | Nun, Hey |
| Vitrum | Hey, Tet |
| Vivere | Nun, Hey |
| Vocare | Pey, Hey |
| Volare | Hey, Gimel |
| Velle | Tsade, Ayin |
| Volvere | Tet, Samekh |
| Vorare | Shin, Zayin |
| Vulnus | Zayin, Shin |
| Vultus | Resh, Hey |

## Notes from the source document

- First-pass mechanical assignment based on pictographic fit — every pairing is worth
  spot-checking, especially the less obvious ones.
- With glyph loads this uneven, the resulting semantic-profile shape looks very different in
  scale from v1/v2's curated sets — whether that's the intended shape, or whether lighter
  glyphs should absorb more load, is an open question (see `../README.md`).
- Some roots could reasonably sit under a 3rd glyph; the source kept everything at exactly 2
  to stay legible. Not expanded here either, for the same reason.
