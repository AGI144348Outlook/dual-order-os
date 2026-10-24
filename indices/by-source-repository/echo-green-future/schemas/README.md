# Schemas

The blank forms: what fields a kind of record must have, their types and rules. Templates live here too, since a template is a schema with blanks to fill.

## Belongs here

- written schemas (`Business/ledger/SCHEMA.md`, the Contract 000 manifest row)
- implied schemas the sweep extracts from code or data (the geosensory reading, each `echo_*.json` row)
- templates (`ASSESSMENT_TEMPLATE.md`, card and dictionary-entry templates)

## Not here

- how two parts exchange messages → `protocols/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `form` | `written` (exists as a document) or `implied` (extracted from code or data) |
| `describes` | which records or messages it governs |
| `notation` | table, JSON Schema, SQL or code |
| `fields` | its fields, or a link to them |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	form	describes	notation	fields	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
SCH-0001	Geosensory reading	implied	one feed reading (schema_version 1)	code	id, value, unit, observed_at_ms, coordinates…	geosensory-crawler-experiment	src/geosensory_model.py			unknown	INERT	home		
```

## Sweep 1 — 2026-10-23

**56 rows: 13 written, 14 declared, 29 implied.** Field lists are read from the files by the script
([`sweeps/sweep_1_schemas.py`](sweeps/sweep_1_schemas.py)), not typed by hand. Cited lines were checked.

| Form | Rows | What |
| --- | --- | --- |
| written | 13 | Contract 000 manifest row, L2 register row, this inventory's index row, business ledger row, the code-library assessment template, ECHO's output format, six D1 tables from the Cloudflare blueprint, and one page template (a cross-reference to `interfaces/`) |
| declared | 14 | data files that name their own schema id (`echo.hebrew-glyph-registry.v0.1` and others); no written definition of any id was found, so fields come from the file |
| implied | 29 | dataclasses in code (the EMEL syntax tree, the Governor's State/Request/Context, the neuroplasticity overlay's PlasticLink, classroom, audits, six code-library modules), the geosensory reading, the entry shape of nine `matrices/echo_*.json` stores, and the Rule Registry rule |

**Alongside:** 7 glossary rows (2 undefined at source: department, reuse disposition) and 6 new registries rows;
each registry now names the schema of one entry (`entry_schema`).

**Echo's shadow run** ([`sweeps/echo_shadow_2.tsv`](sweeps/echo_shadow_2.tsv)) continued from what he learned in
logics (39 attempts carried in) and gained a fifth way of guessing: looking inside the file for a dataclass, a
schema id, a `CREATE TABLE` or a field table. 30 of 64 right: 20 of the first 32, 10 of the last 32. He learned
to trust the new content check for code (0.95 over 19) and JSON (0.79 over 14). The drop in the second half
came from rows whose form is implied by a data store (the `echo_*.json` entries and the blueprint tables):
nothing in those files says "schema", so every way of guessing he has points elsewhere. His question in this
folder was harder than in logics: not which folder a file belongs to, but whether a form is hiding inside it.
