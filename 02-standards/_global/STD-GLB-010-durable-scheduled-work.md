---
doc_meta:
  id: STD-GLB-010
  title: Enterprise Durable Scheduled Work Standard
  owner: Architecture Authority
  version: 1.0.0
  status: adopted
  classification: internal
  governed_by:
    - ADR-GLB-011
  review_cycle_days: 180
  created_date: 2026-08-22
  last_reviewed: 2026-08-22
---

# Enterprise Durable Scheduled Work Standard (STD-GLB-010)

## 1. Objective & Scope

This standard defines mandatory semantics for durable scheduled work across Scnehaux Products and Platforms. It governs schedule ownership, time representation, occurrence identity, dispatch, duplicate safety, misfire, lifecycle mutation, Tenant isolation, and operational evidence.

It applies when a future action must survive consumer restart, infrastructure restart, or independent deployment and is represented through the shared Scheduling capability.

It excludes request deadlines, short retry backoff, tight connector polling loops, in-process debounce/throttle, and infrastructure-local maintenance whose lifecycle is not an application scheduling contract.

## 2. Design Principles

- A durable schedule is temporal state, not business state
- A due occurrence is a trigger, not proof of business completion
- Business meaning and irreversible outcomes remain with the owning consumer
- Runtime time is explicit: UTC instants for occurrences and IANA time zones for wall-clock recurrence
- Delivery is at-least-once and consumers are duplicate-safe
- Schedule payloads are bounded identifiers or immutable trigger inputs, never a substitute business database
- Multi-tenant ownership, quota, and audit are intrinsic to the contract rather than later extensions
- Timing implementation is replaceable behind the enterprise scheduling contract

## 3. Normative Rules

### 3.1 Classification of Timed Work

- A Product or Platform **MUST** use the shared Scheduling capability when a future trigger must survive consumer restart and its lifecycle is managed independently of the consumer process
- A Product or Platform **MUST NOT** register request deadlines, short transient retry backoff, tight connector poll loops, or in-process debounce timers as enterprise schedules
- A timed workflow step **MUST** remain Workflow-owned in meaning even when Scheduling provides the durable wake-up
- A scheduled communication whose business eligibility must be revalidated at due time **MUST** target the owning Product/Platform worker before Notification is requested
- A Notification **MAY** register its own future delivery only after the communication intent, recipient snapshot, and governed content version are frozen

### 3.2 Identity and Ownership

- Every Schedule **MUST** have a globally unique, non-enumerable `schedule_id`
- Every Schedule **MUST** have one owning `application_id`
- Every Tenant-scoped Schedule **MUST** carry the canonical `tenant_id` issued by the Organization authority
- Consumer-supplied ownership identifiers **MUST NOT** override ownership derivable from authenticated workload/client context
- A Schedule **MUST** target a registered application or platform contract
- Arbitrary executable code, shell commands, container images, and unregistered callback URLs **MUST NOT** be Schedule targets

### 3.3 Time Representation

- Every materialized Occurrence **MUST** persist a canonical RFC 3339 UTC `scheduled_for` instant
- A one-time Schedule **MUST** resolve to exactly one UTC instant
- A recurring wall-clock Schedule **MUST** declare an IANA time-zone identifier
- Server-local time and locale-dependent date parsing **MUST NOT** define schedule behavior
- Recurrence syntax and semantic interpretation **MUST** be versioned by the scheduling contract
- A consumer **MUST** be able to preview computed future occurrences before activating or materially changing a recurring Schedule

### 3.4 Daylight-Saving-Time Behavior

- Recurring wall-clock schedules **MUST** have deterministic handling for nonexistent and repeated local times
- The effective DST policy **MUST** be explicit in the contract or bound to a versioned platform policy
- A recurrence-library or time-zone-data upgrade that changes computed UTC occurrences for an existing Schedule **MUST** fail compatibility regression tests before release

### 3.5 Occurrence Identity and Duplicate Safety

- A due occurrence **MUST** be materialized durably before dispatch
- Every Occurrence **MUST** have one stable `occurrence_id`
- Dispatch retries of the same logical Occurrence **MUST** reuse its `occurrence_id`
- The authoritative store **MUST** prevent concurrent replicas or restart recovery from creating two logical Occurrences for one Schedule version and `scheduled_for` instant
- Trigger delivery **MUST** be treated as at-least-once
- A consumer **MUST** enforce idempotency on `occurrence_id` before a non-idempotent side effect
- A duplicate occurrence **MUST NOT** create a duplicate irreversible business effect

### 3.6 Dispatch Semantics

