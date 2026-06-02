---
doc_meta:
  id: STD-GLB-007
  title: Enterprise Data Classification, Governance & Retention Standard
  owner: Enterprise Security Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Enterprise Data Classification, Governance & Retention Standard (STD-GLB-007)

---

## 1. Objective & Scope

This standard defines the mandatory policies for classifying corporate and tenant data, enforcing data retention periods, managing GDPR right-to-erasure deletions, and establishing disaster recovery parameters (RPO/RTO) within the Scnehaux enterprise.

It applies to all persistent datastores, caching layers, log targets, analytical repositories, and backups managed by Scnehaux applications.

---


## 2. Design Principles



## 3. Normative Rules

### Data Classification Tiers

To safeguard sensitive information, all application data fields must map to one of four classification tiers:

| Tier | Classification | Description & Examples | Encryption Requirement |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Restricted PII** | Passwords, private keys, national IDs, payroll details. | Column-level envelope encryption at rest. |
| **Tier 2** | **Identifiable PII** | Full name, email address, physical address, phone number. | Standard database encryption at rest. |
| **Tier 3** | **Internal Data** | Tenant internal configs, system logs, business workflows. | Standard database encryption at rest. |
| **Tier 4** | **Public Data** | Marketing assets, public documentation, open API specs. |  |

- **Log Sanitization**: Under no circumstances can Tier 1 or Tier 2 data be written to logging streams or application stdout. Middleware must scrub all logs.

---

### Data Retention Lifecycle

Data must only reside in active storage for as long as is necessary to fulfill its business purposes.

- **Active Transactional Data**: Retained in primary databases indefinitely while the tenant account remains active.
- **System and Application Logs**: Retained in active search storage for `30 days`, then archived to cold storage for `365 days`, after which they are permanently purged.
- **Audit Logs**: Retained in immutable storage for `7 years` to meet compliance mandates.
- **Inactive Tenant Decommissioning**: Upon tenant subscription termination, all associated data across active databases must be flagged for deletion within `24 hours` and permanently purged (including database backups) within `30 days`.

---

### GDPR Right-to-Erasure (Deletion Mechanics)

Applications must support the legal right of users to be forgotten.

- **Hard Deletes**: Right-to-erasure requests must execute hard deletes or irreversible pseudonymization (replacing identifiable data with random hashes) on Tier 1 and Tier 2 fields. Soft deletes (e.g. setting `deleted_at = NOW()`) are prohibited for compliance completion.
- **Backups Propagation**: Deleted user identifiers must be registered in a tombstones table. Backup restoration scripts must read the tombstones table to re-apply deletions to older restored database state.

---

### Backup RPO and RTO Targets

Disaster recovery plans must commit to defined data recovery limits.

- **Recovery Point Objective (RPO)**:
  - *Tier 1 & 2 Datastores*: RPO must not exceed `3600s` (1 hour). High-availability replication must maintain real-time copies.
  - *Internal Config Datastores*: RPO must not exceed `86400s` (24 hours).
- **Recovery Time Objective (RTO)**:
  - *Primary Portal Access*: RTO must not exceed `14400s` (4 hours) for full service restoration after a catastrophic site failure.
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

| Domain | Data Scope Examples | Domain Data Owner |
| :--- | :--- | :--- |
| **Identity & Access Management (IAM)** | User credentials, multi-factor auth states, OAuth tokens, authorization policies. | Security & IAM Engineering Team |
| **Core Human Resources (HR)** | Employee records, organizational hierarchies, contracts, onboarding workflows. | Core HR Systems Team |
| **Payroll & Compensation** | Bank account details, salary structures, tax filings, payroll transactions. | Payroll Engineering Team |
| **Time & Attendance** | Time-clock records, check-in locations, leave requests, overtime approvals. | Workforce Operations Team |

---


## 4. Exceptions



## 5. Enforcement Mechanism

1. **Vulnerability Scans**: Automated build security checkers must parse database schemas for un-encrypted fields holding sensitive data keys.
2. **Access Control Audits**: Access to Tier 1 and Tier 2 production datastores must follow the Principle of Least Privilege, requiring formal, time-bound approvals.
3. **Exception Waivers**: Deviations from these data governance rules require an approved Architectural Decision Record (ADR) and approval by the Architecture Review Board.
