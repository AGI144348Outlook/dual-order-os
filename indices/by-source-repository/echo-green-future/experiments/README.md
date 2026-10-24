# Experiments

Trials and tests, each linked to the result it produced.

## Belongs here

- `experiments/*.py`, Stress Tests 001 and 002, IVS tests, NVE-D trials
- test suites (`tests/`, `test_*.py`, `*.cjs`)
- their result files

## Not here

- the algorithm under test → `algorithms/` (linked by id)

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `question` | what it asks |
| `code` | the code path |
| `result` | the result path |
| `ran_on` | date it ran |
| `outcome` | what happened, one line |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	question	code	result	ran_on	outcome	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
EXP-0001	Glyph comprehension transfer 007			results/glyph_comprehension_transfer_007.json			algebra	experiments/glyph_comprehension_transfer_007.py			unknown	INERT	home		
```
