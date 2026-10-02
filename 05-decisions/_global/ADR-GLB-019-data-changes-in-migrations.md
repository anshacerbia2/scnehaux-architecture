---
doc_meta:
  id: ADR-GLB-019
  title: ADR-GLB-019 A Migration Changes Existing Data Only as a Bounded Data Migration, and Never Seeds
  adr_type: foundational
  status: accepted
  created: 2026-10-03
  created_date: 2026-10-03
  created_by: Architecture Authority
  governed_by:
    - EAD-003
    - EAD-005
  authorizes: [STD-GLB-002]
---

# ADR-GLB-019: A Migration Changes Existing Data Only as a Bounded Data Migration, and Never Seeds

## 1. Title

Seed data is created by a command or a seed script, never by a migration. A migration changes existing data only as a data migration: in its own file after the schema change it serves, deterministic, idempotent, and small enough to run inside the deployment. Larger changes run as a batched job.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver               |
| :--------- | :------- | :----------- | :------------------------ | :--------------------- |
| 2026-10-03 | accepted | foundational | Architecture Review Board | Architecture Authority |

## 3. Context

`STD-GLB-002` requires schemas to be version controlled and changed through an approved migration mechanism, and `ADR-GLB-004` makes Atlas that mechanism. Neither says what a migration may do to data, so each repository decided it alone:

- Every migration that writes data today is a **backfill**: it completes rows that existed before the schema change, from values already in the database.
  - identity-control `20261003120000` records the ceremony's Principal in `bootstrap_ceremony.principal_id`.
  - organization-control `20261002100000` marks the bootstrap grant `emergency`.
  - foundation-platform `0002` gives legacy idempotency keys a scope, and `0004` completes dead letters.
- **No migration seeds**. Initial data is created by commands: the bootstrap ceremony (`ADR-IAM-001 §5.11`), `organization-control bootstrap-provider`, and test fixtures such as `scripts/ci-fixture.sql`.
- Every backfill shares its file with the DDL it serves. Nothing required otherwise.

The question was raised as "data belongs in a seed script, not a migration". That is right for seed data and wrong for a backfill. The two need different homes.

## 4. Decision Drivers

- A backfill and the code that depends on it ship together. Code that reads a new column must not run against rows a forgotten script left empty.
- A database that cannot be destroyed and recreated is changed in place, so its data changes must be versioned, ordered and repeatable like its schema.
- Seed data differs by environment and purpose. Demo and fixture data must never reach production, and a production's first records are acts with an operator on record, not migration side effects.
- A large data change must not hold a deployment, or a table lock, for its duration.

## 5. Decision

### 5.1 Seed Data Never Travels in a Migration

Data that does not derive from rows already present is seed data: a first account, a first grant, a resource a service registers for itself, reference rows, demo data, test fixtures. It MUST be created by a command or a seed script, never by a migration.

- A production's first records are created by a command with an operator and a reason on record, as the bootstrap ceremony and `bootstrap-provider` are.
- Development and test data is a versioned seed script or fixture, applied only where it is wanted. Fowler and Sadalage keep sample data apart because "this sample data would not make it to production" [R1]. Rails names the seed feature for "initial data after a database is created … especially useful when reloading the database frequently in development and test environments" [R3].

### 5.2 A Backfill Is a Data Migration

A change to rows that already exist, needed because the schema changed, MUST be a versioned migration, because it is part of the change.

- Fowler and Sadalage list "transaction data updates, and fixes to production data problems caused by bugs" among the contents of migration scripts [R1].
- Rails: "Migrations can also be used to add or modify data. This is useful in an existing database that can't be destroyed and recreated, such as a production database" [R3].

A data migration MUST meet all of these:

1. **Its own file**, ordered after the schema migration it serves. Django: data migrations are "best written as separate migrations, sitting alongside your schema migrations" [R2]. The schema change and the data change are then reviewed, validated by `atlas migrate validate` and recovered separately.
2. **Derived, not invented.** Every value comes from rows already in the database. A value that cannot be derived is seed data (§5.1) or a decision for an operator.
3. **Idempotent and safe on an empty database.** It changes only the rows that still need it, so a fresh database, where the application writes the value itself, runs it as a no-op.
4. **Bounded.** It completes within the deployment's migration budget, three minutes, as GitLab bounds its regular migrations [R4].

### 5.3 A Large Data Change Is a Batched Job

