---
doc_meta:
  id: ADR-GLB-003
  title: ADR-GLB-003 Enterprise Transactional Outbox Pattern
  adr_type: foundational
  status: superseded
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
  governed_by:
    - EAD-004
---

# ADR-GLB-003: Mandating the Transactional Outbox Pattern for Secure Asynchronous Domain Event Propagation

---

## 1. Title

Mandating the Transactional Outbox Pattern for Secure Asynchronous Domain Event Propagation

## 2. Status

| Date       | Status     | ADR Type     | Reviewers                                    | Approver               |
| ---------- | ---------- | ------------ | -------------------------------------------- | ---------------------- |
| 2026-05-01 | accepted   | foundational | Architecture Review Board                    | Enterprise Architect   |
| 2026-08-21 | accepted   | foundational | Architecture Review Board                    | Enterprise Architect   |
| 2026-08-23 | accepted   | foundational | Architecture Authority, Platform Engineering | Architecture Authority |
| 2026-08-24 | superseded | foundational | Architecture Authority, Platform Engineering | Architecture Authority |

The 2026-08-21 entry records two corrections. The broker product is fixed to the Kafka protocol in section 5; the original text named a different product in passing without ever deciding one, so the dispatcher was written against a delivery contract no artifact had chosen. The outbox table is also renamed from `auth_outbox` to `platform.outbox`, matching the schema `foundation-platform` ships. The transactional-outbox decision itself is unchanged.

The 2026-08-23 clarification makes an existing invariant explicit: **Outbox state is local to the authoritative transaction and is not a centralized Platform authority.** Shared relay, CDC, libraries, and operational tooling remain valid after the source transaction commits.

## 3. Context

Changes to critical business entities (such as user logins, password changes, tenant provisioning, and payroll transactions) trigger essential secondary operations across the Scnehaux enterprise (sending notification emails, generating audit logs, and synchronizing directories). Executing these secondary actions synchronously within the primary HTTP request flow degrades API latency and introduces high risk of partial failure.

## 4. Decision Drivers

Publishing domain events directly to an external message broker inside an active database transaction introduces critical weaknesses. If the message broker is temporarily unreachable or experiences network hiccups, the entire local database transaction will block, leading to database connection exhaustion and eventual system outages. The Transactional Outbox pattern guarantees that database state changes and their corresponding event emissions succeed or fail as a single, atomic unit.

### The Operational Reality of CDC vs. Polling:

While CDC via WAL logical replication is theoretically elegant, it introduces **severe operational risks and high blast radius**:

1.  **Replication Slot Maintenance**: If the CDC consumer fails or disconnects, the replication slot remains active, forcing the PostgreSQL primary instance to retain all WAL segments on disk. This can lead to rapid disk exhaustion and database crash loops.
2.  **Backpressure & Replay Complexity**: Managing Log Sequence Numbers (LSN) and stream acknowledgments requires advanced state handling.
3.  **Developer Ergonomics (DX)**: CDC requires elevated database permissions (`REPLICATION` privilege) and advanced system setup, creating friction during local development and testing.

Therefore, we choose **Stage 1 (Polling + SKIP LOCKED)** as our pragmatic default. It offers 99% of the reliability of CDC with a fraction of the operational complexity. We will only transition to **Stage 2 (CDC)** once write throughput reaches scales where SQL executor overhead and table vacuum bloat become the dominant bottlenecks.

---

## 5. Decision

We officially establish the **Transactional Outbox** pattern as the mandatory mechanism for propagating domain events asynchronously across the Scnehaux enterprise.

When a database write or state change occurs, the core business module must write both the primary entity mutation (e.g., updating a user record) and a corresponding lightweight event record to a dedicated `platform.outbox` table **atomically within the same local SQL transaction**.

To deliver these events, we adopt a **Two-Stage Evolutionary Architecture Plan** that balances operational complexity with extreme-scale performance goals:

### Outbox Locality and Non-Platformization

The outbox row **MUST be committed inside the same local transactional resource and transaction boundary** as the authoritative state mutation it represents.

```text
Product / Platform database transaction
├─ authoritative state mutation
└─ local outbox publication intent
        ↓ COMMIT
relay / CDC
        ↓
Kafka
```

A central Outbox database or network service **MUST NOT** be inserted into the source commit path as the publication authority. Doing so recreates the dual-write/distributed-transaction problem this ADR exists to remove.

Shared outbox libraries/schema conventions, relay implementations, CDC infrastructure, Kafka producer adapters, event-schema tooling, telemetry, dashboards, and retention automation are allowed. Shared machinery does not move ownership of the outbox record away from the source Product/Platform transaction.

