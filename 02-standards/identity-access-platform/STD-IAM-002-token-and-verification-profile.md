---
doc_meta:
  id: STD-IAM-002
  title: Enterprise Token and Verification Profile
  owner: Identity Platform Team
  version: 1.8.0
  status: approved
  classification: restricted
  governed_by: PAD-PLT-001
  review_cycle_days: 180
  created_date: 2026-08-11
  last_reviewed: 2026-10-08
---

# Enterprise Token and Verification Profile (STD-IAM-002)

## 1. Objective & Scope

Define the normative claim set, audience classes, token-lifetime classes, and
verification rules for every security artifact issued by the Scnehaux Identity
Runtime, so that a protected resource can validate a token locally and a revocation
can be given a stated maximum enforcement delay.

STD-IAM-001 §3.2 sets a 15-minute ceiling on access token lifetime and defers the
class system to this standard. STD-IAM-001 §3.4 requires maximum enforcement delay to
be computed as propagation time plus remaining access token lifetime. This standard
supplies the second term. Neither standard states an enforcement interval alone.

This standard applies to internal Scnehaux access tokens, ID tokens, external and
partner token profiles, workload tokens, and every protected resource that accepts
them. It does not define authentication ceremonies, credential policy, session
lifecycle, or federation trust, which remain with STD-IAM-001 and the Identity
Runtime.

## 2. Design Principles

- **Lifetime is derived, not chosen** — a token lifetime is the consequence of a
  declared revocation target minus the propagation budget, never a latency
  optimisation
- **Local verification by default** — a protected resource validates a signed token
  without a synchronous call to Identity on the ordinary request path
- **Audience decides the profile** — the claim set a token carries follows the
  audience it was issued for, not the caller that requested it
- **A token carries identity and context, never authorization** — permissions,
  entitlements, and business roles stay with their owning domains
- **Correlation is minimised** — an identifier stable across the enterprise is
  released only to audiences that require it
- **Fail closed on absence** — a missing mandatory claim is a rejection, never a
  default

## 3. Normative Rules

### 3.1 Audience Classes

Every token is issued for exactly one audience class, and the class determines the
claim set, the lifetime class, and the subject form.

| Class        | Meaning                                                                                       | Subject form                                         |
| :----------- | :-------------------------------------------------------------------------------------------- | :--------------------------------------------------- |
| `internal`   | A Scnehaux-owned protected resource inside the enterprise trust boundary                      | Shared issuer-scoped `sub` plus `principal_id`       |
| `privileged` | An administrative or control-plane surface performing irreversible or cross-tenant operations | As `internal`, with elevated assurance claims        |
| `workload`   | A non-human service, job, connector, or governed agent identity                               | Workload subject; no human `principal_id`            |
| `external`   | A partner, customer-owned, or third-party relying party                                       | Pairwise `sub`; no enterprise correlation identifier |

- Every access token MUST carry `aud`, and `aud` MUST name registered protected
  resources only [R6][R8][R11].
- **A protected resource is named by its own `resource` registration, which holds no
  credential.** A client that authenticates to the kernel (a confidential, workload or
  administrative client) MUST NOT be named in any `aud`, including the client a service uses for
  its own outbound calls. The resource identifier and the client identifier are different things:
  RFC 9068 §4 has the resource check that `aud` holds "an identifier the resource server expects for
  itself" [R6], and Microsoft Entra has a Web API "only accept tokens containing one of their AppId
  URIs as the `aud` claim", the client being a separate party [R21]. In the kernel the difference is
  also a privilege: standard token exchange requires that "the `subject_token` sent to the token
  exchange endpoint must have the requester client set as an audience in the `aud` claim" [R22], so
  a credential-holding client in `aud` is a client entitled to exchange every token sent to that
  resource. A keyless `resource` registration cannot authenticate, so it can exchange nothing. A
  service's API is therefore registered as `<service>-api` (`identity-control-api`,
  `organization-control-api`), distinct from every client the service authenticates as.
  The cost is one registration per service and a changed `aud` for every caller already
  configured, against a token exchange path that would otherwise sit with the most privileged
  client in the estate.
- A protected resource MUST reject a token whose `aud` does not name it [R1][R5][R6].
- A token MUST NOT be issued for more than one audience class.

#### 3.1.1 Privileged Scope Forms

The `privileged` class covers three operations with incompatible context requirements, and
conflating them made the class unimplementable. A token MUST declare exactly one form.

