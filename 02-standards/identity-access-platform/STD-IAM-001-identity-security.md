---
doc_meta:
  id: STD-IAM-001
  title: Enterprise Identity Security Standard
  owner: Enterprise Security Architect
  version: 2.2.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-03
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
- **Access to a privileged account MUST be multi-factor.** NIST SP 800-53 IA-2(1) says to "Implement
  multi-factor authentication for access to privileged accounts" [R11]. On this platform that is
  `acr` `aal2` (`STD-IAM-002 §3.2`, `ADR-IAM-004`) for every route a provider-scope authority serves,
  reads included. Raising non-privileged access to `aal2` (IA-2(2)) is not required by this revision.
- Credential policy MUST support modern password hashing, breached/weak credential controls where available, secure recovery, MFA, WebAuthn/passkeys, and step-up authentication according to assurance requirements [R9]
- Plaintext credentials, recovery secrets, private keys, and bearer tokens MUST NOT be logged [R18]
- Authentication endpoints MUST implement rate limiting, abuse detection, and bounded resource consumption [R9][R11]

### 3.2 OAuth 2.0 / OpenID Connect Security Profile

- Authorization Code flow with PKCE using `S256` is REQUIRED for public browser and native clients [R1][R2]. RFC 9700 makes PKCE a MUST for public clients and `S256` a SHOULD; requiring `S256` without exception is this standard's own strengthening
- **The Resource Owner Password Credentials grant is PROHIBITED for every client, confidential clients included.** RFC 9700 §2.4 says it MUST NOT be used [R1], and the OAuth 2.1 draft omits it on that ground [R13]. The reason is structural rather than stylistic: the grant requires a client to receive and forward the Principal's password, which places credential material in a process that this standard §3.1 forbids from holding any. It also defeats MFA, WebAuthn, step-up, and every abuse control the kernel's authentication ceremony applies, because none of them are on the path
- A client MAY enable the grant in a local development environment that holds no production credential and issues no token another environment accepts. That exemption is a property of the environment, not of the client, and MUST NOT be carried into a shared environment by configuration. RFC 9700 names no exemption; this one is this standard's, and it is bounded by what the environment can issue
- Being a confidential client is not an exemption. Client authentication proves which application is asking; it says nothing about how the Principal proved who they are
- Redirect URIs MUST be explicitly registered and matched according to the approved client profile; open redirect patterns are prohibited [R1]
- Access tokens MUST be audience-bound and short-lived according to the approved token-lifetime class [R1][R15]
- An access token MUST NOT exceed a 15-minute lifetime unless an approved token-lifetime class defines a longer bound for a named audience; any longer lifetime MUST be carried into the revocation enforcement delay of every affected revocation class. The 15-minute figure is this platform's choice: the sources require access tokens to be short-lived and name no number
- Refresh tokens MUST use the approved identity kernel's rotation, reuse-detection, revocation, and session controls when refresh tokens are issued [R1]
- Client credentials, client private keys, and client secrets MUST never be embedded in public browser or mobile applications [R3][R4]
- **Confidential and workload clients MUST authenticate to the token endpoint with a signed JWT client assertion (`private_key_jwt`, RFC 7523 [R5], OpenID Connect Core §9 [R6]), signed `PS256` with an RSA key of at least 3072 bits**, the floor `STD-IAM-002 §3.2.2` sets for signing keys. RFC 9700 §2.5 recommends asymmetric client authentication, because the server then holds no secret that authenticates the client [R1]. `ADR-IAM-001 §5.12` records the decision:
  - The client generates its key pair. The private key never leaves that client's deployable and its approved secret custody.
  - The identity kernel holds only the client's public keys. The Identity Control Service registers them. A client created to stand the registration path up, before the Identity Control Service can register it, gets its public key from the bootstrap script that creates it. No Scnehaux component holds another client's private key.
  - Each assertion MUST carry a unique `jti` and a short expiry and be refused if presented twice, as OpenID Connect Core §9 requires; RFC 7523 leaves both optional [R5][R6].
  - Each assertion MUST name the realm issuer as its sole audience. That is the rule the RFC 7523 revision adopts after CVE-2025-27370 and CVE-2025-27371 [R14]. The published OpenID Connect Core §9 still says the audience SHOULD be the token endpoint URL, so the issuer is the stricter reading, and it is the one this standard takes.
  - Rotation MUST overlap. A new public key is registered while the retiring one is still valid, and the retiring one is removed at the end of a bounded window. Revocation removes a key, and the kernel refuses it on the next request.
