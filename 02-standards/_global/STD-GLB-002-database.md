---
doc_meta:
  id: STD-GLB-002
  title: Enterprise Database & Persistence Standard
  owner: Architecture Review Board
  version: 3.2.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  authorized_by: [ADR-GLB-019]
  review_cycle_days: 365
  created_date: 2026-01-01
  last_reviewed: 2026-10-09
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

### Aggregate Reads Under Row-Level Security

Added in 3.2.0. A metric that counts rows across Tenants, such as offboardings in progress or provisioning requests awaiting an outcome, is read on every collection (STD-GLB-003 §State Metrics). Reading it as a provider would record a privileged access per collection, and the review of that record would become a review of a timer. Reading it on an owning connection would bypass the isolation this section requires.

- **It reads a view that returns counts and ages and names no row**: no Tenant, no person, no identifier.
- **The view is owned by the migration role and declared `security_barrier`.** A view reads with its owner's privileges and, by default, under its owner's row-level security: "If any of the underlying base relations has row-level security enabled, then by default, the row-level security policies of the view owner are applied" [R10]. `security_barrier` "should be used if the view is intended to provide row-level security" [R10].
- **The owner's own `SELECT` policies admit exactly the rows counted.** `FORCE ROW LEVEL SECURITY` binds the owner like every role, so each policy is declared by name in the service's posture check, which refuses a database with one missing or one more.
- **The runtime role holds `SELECT` on the view and nothing new on the tables.**
- **Not a `SECURITY DEFINER` function.** It would do the same with a second object to own and grant, and its safety rests on a pinned `search_path`: "For security, search_path should be set to exclude any schemas writable by untrusted users" [R11]. A view's references are resolved when it is created.

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

### Restore Evidence

Added in 3.1.0. It states what the two rules above and the enforcement item "restore evidence for authoritative databases" require, so a restore test can be checked. It adds no store to their scope.

Restore evidence comes from a drill that a machine runs, never from a person's account of a restore. "Backups don't matter; what matters is recovery", and "you only know that you can recover your recent state if you actually do so" [R7]. NIST asks the same of a backup: "Test backup information … to verify media reliability and information integrity" [R2].

A drill of a PostgreSQL store MUST:

1. **Back up with the deployment's own procedure.** It runs the script the store's documented backup runs (STD-GLB-009 rule 9), so it tests the backups that exist rather than a command written for the test.
2. **Restore into empty storage.** It deletes the database's volume, or starts a new cluster, and restores into it with the documented restore script. A restore over the live database never meets the case it exists for.
3. **Restore the roles first, then the database, and stop on an error.** `pg_dump` dumps one database and no roles. The roles come from `pg_dumpall --globals-only`, which dumps "only global objects (roles and tablespaces), no databases" [R5], and they must exist before the objects they own or are granted are restored (STD-GLB-009 [R27]). The database is restored whole with `pg_restore --create --exit-on-error`. Without `--exit-on-error`, the default is "to continue and to display a count of errors at the end of the restoration" [R4], which a script can miss. The roles file is allowed one error, the bootstrap superuser's "role already exists", which PostgreSQL calls "harmless" [R5].
4. **Compare the restored database with the source.** The service is stopped before the backup, so both sides describe the same instant. Before any migration job runs, the drill requires each of these to be equal:
   - the schema as `pg_dump --schema-only --create`, which carries owners, grants, default privileges and Row-Level Security policies, written with a fixed `--restrict-key` because pg_dump otherwise "will generate a random one" [R6];
   - the migration version;
   - for every table, its row count and an order-independent checksum of its rows;
   - every sequence's position;
   - the cluster's roles, with their attributes and memberships.

   The tables the store's design names as critical, such as an outbox, delivery receipts, a projection cursor or a consumer registry, MUST be non-empty in the source. Two empty tables are equal and prove nothing.

5. **Start the service on the restored database and read known data.** The service starts with its usual migration job, reaches readiness, and serves known records through its API. The answer MUST equal the one read before the backup. CP-10 asks for "recovery and reconstitution of the system to a known state" [R3].
6. **Measure the recovery against the RTO.** The time runs from the start of the restore into empty storage to the verified read. The drill fails above the store's declared RTO.
7. **Leave a record.** The drill writes a machine-readable evidence file with every check, its result, the durations and the CI run, and CI keeps it as an artifact. The dump and the roles file are not kept as artifacts, because they hold role password hashes (STD-GLB-009 rule 9). CP-4 asks for a test, a review of "the contingency plan test results", and corrective action "if needed" [R1].

