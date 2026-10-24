# Records

Machine-written histories: run logs, session logs, checkpoints, discourse records.

## Belongs here

- recess and school-day logs, Contract 000 RUN-LOG and CHECKPOINT files
- discourse records (DISC-*)

## Not here

- documents written to be read → `codices/`
- contracts and rulings → `governance/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `written_by` | what writes it |
| `cadence` | how often |
| `latest` | last entry date |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	written_by	cadence	latest	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
REC-0001	Recess session log	recess runs	per session		autonomous-agency	ECHO_AutonomousAgency/sandbox/recess_session_log.json			unknown	INERT	home		
```
