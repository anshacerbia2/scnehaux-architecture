---
doc_meta:
  id: ADR-IAM-005
  title: Account Recovery and Guessing Limits
  adr_type: foundational
  status: accepted
  created: 2026-10-04
  created_date: 2026-10-04
  created_by: Identity Platform Team
---

# ADR-IAM-005: Account Recovery and Guessing Limits

## 1. Title

Account Recovery and Guessing Limits.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-04 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

`ADR-IAM-004` requires `aal2` of every provider. A provider proves a second factor at each such sign-in:
a TOTP authenticator or a WebAuthn authenticator. Its §6 names the cost: "A provider whose second
factor is lost cannot administer until it is reset. That needs a recovery runbook before production."
Today there is no way back:

- **No self-service path.** A person who loses their only second factor cannot reach `aal2` again.
- **No assisted path.** The assurance floor refuses to remove or revoke a provider's last second factor
  (`TDD-identity-control-005` 2.6.0, result `assurance_floor`). So another provider cannot clear the
  lost factor either. That is right for a provider who is signed in, and a dead end for one who is
  locked out.
- **Guessing is not throttled.** The realm does not enable Keycloak's brute-force detection, which
  "is disabled by default" [R5]. A password, and the six-digit TOTP code that backs it at `aal2`, can
  be guessed without limit.

Three facts bound the choice:

- `STD-IAM-001 §3.1` requires credential policy to support "secure recovery", and `§3.8` requires
  recovery to "emit governed security/audit events".
- NIST SP 800-63B-4 defines account recovery and which methods suffice at each level [R1].
- The pinned kernel offers recovery codes as a supported, default-enabled feature (`RECOVERY_CODES`,
  `Type.DEFAULT` in Keycloak 26.7.5) [R4], and brute-force detection [R5]. Both are supported
  interfaces (`ADR-IAM-001 §5.7`).

## 4. Decision Drivers

- **At least one recognized recovery method.** "CSPs SHALL support one or more of these and MAY support
  an application-specific method (e.g., interaction with a CSP agent) to recover a subscriber account.
  The use of alternative methods SHALL be based on a risk analysis and documented by the CSP"
  (§4.2.1) [R1].
- **What suffices at `aal2`.** "One recovery code from the set (i.e., saved, issued, and recovery
  contacts) plus authentication with a single-factor authenticator that is bound to the subscriber
  account" (§4.2.2.2) [R1].
- **A bounded number of guesses.** "the verifier SHALL limit consecutive failed authentication
  attempts using a specific authenticator on a single subscriber account to no more than 100"
  (§3.2.2) [R2].
- **Supported kernel interfaces only.** `ADR-IAM-001 §5.7` permits no extension that this decision
  does not itself justify.

## 5. Decision

### 5.1 Saved Recovery Codes, Through the Kernel

The recovery method is NIST's _saved recovery codes_, implemented by the kernel's _Recovery
Authentication Codes_. They are the only one of NIST's four classes this platform can offer now:

- _Issued recovery codes_ and _recovery contacts_ need a channel that delivers a code, such as mail or
  text. The realm sends neither.
- _Repeated identity proofing_ needs an initial proofing. No Principal has been proofed.

The kernel generates 12 one-time codes and asks for them in order. A used code is removed, and the
next one is required at the next sign-in [R4].

### 5.2 Recovering at Level 2

The browser flow's level 2 accepts a recovery code as a third alternative, beside WebAuthn and TOTP.
Keycloak documents this arrangement: "If the user has configured both credential types, the credential
with the highest priority will be displayed by default, but the _Try Another Way_ option will appear"
[R4].

- **Why this meets `aal2` recovery.** The person has already given their password, a single-factor
  authenticator bound to the account. A code then completes NIST's second combination (§4.2.2.2) [R1].
- **A code is for recovery, not routine sign-in.** A recovery sign-in is evidenced as recovery, and
  the account page leads the person to bind a replacement factor.
- **Codes do not count toward the assurance floor.** The floor still counts only `otp` and `webauthn`.
  A provider who holds codes but no second factor has recovered nothing yet.
- **Required evidence.** The kernel records the sign-in. `STD-IAM-001 §3.8` requires it to reach
  governed evidence, with every other recovery event.

### 5.3 Issuing the Codes

- **Self-service.** A person sets up or replaces their codes from the account page. The Identity
  Control API authorizes it at the binding level `ADR-IAM-004` uses for any authenticator: `aal2` once
  the person holds a second factor, `aal1` before. The BFF then drives the kernel action
  `kc_action=CONFIGURE_RECOVERY_AUTHN_CODES`.
