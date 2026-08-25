---
doc_meta:
  id: ADR-ORG-001
  title: Separate Organization Authority from Identity and Use Keycloak as a Projection Target
  adr_type: replacement
  status: accepted
  created: 2026-08-06
  created_date: 2026-08-06
  created_by: Core Platform Team
  governed_by:
    - PAD-PLT-002
---

# ADR-ORG-001: Separate Organization Authority from Identity and Use Keycloak as a Projection Target

## 1. Title

Separate Organization authority from Identity and use Keycloak only as a bounded projection target for identity-context issuance.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                                                | Approver                         |
| :--------- | :------- | :---------- | :------------------------------------------------------- | :------------------------------- |
| 2026-08-06 | proposed | replacement | Architecture, Identity, Core Platform, Security, Product | Architecture Authority — pending |
| 2026-08-11 | accepted | replacement | Architecture, Identity, Core Platform, Security, Product | Architecture Authority           |

On acceptance, the former Enterprise Workspace Platform boundary was retired. Its PAD and its SAD were removed from the active set, and PAD-PLT-002 now carries the Organization Platform.

Upon acceptance, this ADR supersedes the authority model of the former Enterprise Workspace Platform and any IAM implementation decision that treats Tenant, Workspace, Membership, or Product permission as identity-owned state.

## 3. Context

Scnehaux requires one stable Principal to operate across internal ATI, managed-service, customer, partner, and future SaaS contexts. The previous architecture overloaded several distinct concepts:

- Tenant was treated as an independent customer identity boundary;
- Organization was used for both enterprise party and internal hierarchy;
- Workspace was used as a generic container for organization and collaboration;
- Membership was mixed with identity accounts and authorization;
- Keycloak Organizations/Groups could be interpreted as the canonical enterprise model;
- Product systems risked duplicating Tenant and Membership state;
- synchronous central lookups risked making Tenancy a runtime SPOF.

The enterprise EAD v2 model now distinguishes:

```text
Principal             → Identity & Access
Organization          → Organization
Tenant                → Organization
Workspace             → Organization
Membership            → Organization
Subscriber Account    → Subscription & Entitlement
Client Account        → Client & Contract Management
Application Owner     → Software Catalog
Product Permission    → Product Domain / Policy Authority
```

Keycloak is adopted as the Identity protocol and authentication kernel. Its Organizations, Groups, attributes, and roles are useful for local login/token context, but making them canonical would recreate the god-IAM boundary the EAD explicitly rejects.

## 4. Decision Drivers

- Support one stable workforce Principal across many Tenant contexts.
- Preserve independent customer/partner Realm policies without Realm-per-Tenant sprawl.
- Keep authentication and contextual Membership as separate authorities.
- Prevent Keycloak vendor-local structures from becoming the enterprise source of truth.
- Prevent Product permission from leaking into IAM or Tenancy.
- Avoid synchronous Tenancy calls on every token issuance or Product request.
- Provide deterministic Tenant/Membership suspension and revocation propagation.
- Separate technical Tenant identity from subscriber, customer, client, Contract, Product, and deployment concepts.
- Support gradual migration from the existing IAM and Workspace implementations.
- Minimize initial distributed-system and platform-team complexity.

## 5. Decision

### 5.1 Authoritative Domain

Scnehaux SHALL establish **PAD-PLT-002 Organization & Tenancy Platform** as the sole enterprise authority for:

- Organization identity, classification, status, and organization-relevant relationship;
- Tenant identity and lifecycle;
- Workspace identity and lifecycle;
- Principal/workload Membership to Tenant and optional Workspace;
- organization-administrative roles;
- operating-context eligibility and contextual security version;
- Tenant suspension, restoration, offboarding, and retirement coordination;
- authoritative Tenant/Membership lifecycle events and projection obligations.

### 5.2 Distinct Enterprise Concepts

The following SHALL remain distinct and linked only through explicit identifiers/contracts:

```text
Organization
Subscriber Account
Client Account
Tenant
Workspace
Principal
Membership
Product
Application
Entitlement
Product Permission
```

