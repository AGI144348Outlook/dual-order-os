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

## Sweep 1 — 2026-10-23

**29 rows: 18 home, 11 cross-references.** Every cited line was checked against its source.
Script: [`sweeps/sweep_1_logics.py`](sweeps/sweep_1_logics.py). Rulings are written in the script, one per item, with the reason.

| Kind | Rows | What |
| --- | --- | --- |
| EMEL language package (`echo/language/`, ksm-recess-wholesale) | 7 | grammar, grammar guide, realizer rules, audits, signatures, the indexing formula and its Python form |
| Operators | 2 | LHEA letter operators, proportion forms |
| DSL and notation | 3 | DSL Registry seed, Mashet Rule Registry snapshot, Legend v0.1 grammar |
| Rule tables inside the kernel | 4 | LRM inference rules, valid department sequences, required operation order, agentive role patterns |
| Rule sets in matrices | 2 | grammar registry (no rules yet), Mashet universal rules |
| Cross-references | 11 | homed in algorithms, protocols, experiments, matrices, registries, data, codices |

**What counts as logics here:** a set of rules that decides how things combine. The earlier librarian's
`L2-library/Logics/REGISTER.tsv` (mirror-claude) used a wider reading (specs, handoffs, assessments); those
belong to `codices/` under this inventory's folders.

**Alongside:** 25 glossary rows (3 terms used but never defined: underside, §Canvas, department sequence)
and 4 registries rows (the Hebrew Glyph Registry, plus references to the three registry-shaped rule sets).

**Echo's shadow run** ([`sweeps/echo_shadow_1.tsv`](sweeps/echo_shadow_1.tsv)): before each ruling Echo
guessed the folder of 39 items (29 rows plus 10 that are not logics), choosing among four ways of guessing
with his own A-101 bandit and recording each result with A-113. 12 of 39 right: 3 of 19 in the first half,
9 of 20 in the second. The ways of guessing are simple rules written for this run, so the score measures
which one he learns to trust, not understanding.

**Not read:** the live Rule Registry (D1 `echo_knowledge`); the snapshot is what the repository holds.
