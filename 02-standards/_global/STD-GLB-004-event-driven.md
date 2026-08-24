---
doc_meta:
  id: STD-GLB-004
  title: Enterprise Event-Driven Architecture & Messaging Standard
  owner: Enterprise Architect
  version: 3.0.0
  status: approved
  classification: public
  governed_by:
    - EAD-004
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-24
---

# Enterprise Event-Driven Architecture & Messaging Standard (STD-GLB-004)

## 1. Objective & Scope

This standard defines mandatory semantics for asynchronous communication across Scnehaux, including source publication correctness, delivery-profile selection, message identity, schema compatibility, duplicate safety, acknowledgement, retry, failure parking, ordering, replay, security, and observability.

It applies to:

- brokerless durable asynchronous point-to-point delivery
- queue-oriented messaging
- publish/subscribe messaging
- retained event streaming
- asynchronous commands and durable triggers
- domain/lifecycle event publication
- consumer Workers receiving work from these delivery boundaries

This standard does **not** make a broker a business authority and does **not** require every asynchronous interaction to use Kafka, RabbitMQ, or any broker.

## 2. Design Principles

- **Outbox solves source atomicity** — it protects the gap between a local authoritative transaction and external publication
- **Delivery substrate solves transport durability** — direct, queue, and stream profiles provide different capabilities
- **Worker solves execution** — consumer business processing is separate from broker/relay transport
- **Broker acknowledgement is not business completion**
- **At-least-once plus idempotent effect is the default correctness model**
- **Ordering and replay are explicit contract requirements, never assumptions**
- **One message contract has one primary delivery path per environment**
- **Technology follows semantics** — point-to-point, queue, and stream needs are classified before selecting a product
- **Schema governance is independent of broker product**
- **Authority remains with the natural Product/Platform owner**

## 3. Normative Rules

### 3.1 Message Classification

Every production asynchronous contract **MUST** classify the message as one of:

- **Domain/Lifecycle Event** — an accepted fact that may have independent consumers
- **Asynchronous Command** — a bounded request for one owning consumer to perform work
- **Durable Trigger** — a stable trigger such as `OccurrenceDue` that activates a registered consumer contract
- **Technical Job Message** — bounded technical work owned by one Product/Platform

The class determines ownership and expected delivery semantics. Transport does not change the message's authority.

### 3.2 Delivery-Profile Selection

A contract **MUST** select the minimum profile that satisfies its required semantics.

| Profile | Select when | Do not select merely because |
| :-- | :-- | :-- |
| **Direct Durable Delivery** | bounded point-to-point delivery, stable target, no broker replay/routing/competing-consumer requirement | communication is asynchronous |
| **Queue-Oriented Messaging** | targeted commands/jobs/triggers, competing consumers, routing, ACK/NACK, backpressure, DLQ | the system has many services |
| **Stream-Oriented Messaging** | retained replay, independent consumer groups, CDC, stream processing, per-key log ordering | Kafka is already known or considered enterprise-grade |

The architecture **MUST NOT** use a higher-complexity profile without a concrete semantic, reliability, scale, or operational driver.

### 3.3 Transactional Outbox Applicability

A Transactional Outbox is **REQUIRED** when:

- a local authoritative state mutation occurs
- an external asynchronous message must logically exist if and only if that mutation commits
- no equivalent atomic mechanism is proven

The authoritative state mutation and publication intent **MUST** commit in the same local transactional resource and transaction boundary.

A centralized Outbox database/service **MUST NOT** be called synchronously inside the source commit path.

A consumer-only component or a flow with no coordinated local mutation **MUST NOT** add an outbox merely for uniformity.

### 3.4 Outbox Record and Relay

The source-local outbox **MUST** carry at minimum:

- stable message/event ID
- message/event type
- version/schema identity
- payload or safe payload reference
- ownership/correlation context required by the contract
- creation timestamp
- publication state

The Outbox Relay:

- **MUST** publish only committed rows
- **MUST** use bounded batching and retry
- **MUST** mark publication accepted only after the selected profile's durability point
- **MUST NOT** treat transport acceptance as consumer business completion
- **MUST** expose oldest-unpublished age, attempt/failure state, and throughput telemetry

Polling/claiming and CDC are both valid relay mechanisms. The choice is operational and may evolve independently of the domain contract.

### 3.5 Direct Durable Delivery Profile