- A due Occurrence **MUST** be published through the governed enterprise asynchronous contract
- Scheduler dispatch success **MUST** mean durable acceptance by the messaging boundary and **MUST NOT** mean consumer business completion
- The Scheduling Platform **MUST NOT** execute arbitrary consumer business code
- Scheduler retry **MUST** cover dispatch to the governed messaging boundary only
- Consumer execution retry, compensation, and final business status **MUST** remain with the consumer or Workflow Platform
- Trigger envelopes **MUST** carry correlation, ownership, and occurrence metadata sufficient for distributed tracing without carrying credentials

### 3.7 Misfire Semantics

Every durable recurring Schedule **MUST** select one supported misfire behavior:

- `skip` — missed occurrences are not replayed
- `fire_once` — recovery emits one occurrence representing the missed window
- `catch_up_bounded` — missed occurrences are replayed only up to an explicit finite maximum

Additional rules:

- Unlimited catch-up **MUST NOT** be supported
- Recovery Occurrences **MUST** retain the original logical `scheduled_for` instant
- A misfire-policy mutation **MUST** be versioned as a Schedule change
- Misfire outcomes **MUST** be observable and auditable

### 3.8 Pause, Resume, Update, Cancel, and Replay

- Schedule mutation **MUST** use optimistic concurrency or an equivalent stale-write prevention mechanism
- Pause **MUST** prevent future occurrence materialization after the pause mutation commits
- Resume **MUST** apply the persisted misfire policy to elapsed time
- Cancel **MUST** be terminal for that Schedule identity
- Cancellation **MUST NOT** claim to retract an Occurrence whose Trigger was already durably dispatched
- Near-due update/cancel races **MUST** have deterministic tested semantics
- Operational replay **MUST** re-dispatch the same Occurrence identity rather than fabricate a new business occurrence

### 3.9 Payload, Data, and Secret Safety

- Schedule state **MUST NOT** contain passwords, bearer tokens, refresh tokens, API keys, private keys, or provider credentials
- Trigger data **SHOULD** contain identifiers or bounded immutable input rather than copied Product aggregates
- Sensitive authoritative Product facts needed at execution time **SHOULD** be re-read by the consumer under its own freshness and authorization rules
- Cross-domain database reads **MUST NOT** be introduced to satisfy scheduled execution

### 3.10 Multi-Tenant Isolation, Quota, and Fairness

- Tenant-scoped Schedule state **MUST** enforce the enterprise Tenant isolation baseline
- Schedule count, creation rate, and due-trigger rate **MUST** have explicit application/Tenant limits
- One Tenant or application **MUST NOT** be able to consume unbounded dispatcher capacity
- Provider or administrative operations that cross Tenant boundaries **MUST** use a separately authorized and auditable path
- Shared Scheduling **MUST** support pooled multi-tenant operation without requiring one scheduler deployment per Tenant

### 3.11 Messaging and Persistence

- State mutation and trigger publication **MUST** follow the enterprise transactional-outbox decision
- Published due-occurrence events **MUST** conform to the enterprise event-driven standard and schema-registry compatibility rules
- In-memory cron state **MUST NOT** be the sole durable authority for enterprise Schedules
- A recurrence library **MAY** calculate next occurrences, but durable ownership, lifecycle, and occurrence state **MUST** remain in the Scheduling authority

### 3.12 Observability and Reconciliation

The Scheduling capability **MUST** expose at minimum:

- active Schedule count by application and Tenant
- due occurrence materialization rate
- dispatch lateness (`dispatched_at - scheduled_for`)
- oldest undispatched Occurrence
- dispatch success/failure rate
- misfire count by policy
- replay count
- duplicate-dispatch count
- quota utilization and rejected admissions
- authoritative-store contention/claim latency
- outbox publication lag

A consumer **MUST** be able to reconcile its business-owned scheduling references against the Scheduling contract without direct database access.

## 4. Exceptions

The following timing mechanisms remain outside this standard when they do not represent durable application scheduling state:

- HTTP/request deadlines
- short transient retry/backoff inside one owned operation
- connection keepalive and reconnect timers
- tight connector polling loops
- in-process debounce and throttle
- deployment/infrastructure maintenance timers owned entirely by the runtime substrate

## 5. Enforcement Mechanism

- Architecture review checks every durable schedule implementation against PAD-PLT-011 and this standard
- Contract tests verify one-time, recurring, pause, resume, update, cancel, replay, and optimistic-concurrency semantics
- A time-zone golden corpus verifies DST gaps, repeated local times, leap-calendar boundaries, and time-zone-data upgrades
- Concurrency tests prove one logical Occurrence under multiple Scheduler replicas
- Restart and fault-injection tests prove accepted Schedule state and un-dispatched Occurrences survive process loss
- Duplicate-delivery tests prove the same logical Occurrence reuses one `occurrence_id`
- Tenant-isolation and quota tests run under the production-equivalent runtime database role
- Event schema compatibility and consumer idempotency tests are blocking CI gates
- Static architecture checks flag new shared durable cron/scheduler authorities outside the governed Scheduling capability for review
