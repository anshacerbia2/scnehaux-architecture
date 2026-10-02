---
doc_meta:
  id: ADR-IAM-001
  title: Adopt Keycloak as the Scnehaux Identity Protocol and Authentication Kernel
  adr_type: foundational
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

| Date       | Status   | ADR Type     | Reviewers                                  | Approver               |
| :--------- | :------- | :----------- | :----------------------------------------- | :--------------------- |
| 2026-08-11 | accepted | foundational | Identity, Security, Platform, Architecture | Architecture Authority |

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
- Support OAuth 2.0, OpenID Connect, SAML, MFA, passkeys, sessions, federation, and administration through a mature implementation [R9][R10][R11][R13][R16].
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

The pinned release provides each of these through a documented feature or a supported specification [R16][R17][R19].

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

The Control Service SHALL use supported Keycloak interfaces [R22][R23]. It SHALL NOT write directly to the Keycloak database or duplicate authoritative Principal, credential, or session records.

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

Keycloak Organizations, Groups, attributes, or roles MAY be used only as bounded local projections or protocol constructs. Organizations is a supported feature that brings multi-tenancy within one realm [R17][R19], which is exactly why it must not become the Tenant authority. They SHALL NOT become canonical enterprise authority without a replacement ADR and PAD/EAD review.

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

Keycloak Authorization Services, which include a policy decision point [R24], SHALL NOT become the universal enterprise PDP without a replacement architecture decision.

**A provider scope is an Organization grant, never a kernel-owned authority, and it is projected to the resource that checks it, not into the kernel** (`ADR-ORG-002 §5.3`). This replaces the kernel projection this section first decided. That projection was never built, and a claim would outlive an activation ended early until its token expired.

`STD-IAM-002 §3.1.1` requires a provider-scope token to carry a `provider_scope` claim naming a bounded provider authority. The claim is permitted here as "a claim required by an approved consumer contract", and the authority behind it is not this platform's to create: `PAD-PLT-002 §3.1` places provider cross-tenant scope in the Tenancy Administration context, and `ADR-ORG-001 §5.1` makes organization-administrative roles the Organization Platform's sole authority.

The grant and its activations travel Organization's projection to the Identity Control Service, which reads them from its own database for each request (`ADR-ORG-001 §5.7`, `ADR-ORG-002 §5.3`):

```text
Organization authoritative grant and activation
    → canonical event / snapshot, priority lane for an end or a revocation
    → Scnehaux Identity Control Service, as a registered projection consumer
    → its own database, read per request by principal_id
```

Granting a provider scope by writing the kernel attribute directly is prohibited, for the same reason a direct Membership write is: it would make the kernel a second authority for a fact Organization owns, and `PAD-PLT-002 §3.3` invariant 22 requires cross-tenant administration to carry explicit scope, elevated assurance, and evidence — none of which a kernel attribute records.

**A grant is projected only to a resource that does not hold it.** The projection exists so that a resource outside Organization, such as the Identity Control API, can check a provider grant from the token without calling Organization on every request. The Organization Control API holds the grants itself, so it checks `provider:organization-control` from its own record for each request, by the token's `principal_id`, and that scope is never projected (`ADR-ORG-001 §5.11`). This is how Google Cloud IAM and Kubernetes decide access: the token says who the caller is, and the resource reads the policy it holds [R34][R35]. Projecting the scope as well would put in every provider token a claim that means nothing to the resource it is sent to, which RFC 9068 forbids for `scope` and RFC 8707 tells an authorization server to trim [R12][R36]. A Principal's `provider_scope` therefore names at most one scope, the one a resource outside Organization checks, and the attribute stays single-valued.

**The bootstrap ceremony is the one exception, and it is bounded by its own record.** §5.11 creates the first Principal before any Organization authority can exist, and a first Principal holding no provider authority could call nothing: the ceremony would produce an identity that cannot reach the API that issues every later one. The ceremony therefore records exactly one local emergency grant for exactly one Principal, in the same immutable row that names the operator and the reason. That grant is retired once the projection delivers an emergency grant for `provider:identity-control` (`ADR-ORG-002 §5.4`), and every grant after it is Organization's.

