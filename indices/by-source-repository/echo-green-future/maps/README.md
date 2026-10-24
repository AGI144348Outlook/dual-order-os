# Maps

The connections between everything above: uses, reads, writes, imports, supersedes. Every part reachable from both directions.

## Belongs here

- one row per connection between two inventory ids, with the evidence

## Not here

- the things themselves → their folders

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `from_id` | inventory id on one end |
| `relation` | uses, reads, writes, imports, supersedes… |
| `to_id` | inventory id on the other end |
| `evidence` | file and line, or document, that shows the connection |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	from_id	relation	to_id	evidence	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
MAP-0001	crawler writes registry	ALG-0158	writes	REG-0001	to be read in code					unknown	INERT	home		
```
