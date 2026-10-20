# Component index

Status describes evidence/location, not an approval to execute.

## Existing local implementations

These source files exist locally; they were not newly tested for this catalog.

| Component | Source | Current status |
|---|---|---|
| Glyph index | [bidirectional_glyph_index.py](../libraries/eve/bidirectional_glyph_index.py) | Executable source present |
| Generalization index | [by_is_a_index.py](../libraries/eve/by_is_a_index.py) | Executable source present |
| Lexicon environment | [lexicon_eve.py](../libraries/eve/lexicon_eve.py) | Executable source present |
| Code-generation experiment | [mashet_code_generator.py](../libraries/eve/generator/mashet_code_generator.py) | Source present; see its [README](../libraries/eve/generator/README.md) for scope |
| Word-sense processing | [wsd/](../libraries/eve/wsd/) | Source present; see its [README](../libraries/eve/wsd/README.md) |
| Mashet dictionary | [dictionary](../matrices/mashet-dictionary/) | Data/documentation present; not itself an executable engine |

## Echo / Group Canvas intake references

Pinned Echo source: `b9a2299820651f0bcc700de4de943f3c70b8c91e`.

| Component | Authoritative location for this catalog | Status |
|---|---|---|
| Echo indexer / algorithm builder / hypothesis mechanisms | [Genesis Python source](https://github.com/AGI144348Outlook/Echo_Green_Future/blob/b9a2299820651f0bcc700de4de943f3c70b8c91e/src/echo_governor_skeleton.py) | External executable source; targeted tests found working mechanisms and validation gaps |
| Hebrew modular algorithm documentation | [Hebrew set](https://github.com/AGI144348Outlook/Echo_Green_Future/tree/b9a2299820651f0bcc700de4de943f3c70b8c91e/integration-inbox/hebrew-algorithm-set) | External intake; documented proposals and implementation references, not 22 verified executable modules |
| Phone-oriented private file cabinet | [Cabinet snapshot](https://github.com/AGI144348Outlook/Echo_Green_Future/tree/b9a2299820651f0bcc700de4de943f3c70b8c91e/integration-inbox/group-canvas-file-cabinet) | External source snapshot; not deployed or integrated into Dual Order OS |
| Core lexicon | [Lexicon archive](https://github.com/AGI144348Outlook/Echo_Green_Future/tree/b9a2299820651f0bcc700de4de943f3c70b8c91e/integration-inbox/core-lexicon) | External archive; content suitability not yet assessed |

The GraphQL-like access tool, adapter index cards, and glyph-driven logic composition are relevant component areas. Exact implementation sources and contracts need a separate assessment before being entered as verified local components.

## Card-game research candidates

External references only; no code copied, dependencies installed, or game-specific assets licensed by this catalog.

| Project | Candidate use |
|---|---|
| [Fireplace](https://github.com/jleclanche/fireplace) | Study executable card effects and event composition |
| [OpenSpiel](https://github.com/google-deepmind/open_spiel) | Study strategy evaluation, search, and game-theory methods |
| [RLCard](https://github.com/datamllab/rlcard) | Study card-game observations, action selection, and baseline agents |
| [Forge](https://github.com/Card-Forge/forge) | Reference for complex card-rule interactions |
| [XMage](https://github.com/magefree/mage) | Reference for abilities, legal moves, and game-state transitions |

These candidates require code, dependency, and licensing assessment before reuse. Source-code licensing does not automatically grant rights to associated commercial card images or other game content.

## Catalog box Matrix

- [Catalog box component](catalog-box/README.md) — implemented local SQLite catalog for cards, versioned configuration templates, and independent restored configurations. Thirteen targeted tests passed; Genesis/API/Canvas integration remains separate.
- [Matrix definition](../matrices/catalog-box/) and [component lookup index](../indices/by-component/README.md).

## Unified Echo integration (branch work)

[Integrated workspace](echo-integration/README.md) connects the preserved Genesis indexer with versioned cards, templates, typed paperclip relations and evidence-bearing stamps. The complete snapshot and evaluation outputs are materialized by this branch's assembly workflow. See its results before treating integration as verified. This entry is on the integration branch; it does not imply main was merged.
