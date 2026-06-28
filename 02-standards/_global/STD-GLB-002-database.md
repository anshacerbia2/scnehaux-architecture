---
doc_meta:
  id: STD-GLB-002
  title: Enterprise Database & Persistence Standard
  owner: Architecture Review Board
  version: 1.0.0
  status: adopted
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 365
---

# STD-GLB-002: Enterprise Database & Persistence Standard

## Objective & Scope
To prevent data fragmentation and licensing lock-in, this standard mandates the default persistence technologies and schema design rules for Scnehaux platforms.

## Design Principles
- Relational databases are the default. NoSQL is an exception, not a rule.
- Data logic belongs in the application code, not in database triggers or stored procedures.

## Normative Rules
### Default Engine
- **PostgreSQL 15+** is the mandatory default RDBMS engine for all new applications.
- Document stores (MongoDB), Key-Value stores (Redis), and Graph databases are allowed ONLY when explicitly justified via an ADR demonstrating PostgreSQL's inability to meet specific NFRs.

### Multi-Tenancy & Isolation
- Multi-tenant architectures MUST implement **Row-Level Security (RLS)** to enforce tenant isolation at the database engine level.
- Applications MUST NOT rely solely on WHERE clauses in application code to filter tenant data.

### Primary Keys
- **UUIDv7** (time-ordered UUIDs) MUST be used for all primary keys to ensure global uniqueness while preventing index fragmentation (B-tree page splits).
- Auto-incrementing integers (SERIAL) are PROHIBITED for externally exposed identifiers to prevent enumeration attacks.

### Migrations & Schema Management
- Database schemas MUST be managed declaratively (e.g., using Atlas or similar schema-as-code tools).
- Migrations MUST be backward compatible (e.g., adding a column is allowed; dropping or renaming a column requires a multi-phase deployment).

## Exceptions
Highly specialized data models like Timeseries metrics or full-text search indices.

## Enforcement Mechanism
Atlas schema diffing in CI/CD.
