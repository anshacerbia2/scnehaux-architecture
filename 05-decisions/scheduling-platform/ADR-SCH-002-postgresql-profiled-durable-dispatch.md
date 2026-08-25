---
doc_meta:
  id: ADR-SCH-002
  title: ADR-SCH-002 PostgreSQL Temporal Authority and Replaceable Durable Dispatch
  adr_type: replacement
  status: accepted
  created: 2026-08-24
  created_date: 2026-08-24
  created_by: Scheduling Platform Team
  governed_by:
    - PAD-PLT-011
---

# ADR-SCH-002: PostgreSQL Temporal Authority and Replaceable Durable Dispatch

## 1. Title

Use PostgreSQL as Scheduling temporal authority and dispatch due Occurrences through one selected durable-delivery adapter per deployment profile.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                                                                       | Approver               |
| :--------- | :------- | :---------- | :------------------------------------------------------------------------------ | :--------------------- |
| 2026-08-24 | accepted | replacement | Scheduling Platform, Platform Engineering, Architecture Authority, Notification | Architecture Authority |

This ADR supersedes **ADR-SCH-001**.

## 3. Context

The Scheduling Runtime requires durable multi-replica Schedule/Occurrence state and at-least-once dispatch without executing consumer business code.

ADR-SCH-001 correctly selected PostgreSQL as temporal authority but bound dispatch to Kafka because Kafka was then the universal enterprise broker decision. ADR-GLB-016 now separates source publication correctness from delivery-substrate selection and ADR-GLB-017 makes Scheduling dispatch profile-based.

Scheduling must therefore preserve one logical dispatch port while allowing the concrete environment to select:

- direct durable target acceptance
- RabbitMQ queue delivery
- Kafka stream delivery

The default Scnehaux deployment should minimize operational footprint while still exercising a production-grade broker, so RabbitMQ is the baseline Scheduling dispatch substrate.

## 4. Decision Drivers

- PostgreSQL durability and transactional row coordination
- one stable Occurrence identity per logical due instant
- atomic occurrence materialization, Schedule advance, and publication intent
- no network call inside the due-state transaction
- default on-premises-friendly deployment footprint
- queue semantics for targeted due-trigger delivery
- optional retained-stream semantics for Kafka learning/stream workloads
- replaceable delivery adapter
- no arbitrary target URL or Product code inside Scheduler
- at-least-once transport plus idempotent consumer effect
- explicit failure/reconciliation semantics for every profile

## 5. Decision

### 5.1 Temporal Authority

PostgreSQL remains the authoritative durable store for:

- Schedule lifecycle
- next-fire temporal state
- Occurrence identity/state
- command idempotency
- target ownership projection
- quota/admission state
- replay/reconciliation metadata
- local transactional outbox

Correctness-critical state is never held exclusively in process memory.

### 5.2 Atomic Due-State Transaction

Materializing a due Occurrence atomically:

1. establishes the stable logical Occurrence
2. advances/finalizes Schedule temporal state
3. writes the transport-neutral publication intent to the local outbox

No external network call occurs while this transaction is held.

### 5.3 Dispatch Port

Application code publishes through a transport-neutral `OccurrenceDispatchPort`.

Conceptually:

```text
Occurrence Materializer
        ↓
local outbox
        ↓
Outbox Relay
        ↓
OccurrenceDispatchPort
        ↓
selected adapter
```

Broker/API-specific types remain in adapters and never enter Scheduling domain packages.

### 5.4 Deployment Profiles

#### Default — Queue / RabbitMQ

The default Scnehaux deployment uses RabbitMQ.

Production C1 posture requires:

- durable exchange/queue topology
- persistent messages
- quorum/replicated queue durability appropriate to the failure domain
- publisher confirms before the outbox row is marked published
- explicit consumer acknowledgement
- DLQ/parking for poison/unresolved delivery
- routing from registered target contract, not caller-provided endpoint

`OccurrenceDue` is routed to the queue owned by the registered consumer contract.

#### Stream — Kafka

The stream profile uses Kafka when retained-log semantics are required.

Production C1 posture requires:

- replicated topic
- producer acknowledgement satisfying the declared replication policy
- explicit partition key
- consumer-group/offset state
- retention/replay policy
- schema compatibility
- consumer idempotency on `occurrence_id`

Kafka offset advancement is not Product business completion.