Recording this rather than deciding it later matters because the alternative was already in the working harness: a script setting the attribute directly, which is indistinguishable from the prohibited path once it is normal.

### 5.7 Extension Policy

Preferred mechanisms:

- standard configuration;
- supported Admin REST APIs;
- standards-based protocols;
- supported theme and user-interface extension points [R33];
- a minimal event-listener extension where required [R22];
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

- Every deployment runs the latest minor Keycloak release, pinned by digest through the technology lifecycle process. Keycloak supports only the latest minor release: when a new one is published, the previous one receives no more patches, and there is no long-term-support line [R25]. A new minor release is adopted once the kernel's compatibility suite passes against it, and a security patch release through the kernel's accelerated security-release path. The pin moved to 26.7.5 on 2026-10-01 by that path. Among its fixes is CVE-2026-93999, a token-exchange refresh that kept issuing tokens for a disabled audience client [R37], which bears on §5.13 because a suspension disables the client.
- Preview features are disabled by default and require a separate ADR. Keycloak says they are not recommended for production and may change or be removed [R18].
- Initial high availability is one cluster across availability zones [R20], in a single region unless evidence requires more.
- Multi-cluster v2 and the stateless mode are preview in the pinned line [R18][R21] and are not used. Multi-cluster v1 is supported [R20], and is adopted only when evidence requires more than one region.
- Database, key continuity, backup, restore, upgrade, vulnerability response, conformance, and disaster-recovery behavior are owned by the Identity Platform Team.
- Products validate approved tokens locally [R12].

### 5.9 Legacy Go IAM

The existing Go IAM SHALL enter containment and migration mode:

- patch active critical security liabilities;
- freeze new OAuth/OIDC, session, credential, federation, and token-engine features;
- preserve migration, compatibility, canonical event, and integration code that remains useful;
- migrate consumers and data through a governed dual-run/cutover plan;
- retire the custom protocol engine after acceptance evidence and rollback criteria are met.

### 5.10 Credential Containment and the Sole Administration Credential

The Keycloak administration credential SHALL exist in the Identity Control Service and nowhere else in the estate. It SHALL be scoped to the narrowest role set permitting its operations [R15][R17] — user creation, attribute write, user search, enable and disable, context projection, session enumeration and removal, client management, and client public-key registration and rotation (§5.12) — and SHALL carry no realm administration and no credential-read authority.

Every enterprise identity operation SHALL transit the Identity Control API rather than the kernel directly, because that is where enterprise authorization, canonical identifier resolution, last-authenticator guards, idempotency, reason capture, and evidence publication live. A caller reaching the kernel directly bypasses all six.

`ADR-ORG-001` makes the prohibition structural for the Organization authority by giving it neither the credential nor a network route to the kernel.

**Clarifying §5.5.** The prohibition on a second Go-owned Principal database bars a second credential store, authenticator store, or session store. It does not bar the Control Database, which holds the canonical `principal_id`, its uniqueness invariant, the binding to a kernel user, and the payload needed to reconstruct an interrupted creation. That table holds no credential, no authenticator, and no session, and the kernel remains the physical system of record for all three. Recorded because the clause as written reads as forbidding the mapping table that `TDD-identity-control-001` specifies.

### 5.11 The First Principal Is Created by an Evidenced Ceremony

§5.10 makes the Identity Control API the sole path to an enterprise identity operation, and `TDD-identity-control-001` closes every other Principal creation path by realm configuration. Both are correct, and together they leave a realm with no way to reach its first Principal: the API requires a caller holding a `principal_id`, and only the API issues one. The cycle has no entry point, and this was found by standing the service up rather than by reading it.

**The entry point is a single-use ceremony performed by the Identity Control Service itself.** It is a command on the deployable, not an endpoint, and it satisfies four requirements:

