---
doc_meta:
  id: ADR-GLB-017
  title: ADR-GLB-017 Preserve Enterprise Durable Scheduling Boundary with Profiled Dispatch
  adr_type: replacement
  status: accepted
  created: 2026-08-24
  created_date: 2026-08-24
  created_by: Architecture Authority
  governed_by:
    - EAD-001
    - EAD-004
    - EAD-005
---

# ADR-GLB-017: Preserve Enterprise Durable Scheduling Boundary with Profiled Dispatch

## 1. Title

Preserve the shared durable Scheduling authority boundary while replacing universal Kafka dispatch with profile-based durable delivery.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                                                                                             | Approver               |
| :--------- | :------- | :---------- | :---------------------------------------------------------------------------------------------------- | :--------------------- |
| 2026-08-24 | accepted | replacement | Architecture Authority, Platform Engineering, Scheduling, Notification, Workflow, Product Engineering | Architecture Authority |

This ADR supersedes **ADR-GLB-011** in full. Its Scheduling, Product, Workflow, Notification, and Worker authority boundaries are retained. Only the transport assumption is rebaselined through ADR-GLB-016.

## 3. Context

Scnehaux requires one shared definition of durable future-time registration, occurrence identity, time-zone/DST behavior, misfire, cancellation, replay, fairness, and trigger dispatch for more than ten expected consumers.

The original Scheduling boundary correctly separated temporal authority from Product Worker execution, but embedded the then-current Kafka decision into the global boundary. Subsequent analysis established that:

- Scheduling semantics do not require one broker product
- `OccurrenceDue` is a durable trigger whose transport may be direct, queue-oriented, or stream-oriented
- source-local outbox and consumer idempotency remain required independently of broker choice
- the default Scnehaux deployment can use RabbitMQ without losing Scheduling authority
- Kafka remains valuable as a stream profile when retention/replay/consumer-group semantics are required

The enterprise boundary must outlive any transport choice.

## 4. Decision Drivers

- one durable temporal authority for many Products/Platforms
- preserve Product business ownership and independent Worker deployment
- preserve Workflow process authority
- preserve Notification communication/provider authority
- stable occurrence identity and at-least-once trigger delivery
- no correctness dependency on one broker product
- avoid deploying multiple brokers without message-contract evidence
- support low-footprint, queue-oriented, and stream-oriented deployment profiles
- keep target routing governed and prevent arbitrary URL/code execution
- retain idempotent registration reconciliation and cancellation-race correctness

## 5. Decision

### 5.1 Authority Split

| Concern                                                                                                             | Authority                                                            |
| :------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------- |
| Business timing meaning, eligibility, business state, worker code, business retry, irreversible outcome             | Owning Product/Platform                                              |
| Durable Schedule lifecycle, canonical due time, Occurrence identity, misfire state, trigger-dispatch state          | Scheduling Platform                                                  |
| Durable process state, workflow timeout/deadline meaning, compensation, human/system task coordination              | Workflow Platform                                                    |
| Accepted communication intent, template/channel realization, provider routing, communication retry, delivery status | Notification Platform                                                |
| Keys, credentials, certificates, provider secrets                                                                   | Trust / Secret Services                                              |
| Durable delivery mechanics                                                                                          | Engineering & Runtime messaging substrate selected under ADR-GLB-016 |

A Worker is execution topology, not authority.

### 5.2 Scheduler Does Not Execute Product Code

Scheduling **MUST NOT** host arbitrary Product code, scripts, functions, container images, or caller-provided executable handlers.

A due Occurrence is handed to a **registered target contract**. The owning Product/Platform executes the work in its own runtime.

Dispatch success means the selected durable delivery boundary accepted the Occurrence. It never means Product business completion.

### 5.3 Stable Schedule and Occurrence Identity

Retryable Schedule creation **MUST** use a stable scoped idempotency identity.

Equivalent retries after timeout/process loss resolve to the same logical `schedule_id`. Conflicting semantic reuse is rejected.

Every logical due instant materializes one stable `occurrence_id`. Transport retries and operator replay reuse that identity.

### 5.4 Scheduled Communication

Scnehaux retains three explicit compositions.

#### Mode A — Frozen Notification

```text
Product -> Notification -> Scheduling -> Notification -> Provider
```

Use when this communication is authorized now and recipient/content/template-version semantics must remain fixed.

Notification first commits the accepted Notification, frozen communication snapshot, and local Schedule-registration intent. Schedule creation uses a stable idempotency identity and recoverable binding.

Notification terminal cancellation remains the final delivery gate. Scheduling cancellation is asynchronous cleanup and cannot retract an Occurrence already durably dispatched.

Operational provider route, current credential/secret version, endpoint, failover route, and rate-limit state remain late-bound by default unless an explicit governed contract pins configuration.

#### Mode B — Deferred Notification Command

```text
Product -> Scheduling -> Notification -> Provider
```

Use only when a bounded registered Notification command is sufficient at due time.

