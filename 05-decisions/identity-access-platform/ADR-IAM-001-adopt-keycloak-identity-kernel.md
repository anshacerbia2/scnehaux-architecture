---
doc_meta:
  id: ADR-IAM-001
  title: Adopt Keycloak as the Scnehaux Identity Protocol and Authentication Kernel
  adr_type: replacement
  status: accepted
  created: 2026-08-06
  created_date: 2026-08-06
  created_by: Identity Platform Team
  governed_by:
    - PAD-PLT-001
---

# ADR-IAM-001: Adopt Keycloak as the Scnehaux Identity Protocol and Authentication Kernel

## 1. Title

Adopt Keycloak as the Scnehaux Identity Protocol and Authentication Kernel.

## 2. Status

| Date | Status | ADR Type | Reviewers | Approver |
| :-- | :-- | :-- | :-- | :-- |
| 2026-08-06 | proposed | replacement | Identity, Security, Platform, Architecture | Architecture Authority — pending |
| 2026-08-11 | accepted | replacement | Identity, Security, Platform, Architecture | Architecture Authority |

Three earlier identity decisions covering epoch-based sessions, token signing with an ephemeral development signer, and in-process credential hashing were withdrawn on acceptance. None had reached staging, so they were removed rather than retained as superseded records. This decision replaces them in full.

Upon acceptance, this ADR replaces the custom-engine implementation direction wherever earlier artifacts prescribed Scnehaux-owned session, token-signing, password-engine, or OAuth/OIDC runtime internals, including SAD-001 v1.

## 3. Context

Scnehaux requires an enterprise Identity & Access Platform for internal workforce, managed-service users, customer and partner identities, applications, services, workloads, federation, and future third-party access.

The enterprise identity model is specific to Scnehaux:

- one stable Principal may hold Membership in multiple Tenant contexts;
- customer and partner identities may remain Realm-scoped;
- Organization, Tenant, Workspace, and Membership are authoritative outside IAM;
- Application ownership is authoritative in Software Catalog;
- Product authorization remains in Product domains;
- workload and bounded agent identity must be supported.

The existing Go IAM implementation attempted to own both the identity domain and the security protocol engine. Audit identified material gaps in route protection, cryptographic-key continuity, refresh-token correctness, tenant authority, isolation enforcement, protocol completeness, and event delivery.

The architecture must distinguish three decisions:

1. Scnehaux owns the **Identity & Access Platform** and its domain contract.
2. Scnehaux owns the enterprise **identity model, integrations, governance, SLOs, migration, and experience**.
3. Scnehaux does not need to implement every OAuth, OIDC, SAML, session, credential, MFA, and federation primitive itself.

## 4. Decision Drivers

- Reduce security risk in a trust-critical platform.
- Deliver urgent Identity capability faster than a custom protocol implementation.
- Preserve the narrow authority boundary defined by PAD-PLT-001.
- Avoid dual Principal sources of truth.
- Support OAuth 2.0, OpenID Connect, SAML, MFA, passkeys, sessions, federation, and administration through a mature implementation.
- Retain Scnehaux ownership of Tenant integration, Application onboarding, canonical events, audit integration, migration, and user experience.
- Avoid a permanent vendor-core fork.
- Maintain local token verification and bounded control-plane dependencies.
- Establish a supportable upgrade, vulnerability, backup, restore, and conformance lifecycle.
- Preserve an exit path through standards, canonical Scnehaux contracts, and controlled data migration.

## 5. Decision

### 5.1 Adopted Kernel

Scnehaux SHALL adopt **Keycloak** as the strategic runtime kernel for:

- Principal physical persistence within the Identity domain;
- login identifiers and credential storage;
- authenticators and authentication ceremonies;
- MFA and passkey capabilities used by Scnehaux;
- browser and device sessions;
- OAuth 2.0 Authorization Server capability;
- OpenID Provider capability;
- SAML and external identity federation where required;
- token issuance and protocol grant lifecycle;
- client and protected-resource security registration;
- consent and delegated protocol scopes;
- supported identity administration functions.

