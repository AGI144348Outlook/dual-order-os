# Demo: extracting candidate persona sessions

**Client problem:** including every message mentioning a name pollutes a character's memory.

From the repository root, with Node.js 22 or newer:

```sh
node portfolio/demos/persona-filter/showcase.js
```

No installation, credentials, network calls, model calls or personal data.

Eight invented messages demonstrate:
1. Talking about Julian does not start a Julian session in this fixture.
2. Addressing Julian selects a direct prompt/reply candidate.
3. A subsequent unnamed reply is an inherited candidate.
4. Addressing Nexus closes the Julian session before the other reply is paired.

Expected output: two candidate pairs (`direct`, `inherited`), both exclusion checks true, and human review required.

## Existing code being demonstrated

The vendor directory preserves two unmodified files from Group_Canvas commit `8610aa9cfc6bc5437fee47ee348797c06850c5b5`:
- `experiments/session-towers/engine.js`, Git blob `c0ae653986b22bef51118a357b0764a4bb402f2c`.
- `public/tower/archive-parser.js`, Git blob `4f5d1a4d99ea260cf59bd3345b801bb23abd137a`.

[Upstream policy and limits](https://github.com/AGI144348Outlook/Group_Canvas/blob/8610aa9cfc6bc5437fee47ee348797c06850c5b5/experiments/session-towers/README.md). Only the wrapper and synthetic fixture are new. This packaging does not introduce a new license grant.

This is deterministic candidate attribution for the names/rules in the existing policy. It does not identify arbitrary speakers, prove persona continuity, train a model, scan private R2 or demonstrate a completed subscription service. Quotes, aliases, mixed personas and missing timestamps can require review.

## 60-second recording outline

Explain the difference between mentioning and addressing someone, run the command, show the two retained pairs and the persona switch, then state that the user reviews attribution before memory ingestion.
