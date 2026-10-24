# Data

Bodies of content Echo reads: lexicons, corpora, dictionaries, datasets.

## Belongs here

- the Mashet corpus, core lexicon, the 5,000-word dictionary
- third-party datasets (one row per dataset; the files move to R2, the row keeps the pointer)

## Not here

- structured stores Echo updates → `matrices/`
- conversation exports: listed only, never copied

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `kind` | the sort of thing it is |
| `size_bytes` | size |
| `licence` | its licence as stated |
| `location` | the class or function inside the file |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	kind	size_bytes	licence	location	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
DAT-0001	Mashet parsed corpus	corpus			git	genesis-documentary	corpus/mashet_parsed.json			unknown	INERT	home		
```
