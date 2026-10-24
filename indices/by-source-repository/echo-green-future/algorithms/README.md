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

The row for A-158 as the first sweep filled it (blob and commit shortened here):

```tsv
id	name	algorithm_id	location	state_in_code	introduced_in	depends_on	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
ALG-0158	GeosensoryCrawlerUpgrade	A-158	GeosensoryCrawler (line 8846)	ACTIVE			genesis-documentary	src/echo_governor_skeleton.py	63eb9829…	…	unknown	INERT	home	מ;ע	type ACQUISITION; located by A-number comment naming it; same file in 18 other branches; …
```

## Sweep 1 — 2026-10-22

**118 rows: 110 A-numbers plus 8 code-library modules (`ALG-MOD-*`).** Every located row was checked against
its source lines; all 69 confirmed.

| Result | Rows | Meaning |
| --- | --- | --- |
| Located, strong evidence | 57 | a comment naming the class, a section header right above the definition, a defining docstring (`A-NNN:`), or a name match in a file that also carries the A-number |
| Located, weak (`WEAK` in notes) | 12 | only a passing mention inside a class or function, or a name match with no A-number nearby. The implementation is not pinned down |
| In Echo's registry, not found in code | 10 | A-145-AUG, A-160 to A-164, A-169 to A-172: proposed or described, no implementation found yet |
| Mentioned only, in no registry | 31 | ids that appear in dashboards, docs or logs (A-175 to A-196 and A-235 mostly in `artifacts/echo_matrix_browser.jsx`) |
| Code-library modules | 8 | `code_library_registry/modules/MOD-0001…0008`; contents still to be read |

**Sources.** Echo's own registries (`echo_algorithm_matrix.json` on `autonomous-agency`, 65 entries, overriding
the 54 on `genesis-documentary`; then `genesis_structure.json`), every code file on all 42 branches, and
`glyph_algorithm_index.json` for glyph ties (24 rows).

**How a row is located,** strongest evidence first:

1. A comment naming the class: `# A-125: GeneralityMatrix`.
2. A section header within three lines above a definition: `# -- A-101: UCB1 bandit` above `def bandit_select`. When the first definition under a header belongs to another A-number (its own docstring says so), the next definition is used.
3. A class or function with the registry's name, in a file that also carries the A-number.
4. A docstring that defines the A-number (`A-158:`), not one that only refers to it (`(A-101)`).
5. Weak: a name match alone, or a mention inside a class or function.

A-000 and A-000-RESH were set by hand. The Governor is the whole system rather than one class, and its identity check runs through `ReshIdentity`.

**Known overlaps.** Some classes implement more than one A-number. `GeosensoryCrawler` holds A-155 and its upgrade A-158. `AlgorithmMatrix.hub_words` is A-109, a helper for A-107. Where a branch holds the same file, the row points at the first branch in this order: `genesis-documentary`, `autonomous-agency`, `algebra`, `echo-recess-experiment`, `resh-lattice-agency`, then the rest alphabetically. Notes say how many other branches hold the same file.

**Left for later sweeps:** `introduced_in` and `made_by` need full commit history; `depends_on` belongs in `maps/`.
