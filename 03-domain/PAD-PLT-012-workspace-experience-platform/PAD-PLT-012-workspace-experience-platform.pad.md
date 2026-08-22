---
doc_meta:
  id: PAD-PLT-012
  title: Workspace Experience Platform
  owner: Workspace Experience Platform Team
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
    - SAD-016
---

# Workspace Experience Platform

## 1. Purpose & Scope

The Workspace Experience Platform provides the reusable digital work environment through which users discover, enter, compose, and move across Scnehaux Products while preserving Product-owned journeys and Organization-owned operating context.

It owns shared shell/composition semantics, not business state.

### 1.1 Out Of Scope

- Canonical Organization, Tenant, Workspace, Membership, or operating-context authority
- Product business pages, state, workflows, and authorization
- UI design tokens/primitives owned by the UI Platform
- Work Item, Queue, Assignment, and Claim authority owned by Work Management
- Notification delivery, search/retrieval, or AI execution
- Identity authentication/session authority
- Product registry or commercial entitlement authority

## 2. Enterprise Traceability

### 2.1 Realizes

- EAD-001 Experience & Interaction capability for Application Shell and Workspace Experience
- EAD-005 reusable experience Platform Product direction

### 2.2 Relationships

- **UI Platform** provides build-time design tokens/primitives
- **Organization** provides canonical Tenant/Workspace/Membership context
- **Identity / Application Trust** provide authenticated user/application context
- **Software/Product Catalog** provides registered Product/application metadata where available
- **Work Management** provides My Work/queue/assignment surfaces through its contracts
- **Notification** provides notification inbox/status capability where consumed
- **Knowledge & Retrieval** provides shared search/knowledge results where consumed
- **AI Enablement** supports Product/Workspace copilots where consumed
- **Business Products** retain Product-specific navigation/journey semantics and business state

### 2.3 Consumed By

HCM, Travel Operations, future ERP, adjacent BPO Products, Platform administration experiences, and vertical AI Products may compose into Workspace Experience.

Consumers can still expose governed direct entry points when operational continuity requires it.

## 3. Domain & Context Model

### 3.1 Bounded Context

- Application Shell
- Product Navigation & Discovery
- Experience Composition
- Active Context Presentation
- Context Switching Experience
- My Work Composition
- Shared Search Entry
- Notification Composition
- Copilot Composition
- Cross-Product Deep Linking
- Experience Preference

### 3.2 Ubiquitous Language

| Term | Meaning |
| :-- | :-- |
| Workspace Experience | Human-facing digital environment that composes Product experiences |
| Operating Workspace | Organization-owned canonical operating context; not owned here |
| Application Shell | Shared chrome, navigation, layout, and cross-Product composition boundary |
| Product Surface | Product-owned UI mounted or linked from the shared experience |
| Active Context | Locally represented current Organization/Tenant/Workspace context |
| My Work | Composed view of Work Management contracts; not authoritative work state |
| Composition Slot | Governed location for Product/search/notification/copilot experience |
| Deep Link | Stable navigation reference into a Product-owned route/context |

### 3.3 Domain Policies

- Workspace Experience SHALL NOT own Organization/Tenant/Workspace/Membership facts
- Product-specific business journeys remain Product-owned
- UI primitives/tokens are consumed from UI Platform
- Context changes use Organization contracts and locally verifiable context
- Product authorization is re-evaluated by the Product at the protected resource
- My Work is a projection/composition of Work Management contracts
- Failure of one Product surface is isolated from unrelated surfaces where feasible
- Shared shell does not require every Product to deploy through one frontend topology

## 4. Integration Contracts

### 4.1 Integration Provided

- Application Shell contract
- Product/navigation registration consumption
- Context presentation/switch orchestration
- Product composition slot
- Cross-Product deep-link contract
- My Work composition contract
- shared notification/search/copilot composition hooks
- experience preference contract
- experience telemetry contract

### 4.2 Integration Consumed

- UI Platform packages
- Identity and Application Trust
- Organization context
- Software/Product Catalog metadata
- Work Management
- Notification
- Knowledge & Retrieval
- optional AI Enablement
- Product-owned experience entry contracts

## 5. Trust & Data Boundaries

### 5.1 Trust Boundary

Workspace Experience owns presentation/composition state only. It does not become a security authority merely because it displays active context or navigation.

### 5.2 Identity Access

- user authentication comes from Identity
- operating context comes from Organization
- Product resource authorization is enforced by the Product
- navigation visibility is not proof of Product authorization
- cross-tenant administration requires explicit provider-scope authority

### 5.3 Data Classification

The Platform manages minimal experience state such as layout preference, recent navigation, active-context reference, composition metadata, and telemetry.

It does not own Product records, Membership, Employee, financial, travel, or other Product business data.

## 6. Capability NFR

- **Availability:** target >=99.95% monthly for shared shell/control services at mature state
- **RTO:** <=1 hour
- **RPO:** <=15 minutes for server-owned experience configuration; client-only ephemeral state may be recreated
- **Usability:** Product entry, active context, My Work, and error/degraded states must be understandable without hidden cross-Product coupling
- **Accessibility:** shared shell and composition contracts meet WCAG 2.2 AA
- **Performance:** shared shell must not impose more than 200ms server-side control latency P95 excluding Product content
- **Isolation:** one Product-surface failure must not render unrelated Product surfaces unavailable where technically feasible
- **Interoperability:** Product composition is versioned and does not require Product business model leakage
- **Audit:** privileged composition/configuration/context-administration operations are evidenced
- **Cost Target:** platform cost is measurable per active user/application composition where meaningful

## 7. Ownership & Governance

### 7.1 Team Ownership

Workspace Experience Platform Team owns shared shell, composition, navigation, context presentation, and experience-platform reliability.

Organization owns canonical Workspace context. UI Platform owns design-system primitives. Product teams own Product journeys and business state.

### 7.2 Realizing Systems

- SAD-016 Workspace Experience Platform

### 7.3 Governance Rules

- Workspace Experience SHALL NOT become Organization authority
- Product authorization SHALL NOT be inferred from rendered navigation
- Product deployment SHALL NOT be forced into one physical frontend solely for shell consistency
- shared experience must provide measured consumer/adoption value