1. **It can succeed at most once per Control Database, enforced by the database.** The ceremony claims a row whose primary key admits exactly one value. Two concurrent ceremonies produce one Principal, and a second ceremony after the first is refused by a constraint rather than by a check the code could be rewritten to skip.
2. **It refuses to run against a populated registry.** Emptiness of `principal_mapping` is asserted in the claiming transaction, so the ceremony cannot be used later to insert a Principal into a running estate.
3. **It names the human who ran it and why, and that record is immutable.** The evidence row is insert-only: the runtime role holds no `UPDATE` and no `DELETE` on it. A retry reuses the recorded operator and reason rather than supplying new ones, so the second attempt cannot rewrite who is on record.
4. **It creates the Principal through the ordinary path.** The ceremony calls the same provisioning sequence the API calls, under an idempotency key stored in the evidence row, so a crash mid-ceremony recovers rather than producing a second Principal, and the identifier is issued by the authority that owns it.

The ceremony holds no credential. It creates the kernel user with a mandatory credential-setting action, so the first human interaction establishes the credential and the ceremony never handles one.

**This is an entry point, not an exception.** No standing capability is created, nothing is exempted from authorization afterwards, and the ordinary path is unchanged. An out-of-band `INSERT` into `principal_mapping` remains prohibited, and `ADR-ORG-001` is why: an identifier that entered the canonical registry without a recorded decision is indistinguishable from one an attacker placed there.

### 5.12 Confidential and Workload Clients Authenticate with Registered Keys

A confidential or workload client proves which application is asking at every token request. The way it does so SHALL meet three requirements:

- rotation without an outage, so that rotation keeps happening;
- revocation that takes effect at once;
- no Scnehaux component, the kernel included, holding material that would let a reader act as the client.

**The client SHALL authenticate with a signed JWT client assertion (`private_key_jwt`, RFC 7523 [R1]).** The client generates an RSA key pair and keeps the private key in its own deployable's approved secret custody. The Identity Control Service registers the public key on the kernel client as a JWKS held on the client, not fetched from a URL, so no application has to serve a key endpoint to be a client. `STD-IAM-001 §3.2` states the rule, the algorithm, and the assertion requirements.

The mechanism is supported in the pinned kernel and needs no preview feature and no extension. `identity-kernel`'s compatibility suite answered it against 26.7.4 on 2026-09-29 (compat run 36606481342), and every step held:

- two registered keys are accepted together;
- a key removed from the client is refused on the next request;
- an assertion presented twice is refused.

The suite keeps asserting it on every upgrade.

Its consequences:

- **Rotation is add-then-remove.** The new public key is registered, the previous one becomes retiring, and it is removed at the end of a bounded overlap. The kernel accepts either key in between.
- **Nothing secret is ever shown.** Registration and rotation carry a public key in and return no secret. There is no once-only display to lose, and a lost private key is replaced by registering a new one.
- **A kernel breach exposes no client.** The kernel holds public keys only, where a client secret would be readable by its administrators and present in its database backups.

**Bootstrap clients authenticate with keys too.** The clients created to stand the registration path up are made by a bootstrap script, because the Identity Control Service cannot register them before it exists:

- the Identity Control Service's own Admin API clients;
- the first BFF clients;
- the kernel's realm-apply service account.

The script registers the public key its operator supplies, so these clients authenticate with `private_key_jwt` from their first request. No shared environment, development included, holds a client secret. The only exemption `STD-IAM-001 §3.2` keeps is a test fixture inside a throwaway kernel. It was first written as a development exemption for bootstrap clients, and removed before anything relied on it, so that development runs the mechanism production will.

**A bootstrap client comes under registration by an explicit adoption, once the Identity Control Service runs.** Registration refuses a `client_key` that an unregistered Keycloak client already holds, because adopting a client on a matching name would take over a client someone else configured. The bootstrap clients are that case by construction. So their path is a separate command, and it holds to five rules:

1. **One client, named, with its whole desired state.** The command names one client and declares everything a registration declares, the Application reference included. Nothing is adopted because its name matched.
2. **Plan before taking over.** A plan reports, per reconciled field class, how the live client differs from the declaration, and changes nothing.
3. **The declaration matches what the client runs with.** Adoption proceeds only when the redirect URIs and the client's keys, the field classes the reconciler blocks on, do not differ. A difference in a field class the reconciler repairs converges only when the request names it.
4. **Only a key-authenticated client is adopted.** The client must already authenticate with `private_key_jwt`, hold no usable secret, and hold exactly the public keys the declaration names. Adoption is how the service learns which keys a running client holds, and it will not learn them from a client it cannot see authenticating that way.
5. **The adoption is recorded, insert-only.** The record names who adopted which client, when, why, and what the client held at that moment.