| Form              | Meaning                                                                                                                                               | Context claim                                                                                               |
| :---------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `tenant-scoped`   | A privileged operation performed inside one Tenant — suspending a Workspace, revoking a Membership in that Tenant                                     | `tenant_id` MUST                                                                                            |
| `provider-scope`  | A provider operation that is cross-tenant or has no Tenant at all — minting a Principal, registering a protected resource, cross-tenant investigation | `provider_scope` MUST, except at a resource that holds the grant or its projection; `tenant_id` MUST NOT    |
| `resource-scoped` | An operation on records the resource itself holds grants over — an owner managing the client registrations they own                                   | `tenant_id` MUST NOT; the authority is the grant the resource records for the `principal_id` and the target |

`provider_scope` names the bounded authority the operation runs under, and it exists because
the alternative was to put a Tenant identifier on a token whose action does not belong to a
Tenant. The claim MUST name a registered provider scope or an explicit bounded Tenant set; a
value meaning "all Tenants" MUST NOT be issued, because an unbounded scope is what
`PAD-PLT-002 §5.2` requires cross-tenant administration never to be.

**The resource that holds a provider grant, or a projection of it, checks its record.** A provider
scope is a grant Organization records, and it confers authority only while an activation of it, or
an emergency grant, is in force (`ADR-ORG-002 §5.1`, §5.2). The Organization Control API holds the
grants. The Identity Control API holds a projection of the grants for `provider:identity-control`
(`ADR-IAM-001 §5.6`, `ADR-ORG-002 §5.3`). Each MUST check its record for each request, by the
token's `principal_id`, and MUST NOT read the grant from a claim (`ADR-ORG-001 §5.11`). A claim would
outlive an activation ended early until the token carrying it expired. That is how Google
Cloud IAM and Kubernetes decide access: the token establishes who the caller is, and the resource
evaluates the policy it holds [R19][R20]. Projecting the grant to its holder would also put in
every provider token a claim with no meaning for the resource receiving it, which RFC 9068 forbids
for `scope` and RFC 8707 tells an authorization server to trim [R6][R11]. A provider-scope token
sent to the holder carries `principal_id`, `subject_type` `human`, `acr` and `auth_time`, and no
`tenant_id`. A revoked grant then stops the next request rather than the next token. No resource
in this estate checks a provider grant from a claim, so no `provider_scope` claim is issued. The
claim and rule 10 remain for a future resource that neither holds a grant nor a projection of it,
and adopting one needs a decision of its own.

**The `resource-scoped` form** is for an authority bounded by records the resource holds, such as
the owners of a client registration (`ADR-IAM-003`). The token carries `principal_id`,
`subject_type` `human`, `acr` and `auth_time`, and no `tenant_id`; the resource reads the grant for
the `principal_id` and the record the request names, for each request, and refuses a request naming
anything else. A caller whose `principal_id` holds provider authority in force at the resource is
a provider, and is not narrowed to this form. The resource separates the forms by route: a provider-only route refuses a
`resource-scoped` caller before reading any record.

`provider_scope` names one scope. A Principal holding grants for two resources outside
Organization would need two scopes in one claim, sent to both resources, which is the claim RFC
9068 and RFC 8707 rule out. That case is not supported, and no registered scope needs it today:
`provider:identity-control` is the only scope a resource outside Organization checks.

**A client may obtain both the tenant-scoped and the provider-scope form only when its registration
says `per-sign-in` (1.7.0, `ADR-IAM-008`).** Such a client is `confidential`. No form scope is among
its defaults, and each authorization request names exactly one form:
`scnehaux-privileged organization:<tenant_id>` for one Tenant, or `scnehaux-provider` with no
`organization` scope. OAuth puts scope in the request, and a refresh cannot widen it [R24]. On the
callback the client refuses a Tenant sign-in whose ID token `tenant_id` differs from the Tenant asked
for, and a provider sign-in whose ID token carries one, as Auth0 asks a client to validate `org_id`
[R25]. Entering the provider form asks for `aal2` with `max_age=0`. Changing form or Tenant is a new
sign-in, never a refresh. Every other `privileged` registration names one form, and its client holds
that form's scope as a default.

A provider-scope token MUST take lifetime class `L0`, MUST carry `acr` and `auth_time`, and its
issuance MUST be evidenced with the actor, the scope, and the reason. At the resource that holds
the grant, the grant's own record and the access record written for each request are that
evidence. Creating a Principal is provider-scope: it is irreversible, it belongs to no Tenant,
and it is the operation from which every later Membership is derived.

