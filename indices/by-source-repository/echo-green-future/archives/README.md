# Archives

Zip bundles, sealed. Their file lists are recorded; they are never extracted or run during the sweep.

## Belongs here

- every `.zip` (18 distinct)

## Not here

- the unpacked equivalent, when it exists as a branch → its own folder, linked here

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `members` | number of files inside |
| `unpacked_equivalent` | branch or path holding the same content unpacked |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	members	unpacked_equivalent	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
ARC-0001	ECHO_Autonomous_Agency_Branch.zip	14	autonomous-agency	main	ECHO_Autonomous_Agency_Branch.zip			unknown	DEFERRED	home		
```
