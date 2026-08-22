---
doc_meta:
  id: SAD-006
  title: Workflow Platform SAD
  owner: Architecture Authority
  version: 0.2.0
  status: chartered
  classification: internal
  governed_by:
    - EAD-001
    - EAD-003
    - ADR-GLB-011
  parent_pad: PAD-PLT-004
  review_cycle_days: 180
  created_date: 2026-07-06
  last_updated: 2026-08-22
  last_reviewed: 2026-08-22
---

# Workflow Platform Software Architecture (SAD-006)

> **Status: chartered.** PAD-PLT-004 is approved and no Workflow system is currently authorized for build. This placeholder records inherited constraints only. Physical technology, container, persistence, and workflow-engine decisions are made when implementation enters `draft`.

## 1. Purpose & Scope

### 1.1 Objective

Realize PAD-PLT-004 without re-implementing Product business logic, generic durable scheduling, Notification delivery, or another platform authority.

### 1.2 Capability

Durable long-running human/system process orchestration, workflow state, task coordination, timeout/deadline meaning, escalation state, and compensation.

### 1.3 Requirement

A future implementation must preserve durable process position across failure and coordinate Products through governed contracts while leaving Product operations and outcomes with their owning domains.

### 1.4 Constraint

- one Workflow-owned operational store; no cross-domain database access
- generic durable temporal wake-up is consumed from PAD-PLT-011 rather than reimplemented
- Workflow retains semantic ownership of deadlines, timeout, SLA, escalation, and post-wake-up transitions
- Notification delivery is consumed from PAD-PLT-005
- business operations execute in participating Product/Platform systems
- Identity/Organization are consumed as trust/context, not reimplemented
- transactional outbox applies to published workflow state events

### 1.5 Assumption

The enterprise Event & Messaging, Scheduling, Notification, Identity, Organization, Audit, and Observability capabilities are available according to adoption sequencing.

### 1.6 Out of Scope

- Product business rules and records
- generic recurring/one-shot Scheduler authority
- arbitrary worker hosting
- communication-provider delivery
- external provider business ownership

## 2. Enterprise Traceability

| Relationship | Target |
| :-- | :-- |
| Realizes | PAD-PLT-004 |
| Governed by | EAD-001 and EAD-003 |
| Boundary decision | ADR-GLB-011 |
| Consumes | PAD-PLT-011 durable temporal wake-up |
| Consumes | PAD-PLT-005 communication delivery |

## 3. Solution Context

### 3.1 System Context

A Business Product starts or advances a durable process. Workflow records process state and delegates Product work through governed contracts. When a future wake-up is required, Workflow registers it with Scheduling and resumes only after receiving the due occurrence.

### 3.2 External

External Product/vendor operations remain with their Natural Owner or governed Integration capability. Workflow does not become a universal external gateway.

### 3.3 Internal

No physical internal decomposition is authorized while this SAD remains chartered.

## 4. Architecture Model

### 4.1 Container

The physical container model is intentionally deferred until the SAD moves to `draft`.

### 4.2 Component

Workflow implementation must preserve domain/app/adapter dependency direction and keep workflow semantics independent of Scheduler/Notification implementation technology.

### 4.3 Runtime Flow

Conceptual durable timer flow:

```text
Workflow state -> Scheduling registration -> due occurrence -> Workflow resumes -> Product operation
```

The due occurrence does not choose a Workflow transition by itself.

## 5. State & Data Architecture

### 5.1 Storage

Workflow owns process definitions, instances, task state, timer/deadline semantic state, compensation state, and process history. Scheduling owns generic Schedule/Occurrence runtime state.

### 5.2 Schema

Physical schema design is deferred. Enterprise UUIDv7, RLS, migration-role, and declarative-schema standards apply when implementation begins.

### 5.3 Cache

Any future cache is non-authoritative and has explicit staleness semantics.

### 5.4 Stateless

Compute is restartable; durable workflow position is not held only in process memory.

## 6. Integration Contracts

### 6.1 API

Versioned workflow control contracts are defined before implementation.

### 6.2 Published Events

Workflow lifecycle events use the enterprise CloudEvents/schema-registry standard and transactional outbox.

### 6.3 Consumed

Scheduling due occurrences, Product events/results, Notification capability, and bounded trust/context contracts.

## 7. Security & Trust Boundary

### 7.1 Authentication

Delegated to enterprise Identity with local protected-resource validation where applicable.

### 7.2 Authorization

Workflow authorizes its own process/task operations. Participating Products independently authorize business operations.

### 7.3 Encryption

Enterprise transport and at-rest encryption baselines apply.

### 7.4 Secrets

No Product/provider secret becomes Workflow-owned merely because a task is orchestrated.

### 7.5 Audit

Workflow definition/lifecycle, task coordination, timeout, escalation, compensation, cancellation, and privileged operations publish evidence.

## 8. NFR

### 8.1 Blast Radius

A Workflow outage pauses durable process progress rather than losing process state. A Scheduling outage delays timer wake-ups but does not lose Workflow position. A Notification outage delays communication without changing Workflow/Product truth.

### 8.2 Observability and Telemetry

A future design must expose process success/failure, stuck state, task latency, timer/wake-up lag, downstream dependency health, and Tenant impact through OpenTelemetry-compatible telemetry.

### 8.3 Retry, Timeout, and Circuit Breaker

Workflow retry/compensation semantics are explicit per step. Scheduling retry covers only temporal dispatch, and Notification retry covers only communication delivery.

### 8.4 Runbook

Runbooks are a production gate when implementation begins.

## 9. Deployment Strategy

### 9.1 Environment

Physical environment topology is deferred until implementation authorization.

### 9.2 Infrastructure

No workflow engine/runtime technology is selected by this chartered placeholder.

### 9.3 CI/CD

A future draft must define blocking build, contract, migration, resilience, security, and architecture gates.

## 10. Architecture Decisions

### 10.1 Accepted

Inherited PAD-PLT-004 boundaries and ADR-GLB-011 Scheduler/Workflow authority separation.

### 10.2 Rejected

#### 10.2.1 Workflow as Universal Scheduler

Rejected because durable application scheduling without workflow state belongs to PAD-PLT-011.

#### 10.2.2 Product Business Logic Inside Workflow

Rejected because Product domains own business meaning and irreversible outcomes.

#### 10.2.3 Implementation Against This Placeholder

Rejected until a system design moves this SAD to `draft` and passes design review.

## 11. Assumptions

The Workflow capability remains chartered and its first implementation will be driven by concrete consumer process evidence.

## 12. Compatibility Strategy

Workflow contracts are versioned independently of the eventual workflow engine. Scheduling and Notification are consumed through their platform contracts rather than physical implementation details.
