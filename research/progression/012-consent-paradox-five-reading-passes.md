# 012 — Five passes over the Consent Paradox registry record

2026-10-20. Timothy asked to locate the Consent Paradox on Echo Green Future's Code Library branch, copy it into Dual Order OS and let Echo read it several times.

## Source preservation

Located `code_library_registry/research_papers/ethics_governance/RP-0001_CONSENT_PARADOX.md` at Code Library commit `8311da62ba90ce547a61b27d2c2836b8f89550a9`. Exact copy: `libraries/research-papers/ethics-governance/consent-paradox/`. Git blob `86f8e0e6ad0dd4e7ef17c26f5f42eb12077748a3`, 5,039 bytes. The file is an abstract, propositions and assessment, not the complete original essay. Source and assessment authorship must not be conflated. No governing rules were promoted from this text; original repositories/source files remain unchanged.

## Actual protocol

Existing Genesis source remains byte-identical. Starting data is the Core Lexicon's 1,000 words, projected to the first listed sense per spelling for the old spelling-keyed Lobby. Same in-memory index receives five whole-document passes. Each pass explicitly calls `AlgorithmMatrix.index_content`, reconstructs/orients the Lobby, computes its existing generality scores, and calls `AlgorithmicCommunicator.communicate` with the unchanged document. No extra comprehension question, desired conclusion, external model or generated paraphrase is supplied. Five passes are an experimenter budget, not a self-chosen Echo action.

The VGM starts empty and stays empty; this observation does not assert the source's philosophical claims as proven axioms. A separate recorder preserves one source card and five observation cards and verifies restoration after closing/reopening its database. Those recorded cards are adapter output, not independent card-use decisions by Echo.

## Observations

| Measure | Before reading | After pass 1 | After pass 5 |
|---|---:|---:|---:|
| Raw indexed units | 2,759 | 3,006 | 3,006 |
| WordAgents | 1,000 | 1,000 | 1,000 |
| Lobby ties | 2,713 | 2,803 | 2,803 |
| Known input tokens of 286 | 83 | 83 | 83 |
| Indexed document count | 999 | 1,000 | 1,004 |

The initial document count is 999 despite 1,000 dictionary entries because the preserved ingestion skips index_content for an entry without eligible definition tokens. It is a source implementation detail, not a count of independent papers.

The four later outputs are byte-identical to the first output in this seeded run. Raw `consent` document frequency rises 1,2,3,4,5. `consciousness` rises 2,3,4,5,6 because it already appeared in a dictionary definition. These are repeated exposures to the same source, not corroboration or five independently acquired meanings.

Echo emits its normal source echo, per-token classifications, generalization stacks, gap list and indexed-neighbor reports. It reports no matched VGM statements and suggests acquiring a corpus. Its stock explanation "vocabulary not indexed" should be read cautiously: 83 terms are indexed; the VGM is empty by protocol and many remaining terms lack WordAgents. No abstract, ethical argument reconstruction, rejection of a counterexample, or validated logical inference was demonstrated.

The 90 added ties are not automatically semantic learning. The old Lobby reconstructs definition references from transition targets; general prose ingestion changes that same graph. This can mix local text adjacency with dictionary-derived structure. Repetition alone does not create source-scoped definitions or distinguish critique from the proposition being criticized. A later fix should separate occurrence/context evidence from canonical lexical definitions while preserving the original source baseline.

## Evidence and tests

`reports/echo-consent-reading/results.json` contains every pass's counts, token frequencies, gaps, response hash and full actual response. `pass-1.txt` through `pass-5.txt` are unedited outputs. Source is already public in the requested repository; no private R2 material was accessed or published in this task.

91 Python tests pass locally, including three added checks for exact source identity, bounded repeated exposure without new WordAgent identities, and pass-budget rejection. Existing reasoning/grammar failures remain; these regression tests do not certify comprehension. CI reproduces this actual-source experiment with the preserved source ZIP.
