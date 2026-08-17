---
doc_meta:
  id: SAD-011
  title: AI Platform SAD
  owner: Architecture Authority
  version: 0.1.0
  status: chartered
  classification: internal
  governed_by:
    - EAD-001
    - EAD-003
  parent_pad: PAD-PLT-008
  review_cycle_days: 180
  created_date: 2026-07-06
  last_updated: 2026-08-18
  last_reviewed: 2026-08-18
---

# AI Platform Software Architecture (SAD-011)

> **Status: chartered.** The capability is chartered by PAD-PLT-008 and no system is in build.
> Every statement below is inherited from an enterprise document that has already decided
> it. Nothing here is a system-specific design choice, because those are made when the
> system enters build and this document moves to `draft`.
>
> EAD-001 section 5.4 is explicit that a target capability is not implementation
> authorization. This document records the constraints a build inherits on day one so that
> they are not rediscovered or renegotiated then.

---

## 1. Purpose & Scope

This document records the architectural constraints the AI Platform inherits from the enterprise architecture. It is the placeholder that a full system design replaces.

### 1.1 Objective

Realize the capability PAD-PLT-008 charters, within the constraints below, without re-implementing a capability another platform owns.

### 1.2 Capability

Inference, retrieval, and intelligent services.

### 1.3 Constraint

These are inherited and not open to per-system renegotiation:

- **One owning domain, one operational store.** This system owns the AI Store and Vector Index and no other system reads it directly, per EAD-003 section 5.1.
- **No shared operational database and no cross-domain query.** Other domains obtain this system's data through its published API or its events, per EAD-003 section 6.5.
- **Tier-2.** Availability at or above 99.9%, RTO within 4 hours, RPO within 1 hour, per EAD-005 section 5.4.
- **Independently deployable** on its own pipeline, with no coordinated enterprise release, per EAD-002 section 6.2.
- **Identity is consumed, never implemented.** Authentication and token issuance belong to the Identity Platform, per EAD-006 section 6.2.
- **Zero Trust.** Every request is authenticated and authorized regardless of origin, and every internal call is mutually authenticated, per EAD-006 sections 5.1 and 5.4.
- **UUIDv7 primary keys, Row-Level Security for tenant-scoped tables, and declarative schema management**, per STD-GLB-002 and ADR-GLB-002.
- **The transactional outbox** for every published domain event, per ADR-GLB-003.

### 1.4 Requirement

The capability requirements are held by PAD-PLT-008 until a system design exists. This document adds none of its own.

### 1.5 Assumption

The platform substrate described by EAD-005 is available: a managed runtime, brokered secrets, telemetry collection, and the event broker.

---

## 2. Enterprise Traceability

| Relationship | Target |
| :-- | :-- |
| Realizes | PAD-PLT-008 |
| Governed by | EAD-001 — capability ownership and strategic classification |
| Governed by | EAD-003 — data ownership and the operational store assignment |
| Conforms to | EAD-002 — the dependency direction and its acyclic constraint |
| Conforms to | EAD-006 — the mandatory security controls every system inherits |
| Conforms to | STD-GLB-BE-001 — internal package structure and boundary assertion |

---

## 3. Solution Context

### 3.1 System Context

Synchronous inference and asynchronous batch. No consumer places this platform on a synchronous critical path.

Dependencies point inward and downward toward stable substrate and never form a cycle, per EAD-002 section 5.3. This system may depend on Platform Services and MUST NOT be depended upon by one.

### 3.2 External Dependencies

Every external vendor is mediated by the Integration Platform acting as an Anti-Corruption Layer. No vendor SDK or vendor payload model appears inside this system, per EAD-002 section 6.4.

### 3.3 Internal Structure

A modular monolith: one bounded context, one deployable, modules separated at compile time, per ADR-GLB-001 section 5.1 and STD-GLB-BE-001 Rule 1.

---

## 4. Architecture Model

### 4.1 Container View

One deployable service and its operational store. The container decomposition is a system design decision and is made when this document moves to `draft`.

### 4.2 Component View

Components follow the layer direction STD-GLB-BE-001 Rule 2 fixes: adapter depends on app, app depends on domain, and the domain depends on neither. Internal edges are declared in a manifest and asserted against the package graph on every build.

### 4.3 Event Flow

Domain events are appended to the outbox inside the transaction that mutates the aggregate, and a dispatcher publishes them to the broker. A consumer deduplicates on the event identifier inside the same transaction as its effect, which is what makes at-least-once delivery safe.

---

## 5. State & Data Architecture

### 5.1 Storage

The AI Store and Vector Index holds embeddings and the retrieval index. It is private to this domain: no other system holds a connection to it, and no cross-domain join exists, per EAD-003 sections 5.1 and 6.5.

### 5.2 Schema

Declarative under Atlas, with migrations generated deterministically and applied by a job running under a migration role distinct from the runtime role, per ADR-GLB-004. The runtime role holds no DDL privilege.

