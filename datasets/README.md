# datasets

Rung 1 of the ladder: datasets → registries → matrices → indices → codices.

Each file here is a source kept exactly as found (byte for byte, line endings included; `.gitattributes` stops git from rewriting them). `manifest.json` records where each one came from.

To add one: put the file here, add an entry to `manifest.json` with a new `id`, and push to main. The `ladder` workflow breaks it into registry pieces, rebuilds it from those pieces alone, and loads it into Neon only if the rebuild is byte-exact, then checks the copy in Neon the same way. Loaded rows are never changed; a corrected source gets a new `id`.

Each run's findings (repeated passages, headings that may be labels rather than concepts, terms shared with other codices) appear in the run summary on the Actions tab and as a downloadable `ladder-findings` file.
