---
doc_meta:
  id: STD-GLB-011
  title: Enterprise Background Job Execution Standard
  owner: Architecture Authority
  version: 1.1.0
  status: adopted
  classification: internal
  governed_by:
    - EAD-005
  review_cycle_days: 180
  created_date: 2026-08-23
  last_reviewed: 2026-08-23
---

# Enterprise Background Job Execution Standard (STD-GLB-011)

## 1. Objective & Scope

This standard defines mandatory semantics for **bounded background Job execution** across Scnehaux Products and Platforms.

It applies when work executes asynchronously or outside the initiating request and requires governed identity, attempts, duplicate safety, retry, timeout, cancellation, progress, dead-letter/replay, concurrency, telemetry, or durable acceptance.

This standard operationalizes the Work/Workflow/Job/Schedule boundary established by ADR-GLB-013 while attaching normatively to EAD-005 because no independent Job Execution Platform is approved.

It does not require one shared Job runtime and does not authorize a central Platform to host arbitrary Product code.

It excludes:

- durable future timing authority — Scheduling / STD-GLB-010
- durable multi-step process state — Workflow
- business Work Item/Case/Assignment/Claim lifecycle — Work Management
- request-local goroutines/tasks that cannot survive process loss and have no durability requirement
- infrastructure maintenance with no application Job contract

## 2. Design Principles

- A Job is a bounded technical execution unit, not a business aggregate
- Handler/business authority remains with the Product/Platform that owns the effect
- Delivery/execution is assumed at-least-once unless a stronger end-to-end property is explicitly proven
- Retry does not make non-idempotent effects safe by itself
- Worker is execution topology, not authority
- Technical Queue is not Work Management Queue
- Future time belongs to Scheduling
- Multi-step process state belongs to Workflow
- Workload identity, Tenant scope, observability, and bounded resource usage are intrinsic
- Worker network exposure follows STD-GLB-012; pure Worker topology does not create a business ingress API

## 3. Normative Rules

### 3.1 Job Identity and Ownership

- Every durable Job **MUST** have a globally unique `job_id`
- Every Job **MUST** have one owning Product/Platform application or service
- Tenant-scoped Jobs **MUST** carry canonical Tenant scope
- A Job **MUST** identify a registered handler/operation contract rather than arbitrary executable input
- A Job payload **MUST NOT** contain arbitrary shell commands, source code, container images, or unregistered callback code

### 3.2 Workload Identity

- Every Worker **MUST** execute under an attributable non-human workload identity
- Workers **MUST NOT** use shared human credentials for unattended execution
- Provider/service credentials **MUST** be obtained through approved Trust/Secret Services
- Job ownership identifiers **MUST NOT** override authenticated application/workload ownership

### 3.3 Durable Acceptance

- If a caller is told a Job was accepted for durable execution, acceptance **MUST** survive process restart according to the declared RPO
- Durable Job acceptance **MUST** be transactionally coordinated with the owner state that requires the Job, or use an equivalent no-silent-loss pattern
- In-memory-only enqueue **MUST NOT** be reported as durable acceptance

### 3.4 Attempts, Lease, and Claim

- A durable Job execution **MUST** distinguish logical `job_id` from `attempt_id`
- Concurrent workers **MUST** use a lease/claim or equivalent mechanism preventing uncontrolled simultaneous execution
- Lease expiry/recovery semantics **MUST** be deterministic
- A crashed Worker **MUST NOT** leave the Job permanently invisible without an explicit terminal state

### 3.5 Duplicate Safety and Idempotency

- Job delivery/execution **MUST** be treated as at-least-once unless the entire side-effect chain proves otherwise
- A non-idempotent effect **MUST** have an owning-domain duplicate-protection strategy
- Retry of the same logical Job **MUST** preserve correlation to `job_id`
- A new business occurrence **MUST NOT** be fabricated merely to retry technical execution

### 3.6 Retry and Backoff

- Retry **MUST** be bounded by attempt count, elapsed budget, or both
- Retry **MUST** classify transient versus permanent failure
- Backoff **SHOULD** use exponential or workload-appropriate delay with jitter
- Authentication/authorization/validation failures **MUST NOT** be blindly retried
- Product business retry semantics **MUST** remain distinct from technical transport/worker retry

### 3.7 Timeout and Cancellation

