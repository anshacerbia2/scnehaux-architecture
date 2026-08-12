---
doc_meta:
  id: ADR-GLB-002
  title: ADR-GLB-002 Enterprise PostgreSQL Row-Level Security for Isolation
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  last_updated: 2026-08-12
  created_by: Enterprise Architect
---

# ADR-GLB-002: Mandating PostgreSQL Row-Level Security (RLS) as the Primary Multi-Tenant Isolation Standard

---

## 1. Title

Mandating PostgreSQL Row-Level Security (RLS) as the Primary Multi-Tenant Isolation Standard

## 2. Status

| Date       | Status            | ADR Type     | Reviewers                      | Approver               |
| ---------- | ----------------- | ------------ | ------------------------------ | ---------------------- |
| 2026-05-01 | accepted          | foundational | Architecture Review Board      | Enterprise Architect   |
| 2026-08-12 | accepted, amended | foundational | Architecture, Security, Data   | Architecture Authority |

### Amendment Record

**2026-08-12 — scope correction and mechanism completion.** Two defects were corrected.

The original decision applied to "all relational databases inside the Scnehaux platform". ADR-IAM-001 adopts an identity kernel whose persistence is vendor-managed and is modified only through its supported upgrade lifecycle, so the mandate cannot apply there. Section 5 now scopes the requirement to Scnehaux-owned tenant-scoped relational authority tables and names the categories outside it.

More seriously, the original decision mandated RLS without the controls that make it effective. `FORCE ROW LEVEL SECURITY` was never required, and the runtime role was never prohibited from owning the protected tables. PostgreSQL does not apply row-level policies to a table's owner unless `FORCE` is set, so an implementation that satisfied this ADR completely could enable RLS and have it apply to nothing. Section 5 now carries the full mechanism, and the audit method in Section 6 is corrected: it previously verified only that RLS had been enabled, which returns a passing result for an inert control.

This decision is amended rather than superseded because its direction is unchanged: database-enforced tenant isolation remains the default defense in depth. Only its breadth and the completeness of its mechanism are corrected. Sections 3, 4, and the Negative and Tradeoffs consequences are retained as the original reasoning of record.

## 3. Context

The Scnehaux ecosystem operates under a multi-tenant business model. Strong isolation between tenant data is a critical enterprise requirement across all systems (IAM, HRIS, Payroll, Finance). Historically, multi-tenant isolation relied on application-layer filtering (e.g., developers remembering to append `WHERE tenant_id = ?` to every SQL statement). This approach is highly fragile and presents an unacceptable risk of cross-tenant data leakage.

## 4. Decision Drivers

By moving the tenant isolation boundary from the application layer to the database engine itself, we implement a **Defense-in-Depth** security model. A developer's accidental omission of a filter clause in application code will no longer result in data exposure. The database engine itself will silently and securely filter all read/write operations based on the cryptographically validated transaction context.

## 5. Decision

We mandate **PostgreSQL Row-Level Security (RLS)** as the default database-enforced isolation boundary for **Scnehaux-owned tenant-scoped relational authority tables** where the schema and query model are compatible.

RLS is defense in depth. Application and domain authorization remain mandatory and are never replaced by it.

### 5.1 Where RLS Is Not Required

- Vendor-managed private schemas, including the adopted identity kernel's persistence, which is changed only through its supported upgrade lifecycle.
- External SaaS or client-owned databases.
- Dedicated single-tenant or silo stores where an equivalent physical boundary is stronger and explicitly documented.
- Stores whose supported lifecycle or query model makes RLS unsafe or inapplicable.
- Non-relational systems, which declare their own isolation control.

Where RLS is not used, the governing SAD documents the equivalent isolation boundary and its validation evidence.

### 5.2 Required Mechanism

Where RLS is used, **all** of the following are required. Enabling policies without them leaves the control inert:

- **`FORCE ROW LEVEL SECURITY`** on every protected table. PostgreSQL does not apply policies to a table's owner without it.
- The application **runtime role does not own** the tables it reads or writes, and holds neither `SUPERUSER` nor `BYPASSRLS`.
- **Schema migration executes under a role distinct from the runtime role**, and the runtime role holds no DDL privilege.
- Tenant context is bound through a **trusted server-side path** at the start of each transaction, derived from validated identity and membership rather than from client input.
- Tenant-scoped tables carry an index on the tenant discriminator.
- **Isolation tests execute as the actual runtime role** and prove cross-tenant denial. A test executed on an administrative or owning connection is not isolation evidence.

### 5.3 Verification

Compliance is verified by reading `pg_class.relforcerowsecurity` in addition to `pg_class.relrowsecurity`, and by confirming the effective privileges of the role the application actually connects with. Confirming that policies exist is not sufficient.

## 6. Consequences

### Positive

- **Hardened Security Boundary**: Prevents cross-tenant data leaks at the engine level. An empty or null tenant context evaluates to false and returns zero rows, provided the policy applies to the connecting role under §5.2.
- **Second Line of Defence**: An accidental omission of a tenant predicate does not by itself expose data. This does not remove the obligation to authorize in the application; a system that relies on RLS as its only tenant control has one mechanism, not two.
- **Verifiable Compliance**: Auditable for SOC 2 and ISO 27001 through the catalog query in §5.3, which reads forced status and effective role privilege rather than the enable flag alone.

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

### Operational

- Applied to Scnehaux-owned tenant-scoped authority tables through the migration process governed by ADR-GLB-004. The former `scnehaux-iam` implementation is retired under ADR-IAM-001 and is not a reference for this control: its schema enabled RLS without `FORCE` and ran the application under the owning role, which is the failure §5.2 exists to prevent.

The migration shape required by §5.2 is:

```sql
ALTER TABLE <schema>.<table> ENABLE ROW LEVEL SECURITY;
ALTER TABLE <schema>.<table> FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON <schema>.<table>
  USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
```

## 7. Compliance Impact

### Related Standards

- [Enterprise Data Architecture Strategy (EAD-003)](../../01-enterprise/EAD-003-enterprise-data-ownership-and-topology.md)
- [Platform Identity Architecture Document (PAD-PLT-001)](../../03-domain/PAD-PLT-001-identity-access-platform/PAD-PLT-001-identity-access-platform.pad.md)
- [STD-GLB-002 Enterprise Database & Persistence Standard](../../02-standards/_global/STD-GLB-002-database.md) — carries the same mechanism as normative rules and is the artifact engineering teams read.
- [ADR-GLB-004 Atlas Schema Governance](ADR-GLB-004-atlas-schema.md) — the migration process through which `FORCE` and role separation are applied.
- [ADR-IAM-001 Adopt Keycloak Identity Kernel](../identity-access-platform/ADR-IAM-001-adopt-keycloak-identity-kernel.md) — the vendor-managed persistence excluded by §5.1.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Application-Layer Custom Queries (e.g., ORM Filters)

- **Pros**: Straightforward to set up in code, database engine agnostic.
- **Cons**: Relies entirely on developer compliance. Highly vulnerable to raw SQL bypasses, analytical queries, and schema migrations.
- **Why Rejected**: Fails to provide a hardened, verifiable security boundary at the persistence tier.

### Alternative B: Physical Database-Per-Tenant Isolation

- **Pros**: Perfect hardware-level isolation.
- **Cons**: Extremely expensive infrastructure footprints, slow schema migrations (running migrations across thousands of databases), and massive connection pool exhaustion.
- **Why Rejected**: Unviable due to high operational costs and scaling constraints for thousands of small tenants.
