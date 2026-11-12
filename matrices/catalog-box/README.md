# Catalog box Matrix

This matrix describes the catalog's three sections: index cards, configuration templates, and saved configuration instances. Content rows live in a SQLite database selected by the caller; this folder holds the definition and a synthetic example, not private user data.

- [Matrix definition](matrix.json)
- [Synthetic restored configuration](example.json)
- [Component and API](../../components/catalog-box/README.md)
- [Implementation](../../libraries/catalog_box.py)
- [Tests](../../tests/test_catalog_box.py)

Two lookup directions are supported: section + ID (+ optional revision) retrieves a record; section + glyph lists current matching cards. Templates link back to exact card IDs/revisions. This catalog is additive infrastructure; it does not replace existing matrices or indices.

## Optional protocol composition layer

The experimental [typed protocol card registry](protocol-card-types.json) and [architecture guide](../../components/catalog-box/contextual-protocols.md) describe a strict, inert extension for contextual evidence exchange, routing tickets, communication obligations, authority *references*, and approved detours. Stable ID/revision semantics and original catalog tables remain unchanged; actual identity, approvals and cross-Agent evidence memory belong to separately trusted services.
