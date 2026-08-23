---
doc_meta:
  id: STD-GLB-004
  title: Enterprise Event-Driven Architecture & Messaging Standard
  owner: Enterprise Architect
  version: 2.0.0
  status: approved
  classification: public
  governed_by:
    - EAD-004
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-14
---

# Enterprise Event-Driven Architecture & Messaging Standard (STD-GLB-004)

---

## 1. Objective & Scope

This standard establishes the mandatory message structures, publishing mechanisms, delivery guarantees, consumer retry behaviors, and schema evolution models for all asynchronous messaging systems within the Scnehaux enterprise.

It applies to all publish-subscribe configurations, message queue integrations, and event streaming architectures utilizing Apache Kafka, RabbitMQ, or equivalent brokers.

---

## 2. Design Principles

Asynchronous event pipelines must guarantee at-least-once delivery with idempotent consumers. Event schemas are immutable contracts governed by strict versioning to prevent downstream consumer breakage.

## 3. Normative Rules

### Event Payload Schema Specification

To ensure interoperability across heterogeneous services, all asynchronous events must conform strictly to the **CloudEvents 1.0** specification in JSON format.

- **Required Envelope Fields**:
  - `specversion`: Must be exactly `"1.0"`.
  - `type`: Structured type name indicating domain event (e.g., `com.scnehaux.iam.user.created`).
  - `source`: URI identifying the emitting service (e.g., `/services/iam-service`).
  - `id`: Unique event identifier (UUID v4 or v7) for deduplication.
  - `time`: RFC 3339 UTC timestamp.
  - `datacontenttype`: Must be `"application/json"`.
  - `data`: The domain-specific event payload.
- **Ordered Projection Extension**: A publisher whose events support snapshot bootstrap
  or ordered projection must add the CloudEvents extension `streamposition` as a
  positive integer. The value is monotonic within one declared publisher stream, may
  contain gaps, and must not be treated as an entity identifier or broker offset.
- **Example Compliant Payload**:
  ```json
  {
    "specversion": "1.0",
    "type": "com.scnehaux.iam.user.created",
    "source": "/services/iam-service",
    "id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
    "time": "2026-05-22T10:00:00Z",
    "datacontenttype": "application/json",
    "streamposition": 10482,
    "data": {
      "user_id": "usr_99a82f",
      "tenant_id": "ten_1028a",
      "email": "user@scnehaux.com"
    }
  }
  ```

---

### Transactional Outbox Pattern

To prevent dual-write inconsistencies, services must never write to a database and directly publish to an external message broker within the same execution path.

- **Outbox Write**: Services must write both the business entity mutation and an outbox event record into the same transactional database database block.
- **Applicability**: A Transactional Outbox is **REQUIRED** when one local authoritative state transaction and one or more external event publications must be logically atomic. Consumer-only services or flows with no coordinated local mutation **MUST NOT** add an outbox solely for architectural uniformity.
- **Transaction Locality**: The authoritative mutation and its outbox publication intent **MUST** commit in the same local transactional resource and transaction boundary.
- **No Central Outbox Authority**: A source service **MUST NOT** synchronously write its publication intent to a separate central Outbox database/service as part of the business commit path. That is a distributed dual-write, not Transactional Outbox.
- **Shared Delivery Machinery**: Relay code, CDC infrastructure, Kafka producer adapters, schema libraries, telemetry, and operational tooling **MAY** be provided as shared Engineering & Runtime machinery after local commit.
- **Ownership**: Outbox records remain owned by the Product/Platform whose transaction created them. A shared relay **MUST NOT** become authoritative for Product business state.
- **Equivalent Atomic Mechanism**: A system **MAY** use another mechanism only when it proves an equivalent atomic/no-silent-loss property for the authoritative mutation and publication intent.
- **Outbox Schema**: The outbox table must contain:
  - `event_id`: Primary key (UUID).
  - `event_type`: String.
  - `payload`: JSONB.
  - `published`: Boolean (indexed).
  - `created_at`: Timestamp.
- **Projection Position**: An outbox serving an ordered projection must allocate its
  row sequence and envelope `streamposition` from the same value in one database
  statement. A snapshot high-water mark must be read in the same database snapshot as
  the authoritative rows it describes.
- **Relay Processing**: An independent outbox relay processor must poll the outbox table (e.g., using Change Data Capture / CDC or transactional polling), publish events to the broker, and update the table state.

---

### Delivery Semantics & Idempotency

