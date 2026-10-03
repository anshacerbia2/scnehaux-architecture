---
doc_meta:
  id: ADR-IAM-004
  title: Authentication Assurance Levels and Step-Up
  adr_type: foundational
  status: accepted
  created: 2026-10-03
  created_date: 2026-10-03
  created_by: Identity Platform Team
---

# ADR-IAM-004: Authentication Assurance Levels and Step-Up

## 1. Title

Authentication Assurance Levels and Step-Up.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-03 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

Every token a person holds says how they authenticated, in `acr`, and when, in `auth_time`
(`STD-IAM-002 §3.2`). Today the realm maps no level of authentication. Every sign-in is a password,
and every `acr` is the kernel's default `1`.

A provider therefore suspends a Principal, revokes an authenticator or reads another person's
sessions with a password alone. The Identity Control Service's step-up asks only for a recent
sign-in (`TDD-identity-control-005` §Step-Up). That document states the gap: "Requiring MFA for these
commands waits for identity-kernel to define levels and a step-up flow."

Three facts bound the choice:

- `STD-IAM-001 §3.1` already requires credential policy to "support … MFA, WebAuthn/passkeys, and
  step-up authentication according to assurance requirements". Nothing has stated the requirements.
- The pinned kernel maps an `acr` value to a numeric Level of Authentication (LoA). It selects the
  authentication a request needs with the _Conditional - Level Of Authentication_ step of a browser
  flow [R4]. This is a supported interface (`ADR-IAM-001 §5.7`).
- One BFF holds the session for the Admin Portal, the Developer Console and the account security
  application (`TDD-identity-experience-001` 1.9.1). A rule attached to the BFF's client therefore
  applies to all three.

## 4. Decision Drivers

- **Multi-factor authentication for privileged access.** "Implement multi-factor authentication for
  access to privileged accounts" (NIST SP 800-53 IA-2(1)) [R1].
- **Levels with a meaning outside this platform.** NIST SP 800-63B-4 defines the levels: "AAL2
  provides high confidence … Proof of possession and control of two distinct authentication factors
  through the use of secure authentication protocols is required" [R2].
- **The resource decides, and the browser cannot lower it.** A resource names the level it needs in
  an RFC 9470 challenge, and the client asks the kernel for exactly that [R3].
- **Supported kernel interfaces only.** `ADR-IAM-001 §5.7`.

## 5. Decision

### 5.1 The Levels and Their Names

| `acr` value | LoA | Means                                                | Kernel authentication                                                 |
| :---------- | :-- | :--------------------------------------------------- | :-------------------------------------------------------------------- |
| `aal1`      | 1   | One factor (NIST AAL1)                               | The password                                                          |
| `aal2`      | 2   | Two distinct factors (NIST AAL2) [R2]                | The password, then a one-time code (TOTP) or a WebAuthn authenticator |
| `phr`       | 3   | Phishing-resistant: reserved, and not configured yet | A passkey, once a flow admits one                                     |

- **Names.** `aal1` and `aal2` take NIST's names. `phr` is OpenID's EAP ACR value for "an
  authentication mechanism where a party potentially under the control of the Relying Party cannot
  gain sufficient information to be able to successfully authenticate … as if that party were the
  End User" [R5].
- **The map lives in the realm.** The realm maps each name to its LoA, as Keycloak advises: "a best
  practice is to stick to realm mappings" [R4].
- **Ordering.** A resource compares levels by this order. Any other `acr`, including the kernel's
  unmapped `0` and `1`, is below `aal1`.

### 5.2 Where Each Level Is Required

| Access                                                                         | Level  | Freshness                                                      |
| :----------------------------------------------------------------------------- | :----- | :------------------------------------------------------------- |
| Every `providerOnly` route of the Identity Control Service: reads and commands | `aal2` | Commands: `auth_time` within the service's step-up age, as now |
| A person's own sessions and authenticators (route class `self`)                | `aal1` | None                                                           |
| Removing one's own authenticator                                               | `aal2` | Within the step-up age                                         |
| Registration owner routes (`ADR-IAM-003`)                                      | `aal1` | As now                                                         |

