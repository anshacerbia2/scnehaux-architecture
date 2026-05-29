---
doc_meta:
  id: ADR-GLB-004
  title: ADR-GLB-004 Atlas Schema Governance for Deterministic Data Migrations
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# ADR-GLB-004: Atlas Schema Governance for Deterministic Data Migrations

---

## 1. Title
Standardizing on Atlas Declarative schema Management for Safe and Traceable Database Evolutions

## 2. Status
Accepted

## 3. Context
The Scnehaux enterprise operates high-availability relational databases (PostgreSQL) supporting critical, high-transaction workloads across multiple domains (IAM, HRIS, Finance). Safe database schema evolution is vital to prevent outages. Historically, manual SQL migration scripts led to "Schema Drift" (where the database state in production diverged from source control), and developers lacked automated dry-run testing, causing unexpected table locks during deployments.

## 4. Decision
We officially establish **Atlas** (HCL-based declarative management tool) as the enterprise standard for database schema governance, migration testing, and deployment orchestration across the Scnehaux ecosystem. 

All database schemas must be declaratively defined in a `schema.hcl` file under source control. Migration scripts must be deterministically generated using the command `atlas migrate diff`. Direct execution of manual, non-audited DDL scripts in production is strictly prohibited.

## 5. Rationale
Adopting a declarative schema model allows us to establish **Deterministic Infrastructure as Code** at the database layer. Atlas automatically calculates the exact SQL diff required to transition the target database to the intended HCL schema state. By running Atlas in our CI/CD pipelines, we run concurrency-aware dry runs and safety checks before DDL scripts are applied, ensuring that destructive operations (e.g., dropping active columns or running un-indexed queries) are blocked.

## 6. Alternatives Considered

### Alternative A: Imperative SQL Migration Frameworks (e.g., Liquibase, Flyway)
*   **Pros**: Highly mature, supports multiple SQL-based migration formats.
*   **Cons**: Relies on developers writing the exact "Up" and "Down" SQL statements manually. Does not perform declarative state diffing and lacks native HCL validation tools.
*   **Why Rejected**: Does not solve schema drift at source control. Fails to provide automated destructive validation checks out of the box.

### Alternative B: Manual SQL Scripting & Execution
*   **Pros**: Direct control over exact commands run by the DBA.
*   **Cons**: Extremely error-prone, untraceable, and leads to massive environment drift (production database states diverging from dev).
*   **Why Rejected**: Unacceptable risk of production downtime due to human error.

## 7. Consequences

### Positive
- **Zero Schema Drift**: The database state in Git (`schema.hcl`) matches the target database state exactly.
- **Safety Gatekeeping**: Destructive modifications are automatically detected and blocked by the CI/CD pipeline, requiring explicit ARB waiver and admin override.
- **Transactional Migrations**: Fails-safe; Atlas rolls back failed migration runs automatically if supported by the engine.

### Negative
- **Tooling Coupling**: Introduces a dependency on the Atlas CLI.
- **HCL Syntax Onboarding**: Developers must learn the HCL (HashiCorp Configuration Language) syntax to write declarative table definitions.

### Tradeoffs
- We trade minor developer onboarding friction (learning HCL) for ironclad, automated safety guarantees and deterministic environments.

### Operational Impact
- The CD pipeline integrates the execution command `atlas migrate apply` at the deployment gate.
- Environment parity is verified periodically by running `atlas schema inspect`.

### Security Impact
- Credentials used by Atlas must be securely injected via short-lived tokens or KMS roles, preventing hardcoded connection strings in code.

### Scalability Impact
- Leverages Atlas's built-in locking engine, ensuring that migration runs do not cause write locks or service timeouts during high-traffic operations.

## 8. Risks
- **Destructive DDL Lockups**: Adding columns with default values or creating un-indexed foreign keys on large tables (millions of rows) can lock tables.
  - *Mitigation*: Solved by enabling Atlas concurrency-aware linting in CI/CD, which detects table locks and forces the use of concurrent indexes (`CREATE INDEX CONCURRENTLY`).

## 9. Implementation Notes
- Developers execute DDL generation locally:
  ```bash
  atlas migrate diff <migration_name> \
    --dir "file://migrations" \
    --to "file://schema.hcl" \
    --dev-url "docker://postgres/16"
  ```
- Pipeline runs `atlas migrate lint` on every Pull Request to enforce paved road conventions.

## 10. Related Documents
- [Enterprise Data Architecture Strategy (EAD-002)](file:///d:/Ansha/architecture-description/scnehaux-architecture/01-enterprise/EAD-002-Data-Architecture.md)
- [Scnehaux IAM Software Architecture Document (SAD-001)](file:///d:/Ansha/architecture-description/scnehaux-architecture/03-applications/scnehaux-iam/scnehaux-iam.sad.md)
