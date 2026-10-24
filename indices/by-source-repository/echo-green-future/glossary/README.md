# Glossary

Project terms and what they mean, as Timothy defined them or as a source states. Meanings that drifted are kept side by side, not merged.

## Belongs here

- EVE, NVE, LVT, TEMA, LHEA, Recess, KSM, Presentiation, Mirroring Child…
- glyph roles as stated (proposed vs ruled)

## Not here

- ordinary dictionary words → `data/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `term` | the term as written |
| `meaning` | the meaning as stated |
| `stated_by` | Timothy, a document, or an agent |
| `first_seen` | where it first appears |
| `variants` | other meanings found, kept side by side |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	term	meaning	stated_by	first_seen	variants	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
GLO-0001	NVE	NVE	nested Virtual Environment	Timothy							unknown	INERT	home		
```
