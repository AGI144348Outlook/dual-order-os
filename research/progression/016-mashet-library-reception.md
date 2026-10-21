# 016 — How Echo receives Timothy's attached Mashet Dictionary/Library

Date: 2026-10-21. Before/after research thread: [Dual Order OS issue #3](https://github.com/AGI144348Outlook/dual-order-os/issues/3). Baseline integration commit: `ead836e484a660d4a02f42c855c25bc04a1da9d9`.

## Request and source

Timothy paused timeline development and supplied a new Dictionary/Library, asking to feed it to the Echo implementation in Dual Order OS and describe its reception. The input is a 773,600-byte PDF with SHA-256 `4566617ba5f2931343967e29f2c6ccbbbb583b159a9386ee9b7f3512460bdc15`.

The initial `file` utility incorrectly reported eight pages. `pdfinfo` and the 93 page separators from Poppler agree on **93 pages**. This correction and an amended exposure budget were published in issue #3 before any Echo exposure. The original issue plan is not silently rewritten.

`pdftotext -layout` extracted **133,607 Unicode characters**. A rendered sample of page 4 was inspected to compare the text and layout. This is a sample check, not a manual audit of every page. Extraction retains 1,317 right-to-left embedding controls and 1,317 matching directional-formatting controls; no niqqud stripping, spelling correction, OCR, bracket repair or Unicode normalization was applied. The PDF remains the reference for visual Hebrew ordering and layout.

The extraction contains **210 numbered candidate entries: 30 each for Aleph, Bet, Gimel, Dalet, He, Vav and Zayin**. Later glyph divider/blank pages are not treated as completed dictionary entries. A naive line-start heading parser initially counted 206; recognizing page-start headings recovered all 210. This was extraction preparation, not an Echo learning result.

## Method

The new observation harness, `tools/observe_library_intake.py`, uses the unchanged pinned Genesis implementation through `libraries.echo_workspace.genesis()`. It creates a fresh local instance, anchors its identity, and bootstraps the pinned core Lexicon's 1,000 spellings using the first listed sense per spelling. Other senses remain outside this legacy spelling-keyed projection. This is not a continuation of a permanently running remote Echo process.

The complete extracted text is supplied to the actual `AlgorithmMatrix.index_content` method as one source document, twice at most. After each exposure the existing Lobby is rebuilt and its orientation, typed study groups and generality scores are computed. Five short source-derived probes use the actual `AlgorithmicCommunicator`: the first Hebrew heading, its transliteration, a functional phrase, state-shift terms, and common words. No answers or verified VGM propositions are supplied. The full document is indexed; the communicator probes do not substitute for that exposure.

Separately, an explicit intake adapter stores a source card, 210 candidate-entry cards and two observation cards in SQLite. Candidate identities use source hash plus codepoint offset, rather than assuming headings, transliterations or family-local ordinals are globally unique. Cards retain the literal extracted heading/body, source hash, page references and character offsets. The adapter is new recording code; card creation is not a self-initiated Echo action or automatic admission of dictionary meanings.

## Actual results

| Measurement | Before exposure | After first | After second |
| --- | ---: | ---: | ---: |
| Indexed raw units | 2,759 | 6,021 | 6,021 |
| Existing WordAgents | 1,000 | 1,000 | 1,000 |
| Vocabulary ties | 2,713 | 3,554 | 3,554 |
| Recognized unique English content tokens from this source | 344 | 344 | 344 |
| Unrecognized unique English content tokens from this source | 1,896 | 1,896 | 1,896 |
| Identity valid | yes | yes | yes |

These are different measurements: raw units use whitespace splitting, whereas the communicator extracts English letter runs, removes stop words and filters short tokens. Their counts should not be directly equated or interpreted as comprehension percentages.

The first exposure changed two probe responses, involving state terms and common words. Three other probes remained unchanged. The second exposure changed none of the five probe responses and added no further units or ties, although document-frequency/transition counts increased. Repeating one source is not independent evidence for its claims.

The new transliteration probe remained a **GAP (not indexed)**. Its appearance in indexed source text did not create a WordAgent. The Hebrew-only heading produced **zero communicator tokens**, because this interface's tokenizer accepts English `[a-z]+` words only. The raw whitespace index can retain Hebrew-containing strings, but that is not glyph-level parsing or execution.

One existing word changed from ENTITY_NOUN to OBJECT_NOUN after exposure and acquired additional neighbors, including common function words. The preserved Lobby reconstructs definition-related links from shared transitions; document prose can therefore affect dictionary-derived associations without supplying a new validated definition. The observed change must not be described as verified semantic understanding.

The communicator prints messages such as `AcquisitionPlanner queued`, but this experiment does not start an acquisition worker or verify a persistent acquisition queue. It supplied no VGM claims and installed **zero executable algorithms**. Operational descriptions in the document remain source descriptions, not callable implementations or independently verified facts.

## Persistence and privacy

All **213 cards** survived closing and reopening SQLite, with matching logical contents. The original PDF bytes remained unchanged. The source PDF, extraction, full probe responses and catalog are retained locally at `/workspace/private-echo-intake/mashet-library-4566617b/`; the catalog is `reception.sqlite`. These source-bearing artifacts were not uploaded to GitHub or R2.

The public repository receives the observation code, synthetic parser tests, this narrative and aggregate `reports/echo-library-intake/summary.json`. The in-memory AlgorithmMatrix was not serialized for restart. What persists here is the source/candidate/observation catalog; reconstructing those associations later requires explicit source replay or a future state-persistence integration. No deployed Echo instance, authoritative glyph registry, or existing private tower was modified.

## Verification

All **97 Python regression tests passed locally**, including four new synthetic parser cases: literal Unicode/page-start preservation; repeated-title separation; family/glyph-divider boundaries; and unresolved/malformed source preservation. Fixtures contain no private document passages. Existing source emits a pre-existing invalid-escape SyntaxWarning; no test failure resulted.

Reproduce with the supplied original PDF and pinned core Lexicon, using a fresh output directory:

```sh
PYTHONHASHSEED=42 python tools/observe_library_intake.py --pdf PATH/TO/LIBRARY --archive PATH/TO/core-lexicon.zip --output PRIVATE/FRESH-DIRECTORY
python -m unittest discover -s tests -q
```

The script rejects a different PDF hash and refuses to overwrite an existing output directory. `pdftotext` must be installed. Future reproductions require their own published pre-test entry under the repository protocol. This documentation/code commit skips CI to avoid automatically starting other experiments outside this plan.

## Interpretation

Echo received the document as indexed experience and now has a separately preserved candidate-card representation. It did **not** acquire 210 usable lexical definitions, learn the constructed glyph compositions, or demonstrate comprehension of the state transitions. The concrete missing bridge is from a source-linked candidate library entry into an explicit, sense-aware lexical/algorithm contract that the existing query and execution interfaces can actually use. That is the next possible development, not an unreported part of this intake test.