**Cadence.** The drill MUST run on every change to the store's repository and on a schedule of at most 90 days (STD-GLB-007 §Backup RPO and RTO Targets). It is automated rather than staged: "If recovery tests are a manual, staged event, testing becomes an unwelcome bit of drudgery" [R7]. The schedule matters for a repository that has stopped changing, but GitHub disables it in such a repository: "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days" [R9]. Each drill's evidence therefore records its date, and evidence older than 90 days is stale whatever the schedule says.

**A drill does not prove an RPO.** It proves that a backup restores and how long that takes. The data a restore loses is everything after the backup, so the RPO is the backup interval: a daily `pg_dump` loses up to 24 hours. A logical dump cannot shorten that. "pg_dump and pg_dumpall do not produce file-system-level backups and cannot be used as part of a continuous-archiving solution" [R8]. An RPO in minutes needs continuous WAL archiving with point-in-time recovery, which makes it "possible to restore the database to its state at any time since your base backup was taken" [R8]. `archive_timeout` puts "a limit on how old unarchived data can be" [R8]. A store whose declared RPO is shorter than its backup interval MUST record the difference as a gap until its production platform archives WAL. Its drill evidence MUST NOT be cited as meeting that RPO.

**Erasure.** A store that carries out right-to-erasure deletions keeps tombstones, and its restore re-applies them (STD-GLB-007 §GDPR Right-to-Erasure). Its drill MUST prove that a deletion made after the backup is applied again after the restore. A store with no erasure path has no tombstones, and its design says so.

**Why, and what was rejected.**

- _Roles from the migration job, before a `pg_restore --clean` over the schema it built._ Rejected. The restored database would mix the release's objects with the dump's. A dump older than the release would bring back an older migration history over tables the newer release had already created, and the next migration would fail. Restoring the roles from the dump of globals lets the database be restored whole, as it was, and the migration job then upgrades it the way it upgrades any database.
- _Row counts alone._ Rejected: two tables with the same count can hold different rows. Every row's text is hashed, and the hashes are sorted, so the checksum does not depend on physical order.
- _Comparing the dump files byte for byte._ Rejected: a dump records when it was made, and its `\restrict` key is random [R6]. The drill compares the schema and every table's content instead.
- _A manual drill each quarter._ Rejected [R7]. A drill that only a person runs is run less often, and a broken backup goes unseen until it is needed.
- _A drill on the development server._ Rejected. It deletes the database it tests, so it runs on a stack that CI starts and throws away.

**Residual risk.**

- CI holds little data, so the measured duration shows how long the procedure takes, not how long a production-sized restore takes. The production platform measures its own.
- The drill restores the release that made the dump. Restoring an older dump under a newer release relies on the order above (roles, database, then the migration job) and is not drilled.
- The drill deletes the volume only. A server's cron, its backup storage, and its copies of `.env` and `keys/` are not exercised.
- A restore to an older point gives back versions that consumers have already seen superseded. A store that publishes versions states how such a restore is reconciled (SAD-004 §6.6), and the drill, which restores to the instant of its own backup, does not test that.

## Exceptions

Exceptions require formal approval under GDC-000 and must state the data authority, isolation model, failure behavior, migration path, and operational owner.

## Enforcement Mechanism

- schema and migration validation in CI/CD
- review of every migration that writes data against §Data in Migrations: its own file, derived values, idempotent, bounded
- architecture checks for cross-domain database access
- tenant-isolation tests for pooled relational stores
- restore evidence for authoritative databases: the drill of §Restore Evidence in each store's CI, with its evidence file kept as an artifact
- vendor-schema boundary checks for adopted kernels and managed products

## References

Normative:

- **[R1]** NIST, _SP 800-53 Rev. 5_, CP-4 "Contingency Plan Testing", OSCAL catalog, accessed 2026-10-08. <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>. "Test the contingency plan for the system … to determine the effectiveness of the plan and the readiness to execute the plan"; "Review the contingency plan test results; and"; "Initiate corrective actions, if needed." Supports rule 7.
- **[R2]** NIST, _SP 800-53 Rev. 5_, CP-9 "System Backup" and CP-9(1) "Testing for Reliability and Integrity", same catalog, accessed 2026-10-08. CP-9 d: "Protect the confidentiality, integrity, and availability of backup information." CP-9(1): "Test backup information … to verify media reliability and information integrity." Its guidance: "Organizations need assurance that backup information can be reliably retrieved." CP-9(2) "Test Restoration Using Sampling": "Use a sample of backup information in the restoration of selected system functions as part of contingency plan testing." Supports rules 4 and 5.
- **[R3]** NIST, _SP 800-53 Rev. 5_, CP-10 "System Recovery and Reconstitution", same catalog, accessed 2026-10-08. "Provide for the recovery and reconstitution of the system to a known state within … after a disruption, compromise, or failure." Supports rules 5 and 6.