**The Identity Control Service's own Admin API clients are not adopted.** They are the credentials the service reconciles with. They are created before it exists and held nowhere else (§5.10), so the service is not their controller, and a drift repair the service applied to its own credential could cut off its access to the kernel. These two clients are excluded from the rule that disables a Keycloak client no registration describes. The service excludes them by the identifiers its configuration already names, and it excludes the clients Keycloak creates in every realm the same way. The realm-apply service account lives in the master realm and is outside the realm the service manages.

An adopted client is a registration like any other from then on. It is not released back to being unmanaged; §5.13 decides how every registration stops, adopted or not.

### 5.13 A Registration Stops by Suspension, and Is Removed Only After One

A registered client is stopped through the Identity Control Service in two steps, so that a stop can be undone until the operator decides it is final. The steps rest on what the pinned kernel does to a stopped client. `identity-kernel`'s compatibility suite answered that against 26.7.4 on 2026-09-30 (compat run 36765561606):

- a disabled client gets no token, and its refresh tokens are refused, but they are accepted again once the client is enabled;
- a not-before set on the client while it is disabled keeps every refresh token issued before it refused after the client is enabled again, and a new sign-in works;
- a deleted client gets no token, its refresh tokens are refused, its service-account user is deleted with it, and a new client may then take its `clientId`;
- an access token issued before either stop still verifies at a consumer until it expires.

**Suspension contains; it does not pause.** `:suspend` disables the kernel client and sets its not-before in the same step. It keeps the client's keys and its registration. A refresh token that a compromised client held is therefore ended, not held in waiting. Containment prevents an incident from expanding, and eradication removes the persistence mechanisms and entry points it left [R2]; a suspension whose restore revived every earlier session would leave one. `:restore` enables the client again. Its users sign in again; a workload, which authenticates with its key on every request, notices nothing. Until the registration is restored, the reconciler holds the client disabled and repairs a console re-enable as drift.

**Retirement is final, and comes only after a suspension.** `:retire` is refused for a registration that is not suspended. Reversible first, then permanent, is how Google Cloud and AWS IAM ask for a service account or an access key to be removed [R7][R8]: a dependency the operator did not know about breaks during the suspension, while the client can still be restored. `:retire` removes the client's keys, then deletes the kernel client. The registration, its keys, and its findings remain as the record. Deleting the client, rather than leaving it disabled, lets the `client_key` be registered again, and leaves no kernel client that no live registration describes.

**A resource is retired without a suspension.** A protected resource holds no credential and is issued no token, so there is nothing for a suspension to stop. It is refused retirement while an active registration names it in its audience.

**A stop does not reach an access token already issued.** Consumers verify access tokens locally, so a token issued before a stop is outside the kernel's reach until it expires. The exposure is bounded by the audience's lifetime class (`STD-IAM-002 §3.3`), and `SAD-001 §7.7` declares it as the Client or grant revocation class.

**A workload's client is stopped through its workload.** Deleting a client deletes its service-account user, and that user is the workload's identity in the kernel. So the registration path refuses to suspend, restore, or retire a workload's client, and the workload lifecycle stops the client and its Principal together.

Every stop names its reason and the calling Principal, and is recorded (`STD-IAM-001 §3.8`).

## 6. Consequences

### Positive

- Reduces the amount of security-critical protocol code owned by Scnehaux.
- Shortens time to a mature authentication, session, federation, and OAuth/OIDC foundation.
- Preserves Scnehaux domain ownership and enterprise authority boundaries.
- Avoids duplicate Principal authority.
- Retains Go for the differentiated control, reconciliation, integration, and migration layer.
- Provides a broad ecosystem, documented administration APIs, and established operational guidance.
- Improves interoperability and conformance potential. The last OpenID certification Keycloak lists is for 18.0.0 [R16], so the pinned release's conformance is asserted by the kernel's own compatibility suite, not by a certification.

