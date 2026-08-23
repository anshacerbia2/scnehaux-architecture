---
doc_meta:
  id: ADR-GLB-011
  title: ADR-GLB-011 Establish Enterprise Durable Scheduling Boundary
  adr_type: foundational
  status: accepted
  created: 2026-08-22
  created_date: 2026-08-22
  created_by: Architecture Authority
  governed_by:
    - EAD-001
    - EAD-002
    - EAD-005
---

# ADR-GLB-011: Establish Enterprise Durable Scheduling Boundary

## 1. Title

Establish a shared durable temporal scheduling boundary without centralizing business worker execution.

## 2. Status

| Date | Status | ADR Type | Reviewers | Approver |
| :-- | :-- | :-- | :-- | :-- |
| 2026-08-22 | accepted | foundational | Architecture Authority, Platform Engineering, Notification, Workflow, Product Engineering | Architecture Authority |
| 2026-08-23 | accepted | foundational | Architecture Authority, Notification, Scheduling, Product Engineering | Architecture Authority |

## 3. Context

Scnehaux is moving from isolated application automation toward reusable capabilities consumed by more than ten applications. Two concrete migration candidates already duplicate scheduling and notification machinery: the client-owned Mailcast solution and ATI PH. Additional consumers are expected across workflow, HCM, finance operations, travel operations, SLA/escalation, reconciliation, reporting, expiry processing, and reminders.

The estate currently risks conflating four different responsibilities:

1. **Temporal scheduling** — durably remembering that a registered occurrence must become due at a future instant
2. **Trigger dispatch** — durably handing a due occurrence to a registered consumer contract
3. **Workflow orchestration** — preserving the state and meaning of a multi-step process
4. **Business execution** — running Product or Platform logic that owns business rules, revalidation, side effects, and outcomes

Duplicating durable scheduling inside each Product multiplies time-zone, daylight-saving-time, restart, misfire, concurrency, replay, quota, and observability logic. Centralizing arbitrary Product workers inside a shared scheduler creates the opposite failure: a distributed monolith whose security dependencies, release lifecycle, scaling characteristics, and business failure semantics are coupled to one runtime.

Notification adds another boundary risk. Communication delivery requires future timing in some journeys, but SMTP, messaging-provider configuration, templates, recipient policy, and provider delivery state are communication concerns rather than scheduling concerns.

## 4. Decision Drivers

- More than ten expected independent application consumers
- Existing duplicate scheduling and notification machinery in Mailcast and ATI PH
- One enterprise definition for durable occurrence identity, time-zone handling, misfire, replay, cancellation, and duplicate safety
- Product ownership of business meaning and irreversible outcome must remain intact
- Workflow must remain authoritative for process state and transition semantics
- Notification must remain authoritative for communication delivery and provider behavior
- Multi-tenant isolation, quota, fairness, audit, and operational ownership are required from the first shared implementation
- Existing enterprise PostgreSQL and Kafka decisions already provide durable state and asynchronous delivery primitives
- The enterprise must not add another queue/broker substrate without a requirement the adopted Kafka protocol cannot satisfy
- The public scheduling contract must outlive any replaceable timer or recurrence implementation

## 5. Decision

Scnehaux SHALL establish **Enterprise Scheduling** as a shared Platform capability responsible for durable temporal registration, occurrence materialization, misfire handling, and trigger dispatch.

### 5.1 Authority Split

The following authority boundaries are binding:

| Concern | Authority |
| :-- | :-- |
| Business timing meaning, eligibility, business state, worker code, business retry, irreversible outcome | Owning Product or Platform consumer |
| Durable schedule registration, canonical due time, occurrence identity, misfire state, trigger-dispatch state | Scheduling Platform |
| Long-running process state, task transition, workflow timeout meaning, compensation, human-task coordination | Workflow Platform |
| Notification intent after acceptance, template/channel realization, sender/provider routing, communication retry, delivery status | Notification Platform |
| Keys, credentials, certificates, provider secrets | Trust / Secret Services |

A Worker is an execution topology, not an authority. A Product worker remains part of the Product system unless a separate chartered capability owns the work the worker performs.

