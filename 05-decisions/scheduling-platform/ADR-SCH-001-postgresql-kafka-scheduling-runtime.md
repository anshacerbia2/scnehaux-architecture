---
doc_meta:
  id: ADR-SCH-001
  title: ADR-SCH-001 PostgreSQL Temporal Authority and Kafka Dispatch
  adr_type: implementation
  status: accepted
  created: 2026-08-22
  created_date: 2026-08-22
  created_by: Scheduling Platform Team
  governed_by:
    - PAD-PLT-011
---

# ADR-SCH-001: PostgreSQL Temporal Authority and Kafka Dispatch

## 1. Title

Use PostgreSQL as the initial durable temporal authority and the enterprise Kafka protocol for due-occurrence dispatch.

## 2. Status

| Date | Status | ADR Type | Reviewers | Approver |
| :-- | :-- | :-- | :-- | :-- |
| 2026-08-22 | accepted | implementation | Scheduling Platform, Platform Engineering, Architecture Authority | Architecture Authority |

## 3. Context

PAD-PLT-011 requires a multi-tenant durable Scheduling capability that survives process loss, supports multiple runtime replicas, produces stable occurrence identities, and dispatches due work without executing consumer business code.

Scnehaux already adopts PostgreSQL for transactional persistence, Kafka for enterprise asynchronous delivery, the transactional-outbox pattern for reliable publication, Go for server-side control systems, and OpenTelemetry for telemetry. Adding a Redis-backed task framework, a second queue broker, or a paid managed scheduler would increase operational surface without closing a current capability gap.

An in-memory cron scheduler is insufficient as the authority because schedule ownership and next-fire state would disappear or become ambiguous across replicas. A recurrence parser remains useful for deterministic calculation, but it is not the durable system of record.

The expected initial estate is more than ten consuming applications rather than internet-scale timer cardinality. The architecture therefore needs horizontal correctness and a clean evolution path without prematurely introducing a bespoke distributed timing algorithm.

## 4. Decision Drivers

- Reuse adopted PostgreSQL and Kafka operational capabilities
- No paid runtime dependency
- Durable Schedule and Occurrence authority independent of process memory
- Native multi-replica execution without a singleton leader for correctness
- Atomic occurrence materialization and publication intent
- At-least-once dispatch with stable occurrence identity
- Multi-tenant isolation and quota from the first release
- Low operational complexity relative to a new Redis/RabbitMQ/worker framework
- Replaceable recurrence calculator and future replaceable timing kernel
- Custom Scnehaux control experience rather than third-party operational UI

## 5. Decision

The initial Scheduling runtime SHALL use:

- **Go** for the Scheduling control/runtime service
- **PostgreSQL** as authoritative durable state for Schedule lifecycle, next-fire state, Occurrences, idempotency, ownership projections, and the transactional outbox
- **Kafka protocol** as the asynchronous due-occurrence dispatch contract
- **OpenTelemetry** for traces, metrics, and logs
- **Scnehaux-owned web experience** for Scheduler operations; no library/vendor operational UI is part of the product architecture

### 5.1 Temporal Authority

PostgreSQL is the initial durable temporal authority. Correctness-critical schedule state is never held exclusively in process memory.

Multiple runtime replicas claim disjoint due work through short transactional row-claim coordination consistent with the enterprise database and outbox patterns. Exact SQL, indexes, table layout, claim-batch algorithm, and recurrence-library choice belong in downstream TDDs and implementation standards.

The transaction that materializes a due Occurrence SHALL atomically:

1. establish the stable logical Occurrence
2. advance or finalize the Schedule's next temporal state
3. record the publication intent in the transactional outbox

No external network call occurs while the authoritative due-state transaction is held.

### 5.2 Recurrence Calculation

A proven free/open-source recurrence library MAY be used as a pure calculator for parsing a supported recurrence definition and computing future instants.

The library SHALL NOT become the durable schedule authority. Its process memory, goroutines, timers, internal scheduler registry, or leader behavior are not relied upon for correctness.

The recurrence implementation is compatibility-sensitive. Its behavior is protected by a versioned contract and time-zone golden corpus so the library can be replaced without changing consumer semantics.

### 5.3 Dispatch

The outbox relay publishes a versioned due-occurrence event to Kafka. Kafka acknowledgement establishes Scheduler dispatch durability. Consumer business completion is not stored as Scheduler truth.

