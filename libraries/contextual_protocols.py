"""Contextually governed protocol cards on top of the existing inert CatalogBox.

This module compiles *candidate* capabilities; it never executes MCP tools, grants
database privileges, signs approvals, or authenticates the human/Agent caller.
A trusted backend MUST authenticate callers and supply approval_verifier.
The local SQLite evaluation journal is NOT a tamper-proof institutional ledger.
"""
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone

try:
    from .catalog_box import CatalogBox
except ImportError:  # direct module import from libraries/ in existing test style
    from catalog_box import CatalogBox


KINDS = frozenset({
    "evidence", "seat_charter", "tool", "route_ticket", "communication",
    "action", "approval_reference", "authority_stamp", "detour",
})
EFFECTS = frozenset({"read", "assess", "propose", "execute", "admin"})
PROTECTED_EFFECTS = frozenset({"execute", "admin"})
TICKET_CLASSES = frozenset({
    "EVIDENCE_TRANSFER", "ROUND_TRIP_ASSESSMENT", "EXECUTION_ORDER",
    "RECOVERY_DETOUR",
})
PERMITTED_PROPOSAL_EFFECTS = frozenset({"read", "assess", "propose"})
BLOCKED_DETOURS = frozenset({"AUTH_DENIED", "REVOKED", "POLICY_DENIED", "NO_APPROVAL"})


class ProtocolError(ValueError):
    """An unrecognized or malformed typed protocol card."""


def _id(value, name="identifier"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value):
        raise ProtocolError(f"{name} must be a stable identifier (1-128 characters)")
    return value


def _seat(value):
    if not isinstance(value, str) or not re.fullmatch(r"(0[1-9]|1[0-9]|20)", value):
        raise ProtocolError("seat must be a two-digit constitutional office (01-20)")
    return value


