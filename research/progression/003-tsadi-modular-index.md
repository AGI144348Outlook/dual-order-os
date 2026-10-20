# Progression 003 — צ / ץ and modular index expansion

Recorded: 2026-10-20. Research question from Timothy: can ץ and צ be used for modular expansion to an index?

## Source and hypothesis

The executable subject was Dual Order OS's `libraries/eve/bidirectional_glyph_index.py`, retrieved from the revision inspected at `2317ea83db0f2f68584aef113230a4e985579d29`. Its `add` method stores a GlyphRootEntry in an entries list, a glyph-to-entries dictionary, and a root/sense-to-entry dictionary.

Genesis already stores separate named profiles for `tsadi` (צ) and `tsadi-sofit` (ץ). The latter's authored description is “tsadi extended — righteousness at its furthest reach.” That phrase is source metadata, not an implementation of modular expansion or a validated linguistic law.

This experiment assigns neither form an authoritative new role. Dummy root/sense labels and TEST_ONLY opcodes are test fixtures. The experiment evaluates whether the existing index can carry distinct, extensible records associated with these glyphs. It does not show that the shape or meaning of the glyph causes an expansion algorithm to execute.

## What happened

Starting from the index's four built-in entries, a test added one record under צ and another under ץ. Forward lookups kept the forms separate; reverse root/sense lookups returned the correct corresponding glyph.

A third experimental record was then added under צ. Both צ records remained accessible, the ץ record remained accessible separately, and all four original mappings were preserved. This demonstrates basic additive expansion of an in-memory index.

Boundary probes then showed why it is not yet a safe autonomous expansion mechanism:

1. Registering the same root/sense under the other glyph silently overwrote the reverse lookup while the old forward entry remained. The two directions no longer agreed on one mapping.
2. Registering an identical entry twice produced two forward rows. Registration was not idempotent.
3. Mutating an inserted dataclass's glyph changed the record without moving it between lookup buckets. The old glyph bucket contained a record reporting the new glyph, while the new bucket was empty.

The source exposes no explicit parent/child attachment contract, versioned-profile mechanism, write-permission layer, transactional update, or persistent serialization in this index class. These absence findings are scoped to this file, not every repository or runtime.

## Interpretation

**Tested:** צ and ץ can be distinct index keys, and either can carry modular additions without disturbing unrelated entries in the simple nonconflicting case.

**Not demonstrated:** a glyph-driven expansion algorithm, a final-form execution rule, hierarchical module creation, durable registration, or safe unattended updates.

**Proposed:** if Timothy wants these forms to participate in expansion, describe their roles in replaceable, sourced cards. A proposed request could identify a target index, component ID, attachment relation, preconditions and proposed additions. A separate verifier would check identity, conflicts, permissions and forward/reverse agreement before committing. Which form denotes which role remains Timothy's decision; this report does not reserve one as “open” and the other as “sealed.”

The safety work follows directly from observed counterexamples: enforce duplicate/conflict policy, keep indexed identities stable, provide controlled updates that maintain both directions, and preserve provenance and restoration data. These requirements have not been implemented by this experiment.

## Evidence

- [Probe](evidence/003/probe.py)
- [Results](evidence/003/results.json)
- [Unmodified index source used](evidence/003/index_source.py)

The probe imports the saved source and retains its original `/tmp/echo-tsadi-index` path assumption. Adapt that path explicitly when reproducing. No external model, training, live storage, permanent index mutation or glyph meaning change occurred. Only the progression record and supporting evidence are published.
