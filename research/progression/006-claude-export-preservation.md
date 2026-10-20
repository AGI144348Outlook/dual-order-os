# Progression 006 — Claude export preservation in shared private R2

Recorded: 2026-10-20. Timothy supplied expiring Claude export links, then uploaded the available archives to Echo Green Future's main/docs directory and directed that they be preserved in the same private R2 bucket as GPT conversations, under a separate folder.

## Source and scope

The source was pinned at Echo Green Future commit `dfb33e530338517f9837eeb35156245adf9c2bbe`. Six ZIP archives and the original export manifest were present. No frames archive was located in that revision.

Earlier direct-download attempts were blocked by the workspace's networking/access environment and did not establish successful retrieval. The completed route used GitHub Actions with existing Cloudflare credentials. No expiring download link was required for the successful transfer.

The transfer code and metadata manifest were committed to Group Canvas's experiment/hierarchy-tower branch at `b12bfcd09c13a4368785a5d7ae285b3d1c687b11`. The workflow accesses a fixed bucket and destination prefix; it does not create a bucket, change public-access settings, deploy a worker, merge conversations, or train a model.

## Verified outcome

[Actions run 39488581312](https://github.com/AGI144348Outlook/Group_Canvas/actions/runs/39488581312) completed successfully. The copy step reported each source file copied and verified:

- artifact_data-000.zip
- claude_code_cloud-000.zip
- conversations-000.zip
- light_metadata-000.zip
- memories-000.zip
- projects-000.zip
- the original export manifest JSON

Destination: existing private bucket `group-canvas-citadel-sources`, prefix `claude-exports/2026-10-20/`. Original filenames are retained. A separate `transfer-provenance.json` records source identities and verified SHA-256 hashes.

The six ZIP archives total 18,054,863 bytes. The original manifest is an additional 2,120 bytes. The manifest described seven archive categories; therefore seven copied files (six ZIPs plus manifest) must not be mistaken for seven complete archive categories. **frames-000.zip remains missing.**

All sources were downloaded and checked against pinned Git blob identities and sizes before uploads. ZIP CRC checks ran without extracting or executing content. Every R2 copy was fully read back and compared by SHA-256 and byte count; existing matching objects can be reused, while mismatched objects stop the workflow. The provenance object also passed the copy/read-back path.

Six synthetic tests passed in the same Actions job, covering retry reuse, collision preservation, truncated sources, source identity mismatch, corrupt read-back, and restricted destination/path validation. These tests accompany, but do not substitute for, the live successful read-back evidence.

A metadata-only Actions artifact (`claude-export-transfer-metadata`, artifact ID 12294128764) was produced with seven-day retention. The durable private provenance object is the longer-lived source record. Export contents and credential values were not printed to logs or committed to Group Canvas.

## Limits and next work

This is preservation, not a content investigation. No claim is made here that the Presentiation or inversion/§DSL§ discussions were recovered from the archives. Those questions remain for a subsequent authorized read/search.

The destination is a physical R2 prefix. It is not automatically entered in the existing cabinet's collection inventory; that requires a separate supported registration path.

Echo Green Future was publicly visible at inspection. The existing source archives there were not removed, and repository visibility/history were not changed. Private R2 preservation does not eliminate public source exposure. This was disclosed to Timothy without independently changing repository settings.

The original archives, existing GPT objects, Genesis code and Dual Order executable components were unchanged by the transfer. This report records the verified storage step and the missing category explicitly.

## Follow-up — source upload deletion authorized by Timothy

On 2026-10-20, after the R2 transfer succeeded, Timothy explicitly requested deletion of the exported Claude files from the source repository. Echo Green Future commit `8402a45b41a253cc6e405e16ec139bc4b0a30e86` removes exactly the six transferred ZIPs and original export manifest from current `main/docs/`. Each candidate's Git blob identity was checked against the pinned transfer manifest before removal. The resulting diff contained only those seven deletions; CI was skipped for this file cleanup.

The private R2 copies were not deleted or changed. This is ordinary branch-tip deletion, not history rewriting: the original upload commit and file contents remain retrievable from Git history. It does not establish complete erasure of previously public copies. No other source documentation or executable code was removed.
