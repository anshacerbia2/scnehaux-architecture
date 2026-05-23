---
doc_meta:
  id: EAD-002
  title: Enterprise Data Architecture
  owner: Chief Enterprise Architect
  version: 1.0.0
  status: approved
  classification: internal
  review_cycle_days: 180
  last_reviewed: 2026-05-17
---

# Enterprise Data Architecture

## 1. Context & Business Drivers

Data is the most critical asset of the Scnehaux Foundation. The Enterprise Data Architecture ensures that information remains accurate, secure, compliant, and highly available. The primary business drivers for data architecture are:

1.  **Data Sovereignty & Compliance**: HR and Financial data must be protected against unauthorized access and adhere strictly to regional data sovereignty laws.
2.  **Absolute Integrity**: Financial ledgers and compensation systems cannot tolerate "eventual consistency" anomalies within their core transaction boundaries.
3.  **Observability & Lineage**: The origin, transformation, and flow of data must be fully transparent to support forensic auditing.

## 2. Enterprise Principles

### 2.1 Single Source of Truth
*   **Statement**: Every data entity must have one, and only one, authoritative system of record.
*   **Implication**: Data duplication is forbidden unless explicitly designed as a read-only projection (e.g., CQRS read models).

### 2.2 Data as a Contract
*   **Statement**: Data schemas exposed to other domains are immutable contracts.
*   **Implication**: Breaking schema changes without a rigorous versioning and migration strategy are prohibited.

### 2.3 Strict Domain Encapsulation
*   **Statement**: A database belongs entirely to a single microservice/domain.
*   **Implication**: No two domains may connect to the same database. All cross-domain data sharing must occur via APIs or Event Busses.

## 3. Strategic Architecture

The strategic "Paved Road" for data persistence within the enterprise is defined as follows:

### 3.1 Relational Storage (The Source of Truth)
*   **Technology**: **PostgreSQL**.
*   **Usage**: The default and mandatory storage for high-value, structured data requiring strong ACID compliance (e.g., HRIS, Finance, IAM).

### 3.2 Transient & Caching Storage
*   **Technology**: **Redis**.
*   **Usage**: Session management, rate limiting, and high-speed read caching. Redis must never be used as the primary system of record.

### 3.3 Asynchronous Event Backbone
*   **Technology**: **NATS** or **Kafka**.
*   **Usage**: Distributing Domain Events across bounded contexts to achieve decoupled, eventually consistent workflows.

## 4. Cross-Cutting Standards

1.  **Schema Migrations**: All database schema changes must be version-controlled, automated, and executed via a CI/CD pipeline tool (e.g., `golang-migrate` or Flyway). Manual database modifications in production are a critical violation.
2.  **Data Classification**: All data must be classified (e.g., Public, Internal, Confidential, Restricted). Restricted data (PII, Passwords, Financials) must be encrypted at rest and in transit.
3.  **Backup & Disaster Recovery**: All Tier-0 databases must support Point-In-Time Recovery (PITR) with RPO (Recovery Point Objective) < 5 minutes and RTO (Recovery Time Objective) < 1 hour.

## 5. Decision Log

| ID | Decision | Status | Rationale |
| :--- | :--- | :--- | :--- |
| **DAT-01** | PostgreSQL as Default | Approved | Relational integrity is non-negotiable for HRIS and Financial domains. NoSQL is explicitly rejected for core systems. |
| **DAT-02** | Prohibit Shared DBs | Approved | Shared databases cause tight coupling and break domain autonomy. Enforcing API/Event-driven data exchange. |