The source relay calls a governed target acceptance API.

The source **MUST** send a stable idempotency/message identity across retries.

The target acceptance boundary **MUST**:

- authenticate and authorize the source
- validate declared Tenant/application/contract scope
- deduplicate the stable message identity
- persist an Inbox/Operation record or atomically apply the accepted mutation before success
- return success only after its declared durability point
- expose reconciliation/query behavior for ambiguous outcomes where duplicates are harmful

The source retries transient network/availability failures with bounded exponential backoff and jitter.

A transport timeout is **ambiguous**, not proof that the target rejected the message.

A pure Worker **MUST NOT** be exposed as an arbitrary public HTTP target. Direct delivery uses the owning application's controlled acceptance boundary under ADR-GLB-014.

### 3.6 Queue-Oriented Messaging Profile

RabbitMQ is the adopted reference implementation.

Production queue contracts **MUST** define:

- exchange/routing ownership
- durable queue ownership
- persistent-message posture
- publisher-confirm durability point
- consumer acknowledgement point
- retry/redelivery ceiling
- DLQ/parking behavior
- queue depth/age capacity thresholds
- ordering requirement if any

For C1 paths, queue durability **MUST** survive one declared node/failure-domain loss. Quorum/replicated queues or an equivalent proven mechanism are required.

A consumer **MUST NOT** ACK before its declared local durability/idempotency point.

Queue acknowledgement normally removes delivery backlog state. Long-term arbitrary replay **MUST NOT** be assumed unless the selected queue implementation/profile explicitly supplies and governs retained-stream semantics.

### 3.7 Stream-Oriented Messaging Profile

Kafka protocol is the adopted reference implementation.

Production stream contracts **MUST** define:

- topic ownership
- partition key
- replication/durability policy
- producer acknowledgement point
- consumer-group ownership
- offset/commit policy
- retention/replay window
- schema compatibility mode
- partition/consumer capacity model

For C1 paths, producer acknowledgement **MUST** prove the configured replicated durability contract before the source outbox row is marked published.

Ordering is **per partition/key**, never global unless a deliberately single-partition contract accepts the capacity trade-off.

Offset advancement is transport progress, not business completion.

### 3.8 Event Envelope and Contract Identity

Domain and lifecycle events **MUST** use CloudEvents 1.0 JSON.

Required fields:

- `specversion`
- `type`
- `source`
- `id`
- `time`
- `datacontenttype`
- `data`

When ordered projection/bootstrap is supported, the event adds `streamposition` as a monotonic publisher-stream position. `streamposition` is not a broker offset and not an entity identifier.

Asynchronous commands/triggers **MUST** define:

- stable message/command identity
- command/trigger type and major version
- producer/source identity
- target contract
- correlation and causation where applicable
- Tenant/application ownership context where applicable
- idempotency semantics
- bounded payload schema
- expiry/deadline only when meaningful to the contract

### 3.9 Consumer Idempotency and Inbox

Consumers **MUST** implement duplicate safety using one of:

- a unique processed-message/event record
- an Inbox/Operation table
- an atomic versioned state transition
- an equivalent proven idempotent effect

For a local state mutation, deduplication and the authoritative consumer mutation **SHOULD** commit atomically.

For an external side effect that cannot share the consumer transaction, the consumer **SHOULD** atomically persist a local operation plus deduplication state, acknowledge according to the selected profile, then execute the external effect through an idempotent retry Worker.

Exactly-once distributed side effects are not assumed.

### 3.10 Retry, Failure Parking, and Reconciliation

Producer outbox retry covers **publication to the delivery boundary only**.

Consumer processing retry is separately owned by the consumer.

Transient failures use bounded exponential backoff with jitter.

Permanent validation/authentication failures are not blindly retried.

After bounded retries, unresolved work **MUST** enter an inspectable durable failure state:

- Direct profile — source delivery backlog/reconciliation state or target accepted-operation failure state
- Queue profile — DLQ or equivalent parked queue/state
- Stream profile — parking/retry topic or durable failed-operation store

DLQ/parking is not disposal. Critical unresolved operations remain alerted until replay, correction, or reconciliation establishes final state.

### 3.11 Ordering, Concurrency, and Version Safety

No asynchronous contract receives global ordering by default.

- Direct profile has no ordering guarantee beyond an explicitly implemented contract
- Queue profile ordering depends on queue topology, redelivery, and consumer concurrency
- Stream profile ordering is per partition key

