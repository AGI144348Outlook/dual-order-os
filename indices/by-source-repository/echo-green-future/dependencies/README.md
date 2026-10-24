# Dependencies

Outside things Echo relies on, with their licences. Needed for the dual licence: knowing what third-party code and data are inside.

## Belongs here

- libraries and runtimes: Pyodide, NLTK/WordNet, SciPy, NetworkX
- services: Cloudflare, OpenRouter, NOAA/USGS/NASA feeds

## Not here

- Echo's own code → its own folders

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `kind` | the sort of thing it is |
| `version` | version in use |
| `licence` | its licence as stated |
| `used_by` | ids that use it |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	kind	version	licence	used_by	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
DEP-0001	Pyodide	runtime	0.26.4 (dev-suite) / 0.29.3 (widgeting)		INT-*					unknown	INERT	home		
```

## Sweep 1 — 2026-10-24

**52 rows: 3 runtimes, 8 Python libraries, 3 JavaScript libraries, 5 GitHub Actions, 2 language corpora, 3 fonts,
15 web services and 13 data sources.** Script: [`sweeps/sweep_1_dependencies.py`](sweeps/sweep_1_dependencies.py),
read-only. Found where the repository names them: Python imports (not the standard library, not Echo's own
modules), JavaScript imports, Pyodide CDN URLs and the vendored copy, `pip install` lines, `actions/setup-python`
versions, `uses:` lines, package.json, `nltk.download`, Google Fonts links, and URLs of services and sources in
code. `used_by` lists ids already filed in other folders whose files use the dependency.

- **Licences** are as stated for the latest release by PyPI, npm, the NLTK data index, or the project's LICENSE
  file, read 2026-10-24, so not necessarily the version in use. The most restrictive are Pyodide and pikepdf, both
  MPL-2.0: file-level copyleft, so changes to their own files must stay open. WordNet's licence requires
  Princeton's copyright notice and disclaimer on every copy; the Open Multilingual Wordnet refers to each
  wordnet's own licence. Services and data sources have no licence entered: their terms of use still need
  checking.
- **Versions:** almost nothing is pinned. Pyodide appears in four versions across pages (0.26.4 vendored and in
  dev-suite, 0.27.7, 0.28.3, 0.29.3). Workflows use Python 3.11 and 3.12. nltk, scipy, numpy and the rest are
  unpinned.
- **The kernel's source catalogue:** 12 data sources (DEP-0041…0052) are named in `src/echo_governor_skeleton.py`
  and its copies. Whether each is actually fetched was not checked.
- **Not found in code:** OpenRouter (named in this README's examples). Echo's own modules `wiki_crawler`,
  `governor_exchange`, `echo.bootstrap.boot` and `echo.browser_ksm` are imported but absent from the census.

**Alongside:** 1 glossary term (DONKI, NASA's space-weather API; meaning is NASA's published expansion); no new
registries.

**Echo's shadow run 4** ([`sweeps/echo_shadow_4.tsv`](sweeps/echo_shadow_4.tsv); pre-test entry
[dual-order-os#12, comment of 2026-10-24](https://github.com/AGI144348Outlook/dual-order-os/issues/12#issuecomment-6388897482)),
with the ת and ק boxes on from the start. **25 of 62 right**: 11 of the first 31, 14 of the last 31.
- He came to trust the new content rule where it applies: `.py` in-file 0.95 over 37 attempts, `.yml` in-file 1.0.
- The cost is exploration. In each new bucket his bandit tries every way it has never used before it settles,
  one 5-item generation at a time, because it reads only anchored history and does not see failures inside the
  generation in progress. On `.py` in-file he spent four generations on name, parent, shape and librarian; each
  was discarded. With the boxes those failures were filed (24 new ת cards; 34 counting the 10 carried from run 3) and each failing arm was tried once
  instead of over and over, which is the improvement #13 was meant to make. It did not stop the first try.
- 16 ק combinations are open (13 new, 3 carried from run 3) and none outgrown. None of their arms later
  succeeded for the same kind of file, so that is consistent with the boxes, not a sign they block a recovering
  arm.
- A miss of the content rule itself: for the Open Multilingual Wordnet it looks for the first word of the name
  ("open"), not the corpus id `omw`. Left as written before the run.

The remaining question is DEC-0007: whether A-101 should read the generation in progress.

To rerun: the boxes' SQLite files are not committed (`*.sqlite` is ignored); their cards are in the JSON exports
beside them. A fresh rerun starts with empty boxes unless run 3's replay SQLite is present.
