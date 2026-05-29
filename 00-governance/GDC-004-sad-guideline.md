---
doc_meta:
  id: GDC-004
  title: Software Architecture Document (SAD) Guideline
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Software Architecture Document (SAD) Guideline

## 1. Context & Scope

This guideline defines the mandatory structure, metadata schema, and section requirements for **Software Architecture Documents (SAD)** within the Scnehaux architecture registry. 

SADs represent the physical execution containment, technology stacks, container topologies, and operational resilience of deployable applications (e.g. backend service monoliths, frontend/client applications like web SPAs, mobile apps, or desktop clients).

---

## 2. Policy Framework

### 2.1 Document Template Schema

All SAD files must use the suffix `.sad.md` (e.g. `scnehaux-iam.sad.md`) and must contain the following structural sections in the exact order shown:

#### 2.1.1 YAML Metadata Header
Every SAD must begin with a YAML frontmatter block containing these fields:
```yaml
---
doc_meta:
  id: DOC-S-XXX                       # Unique software system ID
  title: [Application Title]          # Descriptive title of the application
  owner: [Principal Engineer/Role]    # Authoritative system owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: internal            # public | internal | restricted
  parent_pad: DOC-P-XXX               # Referencing the Parent Platform Capability PAD ID
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
---
```

#### 2.1.2 Section 1: Context
- **Objective**: Define the immediate upstream and downstream dependencies of this application, and its specific system boundary.
- **Requirement**: Must explicitly link to the governing platform capability PAD.

#### 2.1.3 Section 2: Solution Architecture
- **Objective**: Concrete C2 container diagrams detailing the physical technology stack (e.g., Go, Postgres, Redis, React, Webpack).
- **Requirement**: Must illustrate all physical containers, network zones, and persistence layers.

#### 2.1.4 Section 3: Deployment & Topology
- **Objective**: Document the network boundaries, scaling assumptions, and physical or cloud hosting environments (e.g., Kubernetes namespaces, CDNs).
- **Requirement**: Must define resource limits (CPU/Memory) and scaling triggers.

#### 2.1.5 Section 4: Runtime Flows
- **Objective**: Detail request lifecycles, asynchronous event publishing, and degradation paths.
- **Requirement**: Must contain sequence diagrams for critical operations (e.g., authentication handshake, payment authorization).

#### 2.1.6 Section 5: Resilience & Failure Modes
- **Objective**: Identify Single Points of Failure (SPOFs), cascading failure mitigations, fallback strategies, and the exact **Blast Radius**.
- **Requirement**: Must document circuit breaker configurations, fallback states, and queue isolation limits.

#### 2.1.7 Section 6: Observability
- **Objective**: Mandate the specific Service Level Indicators (SLIs), Service Level Objectives (SLOs), alert thresholds, and distributed tracing spans.
- **Requirement**: Must align with global observability trace propagation and log output standards.

#### 2.1.8 Section 7: Security Considerations
- **Objective**: Detail system-level threat mitigations, input validation, secrets management, and data classification boundaries.
- **Requirement**: Must document Row-Level Security (RLS) policies, token signing rotation, and encryption keys.

#### 2.1.9 Conditional Sections (As Required)
- **Assumptions**: Document external operational assumptions.
- **Alternatives Considered**: Document technical trade-offs of the chosen deployment architecture.
- **Compatibility Strategy**: Detail schema migration or API versioning compatibility rules.
- **Data Classification**: Detail sensitivity levels of data stored/processed (PII, confidential).

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Physical Containment Audit**: The linter will verify that SADs contain technology-specific information. Unlike PADs, SADs must specify the concrete database engines, cache stores, and container topologies.
2. **Blast Radius Analysis**: Under the Resilience section, every major failure mode must specify the *Blast Radius* (e.g., "Single User Session", "Full Tenant Isolation", "Entire Platform Outage") to pass the review gate.

## 4. Severity & Exceptions

### 4.1 Exception Waiver Protocol
- Deviations from Software Architecture requirements or schemas require an approved project Exception ADR and ARB waiver sign-off.
- Approved waivers have a maximum validity of 365 days.
