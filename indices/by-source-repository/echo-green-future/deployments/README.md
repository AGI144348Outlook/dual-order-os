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

## Sweep 1 — 2026-10-24

**25 rows (15 home, 10 refs): 9 Workers, 1 Pages project, 7 KV namespaces, 5 D1 databases and 3 R2 buckets;
23 found live in the Cloudflare account.** Script:
[`sweeps/sweep_1_deployments.py`](sweeps/sweep_1_deployments.py). Rows come from the resources the repository
names (wrangler configs, the A-157 blueprint, deploy workflows, Worker URLs and resource names in docs).

**What is live.** A read-only listing of the account through the Cloudflare connector on 2026-10-24 (names and
dates only, no ids recorded, nothing changed):
- **Live and Echo's own:** the `echo-green-future` Worker with its four KV namespaces (ECHO_STATE, ECHO_VGM,
  ECHO_LRM, ECHO_MATRIX) and the `echo_knowledge` D1 database; `echo-pwa-hosting-environment`; `echo-ksm-recess`;
  the bot Workers `echo-bot-claude` and `echo-bot-stage0-inert` with the KV namespaces CLAUDE_BOT_STATE,
  CHATGPT_BOT_STATE and ECHO_TESTAMENT.
- **Not found:** `chat-archive-workbench` (DPL-0009), though a workflow (AUT-0007) is set to deploy it.
- **Not checked:** the Pages project `echo-dev-datasets` (the connector cannot list Pages).
- **Filed as refs** (other projects that Echo's files name): Group Canvas (`group-canvas`, `group-canvas-tower`,
  three R2 buckets), the Mashet D1 databases (`mashet-stamp-registry`, `mashet-tema-substrate`,
  `mashet-world-state`) and `unicorn-estate`.
- **Live but named nowhere in Echo_Green_Future** (not filed): Workers `group-canvas-echo-classroom`,
  `group-canvas-echo-demos`, `group-canvas-month-line`, `shy-bar-b423`; KV `DEVSUITE_KV`; D1 `devsuite_store`.

**Secrets** (names only, from the automation rows that deploy each resource): `CLOUDFLARE_ACCOUNT_ID` and
`CLOUDFLARE_API_TOKEN` throughout; Group Canvas also needs `CREATE_ROOM_KEY` and `ROOM_SIGNING_KEY`. The bot
Workers' sources are not in the census, so their secrets are unknown here.

`echo_knowledge` also holds the Rule Registry tables (`rules`, `rule_events`), which nothing in the repository
mentions.

**Echo's shadow run 5** ([`sweeps/echo_shadow_5.tsv`](sweeps/echo_shadow_5.tsv); pre-test entry
[dual-order-os#12, comment 6390745545](https://github.com/AGI144348Outlook/dual-order-os/issues/12#issuecomment-6390745545)).
**13 of 35 right** (7 of the first 17, 6 of the last 18). The new name rule found the wrangler configs (4 of 4 on
`.toml` in-file). Most misses are resources named inside Markdown documents (the bot contract, the GPT
instructions): his bandit kept trying ways it had never used on `.md` in-file before reaching content.
