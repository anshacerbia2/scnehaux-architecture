---
doc_meta:
  id: ADR-GLB-004
  title: ADR-GLB-004 Atlas Schema Governance for Deterministic Data Migrations
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
---

# ADR-GLB-004: Standardizing on Atlas Declarative schema Management for Safe and Traceable Database Evolutions

---

## 1. Title

Standardizing on Atlas Declarative schema Management for Safe and Traceable Database Evolutions

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |
| 2026-08-18 | accepted | foundational | Architecture Review Board | Enterprise Architect |

**Amended 2026-08-18: the destructive gate no longer depends on `atlas migrate lint`.**
Since Atlas v0.38 that command aborts on the free CLI — *"'atlas migrate lint' is
available only to Atlas Pro users"* — so the mechanism this decision originally named
cannot run without a commercial account. Atlas remains the schema tool; §5 now states the
gate as a required property and lists the mechanisms that satisfy it.

## 3. Context

The Scnehaux enterprise operates high-availability relational databases (PostgreSQL) supporting critical, high-transaction workloads across multiple domains (IAM, HRIS, Finance). Safe database schema evolution is vital to prevent outages. Historically, manual SQL migration scripts led to "Schema Drift" (where the database state in production diverged from source control), and developers lacked automated dry-run testing, causing unexpected table locks during deployments.

## 4. Decision Drivers

Adopting a declarative schema model allows us to establish **Deterministic Infrastructure as Code** at the database layer. Atlas automatically calculates the exact SQL diff required to transition the target database to the intended HCL schema state. By running Atlas in our CI/CD pipelines, we run concurrency-aware dry runs and safety checks before DDL scripts are applied, ensuring that destructive operations (e.g., dropping active columns or running un-indexed queries) are blocked.

## 5. Decision

We officially establish **Atlas** (HCL-based declarative management tool) as the enterprise standard for database schema governance, migration testing, and deployment orchestration across the Scnehaux ecosystem.

All database schemas must be declaratively defined in a `schema.hcl` file under source control. Migration scripts must be deterministically generated using the command `atlas migrate diff`. Direct execution of manual, non-audited DDL scripts in production is strictly prohibited.

### 5.1 The Destructive Gate Is a Property, Not a Command

_Amended 2026-08-18._

The pipeline MUST block a destructive schema change from reaching production without a reviewed multi-phase plan. That requirement is the decision. The mechanism is not, because the mechanism originally named is no longer available: `atlas migrate lint` became an Atlas Pro feature in v0.38.

Any combination of the following satisfies the gate, and a pipeline MUST implement at least the first two:

1. **`atlas migrate validate`** on every pull request. Free, and it fails when a committed migration was edited after generation — which is how a reviewed plan and an applied plan quietly stop being the same artifact.
2. **A destructive-statement gate** over the generated migration directory, blocking `DROP TABLE`, `DROP SCHEMA`, `DROP COLUMN`, `DROP CONSTRAINT`, `DROP INDEX`, `RENAME`, and `TRUNCATE` unless the line carries an explicit reviewed annotation. This reads text rather than a parsed plan and is therefore cruder than the analyzer it replaces; it is required because it fails, which the absent analyzer does not.
3. **A directory-and-schema synchronisation check**: run `atlas migrate diff` and assert the working tree stayed clean. A migration directory that no longer matches `schema.hcl` is drift that the next deploy applies silently.
4. **`atlas migrate lint` with an Atlas Pro login**, where a commercial account and a pipeline token exist. This is the strongest option and is preferred where available, because it analyses the plan rather than its text.

### 5.2 Declarative Scope Is Per Schema

_Amended 2026-08-18._

An Atlas environment MUST be scoped to the schemas it owns, through a `search_path` on both the target and the dev URL.

Unscoped, Atlas treats every schema in the database as declared state and plans to drop whatever `schema.hcl` omits. This is not hypothetical: the first generated plan for the Identity Control Database ended in `DROP SCHEMA "public" CASCADE`, and would have planned the same for the `platform` schema that a shared module owns.

A schema-scoped plan cannot modify the schema object it is scoped to, so the schema container itself MUST be created by the migration job rather than declared in `schema.hcl`.

### 5.3 A Schema Shipped by a Shared Module Is Applied, Not Re-Declared

_Amended 2026-08-18._

Where a shared library ships the DDL for a schema its own code queries, the consuming service MUST apply that DDL from the library rather than re-author it in `schema.hcl`.

A column added to a shared table and a change to the function that queries it are one change. Splitting them across two repositories permits a deployment in which one has shipped and the other has not, and re-declaring the schema in a consumer's `schema.hcl` creates exactly that split.

## 6. Consequences

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

### Operational

- Developers execute DDL generation locally:
  ```bash
  atlas migrate diff <migration_name> \
    --dir "file://migrations" \
    --to "file://schema.hcl" \
    --dev-url "docker://postgres/16"
  ```
- Pipeline runs `atlas migrate lint` on every Pull Request to enforce paved road conventions.

## 7. Compliance Impact

### Related Standards

- [Enterprise Data Architecture Strategy (EAD-003)](../../01-enterprise/EAD-003-enterprise-data-ownership-and-topology.md)
- [Scnehaux Identity Runtime (SAD-001)](../../04-system/scnehaux-iam/scnehaux-identity-runtime.sad.md)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Imperative SQL Migration Frameworks (e.g., Liquibase, Flyway)

- **Pros**: Highly mature, supports multiple SQL-based migration formats.
- **Cons**: Relies on developers writing the exact "Up" and "Down" SQL statements manually. Does not perform declarative state diffing and lacks native HCL validation tools.
- **Why Rejected**: Does not solve schema drift at source control. Fails to provide automated destructive validation checks out of the box.

### Alternative B: Manual SQL Scripting & Execution

- **Pros**: Direct control over exact commands run by the DBA.
- **Cons**: Extremely error-prone, untraceable, and leads to massive environment drift (production database states diverging from dev).
- **Why Rejected**: Unacceptable risk of production downtime due to human error.
