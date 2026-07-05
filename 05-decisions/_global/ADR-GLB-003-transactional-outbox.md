---
doc_meta:
  id: ADR-GLB-003
  title: ADR-GLB-003 Enterprise Transactional Outbox Pattern
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-GLB-003: Mandating the Transactional Outbox Pattern for Secure Asynchronous Domain Event Propagation

---

## 1. Title

Mandating the Transactional Outbox Pattern for Secure Asynchronous Domain Event Propagation

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

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

When a database write or state change occurs, the core business module must write both the primary entity mutation (e.g., updating a user record) and a corresponding lightweight event record to a dedicated database `auth_outbox` table **atomically within the same local SQL transaction**.

To deliver these events, we adopt a **Two-Stage Evolutionary Architecture Plan** that balances operational complexity with extreme-scale performance goals:

### Stage 1: Polling with SKIP LOCKED (Pragmatic Default)

For early-stage monolith/modular monolith applications (including current Phase 1 deployment):

- A background worker processes the outbox table by querying it periodically (e.g., every 500ms).
- To prevent database locking contention, the query MUST use the `SELECT ... FOR UPDATE SKIP LOCKED` clause, allowing multiple workers to safely poll the table concurrently without thread blockages.
- **Table Vacuum Mitigation**: To prevent table bloat and Autovacuum I/O churn caused by continuous delete/update cycles on the outbox table, the schema must leverage partitioning (e.g., daily partitioned tables) to safely truncate processed event blocks in bulk, bypassing row-by-row deletions.

### Stage 2: CDC WAL Logical Replication Streaming (Optimization Phase)

As transaction volume scales and the operational maturity of the platform team justifies the infrastructure overhead:

- We will migrate to **Change Data Capture (CDC) via WAL Logical Replication Streaming**.
- A background CDC Outbox Worker will establish a direct PostgreSQL replication connection (using `pglogrepl`), subscribe to a dedicated replication slot (using the standard `pgoutput` plugin), decode WAL stream inserts into the `auth_outbox` table, and publish them immediately to the enterprise message broker (NATS JetStream).

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
- **Stage 2**: Requires monitoring logical replication slot size, WAL disk space utilization, and NATS JetStream publisher connection states.

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
SELECT id, payload FROM auth_outbox
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
- [Scnehaux IAM System Architecture Document (SAD-001)](../../04-system/scnehaux-iam/scnehaux-iam.sad.md)

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

