---
doc_meta:
  id: ADR-GLB-001
  title: ADR-GLB-001 Enterprise Adoption of Modular Monolith Architecture
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
---

# ADR-GLB-001: Standardizing on the Modular Monolith Pattern as the Default Architecture for Core Platforms

---

## 1. Title

Standardizing on the Modular Monolith Pattern as the Default Architecture for Core Platforms

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |
| 2026-08-18 | accepted | foundational | Architecture Review Board | Enterprise Architect |

**Amended 2026-08-18: §5.1 states the scope this decision always had.** It governs the
internal structure of one system and not the enterprise topology, which `EAD-001` and
`EAD-002` own. The pattern, its drivers, and its consequences are unchanged.

## 3. Context

Across the Scnehaux ecosystem, balancing deployment simplicity with domain isolation is critical. Early-stage systems and core platforms face massive operational and infrastructure overhead if microservices are adopted prematurely. We need a model that guarantees compile-time domain boundary enforcement without the network latency, distributed transaction complexity, and massive DevOps friction of multi-repository deployments.

## 4. Decision Drivers

Adopting the modular monolith allows us to scale development velocity and simplify deployments during the critical bootstrapping phase. By keeping all core code inside a single repository with native Go packaging, we enforce strict domain boundaries at the compiler level. This prevents structural rot while maintaining a zero-waste, sub-200ms API latency profile by eliminating inter-service network hops.

## 5. Decision

We officially establish the **Modular Monolith** pattern as the default, mandatory architecture for all new core platform systems at Scnehaux, including the Identity Provider (IAM) and the Ledger system.

Core modules (e.g., `internal/auth`, `internal/tenant`, `internal/token` in IAM) must compile and build into a single execution binary, while maintaining complete logical separation (no direct cross-package structural coupling or database table joining).

### 5.1 Scope: Within a System, Never Across Systems

_Amended 2026-08-18._

This decision governs the **internal** structure of one system: one bounded context, one deployable, modules separated at compile time. It does not govern the enterprise topology.

`EAD-001 §7` rejects the modular monolith as an **enterprise** pattern, and `EAD-002 §6.2` requires every system to deploy on its own pipeline without a coordinated enterprise release. Those statements and this decision are compatible, and read as contradictory only when the word "monolith" is applied at both scales at once.

| Scale | Rule | Owner |
| :-- | :-- | :-- |
| Inside one system | One deployable, modules enforced by the compiler | This decision |
| Across systems | Independently deployable, acyclic, contract-mediated | `EAD-001`, `EAD-002` |

A deployable containing two bounded contexts is therefore prohibited by `STD-GLB-BE-001` Rule 1, and splitting one bounded context across two deployables is prohibited by this decision. The estate consequence is explicit: the Identity Platform capability is realised by more than one deployable — an identity kernel, a control service, and an experience — because those are separate systems with separate release cadences, and each of them individually is a modular monolith.

The original text named "the Identity Provider (IAM)" as a single system. That was accurate when one repository held the whole capability. It is read today as naming whichever system is under discussion, not as a requirement that the capability collapse back into one deployable.

## 6. Consequences

### Positive

- **High Development Velocity**: Single repository deployment simplifies CI/CD pipelines, database migration runs, and local dev setups.
- **Sub-millisecond Local Calls**: Direct in-memory method invocation replaces slower gRPC or REST calls for internal operations.
- **compiler Boundary Safeguards**: Enforced via Go internal package boundaries, ensuring no domain cross-pollution.
- **Future Extraction Path**: Because database tables and domains are kept strictly separate, any module can be extracted into an independent microservice in less than 48 hours if high-scale needs arise.

### Negative

- **Single Deployable Unit**: A crash in a single module (e.g., panic in thread) brings down the entire application.
- **Deployment Coordination**: Teams must coordinate releases on the same monolithic codebase repository.

### Tradeoffs

- We trade absolute deployment independence for rapid velocity, simpler transactional boundaries, and low infrastructure footprint.

### Operational Impact

- Drastically simplifies operations: requires only 1 database connection pool, 1 set of Kubernetes pods, and unified OpenTelemetry configuration.

### Security Impact

- Restricts security boundary tracking to a single execution context, simplifying the audit of cryptographic signing key boundaries.

### Scalability Impact

- Standardized scaling is achieved by horizontally scaling identical replicas of the monolith using Kubernetes HPAs.

### Operational

- Applied in the implementation of the `scnehaux-iam` project monorepo in Go.
- Database access within each module must use independent, non-overlapping tables.

## 7. Compliance Impact

### Related Standards

- [Technology Architecture Strategy (EAD-005)](../../01-enterprise/EAD-005-enterprise-platform-architecture.md)
- [Scnehaux IAM System Architecture Document (SAD-001)](../../04-system/scnehaux-iam/scnehaux-iam.sad.md)

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