### 3.2 Claim Set

| Claim              | `internal` | `privileged`                                                                                      | `workload`              | `external`     |
| :----------------- | :--------- | :------------------------------------------------------------------------------------------------ | :---------------------- | :------------- |
| `iss`              | MUST       | MUST                                                                                              | MUST                    | MUST           |
| `sub`              | MUST       | MUST                                                                                              | MUST                    | MUST, pairwise |
| `aud`              | MUST       | MUST                                                                                              | MUST                    | MUST           |
| `iat`, `exp`       | MUST       | MUST                                                                                              | MUST                    | MUST           |
| `jti`, `client_id` | MUST       | MUST                                                                                              | MUST                    | MUST           |
| `scope`            | SHOULD     | SHOULD                                                                                            | SHOULD                  | SHOULD         |
| `principal_id`     | MUST       | MUST                                                                                              | MUST                    | MUST NOT       |
| `subject_type`     | MUST       | MUST                                                                                              | MUST                    | MUST NOT       |
| `tenant_id`        | MUST       | MUST when `tenant-scoped`; MUST NOT when `provider-scope`                                         | MUST when tenant-scoped | MUST NOT       |
| `workspace_id`     | MAY        | MAY                                                                                               | MAY                     | MUST NOT       |
| `provider_scope`   | MUST NOT   | MUST when `provider-scope`, except at a holder of the grant or its projection; MUST NOT otherwise | MUST NOT                | MUST NOT       |
| `acr`, `auth_time` | MAY        | MUST                                                                                              | MUST NOT                | MAY            |
| `workload_owner`   | MUST NOT   | MUST NOT                                                                                          | MUST                    | MUST NOT       |

**`tenant_id` is the Tenant the token was issued for, chosen by the client per sign-in (1.6.0).** A
client asks for one Tenant with the kernel's `organization:<tenant_id>` scope, and the kernel issues
the claim only for a member of that Tenant (`ADR-IAM-006`). A refresh keeps it; another Tenant is
another sign-in. Before 1.6.0 the token also carried `membership_version` and
`tenant_security_version`. They are removed: the kernel has no supported place to keep a version per
Membership, and the resource's check of current state in §3.5 step 8 refuses a revoked context
without them.

A workload is a Principal. PAD-PLT-001 defines a Principal as a stable human, service,
workload, or governed-agent security subject, and Membership binds a `principal_id`
together with a `subject_type` of `human` or `workload`. A workload token therefore
carries `principal_id` like any other, and `subject_type` is what distinguishes it.

Issuing workloads into a separate identifier space would leave a workload Membership
unverifiable: the consumer would hold a Membership keyed on `principal_id` and a token
carrying no such claim.

- `sub` remains the issuer-scoped protocol subject and MUST NOT be used as an
  enterprise foreign key by any Scnehaux domain.
- `principal_id` is the enterprise reference and MUST be the identifier internal
  domains persist.
- A token that carries Tenant context MUST carry exactly one active Tenant and at most one Workspace
  context. The set of Memberships held by a Principal MUST NOT be placed in a token,
  bounded or otherwise.
- Product permissions, entitlements, business roles, and quota state MUST NOT appear
  in any token.
- Personal data beyond what the audience requires MUST NOT appear in any token.
  Verified email and display name are released to `external` audiences only through an
  approved scope and consent.
- An access token is a JWT access token as RFC 9068 defines it [R6]. Its header `typ` MUST
  be `at+jwt`, which is what lets a resource tell it from an ID token or any other JWT, and
  `iss`, `exp`, `aud`, `sub`, `client_id`, `iat` and `jti` are the claims RFC 9068 §2.2
  requires. `scope` carries the scopes granted, when any were requested.
- A claim not defined here, by RFC 9068 §2.2, or by an approved audience profile MUST NOT
  be added to a token.
- The claims `principal_id`, `subject_type`, `tenant_id`, `workspace_id`, `provider_scope` and
  `workload_owner` are this platform's private claims, which RFC 9068
  §2.2.2 allows within a private subsystem [R6]. `acr` and `auth_time` are OpenID Connect's
  [R7], and keep their meaning across a refresh [R9].
