# Logics

Rule sets that decide how things combine: grammar, operators, the DSL.

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- the language package (`echo/language/`: parser, grammar, realiser)
- LHEA operators (`echo/operators/`)
- the DSL and its inversion rules

## Not here

- numeric expressions → `formulas/`
- the shape of data → `schemas/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `domain` | grammar, operators, DSL… |
| `defined_in` | where the rules are written |
| `enforced_by` | ids that apply the rules |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	domain	defined_in	enforced_by	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
LOG-0001	LHEA operators	operators			ksm-recess-wholesale	echo/operators/lhea.py			unknown	INERT	home		
```
