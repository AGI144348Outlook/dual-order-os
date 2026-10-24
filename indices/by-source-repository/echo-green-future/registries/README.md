# Registries

Lists of named entries that something keeps adding to and looks up by name.

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- glyph registries (`ECHO_GlyphRegistry/`)
- the mini ר symbol registry (`symbols.json`)
- the geosensory endpoint registry
- the code library registry (`code_library_registry/`)

## Not here

- a fixed table of numbers or weights → `matrices/`
- the rules for what an entry must contain → `schemas/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `entry_count` | number of entries at the swept commit |
| `entry_schema` | the `schemas/` id for one entry |
| `maintained_by` | tool, algorithm or agent that adds entries |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	entry_count	entry_schema	maintained_by	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
REG-0001	Geosensory endpoint registry	16	SCH-?	A-158 GeosensoryCrawler	geosensory-crawler-experiment	matrices/echo_geosensory_registry.json			unknown	INERT	home		
```
