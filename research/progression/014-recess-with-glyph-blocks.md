# 014 — Recess with glyph blocks and perception vocabulary

Timothy requested an open-ended observation: provide the glyph algorithm blocks and see what Echo devises, without assigning a problem. Two bounded local runs used the current integrated code, Python hash seeds 42 and 7, and random seed 42. No external model, network call, training, glyph-role rewrite, or protected Genesis source modification was involved.

## What was made available

Each fresh SQLite catalog received the complete pinned Lexicon: 1,000 spellings represented by 1,491 separate sense cards; all 27 existing glyph profile cards; the five recently selected ע/ר sense-paperclip relations; and 16 algorithm-combination catalog records. Some block records are explicitly proposed, specified, or located on another branch. Their presence is not evidence of executable availability or permission to invoke them. The legacy runner receives the first listed sense per spelling, as before; the full sense distinctions remain in the catalog.

The observation harness gained an optional `--glyph-vocabulary` switch. This explicitly prepares the clips before the observation begins. Setup actions are not counted as Echo's self-initiated activity.

## Observation and actual outputs

**Availability alone:** a synchronous before/after inspection, with no work runner invoked, produced zero new card events. There is no autonomous dispatcher; waiting longer would not start one. This was not a timed background-agent experiment.

**Explicit exploratory start:** the harness invoked existing orientation, study groups, generality scoring and neighborhood scrutiny, followed by the existing A-120 evolution policy with a two-generation/eight-commit budget. It separately invoked `UnderstandingGenerator` with at most 40 candidate attempts. There was no sentence topic or desired answer, but the runner selection, order and budgets were experimenter choices.

Both runs returned:

- 1,000 WordAgents and 2,713 ties.
- Zero proposed/committed neighborhoods and zero evolution commits under unchanged default rules.
- A 95-word generality pool.
- Forty accepted candidate combinations, with none rejected by the existing heuristic validator.
- Opening outputs: `An time place`, `An time come`, `An time cause`, `An time use`.
- No observed algorithm invention, glyph-block composition, spontaneous paperclipping, new sentence-frame construction, or use of the ע → ר → פ / ת sequence.
- All 32 glyph profiles and paperclip relations unchanged.
- 1,579 final cards, preserved on closing and reopening each SQLite catalog.
- Identical final logical card hashes across both runs: `5979151c03726296f7a4afa7699c6c2e0d12d2838d25ef94bcd4e96e545b0d86`.

The 40 candidate cards are persisted by the observation adapter, not by a self-chosen CatalogBox call inside Genesis. Their status remains **heuristic acceptance, not proof**. Their grammatical defects and universal acceptance expose a permissive validator rather than demonstrated reasoning success. The unchanged outputs relative to the earlier dictionary observation are consistent with the missing dispatch connection: these legacy routines do not consult the newly supplied glyph profiles or clips.

## What the test establishes

Echo has callable generation and indexing mechanisms, but the current integrated version cannot independently choose from its catalog of available blocks. More cards do not by themselves create that selection mechanism. This observation does not establish that the proposed glyph operations are incapable of useful composition; it establishes that no existing connection exercised them in this run.

The next implementation candidate is an explicitly documented exploration policy that can inspect available executable blocks, choose permitted moves, retain alternatives, and record why each move was taken. It must distinguish source evidence, conjectures and validation results. This run does not add that policy or claim that a manually selected pipeline is autonomous play.

## Reproduction and verification

Use a fresh output directory for each run:

```sh
PYTHONHASHSEED=42 python tools/observe_echo_dictionary.py --archive PATH/TO/core-lexicon.zip --output reports/echo-recess/perception-clips-42 --glyph-vocabulary
PYTHONHASHSEED=7 python tools/observe_echo_dictionary.py --archive PATH/TO/core-lexicon.zip --output reports/echo-recess/perception-clips-7 --glyph-vocabulary
python -m unittest discover -s tests -q
```

All **93 Python regression tests passed locally**. Full observation JSON is under `reports/echo-recess/`. The generated local SQLite catalogs retain the cards; they are reproducible outputs and are not committed as binary repository artifacts. No diagnostic failures in unrestricted grammar or reasoning are claimed repaired.