- Shared client secrets (`client_secret_basic`, `client_secret_post`, `client_secret_jwt`) are PROHIBITED for every confidential and workload client in every shared environment, development included. That covers registered clients, bootstrap clients, and administration service accounts alike. The kernel holds one secret per client, so a secret cannot rotate with an overlap without a feature the kernel classifies as preview [R16]. The kernel also returns a client's secret to its administrators through the Admin API [R17].
- A test fixture MAY authenticate with a client secret only inside a throwaway kernel that lives for one test run and issues no token another environment accepts. That exemption is a property of the environment, as for the ROPC grant above. It MUST NOT reach a shared environment
- Token introspection MAY be used where opaque-token or active-state semantics require it, but normal signed-token validation SHOULD remain local when sufficient
- Access tokens are bearer tokens in the initial baseline. RFC 9700 §2.2.1 says servers SHOULD sender-constrain them [R1]; `STD-IAM-002 §3.8` records why the baseline does not yet, and the condition under which that changes

### 3.3 Token & Claim Profile

- Every consumer MUST validate issuer, audience, signature, token type, expiry, and other mandatory protocol claims [R6][R21][R22]
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
- Maximum enforcement delay MUST be computed as `propagation_time + remaining_access_token_lifetime`; access token lifetime is therefore a security parameter of the revocation contract and MUST NOT be selected on performance grounds alone. The formula is this standard's. It follows from RFC 7009: revoking a grant does not invalidate an access token already issued, which stays usable until it expires [R8]
- Every revocation class MUST declare which mechanisms enforce it, covering context-projection removal, kernel session removal, consumer projection update, and termination of long-lived connections
- Acknowledgement of a revocation request means the change is durable and queued; it MUST NOT be reported as enforced until the declared mechanisms have applied
- Stopping a client MUST end the refresh tokens and sessions issued to it before the stop, not only refuse its new requests. A stop that a later re-enable undoes for the earlier sessions is a pause, and MUST NOT be used or reported as a revocation
- A client MUST be stopped reversibly before it is removed permanently. The permanent removal MUST be refused for a client that has not been stopped first; a protected resource, which holds no credential and is issued no token, is exempt
- The two rules above are this standard's, not a protocol's. They rest on what the pinned kernel does to a stopped client (`ADR-IAM-001 §5.13`), on eradication removing the persistence mechanisms an incident left [R20], and on disabling an account before deleting it [R19]
- Products MUST NOT require synchronous Identity calls for every request solely to check session state when local token validation plus bounded revocation/projection mechanisms satisfy the requirement
- Privileged administrative sessions SHOULD use server-managed/BFF session patterns where the application architecture supports them

### 3.5 Signing Keys & Cryptographic Trust

- Production signing keys, federation keys, secrets, and certificates MUST use approved protected custody and lifecycle controls
- One `kid` MUST map to exactly one immutable key pair for its entire lifecycle; a `kid` MUST NOT be reused, regenerated, or bound to different key material by any replica, restart, environment, or recovery procedure. RFC 7517 asks only for distinct `kid` values within one key set [R7]; binding one `kid` to one key pair for its whole life is this standard's strengthening
- Signing key material MUST be identical across every replica of an issuer; per-process or per-replica production key generation is prohibited, including as a fallback when protected custody is unreachable
- Key IDs and rotation MUST allow verification continuity across planned rotation, and public verification material MUST remain published for at least the maximum lifetime of any artifact signed with that key plus consumer cache and clock-skew margin. OpenID Connect Core §10.1.1 says a key set SHOULD retain recently decommissioned keys for a reasonable period [R6]; this standard states the period
- Private signing material MUST NOT be exposed to product consumers or browser applications
- Products MUST obtain verification material through approved discovery/JWKS or equivalent trust distribution
- Exact algorithm and key-lifecycle configuration belong to an approved Identity implementation profile or ADR and MUST remain interoperable with required clients

