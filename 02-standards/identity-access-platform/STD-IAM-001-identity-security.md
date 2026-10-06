---
doc_meta:
  id: STD-IAM-001
  title: Enterprise Identity Security Standard
  owner: Enterprise Security Architect
  version: 2.6.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-06
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
- **Binding, replacing or removing an authenticator, issuing recovery codes, and account recovery MUST each notify every notification address of the Principal, and a Principal MUST be able to hold at least two (2.6.0).** NIST SP 800-63B-4 §4.6 asks that "Events that require notification SHALL cause a notification to be sent to the notification addresses stored in the subscriber account" and that "CSPs SHALL support at least two notification addresses per subscriber account" [R9]. The notification says how to repudiate the event and whom to contact. An address is added only at `aal2` and after proof of control, and the change is itself notified. The Identity Control API decides each notification and the Notification Platform delivers it (`ADR-IAM-007`). The kernel sends no mail. Not met until both are in production, which is a production gate
- **A failed sign-in MUST NOT tell by its time whether the account exists or what state it is in (2.5.0).** An unknown identifier, a wrong password and a disabled account answer in times a test cannot separate, as they already answer with one message and one status. OWASP warns that "the processing time can be significantly different according to the case ... allowing an attacker to mount a time-based attack", and gives the remedy: hash the password whether or not the user exists [R30]. The pinned kernel does that, hashing a dummy password for an unknown identifier [R32]. The compatibility suite measures it by dudect's method: the classes interleaved in a random order, Welch's t-test on every measurement and on the fastest share, and dudect's threshold of 10 [R31]. Against 26.7.5 the three classes stand at 44.2, 44.1 and 43.5 ms, with no pair above 1.6.
- **Two kernel paths answer an existing account about one hash sooner, and are recorded gaps (2.5.0).**
  - _An empty password._ The kernel returns before hashing for an existing account and still hashes for an unknown one, so an empty password is answered in 16.4 ms against 42.1 ms (|t| 137). This is reported upstream as keycloak#51887, open, marked important [R32].
  - _An account under a brute-force lockout._ The lockout is checked before the password, so the answer comes in 16.0 ms (|t| 126). A guesser who has caused the lockout learns from the time that the account exists, though the message is the same.
  - No realm setting closes either gap. Closing one here would take a custom authenticator, a restricted mechanism (`ADR-IAM-001 §5.7`), against a fix the kernel's maintainers are already making. Both stay measured on every compatibility run, so the release that closes them shows it, and the rate limits above bound how fast either can be asked.

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
- Identity Runtime MUST keep a durable record of every kernel user and admin event, read from the kernel's native event store, until Audit & Evidence has received it (2.3.0). The kernel's own store is bounded (`TDD-identity-kernel-003`, 7 days) and is the reconciliation source, not that record. AU-11 asks to "Retain audit records for [an organization-defined time period] to provide support for after-the-fact investigations of incidents" [R11]; the time period is Audit & Evidence's to define, and until it receives an event the record cannot be released without losing it. EAD-002 §8 asks the same of every producer: "Durable producers retain/replay accepted work". The record holds no password, token, key, or other credential value, whatever the kernel's representation carried [R18]

### 3.9 Browser Security

