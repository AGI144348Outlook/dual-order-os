# Codex review and proposed integration sequence

Recorded 2026-10-21. This is source inspection and architectural reasoning from the supplied chat code, not an execution report.

## Useful candidate distinctions

A common card envelope; ordered/cyclic deck relationships; routing separate from interpretation and execution permissions; independently inspectable state history; and nested environments whose stable identities survive internal growth are useful design directions. A stable external identity need not mean an unchanging ordinal path when a card moves.

The proposed index-card LCD may describe a common reference envelope for diverse records. What payloads must conform, whether large artifacts are referenced rather than embedded, and which invariants are authoritative still require definition. “Non-local energy,” physical computing performance and “complete self-contained intelligence” are not established by this code.

## What the boilerplate does and does not implement

| Supplied claim | Source-inspection finding |
|---|---|
| Immutable, non-overwriting history | Most root stamps replace field values; port fields, payload and lineage are mutable. add_deck replaces a deck under an existing key. No revision/event history is implemented. |
| Non-collapsing interpretations | Generic metadata can hold data, but there is no explicit sense-alternative, contradiction, branch or resolution protocol. |
| Live structural lineage proof | execute_zero_point_handshake compares two strings. It does not traverse or verify lineage, use freshness/challenges, or establish permission. |
| Protected catalog | unlock_catalog accepts an externally supplied Boolean; decks are directly accessible regardless of the lock. A failed unlock does not relock an already-open box. |
| Zero-compute / physical-grade filtering | sort_deck scans the Python list in linear time. It returns matching references, does not remove cards, and never uses retained_cards afterward. No physical apparatus or performance measurement is supplied. |
| Algorithm execution | The harness changes a status and prints metadata. payload remains None and no transformation is invoked. |
| Active-state tracking | IndexCard defines is_active; the harness instead creates is_initial. Preserve this discrepancy in the source. |
| Operational glyph roots | apply_root_stamp writes metadata; it does not implement perception, naming, identification, transformation or jurisdictional validation. |
| Strict 6-bit ports | Range comparison alone does not enforce an integer type; unknown port names are silently ignored. Validation needs an explicit contract. |

A six-bit code 0–63 is distinct from a traditional hexagram ordinal 1–64. In a straightforward encoding with unbroken=1, The Creative is 111111 (63), and The Receptive is 000000 (0); these are not their King Wen ordinals 1 and 2. Define the numbering scheme, line order, bit polarity, and explicit conversion table before assigning meanings to stored integers. The source's “63 / After Completion” comment also cannot be assumed to describe binary 63.

A rectangular card has two short edges. Four named logical ports are possible; the physical placement of the four proposed edge ports is unresolved. A physical notch apparatus would require its own selection geometry, complement/exclusion behavior and mechanical validation; integer equality is only the behavior of this software sketch. Physical filtering still has work, energy and time costs.

Append-only recorded events can preserve an expanding historical record while active interpretations are withdrawn or superseded. This does not imply that accepted knowledge, permission, or semantic scope must grow monotonically. Storing a new event is not evidence that it is true.

## Proposed integration order — not yet executed

1. Keep the designated fresh runtime empty; keep Swadesh as unlearned curriculum.
2. Specify common card identity/envelope, payload references, sense alternatives, revision/event history, provenance and permissions.
3. Implement a bounded observation card and source-linked “Seen” record. Exposure does not establish recognition or comprehension.
4. Develop recurrence, similarity/difference, provisional labeling, identification and context attachment with independent tests.
5. Add explicit deck membership/order/cycles; investigate six-bit routing separately from semantic authority.
6. Bind allowed operations through actual existing governance and permission mechanisms.
7. Investigate any proposed zero-point handshake against the real Algorithm-000 implementation, without assigning authority by its name.

## Questions left open

- Which aspects of the “LCD” are fixed envelope invariants and which are evolvable contents?
- Are glyph roles conceptual labels, portfolio selectors, or executable bindings in each use?
- How do dormant, candidate, rejected, superseded, tested and authorized states differ?
- What counts as the same entity, a repeated occurrence, or a similar pattern?
- What evidence qualifies a sense for recognition, composition, inference or action?
- What are the exact hexagram routing convention and physical/software selection contracts?
- How do explicit resolution choices preserve unselected alternatives? Reconcile “non-collapsing” with terminal “collapse/resolve” language.
- Which existing Algorithm-000 identity properties apply, and what authority—if any—may a new proof grant?
- How do stable external addresses relate to card movement, nested environment changes and storage paths?

No existing invariant is changed by saving these questions.
