import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "libraries"))
from catalog_box import CatalogBox, Conflict, demo


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "catalog.sqlite"
        self.box = CatalogBox(self.path)

    def tearDown(self):
        self.box.close()
        self.tmp.cleanup()

    def card(self, **kwargs):
        return self.box.put_card("tsadi", "Paperclip", {"verb": "attach"}, glyph="צ", **kwargs)

    def template(self):
        self.card()
        return self.box.put_template("layout", "Review", {"slots": ["word", "tags"]},
                                     [{"id": "tsadi"}])

    def test_distinct_glyph_forms_and_duplicate_identity(self):
        self.card()
        self.box.put_card("final", "Unassigned", {}, glyph="ץ")
        self.assertEqual([x["id"] for x in self.box.list("cards", glyph="צ")], ["tsadi"])
        self.assertEqual([x["id"] for x in self.box.list("cards", glyph="ץ")], ["final"])
        with self.assertRaises(Conflict):
            self.card()
        self.assertEqual(len(self.box.events()), 2)

    def test_revision_changes_lookup_without_losing_history(self):
        self.card()
        self.box.put_card("tsadi", "Changed experimental notation", {}, glyph="ץ", expected_revision=1)
        self.assertEqual(self.box.list("cards", glyph="צ"), [])
        self.assertEqual(self.box.get("cards", "tsadi", 1)["glyph"], "צ")
        self.assertEqual(len(self.box.history("cards", "tsadi")), 2)

    def test_two_clients_reject_stale_revision(self):
        self.card()
        with CatalogBox(self.path) as other:
            self.box.put_card("tsadi", "First edit", {}, expected_revision=1)
            with self.assertRaises(Conflict):
                other.put_card("tsadi", "Stale edit", {}, expected_revision=1)
        self.assertEqual(self.box.get("cards", "tsadi")["title"], "First edit")
        self.assertEqual(len(self.box.events()), 2)

    def test_return_and_input_mutation_do_not_change_storage(self):
        body = {"slots": ["a"]}
        result = self.box.put_card("card", "Card", body)
        body["slots"].append("b")
        result["body"]["slots"].append("c")
        self.assertEqual(self.box.get("cards", "card")["body"], {"slots": ["a"]})

    def test_template_pins_card_revisions(self):
        template = self.template()
        self.box.put_card("tsadi", "Revised role", {"verb": "review"}, expected_revision=1)
        self.box.instantiate("layout", "instance")
        self.assertEqual(template["card_refs"], [{"id": "tsadi", "revision": 1}])
        self.assertEqual(self.box.resolve_cards("configurations", "instance")[0]["body"], {"verb": "attach"})

    def test_templates_can_be_versioned_and_explicitly_restored(self):
        self.template()
        self.box.put_template("layout", "New review", {"slots": ["new"]},
                              [{"id": "tsadi"}], expected_revision=1)
        old = self.box.instantiate("layout", "old", template_revision=1)
        new = self.box.instantiate("layout", "new")
        self.assertEqual(old["configuration"]["slots"], ["word", "tags"])
        self.assertEqual(new["configuration"]["slots"], ["new"])

    def test_configuration_edits_leave_template_and_other_instance_intact(self):
        self.template()
        self.box.instantiate("layout", "one")
        self.box.instantiate("layout", "two")
        self.box.save_configuration("one", {"slots": ["custom"]}, expected_revision=1)
        self.assertEqual(self.box.get("configurations", "two")["configuration"], {"slots": ["word", "tags"]})
        self.assertEqual(self.box.get("templates", "layout")["configuration"], {"slots": ["word", "tags"]})
        self.assertEqual(self.box.get("configurations", "one", 1)["configuration"], {"slots": ["word", "tags"]})

    def test_missing_or_duplicate_refs_do_not_create_template_or_event(self):
        self.card()
        for refs in [[{"id": "absent"}], [{"id": "tsadi", "revision": 99}],
                     [{"id": "tsadi"}, {"id": "tsadi"}]]:
            with self.assertRaises((KeyError, ValueError)):
                self.box.put_template("bad", "Bad", {}, refs)
        self.assertEqual(self.box.list("templates"), [])
        self.assertEqual(len(self.box.events()), 1)

    def test_duplicate_instance_does_not_overwrite(self):
        self.template()
        first = self.box.instantiate("layout", "instance")
        with self.assertRaises(Conflict):
            self.box.instantiate("layout", "instance")
        self.assertEqual(self.box.get("configurations", "instance"), first)

    def test_saved_configuration_becomes_reusable_snapshot(self):
        self.template()
        self.box.instantiate("layout", "working")
        self.box.save_configuration("working", {"slots": ["custom"]}, expected_revision=1)
        snapshot = self.box.save_as_template("working", "custom-layout", "Custom")
        self.box.save_configuration("working", {"slots": ["later"]}, expected_revision=2)
        restored = self.box.instantiate("custom-layout", "restored")
        self.assertEqual(restored["configuration"], {"slots": ["custom"]})
        self.assertEqual(snapshot["provenance"]["saved_configuration"]["revision"], 2)
        self.assertEqual(restored["card_refs"], [{"id": "tsadi", "revision": 1}])

    def test_reopen_restores_cards_templates_and_instances(self):
        self.template()
        self.box.instantiate("layout", "instance")
        self.box.close()
        self.box = CatalogBox(self.path)
        self.assertEqual(self.box.get("cards", "tsadi")["glyph"], "צ")
        self.assertEqual(self.box.resolve_cards("configurations", "instance")[0]["id"], "tsadi")
        self.assertEqual(len(self.box.events()), 3)

    def test_json_contract_and_identity_validation(self):
        invalid = [{"x": float("nan")}, {"x": float("inf")}, {1: "key"}, {"x": object()}]
        for body in invalid:
            with self.assertRaises(ValueError):
                self.box.put_card("bad", "Bad", body)
        for ident in ["../outside", "", "a/b"]:
            with self.assertRaises(ValueError):
                self.box.put_card(ident, "Bad", {})
        with self.assertRaises(ValueError):
            self.box.put_card("bad", "Bad", {}, expected_revision=True)
        self.assertEqual(self.box.events(), [])

    def test_code_strings_are_data_and_demo_has_no_automatic_execution(self):
        text = "__import__('os').system('this_must_not_execute')"
        self.box.put_card("inert", "Inert", {"code": text})
        self.assertEqual(self.box.get("cards", "inert")["body"]["code"], text)
        result = demo(self.box)
        self.assertFalse(result["configuration"]["configuration"]["automatic_execution"])
        self.assertEqual([c["glyph"] for c in result["cards"]], ["צ", "ת"])


if __name__ == "__main__":
    unittest.main()