Keycloak is a component of the Scnehaux Identity & Access Platform. It is not the enterprise authority for Tenant, Membership, Entitlement, Application ownership, Product authorization, or the enterprise evidence ledger.

### 5.2 Scnehaux-Owned Control Layer

Scnehaux SHALL implement a bounded **Identity Control Service**, preferably in Go, for:

- Software Catalog to protocol-registration orchestration;
- Organization Membership/context projection;
- desired-state configuration and policy validation;
- drift detection and reconciliation;
- canonical Scnehaux identity event translation;
- enterprise Audit & Evidence integration;
- notification coordination;
- legacy IAM migration and compatibility;
- administrative workflow not safely delegated to the vendor console;
- conformance, upgrade, and operational automation.

The Control Service SHALL use supported Keycloak interfaces. It SHALL NOT write directly to the Keycloak database or duplicate authoritative Principal, credential, or session records.

### 5.3 Authority Boundaries

```text
Identity Platform / Keycloak
    Principal, identifier, authenticator, authentication,
    session, protocol trust, federation, workload client trust

Organization
    Organization, Tenant, Workspace, Membership, operating context

Software Catalog
    Product, Application, Application Owner, lifecycle

Subscription & Entitlement
    Subscriber, Subscription, Entitlement, quota

Product Domain / Policy Authority
    business role, permission, resource relationship, approval

Audit & Evidence
    immutable enterprise evidence and retention
```

Keycloak Organizations, Groups, attributes, or roles MAY be used only as bounded local projections or protocol constructs. They SHALL NOT become canonical enterprise authority without a replacement ADR and PAD/EAD review.

### 5.4 Realm Strategy

The default strategy SHALL be a small number of Realms aligned to issuer, cryptographic, policy, residency, or administrative trust boundaries.

`Tenant = Realm` is prohibited as the default model.

A Realm-per-Tenant exception requires explicit evidence of issuer isolation, cryptographic isolation, residency, regulatory separation, customer-controlled identity administration, or another one-way trust boundary.

### 5.5 Principal Authority

The initial strategic runtime SHALL use Keycloak persistence as the physical system of record for Principal, identifiers, authenticators, and sessions within the Identity domain.

Scnehaux SHALL NOT introduce a second Go-owned Principal database. Portability is preserved through canonical identifiers, export/migration procedures, event contracts, and standards-based consumer integration.

### 5.6 Authorization Boundary

Keycloak roles and authorization capabilities SHALL be limited to:

- Identity administration;
- protocol scope and client trust;
- coarse platform entry where explicitly justified;
- claims required by an approved consumer contract.

Product permissions such as refund, payroll approval, quality override, rate-card change, or access to a specific business resource SHALL remain outside Keycloak authority.

Keycloak Authorization Services SHALL NOT become the universal enterprise PDP without a replacement architecture decision.

### 5.7 Extension Policy

Preferred mechanisms:

- standard configuration;
- supported Admin REST APIs;
- standards-based protocols;
- supported theme and user-interface extension points;
- a minimal event-listener extension where required;
- external Scnehaux Control Service.

Restricted mechanisms requiring explicit decision and compatibility tests:

- custom authenticators;
- custom protocol mappers;
- custom user-storage providers;
- custom federation providers;
- other SPIs.

Prohibited by default:

- permanent Keycloak core fork;
- replacement of the Keycloak token/session engine;
- direct writes to the Keycloak database;
- synchronous Tenancy or Product calls on every token validation;
- embedding Product business authorization in Keycloak;
- unmanaged Admin Console changes to controller-owned configuration.

### 5.8 Operational Baseline

- Initial production deployment uses a supported stable Keycloak release pinned through the technology lifecycle process.
- Preview features are disabled by default and require a separate ADR.
- Initial high availability is single-region and multi-availability-zone unless evidence requires more.
- Multi-cluster and stateless preview architectures are not the default.
- Database, key continuity, backup, restore, upgrade, vulnerability response, conformance, and disaster-recovery behavior are owned by the Identity Platform Team.
- Products validate approved tokens locally.