Scheduling does not store provider credentials, SMTP/API secrets, arbitrary communication bodies, or unbounded recipient/contact datasets.

#### Mode C — Revalidated Business Action

```text
Product -> Scheduling -> Product/Platform Worker -> revalidate -> Notification
```

Use when business eligibility, booking/subscription state, recipient, or content can change before due time.

### 5.5 Workflow Timers

Workflow owns timeout, deadline, escalation, compensation, and transition semantics.

Workflow may use Scheduling as a generic durable wake-up mechanism. Scheduling does not inspect Workflow state or decide the next process transition.

### 5.6 Local Timing Mechanics

Request deadlines, short retry backoff, connector polling, debounce/throttle, and process-local timers remain local unless they require the shared durable Schedule lifecycle.

### 5.7 Profiled Durable Trigger Dispatch

Scheduling publishes `OccurrenceDue` through the delivery semantics defined by ADR-GLB-016 and STD-GLB-004.

Supported profiles are:

| Profile                   | Scheduling use                                                              |
| :------------------------ | :-------------------------------------------------------------------------- |
| Direct Durable Delivery   | minimal/bounded topology using a registered consumer durable-acceptance API |
| Queue-Oriented Messaging  | default Scnehaux trigger-delivery profile using RabbitMQ                    |
| Stream-Oriented Messaging | retained/replayable profile using Kafka when stream semantics are justified |

The Schedule and Occurrence contracts contain no RabbitMQ/Kafka concepts.

The selected profile **MUST** preserve:

- at-least-once delivery
- stable `occurrence_id`
- bounded target contract
- durable transport/target acceptance before dispatch is marked complete
- consumer idempotency
- retry/reconciliation
- Tenant/application ownership context
- evidence/correlation

A single Occurrence contract has one primary delivery path per environment. Blind dual-publishing to RabbitMQ and Kafka is prohibited.

### 5.8 Direct Profile Does Not Expose Workers

For Direct Durable Delivery, Scheduling calls only a registered owning-service durable-acceptance API.

That API persists/deduplicates the Occurrence before successful acknowledgement. A Product Worker may process the accepted operation asynchronously afterwards.

Scheduling never accepts an arbitrary caller-provided URL as a target.

### 5.9 Capability Placement

Durable temporal scheduling and trigger dispatch remain **Engineering & Runtime** capability.

This capability remains distinct from Background Job execution, Workflow, Notification, Work Management, and Product business authority.

## 6. Consequences

### Positive

- one Scheduling contract remains valid across direct, queue, and stream transports
- default deployments can use RabbitMQ without Kafka infrastructure
- Kafka remains available for retained-stream learning and production workloads
- source-local outbox and occurrence idempotency remain stable
- Product Workers stay outside Scheduling
- Notification/Workflow boundaries are unchanged
- broker replacement does not mutate Schedule or Occurrence semantics

### Negative

- Scheduling TDDs must test adapter parity across supported profiles
- direct, RabbitMQ, and Kafka paths expose different operational metrics
- enabling multiple transport profiles across the estate requires stronger contract inventory
- queue and stream semantics cannot be treated as interchangeable

### Operational

- the baseline Scnehaux profile deploys PostgreSQL plus RabbitMQ for Scheduling trigger dispatch
- the stream profile deploys PostgreSQL plus Kafka
- the minimal direct profile deploys no broker for the trigger relationship
- source outbox age is monitored regardless of profile
- consumer business health remains separate from Scheduling dispatch health

## 7. Compliance Impact

### Related Standards

- ADR-GLB-016 Transactional Publication and Durable Messaging Profiles
- ADR-GLB-014 Background Worker Network Boundary
- PAD-PLT-011 Enterprise Scheduling Platform
- STD-GLB-004 Event-Driven Architecture & Messaging Standard
- STD-GLB-010 Durable Scheduled Work Standard

### Compliance Status

Compliant. Scheduling authority remains unchanged while the delivery substrate becomes profile-based.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Keep Kafka Mandatory for Scheduling

Rejected because Scheduling correctness requires durable trigger acceptance and idempotency, not retained-log semantics in every deployment.

### Alternative B — Replace Kafka with RabbitMQ Everywhere

Rejected because Kafka remains the appropriate reference implementation when retained stream/replay/CDC semantics are required.

### Alternative C — Outbox Worker Calls Arbitrary Product Worker URLs

Rejected because it leaks routing/trust into Schedule payloads, creates ungoverned Worker ingress, and violates ADR-GLB-014.

### Alternative D — Deploy RabbitMQ and Kafka for Every Scheduling Occurrence

Rejected because duplicate delivery paths create unnecessary reconciliation, cost, security, and operational surface.

### Alternative E — Execute Product Work Inside Scheduling

Rejected because it collapses Product authority, dependencies, release lifecycle, scaling, and business failure semantics into the shared Scheduler.

### Alternative F — Keep Scheduling Inside Every Product

Rejected because duplicate recurrence, DST, misfire, replay, quota, and recovery semantics are already repeated across multiple applications.
