"""Bounded offline tests for inert contextual protocol cards.

Pre-test plan: https://github.com/AGI144348Outlook/dual-order-os/issues/20
No networks, provider credentials, production databases or deployment actions.
"""
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "libraries"))
from catalog_box import CatalogBox
from contextual_protocols import ProtocolCatalog, ProtocolError


class ContextualProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.box = CatalogBox(Path(self.tmp.name) / "catalog.sqlite")
        self.protocols = ProtocolCatalog(self.box)

    def tearDown(self):
        self.box.close()
        self.tmp.cleanup()

    def put(self, name, kind, spec, revision=0):
        return self.protocols.put(name, name, kind, spec, expected_revision=revision)

    def setup_context(self, *, effect="assess", ticket="ROUND_TRIP_ASSESSMENT",
                      actor="05", recipient="05", include_auth=False):
        tool_id = "engineering.review"
        action_id = "plan.review"
        resource = "repo:demo"
        refs = []
        def add(name, kind, spec):
            card = self.put(name, kind, spec)
            refs.append({"id": card["id"], "revision": card["revision"]})
        add("charter", "seat_charter", {
            "seat_id": actor,
            "allowed_tools": [tool_id], "allowed_actions": [action_id],
            "forbidden_actions": []})
        add("tool", "tool", {
            "tool_id": tool_id, "server_seat": actor, "effect": effect})
        add("action", "action", {
            "action_id": action_id, "tool_id": tool_id,
            "effect": effect, "resource": resource})
        route = {
            "ticket_class": ticket, "mission_id": "mission001",
            "origin_seat": "03", "issuer_seat": "03",
            "recipient_seat": recipient, "return_to": "03",
            "allowed_tools": [tool_id], "allowed_actions": [action_id],
            "allowed_resources": [resource], "expires_at": "2099-01-01T00:00:00Z"}
        if ticket == "EXECUTION_ORDER":
            route["approval_ref"] = "approval001"
        add("ticket", "route_ticket", route)
        add("comm", "communication", {
            "sender_seat": "03", "receiver_seat": actor,
            "message_types": ["assignment", "return"],
            "return_required": True})
        if include_auth:
            add("approval", "approval_reference", {
                "approval_ref": "approval001", "mission_id": "mission001",
                "action_id": action_id, "resource": resource, "approving_seat": "02"})
            add("stamp", "authority_stamp", {
                "approval_ref": "approval001", "issuer_seat": "02",
                "mission_id": "mission001", "action_id": action_id,
                "resource": resource, "ticket_id": "ticket"})
        kwargs = {"mission_id": "mission001", "actor_seat": actor,
                  "action_id": action_id, "resource": resource,
                  "now": datetime(2026, 11, 11, tzinfo=timezone.utc)}
        return refs, kwargs

    def test_typed_cards_and_invalid_fields(self):
        self.put("evidence", "evidence", {
            "source_ref": "doc01", "claim_ref": "claim01",
            "relationship": "supports", "epistemic_state": "provisional"})
        self.assertEqual(self.box.get("cards", "evidence")["body"]["protocol_kind"], "evidence")
        for bad in [
            ("bogus", {}),
            ("action", {"action_id": "x", "tool_id": "y", "effect": "execute", "resource": "r", "inject": True}),
            ("route_ticket", {"ticket_class": "EXECUTION_ORDER"}),
        ]:
            with self.assertRaises(ProtocolError):
                self.put("invalid", *bad)
        self.assertEqual(len(self.box.events()), 1)

    def test_limited_assignment_and_no_unrelated_tool_disclosure(self):
        refs, kw = self.setup_context()
        extra = self.put("unrelated", "tool", {
            "tool_id": "root.admin", "server_seat": "02", "effect": "admin"})
        refs.append({"id": extra["id"], "revision": extra["revision"]})
        result = self.protocols.evaluate(refs, **kw)
        self.assertEqual(result["decision"], "eligible_for_nonexecuting_work")
        self.assertEqual(result["permitted_tools"], ["engineering.review"])
        self.assertFalse(result["executes_action"])
        self.assertNotIn("root.admin", str(result["permitted_tools"]))

    def test_round_trip_never_authorizes_execution_even_with_callback(self):
        refs, kw = self.setup_context(effect="execute")
        result = self.protocols.evaluate(refs, approval_verifier=lambda _: {"valid": True}, **kw)
        self.assertEqual(result["decision"], "denied")
        self.assertIn("round-trip", result["reason"])

    def test_deployment_requires_external_verifier_and_exact_scope(self):
        refs, kw = self.setup_context(effect="execute", ticket="EXECUTION_ORDER", include_auth=True)
        no_verifier = self.protocols.evaluate(refs, **kw)
        self.assertEqual(no_verifier["decision"], "denied")
        self.assertIn("trusted", no_verifier["reason"])
        wrong = self.protocols.evaluate(refs, approval_verifier=lambda q: {
            **q, "resource": "repo:other", "valid": True}, **kw)
        self.assertEqual(wrong["decision"], "denied")
        good = self.protocols.evaluate(refs, approval_verifier=lambda q: {
            **q, "valid": True}, **kw)
        self.assertEqual(good["decision"], "eligible_after_external_verification")
        self.assertFalse(good["executes_action"])

    def test_stored_stamp_cannot_authorize_without_matching_ticket(self):
        refs, kw = self.setup_context(effect="execute", ticket="EXECUTION_ORDER", include_auth=True)
        refs = [r for r in refs if r["id"] != "stamp"]
        result = self.protocols.evaluate(refs, approval_verifier=lambda q: {
            **q, "valid": True}, **kw)
        self.assertEqual(result["decision"], "denied")
        self.assertIn("stamp", result["reason"])

    def test_forbidden_action_and_missing_scope_denied(self):
        refs, kw = self.setup_context()
        kw["resource"] = "repo:private"
        self.assertEqual(self.protocols.evaluate(refs, **kw)["decision"], "denied")
        kw["resource"] = "repo:demo"
        card = self.box.get("cards", "charter")
        spec = dict(card["body"]["spec"], forbidden_actions=["plan.review"])
        newer = self.put("charter", "seat_charter", spec, revision=1)
        updated = [({"id": "charter", "revision": newer["revision"]}
                    if r["id"] == "charter" else r) for r in refs]
        self.assertEqual(self.protocols.evaluate(updated, **kw)["decision"], "denied")
        self.assertEqual(self.protocols.evaluate(refs, **kw)["decision"],
                         "eligible_for_nonexecuting_work")

    def test_missing_or_unpinned_references_do_not_issue_permission(self):
        refs, kw = self.setup_context()
        with self.assertRaises(ProtocolError):
            self.protocols.evaluate([{"id": "charter"}], **kw)
        refs = [r for r in refs if r["id"] != "comm"]
        self.assertEqual(self.protocols.evaluate(refs, **kw)["decision"], "denied")

    def test_detour_is_bounded_and_never_bypasses_denial(self):
        refs, kw = self.setup_context(actor="14", recipient="05")
        detour = self.put("detour", "detour", {
            "ticket_id": "ticket", "fallback_seat": "14",
            "allowed_failure_codes": ["UNAVAILABLE", "TIMEOUT"],
            "allowed_tools": ["engineering.review"],
            "max_attempts": 2, "max_hops": 2,
            "expires_at": "2099-01-01T00:00:00Z"})
        refs.append({"id": "detour", "revision": detour["revision"]})
        denied_without_external_attestation = self.protocols.evaluate(
            refs, failure_code="UNAVAILABLE", **kw)
        self.assertEqual(denied_without_external_attestation["decision"], "denied")
        verifier = lambda inquiry: dict(inquiry, valid=True)
        good = self.protocols.evaluate(
            refs, failure_code="UNAVAILABLE", detour_verifier=verifier, **kw)
        self.assertEqual(good["decision"], "eligible_for_nonexecuting_work")
        for params in [{"failure_code": "AUTH_DENIED"},
                       {"failure_code": "UNAVAILABLE", "attempt": 3},
                       {"failure_code": "UNAVAILABLE", "hop": 3}]:
            self.assertEqual(self.protocols.evaluate(refs, detour_verifier=verifier, **kw, **params)["decision"], "denied")

    def test_audit_retains_exact_pinned_versions_without_reauthorization(self):
        refs, kw = self.setup_context()
        first = self.protocols.evaluate(refs, **kw)
        self.protocols.report_outcome(first["evaluation_id"], "reported_success",
                                      evidence_ref="receipt001")
        self.assertEqual(self.protocols.outcomes(first["evaluation_id"])[0]["reported_outcome"],
                         "reported_success")
        self.assertEqual(self.protocols.reconstruct(first["evaluation_id"])[0]["revision"], 1)
        old = self.box.get("cards", "charter")
        self.put("charter", "seat_charter", dict(old["body"]["spec"], allowed_tools=[]),
                 revision=1)
        self.assertEqual(self.protocols.reconstruct(first["evaluation_id"])[0]["revision"], 1)
        self.assertFalse(first["executes_action"])


if __name__ == "__main__":
    unittest.main()
