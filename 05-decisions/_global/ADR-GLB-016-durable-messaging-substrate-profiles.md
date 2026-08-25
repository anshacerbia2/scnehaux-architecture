---
doc_meta:
  id: ADR-GLB-016
  title: ADR-GLB-016 Separate Transactional Publication from Durable Messaging Substrate Selection
  adr_type: replacement
  status: accepted
  created: 2026-08-24
  created_date: 2026-08-24
  created_by: Architecture Authority
  governed_by:
    - EAD-004
    - EAD-005
---

# ADR-GLB-016: Separate Transactional Publication from Durable Messaging Substrate Selection

## 1. Title

Separate source-transaction publication correctness from durable delivery-substrate selection and standardize profile-based asynchronous delivery.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                                                                                   | Approver               |
| :--------- | :------- | :---------- | :------------------------------------------------------------------------------------------ | :--------------------- |
| 2026-08-24 | accepted | replacement | Architecture Authority, Platform Engineering, Product Engineering, Scheduling, Notification | Architecture Authority |

This ADR supersedes **ADR-GLB-003** in full. The source-local Transactional Outbox invariant is retained. The former universal Kafka product mandate is replaced by profile-based delivery selection.

## 3. Context

ADR-GLB-003 correctly established the Transactional Outbox pattern, but later revisions coupled that consistency pattern to one enterprise broker product. The two decisions solve different failure windows:

```text
Source transaction
├─ authoritative mutation
└─ local outbox publication intent
        ↓
Outbox Relay
        ↓
delivery substrate
        ↓
consumer acceptance / consumer worker
```

The local outbox protects the boundary **before external delivery succeeds**. A broker or target endpoint protects delivery **after the source transaction commits**. Kafka, RabbitMQ, and brokerless idempotent HTTP solve different delivery problems and should not redefine source-transaction correctness.

Scnehaux also needs to serve two goals simultaneously:

- production deployments should not carry distributed infrastructure that their workload does not justify
- the architecture should remain a complete learning/reference architecture that exercises queue-oriented and stream-oriented messaging without coupling domain authority to either

A universal broker mandate creates avoidable operational cost and makes the chosen product appear to be architecture. Supporting every broker simultaneously creates the opposite problem: needless code, deployment, security, disaster-recovery, and observability surface.

## 4. Decision Drivers

- preserve atomic source-state plus publication-intent correctness
- keep outbox ownership local to the authoritative transaction
- distinguish Outbox Relay from business Worker execution
- choose delivery semantics from the communication contract rather than technology prestige
- support bounded point-to-point delivery without requiring a broker
- support queue semantics for commands, jobs, routing, acknowledgements, and competing consumers
- support retained-log semantics for replayable facts, independent consumer groups, CDC, and stream processing
- avoid dual-broker deployment unless separate contracts or migration evidence justify it
- preserve replaceable adapters and stable domain contracts
- keep broker durability and node replication separate from business authority

## 5. Decision

### 5.1 Transactional Publication Boundary

When a local authoritative state mutation and an external asynchronous publication must succeed or fail as one logical operation, the source **MUST** persist the publication intent in the same local transactional resource and transaction as the authoritative mutation.

```text
Source database transaction
├─ authoritative state mutation
└─ local outbox publication intent
        ↓ COMMIT
relay / CDC
        ↓
selected durable delivery profile
```

A central Outbox service/database **MUST NOT** be inserted into the source commit path.

A direct database mutation followed by a network publish without an equivalent atomic mechanism **MUST NOT** be used for correctness-critical publication.

The outbox record remains owned by the source Product/Platform even when relay libraries, CDC infrastructure, producer adapters, schema tooling, telemetry, or dashboards are shared.

### 5.2 Outbox Relay Is Not the Business Worker

The **Outbox Relay** is responsible for moving committed publication intent to the selected delivery boundary and recording transport acceptance.

The **Consumer Worker** is responsible for executing consumer-owned work after the consumer's durability/idempotency boundary.

```text
Source
  └─ Outbox
       ↓
    Relay
       ↓
Delivery boundary
       ↓
Consumer acceptance / inbox
       ↓
Business Worker
```

Transport acceptance is not business completion.

### 5.3 Durable Delivery Profiles

Scnehaux defines three standard delivery profiles.

| Profile                       | Primary fit                                                                                | Required semantic properties                                                                                            | Reference implementation                   |
| :---------------------------- | :----------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :----------------------------------------- |
| **Direct Durable Delivery**   | bounded point-to-point asynchronous relationship                                           | idempotent durable target acceptance, retry, timeout, reconciliation, source outbox when atomic publication is required | HTTPS to a governed durable-acceptance API |
| **Queue-Oriented Messaging**  | commands, jobs, targeted triggers, competing consumers, routing, backpressure              | durable queue, publisher acknowledgement, consumer ACK/NACK, DLQ/parking, bounded retry                                 | RabbitMQ                                   |
| **Stream-Oriented Messaging** | replayable domain/lifecycle facts, many independent consumers, CDC, retained event history | retained append-only log, partition/key ordering, offsets, consumer groups, replay                                      | Kafka protocol                             |

These profiles define **delivery semantics**, not business authority.

### 5.4 Direct Durable Delivery

The direct profile is valid when the relationship is bounded and no queue/stream capability is required.

The source relay calls a registered target acceptance API with a stable message/idempotency identity.

The target **MUST**:

- authenticate and authorize the source
- deduplicate the stable message identity
- durably persist the accepted command/event or atomically apply it before returning success
- return success only after its declared durability point
- expose reconciliation/query semantics when response ambiguity can occur

The target **MUST NOT** rely on an irreversible side effect completing inside the HTTP request as the only proof of acceptance.

