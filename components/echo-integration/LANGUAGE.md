# Branch-derived language interfaces

Two source families were adopted after the integrated workspace's diagnostic failures:

1. `autonomous-agency`, commit `d553f503ff12f3f53f7f7b55df74fb228a60fc97`, `experiments/evidence_bound_articulation_011.py`: explicit agent/action/patient realization and abstention. The full source is preserved, but only its three decision/realization functions are loaded; its top-level experiment is not run on import.
2. `ksm-recess-wholesale`, commit `82810112a959dc094dcf40238419cffca6863670`, selected `echo/language/` modules: typed EMEL parse trees, a restricted English parser/renderer, type/lexical/discourse audits and parse-back comparison.

Ten recovered files are preserved unchanged and hash-checked using [branch-components.json](../../matrices/echo-integration/branch-components.json). New glue is in [echo_language.py](../../libraries/echo_language.py). Historical registry labels are source-specific, not replacements for current user-directed glyph cards. Other source modules were not installed wholesale: `compose.py` plans particular benchmark-result records, while the WordNet-dependent sense module and broader operator execution need separate integration.

## Explicit assertions and relative support

```python
from libraries.echo_workspace import EchoWorkspace
with EchoWorkspace('echo.sqlite', capabilities=EchoWorkspace.ALL_CAPABILITIES) as echo:
    for word in ('dog', 'mammal', 'animal'):
        echo.put_word(word, word, 'a kind of entity', department='noun')
    echo.assert_is_a('r1', 'dog', 'mammal')
    echo.assert_is_a('r2', 'mammal', 'animal')
    result = echo.query({'operation': 'language', 'text': 'dog is_a animal'})
    # english: A dog is an animal.  evidence: r1, r2
```

Assertions are caller-supplied assumptions, not independently verified world knowledge. The adapter follows explicit subtype paths. Paperclips, token overlap and glyph stamps are never converted into subtype evidence. Missing paths remain UNKNOWN; their absence does not prove a negation. This deliberately avoids a recovered audit's closed-world assumption that a missing path among known terms is a contradiction.

`language` accepts EMEL or `surface: 'english'` for a restricted grammar. It checks type and lexical membership, renders the tree, and compares a reverse parse. It returns an accepted `english` sentence only for supported claims passing its audits. A withheld result may contain `rendered_candidate` for diagnosis; that candidate must not be presented as an accepted factual answer.

The read API also accepts `articulate` with `nodes` and explicit `agent_of`/`patient_of` edges. It can construct a singular transitive sentence or abstain. New guards reject ambiguous/multiple role assignments instead of relying on the source trial's last-write-wins dictionary behavior. Single lower-case word terms are required. This source grammar mishandles mass nouns, irregular verbs and some article sounds; those failures remain recorded rather than hidden.

No arbitrary user code is evaluated. The only compiled functions are selected from trusted pinned source; request data is never compiled. Parsing a glyph application or `%` does not execute that operation. In particular it does not implement §DSL§ inversion or Presentiation. These are constrained interfaces, not a general English/Hebrew parser, universal proof engine, or trained language model. Optional ambient WordNet corpora do not determine adapter lexical membership.
