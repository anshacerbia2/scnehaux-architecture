---
doc_meta:
  id: STD-GLB-004
  title: Enterprise Event-Driven Architecture & Messaging Standard
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-05-22
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
- **Example Compliant Payload**:
  ```json
  {
    "specversion": "1.0",
    "type": "com.scnehaux.iam.user.created",
    "source": "/services/iam-service",
    "id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
    "time": "2026-05-22T10:00:00Z",
    "datacontenttype": "application/json",
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
- **Outbox Schema**: The outbox table must contain:
  - `event_id`: Primary key (UUID).
  - `event_type`: String.
  - `payload`: JSONB.
  - `published`: Boolean (indexed).
  - `created_at`: Timestamp.
- **Relay Processing**: An independent outbox relay processor must poll the outbox table (e.g., using Change Data Capture / CDC or transactional polling), publish events to the broker, and update the table state.

---

### Delivery Semantics & Idempotency

Messaging must guarantee delivery while protecting consumers from duplicate message processing.

- **Delivery Guarantee**: The system guarantees **At-Least-Once** delivery. Exactly-Once processing must be achieved at the consumer level through application-level deduplication.
- **Consumer Idempotency**: Consumers must track processed event IDs in an idempotent storage table (e.g. `processed_events` with a unique index on `event_id`).
- **Deduplication Check**: Before processing an event, the consumer must verify if the `event_id` exists in the deduplication storage. If present, the message must be acknowledged and ignored.

---

### Consumer Retries & Dead Letter Queues (DLQ)

Transient processing errors must not block event stream consumption or cause message loss.

- **Initial Retry Phase**: Failing consumer executions must be retried locally up to `3` times using exponential backoff.
- **DLQ Routing**: If all local retries fail, the consumer must write the message along with failure metadata (exception details, time, consumer group) to a designated Dead Letter Queue (DLQ).
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
3. **Exception Waivers**: Deviations from these event-driven architecture requirements require an approved Architectural Decision Record (ADR) and approval by the Architecture Review Board.