- **`acr` takes one of the levels `ADR-IAM-004 §5.1` names:** `aal1` (one factor), `aal2` (two
  distinct factors, NIST SP 800-63B-4 AAL2 [R23]), and `phr` (phishing-resistant, reserved). They are
  ordered `aal1` < `aal2` < `phr`.
  - A resource that requires a level accepts that level or a higher one.
  - It counts any other value as below `aal1`, the kernel's unmapped `0` and `1` included.
  - It answers an insufficient token with RFC 9470's challenge, naming the level in `acr_values`
    [R9].
- **Three claims are written by the kernel itself, and are admitted.** The pinned kernel writes
  `azp`, `sid` and a payload `typ` into the access tokens it issues from its token code, not
  through a mapper, so none can be removed without a kernel extension (`ADR-IAM-001 §5.7`).
  `azp` is OpenID Connect's authorized party [R7]. `sid` is the session identifier OpenID
  Connect logout defines [R18], which a BFF needs to match a back-channel logout to its
  session. The payload `typ` is the kernel's own, and a consumer MUST NOT base a decision on
  it: the header `typ` is the type check (§3.5).
- **An access token carries no personal data and no role.** Email, names, usernames, and
  realm or client role claims MUST NOT appear in an access token of any class. A first-party
  BFF that shows the signed-in Principal's name reads it from its ID token, which the
  `scnehaux-profile` scope gives it (§3.2.1).

#### 3.2.1 Claim Projection Profiles

The identity kernel MUST realize the table above through audience-specific client
scopes rather than realm-wide default mappers:

| Client scope          | Required projected claims                                                                                                  |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| `scnehaux-internal`   | `principal_id`, `subject_type`; `tenant_id` through the `organization` scope when a Tenant is asked for                    |
| `scnehaux-privileged` | Internal claims plus mandatory `acr` and `auth_time`; `tenant_id` through the `organization` scope when tenant-scoped      |
| `scnehaux-provider`   | `principal_id`, `subject_type`, `acr`, `auth_time`; `provider_scope` and `tenant_id` prohibited (§3.1.1)                   |
| `scnehaux-workload`   | `principal_id`, `subject_type=workload`, `workload_owner`; `tenant_id` through the `organization` scope when tenant-scoped |
| `scnehaux-external`   | Pairwise `sub`; enterprise and context claims prohibited                                                                   |
| `scnehaux-profile`    | `name` and `preferred_username` in the ID token only, never in an access token; requested by a first-party BFF             |

The client registration authority MUST attach exactly one of the five audience profile scopes.
`scnehaux-profile` is not an audience profile: a first-party BFF requests it at sign-in for the
name it shows. **`tenant_id` reaches a token only through the kernel's `organization` scope (1.6.0).**
The registration authority attaches it, optional, only to a client whose profile may carry
`tenant_id`, and it is neither a realm default nor a realm default optional scope (`ADR-IAM-006
§5.3`). A mapper carrying `principal_id` or context claims MUST NOT be a realm default
because that would disclose enterprise correlation identifiers to external clients.

**The realm's default client scopes are `basic` and `acr` only.** `basic` gives `sub` and
`auth_time`, and `acr` the authentication context; a workload client does not hold `acr`. The
kernel's built-in `profile`, `email`, `roles` and `web-origins` scopes MUST NOT be realm
defaults: each puts a claim this table does not define into an access token, personal data among
them. The registration authority detaches any of them from a client it registers or adopts, and the
reconciler holds them detached.

**The built-in `service_account` scope keeps only its `client_id` mapper.** The pinned kernel
attaches it to every client whose service accounts are enabled, and attaches it again on every
update of such a client, so detaching it from a workload does not hold. Its other two mappers write
the client's network address, `clientHost` and `clientAddress`, which this table does not define.
So the identity kernel declares the scope with its `client_id` mapper alone, a workload holds it,
and the address never reaches a token.

#### 3.2.2 Signing Algorithm Allowlist

- `PS256` with an RSA key of at least 3072 bits is REQUIRED for newly registered
  `internal`, `privileged`, and `workload` profiles and is the default for `external`.
  `PS256` is RSASSA-PSS with SHA-256, which JOSE allows with a key of 2048 bits or more
  [R4]. The 3072-bit floor is this platform's: it gives 128-bit security strength, where
  2048 bits gives 112 [R10].
- `RS256` MAY be used only for an external compatibility registration that records the
  relying party, evidence that `PS256` is unsupported, an owner, and an expiry date.
- No algorithm other than `PS256` or an explicitly registered `RS256` compatibility
  case is permitted in the initial baseline. In particular, `none` and every symmetric
  `HS*` algorithm are prohibited for enterprise-issued access tokens.
