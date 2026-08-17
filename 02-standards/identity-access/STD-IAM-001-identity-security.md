---
doc_meta:
  id: STD-IAM-001
  title: Enterprise Identity Security Standard
  owner: Enterprise Security Architect
  version: 2.0.0
  status: adopted
  classification: restricted
  governed_by: [EAD-006]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_updated: 2026-08-18
  last_reviewed: 2026-08-18
---

# Enterprise Identity Security Standard (STD-IAM-001)

---

## 1. Objective & Scope

This standard states the security properties every identity operation in the Scnehaux enterprise must exhibit: how credentials are protected, how keys are held, how access is revoked, how a workload is held accountable, and where a browser is permitted to hold anything.

It applies to the Identity Runtime and to every system that consumes identity. It applies to a capability whether that capability is written in-house or configured in an adopted component.

### 1.1 Properties, Not Implementations

**Version 2.0.0 restates this standard as properties.** Version 1 mandated specific mechanisms inside a Scnehaux-authored identity provider: a process-level weighted semaphore around Argon2id, a `session_epoch` integer compared against a Redis cache, and a refresh-token rotation blacklist with a ten-second grace window.

`ADR-IAM-001` adopts Keycloak as the identity kernel, so credential hashing, session state, and token issuance happen inside a component this enterprise configures rather than writes. A standard that mandates the internal mechanism of a component it does not author is unenforceable in the only place the mechanism could exist, and it reads as a requirement nobody has met.

Every security requirement from version 1 survives here. What changed is that each is now stated as an observable property with a named place it is asserted, so it can be verified against the kernel's behaviour instead of searched for in source that does not exist.

**Out of scope:** the token claim set, lifetime classes, algorithm allowlist, and verifier obligations, all owned by `STD-IAM-002`; business authorization, owned by the domain that owns the resource; and infrastructure hardening, owned by `EAD-005`.

---

## 2. Design Principles

**A control is a property, and a property is asserted.** A control stated as an implementation detail cannot be verified in an adopted component, and an unverifiable control is a belief.

**Zero-trust verification.** A token is verified from cached material without a per-request call to the issuer, so an identity outage degrades the estate rather than stopping it.

**Fail secure.** On the failure of a security control, privileged and write operations fail closed and existing sessions degrade to read continuity. Never to open access.

**One authority per fact.** Two components answering the same security question will eventually answer differently, and the disagreement is silent. This is why revocation has one authority rather than a primary and a shadow.

---

## 3. Normative Rules

### 3.1 Authenticator Policy

- Every human Principal MUST hold at least one strong authenticator. Phishing-resistant authenticators, meaning FIDO2 and WebAuthn, MUST be available to every Principal and MUST be required for privileged access.
- An authenticator removal MUST be refused when it would leave the Principal below the policy floor or remove the last usable factor. The check MUST re-read the current authenticator set immediately before removal, so two concurrent removals cannot both validate against the same pre-removal count.
- Enrollment and removal MUST require fresh step-up authentication.
- Multi-factor authentication MUST cover 100% of privileged access.

### 3.2 Protocol Surface