- Browser applications MUST NOT persist refresh tokens or equivalent long-lived bearer secrets in `localStorage`. RFC 10017 describes that storage as readable by any script the page runs [R12]; the prohibition is this standard's
- Privileged/admin experiences SHOULD prefer secure `HttpOnly`, `Secure`, appropriately scoped cookies backed by server-side/BFF session control [R12]
- Direct browser-token applications require an approved public-client profile, PKCE, bounded token lifetime, XSS controls, and no client secret
- UI authorization is defense-in-depth and user-experience control only; backend/domain authorization remains authoritative
- The kernel's hosted login pages MUST NOT be framed by any origin: their `Content-Security-Policy` carries `frame-ancestors 'none'`, and `X-Frame-Options: DENY` is sent for browsers that predate it (2.4.0). CSP Level 3 says `frame-ancestors` "is meant to replace the `X-Frame-Options` header" [R23], and OWASP recommends `'none'` and `DENY` "unless a specific need has been identified for framing" [R24]. Keycloak's default is weaker, "only ... a _same-origin_ policy for iframes" [R26], so the realm sets its own. No client of this estate frames a kernel page: a browser application signs in through its BFF [R12], so the OpenID Connect session-status iframe and sign-in inside an iframe are not offered
- Their policy MUST load nothing from another origin: `default-src 'self'`, images also from `data:` (the one-time-code enrolment page renders its QR code as one), `object-src 'none'` and `base-uri 'none'`, the directives OWASP's strict policy sets alongside its script rule [R25] (2.4.0)
- Inline script is permitted on those pages, as `'unsafe-inline'` in `script-src` and `style-src`, until the kernel can mark its own inline scripts with a nonce (2.4.0). This is a recorded gap against the strict policy OWASP recommends, a nonce or hash `script-src` with `'strict-dynamic'` [R25]. The pinned kernel's stock templates run inline scripts and inline event handlers on the sign-in, one-time-code and passkey pages, and the passkey page writes the request's challenge into its inline script, so no hash can name it [R26]. Copying the templates to remove the inline code would fork sixteen of the 33, and a copied template "no longer receives the kernel's changes" (`ADR-IAM-001 §5.7`), security fixes included. Nonces for the kernel's templates are proposed upstream and not released [R26]. Until then the policy still refuses every script from another origin, and CSP remains a "second layer", not "the only defensive mechanism against XSS" [R25]. The gap closes with the kernel release that ships nonces, and `TDD-identity-kernel-004` tracks it
- The policy MUST NOT set `form-action` while the kernel's pages submit a form whose answer redirects to a client (2.4.0). Whether `form-action` governs the redirect that follows a submission is an open question in the CSP specification [R27], and Chrome "takes the redirection target into account" [R28], so `form-action 'self'` would block the return to the client after sign-in, and every `form_post` response
- Those pages MUST also send `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer` (2.4.0). A browser ignores the first over plain HTTP, "the UA MUST ignore any present STS header field(s)" [R29], so it takes effect behind the production load balancer's TLS and is harmless on a development server

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
- compatibility test, against the pinned kernel release, that the hosted login page carries the §3.9 header set, that its policy names no other origin and no `form-action`, and that a definition weakening the anti-framing directives is refused
- compatibility test, against the pinned kernel release, that an unknown identifier, a wrong password and a disabled account are not separable by time, with the §3.1 recorded gaps measured alongside
- realm definition assertion that the kernel holds no SMTP server and no `email` event listener (`ADR-IAM-007 §5.4`)

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
- **[R9]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator Management_, August 2025. <https://doi.org/10.6028/NIST.SP.800-63B-4>. Salted password hashing and blocklists, rate limiting, and a phishing-resistant option at AAL2. §4.6 Account Notifications: "Events that require notification SHALL cause a notification to be sent to the notification addresses stored in the subscriber account"; "CSPs SHALL support at least two notification addresses per subscriber account"; "The notification SHALL provide clear instructions, including contact information, in case the recipient repudiates the event associated with the notification."
- **[R10]** NIST SP 800-63C-4, _Digital Identity Guidelines: Federation and Assertions_, August 2025. <https://doi.org/10.6028/NIST.SP.800-63C-4>. Assertion validation, replay protection, and the federated identifier as subject plus issuer.
- **[R11]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and Organizations_ (release 5.2.0). <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. AC-7 unsuccessful logon attempts; IA-2(1) multi-factor authentication to privileged accounts; IA-5(1) password-based authentication; IA-9 service identification and authentication; AU-2 and AU-3 audit events and their content; AU-11 audit record retention, "Retain audit records for [Assignment: organization-defined time period consistent with records retention policy] to provide support for after-the-fact investigations of incidents and to meet regulatory and organizational information retention requirements."
- **[R12]** IETF RFC 10017, _OAuth 2.0 for Browser-Based Applications_ (Best Current Practice), August 2026. <https://www.rfc-editor.org/rfc/rfc10017>. §6.1.3.2 `HttpOnly` and `Secure` BFF cookies; §8.5 browser storage readable by script.

