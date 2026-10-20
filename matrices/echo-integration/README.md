# Echo integration Matrix

The [source manifest](source-manifest.json) pins all 128 files of the Genesis Documentary snapshot. The original files are preserved under `vendor/echo-genesis/` without modifications. New runtime state remains in a caller-selected SQLite catalog, not committed to Git.

Component relationships:

```mermaid
flowchart TD
    A[Preserved Genesis snapshot] --> B[Original indexer and Lobby]
    C[Versioned CatalogBox] --> D[EchoWorkspace adapter]
    D --> B
    D --> E[Typed paperclip relations]
    D --> F[Evidence-bearing glyph stamps]
    E --> C
    F --> C
    C --> G[Pinned templates and restored configurations]
    G --> H[Descriptive configuration graph]
    H -. definition unresolved .-> I[§DSL§ inversion]
    J[Archived cabinet and lexicon sources] --> A
```

The dotted relation is explicitly unresolved. Archived cabinet code is not a live connection to R2 or the local catalog. [Component guide](../../components/echo-integration/README.md).