- Interactive authentication MUST use Authorization Code with PKCE `S256`. The implicit flow and the resource owner password credentials flow are PROHIBITED.
- Redirect URIs MUST be validated by exact match. A wildcard is PROHIBITED: a wildcard redirect is an open redirect delegating to whoever controls a matching host.
- A public client MUST NOT hold a client secret, and MUST NOT be issued a refresh token. A browser-facing application registers a confidential client for its Backend-for-Frontend instead.
- External HTTP interfaces MUST send `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and a default-deny `Content-Security-Policy`.

### 3.3 Credential Protection

- A stored credential MUST be protected by a memory-hard function with a published security margin. **Argon2id is the required algorithm**, with a memory cost of at least 64 MB, at least 3 iterations, a parallelism of 4, and a salt of at least 16 bytes from a cryptographically secure source. Legacy algorithms, specifically bcrypt, PBKDF2, and any MD5 or SHA family construction used directly, are PROHIBITED for credentials.
- A plaintext credential MUST NOT be stored at rest, written to a log, emitted in an event, or included in an error response.
- Credential verification MUST use a constant-time comparison.
- Credential hashing MUST be bounded so that concurrent authentication attempts cannot exhaust host CPU and starve unrelated request processing. **The bound is required; the mechanism is the implementing component's.** Where the component is adopted, its configured concurrency limits and its rejection behaviour under saturation MUST be measured and recorded, and a saturated authentication path MUST reject with HTTP 429 rather than queue without bound.
- **Enterprise identity resolution MUST depend only on the access token.** A consumer MUST NOT require a claim to be present on the ID token, the UserInfo response, or the introspection response in order to resolve identity. Those surfaces MAY carry the claim; only the access token MUST.

This section is where version 1's process-level semaphore lived. The DoS property it protected is stated above as a bound with a required rejection behaviour, which is assertable against a configured component. The specific `Runtime.NumCPU() - 1` weighted-semaphore construction was correct for a Go process that performed the hashing and has no meaning in a component that does not.

### 3.4 Revocation Classes and Their Enforcement

**Every revocation class MUST declare the mechanisms that enforce it and the interval within which enforcement completes.** A revocation without a stated interval is a request, not a control.

| Class | Enforcing mechanisms |
| :-- | :-- |
| Membership revoked in one Tenant | Projected context removed; kernel sessions for that context removed; consumer read model updated; residual access token lifetime |
| Tenant suspended | Tenant security version advanced; every projected context for the Tenant removed; sessions removed; consumer read model updated |
| Principal quarantined | Kernel user disabled; all sessions terminated; projected context removed |
| Workload suspended | Client credential revoked; projected context removed |
| Authenticator revoked | Authenticator removed at the kernel; affected sessions terminated |

- **Revoking access MUST NOT require scanning or deleting per-session rows.** The operation MUST be constant-time with respect to the number of active sessions.
- Enforcement MUST be presented as the sum of the propagation budget and the residual token lifetime, naming the lifetime class assumed, per `STD-IAM-002 §3.4`. A figure quoting propagation alone understates enforcement by up to the full lifetime of the class.
- Context removal MUST be applied before session removal. The reverse order leaves a window in which a refresh mints a token asserting the revoked context.
- **Exactly one component MUST be authoritative for whether a session is valid.** A second revocation authority that the session engine does not consult is PROHIBITED, because a token rejected by one and accepted by the other produces a silent disagreement no operator can resolve.

The last rule is why version 1's `session_epoch` counter is withdrawn rather than carried forward. Its purpose — constant-time global revocation — is the first rule in this section. Its mechanism presumed ownership of the session engine.

### 3.5 Key Custody

- Signing keys MUST be provisioned from an approved secret manager or keystore custody mechanism. **Generating a signing key inside the serving process is PROHIBITED in every environment whose issuer any other system trusts, including as a fallback.**
- One `kid` MUST bind to one immutable key pair for the whole life of that pair. Reusing a `kid` for different material makes a verifier's cache indistinguishable from an attack.
- Every replica of an issuer MUST serve identical key material. Two replicas advertising different material for one issuer means a token signed by one fails against the other.
- A key MUST progress through a defined lifecycle with a retirement window, and verification material MUST remain published for at least the maximum lifetime of any artifact it signed, plus the maximum permitted clock skew and the maximum verification-material cache lifetime.
- Private key material MUST NOT be persisted in plaintext, committed to source, or included in an image.
- Key rotation MUST be rehearsed, including emergency rotation, before production.

An ephemeral in-process signer is permitted only for local development where no other system trusts the issuer, and MUST NOT be selectable by a staging or production configuration path.

### 3.6 Session and Token Handling

- Refresh token rotation MUST be enforced on every session. A rotated token MUST NOT remain usable indefinitely.
- Replay of a rotated refresh token MUST be detected and MUST result in invalidation of the token family, with the event audited. A bounded tolerance window for a client's automatic retry of a dropped response MAY be configured; outside it, replay is treated as theft.
- Access token lifetimes are fixed by the lifetime classes in `STD-IAM-002 §3.3`, and no interface may issue a token exceeding its registered class.
- Switching the active Tenant context MUST issue a new token rather than mutate an existing one.

### 3.7 Workload and Agent Identity

- Service, workload, automation, and AI-agent identities MUST use non-human credential profiles with an explicit accountable owner, a declared audience, a defined rotation schedule, and a defined lifecycle.
- Shared human credentials are PROHIBITED. A long-lived static secret is PROHIBITED where a managed workload-identity mechanism is available.
- **Workload identity MUST be distinguishable from human Principal context** in every audit record and every authorization decision, by an explicit claim rather than by a naming convention.
- A workload MUST NOT be issued a refresh token. It re-authenticates with its own credential.
- A workload whose accountable owner loses access MUST be detected, escalated, and eventually suspended if unclaimed. Immediate termination is PROHIBITED as a default, because it converts a resignation into an outage and teaches operators to create unowned shared accounts instead.
- An agent acting for a human MUST be the subject of its own token, with the human recorded as the actor, never the reverse. Delegated scope MUST be the intersection of what the human holds and what the agent may hold, and MUST be time-bounded.

### 3.8 Auditability

- Every security-relevant identity operation MUST produce an immutable audit record: authentication outcome, credential change, authenticator change, consent change, registration change, privileged read, and every revocation.
- The audit trail MUST be append-only and tamper-evident, such that retro-active modification is detectable.
- An audit record MUST NOT contain credential material of any kind, per §3.3.
- Loss of the audit path MUST fail security-critical writes closed rather than proceed unrecorded.

### 3.9 Browser and Presentation Boundary

- **A browser MUST NOT hold an access token or a refresh token** for a privileged experience. Tokens are held in a server-side session by a Backend-for-Frontend, and the browser holds an opaque, `HttpOnly`, `Secure`, `SameSite` cookie.
- A state-changing request from a browser MUST carry CSRF protection.
- **Authorization shown in a user interface is defence in depth. The backend is authoritative.** Every command MUST be reauthorized by the owning service, and hiding a control MUST NOT be the only thing preventing the action it represents.
- A Backend-for-Frontend MUST forward an allowlist of routes rather than an arbitrary path, so a defect in it does not become access to every route the authority exposes.

---

## 4. Exceptions

An ephemeral in-process signing key, in a local development environment only, where no other system trusts the issuer and no staging or production configuration path can select it.

A bounded retry-tolerance window for a rotated refresh token, as described in §3.6, where a client population on unreliable networks would otherwise experience spurious session termination. The window is bounded and recorded; replay outside it is theft.

No other deviation exists. In particular there is no exception permitting a plaintext credential at rest, a legacy credential hashing algorithm, a signing key generated in a serving process whose issuer is trusted, a browser-held token for a privileged experience, a second session-validity authority, or a revocation class with no stated enforcement interval.

---

## 5. Enforcement Mechanism

1. **Realm and configuration contract suite**: for every adopted identity component, a suite asserts the configured properties on every candidate release — the credential hashing algorithm and its parameters, the closed creation paths, the authenticator policy floor, the token lifetime per class, and the signing algorithm. A candidate that cannot exhibit a property fails before promotion. This is how §3.1, §3.2, §3.3, and §3.6 are verified in a component nobody here authors.
2. **Key custody assertions**: startup fails when custody is unreachable rather than generating material, and a test asserts that no configuration path reachable in staging or production selects an ephemeral signer. Replica key identity is asserted by verifying a token signed by one replica against every other.
3. **Measured enforcement**: revocation enforcement is measured end to end per class in §3.4 and compared against the published interval. A class whose measured interval exceeds its published figure is a failing test, not a tuning note.
4. **Single-authority assertion**: a test asserts that no component other than the session engine can render a session invalid, by confirming that a token the engine considers valid is not rejected by any other check, and vice versa.
5. **Static and supply-chain analysis**: only a cryptographically secure random source is permitted; a weak generator, a non-constant-time comparison in a verification routine, and a credential-shaped literal in source or in a built artifact each block the build.
6. **Telemetry redaction fuzzing**: error and logging paths are exercised with credential-shaped input, and any occurrence of that input in a log line, span attribute, event payload, or problem document fails the suite. Error paths are the least exercised code in any service, which is where an unredacted value survives.
7. **Every gate must be able to fail**: each rule above carries a case that violates it, and the suite asserts the rule rejects that case. A gate that has never rejected anything is indistinguishable from no gate.
