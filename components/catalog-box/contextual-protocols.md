# Contextually Governed Card Protocols (prototype)

**Status:** experimental standalone Python extension on the feature branch. The original [CatalogBox](README.md) retains its stable IDs, revision-pinned card snapshots and SQLite persistence. **No NexusBoard MCP services, Neon authority schema, Cloudflare Agent runtimes, provider tokens, real corporate approvals, or deployments are connected.**

This extension is **not** an institutional identity/memory store. Neon and the individual Cloudflare Durable Objects retain those architectural responsibilities. The catalog provides **typed communications and evidence-bearing instruments** for work traveling between independent corporate Agents.

## Why cards matter

A stored card is neither an executable instruction nor an authorization grant.

- **Evidence:** source/claim relationships may remain provisional and can be carried into a limited evaluation.
- **Routing tickets:** encode mission, sender, receiving office, permitted action, expiration, and return obligation.
- **Communication contracts:** define sender/recipient and required message types/return expectations, without opening a full mesh.
- **Authority-stamp references:** bind a specific approval reference to exact ticket/action/resource/mission. They are **inert metadata** until an independently authenticated service validates the actual approval.
- **Charter, tool and action cards:** describe scoped jurisdiction, required inputs and the requested effect.
- **Detour cards:** represent an explicitly bounded alternative recipient after an availability failure; independent preapproval is still required.

### Version-1 card kinds