A Tenant SHALL NOT automatically represent the legal customer, commercial subscriber, BPO Client Account, Product, or deployment.

A Workspace SHALL NOT represent an HCM department, BPO Workstream, Product, or Application. Those domains may reference a Workspace as an operating context.

### 5.3 Identity Boundary

Identity & Access SHALL remain authoritative for Principal, Realm, credentials, authentication, session, federation, and protocol trust.

Organization SHALL store only stable Principal/workload references and lifecycle projections required for Membership integrity. It SHALL NOT store reusable credentials or duplicate the Principal source of truth.

Suspending one Membership SHALL NOT suspend the Principal or unrelated Memberships. Principal suspension may prevent use of all Memberships through the Identity security contract.

### 5.4 Keycloak Projection

Keycloak Organizations, Groups, attributes, roles, or equivalent structures MAY represent the minimum context needed for login, token issuance, or identity administration.

They SHALL be treated as non-authoritative projections of Organization state.

The projection path SHALL be:

```text
Organization authoritative mutation
    → canonical event / snapshot
    → Scnehaux Identity Control Service
    → supported Keycloak Admin API
    → Keycloak-local projection
```

Organization SHALL NOT write directly to Keycloak or its database.

Direct Keycloak mutation of controller-owned Tenant/Membership projection is prohibited except a governed emergency repair. Any drift SHALL be reconciled back to the Organization authority.

### 5.5 Realm Strategy

Tenant SHALL NOT map one-to-one to Keycloak Realm by default.

Realm boundaries remain aligned to issuer, cryptographic trust, identity-correlation policy, residency, regulatory separation, or independently delegated identity administration.

A Realm-per-Tenant design requires a separate ADR with evidence that projection inside an existing Realm cannot satisfy the trust boundary.

### 5.6 Membership and Authorization

Membership SHALL establish only contextual relationship and organization-administrative authority.

Membership SHALL NOT imply:

- Product Subscription or Entitlement;
- Product role or permission;
- ownership of a business resource;
- HCM employment or Workforce assignment;
- Application ownership.

Product domains or an approved policy authority remain responsible for business authorization.

### 5.7 Runtime Consumption

Normal IAM token issuance and Product request handling SHALL consume bounded local Tenant/Membership projection and SHALL NOT synchronously call Organization on every request.

Each consumer SHALL declare:

- projection version and fields;
- bootstrap mechanism;
- freshness budget;
- stale behavior;
- revocation priority and maximum enforcement delay;
- reconciliation target.

Exceptional high-risk operations MAY request a fresh authoritative decision through an explicit protected contract.

### 5.8 Physical Realization

Initial realization SHALL use one Go Organization Control application and one private PostgreSQL authority, with logical modules for Organization, Tenant, Workspace, Membership, projection, provisioning coordination, and offboarding.

The initial system SHALL publish through a transactional outbox and SHALL use the enterprise event envelope.

Independent microservices SHALL be extracted only after evidence of independent lifecycle, scale, security isolation, or ownership.

### 5.9 Administrative Experience

Scnehaux SHALL provide a dedicated Organization administrative experience.

The Keycloak Admin Console SHALL NOT be the enterprise UI for canonical Tenant or Membership management.

The browser SHALL authenticate with Keycloak but all Organization/Tenancy mutations SHALL use the Scnehaux Organization Control API.

### 5.10 Migration

The existing Workspace and IAM-owned Tenant/Membership data SHALL enter migration mode:

1. inventory and classify existing concepts;
2. assign canonical identifiers and resolve semantic collisions;
3. backfill the new authoritative store;
4. compare and reconcile legacy sources;
5. bootstrap Keycloak and Product projections;
6. freeze new legacy authoritative features;
7. cut authoritative writes to the new system;
8. retain bounded compatibility and rollback;
9. retire legacy tables/APIs after evidence completion.

Dual authoritative writes are prohibited.

## 6. Consequences

### Positive

