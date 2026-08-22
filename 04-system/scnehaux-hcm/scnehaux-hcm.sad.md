---
doc_meta:
  id: SAD-101
  title: HCM Business System SAD
  owner: Architecture Authority
  version: 0.2.0
  status: chartered
  classification: internal
  governed_by:
    - EAD-001
    - EAD-005
  parent_pad: PAD-BIZ-001
  review_cycle_days: 180
  created_date: 2026-07-06
  last_updated: 2026-08-23
  last_reviewed: 2026-08-23
---

# HCM Business System SAD

> **Status: chartered.** The parent PAD is approved, but no physical system design is approved. This document records inherited constraints only. Implementation against this placeholder is rejected until the SAD moves to `draft` and contains a reviewed physical design.

## 1. Purpose & Scope

### 1.1 Objective

Record the physical-design entry constraints for the system that may realize PAD-BIZ-001.

### 1.2 Capability

HCM Business Product system for authoritative Employee/Employment/HR Organization/Position and related workforce lifecycle capabilities.

### 1.3 Constraint

- HCM owns workforce business semantics and Product authorization
- Identity owns Principal/authentication
- Organization owns Organization/Tenant/Workspace/Membership operating context
- Workspace Experience owns shared human work composition only
- Workflow/Work Management/Rules/AI/Knowledge/Artifact/Notification remain separate reusable capabilities
- future ERP integration uses contracts and no cross-domain persistence

### 1.4 Requirement

The future design SHALL realize the parent PAD without re-owning a capability assigned to another Product or Platform.

### 1.5 Assumption

No database, broker, graph store, vector store, model provider, framework, runtime topology, or deployment product is selected by this charter.

## 2. Enterprise Traceability

| Relationship | Target |
| :-- | :-- |
| Parent PAD | PAD-BIZ-001 |
| Capability authority | EAD-001 |
| Data authority | EAD-003 |
| Integration | EAD-004 |
| Platform/runtime posture | EAD-005 |
| Security | EAD-006 |
| Governance & Assurance | EAD-007 |

## 3. Solution Context

### 3.1 System Context

The physical System Context is intentionally undecided. Consumers interact through the parent PAD's logical contracts.

### 3.2 External Dependencies

External provider/runtime dependencies are selected only during system design and must preserve Natural Owner, authority, security, and portability rules.

### 3.3 Internal Dependencies

Consumed logical capabilities: Identity, Organization, Workspace Experience, Work Management, Workflow, Rules & Decisioning, Artifact & Document, Notification, Knowledge & Retrieval, AI Enablement, Integration, Audit & Evidence, Event & Messaging.

## 4. Architecture Model

### 4.1 Container

No Container topology has been selected.

### 4.2 Component

No Component decomposition has been selected.

### 4.3 Sequence / Runtime Flow

Critical Sequence and Runtime Flow diagrams are authored when the SAD moves to `draft`.

### 4.4 Event Flow

Event Flow is defined only where the parent PAD contract and system design justify asynchronous publication/consumption.

## 5. State & Data Architecture

### 5.1 Storage

Storage technology and topology are not selected. Any authoritative operational state remains private to this system capability.

### 5.2 Cache

Cache is not selected and can never become sole durable authority.

### 5.3 Schema

Schema/DDL is a TDD concern after physical persistence is selected.

### 5.4 Stateless

The future runtime may be Stateless where possible, but durable state required by the parent PAD must survive process restart through an approved storage design.

## 6. Integration Contracts

### 6.1 API

Concrete API protocols/endpoints are selected in the draft SAD and must implement versioned parent-PAD contracts.

### 6.2 Event

Concrete Event contracts are selected only where asynchronous interaction is justified.

### 6.3 Consumed

Identity, Organization, Workspace Experience, Work Management, Workflow, Rules & Decisioning, Artifact & Document, Notification, Knowledge & Retrieval, AI Enablement, Integration, Audit & Evidence, Event & Messaging

### 6.4 Published

HCM workforce domain events according to parent PAD

## 7. Security & Trust Boundary

**Authentication** uses enterprise Identity; this system does not issue user credentials.

**Authorization** remains split according to EAD-006 and the parent PAD. Product business authorization is not inferred from platform access.

**Encryption** must satisfy enterprise data classification and transport/storage requirements once technology is selected.

**Secrets** use managed custody; no production secret may be embedded in source, image, browser bundle, or architecture artifact.

**Audit** evidence is emitted for privileged and consequential capability operations as required by Governance & Assurance.

## 8. NFR

### 8.1 Blast Radius

Failure blocks/degrades workforce operations but must not cause Identity/Organization authority drift. AI/Knowledge unavailability must not silently corrupt HCM authoritative state.

### 8.2 Observability and Telemetry

The draft design must define OpenTelemetry-compatible or enterprise-approved Telemetry, actionable Alerting, and a production Runbook appropriate to its reliability class.

### 8.3 Scalability

Capacity, Throughput, RPS or work-rate, and Concurrency targets are derived from parent-PAD consumers before approval.

### 8.4 Timeout, Retry, Circuit Breaker, Failover

Timeout, bounded Retry, Circuit Breaker, backpressure, and Failover behavior are defined per dependency once a physical design exists.

## 9. Deployment Strategy

### 9.1 Environment and Infrastructure

Environment and Infrastructure topology are not selected by this charter.

### 9.2 CI/CD

The future deployable uses the enterprise CI/CD paved road and must pass architecture, security, contract, test, provenance, and deployment gates appropriate to the selected technologies.

## 10. Architecture Decisions

### Accepted

Only the logical authority and boundary decisions already approved by the parent PAD and EADs.

### Rejected

- beginning implementation against a `chartered` placeholder
- selecting a technology solely because an existing ATI project happened to use it
- creating a second canonical authority for a fact owned elsewhere
- turning a shared capability into a universal runtime hop without evidence

## 11. Assumptions

- Consumer demand and operating profile will be validated before physical design approval
- Platform qualification can be revisited if total shared-system complexity exceeds the value created

## 12. Compatibility Strategy

The future system must preserve parent-PAD logical contracts across implementation replacement.

## 13. Migration Strategy

Existing Product-local implementations are migration evidence only; they are not reference architecture. Migration occurs after the target SAD is approved.

## 14. Alternatives

Technology and topology alternatives remain open until `draft`.
