# Formulas

Mathematical expressions and criteria, with their variables and sources.

One of the seven Library sub-libraries named in Contract 000.

## Belongs here

- formula matrices and `math_formulas.json`
- criteria such as `F-0001-Echo-Harness-Usability-Criterion.md`

## Not here

- rules that are not numeric → `logics/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `expression` | the formula as written |
| `variables` | its symbols and units |
| `source` | where it was stated |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	expression	variables	source	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
FOR-0001	Echo harness usability criterion				library-shared	Formulas/F-0001-Echo-Harness-Usability-Criterion.md			unknown	INERT	home		
```