### Negative

- Introduces a Java/Quarkus runtime into a Go-default platform portfolio [R27].
- Requires Keycloak-specific operational skill, upgrades, cache/session understanding, and security response [R26].
- Some Scnehaux requirements may require adapters or controlled extensions.
- Keycloak's internal data model and APIs create migration and upgrade coupling; preview features and non-public APIs may change at any release [R25].
- Organization or role features may tempt teams to violate authority boundaries.
- High availability and multi-region operation are not free and require tested database/cache architecture [R20].

### Operational

- The Identity team operates Keycloak, its database, configuration, keys, upgrades, extensions, and runbooks.
- A Scnehaux Control Service and Identity Experience system remain required.
- Technology radar and vulnerability-management processes must include Keycloak and its extensions.
- Every upgrade requires compatibility, conformance, migration, and rollback evidence.
- Restoring a suspended BFF signs its users out: they sign in again, because the suspension ended their refresh tokens (§5.13).
- Retirement deletes the kernel client and cannot be undone there. The record stays in the Control Database.

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

**Benefits:** modern API-first operation, strong native B2B organization/project model, an implementation in Go, simpler stateless runtime profile [R30][R31].

**Rejected for the current boundary because:** its primary native differentiation overlaps more directly with Scnehaux Organization, project/application, and role-assignment authorities. Preserving Scnehaux's narrow IAM boundary would reduce those benefits and increase model translation. Licensing and vendor-model coupling also require additional consideration: ZITADEL moved from Apache-2.0 to AGPL-3.0-only with version 3.0 [R29], where Keycloak remains Apache-2.0 [R28].

### Alternative D — Managed Proprietary Identity SaaS

**Benefits:** reduced infrastructure operation, support, rapid capability availability.

**Rejected for the current phase because:** cost, data/control requirements, product lock-in, and enterprise integration strategy have not been justified. This remains a future option if operational capacity becomes the dominant constraint.

### Alternative E — A Standing Break-Glass Identity for the First Principal

Provision a reserved identity with the realm, holding a fixed `principal_id`, and use it to create the first real operator. This was the first candidate considered for §5.11.

- **Pros**: needs no new code — the ordinary API creates the first Principal like any other, and `SAD-001` already establishes an evidenced break-glass posture for the Admin Console, so the concept is not new to the estate.
- **Cons**: it creates a credential that can create Principals _forever_, which is a permanent standing authority in exchange for solving a problem that occurs once. Its `principal_id` is in no registry, so every downstream consumer must tolerate an identifier the authority cannot resolve. And because it must exist before the service does, it can only be placed by the out-of-band write this architecture prohibits — the problem is relocated, not solved.
- **Why Rejected**: a one-time problem does not justify a standing capability, and NIST treats emergency accounts as ones to remove or disable after a bounded period [R15]. Standing emergency accounts are recommended for recovering an existing tenant from lockout [R32], which is a different problem from creating its first Principal, and `SAD-001`'s console break-glass is this estate's answer to that one. It is not a precedent for this either: it is time-bounded, group-scoped, and evidenced per session, and it operates on the kernel rather than minting canonical identifiers. §5.11 keeps the property that matters — a legitimate entry point — while the capability expires by construction after one use.

### Alternative F — Client Secrets with the Kernel's Secret-Rotation Policy

Keep client secrets, and enable the kernel's `client-secret-rotation` feature. Under that feature a regenerated secret leaves the previous one valid for a configured period. This was the design `TDD-identity-control-003` first specified for §5.12.

- **Pros**: the most widely supported client authentication method in any library, and the smallest change to the designs as first written.
- **Cons**: the pinned kernel classifies the feature as preview, "not recommended for use in production" and liable to change or removal [R18]. The secret is returned to kernel administrators by the Admin API [R23] and is present in kernel database backups, where asymmetric client authentication leaves the server no secret to hold [R14].
- **Why Rejected**: `§7 Required Waivers` requires its own ADR or exception for any preview feature. Building credential rotation on one would put every confidential client's availability on a feature the vendor does not support.