### 5.9 Legacy Go IAM

The existing Go IAM SHALL enter containment and migration mode:

- patch active critical security liabilities;
- freeze new OAuth/OIDC, session, credential, federation, and token-engine features;
- preserve migration, compatibility, canonical event, and integration code that remains useful;
- migrate consumers and data through a governed dual-run/cutover plan;
- retire the custom protocol engine after acceptance evidence and rollback criteria are met.

## 6. Consequences

### Positive

- Reduces the amount of security-critical protocol code owned by Scnehaux.
- Shortens time to a mature authentication, session, federation, and OAuth/OIDC foundation.
- Preserves Scnehaux domain ownership and enterprise authority boundaries.
- Avoids duplicate Principal authority.
- Retains Go for the differentiated control, reconciliation, integration, and migration layer.
- Provides a broad ecosystem, documented administration APIs, and established operational guidance.
- Improves interoperability and conformance potential.

### Negative

- Introduces a Java/Quarkus runtime into a Go-default platform portfolio.
- Requires Keycloak-specific operational skill, upgrades, cache/session understanding, and security response.
- Some Scnehaux requirements may require adapters or controlled extensions.
- Keycloak's internal data model and APIs create migration and upgrade coupling.
- Organization or role features may tempt teams to violate authority boundaries.
- High availability and multi-region operation are not free and require tested database/cache architecture.

### Operational

- The Identity team operates Keycloak, its database, configuration, keys, upgrades, extensions, and runbooks.
- A Scnehaux Control Service and Identity Experience system remain required.
- Technology radar and vulnerability-management processes must include Keycloak and its extensions.
- Every upgrade requires compatibility, conformance, migration, and rollback evidence.
- The three earlier identity decisions were withdrawn on acceptance, so no lifecycle transition remains outstanding.

## 7. Compliance Impact

### Related Standards and Artifacts

- PAD-PLT-001 — Identity & Access Platform.
- EAD-005 — Enterprise Platform Architecture.
- EAD-006 — Enterprise Security Architecture.
- SAD-001 — Scnehaux Identity Runtime.
- SAD-002 — Scnehaux Identity Experience.
- GDC-009 — SAD Guideline.
- GDC-010 — ADR Guideline.

### Compliance Status

Accepted and authoritative.

The adoption of Keycloak is consistent with the EAD strategy to own architecture while adopting mature kernels where safer. It is also a justified platform-level exception to the Go default, not a violation requiring a temporary waiver.

### Required Waivers

None at proposal time. Any preview feature, unsupported extension, or deviation from enterprise runtime/security standards requires its own ADR or exception.

## 8. Alternatives Considered

### Alternative A — Continue Full Custom Go IAM

**Benefits:** maximum source-code control, one primary backend language, custom domain semantics.

**Rejected because:** identity-model differentiation does not justify reimplementing OAuth/OIDC, sessions, credential recovery, MFA, federation, key lifecycle, and protocol security. Existing implementation gaps demonstrate high delivery and security risk.

### Alternative B — Use Keycloak as the Entire Enterprise Control Plane

**Benefits:** fastest path to Organizations, groups, roles, and administration in one product.

**Rejected because:** it would absorb Tenant, Membership, Application ownership, Entitlement, and Product authorization into IAM, creating a god-platform and contradicting the enterprise authority model.

### Alternative C — ZITADEL as the Identity Kernel

**Benefits:** modern API-first operation, strong native B2B organization/project model, Go-native implementation culture, simpler stateless runtime profile.

**Rejected for the current boundary because:** its primary native differentiation overlaps more directly with Scnehaux Organization, project/application, and role-assignment authorities. Preserving Scnehaux's narrow IAM boundary would reduce those benefits and increase model translation. Licensing and vendor-model coupling also require additional consideration.

### Alternative D — Managed Proprietary Identity SaaS

**Benefits:** reduced infrastructure operation, support, rapid capability availability.

**Rejected for the current phase because:** cost, data/control requirements, product lock-in, and enterprise integration strategy have not been justified. This remains a future option if operational capacity becomes the dominant constraint.
