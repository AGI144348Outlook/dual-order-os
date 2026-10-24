# Codices

Written documents meant to be read: specs, RFCs, READMEs, handoffs, reports and research notes.

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- `docs/`, handoffs, RFCs, progress reports
- branch READMEs (each version is its own row)
- research notes, including the ByteByteGo library

## Not here

- legally binding or governing text → `governance/`
- machine-written logs → `records/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `kind` | the sort of thing it is |
| `date` | date stated in the item |
| `about` | one line on its subject |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	kind	date	about	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
COD-0001	Geosensory visual-model seam	design note		feed-to-visual conversion rules	geosensory-crawler-experiment	GEOSENSORY_VISUAL_MODELS.md			unknown	INERT	home		
```
