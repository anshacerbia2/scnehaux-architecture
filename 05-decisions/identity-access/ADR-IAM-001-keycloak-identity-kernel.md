---
doc_meta:
  id: ADR-IAM-001
  title: ADR-IAM-001 Adopt the Keycloak Identity Kernel
  adr_type: replacement
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
  governed_by: [PAD-PLT-001]
---

# ADR-IAM-001: Adopting Keycloak as the Identity Kernel, and Keeping the Canonical Identifier

---

## 1. Title

Adopting Keycloak as the Identity Kernel, and Keeping the Canonical Identifier

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                 | Approver             |
| ---------- | -------- | ----------- | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |
| 2026-08-18 | accepted | replacement | Architecture Review Board | Enterprise Architect |

**This decision replaces its own earlier content.** Under this identifier the record
previously decided *Epoch-Based Session Management*: a `session_epoch` integer per
account, injected as a token claim, compared against a Redis-cached value by middleware,
with refresh-token rotation and a ten-second grace period.

That decision presupposed that Scnehaux owned the session engine and the credential store.
It does not. Ten technical designs across four repositories already cite this identifier as
*Adopt Keycloak Identity Kernel* and depend on the sections below, so the identifier's
content is corrected to the decision the estate actually made and builds against. The
epoch mechanism is recorded as withdrawn in §5.6, with the property it existed to
guarantee restated there.

## 3. Context

Identity is centralised by `EAD-006 §5.2`, which makes the identity provider the single
most security-critical component in the estate and an enterprise-wide single point of
failure by construction. The question is not whether to centralise it. The question is
whether to write it.

Writing it means owning an authentication engine, a credential store, a session engine, an
OIDC and OAuth 2.1 protocol implementation, MFA including WebAuthn, and identity
federation. Each is a large surface that is attacked continuously and where being subtly
wrong is a breach rather than a defect. `EAD-006 §4.2` records the outcome directly: *a
product-local authentication implementation became the weakest link and was breached.*

Adopting it means depending on a vendor for the estate's root of trust, and inheriting that
vendor's data model, upgrade cadence, and configuration surface. The cost that matters is
not licensing. It is that every identifier the vendor mints, if persisted by other domains,
becomes a foreign key the enterprise cannot change without a referential migration across
Membership, HCM, audit, evidence, and every analytical store.

So the real question is narrower and answerable: which parts must we own for the dependency
to stay reversible?

## 4. Decision Drivers

**The attack surface is the argument for adopting.** Argon2id parameters, constant-time
comparison, PKCE enforcement, replay detection, token binding, and WebAuthn attestation are
each a place where a subtle error is exploitable and silent. A mature implementation has had
those errors found by people other than us. This is the one component where breadth of
adversarial review is worth more than fit.

**The identifier is the argument for owning.** A vendor identifier persisted estate-wide
converts vendor replacement from a credential migration into an enterprise referential
migration. Minting our own canonical identifier costs one table and one uniqueness
invariant, and it is what keeps the adoption reversible.

**Authority must not migrate into the vendor.** `EAD-003` places authority with the owning
domain. A directory that starts holding Membership state, effective dates, or offboarding
progress has quietly become the authority for data another domain owns, and enterprise
recovery then depends on vendor recovery.

**A vendor is only as replaceable as its interface surface is narrow.** Every unsupported
interface, private endpoint, or direct database write we use is a coupling that a vendor
upgrade can break and that no compatibility test can protect.

## 5. Decision

We adopt **Keycloak** as the identity kernel, and retain the canonical enterprise
identifier and the control plane that governs the kernel.

### 5.1 Adopt the Engine, Own the Identifier

The kernel owns authentication ceremonies, credential material, authenticator enrollment,
session state, token issuance, the published verification material, federation, consent,
and the hosted login experience. No Scnehaux-authored code implements any of them.

Scnehaux mints `principal_id`, a UUIDv7 that is the only identity reference another domain
persists. The kernel stores it as an immutable user attribute; the Control Database holds
its uniqueness invariant, because Keycloak enforces no uniqueness on user attributes.

Exiting Keycloak therefore migrates credential material and protocol configuration. It does
not rewrite foreign keys.

### 5.2 The Kernel Owns Credential Material, and Only Supported Interfaces Are Used

Every interaction with the kernel MUST use a supported interface: the Admin REST API, the
OIDC and OAuth 2.1 protocol endpoints, and published extension points. A private
account-console endpoint, an unpublished internal API, and any direct write to the Keycloak
database are prohibited.

**No control-plane table may hold credential material the kernel already owns.** A client
secret, a password hash, a TOTP seed, a passkey value, or a refresh token MUST NOT be
persisted outside the kernel. A control-plane record may prove that a credential exists and
record when it was issued and when it expires — which is what rotation and audit need — and
MUST hold nothing an attacker could present.

