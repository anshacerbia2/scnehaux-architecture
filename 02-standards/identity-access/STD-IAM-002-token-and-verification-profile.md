---
doc_meta:
  id: STD-IAM-002
  title: Token and Verification Profile
  owner: Enterprise Security Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  governed_by: [EAD-006]
  review_cycle_days: 180
  created_date: 2026-08-18
  last_reviewed: 2026-08-18
---

# Token and Verification Profile (STD-IAM-002)

---

## 1. Objective & Scope

This standard fixes the contract every Scnehaux access token carries and every protected resource verifies: which audience a token is issued for, which claims that audience receives, how long the token remains valid, which algorithm signs it, and what a verifier must check before it acts.

It applies to every artifact issued by the Identity Platform and to every protected resource that accepts one, internal and external alike.

**In scope:** the audience taxonomy, the per-audience claim profile, the signing algorithm profile, the token lifetime classes, the verification obligations of a relying party, and the external token profile.

**Out of scope:** credential material and authentication ceremonies, which belong to the identity kernel; signing key custody and rotation mechanics, which belong to `STD-IAM-001`; and business authorization, which belongs to the domain that owns the resource. A valid token is an authenticated identity and never an authorization decision.

---

## 2. Design Principles

**Local verification, no callback.** A protected resource verifies a token from its own cached signing material and the claims in front of it. A verifier that calls the issuer per request converts every domain into a synchronous dependent of Identity, which `EAD-006 §8` exists to prevent.

**One audience, one claim set.** A token carries the claims its audience is entitled to and no others. A claim present for one audience and absent for another is a boundary; a claim present everywhere is ambient authority.

**The lifetime is the enforcement bound.** Revocation propagates asynchronously, so the interval during which a revoked authorization is still honoured is dominated by the remaining lifetime of an already-issued token. The lifetime is therefore a security parameter and not a performance knob.

**One signature algorithm.** Every additional accepted algorithm adds a branch to every verifier, and algorithm confusion is a defect class that lives in those branches. The profile names one baseline and treats anything else as a recorded, expiring exception.

---

## 3. Normative Rules

### 3.1 Audience Taxonomy

Every token is issued for exactly one audience class. The class is fixed at client registration and MUST NOT be inferred at issue time.

| Class | Issued to | Trust position |
| :-- | :-- | :-- |
| `internal` | A Scnehaux service or product API inside the enterprise trust boundary | Full enterprise claim set |
| `privileged` | An administrative or investigative surface | Full enterprise claim set, tightest lifetime |
| `workload` | A service, job, connector, or governed agent authenticating with its own credential | Enterprise claim set plus accountability claims |
| `external` | A third-party relying party outside the enterprise trust boundary | Protocol claims only |

A registration MUST attach exactly one managed client scope corresponding to its audience class. A token carrying the claim set of two classes MUST be rejected by the verifier, because a claim set is the only evidence a verifier has of which boundary the token crossed.

### 3.2 Claim Profile

#### 3.2.1 Claims by Audience Class

| Claim | `internal` | `privileged` | `workload` | `external` |
| :-- | :-- | :-- | :-- | :-- |
| `iss` | MUST | MUST | MUST | MUST |
| `sub` | MUST | MUST | MUST | MUST |
| `aud` | MUST | MUST | MUST | MUST |
| `iat`, `exp` | MUST | MUST | MUST | MUST |
| `principal_id` | MUST | MUST | MUST | MUST NOT |
| `subject_type` | MUST | MUST | MUST | MUST NOT |
| `tenant_id` | MUST | MUST | MUST | MUST NOT |
| `membership_version` | MUST | MUST | MUST | MUST NOT |
| `workload_owner` | MUST NOT | MUST NOT | MUST | MUST NOT |
| `act` | MUST NOT | MUST NOT | MAY | MUST NOT |

`sub` is the issuer-scoped protocol subject and MUST NOT be used as an enterprise reference. `principal_id` is the canonical enterprise identifier defined by `TDD-identity-control-001`. The two are distinct claims with distinct lifetimes, and a domain persisting `sub` as a foreign key has bound its data to a protocol detail.

`act` names the human a governed agent is acting for. The agent MUST be the subject and the human MUST be in `act`, never the reverse: a token whose `principal_id` is the human's makes the agent invisible in every downstream audit record.

#### 3.2.2 Signing Algorithm

- **Baseline**: every token MUST be signed with **`PS256`** (RSASSA-PSS with SHA-256).
- **RSA key size**: signing keys MUST use a modulus of at least **3072 bits**.
- **Prohibited**: `none`, every symmetric algorithm including the `HS*` family, and every algorithm absent from this section. A verifier MUST reject a token whose `alg` header is not in the allowlist, and MUST determine the expected algorithm from its own configuration rather than from the token.
- **Exception**: `RS256` MAY be accepted for an `external` registration when the relying party cannot verify `PS256`. The exception MUST record a named accountable owner, a reason, and an expiry date, and MUST be refused without all three.

`PS256` rather than `RS256` because PKCS#1 v1.5 signature padding carries no security proof and the Financial-grade API profile prohibits it. `PS256` rather than a dual `ES256`/`RS256` profile because a second algorithm doubles key custody and introduces the algorithm-confusion branch in every verifier, and the header-size saving does not apply: service-to-service authentication inside the runtime is mutual TLS with workload identity under `EAD-006 §5.4`, not a bearer token.

#### 3.2.3 Context Cardinality

A token MUST carry exactly one Tenant context. Switching the active Tenant MUST issue a new token rather than extend the existing one, and MUST NOT invalidate the previously issued token, whose remaining lifetime is bounded by its lifetime class.

