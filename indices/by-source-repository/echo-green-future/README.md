# Echo_Green_Future inventory (2026-10-22)

Read-only inventory of all 42 branches, taken for the integration of Echo (option A: a separate
integration branch; Contract 000 mirrors and `main` are left untouched). Nothing was moved, pruned or deleted.

| File | One row per | Columns |
|---|---|---|
| `MANIFEST-by-branch.tsv` | file in a branch (5,003 rows) | branch, path, blob_sha, bytes, branches_with_identical_content, versions_of_this_path |
| `CONTENT-by-fingerprint.tsv` | distinct file content (2,193 rows) | blob_sha, bytes, n_branches, n_paths, paths, branches |
| `inventory.json` | branch summaries, drifting paths, zip file lists, totals | see keys |

`blob_sha` is git's own fingerprint, so any copy can be checked against its source. Zip contents were
listed, never extracted or run. The five `conversations-00x.json` exports in `chatgpt-conversation-archive`
were listed only, not opened. Commit counts and ancestry come from a full-history pass; sizes from the branch tips
as of 2026-10-23 03:09 UTC.
