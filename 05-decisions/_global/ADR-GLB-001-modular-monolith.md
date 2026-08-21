---
doc_meta:
  id: ADR-GLB-001
  title: ADR-GLB-001 Enterprise Adoption of Modular Monolith Architecture
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  last_updated: 2026-08-12
  created_by: Enterprise Architect
---

# ADR-GLB-001: Standardizing on the Modular Monolith Pattern as the Default Architecture for Core Platforms

---

## 1. Title

Standardizing on the Modular Monolith Pattern as the Default Architecture for Core Platforms

## 2. Status

| Date       | Status            | ADR Type     | Reviewers                        | Approver                        |
| ---------- | ----------------- | ------------ | -------------------------------- | ------------------------------- |
| 2026-05-01 | accepted          | foundational | Architecture Review Board        | Enterprise Architect            |
| 2026-08-12 | accepted, amended | foundational | Architecture, Platform, Identity | Architecture Authority          |

### Amendment Record

**2026-08-12 — scope correction.** The original decision named the Identity Provider and a Ledger system as mandatory modular monoliths. ADR-IAM-001 adopts an external identity kernel that runs the runtime its vendor requires, and no Ledger system exists anywhere in the enterprise landscape. Section 5 is amended to scope the mandate to Scnehaux-owned cohesive transactional and control applications and to name the categories that fall outside it. Consequences asserting Kubernetes as the deployment substrate, an unmeasured extraction duration, and application to the retired `scnehaux-iam` monorepo are corrected in the same amendment. Package layout, previously illustrated here with modules from that retired system, is now governed by ADR-GLB-008.

This decision is amended rather than superseded because its direction is unchanged: prefer a cohesive modular application over premature distribution. Only the breadth of the mandate and factual claims that ceased to be true are corrected. Sections 3, 4, and the Positive, Negative, and Tradeoffs consequences are retained as the original reasoning of record.

## 3. Context

Across the Scnehaux ecosystem, balancing deployment simplicity with domain isolation is critical. Early-stage systems and core platforms face massive operational and infrastructure overhead if microservices are adopted prematurely. We need a model that guarantees compile-time domain boundary enforcement without the network latency, distributed transaction complexity, and massive DevOps friction of multi-repository deployments.

## 4. Decision Drivers

Adopting the modular monolith allows us to scale development velocity and simplify deployments during the critical bootstrapping phase. By keeping all core code inside a single repository with native Go packaging, we enforce strict domain boundaries at the compiler level. This prevents structural rot while maintaining a zero-waste, sub-200ms API latency profile by eliminating inter-service network hops.

## 5. Decision

We establish the **Modular Monolith** pattern as the default initial realization for **Scnehaux-owned cohesive transactional and control applications**, where the relevant bounded contexts can safely share ownership, lifecycle, reliability profile, and runtime.

The default does **not** mandate one binary, one database, or one deployment model for every enterprise capability. The following are outside this mandate:

- adopted vendor kernels, including the approved identity kernel, which run the runtime their vendor requires;
- managed databases, brokers, caches, key-management services, object storage, and other commodity substrate;
- build-time libraries, UI packages, schemas, and generated artifacts;
- data, analytical, AI, batch, and integration workloads whose runtime profile differs materially;
- components deployed independently on evidence of lifecycle, scale, fault isolation, security, residency, compliance, or ownership.

Within a Scnehaux-owned modular application, logical domain boundaries remain explicit even when modules share a process or a database. Cross-module access follows declared contracts, and ownership leakage is prohibited. Package layout and machine-enforced layer separation are governed by ADR-GLB-008.

Extraction from a modular application requires evidence rather than preference. A SAD or a replacement decision documents the independent lifecycle, scaling, reliability, security, operational, or organisational reason for the extraction.

## 6. Consequences

### Positive

- **High Development Velocity**: Single repository deployment simplifies CI/CD pipelines, database migration runs, and local dev setups.
- **Sub-millisecond Local Calls**: Direct in-memory method invocation replaces slower gRPC or REST calls for internal operations.
- **compiler Boundary Safeguards**: Enforced via Go internal package boundaries, ensuring no domain cross-pollution.
- **Future Extraction Path**: Because database tables and domains are kept strictly separate, a module can be extracted into an independently deployed system without redesigning its aggregates or migrating its schema. Extraction cost is a packaging and wiring change, and is not estimated here.

### Negative

- **Single Deployable Unit**: A crash in a single module (e.g., panic in thread) brings down the entire application.
- **Deployment Coordination**: Teams must coordinate releases on the same monolithic codebase repository.

### Tradeoffs

- We trade absolute deployment independence for rapid velocity, simpler transactional boundaries, and low infrastructure footprint.

### Operational Impact

- Simplifies operations: one deployment unit, one migration path, and one telemetry configuration per application.

### Security Impact

- Restricts security boundary tracking to a single execution context, simplifying the audit of cryptographic signing key boundaries.

### Scalability Impact

- Scaling is achieved by running identical replicas of the application. The orchestration mechanism is a runtime decision governed by EAD-005 and is not fixed by this ADR.

### Operational

- Applied to Scnehaux-owned control-plane applications. The former `scnehaux-iam` monorepo is retired under ADR-IAM-001 and is no longer a reference implementation.
- Database access within each module must use independent, non-overlapping tables.

## 7. Compliance Impact

### Related Standards

- [Technology Architecture Strategy (EAD-005)](../../01-enterprise/EAD-005-enterprise-platform-architecture.md)
- [Scnehaux Identity Runtime (SAD-001)](../../04-system/scnehaux-iam/scnehaux-identity-runtime.sad.md)
- [ADR-GLB-008 Go Project Structure and Layer Enforcement](ADR-GLB-008-go-project-structure.md) — governs package layout and layer enforcement inside a modular application.
- [ADR-GLB-010 Application Mechanics In-Process](ADR-GLB-010-application-mechanics-in-process.md) — governs where cross-cutting mechanics are placed relative to the application boundary.
- [ADR-IAM-001 Adopt Keycloak Identity Kernel](../identity-access-platform/ADR-IAM-001-adopt-keycloak-identity-kernel.md) — the adopted vendor kernel excluded by Section 5.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Microservices-First Architecture

- **Pros**: Extreme scalability, independent deployments per service.
- **Cons**: Introduces distributed transactions (2PC/Sagas), complex gRPC orchestrations, network boundary latency, and high Kubernetes configuration overhead.
- **Why Rejected**: Introduces massive premature complexity and infrastructure costs before the domain boundaries have fully stabilized.

### Alternative B: Legacy Monolith (Big Ball of Mud)

- **Pros**: Fast to write initially, zero architectural boundary friction.
- **Cons**: Direct imports across all database tables and logic, making it impossible to separate domains or scale teams in the future.
- **Why Rejected**: Leads to catastrophic domain contamination and code rot within 12 months.