#### Minimal — Direct Durable Delivery

The minimal profile is allowed for lab, local, or bounded point-to-point deployments where broker capabilities are not required.

The relay calls a **registered durable-acceptance API**, never an arbitrary Schedule payload URL.

The target must persist/deduplicate the `occurrence_id` before returning success.

Target Worker execution can occur asynchronously after acceptance and remains outside Scheduling.

### 5.5 One Active Primary Adapter

For one `OccurrenceDue` contract in one environment, exactly one primary dispatch adapter is active.

Startup/config validation must fail when mutually exclusive primary adapters are simultaneously enabled for the same contract, except an explicitly governed migration/bridge.

### 5.6 Dispatch Durability

Scheduling marks outbox publication accepted only after:

| Profile  | Durability point                                                                            |
| :------- | :------------------------------------------------------------------------------------------ |
| Direct   | target durable-acceptance API confirms persisted/idempotent acceptance                      |
| RabbitMQ | broker publisher confirm proves acceptance into the configured durable route/queue contract |
| Kafka    | producer acknowledgement proves acceptance under the configured replication contract        |

This state means Scheduler dispatch durability only.

### 5.7 Recurrence Calculation

A proven free/open-source recurrence library may be used as a pure calculator.

Process timers, goroutine registries, or library-owned in-memory schedules are never temporal authority.

Time-zone/DST behavior remains compatibility-tested through a golden corpus.

### 5.8 Runtime Shape

The initial runtime remains one horizontally replicated Go deployable containing bounded modules for API, temporal calculation, due claiming, occurrence materialization, outbox relay, dispatch adapters, target projection, quota/admission, and operations/reconciliation.

Adapter or Worker extraction requires measured scale, independent security/fault-containment, or operational evidence and a separate SAD.

## 6. Consequences

### Positive

- PostgreSQL temporal correctness remains unchanged
- default deployment can use RabbitMQ without Kafka nodes
- Kafka remains a first-class stream profile
- direct profile enables minimal learning/local deployment
- domain code is isolated from broker APIs
- source outbox survives all delivery-substrate outages
- transport replacement does not change `schedule_id` or `occurrence_id`
- consumer Worker execution remains outside Scheduler

### Negative

- three supported profiles require contract/fault tests
- queue and stream observability differ
- profile migration needs duplicate/reconciliation protection
- the default RabbitMQ profile does not provide Kafka-style retained arbitrary replay

### Operational

- baseline deployment certifies PostgreSQL plus RabbitMQ
- stream deployment certifies PostgreSQL plus Kafka
- minimal direct deployment certifies source retry plus target durable acceptance
- profile-specific dashboards are mandatory
- only one primary adapter per Occurrence contract is enabled in normal operation

## 7. Compliance Impact

### Related Standards

- PAD-PLT-011 Enterprise Scheduling Platform
- ADR-GLB-016 Transactional Publication and Durable Messaging Profiles
- ADR-GLB-017 Enterprise Durable Scheduling Boundary with Profiled Dispatch
- ADR-GLB-014 Background Worker Network Boundary
- STD-GLB-002 Database Standard
- STD-GLB-003 Observability Standard
- STD-GLB-004 Event-Driven Architecture & Messaging Standard
- STD-GLB-005 Resilience Standard
- STD-GLB-010 Durable Scheduled Work Standard

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Kafka-Only Dispatch

Rejected as the universal Scheduling implementation because the default target-trigger workload benefits from queue semantics and does not require retained-log infrastructure in every deployment.

### Alternative B — RabbitMQ-Only Architecture Contract

Rejected because it would repeat the same product coupling in the opposite direction and remove a valuable stream profile.

### Alternative C — Direct HTTP Only

Rejected as the general enterprise profile because many targets, independent consumers, broker backpressure, and queue/stream operations justify a messaging substrate at shared-platform scale.

### Alternative D — RabbitMQ and Kafka Dual Publish

Rejected because two transport acknowledgements create ambiguous partial success and duplicate/reconciliation complexity.

### Alternative E — Redis Task Framework

Rejected for the core Scheduler because it combines task execution/scheduling concerns and adds another persistence substrate while PostgreSQL remains the temporal authority.

### Alternative F — Custom Distributed Timer Consensus Kernel

Rejected until measured cardinality/precision/regional evidence exceeds the relational timing profile.
