---
doc_meta:
  id: STD-GLB-007
  title: Enterprise Data Classification, Governance & Retention Standard
  owner: Enterprise Security Architect
  version: 1.2.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-20
---

# Enterprise Data Classification, Governance & Retention Standard (STD-GLB-007)

---

## 1. Objective & Scope

This standard defines the mandatory policies for classifying corporate and tenant data, enforcing data retention periods, managing GDPR right-to-erasure deletions, and establishing disaster recovery parameters (RPO/RTO) within the Scnehaux enterprise.

It applies to all persistent datastores, caching layers, log targets, analytical repositories, and backups managed by Scnehaux applications.

---

## 2. Design Principles

Data ownership must be explicit and domain-bounded. Each domain retains exclusive write authority over its data. Cross-domain data access must pass through published integration contracts, never direct database queries.

## 3. Normative Rules

### Data Classification Tiers

To safeguard sensitive information, all application data fields must map to one of four classification tiers:

| Tier       | Classification       | Description & Examples                                    | Encryption Requirement                    |
| :--------- | :------------------- | :-------------------------------------------------------- | :---------------------------------------- |
| **Tier 1** | **Restricted PII**   | Passwords, private keys, national IDs, payroll details.   | Column-level envelope encryption at rest. |
| **Tier 2** | **Identifiable PII** | Full name, email address, physical address, phone number. | Standard database encryption at rest.     |
| **Tier 3** | **Internal Data**    | Tenant internal configs, system logs, business workflows. | Standard database encryption at rest.     |
| **Tier 4** | **Public Data**      | Marketing assets, public documentation, open API specs.   |                                           |

- **Log Sanitization**: Under no circumstances can Tier 1 or Tier 2 data be written to logging streams or application stdout. Middleware must scrub all logs.

---

### Data Retention Lifecycle

Data must only reside in active storage for as long as is necessary to fulfill its business purposes.

- **Active Transactional Data**: Retained in primary databases indefinitely while the tenant account remains active.
- **System and Application Logs**: Retained in active search storage for `30 days`, then archived to cold storage for `365 days`, after which they are permanently purged.
- **Audit Logs**: Retained in immutable storage for `7 years` to meet compliance mandates.
  - _What counts (1.1.0)._ Every audit record, privileged access included: a service's record of privileged access, its reviews and its emergency uses (for example organization-control's `audit.privileged_access`, `privileged_access_review` and `emergency_grant_use`) are audit logs. They are kept 7 years and purged after that by the owning service's own maintenance. A record younger than 7 years is never purged.
  - _How the database holds it (1.2.0)._ The table itself refuses the early delete, for every role. On PostgreSQL that is a `BEFORE DELETE` row trigger that raises an error on a record younger than 7 years, and a `BEFORE TRUNCATE` trigger that raises on every truncation. The error rolls the statement back: "if either the statement or the trigger causes an error, the effects of both will be rolled back" [R4]. A row-level security policy is not used for this, for two reasons. It does not bind every role: "Superusers and roles with the BYPASSRLS attribute always bypass the row security system when accessing a table", and "Table owners normally bypass row security as well" [R4]. And it does not cover `TRUNCATE`: "Operations that apply to the whole table, such as TRUNCATE and REFERENCES, are not subject to row security" [R4]. A row trigger alone misses it too, since "TRUNCATE will not fire any ON DELETE triggers that might exist for the tables. But it will fire ON TRUNCATE triggers" [R4], so both triggers are required. organization-control is built this way (`TDD-organization-control-001` §Retention). Disabling a trigger needs the table's owner or a superuser, the same people who could drop a policy, so the trigger adds to the grants and does not replace them: no runtime role holds `UPDATE` or `DELETE` on an audit table (`ADR-ORG-002 §5.6`).
  - _Why 7 years._ It is this estate's choice, and it is longer than every external minimum verified. NIST leaves the period to the organization: "Retain audit records for [Assignment: time period] to provide support for after-the-fact investigations of incidents and to meet regulatory and organizational information retention requirements" [R1]. OMB M-21-31 sets minimums, "12 Months Active Storage" and "18 Months Cold Data Storage", for privileged identity and credential management logs, and says "The retention periods prescribed below are minimum values; agencies may retain data for longer periods if appropriate" [R2]. CIS asks to "Retain audit logs across enterprise assets for a minimum of 90 days" [R3].
- **Inactive Tenant Decommissioning**: Upon tenant subscription termination, all associated data across active databases must be flagged for deletion within `24 hours` and permanently purged (including database backups) within `30 days`.
  - _Audit records are exempt (1.1.0)._ The decommissioning purge does not delete audit records, privileged access to the terminated Tenant included. They are kept for the full 7 years of the rule above. A provider's access to a retired Tenant is exactly what a later investigation needs, and AU-11 keeps audit records "to provide support for after-the-fact investigations of incidents" [R1].

---

### GDPR Right-to-Erasure (Deletion Mechanics)

Applications must support the legal right of users to be forgotten.

- **Hard Deletes**: Right-to-erasure requests must execute hard deletes or irreversible pseudonymization (replacing identifiable data with random hashes) on Tier 1 and Tier 2 fields. Soft deletes (e.g. setting `deleted_at = NOW()`) are prohibited for compliance completion.
- **Backups Propagation**: Deleted user identifiers must be registered in a tombstones table. Backup restoration scripts must read the tombstones table to re-apply deletions to older restored database state.

---

### Backup RPO and RTO Targets