### Alternative G — Client Secrets Rotated Without Overlap

Keep client secrets without the preview feature. Rotation regenerates the secret, and the old one stops working at once.

- **Pros**: supported, simple, and the most common kernel deployment in practice.
- **Cons**: every rotation is an outage for the client, from the moment the secret changes until the new one is deployed.
- **Why Rejected**: a rotation that causes an outage is a rotation teams postpone, which leaves long-lived secrets in place. That is the condition `STD-IAM-001 §3.7` exists to prevent. The supported alternative, §5.12, gives the overlap without the outage.

### Alternative H — Adopt an Existing Client When Its clientId Matches a Registration

Registration would adopt a Keycloak client that already holds the requested `client_key`, instead of refusing it.

- **Pros**: the bootstrap clients would come under registration without a second command.
- **Cons**: an equal name is not ownership. Whoever created a client under that name would have it adopted with whatever keys, secret and redirect URIs it holds, and the reconciler would then defend that configuration as desired state. The desired-state systems whose adoption is documented require each resource to be named explicitly: Terraform's `import` block [R3], CloudFormation's resource import [R4], Crossplane's `external-name` [R5]. Where they adopt by name or label, they refuse a resource another owner already holds.
- **Why Rejected**: a takeover path that looks like a convenience. Explicit adoption (§5.12) keeps the convenience and holds the client to its declaration and its keys.

### Alternative I — Register the Service's Own Admin API Clients

The Identity Control Service would register its own two Admin API clients, like any other client.

- **Pros**: the unmanaged-client rule would need no exclusion.
- **Cons**: the service would be the controller of the credentials it controls with. A repair it applied to one of them could remove its own access to the kernel, and no registration profile describes a client whose authority is a set of kernel administration roles.
- **Why Rejected**: a controller's own credentials are bootstrapped outside what it controls. The exclusion is narrow, and it is named by configuration the service already holds.

### Alternative J — Release an Adopted Client Without Deleting It

The Identity Control Service would stop managing an adopted client and leave it running in the kernel, as Terraform's `removed` block with `destroy = false` [R6], and a Crossplane managed resource whose management policies omit `Delete` [R5], leave the real resource in place.

- **Pros**: a mistaken adoption could be undone without touching the running client.
- **Cons**: those tools offer it to hand a resource to another tool or team. This estate has no other legitimate controller of a client (§5.7). A released client is unmanaged: reported on every sweep, and disabled once the unmanaged rule runs in `disable`. That is a retirement without the key removal and without the record. A wrong declaration is corrected by changing the registration, not by releasing it.
- **Why Rejected**: it is a stop with less evidence than the stops §5.13 already provides.

### Alternative K — Retire by Disabling and Keeping the Kernel Client

`:retire` would remove the keys and disable the client, as a suspension does, and never delete it.

- **Pros**: nothing irreversible happens in the kernel.
- **Cons**: the live client keeps holding its `clientId`, so the `client_key` could never be registered again. A disabled client that no live registration describes is exactly what the reconciler reports as unmanaged, so every retirement would leave a permanent finding. And the reversible state it offers is the suspension, which already precedes a retirement.
- **Why Rejected**: it gives the retirement nothing the suspension does not, and costs the name and a finding that never converges.

### Alternative L — Suspend by Disabling the Client Only

`:suspend` would disable the client and leave its sessions alone.

- **Pros**: a restore would resume every session, and no user would sign in again.
- **Cons**: the compatibility suite shows that the refresh tokens a disabled client held are accepted again when it is enabled. A suspension that contains a compromised client would hand the stolen refresh tokens back at the restore. That is an entry point left in place, which eradication exists to remove [R2].
- **Why Rejected**: a stop used for containment must not resume what it stopped.

## 9. References

These are the external sources this decision rests on. In-repository evidence, such as a compatibility run, is cited inline where it is used. Keycloak pages are cited at 26.7.5, the pinned release, where a versioned page exists.

### Normative