| Kind | Required data | What it does not do |
|---|---|---|
| \`seat_charter\` | seat ID, allowed tools/actions, forbidden actions | Issue real credentials or change the constitution |
| \`tool\` | tool ID, serving seat, effect class | Expose an actual MCP endpoint |
| \`action\` | action ID, tool ID, effect class, exact resource | Execute an effect |
| \`route_ticket\` | ticket class, mission, origin/issuer/recipient/return, scopes, expiry | Permit anything beyond scoped work |
| \`communication\` | sender, receiver, message kinds, return requirement | Turn discoverability into permission |
| \`evidence\` | source and claim references, relationship, epistemic state | Prove that a claim is true |
| \`approval_reference\` | approval ID and exact target, approving office | Make approval genuine |
| \`authority_stamp\` | approval reference, issuer, target and ticket | Sign or authenticate the issuer |
| \`detour\` | original ticket, fallback seat, permitted failures, tools, bounded attempts/hops, expiry | Bypass security denial or allow protected deployment |

**Scope:** This is an intentionally narrow **versioned JSON contract**, enforced in Python standard library code by \`validate_card\`. It is not a complete enterprise JSON Schema standard or MCP protocol extension.

## Proposal, assessment, execution and audit stay separate

\`\`\`text
AR evidence encounter --proposes--> COO routing ticket
                                      |
                                      +-- ROUND_TRIP_ASSESSMENT --> CTO
                                      |                            |
                                      |<--- findings/blueprint -----+
                                      |
                                      +-- governing approval decision
                                      |
                                      +-- NEW EXECUTION_ORDER ------> CTO executing backend
                                          (external approval check) |
                                      |
                                      +-- independently attributed outcome / Audit
\`\`\`

A \`ROUND_TRIP_ASSESSMENT\` **never** enables a \`execute\` or \`admin\` effect. A protected \`EXECUTION_ORDER\` must reference the competent external approval and include matching \`approval_reference\` and \`authority_stamp\` cards. Its **trusted backend** must still validate the approval (identity, authority, mission, resource, action, ticket, expiry, revocation and policy versions); \`ProtocolCatalog.evaluate\` invokes an injected \`approval_verifier\` only when configured by the trusted host. A model cannot select or define its own verifier.

Even a positive verifier result means \`eligible_after_external_verification\` **in a local policy preview**; the tool-serving backend MUST independently enforce authorization at the actual side-effect boundary. This library never executes an operation.

## Card revision pinning and contextual disclosure

Use \`ProtocolCatalog.put\` to create validated typed cards in the existing \`cards\` section and retain their usual revisions. Evaluate with an explicit list of exact \`{"id":"...","revision":1}\` references—not an implicit global lookup.

The evaluator selects **one relevant charter, route, tool, action and communication contract**, and returns only the selected tool identifier when the charter, route, message contract, target and effect agree. Unrelated tools cannot be disclosed as granted permissions merely by existing elsewhere in the catalog.

A later change to a charter/route creates a new card revision; evaluations that pinned an earlier revision retain that historical reference. **Historical replay is data reconstruction, not renewed authorization.**

### Minimal offline usage

\`\`\`python
from libraries.catalog_box import CatalogBox
from libraries.contextual_protocols import ProtocolCatalog

with CatalogBox(":memory:") as box:
    protocol = ProtocolCatalog(box)
    # Store explicit, validated cards first with protocol.put(...).
    # Collect their exact returned id/revision pairs in refs.
    # Preview a route without performing any MCP invocation:
    # result = protocol.evaluate(
    #     refs, mission_id="mission001", actor_seat="05",
    #     action_id="plan.review", resource="repo:demo")
    # result["executes_action"] is always False.
\`\`\`

For examples of the input contracts and denial cases, see [offline test fixtures](../../tests/test_contextual_protocols.py). The test suite uses synthetic identities, temporary SQLite files, and **does not create authority tokens or actual service routes**.

## Detours require independent, prior authorization

A fallback seat can be considered only if the original route and the detour's scopes agree; the recorded failure is \`UNAVAILABLE\` or another preapproved operational failure; retries and hops remain within limits; the recipient has its own charter; and a trusted \`detour_verifier\` confirms the preapproved alternate path. \`AUTH_DENIED\`, \`POLICY_DENIED\`, \`REVOKED\` and \`NO_APPROVAL\` are never eligible detour reasons. Protected execution cannot take the fallback route.

The communication contract must describe the **actual receiving office**, not merely the original destination. Thus a detour cannot make another department's duties invisible.

## Temporal receipts (not institutional audit proof)

The extension adds *local* SQLite tables \`protocol_evaluations\` and \`protocol_outcomes\` and records a decision with pinned card refs and an optional **reported** outcome. Historical entries can be reconstructed using \`ProtocolCatalog.reconstruct\`.

They are **not tamper-proof**, not cryptographically signed and not independently verified. Production NexusBoard event/outcome history belongs in the governed Neon Evidence Memory Network with permitted Cloudflare Agent-local checkpoints; source provenance, protected approval records and independent Audit must remain outside the Agent-controlled local log.

## Hard boundaries and open decisions

1. A card's \`issuer_seat\`, \`approval_ref\` or \`authority_stamp\` fields are **asserted data**, never authenticated identity.
2. The caller must bind actual actor/mission identity server-side; model-supplied role IDs are not trustworthy.
3. This proof-of-concept uses exact resource strings and allowlists, not a complete hierarchy, temporal charter evaluator, token issuer, RLS system, or dynamic policy reconfiguration.
4. The trusted callback is a **dependency-injection seam** for an external policy service, not a cryptographic verifier implemented here. Never expose arbitrary callbacks or Python execution to clients or models.
5. Neither \`put\` nor \`report_outcome\` is a protected production endpoint. Future interfaces require authenticated role and action checks.
6. Production must define whether CEO authorization is universally required for deployments or can be exercised under explicitly delegated low-risk standing authorities, subject to founder/Board reservations.
7. For each actual Agent, Cloudflare Durable Object identity and per-Agent SQLite state are to remain distinct from the logical corporate office charter.
8. The local protocol compiler returns a **candidate capability view**. It cannot itself dispatch, approve or certify a company action.

**Pre-test thread and evidence policy:** [Dual Order OS Issue #20](https://github.com/AGI144348Outlook/dual-order-os/issues/20). No tests should run without advance publication there (already posted); results must be appended to the same thread as observations, failures and limitations.
