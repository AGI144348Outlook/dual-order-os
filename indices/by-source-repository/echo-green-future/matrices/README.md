# Matrices

Echo's structured stores: tables of agents, chains, weights or values that algorithms read and update.

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- `matrices/echo_*.json` (algorithm matrix, lobby agents, VGM, WordNet chains, numbers, equilibria)
- matrix code such as `algorithm_matrix.py`, as a reference to its algorithms row

## Not here

- a list looked up by name → `registries/`
- a list that points at other things → `indices/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `shape` | what a row holds, in a few words |
| `entry_count` | number of entries at the swept commit |
| `fed_by` | ids that write to it |
| `read_by` | ids that read it |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	shape	entry_count	fed_by	read_by	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
MAT-0001	VGM	to be read		to be swept	to be swept	genesis-documentary	matrices/echo_vgm.json			unknown	INERT	home		
```
