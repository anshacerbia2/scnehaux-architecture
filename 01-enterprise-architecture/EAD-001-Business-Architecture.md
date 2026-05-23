---
doc_meta:
  id: EAD-001
  title: Enterprise Business Architecture
  owner: Chief Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# Enterprise Business Architecture (EAD-001)

---

## 1. Context & Business Drivers

The Scnehaux Foundation Business Architecture defines the capability-centric blueprint of the organization. It establishes the "North Star" for all domain models, ensuring that software boundaries map strictly to business capabilities rather than organizational charts.

This document directs the structural decomposition of the enterprise into strictly encapsulated, cohesive domains that enable independent scaling and autonomous product evolution.

## 2. Enterprise Principles

- **Zero Trust by Default**: Identity is the new perimeter. Every transaction must be cryptographically verified and authorized, regardless of origin network.
- **API-First Contracts**: Every capability must expose its functionalities via strict, versioned API contracts (OpenAPI/gRPC). Hidden capabilities are prohibited.
- **Domain-Driven Decoupling**: Service boundaries are defined by business capabilities. Cross-domain dependencies must be asynchronous wherever feasible.
- **Production-Ready Baseline**: Every deployed unit must immediately expose health checks, trace context, and baseline RED metrics upon inception.

## 3. Strategic Architecture

The Scnehaux Super Platform is partitioned into the following primary Capability Domains. These domains dictate the bounded contexts for all downstream software architecture (PADs and SADs).

### 3.1 Identity Management (Platform Foundation)
- **Authentication & Federation**: Single Sign-On (SSO), MFA enforcement, and external IdP brokering.
- **Tenant Governance**: Multi-tenant isolation enforcement and lifecycle management.
- **Session Operations**: Token issuance and global revocation capabilities.

### 3.2 Workforce Management (Core Domain)
- **Employee Lifecycle**: Onboarding, offboarding, and profile state transitions.
- **Organizational Structure**: Position management and hierarchy definitions.

### 3.3 Compensation Processing (Financial Domain)
- **Compensation Modeling**: Salary structuring and benefits calculation.
- **Tax & Compliance Engine**: Regulatory deduction modeling.
- **Disbursement Orchestration**: Financial gateway integration.

### 3.4 Operational Velocity (Work Management)
- **Time & Attendance**: Real-time tracking and leave processing.
- **Capacity Allocation**: Project resourcing and rostering.

### 3.5 Talent & Growth Management
- **Recruitment**: Sourcing and hiring pipelines.
- **Performance Evaluation**: Goal tracking and feedback loops.

## 4. Cross-Cutting Standards

### Exception Governance
Any deviation from the mandated capability boundaries (e.g., merging two distinct capabilities into a single database for performance reasons) requires formal approval.
- **Requirement**: Must submit an Architecture Decision Record (ADR).
- **Approval Gate**: Requires explicit sign-off from the Architecture Review Board (ARB).

### Evolution Strategy
- **Current State**: Monolithic capability grouping.
- **Target State**: Event-Driven Capability choreography. As capabilities mature, synchronous REST calls across domains will transition to asynchronous event streams to maximize decoupling and resilience.

### Metric Baselines
The business architecture mandates the following macro-level service level agreements across all capability domains:
- **Availability**: All tier-0 capability endpoints must achieve >=99.95% availability measured over a rolling 30-day window.
- **Fault Isolation**: Failure in one capability domain must result in zero degraded availability for unrelated capability domains.

## 5. Decision Log

| ID | Decision | Status | Rationale |
| :--- | :--- | :--- | :--- |
| **TOG-01** | TOGAF Alignment | Approved | Aligns with TOGAF Phase B (Business Architecture) requirements. |
