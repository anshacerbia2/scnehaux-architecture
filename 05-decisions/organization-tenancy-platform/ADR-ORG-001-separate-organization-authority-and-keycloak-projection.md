---
doc_meta:
  id: ADR-ORG-001
  title: Separate Organization Authority from Identity and Use Keycloak as a Projection Target
  adr_type: foundational
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

| Date       | Status   | ADR Type     | Reviewers                                                | Approver               |
| :--------- | :------- | :----------- | :------------------------------------------------------- | :--------------------- |
| 2026-08-11 | accepted | foundational | Architecture, Identity, Core Platform, Security, Product | Architecture Authority |

## 3. Context

Scnehaux requires one stable Principal to operate across internal ATI, managed-service, customer, partner, and future SaaS contexts. Without an explicit model, several distinct concepts overload one another:

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

### 5.11 Provider and Consumer Authority Are Organization Records, Checked Where They Are Held

The Organization Control API recognizes three callers: a Tenant administrator, a provider acting across Tenants, and a registered projection consumer. It SHALL decide which one a token is from the standard's claims and from its own records, and SHALL NOT read a role from the token. `STD-IAM-002 §3.2` keeps roles out of every access token, and a role the kernel held would make the kernel a second authority for a fact this platform owns (§5.1).

**A provider is a Principal holding a provider grant this platform records,** and holding it in force: an eligible grant confers authority only while an approved activation of it lasts, and an emergency grant is standing (`ADR-ORG-002`). The grant names the Principal by `principal_id`, the registered scope `provider:organization-control`, who granted it, and why. The Organization Control API reads it for each request, by the token's `principal_id`, and the token carries only identity and assurance: `principal_id`, `subject_type` `human`, `acr` and `auth_time`, and no `tenant_id`. This is how Google Cloud IAM and Kubernetes decide access: authentication establishes who the caller is, and the resource evaluates the policy it holds, denying by default [R2][R3]. Two things follow:

- **The grant is not projected into the kernel.** `ADR-IAM-001 §5.6` projects a provider grant so that a resource outside Organization can check it from the token. This resource holds it, so a projection would add a copy that can drift, and a `provider_scope` claim that means nothing to the Identity Control API it would also travel to. RFC 9068 forbids that for `scope`, and RFC 8707 tells an authorization server to trim a token to what its resource needs [R1][R4].
- **A revoked grant stops the next request.** A claim would stop only when the token carrying it expires.

**The first grant is made by a single-use bootstrap command, recorded like the first Principal.** A provider grant is made by a provider, so the first one has no one to make it. `ADR-IAM-001 §5.11` solved the same cycle for the first Principal, and the grant follows the same four rules:

1. it succeeds at most once per database, enforced by a constraint;
2. it refuses to run when any provider grant exists;
3. it records, in a row no runtime role can change, the operator who ran it and the reason;
4. it names a Principal that already exists, minted by the Identity Control API's ceremony, and creates no identity.

Every later grant, and every revocation, is made by a provider through the API, with a reason.

**A projection consumer is a workload Principal this platform registered.** The consumer registry records the consumer's `principal_id`, and a token is a consumer's when:

- its `subject_type` is `workload`;
- it carries a `workload_owner`;
- its `principal_id` is that of an active registered consumer.

No role and no private claim names the consumer. It is not named by `client_id` either. A retired client registration frees its `client_key` (`ADR-IAM-001 §5.13`), so a `client_id` names whichever client holds it now, and RFC 9068 warns against authorizing on a client identifier a client can choose [R1]. A `principal_id` is never reused.

**Every actor is recorded by `principal_id`.** `STD-IAM-002 §3.2` makes `principal_id` the identifier a domain persists, and keeps `sub` out of every foreign key.

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

## 7. Compliance Impact

### Related Standards and Artifacts

- EAD-001 through EAD-006 v2.
- PAD-PLT-001 — Identity & Access Platform.
- PAD-PLT-002 — Organization & Tenancy Platform.
- SAD-001 — Scnehaux Identity Runtime.
- SAD-004 — Scnehaux Organization Control.
- SAD-012 — Scnehaux Organization Experience.
- ADR-IAM-001 — Adopt Keycloak Identity Kernel.
- STD-IAM-002 — Enterprise Token and Verification Profile.
- ADR-GLB-001 — Modular Monolith.
- ADR-GLB-002 — PostgreSQL RLS.
- ADR-GLB-016 — Transactional Outbox and durable delivery profiles.
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

### Alternative G — Read Provider and Consumer Authority from Realm Roles

**Benefits:** the first implementation did this, and Keycloak puts realm roles in `realm_access.roles` without configuration.

**Rejected because:** `STD-IAM-002 §3.2` keeps roles out of every access token, and a realm role would make the kernel hold a grant this platform owns (§5.1, `ADR-IAM-001 §5.6`). A role in a token also outlives its revocation until the token expires.

### Alternative H — Project the Grant and Carry Several Provider Scopes in One Claim

**Benefits:** one mechanism for every resource; the kernel's user-attribute mapper emits a multivalued attribute as an array [R5].

**Rejected because:** a token sent to the Organization Control API would carry `provider:identity-control` as well, a scope that means nothing to it. RFC 9068 §2.2.3 requires every scope in an access token to mean something to the resources its `aud` names, and RFC 8707 §2.2 has an authorization server downscope a token to what its resource needs [R1][R4]. It would also put a second copy of a grant this resource holds into the kernel.

### Alternative I — Name a Consumer by Its `client_id`

**Benefits:** `client_id` is in every RFC 9068 access token, and needs no lookup of a workload Principal.

**Rejected because:** a retired client registration frees its `client_key` for a later registration (`ADR-IAM-001 §5.13`), so the identifier would hand a retired consumer's authority to whichever client took the name next. `principal_id` is never reused.

## 9. References

The external sources §5.11 rests on, cited as `[Rn]`.

### Normative

- **[R1]** IETF RFC 9068, _JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens_, October 2021. <https://www.rfc-editor.org/rfc/rfc9068>. §2.2.3: every scope must mean something to the resources `aud` names; §5: an authorization server should prevent a client from registering an arbitrary `client_id`, or the client could pose as a privileged subject.

### Informative

- **[R2]** Google Cloud, _IAM overview_, accessed 2026-10-01. <https://docs.cloud.google.com/iam/docs/overview>. An allow policy is attached to a resource, and IAM checks the resource's allow policy when an authenticated principal accesses it.
- **[R3]** Kubernetes, _Authorization_, accessed 2026-10-01. <https://kubernetes.io/docs/reference/access-authn-authz/authorization/>. Authorization takes place in the API server, against the user and groups authentication established; access is denied by default.
- **[R4]** IETF RFC 8707, _Resource Indicators for OAuth 2.0_, February 2020. <https://www.rfc-editor.org/rfc/rfc8707>. §2.2: the authorization server should downscope a token to what the resource is able to process and needs to know.
- **[R5]** Keycloak, `UserAttributeMapper` API documentation, accessed 2026-10-01. <https://www.keycloak.org/docs-api/latest/javadocs/org/keycloak/protocol/oidc/mappers/UserAttributeMapper.html>. A multivalued user-attribute mapper sets every value of the attribute as the claim.
