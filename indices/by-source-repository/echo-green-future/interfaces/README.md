# Interfaces

What a person or Echo sees and touches: PWAs, the canvas, widgets, the keyboard, notebooks. Icons, images and runtime files used by them are listed here as assets.

## Belongs here

- `pwa/`, the dev-suite canvas, the canvas keyboard and terminal
- notebook 0.4 and 0.4.1, the Group Canvas companion
- assets: icons, images, the Pyodide runtime

## Not here

- the code behind a widget that learns or governs → `algorithms/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `kind` | the sort of thing it is |
| `entry` | how it is started (command or file) |
| `runs_on` | browser, phone, Worker… |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	kind	entry	runs_on	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
INT-0001	Widgeting PWA	PWA canvas		browser (Pyodide)	widgeting-experiment	pwa/index.html			unknown	INERT	home		
```