- The registration fixes the permitted algorithm before a token is read. A verifier
  MUST compare the token header to that allowlist and MUST NOT select an implementation
  from the untrusted `alg` header alone [R2][R5].
- **This allowlist departs from two mandatory-to-implement rules on purpose.** RFC 9068 §2.1
  requires authorization and resource servers to support `RS256` [R6], and OpenID Connect
  Core §15.1 requires an OpenID Provider to support `RS256` for ID tokens [R7]. This platform
  follows the FAPI 2.0 Security Profile instead, which permits `PS256`, `ES256` and `Ed25519`
  and not `RS256` [R12]: `RS256` uses PKCS#1 v1.5 padding, which carries no security proof,
  and a second algorithm puts an algorithm branch in every verifier (`ADR-IAM-002`). A
  relying party that can verify only `RS256` uses the registered compatibility exception
  above. No internal resource accepts `RS256`.
- The pinned identity-kernel compatibility suite MUST prove issuance and verification
  of every permitted algorithm. Failure to issue `PS256` blocks that kernel candidate.

### 3.3 Token-Lifetime Classes

Access token lifetime is derived from the revocation target declared for the risk
class, minus the propagation budget the platform owns:

```text
access_token_lifetime  =  revocation_target  −  propagation_budget
```

The lifetime figures below are this platform's choice. The external sources require access
tokens to be short-lived and audience-restricted and name no number [R8].

The propagation budget is the interval between accepting a revocation and applying it
at every enforcing mechanism. It is owned by the control plane and is currently
budgeted below 10 seconds, with 60 seconds reserved here as the planning figure so a
degraded propagation path does not silently invalidate the derived lifetime.

| Class | Revocation target | Access token lifetime | Applies to                                                                                                   |
| :---- | :---------------- | :-------------------- | :----------------------------------------------------------------------------------------------------------- |
| `L0`  | 5 minutes         | 4 minutes             | `privileged` in both scope forms; any surface performing irreversible, financial, or cross-tenant operations |
| `L1`  | 10 minutes        | 9 minutes             | `internal` product APIs handling tenant-scoped business data                                                 |
| `L2`  | 16 minutes        | 15 minutes            | `external` and partner profiles, bounded by the STD-IAM-001 §3.2 ceiling                                     |
| `L3`  | 10 minutes        | 9 minutes             | `workload`, unless a shorter class is declared by the workload profile                                       |

- Every protected resource MUST be assigned exactly one lifetime class, recorded in
  its registration.
- A lifetime longer than the class permits MUST NOT be issued, and MUST NOT be
  configured per client.
- Increasing a lifetime class MUST carry the increase into the stated maximum
  enforcement delay of every revocation class that affects the audience.
- A resource's lifetime class MUST be changed only as a registration change (1.8.0): proposed
  with a reason by an owner of the resource or a provider, naming one of the classes above, and
  approved in production by a provider other than the proposer (`ADR-IAM-003 §5.9`). The change
  states each class's access token lifetime and revocation target, and its apply moves the derived
  lifespan of every client whose audience names the resource in the same transaction. Microsoft
  states what the figure trades: "the amount of time that the client retains access after the user's
  account is disabled" [R26].
- Refresh token lifetime, rotation, and reuse detection remain with the identity
  kernel under STD-IAM-001 §3.2. A refresh MUST NOT extend an access token beyond its
  class.

### 3.4 Long-Lived Connections

A connection authenticated once and held open receives no further request to reject,
so the token-lifetime term does not bound it.

- A consumer holding WebSocket, server-sent-event, or equivalent long-lived
  connections MUST register each connection against the Principal and Tenant context
  that authorized it.
- Maximum connection lifetime MUST NOT exceed the access token lifetime class of the
  audience that authorized it.
- A priority revocation event MUST close every matching connection.
- A connection that cannot be matched to a registered context MUST be closed rather
  than retained.

### 3.5 Verification Rules

A protected resource MUST perform the following before acting on a token, and MUST
fail closed on any failure:

1. Resolve the signing key by `kid` from the issuer's approved JWKS [R3]. An unknown `kid`
   is resolved by fetching that JWKS again, rate-limited, which is how a verifier learns a
   rotated key [R7], and the token is rejected when the `kid` stays unknown. Signing material
   is never fetched from a location the token names.
2. Verify the signature using the algorithm permitted by §3.2.2 and the audience
   registration.
   An algorithm named only inside the token MUST NOT select the verification path.
