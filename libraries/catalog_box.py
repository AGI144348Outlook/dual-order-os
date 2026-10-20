"""Persistent index-card catalog. Templates describe configurations; never execute them.

Python standard library only. Run this file with --demo for a temporary example.
"""
import argparse
import json
import re
import sqlite3
import tempfile
from pathlib import Path


class Conflict(ValueError):
    """A write expected a different current revision."""


class CatalogBox:
    SECTIONS = ("cards", "templates", "configurations")

    def __init__(self, database=":memory:"):
        self.db = sqlite3.connect(str(database), isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS records (
                section TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
                glyph TEXT, title TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(section, id, revision));
            CREATE INDEX IF NOT EXISTS glyph_lookup ON records(section, glyph);
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY, section TEXT NOT NULL, id TEXT NOT NULL,
                revision INTEGER NOT NULL, created TEXT NOT NULL DEFAULT
                (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
        """)

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @staticmethod
    def _id(value):
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value):
            raise ValueError("ID must be a stable 1–128 character identifier")
        return value

    @staticmethod
    def _json(value):
        # Check before encoding: JSON must not silently stringify keys or tuples.
        def check(x):
            if isinstance(x, dict):
                if any(not isinstance(k, str) for k in x):
                    raise ValueError("JSON object keys must be strings")
                for v in x.values():
                    check(v)
            elif isinstance(x, list):
                for v in x:
                    check(v)
            elif x is not None and type(x) not in (str, int, float, bool):
                raise ValueError("Only JSON data may be stored; no callables or objects")
        check(value)
        return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)

    @staticmethod
    def _revision(value, allow_zero=False):
        if type(value) is not int or value < (0 if allow_zero else 1):
            raise ValueError("Revision must be a positive integer (expected revision may be zero)")

    def get(self, section, record_id, revision=None):
        if section not in self.SECTIONS:
            raise ValueError("Unknown catalog section")
        self._id(record_id)
        if revision is not None:
            self._revision(revision)
        row = self.db.execute(
            "SELECT payload FROM records WHERE section=? AND id=? "
            + ("ORDER BY revision DESC LIMIT 1" if revision is None else "AND revision=?"),
            (section, record_id) if revision is None else (section, record_id, revision),
        ).fetchone()
        if row is None:
            raise KeyError((section, record_id, revision))
        return json.loads(row["payload"])

    def list(self, section, glyph=None):
        if section not in self.SECTIONS:
            raise ValueError("Unknown catalog section")
        # Filter AFTER selecting current versions; old glyph aliases do not leak.
        rows = self.db.execute("""SELECT r.* FROM records r
            JOIN (SELECT id, MAX(revision) AS revision FROM records
                  WHERE section=? GROUP BY id) h
            ON r.id=h.id AND r.revision=h.revision
            WHERE r.section=? ORDER BY r.id""", (section, section)).fetchall()
        return [json.loads(r["payload"]) for r in rows if glyph is None or r["glyph"] == glyph]

    def history(self, section, record_id):
        self.get(section, record_id)
        return [json.loads(r[0]) for r in self.db.execute(
            "SELECT payload FROM records WHERE section=? AND id=? ORDER BY revision",
            (section, record_id))]

    def events(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM events ORDER BY sequence")]

    def _put(self, section, record_id, title, payload, expected_revision, glyph=None):
        self._id(record_id)
        self._revision(expected_revision, allow_zero=True)
        if not isinstance(title, str) or not title.strip():
            raise ValueError("A nonblank title is required")
        if glyph is not None and (not isinstance(glyph, str) or not glyph):
            raise ValueError("Glyph must be nonempty text or None")
        result = dict(payload, id=record_id, revision=expected_revision + 1,
                      section=section, title=title, glyph=glyph)
        encoded = self._json(result)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            current = self.db.execute(
                "SELECT MAX(revision) FROM records WHERE section=? AND id=?",
                (section, record_id)).fetchone()[0] or 0
            if current != expected_revision:
                raise Conflict(f"Expected revision {expected_revision}; current revision is {current}")
            self.db.execute("INSERT INTO records VALUES(?,?,?,?,?,?)",
                            (section, record_id, current + 1, glyph, title, encoded))
            self.db.execute("INSERT INTO events(section,id,revision) VALUES(?,?,?)",
                            (section, record_id, current + 1))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return json.loads(encoded)

    def put_card(self, card_id, title, body, *, glyph=None, provenance=None,
                 tags=None, expected_revision=0):
        if not isinstance(body, dict):
            raise ValueError("Card body must be an object")
        if tags is None:
            tags = []
        if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
            raise ValueError("Tags must be a list of strings")
        return self._put("cards", card_id, title,
                         {"body": body, "tags": tags, "provenance": provenance},
                         expected_revision, glyph)

    def _refs(self, refs):
        if not isinstance(refs, list):
            raise ValueError("Card references must be a list")
        pinned, seen = [], set()
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) - {"id", "revision"} or "id" not in ref:
                raise ValueError("Reference needs id and optional revision")
            card = self.get("cards", ref["id"], ref.get("revision"))
            if card["id"] in seen:
                raise ValueError("A card may occur only once in this configuration")
            seen.add(card["id"])
            pinned.append({"id": card["id"], "revision": card["revision"]})
        return pinned

    def put_template(self, template_id, title, configuration, card_refs, *,
                     provenance=None, expected_revision=0):
        if not isinstance(configuration, dict):
            raise ValueError("Configuration must be an object")
        return self._put("templates", template_id, title,
                         {"configuration": configuration, "card_refs": self._refs(card_refs),
                          "provenance": provenance}, expected_revision)

    def instantiate(self, template_id, configuration_id, *, template_revision=None,
                    title=None):
        template = self.get("templates", template_id, template_revision)
        return self._put("configurations", configuration_id, title or template["title"],
                         {"configuration": template["configuration"],
                          "card_refs": template["card_refs"],
                          "template_origin": {"id": template_id, "revision": template["revision"]}}, 0)

    def save_configuration(self, configuration_id, configuration, *, expected_revision):
        if not isinstance(configuration, dict):
            raise ValueError("Configuration must be an object")
        old = self.get("configurations", configuration_id)
        return self._put("configurations", configuration_id, old["title"],
                         {"configuration": configuration, "card_refs": old["card_refs"],
                          "template_origin": old["template_origin"]}, expected_revision)

    def resolve_cards(self, section, record_id, revision=None):
        if section not in ("templates", "configurations"):
            raise ValueError("Resolve cards from a template or saved configuration")
        item = self.get(section, record_id, revision)
        return [self.get("cards", ref["id"], ref["revision"]) for ref in item["card_refs"]]

    def save_as_template(self, configuration_id, template_id, title, *,
                         configuration_revision=None, expected_revision=0):
        """Capture a saved configuration without linking later edits to the template."""
        item = self.get("configurations", configuration_id, configuration_revision)
        return self.put_template(
            template_id, title, item["configuration"], item["card_refs"],
            provenance={"saved_configuration": {"id": configuration_id,
                                                 "revision": item["revision"]}},
            expected_revision=expected_revision)


def demo(box):
    # Explicitly supplied user-directed roles; not meanings inferred by Echo.
    box.put_card("tsadi", "Paperclip", {"verb": "attach", "status": "proposed"},
                 glyph="צ", provenance={"source": "Timothy: צ for paperclipping"})
    box.put_card("tav", "Associative stamp", {"verb": "stamp", "status": "proposed"},
                 glyph="ת", provenance={"source": "Timothy: glyph association stamps"})
    box.put_template("review-layout", "Attachment and tag review",
                     {"columns": ["word", "attachments", "glyph_tags"],
                      "automatic_execution": False}, [{"id": "tsadi"}, {"id": "tav"}])
    instance = box.instantiate("review-layout", "review-001")
    return {"configuration": instance,
            "cards": box.resolve_cards("configurations", "review-001")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Run a temporary example")
    args = parser.parse_args()
    if args.demo:
        with tempfile.TemporaryDirectory() as directory:
            with CatalogBox(Path(directory) / "demo.sqlite") as box:
                print(json.dumps(demo(box), ensure_ascii=False, indent=2))
    else:
        parser.print_help()
