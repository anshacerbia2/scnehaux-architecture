---
doc_meta:
  id: PAD-BIZ-001
  title: Enterprise Human Capital Management
  owner: HCM Team
  version: 1.1.0
  status: approved
  classification: restricted
  governed_by:
    - GDC-008
    - EAD-001
    - EAD-003
    - EAD-006
  realizes_capability:
    - EAD-001
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-23
  fulfilled_by:
    - SAD-101
---

# Enterprise Human Capital Management

## 1. Purpose & Scope

HCM is the Business Plane authority for workforce and employment business meaning across the employee lifecycle.

It owns Employee, Employment, HR Organization, Position, workforce-policy state, and other HCM business outcomes while consuming reusable Platform capabilities.

### 1.1 Out Of Scope

- Principal identity, credentials, authentication, and sessions
- canonical Organization/Tenant/Workspace/Membership operating context
- generic Workflow engine
- generic Work Management
- Notification delivery
- Artifact storage lifecycle
- AI/model execution or Knowledge Graph authority
- future ERP accounting/financial authority
- infrastructure/runtime

## 2. Enterprise Traceability

### 2.1 Realizes

- EAD-001 Human Capital Management Business Product capability

### 2.2 Relationships

- **Identity & Access:** Principal/authentication trust
- **Organization:** canonical Tenant/Workspace/Membership operating context
- **Workspace Experience:** shared digital work environment only
- **Work Management:** reusable HR work queues/assignment/review when used
- **Workflow:** durable multi-step HR processes
- **Rules & Decisioning:** reusable deterministic rule lifecycle when justified
- **Artifact & Document:** employment artifacts
- **Notification:** employee communications
- **Knowledge & Retrieval:** governed HR knowledge/search
- **AI Enablement:** HCM copilot/inference/agent execution
- **Integration:** external payroll/government/benefit/ERP connector machinery where justified
- **Audit & Evidence:** enterprise evidence lifecycle
- **future ERP:** consumes/publishes governed workforce/financial contracts without shared database authority

### 2.3 Consumed By

Authorized Business Products may consume HCM contracts/events for workforce facts according to purpose, Tenant, privacy, and product authorization.

HCM remains the authority for its workforce facts even when those facts are projected into ERP, Workspace Experience, Knowledge, Analytics, or other Products.

## 3. Domain & Context Model

### 3.1 Bounded Context

- Workforce Planning
- Recruitment & Candidate
- Onboarding
- Employee & Employment
- HR Organization
- Position
- Attendance
- Leave
- Performance & Goals
- Competency & Skills
- Career & Succession
- Compensation Planning
- Benefits Administration
- Learning Administration
- Offboarding

### 3.2 Ubiquitous Language

| Term | Meaning |
| :-- | :-- |
| Employee | Workforce person in an active/historical employment relationship |
| Employment | Contractual workforce relationship |
| HR Organization | Departments/reporting structures/positions for workforce business meaning |
| Position | Workforce role/seat inside HR Organization |
| Skill / Competency | HCM-governed workforce capability where HCM is declared authority |
| Leave | Governed absence business state |
| Operating Workspace | Organization-owned tenant/workspace context; not HR Organization |
| HCM Copilot | Product-owned AI experience consuming AI and Knowledge Platforms |

### 3.3 Domain Policies

- HCM owns Employee/Employment/HR Organization business truth
- Organization Platform owns canonical Organization/Tenant/Workspace/Membership
- Identity owns Principal/authentication
- HCM Product authorization is enforced inside HCM
- Workflow coordinates long-running process but does not own HCM business outcome
- Work Management may own shared work lifecycle while HCM owns HR meaning
- AI outputs are proposed/assistive until HCM accepts a governed business mutation
- HR domain prompt/skill semantics remain HCM-owned
- external payroll/ERP/government facts preserve their declared authority
- historical employment events remain traceable

## 4. Integration Contracts

### 4.1 Integration Provided

- employee/employment lifecycle
- HR Organization/Position contracts
- attendance/leave
- performance/goals
- competency/skills
- compensation/benefit planning
- workforce domain events
- HCM Product APIs/commands
- HCM knowledge-source publication where governed

### 4.2 Integration Consumed

- Identity & Access
- Organization
- Workspace Experience
- Work Management
- Workflow
- Rules & Decisioning
- Artifact & Document
- Notification
- Knowledge & Retrieval
- AI Enablement
- Integration
- Audit & Evidence
- Event & Messaging

## 5. Trust & Data Boundaries

### 5.1 Trust Boundary

HCM is authoritative for its Business Product records and invariants. It does not delegate Product authorization or business correctness to shared Platforms.

### 5.2 Identity Access

- authentication comes from Identity
- Tenant/Workspace/Membership comes from Organization
- HCM authorization uses those trust/context signals plus HCM resource/business rules
- HCM copilot/tool actions are authorized exactly like non-AI HCM actions

### 5.3 Data Classification

HCM manages sensitive PII, employment, organization, compensation, attendance, performance, leave, benefits, and career data.

Knowledge/AI/analytics projections inherit source classification, purpose, residency, retention, and access constraints.

## 6. Capability NFR

- **Reliability class:** C1 for core employee/employment lifecycle
- **Availability:** mature core HCM target >=99.95%
- **RTO:** <=1h
- **RPO:** <=15m for authoritative workforce transactions
- **Consistency:** approved HCM business mutations preserve domain invariants
- **Privacy:** least-purpose access to sensitive workforce data
- **Audit:** consequential employment/compensation/access/business actions are traceable
- **Interoperability:** HCM publishes stable contracts rather than database access
- **AI safety:** unavailable AI must not silently corrupt authoritative workforce state
- **Accessibility:** Product experience follows enterprise accessibility baseline

## 7. Ownership & Governance

### 7.1 Team Ownership

HCM Team owns workforce business semantics, HCM data authority, Product authorization, Product roadmap, and HCM Product experience.

Platform teams own their respective reusable capabilities.

### 7.2 Realizing Systems

- SAD-101 HCM Business System

### 7.3 Governance Rules

- HCM SHALL NOT recreate Identity or Organization authority
- Workspace Experience SHALL NOT own workforce business state
- AI/Knowledge copies SHALL NOT become HCM truth without HCM acceptance
- future ERP integrations SHALL use governed contracts, not cross-domain persistence
