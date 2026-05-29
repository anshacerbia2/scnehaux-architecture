---
doc_meta:
  id: STD-GLB-002
  title: Enterprise Database & Persistence Strategy
  owner: Enterprise Architect
  version: 1.1.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Enterprise Database & Persistence Strategy (STD-GLB-002)

---

## 1. Objective & Scope

This standard defines the certified database technologies, migration tools, query frameworks, database partitioning mechanisms, data archiving structures, change data capture pipelines, and replication routing policies for all services within the Scnehaux enterprise. 

It applies to all persistent relational stores, document stores, caches, and key-value stores. It enforces database reliability, query performance SLAs, and tenant separation at the persistence layer.

---


## 2. Design Principles

*(TBD - Architectural philosophy guiding these rules)*

## 3. Normative Rules

### Certified Persistence Standards

To prevent technology fragmentation, development teams must strictly select from the following certified patterns based on their technology stacks:

| Pattern / Tech Stack | Backend Languages | Migration Engine | Query/ORM Engine | Recommended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Declarative SQL** | Golang, Rust | **Atlas** (HCL-based) | **SQLC** (Type-safe compile SQL) | Core IAM, Ledger, and High-Performance critical paths. |
| **Modern ORM** | Node.js, TypeScript | **Prisma** | **Prisma Client** | Rapid application domains, Content Management (CMS), Admin Tools. |
| **Cache & Rotation** | Go, Node.js | N/A | **Redis (v7+)** | Session cache, sliding-window rate limiters, token rotation families. |
| **NoSQL / Document** | Go, Node.js | N/A | **MongoDB / DynamoDB** | Unstructured document catalogs, high-throughput key-value logs (under designated decision matrix). |

#### NoSQL vs. Relational Decision Matrix

Database selection must comply with the following taxonomy. Utilizing an engine outside these parameters requires a formal architectural waiver.

```
                         [Persistence Choice]
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
 [Relational Workload]                            [NoSQL Workload]
  - Multi-Entity ACID transactions                 - Hierarchical documents (JSON)
  - Row-Level Security (RLS)                       - High-velocity append-only data
  - Complex JOINs & Aggregations                   - Key-Value lookup with sub-10ms SLA
         │                                                 │
         ▼                                  ┌──────────────┴──────────────┐
  [PostgreSQL 16+]                          ▼                             ▼
                                   [Document Store]               [Key-Value Store]
                                   - Dynamic Schemas             - High-scale cache
                                   - Nested catalogs             - Rate limiting
                                            │                             │
                                            ▼                             ▼
                                    [MongoDB v7+]                  [Redis v7+]
```

##### Relational Database: PostgreSQL (v16+)
- **Consistency Model**: Immediate consistency with strict ACID compliance.
- **Query Latency SLA**: Read operations $\le 20ms$, Write operations $\le 50ms$ at 95th percentile.
- **Constraints**: Relational schemas must be normalized to Third Normal Form (3NF) unless denormalization is verified to resolve a rendering bottleneck.

##### Document Database: MongoDB (v7+)
- **Consistency Model**: Eventual consistency permitted for read replicas; strong consistency on primary writes.
- **Query Latency SLA**: Read operations $\le 15ms$, Write operations $\le 30ms$ at 95th percentile.
- **Constraints**: Joins (`$lookup`) are prohibited in high-frequency queries. Documents must be self-contained and limited to a maximum size of `16MB`.

##### High-Throughput Key-Value: DynamoDB
- **Consistency Model**: Single-digit millisecond eventual consistency by default; strongly consistent reads are optional.
- **Query Latency SLA**: Read and write operations $\le 10ms$ at 99th percentile.
- **Constraints**: All tables must employ a single-table design pattern. Scan operations are prohibited in production runtimes; queries must fetch records strictly using partition keys.

---

### Database Partitioning & Tenant Isolation

To support large-scale multi-tenant enterprise data without performance degradation:

#### Tenant-Level Partitioning
- **Partition Key Requirement**: Relational databases containing tenant-scoped data must partition tables using a composite partition key consisting of `(tenant_id, id)`.
- **Row-Level Security (RLS)**: PostgreSQL tables containing `tenant_id` must enable RLS:
  ```sql
  ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
  CREATE POLICY tenant_isolation_policy ON accounts
    USING (tenant_id = current_setting('app.current_tenant', true));
  ```
- **Context Activation**: Application data adapters must execute connection initialization mapping tenant identities using session parameters prior to executing nested transactions:
  ```go
  tx.Exec(ctx, "SET LOCAL app.current_tenant = $1", tenantID)
  ```

#### Time-Series Partitioning
- **Hypertable Allocation**: Telemetry, events, and audit logs must utilize time-series partitioning (e.g. TimescaleDB hypertables or native PostgreSQL declarative partitioning).
- **Partition Range Intervals**:
  - *High-Velocity Logs*: Partition intervals must be set to `24 hours` (1 day).
  - *Standard Audit History*: Partition intervals must be set to `7 days` (1 week).
- **Automated Partition Maintenance**: A scheduled cron utility must pre-create empty partitions for the upcoming 7-day window and drop expired partition tables automatically according to the retention policies defined in STD-E019.

---

### Data Archival & Storage Tiering

All persistent data must transition through defined storage lifecycle tiers to optimize database host resources:

```
[Hot Tier] (SSD) ──(After 90 Days)──► [Warm Tier] (HDD/Replicas) ──(After 365 Days)──► [Cold Tier] (S3/Parquet)
```

