# 010 — Question tags and identification-through-transfer curriculum

2026-10-20. Timothy deferred pictures and requested continued text-based developmental stages and question tagging.

Implemented `libraries/echo_question_tags.py`, with a dedicated guide at `libraries/algorithms/question-tagging/README.md`. It separates canonical lexical senses, provisional possible-question annotations, and event-specific answer bindings. These annotations do not overwrite words, definitions, glyphs, or previous cards. They are revision-pinned and stale annotations can be detected after sense updates.

Default rule: noun sense -> possible What. Supplied categories with provenance can add Who, Where, When, How, Why or quantity roles. A sense can have several possibilities. Keyword scans for person/place/time create review hints only and do not promote categories. This avoids classifying a clock as a temporal interval merely because its definition mentions time. No blanket adverb -> How rule.

`answer_role` accepts already-structured event/role facts with IDs and explicit polarity. It returns SUPPORTED, UNKNOWN, WITHHOLD or ABSTAIN; it keeps events and agent/patient roles separate, requires person typing for Who, withholds contradiction and does not invent ownership or causes. Which remains unsupported without an alternative set and selection criterion. Counts vs amounts/units are unresolved. No natural-language passage/question parser or coreference engine was implemented. Calling this structured lookup comprehension would overstate the result.

## Actual data check

The unchanged pinned Core Lexicon ZIP supplies 1,000 words and 1,491 sense cards. A separate annotation is persisted for every sense: 1,491 annotations, including 658 noun senses with a provisional What tag. Keyword scanning flags 80 temporal, 64 spatial and 71 person-related senses for review. Counts can overlap. Zero category hints are promoted automatically. All annotations survive database reopening. Reproduce with `python tools/run_question_tag_intake.py --archive PATH --output reports/echo-question-tags/dictionary-intake.json`.

## Tests and curriculum boundaries

78 Python tests pass locally: previous 61 plus 17 new checks for multirole temporal categories, no blanket adverb/person assumptions, provenance, candidate-only definition hints, idempotence/revision pins, evidence-backed answers, cross-event isolation, missing ownership, negation, contradiction, person typing, role reversal, missing causes, unsupported Which, narrow name transfer and malformed evidence. These are interface/regression tests, not a held-out comprehension benchmark or evidence of learning.

The curriculum guide covers identification, structure, comprehension, generalization, inference, composition, Recursive Return and transfer. For each it requires a pretest, recorded lesson/state change, guided practice, frozen independent test, restart/retention, transfer, and earlier-skill regression. This is a plan with limited implemented supporting mechanisms, not eight mastered stages. Source answer keys must stay outside runtime evidence. Developer code changes and algorithmic card adaptation must be reported separately.

The mapped-combination library now has 15 entries, adding QUESTION-TAGS. Existing dictionary observation runs continue to disclose explicit starts and lack of autonomous dispatch; their current algorithm-block inventory increases from 14 to 15. This changes inventory, not spontaneous agency. No protected Genesis code, Algorithm 000, authoritative glyph semantics or Generalized Evaluator definitions changed. No images, external models, training or deployment.