### 5.2 Scheduler Does Not Execute Product Code

The Scheduling Platform MUST NOT host arbitrary Product code, scripts, container images, dynamic functions, or Product-specific handlers. A due occurrence is delivered to a registered contract. The consumer that owns that contract performs the work under its own deployment, authorization, dependencies, retry policy, and business-state authority.

Scheduler dispatch success means that the governed asynchronous delivery boundary durably accepted the occurrence. It does not mean the consumer's business operation succeeded.

### 5.3 Scheduled Communication

Scnehaux supports three explicit compositions. They freeze state at different authority boundaries.

#### Mode A — Frozen Notification (default for pure scheduled communication)

```text
Product -> Notification -> Scheduling -> Notification Delivery Worker -> Provider
```

Use when the Product is already authorizing **this communication** and recipient/content/template-version semantics should be preserved from creation time. Notification creates the accepted Notification and freezes the bounded snapshot before registering a future wake-up.

**Efficiency:** one additional upfront call, but smallest Scheduler payload, earliest validation, immediate Notification status/cancel/audit identity, and stable recipient/content/version semantics.

#### Mode B — Deferred Notification Command

```text
Product -> Scheduling -> Notification -> Notification Delivery Worker -> Provider
```

Use only when no Notification must exist before due time and a **bounded registered Notification command** is sufficient. Scheduler may retain identifiers or immutable trigger input, but not provider credentials, SMTP/API secrets, provider configuration, arbitrary communication content, or unbounded recipient/contact datasets.

At due time Notification creates the Notification and resolves the applicable **Application Notification Profile** and provider binding.

**Efficiency:** fewer upfront calls and due-time Notification configuration can remain current, but validation is delayed and Scheduler is more coupled to the Notification target contract. If the deferred command cannot remain bounded and non-secret, Mode A is required.

#### Mode C — Revalidated Business Action

```text
Product -> Scheduling -> Product/Platform Worker -> authoritative revalidation -> Notification -> Provider
```

Use when business eligibility, booking state, recipient selection, content, entitlement, or another authoritative Product fact may change before due time.

**Efficiency:** most hops, but preserves current-state correctness and Product authority and avoids stale business decisions.

#### Selection Rule

| Question | Select |
| :-- | :-- |
| Communication final now and snapshot/version must be preserved? | Mode A |
| Small deferred command is sufficient and due-time Notification config should resolve then? | Mode B |
| Business eligibility/recipient/content can change before due time? | Mode C |

Provider credentials are never carried by Product or Scheduling in any mode. Notification resolves provider/channel configuration and secret references; Trust/Secret Services retain credential custody.
### 5.4 Workflow Timers

Workflow owns the semantic meaning of timeout, deadline, escalation, and process timer state. Workflow MAY use Scheduling as the generic durable wake-up mechanism. Scheduling does not inspect workflow state or decide which transition follows a due occurrence.

### 5.5 Local Timing Mechanics

Request deadlines, short retry backoff, connector polling loops, in-process debounce/throttle, and other transient timing mechanics remain local by default. They MUST NOT become enterprise schedules solely because they use time.

### 5.6 Enterprise Messaging

Due occurrences are published through the enterprise Kafka protocol using the existing transactional-outbox and event-contract standards. The Scheduling Platform does not introduce Redis, RabbitMQ, BullMQ, Asynq, or another broker as an enterprise dependency merely to deliver scheduled work.

This decision does not prohibit a future internal implementation change. It protects the Scheduling contract so a later timer kernel, partitioning model, or managed primitive can replace the initial realization without changing consumers.

### 5.7 Enterprise Capability Placement

Durable temporal scheduling and trigger dispatch belong to **Engineering & Runtime** because they are reusable execution substrate and do not own business meaning. This capability is distinct from Workflow, Notification, SLA semantics, and Product business execution.

## 6. Consequences

### Positive

