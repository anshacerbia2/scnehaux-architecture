---
doc_meta:
  id: ADR-GLB-002
  title: ADR-GLB-002 Enterprise PostgreSQL Row-Level Security for Isolation
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# ADR-GLB-002: Enterprise PostgreSQL Row-Level Security for Isolation

---

## 1. Title
Mandating PostgreSQL Row-Level Security (RLS) as the Primary Multi-Tenant Isolation Standard

## 2. Status
Accepted

## 3. Context
The Scnehaux ecosystem operates under a multi-tenant business model. Strong isolation between tenant data is a critical enterprise requirement across all systems (IAM, HRIS, Payroll, Finance). Historically, multi-tenant isolation relied on application-layer filtering (e.g., developers remembering to append `WHERE tenant_id = ?` to every SQL statement). This approach is highly fragile and presents an unacceptable risk of cross-tenant data leakage.

## 4. Decision
We officially mandate **PostgreSQL Row-Level Security (RLS)** as the primary multi-tenant data isolation boundary for all relational databases inside the Scnehaux platform. 

For every table containing tenant-specific data, RLS must be enabled. The application's database connection pool must dynamically bind the active tenant identifier (via a session configuration variable like `app.current_tenant`) at the start of every transaction before executing SQL operations.

## 5. Rationale
By moving the tenant isolation boundary from the application layer to the database engine itself, we implement a **Defense-in-Depth** security model. A developer's accidental omission of a filter clause in application code will no longer result in data exposure. The database engine itself will silently and securely filter all read/write operations based on the cryptographically validated transaction context.

## 6. Alternatives Considered

### Alternative A: Application-Layer Custom Queries (e.g., ORM Filters)
*   **Pros**: Straightforward to set up in code, database engine agnostic.
*   **Cons**: Relies entirely on developer compliance. Highly vulnerable to raw SQL bypasses, analytical queries, and schema migrations.
*   **Why Rejected**: Fails to provide a hardened, verifiable security boundary at the persistence tier.

### Alternative B: Physical Database-Per-Tenant Isolation
*   **Pros**: Perfect hardware-level isolation.
*   **Cons**: Extremely expensive infrastructure footprints, slow schema migrations (running migrations across thousands of databases), and massive connection pool exhaustion.
*   **Why Rejected**: Unviable due to high operational costs and scaling constraints for thousands of small tenants.

## 7. Consequences

### Positive
- **Hardened Security Boundary**: Prevents cross-tenant data leaks at the engine level. An empty or null tenant context evaluates to false, securely returning zero rows by default.
- **Simplified Application Code**: Developers do not need to manually write tenant filter logic in standard business operations.
- **Verifiable Compliance**: Easily audited for compliance standards (SOC 2, ISO 27001) by querying PostgreSQL catalog tables to verify RLS is active.

### Negative
- **Dynamic Connection Binding**: Requires connection pools to set the active context via `SET LOCAL app.current_tenant = '...'` before every transaction, introducing a minor query overhead.
- **Bypass Requirements**: Schema migrations and administrative operations require specialized database credentials to bypass RLS policies securely.

### Tradeoffs
- We trade minor database-level execution overhead for ironclad tenant isolation guarantees.

### Operational Impact
- Requires the database migration system (Atlas) to support RLS DDL policy generation and testing.

### Security Impact
- Provides zero-trust data protection at the persistence layer, satisfying top-tier enterprise compliance requirements.

### Scalability Impact
- Mandates indexing on the `tenant_id` column of all tenant-scoped tables to prevent query planning performance degradation during policy checks.

## 8. Risks
- **Performance Degradation**: Nested queries or complex joins on tables with RLS can lead to bad database execution plans.
  - *Mitigation*: Solved by enforcing composite indexes (`tenant_id`, `id`) on all primary keys and conducting routine explain plan analyses.

## 9. Implementation Notes
- Enforced on all tables in `scnehaux-iam` using SQLC migrations:
  ```sql
  ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
  CREATE POLICY tenant_isolation_policy ON accounts
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
  ```

## 10. Related Documents
- [Enterprise Data Architecture Strategy (EAD-002)](file:///d:/Ansha/architecture-description/scnehaux-architecture/01-enterprise/EAD-002-Data-Architecture.md)
- [Platform Identity Architecture Document (DOC-P001)](file:///d:/Ansha/architecture-description/scnehaux-architecture/02-platform/identity-platform/identity-platform.pad.md)