### 3.6 Federation

- External identities MUST be bound by stable issuer plus external-subject identity, not by mutable email address alone [R6][R10]
- Federation trust MUST validate issuer, signature, audience, time constraints, and approved claims [R10]
- Upstream MFA/assurance MAY be accepted only when the federation contract and assurance mapping explicitly permit it
- JIT provisioning, account linking, and reconciliation MUST preserve Principal authority and prevent unintended account takeover

### 3.7 Workload Identity

- Service, workload, automation, and AI-agent identities MUST use non-human credential profiles with explicit owner, audience, rotation, and lifecycle [R11][R19]. Toward the identity kernel, that credential is a registered key pair under §3.2, rotated by adding the new key before the old one is removed
- Shared human credentials are prohibited. A shared client secret is prohibited for kernel client authentication under §3.2. Other long-lived static secrets are prohibited when a managed workload-identity mechanism is available
- Workload identity MUST be distinguishable from human Principal context in audit and authorization flows

### 3.8 Audit & Security Evidence

- Authentication, federation, recovery, factor change, session lifecycle, token/client administration, privileged identity administration, and security-relevant configuration changes MUST emit governed security/audit events
- Identity Runtime MAY keep operational logs, but enterprise evidence authority remains with the designated Audit & Evidence capability
- Audit evidence MUST preserve actor, subject, action, outcome, time, source, correlation, and relevant assurance/context metadata [R11]

### 3.9 Browser Security

- Browser applications MUST NOT persist refresh tokens or equivalent long-lived bearer secrets in `localStorage`. RFC 10017 describes that storage as readable by any script the page runs [R12]; the prohibition is this standard's
- Privileged/admin experiences SHOULD prefer secure `HttpOnly`, `Secure`, appropriately scoped cookies backed by server-side/BFF session control [R12]
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
- client-registration assertion that every confidential or workload client in a shared environment authenticates with `private_key_jwt` and holds no client secret
- compatibility test, against the pinned kernel release, that two registered client keys overlap, a removed key is refused on the next request, and a replayed assertion is refused
- compatibility test, against the pinned kernel release, that a stopped client gets no new token and no refresh, that the refresh tokens a stop ended stay refused after a re-enable, and that a deleted client's `clientId` can be registered again

## 6. References

The external sources the rules above rest on, cited as `[Rn]`. A rule that is stricter than its source says so where it is stated. In-repository evidence, such as a compatibility run, is cited inline where it is used.

### Normative

- **[R1]** IETF RFC 9700 (BCP 240), _Best Current Practice for OAuth 2.0 Security_, January 2025. <https://www.rfc-editor.org/rfc/rfc9700>. §2.1 exact redirect URI matching; §2.1.1 PKCE; §2.2.1 sender-constrained tokens; §2.2.2 and §4.14 refresh token rotation; §2.3 audience restriction; §2.4 the password grant MUST NOT be used; §2.5 asymmetric client authentication.
- **[R2]** IETF RFC 7636, _Proof Key for Code Exchange by OAuth Public Clients_, September 2015. <https://www.rfc-editor.org/rfc/rfc7636>. §4.2: a client capable of `S256` MUST use it.
- **[R3]** IETF RFC 6749, _The OAuth 2.0 Authorization Framework_, October 2012. <https://www.rfc-editor.org/rfc/rfc6749>. §10.1: no client password or credential for a native or user-agent-based client.
- **[R4]** IETF RFC 8252 (BCP 212), _OAuth 2.0 for Native Apps_, October 2017. <https://www.rfc-editor.org/rfc/rfc8252>. §8.5: a native app is a public client and holds no secret.
- **[R5]** IETF RFC 7523, _JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants_, May 2015. <https://www.rfc-editor.org/rfc/rfc7523>. §3: the assertion format; `jti` and replay checking are optional there.
- **[R6]** OpenID Foundation, _OpenID Connect Core 1.0 incorporating errata set 2_, December 2023. <https://openid.net/specs/openid-connect-core-1_0.html>. §5.7 `iss` and `sub` as the stable identifier; §9 `private_key_jwt`, with `jti` REQUIRED and single use; §10.1.1 retaining decommissioned keys.
- **[R7]** IETF RFC 7517, _JSON Web Key (JWK)_, May 2015. <https://www.rfc-editor.org/rfc/rfc7517>. §4.5: `kid` values within a key set SHOULD be distinct.
- **[R8]** IETF RFC 7009, _OAuth 2.0 Token Revocation_, August 2013. <https://www.rfc-editor.org/rfc/rfc7009>. §3 and §5: an access token already issued is not invalidated at once by a revocation.
- **[R9]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator Management_, August 2025. <https://doi.org/10.6028/NIST.SP.800-63B-4>. Salted password hashing and blocklists, rate limiting, and a phishing-resistant option at AAL2.
- **[R10]** NIST SP 800-63C-4, _Digital Identity Guidelines: Federation and Assertions_, August 2025. <https://doi.org/10.6028/NIST.SP.800-63C-4>. Assertion validation, replay protection, and the federated identifier as subject plus issuer.
- **[R11]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and Organizations_ (release 5.2.0). <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. AC-7 unsuccessful logon attempts; IA-2(1) multi-factor authentication to privileged accounts; IA-5(1) password-based authentication; IA-9 service identification and authentication; AU-2 and AU-3 audit events and their content.
- **[R12]** IETF RFC 10017, _OAuth 2.0 for Browser-Based Applications_ (Best Current Practice), August 2026. <https://www.rfc-editor.org/rfc/rfc10017>. §6.1.3.2 `HttpOnly` and `Secure` BFF cookies; §8.5 browser storage readable by script.

