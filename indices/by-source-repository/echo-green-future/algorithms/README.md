# Algorithms

Every algorithm, one row each, down to the class or function that implements it. Most of Echo's A-numbered algorithms live as classes inside the single skeleton file, so rows point inside files.

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- A-000 onward, from `echo_governor_skeleton.py` and its copies
- experimental algorithms (EXP-*, Recess, KSM, neuroplasticity)
- algorithms described in documents but not yet implemented (status noted)

## Not here

- runnable utilities with no learning or governing role → `tools/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `algorithm_id` | A-number or EXP-id as the source names it |
| `location` | the class or function inside the file |
| `state_in_code` | the status the code itself gives (ACTIVE, DORMANT…) |
| `introduced_in` | branch where it first appears |
| `depends_on` | ids it calls or needs |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	algorithm_id	location	state_in_code	introduced_in	depends_on	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
ALG-0158	GeosensoryCrawler	A-158	class GeosensoryCrawler	to be read		to be swept	genesis-documentary	src/echo_governor_skeleton.py			unknown	INERT	home		docstring: A-157 DeploymentTranslator generates its D1 blueprint
```