The pattern is required when a local authoritative transaction and an external event must be logically atomic. A service that only consumes events, or a flow with no local authoritative mutation to coordinate, does not need an outbox merely because it is event-driven.

### Broker Product: the Kafka Protocol

Both stages publish into the same broker, and that broker is fixed here because the dispatcher is written against one delivery contract rather than against a family of them.

**We commit to the Kafka protocol, not to a single Kafka distribution.** The protocol is the contract; the implementation is an operational choice per environment:

| Environment              | Implementation                                                                            |
| :----------------------- | :---------------------------------------------------------------------------------------- |
| Production               | A managed Kafka service with a replication factor of `3` spread across availability zones |
| Local development and CI | A single-binary Kafka-API broker, or Kafka in KRaft mode                                  |

Four properties decided it:

1. **Log semantics with replay by position.** The outbox assigns a monotonic stream position and consumers reconcile against a snapshot high-water mark. That requires an append-only log addressable by offset. A queue broker, which acknowledges and discards, cannot answer "replay everything after position N" without an additional store.
2. **The reserved priority lane is a separate topic.** Security events and lifecycle events occupy distinct topics with distinct consumer groups, partition counts, and capacity. A lifecycle backlog therefore cannot produce head-of-line blocking ahead of a revocation.
3. **A schema registry exists off the shelf.** `STD-GLB-004` mandates a centralized schema registry with build-time compatibility validation. The Kafka ecosystem supplies one as a deployable component, so that mandate is met by configuration rather than by a bespoke service.
4. **The analytical replication path in `EAD-003` uses the same backbone.** Change Data Capture into the analytical estate is a first-class, widely deployed Kafka capability, so Stage 2 and the analytical estate share one transport instead of two.

**Ordering is per partition, never global.** The stream position allocated by the outbox is monotonic within a publisher, and Kafka preserves order only inside one partition. Producers therefore partition by `aggregate_id`, which yields per-aggregate ordering — the guarantee consumers depend on. Consumers reconcile authority through version comparison and deduplicate on `event_id`, so a later position arriving before an earlier one is a handled case rather than a defect. A producer that partitions on any other key silently removes the per-aggregate guarantee while every test continues to pass.

### Stage 1: Polling with SKIP LOCKED (Pragmatic Default)

For early-stage monolith/modular monolith applications (including current Phase 1 deployment):

- A background worker processes the outbox table by querying it periodically (e.g., every 500ms).
- To prevent database locking contention, the query MUST use the `SELECT ... FOR UPDATE SKIP LOCKED` clause, allowing multiple workers to safely poll the table concurrently without thread blockages.
- **Table Vacuum Mitigation**: To prevent table bloat and Autovacuum I/O churn caused by continuous delete/update cycles on the outbox table, the schema must leverage partitioning (e.g., daily partitioned tables) to safely truncate processed event blocks in bulk, bypassing row-by-row deletions.

### Stage 2: CDC WAL Logical Replication Streaming (Optimization Phase)

As transaction volume scales and the operational maturity of the platform team justifies the infrastructure overhead:

- We will migrate to **Change Data Capture (CDC) via WAL Logical Replication Streaming**.
- A background CDC Outbox Worker will establish a direct PostgreSQL replication connection (using `pglogrepl`), subscribe to a dedicated replication slot (using the standard `pgoutput` plugin), decode WAL stream inserts into the `platform.outbox` table, and publish them immediately to the enterprise message broker. The product is fixed below.

---

## 6. Consequences

### Positive

- **Guaranteed Consistency**: Eliminates dual-write anomalies; events are guaranteed to be persisted if and only if the database state transaction commits.
- **Low Operational Overhead (Stage 1)**: Highly straightforward to implement, test, and run locally without specialized database permissions.
- **Fail-Secure & High Resilience**: Processed events can readily be retained or replayed from the partition if downstream delivery fails.

### Negative

- **Eventually Consistent States**: Secondary systems (e.g., search indexes, notifications) lag behind the primary database by the length of the polling interval (e.g., 100ms - 500ms).
- **Latency Floor**: Stage 1 introduces a latency floor locked to the polling cycle (e.g., 500ms).
- **Unnecessary DB Wakeups**: Periodic SQL execution occurs even when no events are pending (mitigated by exponential backoff on empty polls).

### Tradeoffs

- We trade minor latency delays (in milliseconds) and occasional database wakeups for reduced operational complexity, safety, and rapid time-to-market.

### Operational Impact

