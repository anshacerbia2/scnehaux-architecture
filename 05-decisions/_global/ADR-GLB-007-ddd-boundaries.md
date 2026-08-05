---
doc_meta:
  id: ADR-GLB-007
  title: ADR-GLB-007 Standardizing Domain-Driven Design Boundaries and Data Ownership
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
---

# ADR-GLB-007: Adopting Domain-Driven Design (DDD) Aggregates, Single-Transaction Mutators, and Formal Domain Data Ownership for HRIS Core Platforms

---

## 1. Title

Adopting Domain-Driven Design (DDD) Aggregates, Single-Transaction Mutators, and Formal Domain Data Ownership for HRIS Core Platforms

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

The Scnehaux HRIS ecosystem handles overlapping business domains (Identity, Core HR, Payroll, Time & Attendance). Historically, the lack of defined domain boundaries and clear data ownership led to coupled database schemas, where payroll scripts modified employee contracts directly, and attendance modules queried session data without interface validation. This coupling causes transactional locks, makes schema migrations difficult, and results in ambiguous responsibility during compliance audits. We need to enforce domain boundaries and designate accountable data owners.

## 4. Decision Drivers

Adopting DDD aggregate boundaries and the single-transaction constraint guarantees data integrity and prevents distributed locks. Encapsulating domain logic inside Aggregate Roots ensures business rules are protected. Mapping data domain owners removes operational ambiguity, ensuring schemas, security policies, and data lifecycle rules are managed by the teams with the appropriate domain expertise.

## 5. Decision

We officially establish Domain-Driven Design (DDD) aggregate constraints and assign formal Domain Data Owners:

1.  **Aggregate Boundaries**: Mutating database state must proceed exclusively through the designated Aggregate Root. Downstream services and internal modules are prohibited from holding reference structures to child entities within the aggregate.
2.  **Single-Transaction Constraint**: A database transaction block must mutate exactly one Aggregate Root instance. Cross-aggregate updates must be decoupled using asynchronous domain events.
3.  **Domain Data Owner Mapping**:
    - _Identity & Access Management (IAM)_: Governed by the Security & IAM Engineering Team.
    - _Core Human Resources (HR)_: Governed by the Core HR Systems Team.
    - _Payroll & Compensation_: Governed by the Payroll Engineering Team.
    - _Time & Attendance_: Governed by the Workforce Operations Team.
4.  **Owner Accountabilities**: Owners must approve all schema migrations, define API contracts, and verify data classification/retention policies.

## 6. Consequences

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

### Operational

- Codified in the Enterprise Domain Modeling Standard (`STD-GLB-008`) and the Data Classification Standard (`STD-GLB-006`).
- Entity relations between Bounded Contexts must be modeled strictly using aggregate IDs (foreign keys) rather than object reference schemas.

## 7. Compliance Impact

### Related Standards

- Enterprise Domain Modeling Standard (STD-GLB-008)
- Enterprise Data Classification, Governance & Retention Standard (STD-GLB-006)
- Enterprise Database & Persistence Strategy Standard (STD-GLB-002)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Shared Database Architectures (Direct Cross-Domain Joins)

- **Pros**: Simplifies reporting queries; eliminates API round-trip times.
- **Cons**: Direct coupling of schemas makes it impossible to modify or migrate a domain database without breaking other systems; database locks propagate across domains.
- **Why Rejected**: Creates a monolithic database dependency that blocks scaling, limits development velocity, and violates domain boundary rules.

### Alternative B: Direct Multi-Aggregate Transactions

- **Pros**: Ensures instant ACID consistency across multiple tables in a single write operation.
- **Cons**: Increases lock durations, causes transaction deadlocks under high load, and tightly couples aggregate lifecycles.
- **Why Rejected**: Prevents horizontal scaling of database write operations and causes performance degradation during concurrent updates.