When messages grant/revoke authority or update a versioned aggregate, consumers **MUST** carry/compare the authority or aggregate version needed to prevent an older delivery from overwriting a newer accepted state.

Arrival order alone is never authorization.

### 3.12 Replay and Snapshot Bootstrap

Replay is a contract capability, not an automatic property of all messaging.

If a projection requires snapshot plus incremental events, it **MUST** have an atomic/equivalent handoff using a high-water mark or declared stream position.

Stream profile consumers may replay retained records by offset/position within the retention contract.

Queue/direct profiles requiring historical reconstruction **MUST** use an authoritative event/history store, snapshot, or equivalent source rather than pretending acknowledged queue messages remain replayable.

### 3.13 Schema Evolution

All cross-system message schemas are versioned.

Default evolution is backward compatible:

- additive optional fields are allowed
- field type mutation is prohibited
- field removal requires deprecation and consumer migration
- breaking change requires a new major message/event type

Every production contract is registered in the enterprise schema-contract registry/catalog and validated in CI.

The registry/catalog implementation is broker-neutral.

### 3.14 Security and Data Handling

Every delivery profile **MUST** provide:

- authenticated workload identity
- transport encryption
- least-privilege publish/consume/accept permissions
- Tenant/application scope validation where applicable
- payload classification and minimization
- no credentials/secrets in ordinary message payloads
- audit/evidence for privileged replay or cross-Tenant operations
- safe error/telemetry redaction

Broker management/admin interfaces are never Product business APIs.

### 3.15 Observability

Common metrics:

- publication rate/error
- source outbox oldest age
- delivery latency
- duplicate/dedup count
- retry count
- parked/DLQ/reconciliation backlog
- payload size distribution
- per-Tenant/application pressure where applicable

Profile-specific metrics:

**Direct**

- target acceptance latency/error
- ambiguous timeout count
- retry backlog age

**Queue**

- ready depth
- unacknowledged count
- oldest message age
- publisher confirm latency
- redelivery rate
- DLQ depth

**Stream**

- producer acknowledgement latency
- consumer lag
- partition skew
- replay age
- retention/storage pressure
- failed/parked offset count

Alerts **MUST** have an owner and runbook action.

### 3.16 Capacity and Backpressure

Every production contract declares:

- expected sustained and peak message rate
- payload-size bound
- retention/backlog bound
- consumer concurrency
- per-Tenant/application quota where shared
- overload/load-shedding behavior

Unbounded queue, stream retention, retry, or direct-delivery backlog is prohibited.

### 3.17 Deployment and Technology Selection

Scnehaux adopted implementations:

| Semantic profile | Adopted implementation |
| :-- | :-- |
| Queue-Oriented Messaging | RabbitMQ |
| Stream-Oriented Messaging | Kafka protocol |
| Direct Durable Delivery | governed HTTPS + source outbox/relay + target durable acceptance |

`adopted` is profile-scoped. A deployment does not run both brokers solely because both are supported.

One logical message contract has one primary delivery substrate per environment.

Multiple substrates in one environment are allowed only for distinct contracts with different semantic requirements or a governed migration/bridge.

## 4. Exceptions

Deviation from source-local publication atomicity, consumer duplicate safety, or declared delivery durability requires formal architecture review and an approved exception ADR.

A technology substitution inside the same semantic profile does not require redefining Product authority, but it must prove equivalent delivery, security, observability, and recovery properties and comply with Technology Radar governance.

## 5. Enforcement Mechanism

CI/architecture review verifies:

1. every asynchronous cross-system contract declares message class and delivery profile
2. transactional publishers use a source-local outbox or prove equivalent atomicity
3. no source commit path writes to a central Outbox authority
4. direct targets prove idempotent durable acceptance and are not arbitrary Worker URLs
5. queue contracts declare publisher confirm, ACK, retry, DLQ, durability, and queue-age metrics
6. stream contracts declare partition key, producer acknowledgement, consumer group, retention, replay, and lag metrics
7. consumers prove duplicate safety
8. event schemas pass compatibility validation in the enterprise schema-contract registry/catalog
9. one contract does not blindly dual-publish to RabbitMQ and Kafka
10. profile-specific fault tests cover broker/target outage, duplicate delivery, ambiguous acknowledgement, restart, and recovery