Reads of credential material are prohibited on the same basis. The administration service
account holds no credential read authority.

### 5.3 Keycloak-Local Structures Are Bounded Projections, Never Authority

Keycloak Organizations, Groups, user attributes, and roles MAY carry projected context.
They MUST NOT become canonical enterprise authority for anything.

A projection is repaired in one direction, from the owning domain toward the kernel. No
repair path promotes a Keycloak-local value into authority, and no reconciliation writes to
the Keycloak database.

The consequence is stated so it is not rediscovered: a context present in Keycloak that the
owning authority does not grant is a **privilege-escalation finding**, not drift to repair
silently. Reaching that state requires either a defect in the projection path or a write
outside it.

### 5.4 Realm Topology: a Tenant Is Not a Realm

`Tenant = Realm` is prohibited as the default model. The estate runs a **small, fixed number
of realms**, and tenancy is a claim inside a token.

A realm per Tenant multiplies realm configuration, issuer identity, and key custody by
customer count, and forces every consumer to resolve which issuer to trust per request.
Tenant count, load, and organisational preference are not realm-splitting criteria.

An additional realm is justified only by a genuinely separate trust anchor: a distinct
issuer identity with its own key custody and its own administrative separation.

### 5.5 The Control Service Mediates, and Holds the Sole Administration Credential

The Keycloak administration credential exists in the Identity Control Service and nowhere
else in the estate. It is scoped to the narrowest role set permitting user creation,
attribute write, user search, enable and disable, context projection, session enumeration
and removal, client management, and credential rotation.

Every enterprise identity operation transits the Identity Control API rather than the
kernel directly, because that is where enterprise authorization, canonical identifier
resolution, last-authenticator guards, idempotency, reason capture, and evidence
publication live. A caller reaching the kernel directly bypasses all six.

### 5.6 Session Revocation, and the Withdrawn Epoch Mechanism

**The `session_epoch` mechanism is withdrawn.** It is not implemented, and implementing it
would be harmful rather than redundant: a second epoch authority that the kernel does not
consult means a token rejected by one path is accepted by the other, and the resulting
disagreement is silent.

The property that decision existed to guarantee survives: **revoking access MUST NOT
require scanning or deleting per-session rows.** It is realized by two constant-time
operations the kernel does consult, applied in this order:

1. Remove the projected context, so the next authentication cannot assert it.
2. Remove the kernel sessions, so a refresh cannot mint a fresh token past the removal.

Reversing the order leaves a window in which a session still exists and the context is
still projected, so a refresh inside it mints a token asserting the revoked context.

Refresh-token rotation and replay detection remain mandatory and are the kernel's session
engine to provide. Redis is not a mandated component of this architecture.

### 5.7 Extension and Configuration Policy

**Extension points, cheapest first.** An extension is chosen from this hierarchy and MUST
justify skipping a cheaper option:

1. Realm and client configuration.
2. A declarative user profile.
3. A theme.
4. A published Service Provider Interface implementation.

**Every extension** MUST be built from source in a repository we control, MUST be signed,
MUST declare its own source repository, MUST declare the kernel version range it supports,
and MUST contain no product business logic. A binary extension of unknown provenance runs
with the kernel's privileges over every credential in the enterprise.

**Unmanaged Admin Console changes to controller-owned configuration are prohibited.** Realm
definitions are rendered from source and applied by the pipeline only, above local
development. The pipeline diffs the rendered definition against the running instance on
every run, and an out-of-band change is a finding rather than a state to absorb — an upgrade
applied on top of undeclared drift produces a state no artifact describes.

### 5.8 Preview Features Are Disabled

Every Keycloak preview and experimental feature is disabled. Enabling any one requires its
own approved decision record naming the feature, the reason, and the accepted upgrade risk.

A preview feature carries no compatibility guarantee across releases. Depending on one in
the estate's root of trust means an upgrade can remove a capability that authentication
depends on, and the removal is legitimate rather than a regression.

## 6. Consequences

### Positive

- **The largest attack surface is maintained by people other than us**, with adversarial review far broader than this organisation could fund.
- **Reversibility is bounded.** Vendor replacement migrates credentials and protocol configuration, not enterprise foreign keys.
- **Credential blast radius is contained** to one process holding one narrow credential.
- **No second session authority exists**, so revocation cannot disagree with itself.
- **Upgrades are testable.** A narrow supported-interface surface plus a rendered realm definition make a compatibility suite meaningful.

### Negative

- **A vendor sits at the root of trust**, with its upgrade cadence and its configuration model.
- **Two containers instead of one**, with a projection between authority and kernel and therefore an eventual-consistency window.
- **Configuration is a first-class artifact.** Realm definitions must be rendered, diffed, and versioned, because the console is no longer the source of truth.
- **The identifier costs a table and an invariant** that a single-identifier design would not need.

