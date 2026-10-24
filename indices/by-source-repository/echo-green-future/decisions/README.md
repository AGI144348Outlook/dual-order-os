# Decisions

Every choice waiting on Timothy, and his ruling once made. Open questions are parked here so the sweep keeps moving.

In this folder `status` is `OPEN` or `RULED`, not the Contract 000 terms the other folders use.

## Belongs here

- which of the 6 READMEs, 3 LICENSEs and the PWA shells is current
- deletions and moves (conversation exports, datasets to R2)
- rules for this inventory itself

## Not here

- the governing text a ruling becomes part of → `governance/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `question` | what it asks |
| `options` | the choices on the table |
| `needed_for` | what waits on it |
| `ruling` | Timothy's answer, in his words |
| `date` | date stated in the item |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	question	options	needed_for	ruling	date	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
DEC-0001	Current README	Which README.md version is current for the integrated Echo?	6 versions (see inventory.json drift)	repo identity							unknown	OPEN	home		
```
