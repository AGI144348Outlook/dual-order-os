# Echo_Green_Future inventory

The map of everything in Echo_Green_Future, built for integrating Echo (option A: a separate integration
branch; the Contract 000 mirrors and `main` are left untouched). The inventory points at files where they are.
It never copies, moves or deletes them.

## Census (done 2026-10-22)

A first pass over all 42 branches, file by file. The folders below are filled from it by later sweeps.

| File | One row per | Columns |
|---|---|---|
| `MANIFEST-by-branch.tsv` | file in a branch (5,003 rows) | branch, path, blob_sha, bytes, branches_with_identical_content, versions_of_this_path |
| `CONTENT-by-fingerprint.tsv` | distinct file content (2,193 rows) | blob_sha, bytes, n_branches, n_paths, paths, branches |
| `inventory.json` | branch summaries, drifting paths, zip file lists, totals | see keys |

Commit counts and ancestry come from a full-history pass; sizes from the branch tips as of 2026-10-23 03:09 UTC.

## Folders

Each folder has a `README.md` (what belongs, what doesn't, its row format, an example) and an `INDEX.tsv`
that the sweeps fill.

| Group | Folders |
|---|---|
| The seven Library sub-libraries (Contract 000) | [`registries/`](registries/) · [`matrices/`](matrices/) · [`indices/`](indices/) · [`codices/`](codices/) · [`logics/`](logics/) · [`algorithms/`](algorithms/) · [`formulas/`](formulas/) |
| How Echo is built and talks | [`tools/`](tools/) · [`schemas/`](schemas/) · [`protocols/`](protocols/) · [`interfaces/`](interfaces/) |
| What Echo learns from and leaves behind | [`experiments/`](experiments/) · [`data/`](data/) · [`records/`](records/) · [`archives/`](archives/) |
| Running it | [`automation/`](automation/) · [`deployments/`](deployments/) · [`dependencies/`](dependencies/) |
| Holding it together | [`governance/`](governance/) · [`glossary/`](glossary/) · [`maps/`](maps/) · [`decisions/`](decisions/) |

## Shared columns

Every `INDEX.tsv` starts with `id` and `name`, then the folder's own columns, then these:

| Column | Meaning |
| --- | --- |
| `id` | stable inventory id: a folder prefix and a number (`ALG-0158`, `SCH-0001`). Never reused. |
| `name` | the item's own name, as its source writes it |
| `branch` | branch where this copy was found |
| `path` | path inside that branch |
| `blob_sha` | git's fingerprint of the file, so any copy can be checked against the source |
| `commit` | the branch commit the sweep read |
| `made_by` | `timothy`, `claude`, `chatgpt`, `codex`, `gemini` or `unknown`, as the commit or file states |
| `status` | `INERT`, `KEPT`, `PRUNED` or `DEFERRED` (Contract 000's terms; every row starts `INERT`) |
| `home_or_ref` | `home` for the item's one primary folder, `ref` for a cross-reference from another folder |
| `glyph` | one of the 27 glyph matrices (א … ת, ך ם ן ף ץ) if the item belongs to one; blank otherwise |
| `notes` | anything that does not fit a column |

## Rules

1. **Inert.** Rows point at files by branch, path and fingerprint. Nothing is copied into the inventory.
2. **One home, cross-references elsewhere.** An item that is two kinds at once (an algorithm that is also a matrix) gets one `home` row and a `ref` row in each other folder. This rule is provisional until ruled on in [`decisions/`](decisions/).
3. **Nothing is Canon.** When two versions differ, both get rows. Neither wins until Timothy rules.
4. **Status changes carry reasons.** Moving a row away from `INERT` needs a reason in its `notes` or a linked decision.
5. **Sensitive material is listed, never opened or copied.** The `chatgpt-conversation-archive` exports (`conversations-000`, `-001`, `-002`, `-005.json` and `shared_conversations.json`) are listed only.
6. **Never secret values.** Deployments and automation record secret *names* only.
7. **Implied vs written.** A schema, protocol or meaning extracted from code is marked as implied, not presented as authored.
