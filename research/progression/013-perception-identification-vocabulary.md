# Perception and identification vocabulary clipping

Timothy requested vocabulary cards for ע perception and ר identification/recognition, keeping פ naming and ת labeling distinct. The experimental order is ע → ר → פ / ת. This is a scoped workflow proposal, not a newly established universal invariant.

The pinned original core Lexicon was inspected directly. Four source verb senses were selected for ע: **see**, **look**, **hear**, and **sense**. **Match**, in its comparison verb sense, was selected as supporting vocabulary for ר. Matching characteristics does not establish that two observations identify the same entity.

The following candidates are absent from the 1,000-word sense dictionary and remain acquisition targets, not fabricated dictionary records:

| Tool | Proposed additional vocabulary |
| --- | --- |
| ע | perceive, observe, notice, detect, distinguish |
| ר | identify, recognize, classify, compare, verify |

The explicit adapter ingests source senses into inert lexical cards, then uses the existing צ paperclip operation to associate selected sense IDs with existing glyph profiles. No glyph keyword profile or executable authority is revised. The noun senses of **match** (fire-lighting object), **look** (facial expression), and **sense** (awareness) remain available as separate cards but are not clipped by this experiment. Synonym lists are not treated as equivalent senses.

## Actual results

Five selected senses were clipped. SQLite close/reopen preserved all cards and relations; profile revisions remained unchanged; a read-only caller was denied a paperclip write. Two additional regression tests verify sense selection, duplicate-call idempotency, persistence, separate tool sets, and permission rejection. The full local Python regression suite passed **93 tests**.

These tests establish association and storage behavior. They do not demonstrate visual perception, independent identification, comprehension, or automatic vocabulary selection. Codex selected the candidates; Echo's existing governed card adapter performed the requested associations. Original Genesis source remains unchanged.

## Reproduce

```sh
python tools/test_glyph_vocabulary.py --archive PATH/TO/core-lexicon.zip --database vocabulary.sqlite
python -m unittest discover -s tests -q
```

Omit `--database` to use a temporary catalog for a repeatable test. Results are written to `reports/echo-glyph-vocabulary/results.json`; the optional database retains the actual operational cards for subsequent experiments. Source archive Git blob: `370e23a301badb6362eac29682afc5bba9e8d5a4`, member `core-lexicon/words.json`. Source definitions are preserved as supplied, without claiming independent linguistic verification.

## Next discriminating test

Supply observations as evidence cards, ask ר to choose among explicitly registered candidate identities, and require an unresolved result when evidence is ambiguous. Only after an identification decision should a separate פ naming proposal or ת associative label be recorded. An identifier can also be supplied directly by a registry; this sequence must not prohibit that route. No such recognition algorithm is claimed implemented by this vocabulary experiment.
