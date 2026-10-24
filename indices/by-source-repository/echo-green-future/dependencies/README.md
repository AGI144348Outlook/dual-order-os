# Dependencies

Outside things Echo relies on, with their licences. Needed for the dual licence: knowing what third-party code and data are inside.

## Belongs here

- libraries and runtimes: Pyodide, NLTK/WordNet, SciPy, NetworkX
- services: Cloudflare, OpenRouter, NOAA/USGS/NASA feeds

## Not here

- Echo's own code → its own folders

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `kind` | the sort of thing it is |
| `version` | version in use |
| `licence` | its licence as stated |
| `used_by` | ids that use it |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	kind	version	licence	used_by	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
DEP-0001	Pyodide	runtime	0.26.4 (dev-suite) / 0.29.3 (widgeting)		INT-*					unknown	INERT	home		
```
