# Tools

Runnable utilities: builders, crawlers, migrators, checkers. A tool does a job; it does not learn or govern.

## Belongs here

- `build.py` scripts, `a159_cloudflare_migrator.py`, the dataset crawler
- the F-001 checking and build scripts
- shell scripts such as `fetch-pyodide.sh`

## Not here

- anything with an A-number or a learning role → `algorithms/`
- CI workflows → `automation/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `entry` | how it is started (command or file) |
| `inputs` | what it reads |
| `outputs` | what it produces |
| `side_effects` | what it changes beyond its outputs (writes, network) |
| `runs_where` | Pydroid, browser, CI… |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	entry	inputs	outputs	side_effects	runs_where	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
TOOL-0001	Dataset crawler				writes Datasets/ on a schedule	GitHub Actions	code-library-registry	Datasets/crawler/			unknown	INERT	home		
```