A data change that cannot meet §5.2 rule 4 MUST run as a batched job, scheduled by a migration but executed by the application outside the deployment, in batches with bounded queries. This is GitLab's batched background migration: "These aren't regular Rails migrations, but application code that is executed via Sidekiq jobs," used for data migrations that exceed the post-deployment time limit [R4]. Code depending on its result tolerates rows the job has not reached yet, or waits for it to finish. That is the expand/migrate/contract sequence `STD-GLB-002` already requires for incompatible changes.

### 5.4 What Is Already Applied Stays

The four backfills in §3 meet §5.2 rules 2 to 4, and share a file with their DDL. They have been applied to databases that keep their history, and Atlas checksums every applied file, so they are not edited. §5.2 rule 1 applies to every migration written after this decision.

## 6. Consequences

### Positive

- A reviewer can tell a seed from a backfill by where it lives, and a backfill from a schema change by its file.
- No environment's first records are a migration side effect. Each has an operator on record or is a fixture that only a test loads.
- A large backfill cannot hold a deployment.

### Negative

- A backfill that used to be one file is now two.
- A batched job is application code with its own tests and progress reporting, not a SQL statement.

### Operational

- `STD-GLB-002` §Migrations & Schema Management states the rules. Review checks the file split and the derivation; the destructive-statement gate of `ADR-GLB-004 §5.1` is unchanged.

## 7. Compliance Impact

### Related Standards

- `STD-GLB-002` 3.0.0, §Migrations & Schema Management, which this decision authorizes. It also records the authorizing ADR the standard's major version 2 lacked (`GOV-DEBT-002`).
- [ADR-GLB-004](ADR-GLB-004-atlas-schema.md): Atlas versioned migrations and the destructive gate.
- [ADR-IAM-001](../identity-access-platform/ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.11: the first Principal and the service's own resource come from a ceremony, not a migration.

### Compliance Status

Compliant for everything applied, under §5.4. New migrations follow §5.2 rule 1 from this decision.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — All Data Through Seed Scripts

Every data change, backfills included, would run as a script outside the migrations.

- **Pros**: migrations would hold DDL only.
- **Cons**: a backfill would be a step someone runs after a deploy, in the right order, on every database, with no record of whether it ran. The code that reads the backfilled column ships with the migration and would meet empty rows wherever the step was missed. Every source above versions backfills with the schema for that reason [R1][R2][R3][R4].
- **Why Rejected**: it moves an ordered, repeatable change into a manual one.

### Alternative B — Data Migrations in the Same File as Their DDL

What every repository did until this decision.

- **Pros**: one file per change, and Fowler and Sadalage's own example does it [R1].
- **Cons**: the schema change and the data change cannot be reviewed, validated or recovered separately, and a slow data statement holds the DDL's transaction and its locks.
- **Why Rejected**: Django and GitLab both separate them [R2][R4], and the separation costs one file.

### Alternative C — Seed First Records in Migrations

A migration would insert the first provider, the service's own resource, or reference rows.

- **Pros**: a fresh environment would need no command.
- **Cons**: the record would have no operator and no reason, and would appear in every environment the migration reaches, production included. `ADR-IAM-001 §5.11` exists because a first identity without a recorded decision is indistinguishable from one an attacker placed there.
- **Why Rejected**: first records are decisions, and a migration records none.

## 9. References

### Informative

- **[R1]** Pramod Sadalage and Martin Fowler, _Evolutionary Database Design_, accessed 2026-10-03. <https://martinfowler.com/articles/evodb.html>. "These migration scripts include: schema changes, database code changes, reference data updates, transaction data updates, and fixes to production data problems caused by bugs"; of sample data, "This sample data would not make it to production, unless specifically needed for sanity testing or semantic monitoring."
- **[R2]** Django, _Migrations_, §Data Migrations, accessed 2026-10-03. <https://docs.djangoproject.com/en/stable/topics/migrations/>. "As well as changing the database schema, you can also use migrations to change the data in the database itself"; "they're best written as separate migrations, sitting alongside your schema migrations."
- **[R3]** Ruby on Rails Guides, _Active Record Migrations_, §Migrations and Seed Data, accessed 2026-10-03. <https://guides.rubyonrails.org/active_record_migrations.html>. "Migrations can also be used to add or modify data. This is useful in an existing database that can't be destroyed and recreated, such as a production database"; seeds are for "initial data after a database is created."
- **[R4]** GitLab, _Migration Style Guide_, accessed 2026-10-03. <https://docs.gitlab.com/development/migration_style_guide/>. Regular migrations "run _before_ new application code is deployed", with a recommended duration of three minutes or less; batched background migrations: "These aren't regular Rails migrations, but application code that is executed via Sidekiq jobs." They take the data migrations that exceed the post-deployment limit of ten minutes, and do not change the schema.
