# Protocols

How parts talk to each other: who sends what, in which order, with which checks.

## Belongs here

- the widget operations API (`OPEN_WIDGET`, `BIND_WIDGET`…)
- the MCW message envelope (`mcw/0.1`)
- the GraphQL-style canvas query
- Echo's IDENTIFY → VALIDATE → OPEN check

## Not here

- the shape of a single message → `schemas/` (the protocol row links to it)

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `parties` | who talks to whom |
| `messages` | `schemas/` ids of the messages |
| `defined_in` | where the rules are written |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	parties	messages	defined_in	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
PRO-0001	MCW envelope	Echo → host (bridge.js) → endpoint	SCH-?	mcw/client.py	widgeting-experiment	pwa/echo/mcw/client.py			unknown	INERT	home		
```
