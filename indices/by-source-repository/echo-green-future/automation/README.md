# Automation

How things build, test and deploy on their own: workflows and deploy configs.

## Belongs here

- `.github/workflows/*.yml`
- `wrangler.toml` and deploy configs

## Not here

- what is live as a result → `deployments/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `trigger` | push, schedule, manual… |
| `does` | what it does, one line |
| `secret_names` | names of secrets it needs (never values) |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	trigger	does	secret_names	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
AUT-0001	Echo classroom lab	to be read			main	.github/workflows/echo-classroom-lab.yml			unknown	INERT	home		
```
