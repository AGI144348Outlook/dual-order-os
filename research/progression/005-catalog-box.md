# Progression 005 — Catalog box Matrix and reusable configurations

Recorded 2026-10-20. Timothy requested a catalog box Matrix for Echo's index cards, including a section for templates of saved configurations.

## From experiments to a usable component

Earlier work established that records can carry glyph identities and that Echo can generate field queries. It also found duplicate, conflict, and mutable-record weaknesses in an existing experimental glyph index. The new component addresses catalog persistence and revision handling without modifying that older index or Genesis algorithms.

The implementation uses Python's standard-library SQLite support. Three sections distinguish cards, reusable templates, and independent saved configurations. Stable IDs persist across revisions. Arbitrary JSON card bodies leave room for replaceable semantic profiles rather than fixing one meaning per glyph. Unicode notation remains intact; צ and ץ stay distinct in glyph lookup.

A template captures configuration data and exact card revisions. Restoring it creates a separate configuration identity. A saved configuration can itself be captured as another template, preserving its source revision. Later edits to the source instance, the template, or the latest card profile do not retroactively alter earlier snapshots.

These are data operations. “Restore” does not launch programs, reconstruct a browser workspace, or execute glyph operations. The demo records the user-directed צ paperclip and ת associative-stamp roles as proposals; it does not implement their behaviors or finalize their meanings.

## Validation

Thirteen tests ran with zero failures or errors under Python 3.12.14. They exercised:

- distinct glyph forms and duplicate identity rejection;
- lookup after revised notation while retaining historical versions;
- stale writes rejected across two database connections;
- caller-side mutation unable to alter persisted records;
- template pinning and restoration of older card/template versions;
- independent instances and saved-configuration-to-template capture;
- missing/duplicate references rejected without partial templates or events;
- reopen-from-disk persistence;
- strict JSON, invalid identifiers, NaN/infinity rejection, and inert code strings.

The runnable demo also completed and its synthetic output is stored in the matrix folder. [Machine-readable results](evidence/005/results.json) and [test output](evidence/005/test-output.txt) accompany the [test source](../../tests/test_catalog_box.py). No personal data or cloud storage was used.

The tests establish the bounded local catalog behavior; they do not certify production access controls, hostile concurrent workloads, Android UI behavior, or full-environment restoration. SQLite protects the tested transaction/revision boundary. The event log is not tamper-proof and the database is not encrypted.

## Integration boundary

Implemented: [CatalogBox](../../libraries/catalog_box.py), [matrix definition](../../matrices/catalog-box/), [component guide](../../components/catalog-box/), and tests. Not implemented: automatic invocation by Echo, GraphQL/API endpoints, Canvas interface, R2 synchronization, account permissions, or semantic validation of card claims.

The record-creation methods can be used by a future governed Echo adapter. Merely saving a component card must not promote it to ACTIVE or VERIFIED in Genesis. That connection remains separate work. This change publishes a reusable component and documentation in Dual Order OS; it does not alter Genesis or deploy anything.