Partitioning follows the enterprise event standard and preserves ordering required by one Schedule aggregate. Consumers deduplicate by stable occurrence identity.

### 5.4 Runtime Shape

The initial runtime is one independently deployed Go application with bounded modules for control API, temporal calculation, due claiming, occurrence materialization, outbox relay, target projection, quota/admission, and operational queries. Background loops are part of this deployable until measured scale or failure isolation justifies physical extraction.

This runtime is horizontally replicated across availability zones. A singleton leader is not a correctness prerequisite for due claiming.

### 5.5 User Experience

The Scheduler operational experience is a separate Scnehaux-owned deployable. It calls only governed Scheduler APIs and never reads PostgreSQL or Kafka directly. Third-party monitoring UIs such as task-queue dashboards are not part of the supported Scheduler product surface.

## 6. Consequences

### Positive

- Minimal new distributed-system surface: PostgreSQL and Kafka are already adopted
- Process loss does not lose authoritative schedule state
- Multiple replicas can process independent due work without one correctness leader
- Occurrence creation and publication intent are atomic
- Kafka provides durable decoupling, consumer groups, replay, and enterprise schema governance
- Consumer code remains outside Scheduler
- The recurrence calculator, due-claim implementation, and future timing kernel remain replaceable behind the contract
- Custom operations UX remains stable if the internal kernel changes

### Negative

- Relational due scanning/claiming has practical scale limits and requires disciplined indexing, partitioning, vacuum management, and capacity tests
- At-least-once Kafka dispatch requires consumer idempotency
- Polling introduces a finite dispatch-latency floor determined by claim cadence
- PostgreSQL load must be observed separately from Product databases because scheduling cardinality can grow independently

### Operational

- Capacity gates measure active Schedule cardinality, due rate, claim latency, outbox age, dispatch lateness, partition skew, and Tenant/app fairness
- Time-zone database and recurrence-library upgrades require deterministic regression tests before deployment
- If measured cardinality or precision exceeds the relational timing profile, a replacement timing kernel may be introduced behind the existing PAD/API/event contracts

## 7. Compliance Impact

### Related Standards

- PAD-PLT-011 Enterprise Scheduling Platform
- ADR-GLB-003 Transactional Outbox and Kafka Protocol
- ADR-GLB-004 Declarative Schema Lifecycle
- STD-GLB-002 Database Standard
- STD-GLB-003 Observability Standard
- STD-GLB-004 Event-Driven Architecture & Messaging Standard
- STD-GLB-005 Resilience Standard
- STD-GLB-010 Durable Scheduled Work Standard

### Compliance Status

Compliant with the adopted enterprise technology portfolio and global scheduling boundary.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — In-Memory Cron as Scheduler Authority

**Rejected.** Appropriate as a recurrence calculator or local timer, but it lacks durable multi-replica ownership, Tenant isolation, occurrence history, and restart recovery.

### Alternative B — Asynq + Redis

**Rejected for the core Scheduler.** Asynq is a capable Go task queue, but it combines worker/task execution with scheduling and adds Redis as another distributed operational dependency. The Scnehaux boundary requires time and dispatch without centralizing Product worker execution.

### Alternative C — BullMQ + Redis

**Rejected.** It introduces a Node/Redis task execution stack, has a broader queue/worker scope than required, and adds another operational substrate beside the adopted Kafka protocol.

### Alternative D — RabbitMQ

**Rejected for initial dispatch.** RabbitMQ is strong for work queues, but a second enterprise broker is not justified while Kafka satisfies durable asynchronous dispatch, consumer groups, replay, and schema governance requirements.

### Alternative E — Temporal

**Rejected for this capability.** Temporal is a durable workflow/execution engine whose scope overlaps the Workflow domain and worker execution. Scheduling alone does not justify adopting the larger runtime model.

### Alternative F — Custom Distributed Timer Wheel / Consensus Scheduler

**Rejected initially.** No measured schedule cardinality, precision, or regional requirement justifies owning consensus/timer-partition machinery. The public contract preserves the option to introduce a specialized kernel later.

### Alternative G — Paid Managed Scheduling Product

**Rejected.** The enterprise requires a free/open-source-compatible core architecture and already operates the persistence and messaging primitives needed for the initial scale profile.
