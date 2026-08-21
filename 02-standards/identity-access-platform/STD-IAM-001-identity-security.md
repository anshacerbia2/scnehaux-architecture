---
doc_meta:
  id: STD-IAM-001
  title: Enterprise Identity Security Standard
  owner: Enterprise Security Architect
  version: 2.1.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-22
---

# Enterprise Identity Security Standard (STD-IAM-001)

## 1. Objective & Scope

Define the mandatory security profile for Scnehaux Identity & Access implementations without coupling the enterprise standard to a custom password, session, token, or signing engine.

This standard applies to the Identity Runtime, Identity Control Service, federation adapters, OAuth/OIDC clients, workload identities, administrative identity experiences, and product-side token validation.

Business authorization, Tenant/Membership authority, Product permissions, and commercial entitlements remain outside Identity authority unless explicitly defined by their accountable domains.

## 2. Design Principles

- **Standards-based trust** — OAuth 2.0, OpenID Connect, SAML, WebAuthn, and federation behavior use approved protocol profiles rather than proprietary equivalents
- **Kernel over reimplementation** — credential hashing, authenticator storage, session lifecycle, token grants, and protocol runtime are delegated to the approved identity kernel where supported
- **Local verification by default** — normal product requests validate signed tokens locally and do not synchronously call Identity on every request
- **Least-context tokens** — tokens carry only audience-appropriate identity and operating context required by the consumer
- **Separation of authorities** — Principal/authentication, Tenant/Membership, Entitlement, and Product permission remain distinct
- **Fail secure** — loss of a dependency must never silently create new trust, privilege, or operating context

## 3. Normative Rules

### 3.1 Credential & Authenticator Security

- Passwords, passkeys, OTP secrets, recovery factors, and other authenticators MUST be stored and processed only by the approved identity kernel or an explicitly approved external identity provider
- Scnehaux services MUST NOT create a parallel credential database or custom password-verification engine when the approved kernel already owns that responsibility
- Credential policy MUST support modern password hashing, breached/weak credential controls where available, secure recovery, MFA, WebAuthn/passkeys, and step-up authentication according to assurance requirements
- Plaintext credentials, recovery secrets, private keys, and bearer tokens MUST NOT be logged
- Authentication endpoints MUST implement rate limiting, abuse detection, and bounded resource consumption

### 3.2 OAuth 2.0 / OpenID Connect Security Profile

- Authorization Code flow with PKCE using `S256` is REQUIRED for public browser and native clients
- **The Resource Owner Password Credentials grant is PROHIBITED for every client, confidential clients included.** OAuth 2.1 removes it, and the reason is structural rather than stylistic: the grant requires a client to receive and forward the Principal's password, which places credential material in a process that this standard §3.1 forbids from holding any. It also defeats MFA, WebAuthn, step-up, and every abuse control the kernel's authentication ceremony applies, because none of them are on the path
- A client MAY enable the grant in a local development environment that holds no production credential and issues no token another environment accepts. That exemption is a property of the environment, not of the client, and MUST NOT be carried into a shared environment by configuration
- Being a confidential client is not an exemption. Client authentication proves which application is asking; it says nothing about how the Principal proved who they are
- Redirect URIs MUST be explicitly registered and matched according to the approved client profile; open redirect patterns are prohibited
- Access tokens MUST be audience-bound and short-lived according to the approved token-lifetime class
- An access token MUST NOT exceed a 15-minute lifetime unless an approved token-lifetime class defines a longer bound for a named audience; any longer lifetime MUST be carried into the revocation enforcement delay of every affected revocation class
- Refresh tokens MUST use the approved identity kernel's rotation, reuse-detection, revocation, and session controls when refresh tokens are issued
- Client credentials and private client secrets MUST never be embedded in public browser or mobile applications
- Confidential clients MUST authenticate using an approved method appropriate to their threat model
- Token introspection MAY be used where opaque-token or active-state semantics require it, but normal signed-token validation SHOULD remain local when sufficient

### 3.3 Token & Claim Profile

- Every consumer MUST validate issuer, audience, signature, token type, expiry, and other mandatory protocol claims
- `sub` remains the protocol subject, MAY be pairwise or otherwise scoped per relying party, and MUST NOT be used as an enterprise foreign key by any Scnehaux domain
- Internal Scnehaux access tokens MUST carry the canonical enterprise `principal_id` claim defined by the Principal Identifier decision
- A protected resource accepting an internal-audience token MUST reject the token when `principal_id` is absent
- External, partner, and third-party token profiles MAY omit `principal_id`; such profiles MUST be identified by audience and validated against their declared external profile
- Tenant, Membership, Workspace, or operating-context claims MUST represent an authority-derived or approved projection, never untrusted browser input
- An access token MUST carry exactly one active Tenant context and at most one Workspace context; the set of Memberships held by a Principal MUST NOT be placed in a token, bounded or otherwise
- Business Product permissions SHOULD remain product-owned and MUST NOT be silently converted into IAM-owned authorization truth
- Claims containing sensitive identity or tenant context MUST be minimized by audience and data-classification need