- **[R21]** IETF RFC 9068, _JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens_, October 2021. <https://www.rfc-editor.org/rfc/rfc9068>. §4: the validation a resource server performs. The operative profile is `STD-IAM-002`.
- **[R22]** IETF RFC 8725 (BCP 225), _JSON Web Token Best Current Practices_, February 2020. <https://www.rfc-editor.org/rfc/rfc8725>. §3.1 algorithm allowlists; §3.8 to §3.11 issuer, audience, and explicit typing.
- **[R23]** W3C, _Content Security Policy Level 3_, Working Draft, accessed 2026-10-06. <https://www.w3.org/TR/CSP3/>. §6.4.2 `frame-ancestors` "restricts the origins which may embed the protected resource in a frame"; §6.4.2.2: "The `frame-ancestors` directive is meant to replace the `X-Frame-Options` header. User agents that support CSP should prefer `frame-ancestors` over `X-Frame-Options` when both are present." §6.4.1 `form-action` "restricts the URLs to which a form can be submitted."
- **[R29]** IETF RFC 6797, _HTTP Strict Transport Security (HSTS)_, November 2012. <https://www.rfc-editor.org/rfc/rfc6797>. §8.1: "If an HTTP response is received over insecure transport, the UA MUST ignore any present STS header field(s)."

### Informative

