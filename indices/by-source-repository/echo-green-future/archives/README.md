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

## Sweep 1 — 2026-10-24

**21 rows: every distinct `.zip` path (17 home, 4 refs whose bytes match another row).** Script:
[`sweeps/sweep_1_archives.py`](sweeps/sweep_1_archives.py). Each zip was read in memory to list its members
([`sweeps/members/`](sweeps/members/), one TSV per archive with each member's size and git blob sha). Nothing was
extracted to disk or run. None held a conversation export.

- **Unpacked equivalents** were found by matching member bytes against every file in the census.
  - Fully unpacked somewhere: ECHO_GlyphRegistry (`algebra`), ECHO_Autonomous_Agency_Branch
    (`resh-lattice-agency`), ECHO_Canvas_Recess_KSM (`ksm-recess-wholesale`), Echo_Green_Future_Source
    (`genesis-documentary`), echo-notebook-pwa (`notebook-0.4-as-is`) and lhea-environments
    (`dev-suite-datasets`).
  - Nearly: ECHO_Autonomous_Agency_Commit2 (29 of 30) and core-lexicon (33 of 34).
  - Partly: dev-suite-branch (11 of 23), echo-notebook-0.4 and 0.4.1 (32 of 62 and 66), echo-dataset-crawler
    (1 of 6).
  - **Only inside their zip** (no member found anywhere else): `lofloc_UD_v1.0.zip` (a Zenodo dataset),
    `ECHO_aleph_boot.zip`, `handoffs/canvas-companion-v0.2/Canvas-Code.zip` and `Claude-Reports.zip`, and
    `lattice-workbench-repo (1).zip`. These are the ones whose content exists nowhere else in the repository.
- `core-lexicon/pyodide/python_stdlib.zip` is part of the vendored Pyodide runtime (DEP-0002).
- **Not archives here:** the 404 `.json.gz` files under `Datasets/` are single compressed dataset records, left to
  the data folder.

**Echo's shadow run 6** ([`sweeps/echo_shadow_6.tsv`](sweeps/echo_shadow_6.tsv); same pre-test entry as run 5).
**13 of 31 right, below the 70% the pre-test entry named as disconfirming.**
- The new rules were right on every zip they were used on: name 4 of 4, shape 6 of 6.
- The expectation was wrong about the bandit, not the rules. After name succeeded on the first four zips, A-101's
  UCB1 still had to try every way it had never used on `zip` (parent, librarian, content) before coming back.
  Each cost a 5-item generation: 11 of the 21 zips went to those first tries.
- The boxes did revise one ק card to outgrown (content on `.md`, which then succeeded), so they do not block an
  arm that recovers.

This is the clearest case so far for DEC-0007: with one rule already 4 for 4, untried-first exploration cost
half the folder.