- **Providers.** A provider holds a privileged account, which is IA-2(1) [R1], so every provider route
  needs `aal2`, reads included. A provider's read discloses another person's security state
  (`TDD-identity-control-005` §Read Authorization and Disclosure).
- **Removing an authenticator.** This changes how the account is protected
  (`TDD-identity-experience-002` §Technical Context). It needs the stronger level the account offers.

### 5.3 How the Level Is Reached

- **The challenge.** A resource answers an insufficient token as RFC 9470 does: `401` with
  `error="insufficient_user_authentication"`, `acr_values="aal2"` and, where freshness is required,
  `max_age` [R3].
- **The client asks for exactly that.** The BFF passes `acr_values` and `max_age` into the
  authorization request, and refuses a callback whose ID token shows a lower `acr`.
- **The Admin Portal asks up front.** Its sign-in already requests `aal2`, so a provider meets the
  challenge once per sign-in rather than at the first page. A sign-in from the account application
  requests nothing more than `aal1`.
- **The kernel decides only how.** Its browser flow authenticates the person to the requested LoA.
  The LoA 2 step reuses an earlier LoA 2 sign-in for as long as the service's step-up age, and no
  longer.

### 5.4 The First Second Factor

A person asked for `aal2` who has no second factor enrolls a TOTP authenticator during that sign-in,
after the password, through the kernel's own configuration page. This is the only path in the slice
that enrolls one. `TDD-identity-control-005` slice 4 brings enrollment through the Identity Control
API.

### 5.5 A Development Server's Operator Automation

On a development server, the agent that operates the server acts as its bootstrap provider. That
agent needs `aal2` tokens, and a person's TOTP code, valid for 30 seconds, cannot reasonably be
relayed to it. The provider therefore holds a second TOTP authenticator on that server:

- **It is bound at `aal2`.** The account already has the person's own TOTP, and NIST requires that
  "binding … requires authentication at either the maximum AAL currently available in the
  subscriber account or the maximum AAL at which the new authenticator will be used, whichever is
  lower" [R6]. Binding a second authenticator is permitted: "CSPs SHALL permit the binding of
  multiple authenticators to a subscriber account" [R6].
  - The enrollment script signs in at `aal2` with one code the person reads from their own
    authenticator, once.
  - It then asks the kernel to set up another TOTP, through the supported application-initiated
    action `kc_action=CONFIGURE_TOTP`.
- **Its secret never leaves the server.** It is written to the deployment's `keys/`, mode 0600, and
  is never printed. The scripts compute codes from it.
- **Only on a development server.** On a development server the server holds both factors of that
  account, the password the scripts already read and this TOTP, so for that account the two factors
  are one place. That is acceptable only where nothing real is protected. A production estate's
  operators authenticate as themselves, and automation acts as a workload.
- **The person can end it.** Revoking the server's authenticator through containment (slice 2) ends
  it without touching the person's own.

The NIST requirement to notify the subscriber of a new authenticator "via a mechanism independent of
the transaction binding the new authenticator" [R6] is not met yet: the realm sends no mail. It is a
gap to close before production, together with recovery.

## 6. Consequences

### Positive

- Every provider action, and every privileged read, is behind two factors, as IA-2(1) requires.
- `acr` carries a level any reader can look up, instead of the kernel's default `1`.
- The step-up already built for freshness carries the level too. No second mechanism is added.

### Negative

- **Bootstrap enrollment can be abused.** Whoever holds a provider's password before the provider
  enrolls a second factor can enroll their own. Until providers are enrolled under supervision, this
  is detected rather than prevented:
  - enrollment is a kernel event;
  - `TDD-identity-control-005` §Operational Notes alerts on authenticator changes;
  - a provider's unexpected second factor is revoked by another provider (slice 2).
- **Owners are not yet held to `aal2`.** Registration owners and application developers stay at
  `aal1`. An owner of a production client can rotate its keys with a password alone. Raising them is a
  separate decision, and it costs every application team an enrollment.
- **Everyone else stays on a password.** MFA for non-privileged accounts (IA-2(2)) is not decided here.
- **One more failure mode at sign-in.** A provider whose second factor is lost cannot administer until
  it is reset. That needs a recovery runbook before production.

### Operational

- The realm's browser flow, its LoA map, and the OTP and WebAuthn steps are part of the applied realm
  definition. identity-kernel's compat suite asserts the levels on every upgrade.
