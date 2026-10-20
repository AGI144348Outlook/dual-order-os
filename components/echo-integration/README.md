# Integrated Echo workspace

This integration branch combines a **complete, unchanged** Genesis Documentary snapshot with Dual Order OS's existing catalog box and a new explicit adapter. Genesis remains at source commit `b9a2299820651f0bcc700de4de943f3c70b8c91e`; every one of its 128 files is copied under `vendor/echo-genesis/`, including the integration inbox, binary lexicon archive, and archived Group Canvas cabinet source.

## What runs together

- Genesis `AlgorithmMatrix`, dictionary ingestion, Lobby orientation and classification.
- The persistent CatalogBox for cards, templates, saved configurations and revisions.
- Stable vocabulary-card identities; reopening the workspace reconstructs the original index from current persisted vocabulary cards.
- Separate glyph profiles, including distinct צ and ץ. These preserve original descriptions; the user-directed צ paperclip and ת associative-stamp uses are explicitly marked associations.
- צ paperclip operations persist typed links between exact card revisions. They do not merge or delete their endpoints.
- ת stamp operations attach glyph associations to vocabulary cards using explicit profile-keyword evidence. They never promote these links into VGM axioms or verified theorems.
- Templates pin word, profile and relation versions. The configuration graph exposes nodes/relations for later presentation.
- A structured Python query interface provides card, glyph, relation and indexed-neighbor access. It is not an HTTP service or an implementation of GraphQL syntax.

## Run

```sh
python -m libraries.echo_demo
python -m unittest discover -s tests -v
python tools/run_echo_integration.py
```

The demo uses temporary synthetic data, then closes and reopens SQLite before reporting restored state. It uses the standard library and is intended to remain runnable in a Python-capable Android environment; actual Android execution has not been verified here.

```python
from libraries.echo_workspace import EchoWorkspace

with EchoWorkspace('echo.sqlite', capabilities=EchoWorkspace.ALL_CAPABILITIES) as echo:
    echo.seed_profiles()
    echo.put_word('word:paperclip', 'paperclip', 'attach card to index', department='verb')
    echo.put_word('word:index', 'index', 'card collection', department='noun')
    echo.paperclip('link:1', 'word:paperclip', 'word:index')
    stamps = echo.stamp_matches('word:paperclip')
    print(echo.query({'operation': 'neighbors', 'word': 'paperclip'}))
```

IDs in this example create records once; editing requires the catalog's expected-revision contract. Missing references, conflicting relation identities, duplicate word identities and unauthorized adapter operations reject rather than silently overwriting. Default callers have read access only. Adapter capabilities are trusted-caller configuration, **not account authentication**; direct access to the Python object/database remains trusted. No public endpoint is installed.

## Preservation and limits

`tools/materialize_genesis.py` fetches the pinned public source in Actions and verifies every file's size and Git blob identity against `matrices/echo-integration/source-manifest.json`. The nested original `.github` files do not become active root workflows. The assembly workflow writes only this integration branch and does not deploy services.

The existing cabinet's frontend and Cloudflare workers are preserved in the snapshot, but are not connected to this local SQLite runtime or redeployed. Existing private R2 sources remain in place; no dataset copies or training runs are started. The lexicon archive is preserved, not automatically loaded as an approved semantic registry.

The configuration graph is a relational description, not the still-undefined §DSL§ inversion. Matrix-folder creation, a finalized DSL grammar, game strategy, generalized sound inference and glyph-driven operator synthesis are not silently implemented by this adapter. No new role is assigned to ץ.

Genesis's permissive generic validators, weak theorem-composition rules and raw-glyph tokenizer remain unchanged and are reported as known gaps. The adapter supplies bounded checks around its new operations; it does not claim to repair or certify all Governor paths. Keyword matches are authored associations, not proof of understanding, subjective judgment, or logical truth.

See the [combined results](../../reports/echo-integration/results.json), [snapshot manifest](../../matrices/echo-integration/source-manifest.json), and [progression report](../../research/progression/007-unified-echo-integration.md). The complete snapshot and results links become populated when the assembly run succeeds; their mere presence in this guide is not evidence that assembly completed.