3. Verify `iss` against the expected issuer for the environment [R5][R6].
4. Verify `aud` names this resource [R1][R6].
5. Verify the header `typ` is `at+jwt`, and reject a token issued for a different purpose,
   an ID token among them [R5][R6].
6. Verify `iat` and `exp` with a clock-skew allowance no greater than 60 seconds [R1]. The
   60-second cap is stricter than the "few minutes" RFC 7519 allows.
7. Reject an `internal`, `privileged`, or `workload` token whose `principal_id` is
   absent, and reject a `workload` token whose `workload_owner` is absent.
8. Where `tenant_id` is present, reject the token unless the local projection holds the
   Principal's Membership in that Tenant as active and the Tenant as active (1.6.0,
   `ADR-IAM-006 §5.4`). The check is of current state, not of the token: a revoked
   Membership or a suspended Tenant is refused as soon as the resource has applied the
   event, however recently the token was issued. A resource holding no projection of that
   Tenant's Memberships cannot make the check and rejects the token. Before 1.6.0 this
   step compared version claims the token carried.
9. Reject a `privileged` token that carries neither `tenant_id` nor a provider authority,
   at a resource with no `resource-scoped` grant for it, and reject one that carries both
   `tenant_id` and a provider authority. A privileged token whose scope form cannot be
   determined has no bounded authority, and the safe reading of an ambiguous scope is
   not the narrow one — it is refusal. The provider authority is the `provider_scope`
   claim, except at a resource that holds provider grants or their projection, where it is
   provider authority in force, an approved activation or an emergency grant, that the
   resource records for the token's `principal_id` (§3.1.1).
10. Reject a `provider_scope` value that is not a registered scope or an explicit
    bounded Tenant set. At a resource that holds provider grants or their projection, reject a
    token whose `principal_id` holds no provider authority in force for a provider route, or
    whose `subject_type` is not `human`.
11. Enforce Product authorization locally. A valid signature is one input and is never
    the authorization decision.

- Introspection or an equivalent online check MAY be used where opaque-token or
  active-state semantics require it, and MUST NOT be placed on an ordinary request
  path where local validation plus bounded revocation mechanisms satisfy the
  requirement [R13].
- Public verification material MUST remain published for at least the maximum lifetime
  of any artifact signed with that key, plus consumer cache and clock-skew margin [R7].

### 3.6 External Profiles

- An `external` profile MUST be identified by audience and validated against its
  declared profile rather than against the internal rules.
- An `external` token MUST NOT carry `principal_id` or `tenant_id`.
- Pairwise subjects MUST be used where cross-relying-party correlation is not
  justified [R7][R14].
- Attribute release to an external relying party MUST be minimised by purpose and
  governed by an approved scope.

### 3.7 Evidence

- Audit and evidence records MUST retain `principal_id` together with `iss` and `sub`,
  so protocol-level and enterprise-level identity remain reconcilable after any future
  issuer change.
- A token, a credential, and a signing key MUST NOT appear in a log, a trace, an
  event payload, or an error response.
- A verification failure MUST be recorded with its failure reason class, issuer, and
  audience, and MUST NOT record the token.

### 3.8 Bearer Tokens and Sender Constraint

RFC 9700 §2.2.1 says authorization and resource servers SHOULD sender-constrain access
tokens, by mutual TLS or DPoP [R8][R15][R16]. The initial baseline does not: its access
tokens are bearer tokens. That is a recorded gap, and it is bounded by where the tokens go.

- A browser never holds an access token. The BFF keeps it server-side and the browser holds
  only a session cookie [R17].
- A service calls another over mutual TLS or with a service-mesh token (`STD-GLB-001`), so a
  token in transit between services is inside a channel that authenticates both ends.
- An `external` relying party holds its tokens outside both paths. It is the case the gap
  leaves open.

Sender constraint is decided again, in an ADR, before an `external` profile is issued to a
relying party the platform does not operate, or before an access token is issued to a
browser. Until then the gap is tracked on the Identity Runtime roadmap.

## 4. Exceptions

Deviation from this standard requires formal exception approval under GDC-000 with an
explicit threat model, compensating controls, a named owner, an expiry date, and the
revocation enforcement delay that results from the deviation.

A longer token lifetime is the most common request and is the least separable from
risk: granting it lengthens the enforcement delay of every revocation class affecting
that audience, so the resulting delay must be stated in the request rather than
discovered afterwards.

## 5. Enforcement Mechanism