A pure background Worker remains non-public under ADR-GLB-014. Direct delivery targets the owning application's governed acceptance boundary, not an arbitrary Worker URL.

### 5.5 Queue-Oriented Messaging

The queue profile is selected when work distribution or routing semantics dominate.

For C1 production paths the implementation **MUST** provide:

- durable topology and persistent messages
- replicated/quorum durability appropriate to the failure model
- publisher confirms before source outbox publication is marked accepted
- explicit consumer acknowledgement
- bounded redelivery
- DLQ or equivalent parked-failure state
- queue depth, unacknowledged count, age, redelivery, and DLQ observability

RabbitMQ is the adopted reference implementation for this profile.

Queue consumption does not imply long-term replay after acknowledgement. Contracts requiring retained arbitrary replay use the stream profile or an explicit authoritative event store.

### 5.6 Stream-Oriented Messaging

The stream profile is selected when retained-log semantics are required.

For C1 production paths the implementation **MUST** provide:

- replicated durable records
- producer acknowledgement that satisfies the declared replication policy
- explicit partition/key strategy
- consumer-group/offset state
- retention sufficient for the declared replay/recovery window
- schema compatibility governance
- lag, partition skew, retention, producer acknowledgement, and replay observability

Kafka protocol is the adopted reference implementation for this profile.

Consumption/offset advancement is transport state, not proof of business completion.

### 5.7 One Primary Delivery Path per Contract and Environment

One logical message contract **MUST** have one primary delivery path in one environment.

Running RabbitMQ and Kafka simultaneously is permitted only when:

- different contracts require genuinely different queue vs stream semantics
- a governed migration/bridge is in progress
- an explicit resilience design proves why both are required

Blind dual-publishing of the same logical message to two brokers is prohibited because it creates duplicate authority over delivery state and reconciliation complexity.

### 5.8 Consumer Durability and Idempotency

At-least-once delivery is the enterprise default.

Consumers **MUST** deduplicate by stable message/event identity or prove an equivalent idempotent effect.

When broker acknowledgement and local state mutation cannot be one transaction, the consumer **SHOULD** atomically persist a local Inbox/Operation record and deduplication state before acknowledging, then perform external side effects through an idempotent retry Worker.

Exactly-once distributed business execution is not an enterprise guarantee.

### 5.9 Schema Governance Is Broker-Neutral

Schema compatibility is an enterprise contract independent of RabbitMQ or Kafka.

Domain/lifecycle events continue to use the governed CloudEvents contract. Commands and triggers declare versioned schemas, stable identity, ownership context, correlation, and idempotency semantics.

A schema-registry capability may be implemented by a service or repository/build-time tooling. The existence of schema governance does not force a specific broker product.

### 5.10 Technology Lifecycle

The enterprise Technology Radar records:

- RabbitMQ as the adopted queue-broker implementation
- Kafka as the adopted event-streaming implementation

Applicability is conditional on the profile selected by STD-GLB-004. `adopted` does not mean every deployment runs both technologies.

## 6. Consequences

### Positive

- Transactional Outbox correctness no longer depends on Kafka
- point-to-point asynchronous delivery can avoid unnecessary broker infrastructure
- RabbitMQ is available where queue semantics are natural
- Kafka remains available where retained-stream semantics are justified
- systems can learn both paradigms without making both runtime dependencies
- domain and Product contracts remain stable across transport replacement
- broker cost, storage, replication, and operational complexity become explicit deployment decisions
- outbox relay, broker, consumer acceptance, and business Worker responsibilities remain distinct

### Negative

- teams must classify message semantics instead of choosing one universal transport
- Platform Engineering must maintain two adopted broker profiles even when one environment deploys only one
- cross-profile migrations require contract and reconciliation testing
- operational dashboards differ between direct, queue, and stream profiles

### Operational

- default Scnehaux deployment may run RabbitMQ only when queue/direct semantics satisfy active contracts
- Kafka is deployed when stream contracts justify retained-log capability
- each profile has separate durability, capacity, backup/recovery, security, and observability certification
- source outbox backlog remains the first indicator of publication failure regardless of selected profile

## 7. Compliance Impact

### Related Standards

- EAD-004 Enterprise Integration Architecture
- EAD-005 Enterprise Platform Architecture
- STD-GLB-003 Observability Standard
- STD-GLB-004 Event-Driven Architecture & Messaging Standard
- STD-GLB-005 Resilience Standard
- ADR-GLB-014 Background Worker Network Boundary

### Compliance Status

Compliant. This ADR replaces the broker-coupled ADR-GLB-003 while retaining its source-local Transactional Outbox safety invariant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Kafka as the Universal Enterprise Broker

Rejected because queue/work-distribution and small point-to-point relationships do not inherently require retained-log semantics, and a universal Kafka mandate couples deployment cost to unrelated contracts.

### Alternative B — RabbitMQ as the Universal Enterprise Broker

Rejected because queue semantics do not replace Kafka's retained-log, partition/offset, independent replay, CDC, and stream-processing strengths.

### Alternative C — Broker Required for Every Asynchronous Relationship

Rejected because source-local outbox plus idempotent durable HTTP acceptance can provide reliable asynchronous point-to-point delivery with substantially less infrastructure.

### Alternative D — Deploy RabbitMQ and Kafka Everywhere

Rejected because it doubles broker security, storage, monitoring, patching, capacity, backup/recovery, and operator cognitive load even when one substrate is unused.

### Alternative E — Centralized Outbox Service

Rejected because a remote outbox authority recreates the dual-write/distributed-transaction problem the Transactional Outbox pattern exists to remove.

### Alternative F — Direct Database-to-Broker Publish Without Outbox

Rejected for correctness-critical state publication because process/network failure between the local commit and broker publish can silently lose the message.