- **[R1]** IETF RFC 7523, _JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants_, May 2015. <https://www.rfc-editor.org/rfc/rfc7523>. The `private_key_jwt` client assertion §5.12 requires.
- **[R2]** NIST SP 800-61 Rev. 3, _Incident Response Recommendations and Considerations for Cybersecurity Risk Management_, April 2025, RS.MI-01 and RS.MI-02. <https://csrc.nist.gov/pubs/sp/800/61/r3/final>. Containment prevents an incident's expansion; eradication eliminates persistence mechanisms and entry points, including by disabling breached accounts.

- **[R9]** IETF RFC 6749, _The OAuth 2.0 Authorization Framework_, October 2012. <https://www.rfc-editor.org/rfc/rfc6749>.
- **[R10]** OpenID Foundation, _OpenID Connect Core 1.0 incorporating errata set 2_, December 2023. <https://openid.net/specs/openid-connect-core-1_0.html>.
- **[R11]** OASIS, _Assertions and Protocols for the OASIS Security Assertion Markup Language (SAML) V2.0_, March 2005. <https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf>.
- **[R12]** IETF RFC 9068, _JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens_, October 2021. <https://www.rfc-editor.org/rfc/rfc9068>. §4: a resource server validates the token itself; §2.2.3: every scope in an access token must mean something to the resources its `aud` names.
- **[R13]** W3C, _Web Authentication: An API for accessing Public Key Credentials, Level 3_, Recommendation, accessed 2026-09-30. <https://www.w3.org/TR/webauthn-3/>.
- **[R14]** IETF RFC 9700 (BCP 240), _Best Current Practice for OAuth 2.0 Security_, January 2025. <https://www.rfc-editor.org/rfc/rfc9700>. §2.5: with asymmetric client authentication the server holds no symmetric key.
- **[R15]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and Organizations_ (release 5.2.0). <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. AC-6 least privilege; AC-2(2) removing or disabling temporary and emergency accounts after a set period.

### Informative