### 3.4 Session & Revocation

- Session creation, refresh, logout, global logout, factor changes, credential reset, and high-risk administrative actions MUST be governed by the approved identity kernel and enterprise session policy
- Revocation requirements MUST define a measurable maximum enforcement delay appropriate to the affected risk class
- Maximum enforcement delay MUST be computed as `propagation_time + remaining_access_token_lifetime`; access token lifetime is therefore a security parameter of the revocation contract and MUST NOT be selected on performance grounds alone
- Every revocation class MUST declare which mechanisms enforce it, covering context-projection removal, kernel session removal, consumer projection update, and termination of long-lived connections
- Acknowledgement of a revocation request means the change is durable and queued; it MUST NOT be reported as enforced until the declared mechanisms have applied
- Products MUST NOT require synchronous Identity calls for every request solely to check session state when local token validation plus bounded revocation/projection mechanisms satisfy the requirement
- Privileged administrative sessions SHOULD use server-managed/BFF session patterns where the application architecture supports them

### 3.5 Signing Keys & Cryptographic Trust

- Production signing keys, federation keys, secrets, and certificates MUST use approved protected custody and lifecycle controls
- One `kid` MUST map to exactly one immutable key pair for its entire lifecycle; a `kid` MUST NOT be reused, regenerated, or bound to different key material by any replica, restart, environment, or recovery procedure
- Signing key material MUST be identical across every replica of an issuer; per-process or per-replica production key generation is prohibited, including as a fallback when protected custody is unreachable
- Key IDs and rotation MUST allow verification continuity across planned rotation, and public verification material MUST remain published for at least the maximum lifetime of any artifact signed with that key plus consumer cache and clock-skew margin
- Private signing material MUST NOT be exposed to product consumers or browser applications
- Products MUST obtain verification material through approved discovery/JWKS or equivalent trust distribution
- Exact algorithm and key-lifecycle configuration belong to an approved Identity implementation profile or ADR and MUST remain interoperable with required clients

### 3.6 Federation

- External identities MUST be bound by stable issuer plus external-subject identity, not by mutable email address alone
- Federation trust MUST validate issuer, signature, audience, time constraints, and approved claims
- Upstream MFA/assurance MAY be accepted only when the federation contract and assurance mapping explicitly permit it
- JIT provisioning, account linking, and reconciliation MUST preserve Principal authority and prevent unintended account takeover

### 3.7 Workload Identity

- Service, workload, automation, and AI-agent identities MUST use non-human credential profiles with explicit owner, audience, rotation, and lifecycle
- Shared human credentials or long-lived static secrets are prohibited when a managed workload-identity mechanism is available
- Workload identity MUST be distinguishable from human Principal context in audit and authorization flows

### 3.8 Audit & Security Evidence

- Authentication, federation, recovery, factor change, session lifecycle, token/client administration, privileged identity administration, and security-relevant configuration changes MUST emit governed security/audit events
- Identity Runtime MAY keep operational logs, but enterprise evidence authority remains with the designated Audit & Evidence capability
- Audit evidence MUST preserve actor, subject, action, outcome, time, source, correlation, and relevant assurance/context metadata

### 3.9 Browser Security

- Browser applications MUST NOT persist refresh tokens or equivalent long-lived bearer secrets in `localStorage`
- Privileged/admin experiences SHOULD prefer secure `HttpOnly`, `Secure`, appropriately scoped cookies backed by server-side/BFF session control
- Direct browser-token applications require an approved public-client profile, PKCE, bounded token lifetime, XSS controls, and no client secret
- UI authorization is defense-in-depth and user-experience control only; backend/domain authorization remains authoritative

## 4. Exceptions

Deviation from this standard requires formal exception approval under GDC-000 with explicit threat model, compensating controls, owner, and review condition where appropriate.

## 5. Enforcement Mechanism

- protocol conformance and integration tests
- client-registration policy and redirect-URI validation
- token-validation contract tests
- federation and account-linking security tests
- browser security and secret-scanning checks
- administrative audit-event assertions
- architecture fitness functions preventing Identity ownership of Tenant, Membership, Product Permission, or business state
- client-registration assertion that no client in a shared environment enables the Resource Owner Password Credentials grant
