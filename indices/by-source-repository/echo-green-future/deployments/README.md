# Deployments

What is actually live, where: Workers, D1, KV, R2, Pages, their URLs, and the names of secrets each needs. Never secret values.

## Belongs here

- Cloudflare Workers and Pages apps
- D1 databases, KV namespaces, R2 buckets

## Not here

- how they get deployed → `automation/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `resource` | Worker, D1, KV, R2, Pages |
| `url` | where it is live |
| `deployed_from` | source path or workflow |
| `secret_names` | names of secrets it needs (never values) |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	resource	url	deployed_from	secret_names	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
DPL-0001	Echo Worker	Cloudflare Worker	to be confirmed	src/index.js + wrangler.toml						unknown	INERT	home		
```
