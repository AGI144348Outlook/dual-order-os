# Persistent-memory chatbot platform — concept note

Recorded 23 October 2026 at Timothy's request. This planning branch holds the concept until a dedicated repository is created. Status: proposed product, not a launched service.

## User objective

Let customers create named AI bots with persistent memory. Customers may upload exports from AI platforms. A scanner identifies candidate persona exchanges; customers review attribution before records become approved memory. Store originals and derived records privately in R2, connect approved memories to chat, and offer access through subscription.

A bot may assist with creating memory spaces and explaining their status. Backend tools enforce provisioning, ownership, quotas and subscription entitlement. GitHub holds application code and deployment workflows; a repository per customer is optional, not required for persistent memory.

## Proposed architecture

- Cloudflare Workers: application/API, authorization checks and orchestration.
- R2: original exports, derived datasets, attachments and optional model artifacts.
- Database: accounts, bot ownership, messages, versions, jobs, usage and billing entitlement.
- Search index: relevant approved memory retrieval for each reply.
- Compatible model service: response generation from persona configuration, recent chat and retrieved evidence.
- GitHub/Actions: code versioning, tests and deployment.

The customer's stable memory ID/address identifies a resource; a separate credential authorizes access. Folder prefixes organize objects but do not themselves isolate customers.

Keep conversation history, editable remembered facts, and persona configuration separate. Store source references so a memory can be corrected without silently rewriting an original archive.

## First usable flow

1. Sign in; create and name one bot.
2. Chat; return in a later session and retrieve relevant saved memories.
3. Inspect, correct, approve or exclude remembered information.
4. Optionally import one supported export format with branch/source provenance.
5. Export and delete the customer's data.

Start with retrieval-backed memory. Optional LoRA adaptation is a later experiment for a compatible base model; it is not the factual memory database or a transfer of a proprietary provider's original model. Training requires a chosen trainer, evaluated examples, model compatibility and a budget.

## Existing reusable work

Pinned reference: Group_Canvas `8610aa9cfc6bc5437fee47ee348797c06850c5b5`, branch experiment/hierarchy-tower.

- Private multipart archive storage and short-lived file tickets.
- Named-character occurrence and selected-branch session filters.
- Provenance-linked outputs, bounded queries and retrieval cards.
- Retrieval-backed hosted model chat.
- Dataset preparation with review/exclusion and conversation-grouped splits.

These remain prototype components. The existing global operator credential and serialized cabinet actor are not a customer account/tenant system. Dataset preparation and model catalog entries do not establish that training has run.

## Decisions and missing work

Customer authentication and isolation; durable import jobs; search/retrieval evaluation; bot-specific read/write permissions; billing and usage limits; account recovery; correction/export/deletion across original data, indexes, caches and optional adapters; actual per-import/session cost; compatible training and inference options if adaptation is justified.

The first pilot should use synthetic data, then a consenting user, demonstrate source-grounded answers and a cross-customer access-denial test. Validate willingness to pay before pricing unlimited storage, inference or training.

## Scope of this note

Documentation only. No paid compute, training, customer-data transfer, bucket creation, deployment, billing integration or new GitHub repository is started. The later dedicated repository should preserve this concept's provenance and distinguish implemented features from proposals.