- Token contract tests asserting the claim set per audience class, the RFC 9068 claims, and
  the `at+jwt` header type, executed against the pinned identity kernel release.
- Token contract tests asserting that an access token carries no claim outside §3.2, RFC 9068
  §2.2 and the three kernel-written claims, and no personal data.
- Negative token tests proving external clients never receive `principal_id`,
  `subject_type`, Tenant, or Workspace claims.
- Algorithm tests proving `PS256` issuance and verification and rejecting `none`,
  symmetric algorithms, header-selected algorithms, and unregistered `RS256`.
- Reference verifier conformance tests covering each rule in §3.5, including negative
  cases for absent `principal_id`, wrong `aud`, unknown `kid`, and a `tenant_id` whose
  Membership or Tenant is not active in the projection.
- Client registration validation rejecting a protected resource without an assigned
  lifetime class.
- Configuration assertion that no client carries a token lifetime exceeding its class.
- Registration change tests proving a lifetime-class change moves the lifespan of every client whose audience names the resource, rolls back with the kernel, and is approved in production by a provider other than its proposer.
- Connection registry tests proving a priority revocation closes matching long-lived
  connections within budget.
- Secret and token scanning across logs, traces, events, and error responses.
- Architecture fitness functions preventing permission, entitlement, or business role
  claims from entering a token.

## 6. References

The external sources the rules above rest on, cited as `[Rn]`. A rule stricter than its source,
or departing from it, says so where it is stated. The lifetime figures and the long-lived
connection rules are this platform's own and cite no external source; who changes a class, and how,
rests on `ADR-IAM-003 §5.9` and its sources. The Tenant selection and the
current-state check follow `ADR-IAM-006`, whose sources are the platforms and OWASP guidance it
quotes.

### Normative

- **[R1]** IETF RFC 7519, _JSON Web Token (JWT)_, May 2015. <https://www.rfc-editor.org/rfc/rfc7519>. §4.1.3 `aud` rejection; §4.1.4 a small clock-skew leeway.
- **[R2]** IETF RFC 7515, _JSON Web Signature (JWS)_, May 2015. <https://www.rfc-editor.org/rfc/rfc7515>. §5.2: which algorithms may be used is an application decision.
- **[R3]** IETF RFC 7517, _JSON Web Key (JWK)_, May 2015. <https://www.rfc-editor.org/rfc/rfc7517>. §4.5: `kid` selects a key within a set during rollover.
- **[R4]** IETF RFC 7518, _JSON Web Algorithms (JWA)_, May 2015. <https://www.rfc-editor.org/rfc/rfc7518>. §3.5: `PS256`, with a key of 2048 bits or larger.
- **[R5]** IETF RFC 8725 (BCP 225), _JSON Web Token Best Current Practices_, February 2020. <https://www.rfc-editor.org/rfc/rfc8725>. §3.1 algorithm allowlists; §3.8 issuer; §3.9 audience; §3.11 explicit typing.
- **[R6]** IETF RFC 9068, _JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens_, October 2021. <https://www.rfc-editor.org/rfc/rfc9068>. §2.1 `typ` `at+jwt`, `none` prohibited, `RS256` mandatory to implement; §2.2 required claims; §2.2.2 private claims; §2.2.3 every scope must mean something to the resources `aud` names; §4 validation.
- **[R7]** OpenID Foundation, _OpenID Connect Core 1.0 incorporating errata set 2_, December 2023. <https://openid.net/specs/openid-connect-core-1_0.html>. §2 `acr` and `auth_time`; §8 pairwise identifiers; §10.1.1 refetching a key set on an unfamiliar `kid` and retaining decommissioned keys; §15.1 `RS256` for ID tokens.
- **[R8]** IETF RFC 9700 (BCP 240), _Best Current Practice for OAuth 2.0 Security_, January 2025. <https://www.rfc-editor.org/rfc/rfc9700>. §2.2.1 sender-constrained tokens; §2.3 audience-restricted access tokens.
- **[R9]** IETF RFC 9470, _OAuth 2.0 Step Up Authentication Challenge Protocol_, September 2023. <https://www.rfc-editor.org/rfc/rfc9470>. §6.1: `acr` and `auth_time` do not change on renewal.
- **[R10]** NIST SP 800-57 Part 1 Rev. 5, _Recommendation for Key Management: Part 1 – General_, May 2020. <https://doi.org/10.6028/NIST.SP.800-57pt1r5>. Table 2: RSA 2048 bits gives 112-bit and 3072 bits 128-bit security strength.