- **[R21]** IETF RFC 9068, _JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens_, October 2021. <https://www.rfc-editor.org/rfc/rfc9068>. §4: the validation a resource server performs. The operative profile is `STD-IAM-002`.
- **[R22]** IETF RFC 8725 (BCP 225), _JSON Web Token Best Current Practices_, February 2020. <https://www.rfc-editor.org/rfc/rfc8725>. §3.1 algorithm allowlists; §3.8 to §3.11 issuer, audience, and explicit typing.

### Informative

- **[R13]** IETF draft-ietf-oauth-v2-1-16, _The OAuth 2.1 Authorization Framework_, Internet-Draft, accessed 2026-09-30. <https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/>. Omits the password grant, citing RFC 9700 §2.4. A draft, not a standard.
- **[R14]** IETF draft-ietf-oauth-rfc7523bis-11, Internet-Draft, accessed 2026-09-30, <https://datatracker.ietf.org/doc/draft-ietf-oauth-rfc7523bis/>; and OpenID Foundation, _Notice of a Security Vulnerability_ (CVE-2025-27370, CVE-2025-27371), <https://openid.net/notice-of-a-security-vulnerability/>. A client assertion's audience is the authorization server's issuer as its sole value.
- **[R15]** IETF RFC 6819, _OAuth 2.0 Threat Model and Security Considerations_, January 2013. <https://www.rfc-editor.org/rfc/rfc6819>. §5.1.5.3: use short expiration times.
- **[R16]** Keycloak, _Enabling and disabling features_, accessed 2026-09-30. <https://www.keycloak.org/server/features>. `client-secret-rotation` is a preview feature, not recommended for production.
- **[R17]** Keycloak, _Admin REST API_ 26.7.5. <https://www.keycloak.org/docs-api/26.7.5/rest-api/index.html>. `GET /admin/realms/{realm}/clients/{client-uuid}/client-secret` returns the secret.
- **[R18]** OWASP, _Logging Cheat Sheet_, accessed 2026-09-30. <https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html>. Access tokens, passwords, and keys are data to exclude from logs.
- **[R19]** Center for Internet Security, _CIS Controls v8.1_, accessed 2026-09-30. <https://www.cisecurity.org/controls/v8-1>. 5.5 inventory of service accounts; 6.2 disabling accounts rather than deleting them may preserve audit trails.
- **[R20]** NIST SP 800-61 Rev. 3, _Incident Response Recommendations and Considerations for Cybersecurity Risk Management_, April 2025. <https://csrc.nist.gov/pubs/sp/800/61/r3/final>. RS.MI-01 and RS.MI-02: containment, and eradication of persistence mechanisms and entry points.