Messaging must guarantee delivery while protecting consumers from duplicate message processing.

- **Delivery Guarantee**: The system guarantees **At-Least-Once** delivery. Exactly-Once processing must be achieved at the consumer level through application-level deduplication.
- **Consumer Idempotency**: Consumers must track processed event IDs in an idempotent storage table (e.g. `processed_events` with a unique index on `event_id`).
- **Authority Versioning**: A stream that can be reordered by a priority lane and can
  grant or remove authority must carry the aggregate's monotonic authority version in
  every state event. Consumers must compare that version with their accepted desired
  state and mark an older operation superseded. Neither arrival order nor
  `streamposition` may authorize an older state to overwrite a newer one.
- **Deduplication Check**: Before applying an event, the consumer must verify whether
  `event_id` exists in deduplication storage. If present, the message must be
  acknowledged and ignored. For an external side effect that cannot share this database
  transaction, the consumer must atomically persist a local operation and the
  deduplication mark, acknowledge the broker message, and execute the operation through
  an idempotent retry worker.
- **Snapshot Bootstrap**: A projection consumer must establish its durable subscription
  before requesting a snapshot, buffer deliveries, load the snapshot and its high-water
  mark, then apply only buffered events whose `streamposition` is greater than the mark.
  This ordering is mandatory unless a broker adapter proves an equivalent atomic
  snapshot-to-offset mapping.

---

### Consumer Retries & Dead Letter Queues (DLQ)

Transient processing errors must not block event stream consumption or cause message loss.

- **Ownership Boundary**: Producer outbox retries cover publication to the broker only.
  They never satisfy retry requirements for a consumer handler or its downstream side
  effects.
- **Initial Retry Phase**: A failing consumer operation must be retried by the consuming
  adapter or its durable operation worker up to `3` immediate attempts using exponential
  backoff. Broker acknowledgement must follow the consumer's declared durability point.
- **DLQ Routing**: If all immediate attempts fail, the consumer must persist or route the
  message together with failure metadata, attempt count, timestamps, consumer identity,
  and replay status to its designated DLQ. Security-priority operations must remain
  unresolved and alerted until successful replay or reconciliation proves the intended
  state.
- **DLQ Monitoring**: DLQ volumes must trigger alerts. Human operator evaluation or automated reconciliation scripts must process DLQ messages.

---

### Event Versioning & Schema Evolution Rules

To prevent downstream consumer failures during schema changes, services must adhere to strict compatibility contracts:

- **Default Compatibility Mode**: Event schemas must support **Backward Compatibility** by default. Consumers running older code versions must be able to parse payloads emitted by newer publishers.
- **Backward-Compatible Schema Changes**:
  - _Field Additions_: Permitted. New fields must be optional or have a default value.
  - _Field Deletions_: Prohibited. Fields must be marked as deprecated first and cannot be removed until all consumer systems have migrated off them.
  - _Field Type Modifications_: Prohibited. Data types of existing attributes must not be altered (e.g., converting an integer ID to a string UUID).
- **Major Version Promotion**:
  - When breaking schema modifications are required, the event must be published under a new major version namespace.
  - The version indicator must be embedded directly in the event type identifier (e.g., promoting `com.scnehaux.iam.user.created` to `com.scnehaux.iam.user.created.v2`).
- **Dual-Field Publishing Migration Pattern**:
  - To rename a schema field (e.g., migrating `name` to `full_name`), the publisher must populate both properties concurrently during the transition phase:
    ```json
    {
      "name": "John Doe",
      "full_name": "John Doe"
    }
    ```
  - Publishers must continue to populate both fields until all dependent downstream consumer services have updated their code to read the new property.
- **Centralized Schema Registry**: Every event schema must be registered in the enterprise Schema Registry. The registry must validate every schema check-in for backward compatibility before permitting compilation.

---

## 4. Exceptions

None. All event-driven architecture rules apply unconditionally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

1. **Schema Registry Validation**: Build validation pipelines must check event models against the centralized schema registry. Schema modifications that break backward compatibility rules must block the build.
2. **Consumer Group Audit**: All services running consumer groups must register their offsets and lagging metrics under the enterprise observability stack.
3. **Outbox Locality Check**: Architecture/code review verifies transactional publishers persist publication intent in the same local transaction as the authoritative mutation and do not call a central Outbox service in the commit path.
4. **Exception Waivers**: Deviations from these event-driven architecture requirements require an approved Architectural Decision Record (ADR) and approval by the Architecture Review Board.