- **[R13]** IETF draft-ietf-oauth-v2-1-16, _The OAuth 2.1 Authorization Framework_, Internet-Draft, accessed 2026-09-30. <https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/>. Omits the password grant, citing RFC 9700 §2.4. A draft, not a standard.
- **[R14]** IETF draft-ietf-oauth-rfc7523bis-11, Internet-Draft, accessed 2026-09-30, <https://datatracker.ietf.org/doc/draft-ietf-oauth-rfc7523bis/>; and OpenID Foundation, _Notice of a Security Vulnerability_ (CVE-2025-27370, CVE-2025-27371), <https://openid.net/notice-of-a-security-vulnerability/>. A client assertion's audience is the authorization server's issuer as its sole value.
- **[R15]** IETF RFC 6819, _OAuth 2.0 Threat Model and Security Considerations_, January 2013. <https://www.rfc-editor.org/rfc/rfc6819>. §5.1.5.3: use short expiration times.
- **[R16]** Keycloak, _Enabling and disabling features_, accessed 2026-09-30. <https://www.keycloak.org/server/features>. `client-secret-rotation` is a preview feature, not recommended for production.
- **[R17]** Keycloak, _Admin REST API_ 26.7.5. <https://www.keycloak.org/docs-api/26.7.5/rest-api/index.html>. `GET /admin/realms/{realm}/clients/{client-uuid}/client-secret` returns the secret.
- **[R18]** OWASP, _Logging Cheat Sheet_, accessed 2026-09-30. <https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html>. Access tokens, passwords, and keys are data to exclude from logs.
- **[R19]** Center for Internet Security, _CIS Controls v8.1_, accessed 2026-09-30. <https://www.cisecurity.org/controls/v8-1>. 5.5 inventory of service accounts; 6.2 disabling accounts rather than deleting them may preserve audit trails.
- **[R20]** NIST SP 800-61 Rev. 3, _Incident Response Recommendations and Considerations for Cybersecurity Risk Management_, April 2025. <https://csrc.nist.gov/pubs/sp/800/61/r3/final>. RS.MI-01 and RS.MI-02: containment, and eradication of persistence mechanisms and entry points.
- **[R24]** OWASP, _Clickjacking Defense Cheat Sheet_, accessed 2026-10-06. <https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html>. `frame-ancestors 'none'`: "This setting is recommended unless a specific need has been identified for framing"; `X-Frame-Options`: "The 'DENY' setting is recommended unless a specific need has been identified for framing", and the header "has been obsoleted in favor of the frame-ancestors directive".
- **[R25]** OWASP, _Content Security Policy Cheat Sheet_, accessed 2026-10-06. <https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html>. The strict policy: "script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none';", or the same with a hash; "a strong CSP provides an effective second layer of protection" and "CSP should not be relied upon as the only defensive mechanism against XSS".
- **[R26]** Keycloak 26.7.5, the release the kernel pins. Server Administration Guide, _Clickjacking_: "By default, Keycloak only sets up a _same-origin_ policy for iframes", <https://www.keycloak.org/docs/26.7.5/server_admin/index.html#clickjacking>. Source at tag `26.7.5`, <https://github.com/keycloak/keycloak/tree/26.7.5>: `BrowserSecurityHeaders` and `ContentSecurityPolicyBuilder` (the default policy, `frame-src 'self'; frame-ancestors 'self'; object-src 'none'`), and the `keycloak.v2` login templates, where `template.ftl` and `login-otp.ftl` carry inline `<script>` and `onclick`, `login.ftl` an inline `onsubmit`, and `webauthn-authenticate.ftl` an inline module script holding `challenge : ${challenge?c}`. Issue #16277, _Hardened Content Security Policy (CSP)_, open since 2023-01-05: "The default Content Security Policy (CSP) used by Keycloak is not locked down enough", <https://github.com/keycloak/keycloak/issues/16277>; pull request #49879, _Generate CSP nonce for Freemarker_, open, <https://github.com/keycloak/keycloak/pull/49879>.
- **[R27]** W3C WebAppSec, issue #8, _CSP: form-action and redirects_, open since 2015-10-07, accessed 2026-10-06. <https://github.com/w3c/webappsec-csp/issues/8>.
- **[R28]** GitLab, merge request 90082, _Allowlist OAuth application redirect URI in CSP_, merged 2022-06-17. <https://gitlab.com/gitlab-org/gitlab/-/merge_requests/90082>. An OAuth authorization page "immediately redirects to the OAuth application's `redirect_uri` and Chrome takes the redirection target into account when evaluating CSP violations."
- **[R30]** OWASP, _Authentication Cheat Sheet_, accessed 2026-10-06. <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>. Authentication and error messages: "the processing time can be significantly different according to the case (success vs failure) allowing an attacker to mount a time-based attack"; the remedy computes the password hash whether or not the user exists.
- **[R31]** Oscar Reparaz, Josep Balasch and Ingrid Verbauwhede, _Dude, is my code constant time?_, DATE 2017. <https://eprint.iacr.org/2016/1123.pdf>; reference implementation <https://github.com/oreparaz/dudect>. Measurements of two input classes compared by "a Welch's t-test to determine if the function runs in constant time"; the long tail is dropped by keeping "the x% percent fastest timings" alongside the uncropped test; the implementation's `t_threshold_moderate` is 10 ("Pankaj likes 4.5 but let's be more lenient", the TVLA threshold).
- **[R32]** Keycloak 26.7.5 source, `AuthenticatorUtils.dummyHash`: "simulate hashing of some "dummy" password. The purpose is to make the user enumeration harder, so the authentication request with non-existing username also need to simulate the password hashing overhead", and `AbstractUsernameFormAuthenticator.validatePassword`, which returns for an empty password and for a brute-force lockout before the password is hashed, <https://github.com/keycloak/keycloak/tree/26.7.5/services/src/main/java/org/keycloak/authentication/authenticators>. Issue #51887, _Username enumeration via empty-password timing_, open, `priority/important`, <https://github.com/keycloak/keycloak/issues/51887>.