- Supports cross-client ATI workforce without duplicate identity accounts.
- Preserves a narrow, standards-focused IAM boundary.
- Prevents Keycloak-specific organization semantics from controlling enterprise tenancy.
- Keeps Product authorization and commercial access in the correct domains.
- Allows local context enforcement during Tenancy outages.
- Makes Tenant suspension, Membership revocation, projection freshness, and drift measurable.
- Preserves future portability away from Keycloak because canonical Tenancy remains external.
- Enables a modular initial implementation without premature microservices.

### Negative

- Requires an additional authoritative control system and administrative experience.
- Requires projection, event, and reconciliation logic between Tenancy, Identity, and Products.
- Introduces temporary migration complexity because existing data is duplicated semantically across IAM and Workspace.
- Some Keycloak native organization/self-service capabilities cannot be used as authoritative shortcuts.
- Eventual consistency requires explicit stale-state and revocation policy.

### Operational

- Core Platform operates the Organization Control and Experience systems.
- Identity Platform operates the Keycloak projection adapter through the Identity Control Service.
- Consumer teams own their local projection health and enforcement.
- Security owns cross-tenant administration and incident requirements.
- Architecture Authority governs ontology and breaking contract changes.
- The old PAD-PLT-002 Workspace Platform and SAD-004 v1 require transition to superseded/deprecated lifecycle after approval and migration.

## 7. Compliance Impact

### Related Standards and Artifacts

- EAD-001 through EAD-006 v2.
- PAD-PLT-001 — Identity & Access Platform.
- PAD-PLT-002 — Organization & Tenancy Platform.
- SAD-001 — Scnehaux Identity Runtime.
- SAD-004 — Scnehaux Organization Control.
- SAD-012 — Scnehaux Organization Experience.
- ADR-IAM-001 — Adopt Keycloak Identity Kernel.
- ADR-GLB-001 — Modular Monolith.
- ADR-GLB-002 — PostgreSQL RLS.
- ADR-GLB-003 — Transactional Outbox.
- ADR-GLB-006 — Event Versioning.
- ADR-GLB-007 — DDD Boundaries.

### Compliance Status

Accepted and authoritative.

The decision aligns with the EAD authority model and PAD/SAD boundary rules. No implementation-vendor detail is introduced into EAD.

### Required Waivers

None at proposal time. Any temporary dual-write, direct Keycloak database access, Realm-per-Tenant default, or bypass of projection reconciliation requires an explicit exception ADR and expiry.

## 8. Alternatives Considered

### Alternative A — Keep the Existing Enterprise Workspace Platform Boundary

**Benefits:** minimal documentation and naming change.

**Rejected because:** the old boundary overloaded Tenant, Workspace, Organization hierarchy, collaboration, provisioning, and context, and incorrectly treated Tenant as an independent customer. It could not distinguish commercial, identity, operational, and technical structures.

### Alternative B — Make Keycloak Organizations Canonical

**Benefits:** fewer custom systems, faster basic B2B organization administration.

**Rejected because:** it transfers enterprise Tenancy authority into IAM/vendor semantics, creates direct coupling to Keycloak lifecycle, and encourages Product roles and Membership to merge.

### Alternative C — Keep Tenant and Membership in the Custom Go IAM

**Benefits:** reuse existing code and one control system.

**Rejected because:** it creates a god-IAM, duplicates identities per Tenant, couples token/session security to business context, and conflicts with the adopted Keycloak kernel.

### Alternative D — Let Every Product Own Its Tenant and Membership

**Benefits:** product autonomy and no central control service.

**Rejected because:** Tenant identity, cross-product Membership, isolation, offboarding, and provider administration would diverge and become impossible to govern consistently.

### Alternative E — Central Synchronous Tenancy PDP on Every Request

**Benefits:** immediately fresh decisions and simple consumer storage.

**Rejected because:** it creates a critical runtime dependency, increases latency, and expands outage Blast Radius. Local projections with bounded freshness are preferred.

### Alternative F — Start with Separate Organization, Tenant, Workspace, Membership, and Projection Microservices

**Benefits:** independent deployment and scaling.

**Rejected because:** current scale, teams, and lifecycle evidence do not justify the distributed-system complexity. Logical boundaries are preserved inside one initial control runtime.
