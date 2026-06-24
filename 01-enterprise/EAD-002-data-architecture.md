---
doc_meta:
  id: EAD-002
  title: Enterprise Data Architecture
  owner: Chief Enterprise Architect
  version: 1.0.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-17
---

# Enterprise Data Architecture (EAD-002)

---

## 1. Enterprise Data Principles

Data is the most critical asset of the Scnehaux Foundation. The Enterprise Data Architecture ensures that information remains accurate, secure, compliant, and highly available.

### 1.1 Single Source of Truth
Every data entity must have one, and only one, authoritative system of record. Distributing write authority across systems introduces transaction race conditions and split-brain inconsistency. Data duplication is forbidden unless explicitly designed as a read-only projection (e.g., CQRS read models).

### 1.2 Data as a Contract
Data schemas exposed to other domains are immutable contracts. Downstream consumer applications rely on schema stability to function reliably without constant redeployments. Breaking schema changes without a rigorous versioning and migration strategy are prohibited.

### 1.3 Strict Domain Encapsulation
A database belongs entirely to a single microservice/domain. Direct database sharing couples teams, bypasses validation rules, and compromises security isolation boundaries. No two domains may connect to the same database. All cross-domain data sharing must occur via APIs or Event Busses.

## 2. Master Data

The Scnehaux master data entities include core HR profiles, compensation parameters, tenant configurations, and organizational structures. These entities are centrally managed within their authoritative boundaries but propagated across the enterprise using event-driven architectures to prevent synchronous query coupling.

## 3. Data Ownership

To preserve domain integrity, data ownership is strictly mapped to the owning bounded contexts:
- **Identity Data (Credentials, Tenants)**: Owned by the Identity & Access Context.
- **Employee & Org Data**: Owned by the Workforce Registry Context.
- **Financial & Tax Data**: Owned by the Payroll & Compensation Context.

## 4. Data Classification

All enterprise data must be strictly classified into the following tiers to dictate storage and transit encryption constraints:
- **Public**: Available to anyone (e.g., public job descriptions).
- **Internal**: Restricted to company employees (e.g., internal memos).
- **Confidential**: Sensitive business data (e.g., strategic roadmap).
- **Restricted**: Highly sensitive data (e.g., PII, Passwords, Financials). Restricted data must be encrypted at rest and in transit.

## 5. Data Governance

Data sovereignty and integrity are maintained through rigorous compliance constraints:
- **Schema Migrations**: All database schema changes must be version-controlled, automated, and executed via a CI/CD pipeline migration utility. Manual database modifications in production are a critical violation.
- **Sovereignty**: HR and Financial data must be protected against unauthorized access and adhere strictly to regional data sovereignty laws.
- **Auditability**: The origin, transformation, and flow of data must be fully transparent to support forensic auditing.

## 6. Data Lifecycle

The lifecycle of data encompasses its creation, utilization, archival, and deletion:
- **Transactional Phase**: High-value, structured data resides in ACID-Compliant RDBMS.
- **Analytical Offloading (CDC)**: Querying production databases directly for reports, ETL, or analytics is strictly prohibited. All transactional updates must be captured at the engine log level using Change Data Capture (CDC) and published as event streams.
- **Backup & DR**: All Tier-0 databases must support Point-In-Time Recovery (PITR) with RPO < 5 minutes and RTO < 1 hour.
- **Data Purging**: Deprecated or expired data must be permanently purged or anonymized in compliance with GDPR and localized data retention laws.

## 7. Data Flow Landscape

Data flows across the enterprise must adhere to the defined Paved Road technologies:
- **Relational Storage**: The primary system of record for structured data.
- **Transient & Caching Storage**: Used strictly for session management, rate limiting, and high-speed read caching. Must never be the primary system of record.
- **Asynchronous Event Backbone**: The enterprise neural network for distributing Domain Events across bounded contexts.
- **Scale Strategy**: Relational transactional databases must be horizontally partitioned using distributed sharding engines once an individual database instance size exceeds 1TB or write IOPS exceed 10,000 IOPS.
