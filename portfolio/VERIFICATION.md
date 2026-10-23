# Verification checkpoint — 23 October 2026

## Packaged demos executed

- `python portfolio/demos/catalog/showcase.py`: passed. Different A/B configurations, historical configuration retained, checklist revision 2 while pinned project stays on revision 1, state reopened from SQLite.
- `node portfolio/demos/persona-filter/showcase.js`: passed. Eight synthetic messages; two candidate pairs (direct/inherited); ordinary mention and other-persona reply excluded in this fixture.
- Both exit successfully, need no model calls, and use only synthetic records. A script assertion checks the behavior it displays; this is a smoke demonstration, not a new broad regression suite.

The persona engine/parser copies retain their pinned upstream Git blob identities; the new fixture/wrapper does not change the filter policy.

## Previously executed assessment checks in the same review session

- Group Canvas main `36d1b1a311c55cdf1ebeec3ef7499945f56186e8`: 100 passing tests, Node 24.19.0.
- Dual Order main `2977b2d1a8332766301462869ba6244bfb34f57d`: 13 passing CatalogBox tests.
- The small demo packaging does not change those core implementations.
- Classroom publication run 39862826702 and successful verification/browser-check steps were inspected.

No new live browser recording, physical Android session, cloud deployment, private archive scan, paid model call, subscription implementation or training run was performed for this portfolio packaging. The linked hosted reading page is an existing artifact.