A token carrying two Tenant contexts is prohibited. A verifier cannot apply a tenant predicate to a token that names two tenants, and the failure is silent because both values look valid.

### 3.3 Lifetime Classes

Every protected resource MUST declare exactly one lifetime class, recorded in its registration. A resource without a class MUST NOT be registered: the class is the term that bounds revocation enforcement for every consumer of that resource, and a resource without one has no stated enforcement delay.

| Class | Maximum access token lifetime | Applies to |
| :-- | :-- | :-- |
| `L0` | 4 minutes | `privileged` audiences |
| `L1` | 9 minutes | `workload` audiences |
| `L2` | 15 minutes | `internal` audiences |
| `L3` | 15 minutes | `external` audiences |

The classes are ordered by enforcement tightness. `L0` derives from a five-minute revocation target for administrative surfaces, less the propagation budget. `L2` is the ceiling `STD-IAM-001` sets on any access token and is the general internal default.

`L2` and `L3` share a maximum lifetime and remain separate classes because a lifetime class binds a claim profile as well as a duration, and the `external` profile in §3.6 differs from the `internal` one. Assigning an external resource to `L2` would attach the internal claim set to a party outside the trust boundary.

Refresh tokens MUST NOT be issued to a `public` client profile or to a `workload` registration. A workload re-authenticates with its own credential rather than continuing a session, which is what makes §3.3 the whole enforcement bound for a workload rather than one term in it.

### 3.4 Enforcement Interval

The interval during which a revoked authorization can still be honoured is the sum of the propagation budget and the remaining lifetime of an already-issued token. Neither term alone bounds it, and no single system owns it.

Every system publishing a revocation-enforcement figure MUST present it as that sum and MUST name the lifetime class it assumed. A figure quoting propagation alone understates enforcement by up to the full lifetime of the class.

### 3.5 Verification Obligations

A protected resource MUST perform every check below before acting on a token. Each is stated because omitting it produces a token that verifies and should not.

1. **Signature** against material retrieved from the issuer's published JWKS endpoint, resolved by `kid`.
2. **Algorithm** matches the verifier's configured expectation from §3.2.2.
3. **Issuer** matches the configured issuer exactly. A prefix or suffix match is prohibited.
4. **Audience** contains this resource's registered identifier.
5. **Expiry and issued-at**, with a clock skew allowance of at most 60 seconds.
6. **`principal_id` is present** for every `internal`, `privileged`, and `workload` audience token. Its absence MUST cause rejection. This invariant prevents a partially migrated estate in which some domains key on `sub` and others on `principal_id`, which is worse than either choice applied consistently.
7. **Claim set matches the audience class** declared for this resource, per §3.2.1.

A verifier MUST NOT fetch signing material from a location named inside the token. The `jku`, `x5u`, `jwk`, and `x5c` header parameters MUST be ignored: honouring them lets the presenter of a token nominate the key that validates it, which removes the signature as a control entirely.

A verifier MUST resolve an unknown `kid` by refetching JWKS under a rate limit, and MUST reject the token while the `kid` remains unknown. Failing open on an unknown `kid` converts a key-distribution problem into an authentication bypass.

The issuer MUST publish verification material for at least the maximum lifetime of any artifact signed by that key, plus the maximum permitted clock skew and the maximum JWKS cache lifetime. Retiring a key sooner rejects tokens that have not expired.

### 3.6 External Token Profile

A token issued to an `external` audience:

- MUST NOT carry `principal_id`, `subject_type`, `tenant_id`, `membership_version`, or `workload_owner`.
- MUST use a pairwise `sub` per relying party unless cross-relying-party correlation is justified and recorded.
- MUST be identified by audience rather than by inspecting which claims are absent.

`principal_id` is deliberately stable and enterprise-wide, which makes it a correlation key across every domain. Disclosing it to a third party hands out that correlation capability permanently, because the identifier cannot be rotated without an enterprise-wide referential migration.

A protected resource that accepts both internal and external audiences MUST apply the profile matching the presented audience and MUST NOT fall back to the internal profile when a claim is missing.

---

## 4. Exceptions

`RS256` for an `external` registration, bounded as stated in §3.2.2: a named accountable owner, a recorded reason, and an expiry date. The registration record is refused without all three, and the algorithm reverts to the §3.2.2 baseline when the expiry passes.

No other deviation exists. In particular there is no exception permitting a symmetric algorithm, an `alg` of `none`, a token carrying two audience claim sets, a token carrying two Tenant contexts, or a lifetime exceeding the class ceiling in §3.3.

---

## 5. Enforcement Mechanism

1. **Registration constraints**: the client registry rejects a protected resource without a lifetime class, an audience class outside §3.1, an algorithm outside §3.2.2, and an `RS256` record lacking an owner, reason, or future expiry. Each rule is expressed as a database constraint as well as application validation, so a migration or a repair script cannot create the one registration whose profile nobody chose.
2. **Realm contract tests**: the identity kernel asserts on every candidate release that a token of each audience class carries exactly its §3.2.1 profile, that an external token carries none of the enterprise claims, and that the baseline algorithm is issued and verified.
3. **Verifier conformance suite**: the reference verifier is tested against tokens that must be rejected — wrong issuer, wrong audience, expired, absent `principal_id` on an internal audience, `alg` of `none`, a symmetric algorithm, an unknown `kid`, and a token nominating its own key through `jku` or `jwk`. A verifier implementation that accepts any of them fails the suite.
4. **Upgrade compatibility suite**: a candidate identity kernel release that changes the issuer form, drops a claim from a covered surface, or cannot issue the baseline algorithm fails before promotion.
