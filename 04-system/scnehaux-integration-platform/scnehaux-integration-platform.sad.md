---
doc_meta:
  id: SAD-007
  title: Integration Platform SAD
  owner: Architecture Authority
  version: 0.2.0
  status: chartered
  classification: internal
  governed_by:
    - EAD-001
    - EAD-004
  parent_pad: PAD-PLT-006
  review_cycle_days: 180
  created_date: 2026-07-06
  last_updated: 2026-08-22
  last_reviewed: 2026-08-22
---

# Integration Platform Software Architecture (SAD-007)

> **Status: chartered.** PAD-PLT-006 is approved and no physical shared Integration runtime is currently authorized for build. This placeholder records inherited constraints only. It does not establish a universal integration gateway.

## 1. Purpose & Scope

### 1.1 Objective

Realize reusable connector, protocol, transformation, routing, and integration-governance machinery where shared execution is justified while preserving the Natural Owner of each external business relationship.

### 1.2 Capability

Reusable external/internal connector lifecycle, protocol translation, transformation, routing, integration contract registry, policy, reconciliation support, and integration observability.

### 1.3 Requirement

A future implementation must be optional machinery selected by integration evidence. It cannot require every Product or Platform external call to traverse one runtime.

### 1.4 Constraint

- external authority and business meaning remain with the Natural Owner
- Product/Platform direct adapters remain allowed under enterprise contract/security/observability standards
- Event & Messaging broker ownership remains Engineering & Runtime rather than this domain
- Notification naturally owns communication-provider delivery adapters
- credentials are consumed from Trust Services
- Integration never owns exchanged Product business truth

### 1.5 Assumption

Concrete shared connectors will be justified by multiple consumers, independent lifecycle, governance, scale, risk, or protocol reuse before build.

### 1.6 Out of Scope

- universal gateway topology
- Event Broker ownership
- Product business logic
- Workflow execution
- Notification delivery semantics
- Identity authority
- Product data authority

## 2. Enterprise Traceability

| Relationship | Target |
| :-- | :-- |
| Realizes | PAD-PLT-006 |
| Governed by | EAD-001 and EAD-004 |
| Aligns with | EAD-002 Shared Integration is not a universal gateway |
| Consumes | Event & Messaging, Trust, Identity/Application Trust, Audit/Observability |

## 3. Solution Context

### 3.1 System Context

Products/Platforms may use a shared Integration runtime when connector/protocol reuse is justified. A domain-specific external adapter may remain inside its Natural Owner without violating the enterprise architecture.

### 3.2 External

External systems retain their canonical authority. A connector translates/protects the boundary but does not become the business source of truth.

### 3.3 Internal

No physical connector host, gateway, broker, or transformation engine is selected while this SAD remains chartered.

## 4. Architecture Model

### 4.1 Container

Physical container topology is deferred until concrete shared connector requirements enter build.

### 4.2 Component

A future design must terminate vendor models in adapter/ACL boundaries and keep Product-domain contracts independent of vendor SDKs.

### 4.3 Runtime Flow

```text
Natural Owner -> governed Integration contract (when justified) -> external provider/system
```

or, for a domain-specific relationship:

```text
Natural Owner -> governed local adapter -> external provider/system
```

Both remain subject to enterprise standards.

## 5. State & Data Architecture

### 5.1 Storage

Future Integration state is limited to connector/configuration/correlation/reconciliation metadata required by shared connector contracts. Product business records remain external to this domain.

### 5.2 Schema

Physical persistence and migration design are deferred until a draft system exists.

### 5.3 Cache

Any future cache is non-authoritative with explicit staleness and invalidation semantics.

### 5.4 Stateless

Connector compute is replaceable/restartable; authoritative Product/external facts are not held solely in connector memory.

## 6. Integration Contracts

### 6.1 API

Shared connector/control contracts are versioned when implementation begins.

### 6.2 Published Events

Connector lifecycle/status events use Event & Messaging contracts but Integration does not own the broker.

### 6.3 Consumed

Event & Messaging, Trust Services, Identity/Application Trust, Audit/Evidence, Observability, and external provider/system protocols.

## 7. Security & Trust Boundary

### 7.1 Authentication

Enterprise human/workload authentication applies at control and runtime boundaries.

### 7.2 Authorization

Connector usage and administration are scoped by registered Product/Platform/Tenant relationships.

### 7.3 Encryption

Enterprise in-transit and at-rest security baselines apply.

### 7.4 Secrets

Connector credentials remain in Trust Services and are not exposed to consuming Products beyond the governed contract.

### 7.5 Audit

Connector creation/change, contract/policy mutation, replay/reconciliation, and privileged cross-Tenant operations produce evidence.

## 8. NFR

### 8.1 Blast Radius

One provider/connector failure must remain isolated from unrelated integrations. A shared Integration outage affects only consumers that selected its runtime; direct Natural-Owner adapters outside that runtime are not made dependent by architecture label alone.

### 8.2 Observability and Telemetry

Future connectors expose provider latency/error/rate-limit, backlog/reconciliation, Tenant/app impact, and contract health.

### 8.3 Retry, Timeout, and Circuit Breaker

Future connector designs apply bounded retry, timeout, backpressure, and provider-specific bulkheads according to enterprise resilience standards.

### 8.4 Runbook

Runbooks become mandatory when a physical connector/runtime enters production.

## 9. Deployment Strategy

### 9.1 Environment

No environment topology is authorized by this chartered placeholder.

### 9.2 Infrastructure

No universal gateway, connector framework, or integration product is selected here.

### 9.3 CI/CD

A future draft must define contract compatibility, adapter boundaries, security, failure-injection, secret, and architecture gates.

## 10. Architecture Decisions

### 10.1 Accepted

Inherited EAD-002/EAD-004 rule that Integration is reusable optional machinery rather than a mandatory hop.

### 10.2 Rejected

#### 10.2.1 Universal Integration Gateway

Rejected because it adds synchronous blast radius and strips Natural Owners of direct responsibility without proven reuse value.

#### 10.2.2 Event Broker Ownership in Integration Domain

Rejected because Event & Messaging is an Engineering & Runtime capability.

#### 10.2.3 Implementation Against This Placeholder

Rejected until concrete shared connector requirements justify a draft physical design.

## 11. Assumptions

Integration remains chartered until concrete connector consumers establish a physical runtime need.

## 12. Compatibility Strategy

Shared Integration contracts isolate consuming domains from connector/provider implementation. A direct adapter can later migrate behind shared Integration without changing Product business authority.
