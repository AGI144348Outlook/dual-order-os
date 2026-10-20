# Group Canvas private file cabinet — integration intake

Status: **pending review, not integrated or deployed**.

Source: [Group_Canvas, experiment/hierarchy-tower](https://github.com/AGI144348Outlook/Group_Canvas/tree/20c8c27352d063c94e54ca6bd17c1a8e747ca0bf), pinned at `20c8c27352d063c94e54ca6bd17c1a8e747ca0bf`.

## Start here

- [Cabinet UI](source/public/tower/files.html)
- [Cabinet features and limitations](source/experiments/hierarchy-tower/FILING.md)
- [Filing service](source/experiments/hierarchy-tower/filing-service.js)
- [Upload service](source/experiments/hierarchy-tower/upload-service.js)
- [Worker entry point](source/experiments/hierarchy-tower/worker.js)
- [Filing tests](source/experiments/hierarchy-tower/filing.test.js)
- [File inventory and source hashes](PROVENANCE.json)

Original files are preserved under `source/`, retaining their relative paths and imports. The snapshot includes the tower's connected UI/assets and the session-tower and card-chat modules required by the existing service imports. Including these dependencies does not authorize activating character processing, adapters, or hosted AI in Genesis.

The cabinet supports operator-code access, phone/Android file-provider selection (including Drive when available), resumable multipart uploads, flat collections, listing, rename/move labels, downloads, and explicit deletion. Consult the preserved source documentation for its limitations; this intake is not a new security or live-storage certification.

Only repository source is copied. No R2 objects, conversation datasets, live Durable Object state, operator codes, API keys, or cloud credentials are transferred. The source Wrangler files preserve existing resource names as historical configuration, not authorization to deploy against them.

The original package metadata is retained for context; its root npm scripts refer to the full Group Canvas repository and are not a complete project launcher for this extracted snapshot. The included tests can be selected directly with Node:

```sh
cd integration-inbox/group-canvas-file-cabinet/source
node --test experiments/hierarchy-tower/*.test.js experiments/session-towers/*.test.js experiments/card-chat/*.test.js
```

No live-check script or deployment is run by this intake. Genesis source, runtime registrations, existing workflows, and the Group Canvas repository are unchanged.