- **[R23]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator Management_, August 2025. <https://pages.nist.gov/800-63-4/sp800-63b.html>. §2.1–§2.3: AAL1, AAL2 ("two distinct authentication factors") and AAL3.
- **[R18]** OpenID Foundation, _OpenID Connect Back-Channel Logout 1.0 incorporating errata set 1_, December 2023. <https://openid.net/specs/openid-connect-backchannel-1_0.html>. §2.4 the `sid` claim in a logout token, matching the session an ID token's `sid` named.
- **[R24]** IETF RFC 6749, _The OAuth 2.0 Authorization Framework_, October 2012. <https://www.rfc-editor.org/rfc/rfc6749>. §3.3: "The authorization and token endpoints allow the client to specify the scope of the access request using the "scope" request parameter"; §6: "The requested scope MUST NOT include any scope not originally granted by the resource owner".

### Informative

- **[R11]** IETF RFC 8707, _Resource Indicators for OAuth 2.0_, February 2020. <https://www.rfc-editor.org/rfc/rfc8707>. Audience restriction to the resource requested; §2.2 downscoping a token to what the resource needs to know.
- **[R12]** OpenID Foundation, _FAPI 2.0 Security Profile_, Final, February 2025. <https://openid.net/specs/fapi-security-profile-2_0-final.html>. §5.4.1: `PS256`, `ES256` or `Ed25519`.
- **[R13]** IETF RFC 7662, _OAuth 2.0 Token Introspection_, October 2015. <https://www.rfc-editor.org/rfc/rfc7662>. §4: caching introspection trades freshness for traffic.
- **[R14]** NIST SP 800-63C-4, _Digital Identity Guidelines: Federation and Assertions_, August 2025. <https://doi.org/10.6028/NIST.SP.800-63C-4>. §3.4.1 pairwise pseudonymous identifiers. It governs federation assertions, not API access tokens.
- **[R15]** IETF RFC 8705, _OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens_, February 2020. <https://www.rfc-editor.org/rfc/rfc8705>.
- **[R16]** IETF RFC 9449, _OAuth 2.0 Demonstrating Proof of Possession (DPoP)_, September 2023. <https://www.rfc-editor.org/rfc/rfc9449>.
- **[R17]** IETF RFC 10017, _OAuth 2.0 for Browser-Based Applications_ (Best Current Practice), August 2026. <https://www.rfc-editor.org/rfc/rfc10017>. The backend-for-frontend pattern.
- **[R19]** Google Cloud, _IAM overview_, accessed 2026-10-01. <https://docs.cloud.google.com/iam/docs/overview>. An allow policy is attached to a resource, and IAM checks the resource's allow policy when an authenticated principal accesses it.
- **[R20]** Kubernetes, _Authorization_, accessed 2026-10-01. <https://kubernetes.io/docs/reference/access-authn-authz/authorization/>. Authorization takes place in the API server, against the user and groups authentication established; access is denied by default.
- **[R21]** Microsoft, _Access tokens in the Microsoft identity platform_, §Token ownership and §Validate tokens, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens>. "An access token request involves two parties: the client, who requests the token, and the resource (Web API) that accepts the token"; Web APIs "must only accept tokens containing one of their AppId URIs as the `aud` claim".
- **[R22]** Keycloak, _Configuring and using token exchange_, §Standard token exchange, accessed 2026-10-02. <https://www.keycloak.org/securing-apps/token-exchange>. "The `subject_token` sent to the token exchange endpoint must have the requester client set as an audience in the `aud` claim"; only confidential clients may send a token exchange request.
- **[R25]** Auth0, _Custom development_ for Organizations, accessed 2026-10-07. <https://auth0.com/docs/manage-users/organizations/custom-development>. "on callback, ensure that the organization returned in the ID token is the same one that was sent in the /authorize request by validating the org_id claim in the same way that other claims like exp and nonce are validated." The per-request choice on one client is `ADR-IAM-008`'s, with its Keycloak, Auth0 and Microsoft sources.
- **[R26]** Microsoft, _Configurable token lifetimes in the Microsoft identity platform_, accessed 2026-10-08. <https://learn.microsoft.com/en-us/entra/identity-platform/configurable-token-lifetimes>. "Adjusting the lifetime of an access token is a trade-off between improving system performance and increasing the amount of time that the client retains access after the user's account is disabled." The owner-and-administrator split this standard follows is `ADR-IAM-003` [R13], [R14], [R15].