### 5.3 Cache

Any cache carries a bounded lifetime and an explicit staleness behaviour. A cached authorization decision is never used to permit an action.

### 5.4 Stateless Runtime

The process holds no state that survives a request, so replicas are interchangeable and scale horizontally, per EAD-005 section 5.3.

---

## 6. Integration Contracts

### 6.1 Published API

A versioned contract owned by this system, published before implementation, per EAD-004 section 6.3. REST with an OpenAPI 3.1 document for control-plane and client-facing interfaces; gRPC for internal request-hot-path interfaces, per STD-GLB-006. Errors are RFC 9457 problem documents.

### 6.2 Published Events

CloudEvents 1.0 in JSON, registered in the enterprise schema registry, with backward compatibility enforced in the build, per STD-GLB-004 and ADR-GLB-006. A breaking change promotes the major version inside the event type.

### 6.3 Consumed Events and Capabilities

Consumed contracts belong to their publishing domains. This system depends on the contract and never on a publisher's internal model.

---

## 7. Security & Trust Boundary

**Authentication** is delegated to the Identity Platform. Tokens are verified locally against the published JWKS, per STD-IAM-002 section 3.5, and a token for an internal audience without `principal_id` is rejected.

**Authorization** is applied by this system to every command. A valid token is an authenticated identity and never an authorization decision.

**Encryption**: TLS 1.3 in transit and AES-256 at rest, per EAD-006 section 5.5.

**Secrets** are brokered from the managed store and never present in source or in an image, per EAD-006 section 5.5.

**Audit**: every security-sensitive action publishes an immutable evidence event to the Audit Platform, per EAD-006 section 6.6.

---

## 8. NFR

### 8.1 Blast Radius

Consumers degrade gracefully to non-AI behaviour rather than failing. This is why EAD-001 section 5.3 assigns Tier-2 to a Shared Platform: inference is best-effort by contract, and a consumer that cannot proceed without it has violated that contract.

The reliability tier is inherited rather than chosen: Tier-2 at or above 99.9%, with RTO within 4 hours and RPO within 1 hour. An error budget derived from that target gates feature work when exhausted, per EAD-005 section 5.4.

### 8.2 Observability and Telemetry

OpenTelemetry traces, RED metrics, and structured JSON logs to stdout, every line carrying the trace and span identifiers and the tenant identifier where one applies, per STD-GLB-003. No vendor agent is coupled into application code.

### 8.3 Timeout, Retry, and Circuit Breaker

The cascaded timeout hierarchy, three retries with exponential backoff and jitter for transient classes only, bulkhead isolation per downstream dependency, and priority-based load shedding, all per STD-GLB-005 and ADR-GLB-005.

### 8.4 Runbook

Runbooks are written before production and are a release gate rather than a follow-up. Their contents depend on the system design and are authored with it.

---

## 9. Deployment Strategy

### 9.1 Environment and Infrastructure

The standardised containerised runtime on Kubernetes across multiple availability zones, provisioned declaratively through the Internal Developer Platform. Direct resource creation through a cloud console is prohibited, per STD-GLB-009.

### 9.2 CI/CD

The Golden Path pipeline, with every gate blocking a merge: formatting, static analysis, build, tests under the race detector, a coverage floor, package-graph boundary assertion, schema migration integrity and the destructive gate, event schema compatibility, dependency tidiness, secret scanning, and a scheduled vulnerability scan.

Deployment is zero-downtime and progressive, and any deployment is reversible within five minutes, per EAD-005 section 5.3.

---

## 10. Architecture Decisions

### Accepted

Every inherited constraint in section 1.3, each traced to the enterprise document that decided it. This document makes no independent decision, which is the property that distinguishes a chartered placeholder from a design.

### Rejected

#### 10.1 Placing inference on a synchronous critical path

Rejected. It would make a Tier-2 dependency into a Tier-1 requirement and couple product availability to an external model provider. EAD-001 section 5.3 records the Tier-2 assignment as conditional on exactly this constraint being honoured.

#### 10.2 Re-implementing a capability another platform owns

Rejected by EAD-001 section 6.1. A shared capability implemented twice produces divergent behaviour and multiplied cost, and the duplication is invisible until the two versions disagree in production.

#### 10.3 Beginning implementation against this document

Rejected. A chartered placeholder is not an implementation authorization. A build starts when this document holds a system design, has moved to `draft`, and has passed design review.

---

## 11. Assumptions

- The capability remains chartered and is not folded into another domain before build.
- The enterprise substrate and the platform capabilities this system consumes are available at build time.

---

## 12. Compatibility Strategy

APIs are versioned in the path and events in the type. A breaking change requires a new major version and a deprecation window of at least 90 days or two consumer release cycles, whichever is longer, per EAD-004 section 5.3.
