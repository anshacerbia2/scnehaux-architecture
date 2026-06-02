---
doc_meta:
  id: ADR-GLB-001
  title: ADR-GLB-001 Enterprise Adoption of Modular Monolith Architecture
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-GLB-001: Standardizing on the Modular Monolith Pattern as the Default Architecture for Core Platforms

---

## 1. Title
Standardizing on the Modular Monolith Pattern as the Default Architecture for Core Platforms

## 2. Status
| Date | Status | ADR Type | Reviewers | Approver |
|---|---|---|---|---|
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |


## 3. Context
Across the Scnehaux ecosystem, balancing deployment simplicity with domain isolation is critical. Early-stage systems and core platforms face massive operational and infrastructure overhead if microservices are adopted prematurely. We need a model that guarantees compile-time domain boundary enforcement without the network latency, distributed transaction complexity, and massive DevOps friction of multi-repository deployments.

## 4. Decision Drivers
Adopting the modular monolith allows us to scale development velocity and simplify deployments during the critical bootstrapping phase. By keeping all core code inside a single repository with native Go packaging, we enforce strict domain boundaries at the compiler level. This prevents structural rot while maintaining a zero-waste, sub-200ms API latency profile by eliminating inter-service network hops.

## 5. Decision
We officially establish the **Modular Monolith** pattern as the default, mandatory architecture for all new core platform systems at Scnehaux, including the Identity Provider (IAM) and the Ledger system. 

Core modules (e.g., `internal/auth`, `internal/tenant`, `internal/token` in IAM) must compile and build into a single execution binary, while maintaining complete logical separation (no direct cross-package structural coupling or database table joining).

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
- [Technology Architecture Strategy (EAD-004)](..\..\01-enterprise\EAD-004-technology-architecture.md)
- [Scnehaux IAM Software Architecture Document (SAD-001)](..\..\04-application\scnehaux-iam\scnehaux-iam.sad.md)

### Compliance Status
Compliant.

### Required Waivers
None.

## 8. Alternatives Considered
### Alternative A: Microservices-First Architecture
*   **Pros**: Extreme scalability, independent deployments per service.
*   **Cons**: Introduces distributed transactions (2PC/Sagas), complex gRPC orchestrations, network boundary latency, and high Kubernetes configuration overhead.
*   **Why Rejected**: Introduces massive premature complexity and infrastructure costs before the domain boundaries have fully stabilized.

### Alternative B: Legacy Monolith (Big Ball of Mud)
*   **Pros**: Fast to write initially, zero architectural boundary friction.
*   **Cons**: Direct imports across all database tables and logic, making it impossible to separate domains or scale teams in the future.
*   **Why Rejected**: Leads to catastrophic domain contamination and code rot within 12 months.