- **Stage 1**: Requires monitoring outbox table size and configuring automatic pruning jobs on partitioned tables.
- **Stage 2**: Requires monitoring logical replication slot size, WAL disk space utilization, and Kafka producer connection states.

### Security Impact

- Ensures event audit trails are recorded atomically inside the transactional boundary.

### Scalability Impact

- Polling `SKIP LOCKED` allows horizontally scaled background workers to process independent batches of events concurrently without locking conflicts, easily supporting several thousand transactions per second.

---

### Operational

### Stage 1 Polling Dispatcher Code Pattern:

In Go, the polling worker executes a transaction-safe query utilizing `SKIP LOCKED`:

```sql
-- Retrieve and lock a batch of pending events safely
SELECT id, payload FROM platform.outbox
WHERE state = 'pending'
ORDER BY occurred_at ASC
LIMIT $1
FOR UPDATE SKIP LOCKED;
```

The dispatcher processes the batch, publishes the events, and updates their state to `delivered` or deletes them in a single transaction, or delegates the deletion to bulk partition truncation.

### Stage 2 CDC pglogrepl Migration Template:

When scaling demands CDC migration, the adapter establishes a logical replication connection:

```go
// Establish logical replication connection
conn, err := pgconn.Connect(ctx, "replication=database")
// Create replication slot and start replication using pgoutput
err = pglogrepl.StartReplication(ctx, conn, "scnehaux_outbox_slot", startLSN, pglogrepl.StartReplicationOptions{PluginName: "pgoutput"})
```

---

## 7. Compliance Impact

### Related Standards

- [Enterprise Application Architecture Strategy (EAD-004)](../../01-enterprise/EAD-004-enterprise-integration-architecture.md)
- [Scnehaux Identity Runtime (SAD-001)](../../04-system/scnehaux-iam/scnehaux-identity-runtime.sad.md)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Pure Periodic Polling Without Concurrency Protections

- **Pros**: Standard SQL.
- **Cons**: Lacks `SKIP LOCKED`, resulting in heavy row locks, thread blockages, and severe performance degradation under high concurrent login volumes.
- **Why Rejected**: Standard polling without concurrency protection is a severe bottleneck.

### Alternative B: Direct App-Layer / Broker-In-Transaction Publishing

- **Pros**: Straightforward, no persistent database outbox table required.
- **Cons**: Dual-write consistency hazards. If the broker is unreachable, commits succeed but events are permanently lost, leading to silent state drift across downstream systems.
- **Why Rejected**: Unacceptable risk of state inconsistencies in core transactional domains.

---

### Alternative C: NATS JetStream as the Broker Product

- **Pros**: A single Go binary with no JVM and no external coordination service, the lowest operational footprint of the candidates. Streams provide replay by sequence, subject hierarchies map onto the priority-lane split, and durable consumers carry a native retry-backoff array and delivery ceiling.
- **Cons**: No schema registry exists as a deployable component, so the centralized registry mandated by `STD-GLB-004` would remain a bespoke build indefinitely. The analytical replication path in `EAD-003` would require a hand-built connector rather than an existing one. JetStream is materially younger than the alternative, and its clustered stream-state recovery has a shorter production record than a Tier-0 revocation path warrants.
- **Why Rejected**: Two standing enterprise mandates — a centralized schema registry and Change Data Capture into the analytical estate — are satisfied by existing components under the Kafka protocol and by bespoke work here. The operational saving is real, and it is smaller than the cost of building and owning both.

### Alternative D: RabbitMQ as the Broker Product

- **Pros**: The longest production record of the candidates as a message broker, mature routing topologies, native dead-letter exchanges, per-queue priority, and quorum queues for high availability. The Streams feature supplies an append-only log with offset-based consumption, so the replay requirement is reachable.
- **Cons**: Reaching the replay requirement means adopting Streams alongside classic queues, which places two delivery models in one deployment. The schema-registry and Change Data Capture ecosystems are markedly smaller than the Kafka protocol's, so both enterprise mandates again become bespoke work.
- **Why Rejected**: Capable of the mechanics, and it carries the same two ecosystem gaps as Alternative C while adding a second delivery model to operate.

### Alternative E: Centralized Outbox Platform / Database

- **Pros**: One operational surface and one apparent event-publishing service
- **Cons**: The source database commit and central outbox write become separate failure domains, recreating dual-write or requiring distributed transactions
- **Why Rejected**: Transactional Outbox derives its guarantee from source-local atomicity. Shared relay/CDC/tooling is allowed, but the outbox record itself remains local to the authoritative transaction