- One enterprise temporal contract serves many Products and Platforms
- Time-zone, DST, misfire, cancellation, replay, and duplicate semantics become consistent
- Product workers remain independently deployable, independently scalable, and independently recoverable
- Notification and Workflow retain narrow domain authority
- A Scheduler outage delays triggers without taking ownership of Product business truth
- Multi-tenant quotas, fairness, and observability can be operated once rather than rebuilt per Product
- Existing PostgreSQL and Kafka investments are reused instead of adding another distributed substrate
- The internal timing implementation remains replaceable behind a stable Scnehaux contract

### Negative

- Products using enterprise durable scheduling gain a shared asynchronous dependency
- Consumers must implement occurrence-level idempotency
- Schedule lifecycle and Product business policy can drift and therefore require reconciliation
- Teams must distinguish local transient timers from enterprise durable schedules instead of treating every timed action identically

### Operational

- Scheduling requires its own SLO, on-call ownership, capacity model, quota model, dashboards, reconciliation, and recovery runbooks
- Consumer teams monitor business execution separately from Scheduler dispatch health
- Notification and Workflow must remove duplicate generic temporal authority as they adopt Scheduling
- Migration from legacy per-application schedulers must preserve the original business owner and explicit Tenant/Application mapping

## 7. Compliance Impact

### Related Standards

- EAD-001 Enterprise Capability & Domain Map
- EAD-002 Enterprise System Landscape
- EAD-003 Enterprise Data Ownership & Topology
- EAD-004 Enterprise Integration Architecture
- EAD-005 Enterprise Platform Architecture
- EAD-006 Enterprise Security Architecture
- ADR-GLB-003 Transactional Outbox and Kafka Protocol
- STD-GLB-002 Database Standard
- STD-GLB-003 Observability Standard
- STD-GLB-004 Event-Driven Architecture & Messaging Standard
- STD-GLB-005 Resilience Standard
- STD-GLB-010 Durable Scheduled Work Standard

### Compliance Status

Compliant. This decision creates the enterprise authority needed to remove overlapping generic scheduling responsibility from Notification and Workflow while preserving Product business authority.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Keep Scheduling Inside Every Product

**Rejected.** With more than ten consumers, independently implementing recurrence, time zones, DST, misfire, high availability, duplicate protection, replay, and operational tooling creates correctness divergence and repeated engineering cost.

### Alternative B — Put All Scheduling Inside Workflow Platform

**Rejected.** Many durable schedules are not workflows. A report trigger, reconciliation wake-up, one-time Product command, or frozen notification delivery should not require a workflow instance. Workflow retains process-timer semantics and may delegate wake-up mechanics.

### Alternative C — Put All Scheduling Inside Notification Platform

**Rejected.** Scheduling is also required for non-communication work, and Notification must not become the authority for Product business timing.

### Alternative D — Central Worker Platform Executes Every Scheduled Job

**Rejected.** Product code, dependencies, credentials, scaling profiles, releases, and business failure semantics would be pulled into one shared runtime. That creates a distributed monolith and violates Product ownership.

### Alternative E — Standardize on Asynq or BullMQ as the Platform

**Rejected.** Both combine task-queue/worker execution concerns with scheduling and introduce an additional Redis-based substrate. Scnehaux already owns PostgreSQL durability and Kafka delivery. Their operational user interfaces are also not part of the Scnehaux experience contract.

### Alternative F — Add RabbitMQ for Scheduled Worker Dispatch

**Rejected for the initial architecture.** RabbitMQ is a mature work-queue technology, but operating it beside the already adopted Kafka protocol adds a second messaging control surface, security model, disaster-recovery path, and observability stack without a current requirement that justifies the additional distributed system.

### Alternative G — Use In-Memory Cron as the Durable Authority

**Rejected.** In-memory cron libraries are valid recurrence calculators and local process timers but do not provide durable multi-replica ownership, Tenant isolation, occurrence history, or recovery semantics required by the shared capability.

### Alternative H — Use Infrastructure CronJobs as the Application Contract

**Rejected.** Deployment-scheduler objects are infrastructure topology, not a multi-tenant application scheduling contract. They remain valid for infrastructure-local jobs whose business durability and Product-facing lifecycle do not require the shared capability.
