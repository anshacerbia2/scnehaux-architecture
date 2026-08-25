---
doc_meta:
  id: STD-GLB-012
  title: Enterprise Background Worker Network Exposure Standard
  owner: Architecture Authority
  version: 1.0.0
  status: adopted
  classification: internal
  governed_by:
    - EAD-005
    - EAD-006
  review_cycle_days: 180
  created_date: 2026-08-23
  last_reviewed: 2026-08-23
---

# Enterprise Background Worker Network Exposure Standard (STD-GLB-012)

## 1. Objective & Scope

This standard defines mandatory network-exposure rules for background Worker runtimes across Scnehaux Products and Platforms. It operationalizes ADR-GLB-014 under EAD-005 and EAD-006.

It applies to broker/message consumers, outbox relays, Scheduler due claimers/materializers, Notification delivery/reconciliation workers, indexing/import/export workers, and Product-owned background Job handlers. It does not require API and Worker roles to be separate deployables.

## 2. Design Principles

- Worker is execution topology, not business authority
- no business ingress is safer than unnecessary business ingress
- operational reachability is distinct from Product-facing reachability
- workload identity and least privilege apply even without public ingress
- callbacks/webhooks are ingress-adapter concerns
- topology should minimize total system complexity rather than enforce process purity

## 3. Normative Rules

### 3.1 Pure Worker Business Ingress

- A pure background Worker **MUST NOT** expose a public or Product-facing business HTTP/gRPC/WebSocket endpoint
- A pure Worker **MUST NOT** require inbound business reachability merely to receive normal work from a broker, queue, database claim, schedule occurrence, or equivalent asynchronous source
- Direct ad-hoc HTTP invocation **MUST NOT** replace a declared durable Job/event/schedule contract

### 3.2 Operational Listeners

A Worker **MAY** expose liveness/readiness/startup, metrics, and authenticated diagnostic/admin listeners when required.

Such listeners:

- **MUST NOT** implement Product business commands
- **MUST** remain private/internal
- **MUST** be restricted by network policy or equivalent control
- **MUST** require authentication/authorization for diagnostic or administrative mutation
- **MUST NOT** expose secrets, business payloads, or cross-Tenant data through health/metrics endpoints

### 3.3 Mixed API + Worker Deployables

- A deployable **MAY** contain both API adapters and Worker components
- The owning SAD **MUST** identify which listener is the governed business ingress and which components are background Workers
- Worker business logic **MUST NOT** gain a second direct ingress contract merely because it shares a process with the API
- Separate deployment **SHOULD** occur only when measured scaling, security isolation, release cadence, fault containment, or operational ownership justifies it

### 3.4 External Callbacks and Webhooks

- External callbacks/webhooks **MUST** terminate at an authenticated ingress/API adapter
- The ingress adapter **MAY** persist or enqueue normalized work for a Worker
- Callback authentication, replay protection, rate limiting, schema validation, and evidence **MUST** occur before background execution
- External providers **MUST NOT** call a private delivery/processing Worker directly

### 3.5 Network Policy

- Pure Worker workloads **SHOULD** default-deny inbound traffic
- Only declared operational ports/sources **MAY** be permitted
- Outbound access **MUST** be limited to required brokers, databases, APIs, secret services, telemetry, or provider endpoints
- Worker egress **MUST NOT** rely on broad network-location trust for authorization

### 3.6 Identity and Secrets

- Every unattended Worker **MUST** use attributable non-human workload identity
- Shared human sessions/credentials **MUST NOT** be used for unattended Worker execution
- Secrets **MUST** be resolved through governed secret custody
- Health, readiness, and metrics output **MUST NOT** disclose secrets or raw sensitive payloads

### 3.7 Observability

Worker runtime telemetry **MUST** distinguish business execution metrics, operational listener health, rejected/unauthorized diagnostic access, dependency/egress failures, workload identity, and owning application/Tenant scope where relevant.

## 4. Exceptions

None.

A system with both API and Worker roles is not an exception; it is a mixed-role deployable and must comply with section 3.3.

## 5. Enforcement Mechanism

- SAD review classifies each inbound listener as business or operational
- deployment/network-policy review verifies public/business ingress is absent for pure Workers
- security tests verify operational endpoints are internal and do not expose sensitive data
- runtime inventory records owning workload identity and declared listeners
- architecture review flags direct provider-to-Worker callbacks and ad-hoc HTTP Worker execution
- STD-GLB-011 Job implementations inherit this standard when they use Worker runtime topology
