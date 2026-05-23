---
doc_meta:
  id: ADR-E011
  title: ADR-E011 Standardizing Domain-Driven Design Boundaries and Data Ownership
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# ADR-E011: Standardizing Domain-Driven Design Boundaries and Data Ownership

---

## 1. Title
Adopting Domain-Driven Design (DDD) Aggregates, Single-Transaction Mutators, and Formal Domain Data Ownership for HRIS Core Platforms

## 2. Status
Accepted

## 3. Context
The Scnehaux HRIS ecosystem handles overlapping business domains (Identity, Core HR, Payroll, Time & Attendance). Historically, the lack of defined domain boundaries and clear data ownership led to coupled database schemas, where payroll scripts modified employee contracts directly, and attendance modules queried session data without interface validation. This coupling causes transactional locks, makes schema migrations difficult, and results in ambiguous responsibility during compliance audits. We need to enforce domain boundaries and designate accountable data owners.

## 4. Decision
We officially establish Domain-Driven Design (DDD) aggregate constraints and assign formal Domain Data Owners:
1.  **Aggregate Boundaries**: Mutating database state must proceed exclusively through the designated Aggregate Root. Downstream services and internal modules are prohibited from holding reference structures to child entities within the aggregate.
2.  **Single-Transaction Constraint**: A database transaction block must mutate exactly one Aggregate Root instance. Cross-aggregate updates must be decoupled using asynchronous domain events.
3.  **Domain Data Owner Mapping**:
    - *Identity & Access Management (IAM)*: Governed by the Security & IAM Engineering Team.
    - *Core Human Resources (HR)*: Governed by the Core HR Systems Team.
    - *Payroll & Compensation*: Governed by the Payroll Engineering Team.
    - *Time & Attendance*: Governed by the Workforce Operations Team.
4.  **Owner Accountabilities**: Owners must approve all schema migrations, define API contracts, and verify data classification/retention policies.

## 5. Rationale
Adopting DDD aggregate boundaries and the single-transaction constraint guarantees data integrity and prevents distributed locks. Encapsulating domain logic inside Aggregate Roots ensures business rules are protected. Mapping data domain owners removes operational ambiguity, ensuring schemas, security policies, and data lifecycle rules are managed by the teams with the appropriate domain expertise.

## 6. Alternatives Considered

### Alternative A: Shared Database Architectures (Direct Cross-Domain Joins)
*   **Pros**: Simplifies reporting queries; eliminates API round-trip times.
*   **Cons**: Direct coupling of schemas makes it impossible to modify or migrate a domain database without breaking other systems; database locks propagate across domains.
*   **Why Rejected**: Creates a monolithic database dependency that blocks scaling, limits development velocity, and violates domain boundary rules.

### Alternative B: Direct Multi-Aggregate Transactions
*   **Pros**: Ensures instant ACID consistency across multiple tables in a single write operation.
*   **Cons**: Increases lock durations, causes transaction deadlocks under high load, and tightly couples aggregate lifecycles.
*   **Why Rejected**: Prevents horizontal scaling of database write operations and causes performance degradation during concurrent updates.

## 7. Consequences

### Positive
- **High Schema Agility**: Teams modify their domain schemas independently without impacting other systems, provided API contracts are preserved.
- **Improved Performance**: Restricting transactions to single aggregates reduces lock contention.
- **Traceable Accountability**: Domain owners serve as the single authority for database permissions and compliance audits.

### Negative
- **Asynchronous Coordination**: Cross-domain workflows require event-driven patterns, introducing eventual consistency profiles.
- **Reporting Complexity**: Cross-domain reports cannot rely on direct database joins; they must consume API endpoints or aggregate data in analytical stores.

### Tradeoffs
- We trade immediate, multi-table database consistency for schema flexibility, improved write throughput, and clear organizational ownership boundaries.

### Operational Impact
- Reduces debugging effort: database locks are isolated to single aggregates. Requires monitoring transactional outbox processing latency.

### Security Impact
- Enforces data isolation. Sensitive payroll records cannot be queried or updated by unauthorized workforce management modules.

### Scalability Impact
- Facilitates database sharding or partitioning, as data domains operate on independent, self-contained schemas.

## 8. Risks
- **Data Synchronization Delays**: Asynchronous updates can lead to temporary discrepancies across domains (e.g. an employee is terminated in HR but active in IAM for a brief duration).
  - *Mitigation*: The system monitors transactional outbox processing delay, triggering alerts if processing exceeds `5 seconds`.

## 9. Implementation Notes
- Codified in the Enterprise Domain Modeling Standard (`STD-E018`) and the Data Classification Standard (`STD-E017`).
- Entity relations between Bounded Contexts must be modeled strictly using aggregate IDs (foreign keys) rather than object reference schemas.

## 10. Related Documents
- [Enterprise Domain Modeling Standard (STD-E018)](file:///d:/Ansha/architecture-description/scnehaux-architecture/05-standards/STD-E018-domain-modeling-standard.md)
- [Enterprise Data Classification, Governance & Retention Standard (STD-E017)](file:///d:/Ansha/architecture-description/scnehaux-architecture/05-standards/STD-E017-data-classification-governance-retention-standard.md)
- [Enterprise Database & Persistence Strategy Standard (STD-E002)](file:///d:/Ansha/architecture-description/scnehaux-architecture/05-standards/STD-E002-database-standard.md)