- **[R3]** HashiCorp, Terraform `import` block, accessed 2026-09-30. <https://developer.hashicorp.com/terraform/language/import>. Adoption names each resource explicitly.
- **[R4]** AWS, CloudFormation resource import, accessed 2026-09-30. <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import.html>. Adoption names each resource, and a resource another stack holds is refused.
- **[R5]** Crossplane, Managed Resources (v2.4), accessed 2026-09-30. <https://docs.crossplane.io/latest/managed-resources/managed-resources/>. `external-name` adoption, the `Observe` management policy, and management policies without `Delete`, under which deleting the managed resource leaves the external one.
- **[R6]** HashiCorp, Terraform `removed` block (v1.16), accessed 2026-09-30. <https://developer.hashicorp.com/terraform/language/block/removed>. `destroy = false` removes a resource from state without destroying it, to hand its management to another tool or team.
- **[R7]** Google Cloud, _Delete and undelete service accounts_, accessed 2026-09-30. <https://docs.cloud.google.com/iam/docs/service-accounts-delete-undelete>. Disable a service account instead of deleting it; a disabled one can be re-enabled.
- **[R8]** AWS, IAM _Update access keys_, accessed 2026-09-30. <https://docs.aws.amazon.com/IAM/latest/UserGuide/id-credentials-access-keys-update.html>. Deactivate a key before deleting it, and reactivate it if something still uses it.
- **[R16]** Keycloak, _Supported specifications_, accessed 2026-09-30. <https://www.keycloak.org/securing-apps/specifications>. OpenID Connect Core supported, last certified with 18.0.0; SAML 2.0 supported.
- **[R17]** Keycloak, _Server Administration Guide_ 26.7.5. <https://www.keycloak.org/docs/26.7.5/server_admin/index.html>. Features; Organizations, "multi-tenancy within a realm"; the master realm; realm-management roles.
- **[R18]** Keycloak, _Enabling and disabling features_, accessed 2026-09-30. <https://www.keycloak.org/server/features>. Preview features are disabled by default, not recommended for production, and may change or be removed; `client-secret-rotation` and `stateless` are preview.
- **[R19]** Keycloak, _Release Notes_, accessed 2026-09-30. <https://www.keycloak.org/docs/latest/release_notes/index.html>. 26.0.0: Organizations fully supported; 26.4.0: passkeys supported.
- **[R20]** Keycloak, _High availability_ guides, accessed 2026-09-30. <https://www.keycloak.org/high-availability/introduction>. One cluster across availability zones; multi-cluster v1 supported, v2 preview.
- **[R21]** Keycloak blog, _Multi-Cluster v2 and Stateless Mode now in Preview_, July 2026. <https://www.keycloak.org/2026/07/multi-cluster-v2-and-stateless-mode>.
- **[R22]** Keycloak, _Server Developer Guide_ 26.7.5. <https://www.keycloak.org/docs/26.7.5/server_development/index.html>. The Admin REST API; the Event Listener and User Storage SPIs.
- **[R23]** Keycloak, _Admin REST API_ 26.7.5. <https://www.keycloak.org/docs-api/26.7.5/rest-api/index.html>. `GET .../clients/{client-uuid}/client-secret` returns a client's secret.
- **[R24]** Keycloak, _Authorization Services Guide_ 26.7.5. <https://www.keycloak.org/docs/26.7.5/authorization_services/index.html>. A policy decision point.
- **[R25]** Keycloak, `RELEASES.md`, accessed 2026-09-30. <https://github.com/keycloak/keycloak/blob/main/RELEASES.md>. Only the latest minor release receives patches; preview features and non-public APIs may change at any time.
- **[R26]** Keycloak, _Configuring distributed caches_, accessed 2026-09-30. <https://www.keycloak.org/server/caching>. Sessions persisted in the database; caching built on Infinispan.
- **[R27]** Keycloak, _Configuring Keycloak_, accessed 2026-09-30. <https://www.keycloak.org/server/configuration>. Built on Quarkus.
- **[R28]** Keycloak, `LICENSE.txt`, <https://github.com/keycloak/keycloak/blob/main/LICENSE.txt>, Apache-2.0; and CNCF, _Keycloak_ project page, <https://www.cncf.io/projects/keycloak/>, incubating since April 2023.
- **[R29]** ZITADEL, `LICENSING.md`, <https://github.com/zitadel/zitadel/blob/main/LICENSING.md>, and _Moving to AGPL 3.0_, March 2025, <https://zitadel.com/blog/apache-to-agpl>. AGPL-3.0-only from version 3.0.
- **[R30]** ZITADEL, _Organizations_ and _Projects_, accessed 2026-09-30. <https://zitadel.com/docs/guides/manage/console/organizations-overview>, <https://zitadel.com/docs/concepts/structure/projects>. An organization is comparable to a tenant; granted organizations manage role assignments.
- **[R31]** ZITADEL, _Principles_ and _Software Architecture_, accessed 2026-09-30. <https://zitadel.com/docs/concepts/principles>, <https://zitadel.com/docs/concepts/architecture/software>. API-first; stateless.
- **[R32]** Microsoft, _Manage emergency access admin accounts in Microsoft Entra ID_, updated June 2026. <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access>.
- **[R33]** Keycloak, _Working with themes_, accessed 2026-09-30. <https://www.keycloak.org/ui-customization/themes>.
- **[R34]** Google Cloud, _IAM overview_, accessed 2026-10-01. <https://docs.cloud.google.com/iam/docs/overview>. An allow policy is attached to a resource, and IAM checks the resource's allow policy when an authenticated principal accesses it.
- **[R35]** Kubernetes, _Authorization_, accessed 2026-10-01. <https://kubernetes.io/docs/reference/access-authn-authz/authorization/>. Authorization takes place in the API server, against the user and groups authentication established; access is denied by default.
- **[R36]** IETF RFC 8707, _Resource Indicators for OAuth 2.0_, February 2020. <https://www.rfc-editor.org/rfc/rfc8707>. §2.2: the authorization server should downscope a token to what the resource is able to process and needs to know.
- **[R37]** Keycloak, _Keycloak 26.7.5 released_, September 2026. <https://www.keycloak.org/2026/09/keycloak-2675-released>, and the GitHub release <https://github.com/keycloak/keycloak/releases/tag/26.7.5>. The security fixes in the patch release, CVE-2026-93999 among them.