Disaster recovery plans must commit to defined data recovery limits.

- **Recovery Point Objective (RPO)**:
  - _Tier 1 & 2 Datastores_: RPO must not exceed `3600s` (1 hour). High-availability replication must maintain real-time copies.
  - _Internal Config Datastores_: RPO must not exceed `86400s` (24 hours).
- **Recovery Time Objective (RTO)**:
  - _Primary Portal Access_: RTO must not exceed `14400s` (4 hours) for full service restoration after a catastrophic site failure.
- **Testing Cadence**: Backup restore drills must execute automatically once every `90 days` to verify image and script integrity.

---

### Data Domain Ownership

To prevent data quality degradation and logical domain leakage in large-scale multi-domain environments, all corporate and tenant data elements must map to a designated Domain Data Owner:

#### Owner Responsibilities

Domain Data Owners are accountable for the lifecycle of their domain data, specifically:

- **Access Control Approval**: Approving all access permission grants and API consumer integrations targeting the domain.
- **Schema Modification Sign-off**: Reviewing and approving all database schema updates or event contract modifications.
- **Retention & Purge Verification**: Conducting quarterly verification checks that data retention and GDPR purge operations conform to standard rules.
- **Data Sharing Contracts**: Defining explicit interfaces (public API models or Outbox event schemas) for cross-domain data access. Direct database-level sharing is prohibited.

#### HRIS Core Domain Ownership Mapping

All data schemas, tables, and attributes must align to this domain ownership matrix:

| Domain                                 | Data Scope Examples                                                               | Domain Data Owner               |
| :------------------------------------- | :-------------------------------------------------------------------------------- | :------------------------------ |
| **Identity & Access Management (IAM)** | User credentials, multi-factor auth states, OAuth tokens, authorization policies. | Security & IAM Engineering Team |
| **Core Human Resources (HR)**          | Employee records, organizational hierarchies, contracts, onboarding workflows.    | Core HR Systems Team            |
| **Payroll & Compensation**             | Bank account details, salary structures, tax filings, payroll transactions.       | Payroll Engineering Team        |
| **Time & Attendance**                  | Time-clock records, check-in locations, leave requests, overtime approvals.       | Workforce Operations Team       |

---

## 4. Exceptions

None. All data governance and ownership rules apply universally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

1. **Vulnerability Scans**: Automated build security checkers must parse database schemas for un-encrypted fields holding sensitive data keys.
2. **Access Control Audits**: Access to Tier 1 and Tier 2 production datastores must follow the Principle of Least Privilege, requiring formal, time-bound approvals.
3. **Exception Waivers**: Deviations from these data governance rules require an approved Architectural Decision Record (ADR) and approval by the Architecture Review Board.
4. **Audit retention (1.1.0, 1.2.0)**: A service that holds audit records tests that its purge deletes only records older than 7 years, and that the tenant decommissioning purge leaves them. From 1.2.0 it also tests that a direct `DELETE` of a younger record and a `TRUNCATE` are refused, as the migration role and as a superuser.

## 6. References

The external sources the audit retention rules, and how a database holds them, rest on, cited as `[Rn]`. The other periods in this standard are this estate's own and cite no external source.

### Normative

- **[R1]** NIST SP 800-53 Rev. 5, AU-11 _Audit Record Retention_, accessed 2026-10-20. NIST OSCAL catalog, <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>. "Retain audit records for [Assignment: time period] to provide support for after-the-fact investigations of incidents and to meet regulatory and organizational information retention requirements."
- **[R2]** OMB Memorandum M-21-31, _Improving the Federal Government's Investigative and Remediation Capabilities Related to Cybersecurity Incidents_, 2021-08-27, Appendix C, accessed 2026-10-20. <https://www.whitehouse.gov/wp-content/uploads/2021/08/M-21-31-Improving-the-Federal-Governments-Investigative-and-Remediation-Capabilities-Related-to-Cybersecurity-Incidents.pdf>. "The retention periods prescribed below are minimum values; agencies may retain data for longer periods if appropriate." Table 5, log category "Privileged Identity & Credential Management": "12 Months Active Storage", "18 Months Cold Data Storage" (table cells, quoted as extracted). It binds federal agencies, not this estate; it is cited as a published minimum.

### Informative

- **[R3]** CIS, _CIS Controls Assessment Specification v8.1_, Control 8, Safeguard 8.10, accessed 2026-10-20. <https://cas.docs.cisecurity.org/en/latest/source/Controls8/>. "Retain audit logs across enterprise assets for a minimum of 90 days."
- **[R4]** PostgreSQL 17 Documentation, accessed 2026-10-20. _Row Security Policies_, <https://www.postgresql.org/docs/17/ddl-rowsecurity.html>: "Superusers and roles with the BYPASSRLS attribute always bypass the row security system when accessing a table." "Table owners normally bypass row security as well, though a table owner can choose to be subject to row security with ALTER TABLE ... FORCE ROW LEVEL SECURITY." "Operations that apply to the whole table, such as TRUNCATE and REFERENCES, are not subject to row security." _TRUNCATE_, <https://www.postgresql.org/docs/17/sql-truncate.html>: "TRUNCATE will not fire any ON DELETE triggers that might exist for the tables. But it will fire ON TRUNCATE triggers." _Overview of Trigger Behavior_, <https://www.postgresql.org/docs/17/trigger-definition.html>: "In all cases, a trigger is executed as part of the same transaction as the statement that triggered it, so if either the statement or the trigger causes an error, the effects of both will be rolled back."
