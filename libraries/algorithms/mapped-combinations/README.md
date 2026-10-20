# Mapped algorithm combinations

Experimental library on `integration/echo-genesis-unified`; original Genesis source remains unchanged.

`catalog.json` maps each combination to relative source files and callable/class names. These are inert index records, not executable strings. `recipes.py` provides explicit Python entry points for selected existing combinations. No Algorithm 000 authority or glyph invariant is changed. New CARD IDs are library identifiers, not official algorithm numbers.

| ID | Combination | Status |
|---|---|---|
| GEN-EXPRESSION | A-141 stack → A-142 VGM query → A-143 descent → A-144 composition / A-145 input | Existing Genesis implementation; heuristic genus selection and substitutions |
| GEN-UNDERSTANDING | A-125 vocabulary pool → generator → A-126 check → A-127 VGM | Existing candidate generator; acceptance is not semantic proof |
| GEN-LOGIC | A-127 → A-146 specialization/composition/causal/conditional candidates | Existing; unsound inference challenges remain visible |
| LOBBY-EVOLUTION | A-120 measure → diagnose → propose → validate → commit | Existing bounded runner; goals and policy already programmed |
| CARD-SENTENCE | sense cards → position cards → subtype path → generalize/specialize → render | New, tested, restricted positive existential SVO |
| CARD-RETURN | position IDs → suspend → branch → resume → insert → re-audit | Proposed only; version history alone is not Recursive Return |
| CARD-CLIP | canonical cards → צ paperclip → persistent relationship | Existing tested workspace interface |
| CARD-STAMP | vocabulary + explicit profile keywords → ת association → evidence | Existing tested association, not truth certification |
| CARD-TEMPLATE | cards + pinned references → template → restored configuration | Existing tested catalog mechanism |
| EVIDENCE-LANGUAGE | records + typed parser → audit → evidence path → articulation/withholding | Existing tested bounded language wrapper |
| ROLE-ARTICULATION | agent/patient edges → ambiguity checks → clause realizer | Existing bounded wrapper; known mass-noun/irregular/article failures |
| MIRROR-RETURN | hypernym grammar → A-145 MirrorStep → bounded repeat | Separate branch, not merged here; not indexed Recursive Return |
| JOINT-SENSE | alternative sense sets → joint coherence selection | Source on main; WordNet/NLTK dependency; not integrated into card prototype |
| QUESTION-TAGS | sense-specific affordances → contextual roles → supplied evidence → answer/withhold | New bounded prototype; no free-text extraction |
| ECHO-TIMELINE | provider records → UTC ordering → source cards → bounded Canvas view | New deterministic private-source index; no inferred milestones |
| DSL-INVERSION | Registry → % → infrastructural §DSL§ → governed manifestations | Specification only; not implemented by these recipes |

## Use

Run `python -m unittest discover -s tests -v` from repository root.
Run `PYTHONHASHSEED=42 python tools/observe_echo_dictionary.py --archive PATH --output reports/echo-cards/run-42` for a bounded observation. The source ZIP must match the preserved artifact's Git blob identity. No archive code is executed.

The experiment separates idle availability from explicit starts of existing runners. Supplying a library does not create a dispatcher. All dictionary senses become inert cards, but the old Genesis index receives the first sense per word because its data model supports one record per spelling. Every dropped alternative in that legacy projection remains in the sense-card catalog. No automatic subtype edges are imported from the mixed-POS Chinese export. No external models, training, network acquisition, or deployment.

Sentence positions are not canonical vocabulary residents. Replacement changes a position's selection, not the selected resident's identity. Reordering keeps semantic roles attached. Only six explicit singular verb forms are rendered; unsupported predicates abstain. Countability, broad morphology and full grammar remain unresolved.
