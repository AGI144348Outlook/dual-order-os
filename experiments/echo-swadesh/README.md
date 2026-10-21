# Echo — fresh Swadesh profile

Created at Timothy's request from `integration/echo-genesis-unified` commit `6c0cf810b0026c02e3afce8dccbaeb84b1b93ab6` on 2026-10-21. Branch: `experiment/echo-swadesh-fresh-start`.

The copied code, governance, algorithms and research history are retained. The designated new runtime starts with zero learned vocabulary, index cards, templates, configurations, catalog events, lexical agents, content units and indexed dictionary entries. Historical lexicons, fixtures and reports remain archival source files, not memory imported by this profile. Existing demos/bootstrap scripts can still load their old datasets if explicitly invoked; use this profile for the experiment. This is a fresh active state, not a deletion of repository history or every English constant in code. Built-in glyph descriptions, identity semantics and language rules remain inherited mechanisms and must be treated as priors in future evaluations.

## Start

If the pinned Genesis source is not already materialized, use the repository's existing `python tools/materialize_genesis.py` setup. Then:

```sh
python tools/start_swadesh_echo.py --database /tmp/echo-swadesh/fresh.sqlite
```

Use a new path for each fresh run. Existing files are refused atomically; no old database is wiped. The entry point creates and inspects an empty read-only-capability workspace and closes it, leaving a persistent empty catalog. It does not start an autonomous loop, ingest the curriculum, grant learning writes or run a comprehension test. Future teaching requires a separately specified, governed intake/qualification workflow.

`curriculum.md` lists the common Swadesh 100 concepts in English, as requested. `initial-state.json` records measured empty state, not a replacement for the SQLite runtime. The curriculum is never automatically ingested.

## Validation

Pre-test plan and post-test report: https://github.com/AGI144348Outlook/dual-order-os/issues/5 . Four bounded diagnostic checks passed: empty state, retained identity/governor, reopening the empty state, and refusal to overwrite an existing database. These are fresh-profile checks, not vocabulary or comprehension learning. No R2 data, external inference, model training or original-branch changes were involved.
