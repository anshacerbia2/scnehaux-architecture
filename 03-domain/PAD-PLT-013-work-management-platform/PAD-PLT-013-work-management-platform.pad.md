---
doc_meta:
  id: PAD-PLT-013
  title: Work Management Platform
  owner: Work Management Platform Team
  version: 1.0.0
  status: approved
  classification: internal
  governed_by:
    - GDC-008
    - EAD-001
    - EAD-005
  realizes_capability:
    - EAD-001
    - EAD-005
  review_cycle_days: 180
  created_date: 2026-08-23
  last_reviewed: 2026-08-23
  fulfilled_by:
    - SAD-017
---

# Work Management Platform

## 1. Purpose & Scope

The Work Management Platform provides reusable operational work-management semantics for Products that need human or workload-visible work inventory, cases, queues, assignment, claim, priority, generic review/approval state, ownership, and work history.

Products own what a Work Item means and the final business outcome.

### 1.1 Out Of Scope

- Product business entity or Product outcome authority
- durable multi-step process definition/state owned by Workflow
- technical Job/Worker/Queue runtime semantics
- durable future timing owned by Scheduling
- Product-specific eligibility/routing rules
- Identity, Membership, or workforce/employment authority
- notification delivery
- Product-specific UI journey

## 2. Enterprise Traceability

### 2.1 Realizes

- EAD-001 Work / Case / Queue / Assignment shared execution capability
- EAD-005 shared operational execution capability

### 2.2 Relationships

- **Products** define work meaning and business outcome
- **Workflow** may create/reference Work Items for human tasks while retaining process state
- **Rules & Decisioning** may provide deterministic assignment/routing evaluations when used
- **Scheduling** may wake Product/Workflow for SLA or future actions but does not own work
- **Notification** communicates assignments/escalations
- **Organization** supplies Tenant/Workspace/Membership context
- **Identity** supplies Principal/workload identity
- **Workspace Experience** composes My Work surfaces

### 2.3 Consumed By

Travel Operations, HCM, future ERP, adjacent BPO/support Products, Workflow, and other operational Products requiring shared work inventory and ownership semantics.

## 3. Domain & Context Model

### 3.1 Bounded Context

- Work Item Registry
- Case Lifecycle
- Queue
- Assignment
- Claim / Release
- Priority
- Work Ownership
- Generic Review & Approval
- Work SLA Reference
- Work History
- Work Search/Projection

### 3.2 Ubiquitous Language

| Term | Meaning |
| :-- | :-- |
| Work Item | Reusable unit of actionable operational work |
| Case | Durable work container grouping related work/activity |
| Queue | Business-visible ordered/bucketed work inventory; distinct from technical message queue |
| Assignment | Explicit ownership relationship between Work Item and Principal/team/workload |
| Claim | Atomic acquisition of eligible work |
| Release | Return of claimed work to an eligible pool |
| Priority | Work-management ordering signal; Product may supply domain priority inputs |
| Review | Human/system examination of work without defining Product business truth |
| Approval | Recorded review decision in the reusable work lifecycle; Product owns business effect |
| Work History | Immutable/append-oriented record of work-management lifecycle facts |

### 3.3 Domain Policies

- Product domain owns business meaning and final mutation
- Work Management owns reusable work lifecycle/assignment/claim semantics
- technical message queues are not Work Management queues
- claim/assignment operations are concurrency-safe and attributable
- Product-specific routing policy remains Product-owned unless expressed through a separately governed Rules contract
- Approval recorded here does not itself mutate Product truth; Product executes/accepts the resulting business command
- Workflow process state is not duplicated as Work Item state
- every work item has one owning Product/application and Tenant scope where applicable

## 4. Integration Contracts

### 4.1 Integration Provided

- Work Item creation/reference
- Case lifecycle
- Queue enrollment/removal
- assignment/unassignment
- claim/release
- priority update
- generic review/approval recording
- work history
- Work Item query/search
- My Work projection
- work lifecycle events

### 4.2 Integration Consumed

- Identity
- Organization
- optional Workflow
- optional Rules & Decisioning
- optional Scheduling
- Notification
- Audit & Evidence
- Event & Messaging where async contracts are selected

## 5. Trust & Data Boundaries

### 5.1 Trust Boundary

Work Management is authoritative for shared work lifecycle state it accepts. It does not own the Product record or business outcome referenced by the Work Item.

### 5.2 Identity Access

- assignments/claims reference validated Principals/workloads
- Tenant/Workspace context is Organization-owned
- queue visibility/claim eligibility is authorized by Work Management plus Product-provided policy/context
- Product actions require Product authorization independently

### 5.3 Data Classification

Stores bounded work metadata, references, assignment/claim/review state, priority, history, and correlation.

Unbounded Product payloads and Product business records remain with the Product.

## 6. Capability NFR

- **Reliability class:** C1 Mission-Critical Operations for core work inventory/claim paths
- **Availability:** target >=99.95% monthly
- **RTO:** <=1 hour
- **RPO:** <=15 minutes
- **Concurrency:** duplicate successful claim of one exclusive Work Item is prohibited
- **Scalability:** Tenant/application/work-type bulkheads and quotas prevent one consumer from exhausting shared capacity
- **Latency:** claim/assignment control path target P95 <=300ms excluding external dependencies
- **Audit:** create/assign/claim/release/review/approve/reprioritize/close and privileged override are traceable
- **Privacy:** Product payload minimization and Tenant isolation
- **Interoperability:** Product references are versioned opaque identifiers/contracts, not cross-database joins
- **Cost Target:** unit cost measurable per active Work Item / lifecycle transition

## 7. Ownership & Governance

### 7.1 Team Ownership

Work Management Platform Team owns generic Work Item/Case/Queue/Assignment/Claim/Review lifecycle and service reliability.

Product teams own business meaning, eligibility, business rules, and final outcome. Workflow Team owns process state.

### 7.2 Realizing Systems

- SAD-017 Work Management Platform

### 7.3 Governance Rules

- Work Management Queue SHALL NOT be confused with technical messaging queue
- Work Item SHALL NOT become a copy of Product aggregate
- generic Approval SHALL NOT become Product authorization/business-decision authority
- Workflow state SHALL NOT be duplicated merely for convenience
