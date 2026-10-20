# Catalog box Matrix

This matrix describes the catalog's three sections: index cards, configuration templates, and saved configuration instances. Content rows live in a SQLite database selected by the caller; this folder holds the definition and a synthetic example, not private user data.

- [Matrix definition](matrix.json)
- [Synthetic restored configuration](example.json)
- [Component and API](../../components/catalog-box/README.md)
- [Implementation](../../libraries/catalog_box.py)
- [Tests](../../tests/test_catalog_box.py)

Two lookup directions are supported: section + ID (+ optional revision) retrieves a record; section + glyph lists current matching cards. Templates link back to exact card IDs/revisions. This catalog is additive infrastructure; it does not replace existing matrices or indices.
