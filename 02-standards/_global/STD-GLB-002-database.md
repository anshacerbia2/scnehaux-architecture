---
doc_meta:
  id: STD-GLB-002
  title: Enterprise Database & Persistence Standard
  owner: Architecture Review Board
  version: 3.0.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  authorized_by: [ADR-GLB-019]
  review_cycle_days: 365
  created_date: 2026-01-01
  last_reviewed: 2026-10-03
---

# STD-GLB-002: Enterprise Database & Persistence Standard

## Objective & Scope

Define the default persistence and isolation rules for **Scnehaux-owned data stores** while preserving vendor-managed schemas, external authorities, and evidence-driven exceptions.

## Design Principles

- Relational persistence is the default for Scnehaux-owned transactional authority where the model is relational
- One authoritative domain owns each fact; cross-domain database access is prohibited
- Database isolation is defense-in-depth and does not replace application/domain authorization
- Vendor-managed private schemas are controlled through supported vendor lifecycle and APIs, not by injecting Scnehaux schema rules
- Persistence technology follows data model, NFR, lifecycle, and operating cost rather than prestige
- Business logic belongs in application code; database triggers and stored procedures are not a substitute for domain rules. Declarative isolation policy such as RLS is a security control and is not business logic

## Normative Rules

### Default Relational Engine

- PostgreSQL-compatible managed relational capability is the default for new Scnehaux-owned transactional systems unless an ADR justifies another engine
- Document, key-value, graph, time-series, search, or analytical stores are permitted when their workload and NFR justify them
- A specialized store MUST NOT become the sole authority for facts whose authoritative system cannot meet its recovery and consistency requirements

### Multi-Tenancy & Isolation

- Scnehaux-owned tenant-scoped PostgreSQL authority tables MUST use database-enforced isolation appropriate to the query model
- PostgreSQL RLS is the default defense-in-depth mechanism when the schema and access pattern are compatible
- Tables protected by RLS MUST enable `FORCE ROW LEVEL SECURITY`; without it, policies do not apply to the table owner and the control is inert
- The application runtime role MUST NOT own the tables it reads or writes, and MUST NOT hold `SUPERUSER` or `BYPASSRLS`
- Schema migration MUST execute under a role distinct from the application runtime role, and the runtime role MUST hold no DDL privilege
- Isolation tests MUST prove cross-tenant denial using the actual application runtime role; a test executed on an administrative or owning connection is not isolation evidence
- Applications MUST NOT rely solely on unreviewed ad-hoc tenant `WHERE` clauses for authoritative tenant isolation
- RLS is NOT mandatory for vendor-managed private schemas, external SaaS databases, immutable vendor stores, or data models where RLS would violate supported lifecycle or correctness
- Keycloak private persistence MUST remain owned by Keycloak and MUST NOT be modified with Scnehaux tables, triggers, policies, or RLS unless explicitly supported and approved by the vendor integration contract
- Pooled, bridge, silo, and regional data-isolation profiles MAY use different physical controls when risk, residency, scale, or contractual requirements justify them

### Data Ownership & Access

- Cross-domain direct database reads and writes are prohibited unless explicitly approved as a bounded migration or operational exception
- Consumers use APIs, events, governed projections, data products, or approved analytical interfaces
- Read replicas, projections, caches, and indexes MUST NOT silently become canonical authority

### Identifiers

- Scnehaux-owned externally durable entity identifiers SHOULD use globally unique, non-enumerable identifiers; UUIDv7 is the default where the implementation stack supports it safely
- Sequential or auto-incrementing identifiers MUST NOT be exposed as externally visible entity identifiers, because they permit resource enumeration and disclose volume
- Database-local surrogate keys MAY use another form when they are not exposed as enterprise identity and an approved schema rationale exists
- Vendor-managed identifiers MUST remain vendor-managed; Scnehaux MUST NOT rewrite private vendor primary-key strategy

### Migrations & Schema Management

- Scnehaux-owned database schemas MUST be version controlled and changed through an approved schema-migration mechanism
- Atlas is the current paved-road tool where applicable under ADR-GLB-004
- Destructive or incompatible changes require expand/migrate/contract or another explicitly reviewed migration sequence
- Production schema changes require traceable deployment authorization and rollback/recovery planning
- Vendor-managed database migrations MUST use the vendor-supported upgrade lifecycle

### Data in Migrations

Authorized by ADR-GLB-019.

- **Seed data MUST NOT be written by a migration.** Data that does not derive from rows already present (a first account or grant, a resource a service registers for itself, reference rows, demo data, test fixtures) is created by a command or a seed script. A production's first records are created by a command that records the operator and the reason.
- **A change to existing rows that a schema change requires MUST be a versioned data migration.** It is part of the change, and the code that depends on it ships with it.
- A data migration MUST:
  - sit in its own migration file, ordered after the schema migration it serves;
  - derive every value from rows already in the database;
  - change only the rows that still need it, so it is idempotent and a no-op on an empty database;
  - complete within the deployment's migration budget of three minutes.
- **A data change that cannot complete within that budget MUST run as a batched job**: scheduled by a migration, executed by the application outside the deployment in batches with bounded queries, and following expand/migrate/contract so that code tolerates the rows not yet reached.
- Migrations applied before ADR-GLB-019 are not edited. Its file-separation rule applies to every migration written after it.

### Durability & Recovery

- Every authoritative data store declares backup, restore, RPO, RTO, retention, and integrity requirements according to its reliability class
- Backup existence is insufficient; restore must be tested
- Ephemeral cache or search/index stores MUST NOT be the sole durable authority unless their durability model is explicitly approved

## Exceptions

Exceptions require formal approval under GDC-000 and must state the data authority, isolation model, failure behavior, migration path, and operational owner.

## Enforcement Mechanism

- schema and migration validation in CI/CD
- review of every migration that writes data against §Data in Migrations: its own file, derived values, idempotent, bounded
- architecture checks for cross-domain database access
- tenant-isolation tests for pooled relational stores
- restore evidence for authoritative databases
- vendor-schema boundary checks for adopted kernels and managed products
