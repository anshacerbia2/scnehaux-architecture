---
doc_meta:
  id: PAD-PLT-010
  title: Enterprise Usage Metering & Billing Platform
  owner: Commercial Platform Team
  version: 2.0.0
  status: approved
  classification: restricted
  governed_by:
    - GDC-008
    - EAD-001
    - EAD-003
    - EAD-005
  realizes_capability:
    - EAD-001
    - EAD-003
    - EAD-005
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-23
  fulfilled_by:
    - SAD-009
---

# Enterprise Usage Metering & Billing Platform

## 1. Purpose & Scope

The Usage Metering & Billing Platform provides reusable cross-Product commercial metering, rating, charge, billing-cycle, and bill/invoice-generation mechanics for Scnehaux commercial offerings.

Subscription & Entitlement remains a distinct authority for whether a Product capability is commercially granted. ERP/financial systems remain authoritative for accounting ledger, payment settlement, tax, and financial posting unless separately chartered.

### 1.1 Out Of Scope

- Subscription/Entitlement authority
- Product Offering ownership and Product pricing strategy
- general Product business authorization
- ERP general ledger/accounts receivable accounting authority
- payment-provider settlement authority
- tax authority/reporting
- Product business usage semantics
- Tenant/Organization authority
- arbitrary financial workflow
- payment credentials

## 2. Enterprise Traceability

### 2.1 Realizes

- EAD-001 Usage Metering & Billing shared commercial capability
- EAD-003 commercial usage/billing state ownership
- EAD-005 shared Platform Product direction

### 2.2 Relationships

- **Subscription & Entitlement** owns commercial grants/quotas
- **Products** emit accepted usage/metering facts and own Product usage semantics
- **Organization** supplies Tenant/customer operating context
- **Product/Offering Catalog** supplies offering references where chartered
- **future ERP/Finance** owns accounting/receivable/ledger facts
- **Integration** may provide payment/tax/financial connector machinery
- **Notification** delivers bills/invoices/communications
- **Artifact & Document** stores generated bill/invoice artifacts
- **Audit & Evidence** preserves consequential commercial evidence

### 2.3 Consumed By

Products requiring usage-based or recurring commercial billing, commercial operations, future ERP/finance integrations, and authorized customer/admin experiences.

Internal-only Products do not need to consume Billing merely because the capability exists.

## 3. Domain & Context Model

### 3.1 Bounded Context

- Usage Meter
- Meter Definition
- Usage Record
- Rating
- Charge
- Billing Account Reference
- Billing Cycle
- Bill / Commercial Invoice
- Credit / Adjustment
- Billing Reconciliation
- Billing Export

### 3.2 Ubiquitous Language

| Term | Meaning |
| :-- | :-- |
| Usage Record | Accepted measurable Product usage fact with source/correlation |
| Meter | Versioned definition for how usage is counted |
| Rating | Application of commercial rate configuration to accepted usage |
| Charge | Commercial amount produced by rating/adjustment |
| Bill | Periodic commercial statement of charges |
| Commercial Invoice | Billing document, distinct from ERP accounting posting |
| Entitlement | Commercial grant owned outside this Platform |
| Financial Posting | ERP/accounting fact owned outside this Platform |

### 3.3 Domain Policies

- Product owns meaning/correctness of published usage facts
- Subscription & Entitlement owns grants/access, not Billing
- Billing owns accepted meter/rating/charge/bill lifecycle
- billing completion does not imply ERP posting/payment settlement
- duplicate usage is protected through source/event idempotency
- rating versions/effective dates are explicit
- adjustments are attributable and do not rewrite historical evidence silently
- Product pricing strategy remains Product/commercial authority; Platform executes governed rating configuration

## 4. Integration Contracts

### 4.1 Integration Provided

- meter/version lifecycle
- usage acceptance/deduplication
- rating
- charge lifecycle
- billing cycle
- bill/commercial-invoice generation
- adjustment/credit mechanics
- billing query/export
- billing lifecycle events

### 4.2 Integration Consumed

- Product usage facts
- Subscription & Entitlement
- Organization
- Product/Offering references
- Artifact & Document
- Notification
- Integration
- Audit & Evidence
- Event & Messaging
- future ERP/Finance contracts

## 5. Trust & Data Boundaries

### 5.1 Trust Boundary

Billing is authoritative for accepted usage records inside its meter contract, rating results, charges, and billing statements. It is not authoritative for Product usage business facts before acceptance, Entitlement, or ERP ledger/payment state.

### 5.2 Identity Access

Administration/rating/adjustment/export operations require attributable identity, Tenant/application scope, and commercial authorization.

Products publish usage under registered workload/application identity.

### 5.3 Data Classification

Billing stores commercial usage, meter/rating metadata, charges, billing statements, adjustments, correlation, and customer/Tenant references.

Payment credentials and unrelated Product payloads are excluded.

## 6. Capability NFR

- **Reliability:** C1 for accepted commercial usage and billing state
- **Availability:** mature target >=99.95%
- **RTO:** <=1h
- **RPO:** <=15m
- **Correctness:** duplicate accepted usage cannot create duplicate charge under declared idempotency contract
- **Reconciliation:** critical source usage and ERP/payment exports have explicit reconciliation
- **Audit:** rate changes, adjustments, billing close/reopen/export are traceable
- **Scalability:** metering ingestion separated from billing/reporting pressure
- **Interoperability:** Product usage and ERP export contracts are versioned/vendor-neutral
- **Cost Target:** billing platform cost measurable per usage record/bill/Tenant where meaningful

## 7. Ownership & Governance

### 7.1 Team Ownership

Commercial Platform Team owns metering/rating/charge/billing mechanics.

Subscription & Entitlement owns grants. Product/commercial owners own Product pricing intent. ERP/Finance owns accounting.

### 7.2 Realizing Systems

- SAD-009 Usage Metering & Billing Platform

### 7.3 Governance Rules

- Billing SHALL NOT own Product Entitlement
- Billing SHALL NOT become ERP ledger authority
- payment/settlement success SHALL NOT be inferred from bill generation
