# Echo catalog box

A reusable Python catalog for Echo's index cards and configuration templates. Standard library only; SQLite persists local data. It is implemented in Dual Order OS, not yet automatically invoked by Genesis.

## The three sections

| Section | Contents |
|---|---|
| `cards` | Stable card IDs, numbered revisions, optional glyph, title, JSON body, tags, provenance |
| `templates` | Named configuration snapshots and exact card-revision references |
| `configurations` | Independent instances restored from templates, with their own revision histories |

The matrix definition is at [matrices/catalog-box](../../matrices/catalog-box/). The implementation is [libraries/catalog_box.py](../../libraries/catalog_box.py). A card is a record; this component does not give glyphs execution authority.

## Python interface

From the repository root, on a computer or a Python-capable phone environment:

```python
from libraries.catalog_box import CatalogBox

with CatalogBox("echo-catalog.sqlite") as box:
    box.put_card(
        "tsadi-paperclip", "Paperclip", {"verb": "attach", "status": "proposed"},
        glyph="צ", provenance={"source": "Timothy's paperclipping direction"})
    box.put_template(
        "word-review", "Word review layout",
        {"columns": ["word", "attachments", "glyph_tags"]},
        [{"id": "tsadi-paperclip"}])
    box.instantiate("word-review", "session-001")
    box.save_configuration("session-001", {"columns": ["word", "glyph_tags"]},
                           expected_revision=1)
    box.save_as_template("session-001", "compact-review", "Compact review")
    restored = box.instantiate("compact-review", "session-002")
    cards = box.resolve_cards("configurations", "session-002")
```

These are first-creation calls. Rerunning the same IDs produces `Conflict`, not silent replacement. To revise a card/template, supply the expected current revision. `expected_revision=0` means create only. SQLite files are runtime data: keep them outside Git when they contain private records.

The original IDs persist across edits. `get(section, id)` retrieves the current revision; `get(section, id, revision)` and `history(section, id)` retrieve older versions. `list("cards", glyph="צ")` provides reverse lookup without conflating צ with ץ. Multiple cards may share one glyph; their IDs remain distinct. There is no requirement for one fixed meaning per glyph.

`save_as_template` captures a specific saved-configuration version; later edits do not change the template. Templates pin card revisions at creation. `instantiate` restores JSON configuration and pinned references, not external programs, browser windows, or a complete running environment. `resolve_cards` returns the referenced card versions.

## Verification and limits

```sh
python -m unittest discover -s tests -p 'test_catalog_box.py' -v
python libraries/catalog_box.py --demo
```

The demo uses a temporary database and the user-directed צ paperclip / ת associative-stamp roles as **proposed records**. It neither performs attachments nor stamps vocabulary. Its output is preserved as [example.json](../../matrices/catalog-box/example.json).

Thirteen tests cover persistence, independent restoration, captured templates, historical versions, stale updates from two clients, duplicate identities, missing references, input/return mutation, strict JSON values, and inert code strings.

Writes and event records commit together. Events are an operational log, not a tamper-proof audit chain. There is no delete API. Data is not encrypted and this module supplies no account authentication, remote access controls, hosted UI, R2 synchronization, or schema migration system. Access to the database file is trusted. Do not expose these methods directly as public endpoints without a separately reviewed access layer.

No automatic semantic inference or code execution occurs. JSON configuration is preserved, not validated against a particular application's layout schema. Saving a card or template does not certify its claims or grant execution permissions. Callers must keep credentials out of cards/templates unless a future reviewed secret-reference mechanism is provided.

The Python component has not been tested on an actual Android device or wired into the Canvas. A phone-oriented catalog interface can later use these contracts without changing the identities or snapshot rules.
