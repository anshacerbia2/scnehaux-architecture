---
doc_meta:
  id: STD-IAM-002
  title: Enterprise Token and Verification Profile
  owner: Identity Platform Team
  version: 1.0.0
  status: approved
  classification: restricted
  governed_by: PAD-PLT-001
  review_cycle_days: 180
  created_date: 2026-08-11
  last_reviewed: 2026-08-11
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

| Class | Meaning | Subject form |
| :-- | :-- | :-- |
| `internal` | A Scnehaux-owned protected resource inside the enterprise trust boundary | Shared issuer-scoped `sub` plus `principal_id` |
| `privileged` | An administrative or control-plane surface performing irreversible or cross-tenant operations | As `internal`, with elevated assurance claims |
| `workload` | A non-human service, job, connector, or governed agent identity | Workload subject; no human `principal_id` |
| `external` | A partner, customer-owned, or third-party relying party | Pairwise `sub`; no enterprise correlation identifier |

- Every access token MUST carry `aud`, and `aud` MUST name registered protected
  resources only.
- A protected resource MUST reject a token whose `aud` does not name it.
- A token MUST NOT be issued for more than one audience class.

### 3.2 Claim Set

| Claim | `internal` | `privileged` | `workload` | `external` |
| :-- | :-- | :-- | :-- | :-- |
| `iss` | MUST | MUST | MUST | MUST |
| `sub` | MUST | MUST | MUST | MUST, pairwise |
| `aud` | MUST | MUST | MUST | MUST |
| `iat`, `exp` | MUST | MUST | MUST | MUST |
| `principal_id` | MUST | MUST | MUST | MUST NOT |
| `subject_type` | MUST | MUST | MUST | MUST NOT |
| `tenant_id` | MUST | MUST | MUST when tenant-scoped | MUST NOT |
| `workspace_id` | MAY | MAY | MAY | MUST NOT |
| `membership_version` | MUST when `tenant_id` present | MUST | MUST when `tenant_id` present | MUST NOT |
| `tenant_security_version` | MUST when `tenant_id` present | MUST | MUST when `tenant_id` present | MUST NOT |
| `acr`, `auth_time` | MAY | MUST | MUST NOT | MAY |
| `workload_owner` | MUST NOT | MUST NOT | MUST | MUST NOT |

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
- A token MUST carry exactly one active Tenant context and at most one Workspace
  context. The set of Memberships held by a Principal MUST NOT be placed in a token,
  bounded or otherwise.
- Product permissions, entitlements, business roles, and quota state MUST NOT appear
  in any token.
- Personal data beyond what the audience requires MUST NOT appear in any token.
  Verified email and display name are released to `external` audiences only through an
  approved scope and consent.
- A claim not defined here or by an approved audience profile MUST NOT be added to a
  token.

### 3.3 Token-Lifetime Classes

Access token lifetime is derived from the revocation target declared for the risk
class, minus the propagation budget the platform owns:

```text
access_token_lifetime  =  revocation_target  −  propagation_budget
```

The propagation budget is the interval between accepting a revocation and applying it
at every enforcing mechanism. It is owned by the control plane and is currently
budgeted below 10 seconds, with 60 seconds reserved here as the planning figure so a
degraded propagation path does not silently invalidate the derived lifetime.

| Class | Revocation target | Access token lifetime | Applies to |
| :-- | :-- | :-- | :-- |
| `L0` | 5 minutes | 4 minutes | `privileged`; any surface performing irreversible, financial, or cross-tenant operations |
| `L1` | 10 minutes | 9 minutes | `internal` product APIs handling tenant-scoped business data |
| `L2` | 16 minutes | 15 minutes | `external` and partner profiles, bounded by the STD-IAM-001 §3.2 ceiling |
| `L3` | 10 minutes | 9 minutes | `workload`, unless a shorter class is declared by the workload profile |

- Every protected resource MUST be assigned exactly one lifetime class, recorded in
  its registration.
- A lifetime longer than the class permits MUST NOT be issued, and MUST NOT be
  configured per client.
- Increasing a lifetime class MUST carry the increase into the stated maximum
  enforcement delay of every revocation class that affects the audience.
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

1. Resolve the signing key by `kid` from approved discovery or JWKS material, and
   reject an unknown `kid` rather than fetching on demand from an unverified source.
2. Verify the signature using an algorithm permitted by the approved algorithm policy.
   An algorithm named only inside the token MUST NOT select the verification path.
3. Verify `iss` against the expected issuer for the environment.
4. Verify `aud` names this resource.
5. Verify token type and reject a token issued for a different purpose.
6. Verify `iat` and `exp` with a clock-skew allowance no greater than 60 seconds.
7. Reject an `internal`, `privileged`, or `workload` token whose `principal_id` is
   absent, and reject a `workload` token whose `workload_owner` is absent.
8. Compare `membership_version` and `tenant_security_version` against the local
   projection, and reject a token whose version is lower than the locally known
   version.
9. Enforce Product authorization locally. A valid signature is one input and is never
   the authorization decision.

- Introspection or an equivalent online check MAY be used where opaque-token or
  active-state semantics require it, and MUST NOT be placed on an ordinary request
  path where local validation plus bounded revocation mechanisms satisfy the
  requirement.
- Public verification material MUST remain published for at least the maximum lifetime
  of any artifact signed with that key, plus consumer cache and clock-skew margin.

### 3.6 External Profiles

- An `external` profile MUST be identified by audience and validated against its
  declared profile rather than against the internal rules.
- An `external` token MUST NOT carry `principal_id`, `tenant_id`, or any version
  claim.
- Pairwise subjects MUST be used where cross-relying-party correlation is not
  justified.
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

## 4. Exceptions

Deviation from this standard requires formal exception approval under GDC-000 with an
explicit threat model, compensating controls, a named owner, an expiry date, and the
revocation enforcement delay that results from the deviation.

A longer token lifetime is the most common request and is the least separable from
risk: granting it lengthens the enforcement delay of every revocation class affecting
that audience, so the resulting delay must be stated in the request rather than
discovered afterwards.

## 5. Enforcement Mechanism

- Token contract tests asserting the claim set per audience class, executed against
  the pinned identity kernel release.
- Reference verifier conformance tests covering each rule in §3.5, including negative
  cases for absent `principal_id`, wrong `aud`, unknown `kid`, and a stale version
  claim.
- Client registration validation rejecting a protected resource without an assigned
  lifetime class.
- Configuration assertion that no client carries a token lifetime exceeding its class.
- Connection registry tests proving a priority revocation closes matching long-lived
  connections within budget.
- Secret and token scanning across logs, traces, events, and error responses.
- Architecture fitness functions preventing permission, entitlement, or business role
  claims from entering a token.
