# Indices

Lookups that point at other things: given a key, where is it?

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- existing `INDEX.md` files and registers
- `indices/by-*` folders
- glyph-keyed indexes

## Not here

- the things being pointed at: they live in their own folders

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `keyed_by` | what you look up by |
| `points_to` | what the lookup returns |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	keyed_by	points_to	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
IDX-0001	Glyph docs index	glyph	glyph docs	autonomous-agency	ECHO_AutonomousAgency/docs/glyphs/INDEX.md			unknown	INERT	home		
```