#### Hot Storage (Active Operational Tier)
- **Engine**: SSD-backed high-IOPS PostgreSQL or MongoDB primary nodes.
- **Lifespan**: Data accessed within the last 90 days.
- **Access SLA**: Sub-50ms query execution.

#### Warm Storage (Read-Only Archive Tier)
- **Engine**: Local historical tables or compressed partition tables on read-replicas.
- **Lifespan**: Data older than 90 days but under 365 days.
- **Access SLA**: Sub-2s query execution. Altering or writing to warm storage is prohibited.

#### Cold Storage (Frozen Analytical Tier)
- **Engine**: Compressed Apache Parquet files exported to object storage (Amazon S3 / Google Cloud Storage).
- **Lifespan**: Data older than 365 days.
- **Access SLA**: Under 5 minutes via serverless query engines (Athena/Presto). Cold storage files must be read-only and encrypted using envelope keys managed by AWS KMS or GCP KMS.

---

### Change Data Capture (CDC) & Outbox Integration

To guarantee transactional integrity and prevent data drift during asynchronous event propagation:

```
[Application Write] ──► [PostgreSQL Transaction (Outbox Table)]
                                   │
                                   ▼ (WAL Log)
                          [Debezium Connector]
                                   │
                                   ▼
                           [Kafka Event Bus]
```

#### Transactional Outbox Pattern
- **Atomic Operations**: Services updating state must record outgoing event envelopes within the same database transaction. The events must be appended to an `outbox` table in the local schema boundary.
- **Schema Separation**: Direct external service access to internal domain tables is prohibited. Data sync must rely strictly on event messages.

#### CDC Engine (Debezium & Kafka)
- **WAL Extraction**: A dedicated Debezium connector must monitor the PostgreSQL Write-Ahead Log (WAL). Debezium must extract updates to the `outbox` table and stream them to Kafka/NATS.
- **Deduplication Strategy**: Incoming outbox streams must use a composite unique identifier (`event_id` or `message_id`) to enforce idempotent processing at the consumer boundary.

---

### Read Scaling, Replication & Routing Rules

To avoid premature complexity while ensuring a clear path to scale read capacity under heavy load:

#### Single Primary Database Pool Default (Baseline)

1.  **Default Mode**: All newly deployed microservices must connect to a single database primary node instance for both read and write queries. The use of read-replicas by default is prohibited to prevent eventual consistency anomalies and replication lag.
2.  **Benefits**: Guarantees read-after-write consistency and eliminates transactional out-of-sync states during active user sessions.

#### Conditional Read Replica Scaling Gate (Future-State)

Read/Write connection segregation and dedicated read replicas are authorized for activation if and only if one of the following production criteria is met:

- **Primary Read CPU Threshold**: Read operations consume greater than `70%` of primary database CPU resources continuously for a duration of `10 minutes`.
- **Query Volume Threshold**: Read query volume exceeds `5000 read QPS`.
- **Latency SLA Breach**: Relational read SLA latency exceeds `20ms` (at p95) due to thread starvation or CPU limits on the primary database node.

#### Read/Write Connection Segregation Invariants

When the Conditional Scaling Gate is activated, the service must implement the following segregation rules:

1.  **Dual Connection Pools**: Service initializations must establish distinct connection pools for write and read operations:
    ```go
    type DBClient struct {
        Writer *sql.DB // Connects to Primary
        Reader *sql.DB // Connects to Replica Cluster
    }
    ```
2.  **Routing Separation**: Write operations (`INSERT`, `UPDATE`, `DELETE`) and read operations executing inside a writing transaction block must run on the `Writer` pool. Regular read queries must route to the `Reader` pool.

#### Replication Lag & Actor-Pinning Mitigations

To prevent user session inconsistencies resulting from replication lag:

1.  **Lag Routing Fallback**: If replica replication lag exceeds `1000ms`, the application query router must route high-priority queries (such as session credential verifications) back to the `Writer` database automatically.
2.  **Actor-Pinning Mechanism**: Following a write transaction initiated by a user, all subsequent read requests from that specific user (actor) must be pinned to the `Writer` pool for a duration of `2000ms`. This prevents the user from observing stale states before replication sync completes.

---

### Schema Evolution & Migration Rules

- **Declarative Source of Truth**: All relational table definitions must be written in HCL (`schema.hcl`) and committed to source control.
- **Versioned Migrations**: Direct manual SQL executions (DDL) in staging or production environments are strictly prohibited. Migrations must be generated as versioned SQL scripts using:
  ```bash
  atlas migrate diff <migration_name>
  ```
- **Lock-Free Migrations**:
  - *No Table Locks*: Adding columns with default values must use nullable fields or default values added after creation to prevent table-rewrite locks.
  - *Concurrent Indexing*: Indexes must be created using the `CONCURRENTLY` keyword in PostgreSQL.
- **Failsafe Executions**: The CD pipeline must execute migrations inside a transactional rollback boundary using `atlas migrate apply`.

---


## 4. Exceptions & Alternatives

Deviations from these normative rules require an approved exception waiver from the Architecture Review Board (ARB).

## 5. Enforcement Mechanism

- **Schema Lint Checks**: CI gates must execute `atlas migrate lint` on every Pull Request. Any destructive change (e.g. dropping columns) or locking operation blocks the build pipeline.
- **Replication Lag Monitoring**: Infrastructure alerts must trigger pages if database replication lag exceeds `1000ms` for more than 5 consecutive minutes.
- **Waiver Protocol**: The use of any uncertified persistence engine (or utilizing certified engines outside their decision matrix parameters) requires an approved ADR and Architecture Review Board (ARB) exception sign-off.