- Enrollment of a provider's first second factor is reported.

## 7. Compliance Impact

### Related Standards

- `STD-IAM-001 §3.1`: gains the rule that privileged access requires `aal2`.
- `STD-IAM-002 §3.2`: gains the `acr` values and their order.
- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.7: supported kernel interfaces only.
- `TDD-identity-control-005` §Step-Up, `TDD-identity-experience-001` §Step-Up, and identity-kernel's
  realm design change to implement it.

### Compliance Status

Compliant once the kernel's realm and the two services implement §5. Until then, provider access does
not meet IA-2(1), as before this decision.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Keep the Kernel's Numeric `acr`

**Benefits:** no map. `acr` would be `1` or `2`.

**Rejected because:** a number means nothing to a reader outside this realm. A named level states
what was proven.

### Alternative B — Require `aal2` at Every Sign-In, for Everyone

**Benefits:** IA-2(1) and IA-2(2) at once [R1]; one rule.

**Rejected for now because:** it enrolls every person before any of them can read their own
sessions. It is a separate decision about non-privileged accounts, not a prerequisite for privileged
ones.

### Alternative C — A Minimum `acr` on the BFF's Client

**Benefits:** the kernel enforces it at every sign-in through the BFF, with no step-up handling.

**Rejected because:** one BFF serves the account application too, so every person would need
`aal2`, which is Alternative B by another route. Where the level is needed is the resource's
decision, which RFC 9470 places at the resource [R3].

### Alternative D — Step-Up for Commands Only, Reads at `aal1`

**Benefits:** a provider browsing is not interrupted.

**Rejected because:** IA-2(1) is about access to the privileged account, not only its writes. A
provider's read discloses another person's sessions and authenticators, which an attacker preparing
a takeover wants.

## 9. References

### Normative

- **[R1]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and
  Organizations_, from NIST's OSCAL catalog
  <https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>,
  accessed 2026-10-03. IA-2(1) "Implement multi-factor authentication for access to privileged
  accounts"; IA-2(2) "Implement multi-factor authentication for access to non-privileged accounts".
- **[R2]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator
  Management_, August 2025, <https://pages.nist.gov/800-63-4/sp800-63b.html>, §2.1–§2.2. "AAL1
  provides basic confidence that the claimant controls an authenticator that is bound to the
  subscriber account"; "AAL2 provides high confidence … Proof of possession and control of two
  distinct authentication factors through the use of secure authentication protocols is required."
- **[R3]** IETF RFC 9470, _OAuth 2.0 Step Up Authentication Challenge Protocol_, September 2023,
  <https://www.rfc-editor.org/rfc/rfc9470>. §3 `insufficient_user_authentication`, `acr_values`,
  `max_age`; §4 the client uses them in its authorization request.

- **[R6]** NIST SP 800-63B-4, §4.1.2.1 Binding an Additional Authenticator,
  <https://pages.nist.gov/800-63-4/sp800-63b.html>, accessed 2026-10-03. "CSPs SHALL permit the
  binding of multiple authenticators to a subscriber account. When any new authenticator is bound to
  a subscriber account, the CSP SHALL ensure that the process requires authentication at either the
  maximum AAL currently available in the subscriber account or the maximum AAL at which the new
  authenticator will be used, whichever is lower"; "When an authenticator is added, the CSP SHALL
  notify the subscriber via a mechanism independent of the transaction binding the new
  authenticator".

### Informative

- **[R4]** Keycloak, _Server Administration Guide_, ACR to Level of Authentication (LoA) Mapping and
  Creating a browser login flow with step-up mechanism, accessed 2026-10-03,
  <https://www.keycloak.org/docs/latest/server_admin/index.html>. "The ACR can be any value, whereas
  the LoA must be numeric"; "a best practice is to stick to realm mappings"; the flow's
  _Conditional - Level Of Authentication_ step with a Max Age per level.
- **[R5]** OpenID Foundation, _OpenID Connect Extended Authentication Profile (EAP) ACR Values 1.0_,
  Final, June 2025, <https://openid.net/specs/openid-connect-eap-acr-values-1_0.html>. `phr` and
  `phrh`.