### Tradeoffs

We trade fit and directness for adversarial maturity in the one component where a subtle
error is a breach, and we pay one table plus one projection to keep the dependency
reversible.

### Operational Impact

Requires realm-definition rendering and drift detection in the pipeline, an upgrade
compatibility suite gating promotion, and monitoring of projection delay and drift
findings. Removes the operational burden of running a credential store, a session store,
and a signing path.

### Security Impact

Credential handling moves to a hardened implementation. The administration credential is
contained in one process. The compensating obligations are explicit: the console is closed
as an administration path, extensions are signed and provenance-tracked, preview features
are off, and a projected context without authority is escalated rather than repaired.

### Scalability Impact

Token verification is local to each consumer, so the kernel is not on any consumer's
per-request path. Administrative throughput is bounded by the Admin API, which is why
reconciliation sweeps are rate-limited below the capacity reserved for authentication.

## 7. Compliance Impact

### Related Standards

- [Enterprise Security Architecture (EAD-006)](../../01-enterprise/EAD-006-enterprise-security-architecture.md) — centralised identity and the degradation contract
- [Enterprise Data Ownership & Topology (EAD-003)](../../01-enterprise/EAD-003-enterprise-data-ownership-and-topology.md) — authority stays with the owning domain
- [Identity Security Standard (STD-IAM-001)](../../02-standards/identity-access/STD-IAM-001-identity-security.md) — the controls this kernel is configured to exhibit
- [Token and Verification Profile (STD-IAM-002)](../../02-standards/identity-access/STD-IAM-002-token-and-verification-profile.md) — the contract the kernel issues against
- [Token Signing and Key Lifecycle (ADR-IAM-002)](ADR-IAM-002-token-signing.md) — the single `PS256` baseline and the key lifecycle
- [Organization Authority and Keycloak Projection (ADR-ORG-001)](../organization-tenancy/ADR-ORG-001-organization-authority-and-keycloak-projection.md) — who may write the projection

### Compliance Status

Compliant.

### Required Waivers

None. `ADR-IAM-003`, which bounded Argon2id hashing concurrency inside a Scnehaux process,
is deprecated by this decision: the hashing it protected happens inside the kernel, so the
process-level guard has no surface to protect.

## 8. Alternatives Considered

### Alternative A: Build the Identity Provider In-House

- **Pros**: exact fit, no vendor in the trust path, no projection and no eventual-consistency window, and full control of the upgrade cadence.
- **Cons**: requires owning an authentication engine, credential store, session engine, OIDC and OAuth 2.1 implementation, MFA including WebAuthn, and federation. Each is continuously attacked and each fails silently when subtly wrong. `EAD-006 §4.2` records a breach from exactly this posture.
- **Why Rejected**: the surface is too large to review adequately at this organisation's size, and the failure mode is a breach rather than a defect. This is the alternative the previous architecture chose, and reversing it is the substance of this decision.

### Alternative B: Adopt Keycloak and Use Its Identifier as the Enterprise Reference

- **Pros**: one identifier, no mapping table, no uniqueness invariant, no reconciliation for unmapped Principals.
- **Cons**: every domain that persists it — Membership, HCM, audit, evidence, analytics — binds a foreign key to a vendor value. Replacing the vendor becomes an estate-wide referential migration rather than a credential migration.
- **Why Rejected**: it makes an otherwise reversible adoption irreversible, for a saving of one table.

### Alternative C: Adopt Keycloak and Let It Hold Membership Authority

- **Pros**: no projection, no drift, no reconciliation, and no eventual-consistency window.
- **Cons**: Membership carries versions, effective dates, invitation provenance, and offboarding state that a directory does not model. Authority inside the vendor couples enterprise recovery to vendor recovery, and violates `EAD-003`.
- **Why Rejected**: authority belongs to the owning domain. Argued further in `ADR-ORG-001 §8` Alternative B.

### Alternative D: Retain the Session Epoch Alongside the Kernel

- **Pros**: constant-time global revocation expressed in our own code, independent of kernel behaviour.
- **Cons**: creates a second session authority the kernel does not consult, so the kernel would issue and refresh tokens the epoch check rejects while its own session remains valid. The two disagree silently, and an operator cannot tell which is in force.
- **Why Rejected**: a revocation control that two components answer differently is worse than either component answering alone. §5.6 keeps the property and drops the mechanism.

### Alternative E: A Realm per Tenant

- **Pros**: hard configuration isolation between customers, and a per-Tenant blast radius for realm-level misconfiguration.
- **Cons**: multiplies issuer identity and key custody by customer count, forces per-request issuer resolution into every consumer, and makes realm upgrades a per-customer operation.
- **Why Rejected**: tenancy is a claim, not a trust anchor. Fixed in §5.4.