- Every Job class **MUST** declare a maximum execution or heartbeat/lease policy
- Cancellation **MUST** have explicit semantics: requested, acknowledged, or terminal
- Cancellation **MUST NOT** claim to undo an already committed external/business effect
- Long-running cancellation-capable handlers **SHOULD** cooperate at safe interruption points

### 3.8 Progress and Result

- Progress **MAY** be reported but **MUST NOT** be treated as authoritative Product state unless the Product explicitly accepts it
- A Job result **MUST** distinguish technical completion from Product business outcome
- Large output artifacts **SHOULD** be stored through Artifact & Document and referenced by identifier rather than embedded unbounded in Job state

### 3.9 Dead Letter and Replay

- Exhausted or non-retryable Jobs **MUST** become explicitly inspectable terminal/dead-letter state
- Replay **MUST** preserve original Job/business correlation
- Replay of a non-idempotent side effect **MUST** require the owning Product's duplicate-safety/revalidation path
- Dead-letter storage **MUST NOT** expose secrets or unrestricted Product payloads

### 3.10 Scheduling Boundary

- A Job that must begin at a durable future time **MUST** use Scheduling when the temporal lifecycle must survive the consumer runtime
- Worker-local delays/backoff **MUST NOT** become a second durable Scheduling authority
- A Schedule Occurrence may request a Job but Scheduler does not own Job completion

### 3.11 Workflow Boundary

- A sequence requiring durable process position, human/system transitions, compensation, or business deadlines **MUST** use Workflow rather than chaining Jobs as an implicit workflow engine
- A bounded Workflow task **MAY** be implemented by a Product/Platform Job

### 3.12 Work Management Boundary

- A Job Queue **MUST NOT** be presented as canonical human Work Queue unless the Work Management contract explicitly owns that lifecycle
- Human assignment, claim, review, and Work Item history **MUST** use Work Management semantics where shared capability is selected

### 3.13 Payload and Secret Safety

- Job state **MUST NOT** contain passwords, API keys, refresh tokens, private keys, or provider session secrets
- Job payloads **SHOULD** contain bounded identifiers/snapshots rather than copied Product aggregates
- Sensitive authoritative facts required at execution time **SHOULD** be re-read by the owner under current authorization/freshness policy

### 3.14 Multi-Tenant Isolation and Fairness

- Shared Job runtimes **MUST** enforce Tenant/application quotas or bounded concurrency where one consumer could starve another
- Worker pools **MUST** isolate materially different risk/resource/provider profiles where needed
- Cross-Tenant administration/replay **MUST** require explicit provider scope and evidence

### 3.15 Observability

Every durable Job implementation **MUST** expose, at minimum:

- accepted/running/succeeded/failed/cancelled/dead-letter counts
- queue/wait time where applicable
- execution duration
- attempts/retries
- lease expiry/recovery
- timeout/cancellation
- duplicate/idempotency outcomes where measurable
- Tenant/application/handler class
- trace/correlation identifiers
- workload identity
- resource/cost signals appropriate to workload

### 3.16 Background Job Technology

- Products/Platforms **MAY** use different compliant runtimes when shared execution is not justified
- A new broker/runtime **MUST NOT** become an enterprise dependency merely because one Product uses it
- Physical runtime selection belongs to the owning SAD/ADR and technology lifecycle governance
- An independent shared Job Execution Platform **MUST NOT** be assumed by this standard

### 3.17 Worker Network Exposure

- Job Worker topology **MUST** conform to STD-GLB-012
- A pure Job Worker **MUST NOT** expose a public/Product-facing business API merely to receive or execute Jobs
- A mixed API + Worker deployable **MAY** remain one deployable when its SAD identifies API ingress and Worker execution boundaries
- Health/readiness/metrics listeners remain operational surfaces rather than Job command contracts

## 4. Exceptions

None.

Local non-durable request-internal asynchronous work is outside this standard only when loss on process termination is explicitly acceptable and no durable acceptance is reported.

## 5. Enforcement Mechanism

Compliance is enforced through:

- PAD/SAD architecture review for Job/Workflow/Schedule/Work classification
- TDD/code review for durable acceptance, idempotency, lease/retry/timeout/cancellation semantics
- CI tests for duplicate execution and restart recovery where applicable
- security checks for workload identity, secrets, and Tenant isolation
- observability/reliability review for production Job classes
- Architecture fitness functions that flag central arbitrary Product-code execution or ambiguous Queue/Workflow/Schedule ownership
