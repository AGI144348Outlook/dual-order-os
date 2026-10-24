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
