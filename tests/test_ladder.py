"""Ladder tests: every dataset climbs down to registry pieces and back up byte for byte.

The database tests run when LADDER_TEST_DATABASE_URL points at a throwaway Postgres
(the GitHub workflow starts one). They rebuild the ladder schema there from
libraries/ladder_schema.sql, so they never touch Neon.
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "libraries"))
from ladder import Ladder, sha
import ladder_load

ROOT = Path(__file__).resolve().parents[1]
DB = os.environ.get("LADDER_TEST_DATABASE_URL")


class RebuildTests(unittest.TestCase):
    def test_every_dataset_rebuilds_byte_exact(self):
        for e in ladder_load.read_manifest():
            with self.subTest(dataset=e["id"]):
                c = ladder_load.deconstruct(Ladder(), e)
                self.assertTrue(c["byte_exact"], c["first_difference"])
                self.assertEqual(c["rebuilt_sha256"], e["sha256"])

    def test_files_are_kept_as_found(self):
        # git must not rewrite line endings on the datasets shelf (see .gitattributes)
        raw = (ROOT / "datasets" / "mind-domain-2025-01-05.json").read_bytes()
        self.assertIn(b"\r\n", raw)

    def test_line_endings_survive_json_rebuild(self):
        for nl in ("\n", "\r\n"):
            text = '{\n  "a": [\n    1,\n    "two"\n  ]\n}'.replace("\n", nl)
            L = Ladder()
            L.add_dataset("d", text, {})
            L.deconstruct_json("c", "d")
            self.assertEqual(L.rebuild("c"), text)

    def test_identical_pieces_share_one_registry_entry(self):
        L = Ladder()
        L.add_dataset("d", "Same line.\nSame line.\n", {})
        L.deconstruct_prose("c", "d")
        statements = [pid for k, pid in L.codices["c"]["segments"] if k == "statement"]
        self.assertEqual(len(statements), 2)
        self.assertEqual(len(set(statements)), 1)

    def test_seed_keeps_ids_and_continues_numbering(self):
        L = Ladder()
        L.seed([("statement:0007", "statement", "Already here.")])
        self.assertEqual(L.register("statement", "Already here."), "statement:0007")
        self.assertEqual(L.register("statement", "New one."), "statement:0008")


@unittest.skipUnless(DB, "set LADDER_TEST_DATABASE_URL to run the database tests")
class LoadTests(unittest.TestCase):
    def setUp(self):
        import psycopg
        self.conn = psycopg.connect(DB, autocommit=True)
        self.conn.execute("drop schema if exists ladder cascade")
        self.conn.execute((ROOT / "libraries" / "ladder_schema.sql").read_text())
        self.conn.autocommit = False
        self.entries = {e["id"]: e for e in ladder_load.read_manifest()}

    def tearDown(self):
        self.conn.close()

    def count(self, table):
        with self.conn.cursor() as cur:
            cur.execute(f"select count(*) from ladder.{table}")
            return cur.fetchone()[0]

    def test_load_then_rerun_skips(self):
        _, ok = ladder_load.load(self.conn, list(self.entries.values()))
        self.assertTrue(ok)
        self.assertEqual(self.count("dataset"), 2)
        segs = self.count("codex_segment")
        _, ok = ladder_load.load(self.conn, list(self.entries.values()))
        self.assertTrue(ok)
        self.assertEqual(self.count("codex_segment"), segs)

    def test_ids_match_what_neon_already_holds(self):
        # Neon was loaded by hand with the Mind Domain; a loader run must give the same ids
        ladder_load.load(self.conn, [self.entries["ds-mind-domain"]])
        with self.conn.cursor() as cur:
            cur.execute("""select string_agg(piece_id || '=' || text, chr(10) order by piece_id collate "C")
                           from ladder.registry""")
            digest = sha(cur.fetchone()[0])
        self.assertEqual(digest, "d194c0e3ff19e8cb19f198bae1223bb877c0c3790f62fd6fe9d94b534247c22f")

    def test_changed_source_under_same_id_is_refused(self):
        ladder_load.load(self.conn, [self.entries["ds-mind-domain"]])
        changed = dict(self.entries["ds-mind-domain"], text="{}", sha256=sha("{}"))
        _, ok = ladder_load.load(self.conn, [changed])
        self.assertFalse(ok)
        self.assertEqual(self.count("dataset"), 1)

    def test_rows_cannot_be_changed(self):
        ladder_load.load(self.conn, [self.entries["ds-mind-domain"]])
        import psycopg
        with self.assertRaises(psycopg.errors.RaiseException):
            with self.conn.transaction():
                self.conn.execute("update ladder.registry set text = 'x'")


if __name__ == "__main__":
    unittest.main()