Informative:

- **[R4]** PostgreSQL 17 Documentation, _pg_restore_, accessed 2026-10-08. <https://www.postgresql.org/docs/17/app-pgrestore.html>. `--create`: "Create the database before restoring into it"; "All data is restored into the database name that appears in the archive." `--exit-on-error`: "Exit if an error is encountered while sending SQL commands to the database. The default is to continue and to display a count of errors at the end of the restoration." Supports rule 3.
- **[R5]** PostgreSQL 17 Documentation, _pg_dumpall_, accessed 2026-10-08. <https://www.postgresql.org/docs/17/app-pg-dumpall.html>. `--globals-only`: "Dump only global objects (roles and tablespaces), no databases." Notes: "because the script will issue CREATE ROLE for every role existing in the source cluster, it is certain to get a “role already exists” error for the bootstrap superuser, unless the destination cluster was initialized with a different bootstrap superuser name. This error is harmless and should be ignored." Supports rule 3.
- **[R6]** PostgreSQL 17 Documentation, _pg_dump_, accessed 2026-10-08. <https://www.postgresql.org/docs/17/app-pgdump.html>. `--schema-only`: "Dump only the object definitions (schema), not data." `--restrict-key`: "Use the provided string as the psql \restrict key in the dump output"; "If no restrict key is specified, pg_dump will generate a random one as needed." Supports rule 4.
- **[R7]** Google, _Site Reliability Engineering_, ch. 26, "Data Integrity: What You Read Is What You Wrote", accessed 2026-10-08. <https://sre.google/sre-book/data-integrity/>. "No one really wants to make backups; what people really want are restores"; "backups don't matter; what matters is recovery"; "Continuously test the recovery process as part of your normal operations"; "you only know that you can recover your recent state if you actually do so"; "If recovery tests are a manual, staged event, testing becomes an unwelcome bit of drudgery"; "Prove that data recovery works with regular exercise, or data recovery won't work." Supports the drill and its cadence.
- **[R8]** PostgreSQL 17 Documentation, _25.3. Continuous Archiving and Point-in-Time Recovery (PITR)_, accessed 2026-10-08. <https://www.postgresql.org/docs/17/continuous-archiving.html>. "it is possible to restore the database to its state at any time since your base backup was taken"; "pg_dump and pg_dumpall do not produce file-system-level backups and cannot be used as part of a continuous-archiving solution. Such dumps are logical and do not contain enough information to be used by WAL replay"; "To put a limit on how old unarchived data can be, you can set archive_timeout to force the server to switch to a new WAL segment file at least that often"; "archive_timeout settings of a minute or so are usually reasonable." Supports §A drill does not prove an RPO.
- **[R9]** GitHub, _Events that trigger workflows_, `schedule`, accessed 2026-10-08. <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>. "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days"; "Scheduled workflows will only run on the default branch." Supports §Cadence.
- **[R10]** PostgreSQL 17 Documentation, _CREATE VIEW_, accessed 2026-10-09. <https://www.postgresql.org/docs/17/sql-createview.html>. Notes: "By default, access to the underlying base relations referenced in the view is determined by the permissions of the view owner"; "If any of the underlying base relations has row-level security enabled, then by default, the row-level security policies of the view owner are applied, and access to any additional relations referred to by those policies is determined by the permissions of the view owner." `security_barrier`: "This should be used if the view is intended to provide row-level security." Supports §Aggregate Reads Under Row-Level Security.
- **[R11]** PostgreSQL 17 Documentation, _CREATE FUNCTION_, "Writing SECURITY DEFINER Functions Safely", accessed 2026-10-09. <https://www.postgresql.org/docs/17/sql-createfunction.html>. "For security, search_path should be set to exclude any schemas writable by untrusted users." Supports §Aggregate Reads Under Row-Level Security.
