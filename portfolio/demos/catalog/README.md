# Demo: editable projects without losing history

**Client problem:** reusing a template should not make every project change when one project is edited.

From the repository root, with Python 3:

```sh
python portfolio/demos/catalog/showcase.py
```

No extra packages, credentials, network or model calls. A temporary SQLite database is created and removed when the demonstration exits.

The demo uses the existing [CatalogBox](../../../libraries/catalog_box.py). It makes two projects from one template, customizes Project A, updates the shared checklist, then closes and reopens the database.

Expected highlights:
- A has source/draft/approval columns; B retains source/draft.
- A's original configuration can still be retrieved.
- The latest checklist is revision 2; the saved projects still reference revision 1.
- Reopening the database preserves the records.

## 60-second recording outline

1. Explain the problem in one sentence.
2. Run the command and show the named output fields.
3. Point to different A/B columns and preserved revisions.
4. Close with the relevant service: small versioned catalogs or reusable configuration tools.

This is a command-line persistence demo, not a hosted multi-user app. It supplies no account authentication, encryption, remote synchronization or full disaster-recovery service. Source is synthetic and no customer's records are shown.