def _str(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ProtocolError(f"{name} must be nonempty text")
    return value


def _list(value, name, *, allow_empty=False, ids=True):
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ProtocolError(f"{name} must be a nonempty array")
    for v in value:
        (_id(v, name) if ids else _str(v, name))
    if len(value) != len(set(value)):
        raise ProtocolError(f"{name} cannot contain duplicates")
    return value


def _timestamp(value):
    _str(value, "expires_at")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProtocolError("expires_at must be an ISO 8601 datetime") from exc
    if parsed.tzinfo is None:
        raise ProtocolError("expires_at must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _shape(spec, required, optional=()):
    if not isinstance(spec, dict):
        raise ProtocolError("spec must be a JSON object")
    missing = set(required) - set(spec)
    unknown = set(spec) - set(required) - set(optional)
    if missing or unknown:
        raise ProtocolError(f"spec fields missing={sorted(missing)} unknown={sorted(unknown)}")
    try:
        json.dumps(spec, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("spec must be strict JSON") from exc


def validate_card(kind, spec):
    """Validate a version-1 card contract. Returns a JSON-detached copy."""
    if kind not in KINDS:
        raise ProtocolError(f"unsupported protocol card kind: {kind}")
    if kind == "seat_charter":
        _shape(spec, ("seat_id", "allowed_tools", "allowed_actions", "forbidden_actions"))
        _seat(spec["seat_id"])
        for name in ("allowed_tools", "allowed_actions", "forbidden_actions"):
            _list(spec[name], name, allow_empty=True)
    elif kind == "tool":
        _shape(spec, ("tool_id", "server_seat", "effect"))
        _id(spec["tool_id"]); _seat(spec["server_seat"])
        if spec["effect"] not in EFFECTS:
            raise ProtocolError("invalid tool effect")
    elif kind == "action":
        _shape(spec, ("action_id", "tool_id", "effect", "resource"))
        _id(spec["action_id"]); _id(spec["tool_id"])
        if spec["effect"] not in EFFECTS:
            raise ProtocolError("invalid action effect")
        _id(spec["resource"], "resource")
    elif kind == "route_ticket":
        _shape(spec, ("ticket_class", "mission_id", "origin_seat", "issuer_seat",
                      "recipient_seat", "return_to", "allowed_tools",
                      "allowed_actions", "allowed_resources", "expires_at"),
               ("approval_ref",))
        if spec["ticket_class"] not in TICKET_CLASSES:
            raise ProtocolError("invalid ticket_class")
        _id(spec["mission_id"])
        for f in ("origin_seat", "issuer_seat", "recipient_seat", "return_to"):
            _seat(spec[f])
        for f in ("allowed_tools", "allowed_actions", "allowed_resources"):
            _list(spec[f], f)
        _timestamp(spec["expires_at"])
        if "approval_ref" in spec and spec["approval_ref"] is not None:
            _id(spec["approval_ref"])
        if spec["ticket_class"] == "EXECUTION_ORDER" and not spec.get("approval_ref"):
            raise ProtocolError("execution order must reference an external approval")
        if spec["ticket_class"] == "ROUND_TRIP_ASSESSMENT" and spec["return_to"] == spec["recipient_seat"]:
            raise ProtocolError("round-trip must return to a different office")
    elif kind == "communication":
        _shape(spec, ("sender_seat", "receiver_seat", "message_types", "return_required"))
        _seat(spec["sender_seat"]); _seat(spec["receiver_seat"])
        _list(spec["message_types"], "message_types")
        if type(spec["return_required"]) is not bool:
            raise ProtocolError("return_required must be a boolean")
    elif kind == "evidence":
        _shape(spec, ("source_ref", "claim_ref", "relationship", "epistemic_state"))
        for f in ("source_ref", "claim_ref"):
            _id(spec[f])
        if spec["relationship"] not in ("supports", "contradicts", "contextualizes", "unassessed"):
            raise ProtocolError("invalid relationship")
        if spec["epistemic_state"] not in ("provisional", "contested", "reviewed"):
            raise ProtocolError("invalid epistemic_state")
    elif kind == "approval_reference":
        _shape(spec, ("approval_ref", "mission_id", "action_id", "resource", "approving_seat"))
        for f in ("approval_ref", "mission_id", "action_id", "resource"):
            _id(spec[f])
        _seat(spec["approving_seat"])
    elif kind == "authority_stamp":
        _shape(spec, ("approval_ref", "issuer_seat", "mission_id", "action_id",
                      "resource", "ticket_id"))
        for f in ("approval_ref", "mission_id", "action_id", "resource", "ticket_id"):
            _id(spec[f])
        _seat(spec["issuer_seat"])
    elif kind == "detour":
        _shape(spec, ("ticket_id", "fallback_seat", "allowed_failure_codes",
                      "allowed_tools", "max_attempts", "max_hops", "expires_at"))
        _id(spec["ticket_id"]); _seat(spec["fallback_seat"])
        _list(spec["allowed_failure_codes"], "allowed_failure_codes")
        _list(spec["allowed_tools"], "allowed_tools")
        if set(spec["allowed_failure_codes"]) & BLOCKED_DETOURS:
            raise ProtocolError("detour may not bypass security or approval denial")
        for name in ("max_attempts", "max_hops"):
            if type(spec[name]) is not int or not 1 <= spec[name] <= 8:
                raise ProtocolError(f"{name} must be between 1 and 8")
        _timestamp(spec["expires_at"])
    return json.loads(json.dumps(spec, ensure_ascii=False, sort_keys=True, allow_nan=False))


class ProtocolCatalog:
    """Validated inert protocol card storage and context/policy evaluation.

    The caller is responsible for supplying only authenticated mission/actor
    context. Any external verifier must be injected by a trusted server,
    NEVER selected by a card, model, request or network client.
    """

    def __init__(self, box: CatalogBox):
        self.box = box
        self.box.db.executescript("""
            CREATE TABLE IF NOT EXISTS protocol_evaluations (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              evaluation_id TEXT NOT NULL UNIQUE,
              recorded_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              mission_id TEXT NOT NULL, actor_seat TEXT NOT NULL,
              context_refs TEXT NOT NULL, decision TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS protocol_outcomes (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              evaluation_id TEXT NOT NULL,
              recorded_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              reported_outcome TEXT NOT NULL, evidence_ref TEXT,
              FOREIGN KEY(evaluation_id) REFERENCES protocol_evaluations(evaluation_id));
        """)

    def put(self, card_id, title, kind, spec, *, expected_revision=0, provenance=None):
        clean = validate_card(kind, spec)
        return self.box.put_card(card_id, title,
            {"protocol_kind": kind, "schema_version": 1, "spec": clean},
            tags=["protocol", kind], provenance=provenance,
            expected_revision=expected_revision)

    def load(self, reference):
        if not isinstance(reference, dict) or set(reference) != {"id", "revision"}:
            raise ProtocolError("each context reference must pin an id and exact revision")
        card_id = _id(reference["id"])
        revision = reference["revision"]
        if type(revision) is not int or revision < 1:
            raise ProtocolError("revision must be a positive integer")
        stored = self.box.get("cards", card_id, revision)
        body = stored["body"]
        if not isinstance(body, dict) or body.get("schema_version") != 1:
            raise ProtocolError("card is not versioned protocol data")
        kind = body.get("protocol_kind")
        validate_card(kind, body.get("spec"))
        return stored

    def _record(self, mission_id, actor_seat, pinned, result):
        evaluation_id = uuid.uuid4().hex
        self.box.db.execute(
            "INSERT INTO protocol_evaluations(evaluation_id,mission_id,actor_seat,context_refs,decision) VALUES(?,?,?,?,?)",
            (evaluation_id, mission_id, actor_seat,
             json.dumps(pinned, sort_keys=True), json.dumps(result, sort_keys=True)))
        return dict(result, evaluation_id=evaluation_id, context_refs=pinned)

    def history(self, evaluation_id=None):
        rows = (self.box.db.execute(
            "SELECT * FROM protocol_evaluations WHERE evaluation_id=? ORDER BY seq",
            (evaluation_id,)) if evaluation_id else self.box.db.execute(
            "SELECT * FROM protocol_evaluations ORDER BY seq"))
        return [dict(r, context_refs=json.loads(r["context_refs"]),
                     decision=json.loads(r["decision"])) for r in rows]

    def report_outcome(self, evaluation_id, outcome, *, evidence_ref=None):
        """Attach an UNVERIFIED report; no assertion of independently proven effects."""
        if outcome not in ("unobserved", "reported_success", "reported_failure",
                           "reported_cancelled"):
            raise ProtocolError("outcome must be explicitly reported, not verified")
        if evidence_ref is not None:
            _id(evidence_ref, "evidence_ref")
        if not self.history(evaluation_id):
            raise KeyError(evaluation_id)
        self.box.db.execute(
            "INSERT INTO protocol_outcomes(evaluation_id,reported_outcome,evidence_ref) VALUES(?,?,?)",
            (evaluation_id, outcome, evidence_ref))

    def outcomes(self, evaluation_id):
        return [dict(r) for r in self.box.db.execute(
            "SELECT * FROM protocol_outcomes WHERE evaluation_id=? ORDER BY seq",
            (evaluation_id,))]

    def reconstruct(self, evaluation_id):
        """Retrieve exact historical source cards, NOT a new authorization."""
        entries = self.history(evaluation_id)
        if not entries:
            raise KeyError(evaluation_id)
        return [self.load(r) for r in entries[0]["context_refs"]]

    def evaluate(self, references, *, mission_id, actor_seat, action_id, resource,
                 now=None, failure_code=None, attempt=1, hop=1,
                 approval_verifier=None):
        """Produce an inspectable *candidate* decision, never an actual side effect.

        For execution, approval_verifier must be a trusted, independently
        authenticated backend callback accepting a bound request object and
        returning a verified approval record. Merely storing a stamp is inert.
        """
        _id(mission_id, "mission_id"); _seat(actor_seat)
        _id(action_id, "action_id"); _id(resource, "resource")
        if not isinstance(references, list):
            raise ProtocolError("references must be an array")
        if now is None:
            now = datetime.now(timezone.utc)
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise ProtocolError("now must be timezone-aware")
        if type(attempt) is not int or type(hop) is not int or attempt < 1 or hop < 1:
            raise ProtocolError("attempt and hop must be positive integers")
        cards = [self.load(ref) for ref in references]
        pinned = [{"id": c["id"], "revision": c["revision"]} for c in cards]
        if len({(r["id"], r["revision"]) for r in pinned}) != len(pinned):
            raise ProtocolError("duplicate pinned references")
        selected = {}
        for card in cards:
            body = card["body"]
            selected.setdefault(body["protocol_kind"], []).append(
                {"id": card["id"], "revision": card["revision"], **body["spec"]})
        def one(kind, predicate=lambda x: True):
            matches = [x for x in selected.get(kind, []) if predicate(x)]
            return matches[0] if len(matches) == 1 else None
        action = one("action", lambda a: a["action_id"] == action_id)
        tool = one("tool", lambda t: bool(action) and t["tool_id"] == action["tool_id"])
        charter = one("seat_charter", lambda c: c["seat_id"] == actor_seat)
        route = one("route_ticket", lambda r: r["mission_id"] == mission_id)
        def emit(decision, reason, *, permitted_tools=None, extra=None):
            value = {
                "decision": decision, "reason": reason,
                "mission_id": mission_id, "actor_seat": actor_seat,
                "action_id": action_id, "resource": resource,
                "permitted_tools": permitted_tools or [],
                "executes_action": False,
                "external_authorization": "not_verified" if decision != "eligible_after_external_verification"
                    else "verified_by_trusted_callback_only",
            }
            if extra:
                value.update(extra)
            return self._record(mission_id, actor_seat, pinned, value)
        if not all((charter, route, action, tool)):
            return emit("denied", "missing or ambiguous charter/route/action/tool context")
        if route["expires_at"] and _timestamp(route["expires_at"]) <= now.astimezone(timezone.utc):
            return emit("denied", "routing ticket has expired")
        if (action["effect"] != tool["effect"] or tool["server_seat"] != actor_seat
                or action["resource"] != resource):
            return emit("denied", "tool/action/seat/resource mismatch")
        if (action_id not in charter["allowed_actions"]
                or action_id in charter["forbidden_actions"]
                or tool["tool_id"] not in charter["allowed_tools"]):
            return emit("denied", "seat charter forbids the operation")
        if (action_id not in route["allowed_actions"]
                or tool["tool_id"] not in route["allowed_tools"]
                or resource not in route["allowed_resources"]):
            return emit("denied", "route ticket forbids action, tool or resource")

        is_fallback = actor_seat != route["recipient_seat"]
        if is_fallback:
            detour = one("detour", lambda d: d["ticket_id"] == route["id"])
            if not detour or detour["fallback_seat"] != actor_seat:
                return emit("denied", "no authorized detour to this office")
            if (failure_code in BLOCKED_DETOURS or failure_code not in detour["allowed_failure_codes"]
                    or attempt > detour["max_attempts"] or hop > detour["max_hops"]
                    or _timestamp(detour["expires_at"]) <= now.astimezone(timezone.utc)
                    or tool["tool_id"] not in detour["allowed_tools"]
                    or action["effect"] not in PERMITTED_PROPOSAL_EFFECTS):
                return emit("denied", "detour does not permit this failure, operation or retry")
        elif failure_code is not None:
            return emit("denied", "unexpected failure_code without detour")

        communication = one("communication", lambda c:
            c["sender_seat"] == route["origin_seat"] and
            c["receiver_seat"] == route["recipient_seat"])
        if not communication:
            return emit("denied", "missing or ambiguous communication contract")
        if route["ticket_class"] == "ROUND_TRIP_ASSESSMENT":
            if (action["effect"] not in PERMITTED_PROPOSAL_EFFECTS
                    or not communication["return_required"]):
                return emit("denied", "round-trip is return-only; no execution or unreturned work")
        elif route["ticket_class"] == "EVIDENCE_TRANSFER":
            if action["effect"] not in ("read", "propose"):
                return emit("denied", "evidence transfer cannot execute an effect")
        elif route["ticket_class"] == "RECOVERY_DETOUR":
            if action["effect"] not in PERMITTED_PROPOSAL_EFFECTS:
                return emit("denied", "recovery detour cannot execute a protected operation")
        elif route["ticket_class"] == "EXECUTION_ORDER":
            if action["effect"] not in PROTECTED_EFFECTS:
                return emit("denied", "execution order cannot silently change an assessment")
            if is_fallback:
                return emit("denied", "protected execution cannot use a fallback route")

        if action["effect"] in PROTECTED_EFFECTS:
            if route["ticket_class"] != "EXECUTION_ORDER":
                return emit("denied", "execution requires a distinct execution ticket")
            approval = one("approval_reference", lambda a: a["approval_ref"] == route.get("approval_ref"))
            stamp = one("authority_stamp", lambda a: a["approval_ref"] == route.get("approval_ref"))
            if not approval or not stamp:
                return emit("denied", "missing or ambiguous approval reference/stamp")
            expected = {"approval_ref": route["approval_ref"], "mission_id": mission_id,
                        "action_id": action_id, "resource": resource}
            if (any(approval.get(k) != v or stamp.get(k) != v for k, v in expected.items())
                    or stamp["ticket_id"] != route["id"]
                    or stamp["issuer_seat"] != approval["approving_seat"]):
                return emit("denied", "approval or stamp does not match exact action and ticket")
            if not callable(approval_verifier):
                return emit("denied", "trusted external authorization verifier required")
            inquiry = dict(expected, ticket_id=route["id"], recipient_seat=actor_seat,
                           approving_seat=approval["approving_seat"])
            try:
                verified = approval_verifier(dict(inquiry))
            except Exception:
                return emit("denied", "trusted verifier unavailable")
            if not isinstance(verified, dict) or verified.get("valid") is not True:
                return emit("denied", "trusted verifier rejected approval")
            if any(verified.get(k) != v for k, v in inquiry.items()):
                return emit("denied", "trusted verifier scope differs from request")
            return emit("eligible_after_external_verification",
                        "callback attests exact scoped approval; executing backend must revalidate",
                        permitted_tools=[tool["tool_id"]],
                        extra={"ticket_class": route["ticket_class"], "ticket_id": route["id"],
                               "return_to": route["return_to"]})

        return emit("eligible_for_nonexecuting_work",
                    "charter, route, communication and action scopes match; no side effects authorized",
                    permitted_tools=[tool["tool_id"]],
                    extra={"ticket_class": route["ticket_class"], "ticket_id": route["id"],
                           "return_to": route["return_to"]})
