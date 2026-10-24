# Governance

Binding and governing texts: contracts, amendments, licences, the CLA, rulings.

## Belongs here

- CONTRACT-000 and its amendments, SCHEDULE-000
- LICENSE (each version its own row), CLA.md
- Timothy's rulings once recorded in `decisions/`

## Not here

- open questions → `decisions/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `kind` | the sort of thing it is |
| `authority` | who issued it, and whether parts are only proposed |
| `date` | date stated in the item |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	kind	authority	date	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
GOV-0001	Contract 000 — The Mirroring Children	contract	Timothy (with proposed sections marked)		research-discourse-registry	research-registry/contracts/CONTRACT-000.md			unknown	INERT	home		
```