- **At first enrollment.** "At enrollment, a CSP that supports this recovery option SHOULD issue a
  recovery code to the subscriber" (§4.2.1.1) [R1]. The kernel's _Configure OTP_ action can ask for
  codes when it completes ("You can configure the `Configure OTP` required action to ask for recovery
  codes automatically by enabling _Add recovery codes_") [R4]. The realm enables that option.
- **Replacing them.** The kernel re-creates the set "at any moment" [R4]. NIST requires a
  notification when a replacement is issued (§4.2.1.1) [R1], and §5.7 records that gap.

### 5.4 Where the Kernel's Codes Fall Short of NIST, Accepted

The kernel's implementation departs from §4.2.1.1 in three ways. Changing any of them would need a
kernel extension, and this decision does not justify one.

| NIST §4.2.1.1 [R1]                                                                                                                  | The pinned kernel [R4][R6]                                                                            | Why it is accepted                                                                                                                                                                                     |
| :---------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "at least 64 bits from an approved random bit generator"                                                                            | 12 characters from a 34-character alphabet, about 61 bits. `CODE_LENGTH` is a constant, not a setting | Online guessing is bounded by §5.6 to at most 100 attempts. 2^61 is out of reach of that                                                                                                               |
| Stored "in hashed form using an approved one-way function, as described in Sec. 3.1.1.2", which asks for a salt and a cost factor   | SHA-512, unsalted                                                                                     | An offline attack needs the kernel's database. That database already holds every TOTP secret in a form the verifier can read, because TOTP is a shared-secret algorithm. The codes add no new exposure |
| "Following the use of a saved recovery code, the CSP SHALL invalidate that recovery code and SHALL issue a new saved recovery code" | The used code is removed. A new set is required only once all 12 are used                             | The account page shows that a code was used, and offers a new set                                                                                                                                      |

**Reopened** if a Keycloak release makes the code length a setting, or before production if the review
declines any of the three.

### 5.5 Assisted Recovery, for a Person Without Codes

A person who has lost their second factor and their codes is recovered by another provider. This is
NIST's application-specific method "(e.g., interaction with a CSP agent)", and §4.2.1 requires its risk
analysis to be documented [R1]. This section is that analysis.

**The procedure.**

1. **Verify the person outside the platform.** A provider other than the subject verifies them in
   person or on a live call, following the recovery runbook. The service already refuses any provider
   acting on their own Principal.
2. **Suspend the Principal.** Suspension ends every session (`TDD-identity-control-005` slice 2).
3. **Revoke the lost factors.** The assurance floor applies only to a Principal who can sign in. A
   suspended one cannot, so the floor does not refuse this revocation.
4. **Restore, then enroll.** The provider restores the Principal while still in contact with them. The
   person signs in at once, and the `aal2` sign-in enrolls a new TOTP authenticator
   (`ADR-IAM-004 §5.4`) and new codes (§5.3).

Each step is an evidenced command and carries the provider's reason.

**The risk.** Between the restore and the person's enrollment, anyone who holds the password can
enroll a factor of their own. This is the bootstrap risk `ADR-IAM-004 §6` already accepts, and three
things narrow it:

- the restore happens while the provider is in contact with the person;
- enrollment is a kernel event, and it is alerted on (`TDD-identity-control-005` §Operational Notes);
- an unexpected factor is revoked by the same procedure.

### 5.6 Guessing Limits

The realm enables brute-force detection, in Keycloak's mode _Lockout permanently after temporary
lockout_ ("Locks user temporarily for specified number of times and then locks user permanently")
[R5].

- **What it covers.** "{project_name} applies it only to password, OTP and recovery codes" [R5].
  WebAuthn needs no counter: an assertion is a signature, and there is nothing to guess.
- **The bound.** A permanent lockout comes no later than the 100th consecutive failure, as §3.2.2
  requires [R2]. Temporary lockouts, with a growing wait, come first. Each one slows an attacker
  without ending the account. The values are the realm's, stated in `TDD-identity-kernel-001`.
- **What a locked person sees.** "the default `Invalid username or password` error message … to
  ensure the attacker is unaware the account is disabled" [R5].
- **Getting out of a permanent lockout.** It is assisted recovery (§5.5). It is not an automatic
  unlock, because a permanent lockout is evidence of an attack.

### 5.7 Notification, Still a Gap

"In all cases, account recovery SHALL cause a notification to be sent to the subscriber or their
designee" (§4.2.3) [R1].

- **Not met yet.** The realm sends no mail, as `ADR-IAM-004 §5.5` already records for binding.
- **Production gate.** A notification channel is a prerequisite for production. It is the same
  channel that would make issued recovery codes possible.
- **Decided (2026-10-06).** `ADR-IAM-007` covers recovery, a used recovery code, issued or replaced
  codes, and assisted recovery. Identity Control requests each notification from the Notification
  Platform for every notification address. It remains a production gate until it is built.

## 6. Consequences

### Positive

- A provider who loses a second factor has a way back, by themselves with codes or through another
  provider without them.
- Guessing a password, a TOTP code or a recovery code is bounded for the first time.
- The kernel does all of it with supported features. No extension is added.

### Negative

- **A lockout can be used against a provider.** Anyone who knows a provider's username can lock that
  account with failed passwords. NIST chose its limit "to balance the likelihood of a correct guess …
  versus the potential need for account recovery when the limit is exceeded" [R2]. Recovering from a
  permanent lockout needs another provider, so the platform needs at least two active providers.
- **The codes fall short of NIST in three ways** (§5.4). They are accepted here, and they are open
  again before production.
- **Assisted recovery depends on people.** Its controls are a runbook, a second person and evidence.
  A careless verification is the weak point, as it is for any help desk.

### Operational

- The realm's flow, the recovery-code step, the _Configure OTP_ option and the brute-force settings
  are part of the applied realm definition. identity-kernel's compat suite proves:
  - recovery at level 2;
  - the lockout bound;
  - that a person with neither factor is still taken to TOTP enrollment.
- Scripts that enroll TOTP on a development server (`ADR-IAM-004 §5.5`) answer the recovery-code page
  that now follows enrollment. They keep the codes with the TOTP secret and never print them.

## 7. Compliance Impact

### Related Standards

- `STD-IAM-001 §3.1`: "secure recovery" is implemented by this decision.
- `STD-IAM-001 §3.8`: recovery and factor changes emit evidence (§5.2, §5.5).
- [ADR-IAM-004](ADR-IAM-004-authentication-assurance-and-step-up.md) §6: closes the recovery item it
  left open. Its notification gap remains, and §5.7 here shares it.
- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.7: supported kernel interfaces only.
- `TDD-identity-kernel-001` §Authentication Levels, `TDD-identity-control-005` §Enrollment and the
  Assurance Floor, and `TDD-identity-experience-002` change to implement it.

### Compliance Status

- **Meets NIST SP 800-63B-4 §3.2.2** once the realm enables §5.6.
- **Meets §4.2.1 and §4.2.2.2** with the three deviations in §5.4.
- **Does not meet §4.2.3**, for lack of notification (§5.7).

### Required Waivers

None before production. The deviations in §5.4 and the gap in §5.7 are reviewed at the production gate.

## 8. Alternatives Considered

### Alternative A — Assisted Recovery Only, No Codes

**Benefits:** no secret for the person to keep, and nothing in the kernel short of NIST.

**Rejected because:** §4.2.1 requires one of NIST's four classes, and assisted recovery is not one of
them [R1]. Every recovery would also need a second provider at a moment's notice.

### Alternative B — Issued Recovery Codes or Recovery Contacts, by Mail or Text

**Benefits:** nothing for the person to keep. NIST recognizes both classes [R1].

**Rejected for now because:** the realm has no delivery channel. When one exists for notification
(§5.7), issued codes can be decided again.

### Alternative C — A Kernel Extension for Longer, Salted Codes

**Benefits:** meets §4.2.1.1 in full.

**Rejected because:** an extension that owns a credential type is the most expensive thing to carry
across kernel upgrades (`ADR-IAM-001 §5.7`). The gap it closes is about 3 bits and a salt, and §5.4
bounds both.

### Alternative D — Exempt No One From the Assurance Floor; Recover by Deleting the User

**Benefits:** the floor stays absolute.

**Rejected because:** deleting a user ends the Principal's mapping and its history in the kernel. The
floor exists to keep a signed-in provider at two factors, and a suspended Principal is not signed in.

### Alternative E — A Second Authenticator as the Only Backup

**Benefits:** nothing new to build. "CSPs SHALL permit the binding of multiple authenticators"
(§4.1.2.1) [R1], and the account page already offers a security key beside an authenticator app.

**Not sufficient on its own because:** it is avoidance, not recovery. The account page still suggests
a second authenticator, and the codes cover a person who did not take that advice.

## 9. References

### Normative

- **[R1]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator
  Management_, August 2025, <https://pages.nist.gov/800-63-4/sp800-63b.html>, accessed 2026-10-04.
  - §4.2: "Account recovery is when a subscriber recovers from losing control of the authenticators
    that are needed to authenticate at a desired AAL."
  - §4.2.1: "CSPs SHALL support one or more of these and MAY support an application-specific method
    (e.g., interaction with a CSP agent) to recover a subscriber account. The use of alternative methods
    SHALL be based on a risk analysis and documented by the CSP."
  - §4.2.1.1: "At enrollment, a CSP that supports this recovery option SHOULD issue a recovery code to
    the subscriber. The recovery code SHALL include at least 64 bits from an approved random bit
    generator"; "Saved recovery codes SHALL be stored in the subscriber account in hashed form using an
    approved one-way function, as described in Sec. 3.1.1.2. Following the use of a saved recovery
    code, the CSP SHALL invalidate that recovery code and SHALL issue a new saved recovery code to the
    subscriber"; "The issuance of a replacement recovery code SHALL result in an account recovery
    notification."
  - §4.2.2.2: "To recover an account that can authenticate at a maximum of AAL2, the CSP SHALL require
    the subscriber to complete one of the following: … One recovery code from the set (i.e., saved,
    issued, and recovery contacts) plus authentication with a single-factor authenticator that is bound
    to the subscriber account."
  - §4.2.3: "In all cases, account recovery SHALL cause a notification to be sent to the subscriber or
    their designee."
  - §4.1.2.1: "CSPs SHALL permit the binding of multiple authenticators to a subscriber account."
- **[R2]** NIST SP 800-63B-4, §3.2.2 Rate Limiting (Throttling), same source: "the verifier SHALL
  limit consecutive failed authentication attempts using a specific authenticator on a single
  subscriber account to no more than 100 by disabling that authenticator"; "The limit of 100 was chosen
  to balance the likelihood of a correct guess (e.g., 100 attempts against a six-digit decimal OTP
  authenticator output) versus the potential need for account recovery when the limit is exceeded."
- **[R3]** NIST SP 800-63B-4, §3.1.1.2, same source: passwords are "salted and hashed using a suitable
  password hashing scheme. Password hashing schemes take a password, a salt, and a cost factor as
  inputs".

### Kernel

- **[R4]** Keycloak 26.7.5, _Server Administration Guide_, Recovery Codes, source
  `docs/documentation/server_admin/topics/authentication/recovery-codes.adoc` at tag 26.7.5, accessed
  2026-10-04:
  - "The Recovery Codes are a number of sequential one-time passwords (currently 12) auto-generated by
    {project_name}"; "When the current code is introduced by the user, it is removed and the next code
    will be required for the next login."
  - "You can configure the `Configure OTP` required action to ask for recovery codes automatically by
    enabling _Add recovery codes_."
  - "If the user has configured both credential types, the credential with the highest priority will be
    displayed by default, but the _Try Another Way_ option will appear."
  - "The Recovery Codes can be re-created at any moment."

  The feature's status is in `common/src/main/java/org/keycloak/common/Profile.java`:
  `RECOVERY_CODES("Recovery codes", Type.DEFAULT)`.

- **[R5]** Keycloak 26.7.5, _Server Administration Guide_, Brute force attacks, source
  `docs/documentation/server_admin/topics/threat/brute-force.adoc` at tag 26.7.5:
  - "{project_name} applies it only to password, OTP and recovery codes."
  - "Brute force detection is disabled by default."
  - _Lockout permanently after temporary lockout_: "Locks user temporarily for specified number of times
    and then locks user permanently."
  - A locked user sees "the default `Invalid username or password` error message … to ensure the
    attacker is unaware the account is disabled."
- **[R6]** Keycloak 26.7.5, `server-spi/src/main/java/org/keycloak/models/utils/RecoveryAuthnCodesUtils.java`:
  - `QUANTITY_OF_CODES_TO_GENERATE = 12`;
  - `CODE_LENGTH = 12`;
  - `UPPERNUM = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"` (34 characters; 12 × log2 34 ≈ 61 bits);
  - `NOM_ALGORITHM_TO_HASH = JavaAlgorithm.SHA512`.

  `RecoveryAuthnCodesFormAuthenticator` adds `CONFIGURE_RECOVERY_AUTHN_CODES` once every code is used.
