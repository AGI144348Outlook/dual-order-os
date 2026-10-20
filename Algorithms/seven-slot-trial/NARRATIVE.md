# Seven invariant slot identities: first autonomous assignment experiment

The experiment kept ע פ צ ק ר ש ת fixed as seven card slots, without assigning intrinsic glyph meanings. Ten executable filtering operations were supplied as a candidate toolbox. Echo's existing UCB selection, outcome recording and generation checkpoint routines compared 120 seven-function configurations over 600 selection trials. There were 28 training cases and 21 held-out cases with different subject names and contexts.

Each case contained one supported target record and seven distractors: wrong subject, relation, context, condition, polarity, time, or missing evidence. The curriculum was deliberately constructed to require these seven dimensions. It therefore tests bounded configuration selection, not discovery of what real-world context universally requires.

Echo's selected configuration retained the seven corresponding filters and excluded three redundant checks (nonempty object, present identifier, dictionary-shaped record). It recovered exactly the supported record on 21/21 held-out cases. The supplied untrained configuration and no-slot baseline each recovered the exact set on 0/21. These strict exact-set scores penalize even one distractor and are not general understanding scores. All eight programmed checks passed, including source preservation, ablations and unknown-operation rejection.

The selected trial placed relation checking at ע, conditions at פ, context at צ, time at ק, evidence at ר, subject at ש and polarity at ת. These are arbitrary candidate placements, NOT discovered meanings or approved glyph definitions. Reversing those positions preserved performance because all filters commute. The experiment identifies a useful function set within this constructed task family, but cannot distinguish glyph placement or order.

This is a concrete start on autonomous context assembly: given supplied operations and external correctness feedback, Echo can select which combination to use. It did not invent new operations, learn novel language, or choose its own evaluation standard. The next experiment must vary the task requirements, introduce optional or missing fields, permit abstention, include costs and counterexamples, and compare configurations across genuinely different task families. Glyph-specific assignments require asymmetries or source-backed constraints that this experiment intentionally did not invent.

Reproduce from package root: python3 Algorithms/seven-slot-trial/run_trial.py
Results, learned selection history, full training trace and held-out cases are included. Engine is the pinned existing Echo source copied from the prior acquisition work.
