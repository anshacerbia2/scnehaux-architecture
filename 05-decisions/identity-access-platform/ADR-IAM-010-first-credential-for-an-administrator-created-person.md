---
doc_meta:
  id: ADR-IAM-010
  title: A Person Created by a Provider Receives a Temporary Password, Shown Once
  adr_type: foundational
  status: accepted
  created: 2026-10-19
  created_date: 2026-10-19
  created_by: Identity Platform Team
  governed_by: [PAD-PLT-001]
---

# ADR-IAM-010: A Person Created by a Provider Receives a Temporary Password, Shown Once

## 1. Title

A Person Created by a Provider Receives a Temporary Password, Shown Once.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                       |
| ---------- | -------- | ------------ | ------------------------- | ------------------------------ |
| 2026-10-19 | proposed | foundational | Architecture Review Board | Enterprise Architect — pending |
| 2026-10-20 | accepted | foundational | Architecture Review Board | Enterprise Architect           |

## 3. Context

A provider creates a person in the Admin Portal. That person can never sign in.

- **The account is created without a credential.** `POST /v1/principals` creates the kernel user
  with the required action `UPDATE_PASSWORD` outstanding (`TDD-identity-control-001` 1.20.0,
  §The Bootstrap Ceremony, and identity-control's ROADMAP). The ceremony and the ordinary path share
  this, so that "the first human interaction establishes the credential".
- **A required action runs only after a sign-in.** Keycloak: "These actions are required after the
  user provides credentials" [R9]. The person has no credential to provide.
- **Nothing else gives one.**
  - The realm sets `resetPasswordAllowed` false (`realm/scnehaux.json`), so the login page offers
    no reset. Recovery is a recovery code or assisted recovery (`ADR-IAM-005`).
  - The kernel sends no mail (`ADR-IAM-007 §5.4`, `TDD-identity-kernel-004`). Its
    execute-actions email is off, and `realmdef` refuses an SMTP server.
  - Nothing in the Admin Portal or the Identity Control API sets a password.
- **The documentation says otherwise.** `TDD-identity-experience-003` 1.26.0, §Creating a person,
  says "Keycloak asks the person to set a password at first sign-in". That holds only for a sign-in
  the person cannot make.
- **Only two scripts sign anyone in.** identity-control's `deploy/dev/bootstrap.sh` sets the
  bootstrap operator's password through the kernel's administrator. organization-experience's
  `e2e/seed.ps1` does the same for CI's people. Both go around the Identity Control API.

Facts that bound the choice:

- **The kernel's supported interface.** `PUT /admin/realms/{realm}/users/{user-id}/reset-password`
  "Set up a new password for the user" [R10]. With `temporary`, "the user must change the password
  at the first login" [R9]. The kernel offers no way to make an action link without mailing it:
  execute-actions-email is to "Send an email to the user with a link" [R10].
- **No delivery channel yet.** The Notification Platform is designed and not built. On a
  development server its stand-in delivers nothing (`ADR-IAM-007 §5.6`,
  `TDD-identity-control-008` §The Adapter).
- **Providers sign in at `aal2`** (`ADR-IAM-004`). A provider with no second factor enrolls a TOTP
  authenticator, then recovery codes, at that sign-in (`ADR-IAM-004 §5.4`, `ADR-IAM-005 §5.3`).
- **Credentials belong to the kernel.** `STD-IAM-001 §3.1` before 2.8.0: "Passwords … MUST be
  stored and processed only by the approved identity kernel". 2.8.0 names the one exception this
  decision needs (§7).

## 4. Decision Drivers

- **What first-class providers do for an account an administrator creates.**
  - Microsoft Entra "autogenerates a temporary password for the user". The administrator copies it
    "and give[s] it to the user. The user must change the password during the next sign-in" [R4].
  - Entra's Temporary Access Pass is "a time-limited passcode that can be configured for single use
    or multiple sign-ins", most commonly used "for a user to register authentication details during
    the first sign-in". Its value is shown once: "You can't view this value after you select
    **Ok**" [R5].
  - Google Workspace lets the administrator "Copy Password, for example, to send the user their
    password in a chat", and to "Ask the user to change their password" [R6].
  - Okta offers "Set by admin", where "User must change password on first login" is "selected by
    default" [R7].
- **An initial secret is random, short-lived, and never becomes the lasting password.** ASVS 5.0
  6.4.1: "system generated initial passwords or activation codes are securely randomly generated,
  follow the existing password policy, and expire after a short period of time or after they are
  initially used. These initial secrets must not be permitted to become the long term password"
  [R3].
- **Who may choose a password.** NIST SP 800-63B-4 §3.1.1: "Passwords SHALL either be chosen by the
  subscriber or assigned randomly by the CSP" [R1]. Random values come from "an approved random bit
  generator … (i.e., 112 bits as of the date of this publication)" (§3.2.12) [R1].
- **A forced change is allowed here.** "Verifiers and CSPs SHALL NOT require subscribers to change
  passwords periodically. However, verifiers SHALL force a change if there is evidence that the
  authenticator has been compromised" [R1]. A password the issuing provider has seen is such
  evidence.
- **Supported kernel interfaces only** (`ADR-IAM-001 §5.7`), and **no mail from the kernel**
  (`ADR-IAM-007 §5.4`).
- **It must work on a development server**, which has no mail and no Notification Platform.

## 5. Decision

### 5.1 A Provider Issues a Temporary Password

A new command of the Identity Control API:

```text
POST /v1/principals/{principal_id}:issue-temporary-password
     provider, aal2 within the step-up age, X-Administrative-Reason, Idempotency-Key
```

- **When it is allowed.** The Principal is a human, active, and has not yet set a password of its
  own: its kernel user still has `UPDATE_PASSWORD` outstanding. Otherwise it answers `409`
  `credential-established`. It is not a password reset, which stays undecided (§6).
- **Who.** A provider, held like every provider command (`ADR-IAM-004 §5.2`). A provider acting on
  their own Principal is refused, as for every other command.
- **The value.** 24 characters drawn from the operating system's random source, from a 32-symbol
  alphabet without look-alike characters: 120 bits, above NIST's 112 [R1].
- **The kernel call.** `PUT /users/{id}/reset-password` with `temporary` true [R10]. The kernel
  stores and verifies the password. Its required action stays outstanding.
- **Shown once.** The response carries the value with `Cache-Control: no-store`, as Entra's pass is
  shown once [R5]. The Identity Control API keeps no copy, and neither does the BFF. A retry with
  the same `Idempotency-Key` answers the issuance without the value. The provider issues again,
  which replaces it.
- **Evidence.** The service records the issuance: the Principal, the provider, the reason, and when
  it was issued and lapses. Never the value, in a row, a log, a trace or an event
  (`STD-IAM-001 §3.1`, "MUST NOT be logged").

### 5.2 It Lapses, and Is Used Once

- **It lapses.** Keycloak's temporary password, like Entra's, "never expires" [R4]. The Identity
  Control API expires it instead. `IDENTITY_TEMPORARY_PASSWORD_TTL` is 24 hours by default and at
  most, and at least 1 hour (`STD-IAM-001` 2.8.0 §3.1). Entra's pass allows 10 minutes to 30 days
  [R5]. NIST bounds a confirmation code sent to an email address at "24 hours" [R2].
- **How it lapses.** A sweep finds an issuance past its expiry whose user still has
  `UPDATE_PASSWORD` outstanding. It removes the password with
  `DELETE /users/{id}/credentials/{credentialId}`. The authenticator guard's `last_authenticator`
  rule does not apply, because the person never held this credential
  (`TDD-identity-control-005` §Authenticator Guard). The issuance is recorded `lapsed`.
- **It is used once.** At the first sign-in the kernel requires the new password before anything
  else. The issuance is recorded `used` when the kernel event record shows the person's own
  password change (`TDD-identity-control-007`).
- **It cannot become the lasting password.** The realm's password policy gains Keycloak's _Not
  recently used_: "Password cannot be already used by the user. Keycloak stores a history of used
  passwords" [R9]. The forced change refuses the temporary value, as ASVS 6.4.1 requires [R3].

### 5.3 The First Sign-In

1. The person signs in at the kernel's login page with their username and the temporary password.
2. The kernel requires a new password (`login-update-password`, already themed,
   `TDD-identity-kernel-004`).
3. A sign-in that asks for `aal2`, such as the Admin Portal's, then enrolls a TOTP authenticator and
   recovery codes (`ADR-IAM-004 §5.4`, `ADR-IAM-005 §5.3`). A sign-in at `aal1`, such as the account
   application's, does not.
4. Both bindings are notified to the Principal's addresses (`ADR-IAM-007 §5.1`). So is the
   issuance itself, as a password bound by an administrator.

### 5.4 How the Value Reaches the Person

- **The provider verifies the person first,** in person or on a live call, as assisted recovery
  does (`ADR-IAM-005 §5.5`).
- **Then hands it over on a different channel from the username,** and never in a ticket, a chat
  log or an email that also carries the username.
- **A development server.** The owner, as the provider, reads it from the Admin Portal and gives it
  to the person, or signs in as them.
- **Until the command exists, a development server only** uses the kernel's Admin Console: the
  bootstrap administrator sets the password with **Temporary** on, and adds **Configure OTP** to the
  person's required actions, so the first sign-in sets a password and enrolls TOTP. Keycloak
  documents both: "If Temporary is ON, the user must change the password at the first login", and
  required actions "are required after the user provides credentials" [R9]. The runbook's step 10.1
  is that procedure (`deploy/dev/README.md`); it is how a person such as `billy` becomes a Tenant's
  first administrator today. Alternative F says why it is not the lasting path.

### 5.5 What Each Repository Changes

| Repository              | Change                                                                                                                                                                                                                                                                                                                                                                                       |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| identity-control        | `TDD-identity-control-001` (or 005): the command of §5.1, its issuance record and the lapse sweep of §5.2. `TDD-identity-control-008`: the kernel's admin `reset-password` event notified as a password bound by an administrator. `docs/runbooks`: handing the value over (§5.4). `deploy/dev/bootstrap.sh` is unchanged: the bootstrap operator exists before any provider can issue       |
| identity-kernel         | `realm/scnehaux.json` gains the password policy _Not recently used_. `resetPasswordAllowed` stays false and the kernel still sends no mail. The compat suite proves: a temporary password forces `UPDATE_PASSWORD`; the same value is refused at the change; a deleted temporary password no longer signs in. `TDD-identity-kernel-001` §Guessing Limits or a new §Password Policy states it |
| identity-experience     | `TDD-identity-experience-003` §Creating a person: corrected. After creation, the console issues the temporary password and shows it once, with a copy control and its expiry, and clears it on leaving the page. A Principal with no password of its own offers **Issue a new temporary password**. The BFF passes the value through with `no-store`, and logs and stores none of it         |
| organization-experience | Optional: `e2e/seed.ps1` issues through the command instead of the kernel's administrator                                                                                                                                                                                                                                                                                                    |

## 6. Consequences

### Positive

- A person a provider creates can sign in, on a server with no mail.
- Every first credential has a record: who issued it, why, and when it lapsed or was used.
- A provider's second factor is enrolled at that first sign-in, as `ADR-IAM-004` already decides.

### Negative

- **The issuing provider knows the password until the person replaces it.** They could sign in
  first, choose a password and enroll a factor of their own. This is the bootstrap risk
  `ADR-IAM-004 §6` accepts, made narrower by:
  - the issuance's evidence, naming the provider;
  - the notification to the creation address;
  - the lapse after 24 hours;
  - the person, who finds the value refused and reports it.
- **A credential value passes through two Scnehaux processes.** The Identity Control API generates
  it and the BFF carries it once. `STD-IAM-001` 2.8.0 §3.1 admits exactly that, under the conditions
  it lists (§7).
- **A lost password is still not recovered.** Once the person has set their own, this command is
  refused. A provider can only suspend (`TDD-identity-control-005`). A password reset is a separate
  decision.

### Operational

- An issuance that lapses unused is reported to the provider who issued it.
- More than one issuance for a Principal in a day is a signal, and is alerted on.

## 7. Compliance Impact

### Related Standards

- `STD-IAM-001` 2.8.0 §3.1: the one exception this decision needs. A temporary password the
  Identity Control API generates may be held in memory by it and the issuing BFF for one response.
  It is generated, never chosen; temporary in the kernel; shown once to a provider at `aal2`, over
  TLS, with `no-store`; never logged, persisted or replayed; and gone within 24 hours. The
  precedents are the same administrators' APIs: Microsoft Graph returns "a Microsoft-generated
  password", Okta returns "A temporary password that the user can sign in with", and Google's
  Directory API keeps it write-only, "never returned in the API's response body" (STD-IAM-001
  [R37], [R38], [R40]).
- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.7: supported kernel interfaces
  only.
- [ADR-IAM-004](ADR-IAM-004-authentication-assurance-and-step-up.md): `aal2` for the issuing
  provider, and enrollment at the first `aal2` sign-in.
- [ADR-IAM-005](ADR-IAM-005-account-recovery-and-guessing-limits.md): the lockout bounds guessing of
  the temporary password, and §5.5's verification is reused.
- [ADR-IAM-007](ADR-IAM-007-account-security-notifications.md): the issuance and the change are
  notified. The kernel sends no mail.
- [ADR-ORG-007](../organization-tenancy-platform/ADR-ORG-007-the-invited-person-accepts-signed-in.md):
  an invitee signs in with the credential this decision gives.

### Compliance Status

- Meets ASVS 5.0 6.4.1 [R3] and NIST SP 800-63B-4 §3.1.1 [R1] once §5.1 and §5.2 are built.
- Compliant with `STD-IAM-001` 2.8.0 §3.1 once §5.1 and §5.2 hold every condition of its
  exception.

### Required Waivers

None. `STD-IAM-001` 2.8.0 states the exception, so no waiver is needed.

## 8. Alternatives Considered

### Alternative A — A One-Time Enrolment Link, Delivered Out of Band

Okta sends an activation link, or returns it when `sendEmail` is false: "Users who don't have a
password must complete the welcome flow by visiting the activation link" [R7]. Keycloak's
execute-actions email and Auth0's password change ticket do the same [R10][R8].

**Benefits:** nobody but the person sees a secret; the link proves control of the address.

**Rejected for now because:**

- the kernel sends no mail (`ADR-IAM-007 §5.4`), and the Notification Platform is not built;
- the kernel has no supported way to make the link without mailing it [R10], so a link from the
  Notification Platform needs a kernel extension (`ADR-IAM-001 §5.7`);
- the alternative, a page of the Identity Control API that sets the password, processes the
  person's lasting password outside the kernel, which is worse for `STD-IAM-001 §3.1`;
- Auth0 itself warns its ticket endpoint "does not verify the given user's identity" [R8].

**Reopened** when the Notification Platform is in production and the kernel offers a supported
action link.

### Alternative B — Invitation-Based Self-Registration

**Rejected because:** the realm offers no registration (`registrationAllowed` false). A
self-registered user is not created through the Identity Control API, so it carries no
`principal_id` (`TDD-identity-control-001`), and the reconciler disables it as unmapped.

### Alternative C — Passkey First

**Deferred because:** a passkey is registered by someone already signed in. passkeys.dev: "First,
verify that the user is sufficiently strongly authenticated using other login methods" [R11].
Entra bootstraps passkeys with a Temporary Access Pass for that reason [R5]. The realm admits no
passkey sign-in yet (`ADR-IAM-004 §5.1`, `phr` reserved). When it does, this temporary password is
the bootstrap a passkey is registered from.

### Alternative D — The Provider Types the Password

Entra and Okta allow it [R4][R7].

**Rejected because:** NIST admits a password "chosen by the subscriber or assigned randomly by the
CSP" [R1]. A provider is neither, and a chosen value is a guessable one.

### Alternative E — A Temporary Password That Never Lapses

Entra's reset password "never expires" [R4].

**Rejected because:** ASVS 6.4.1 requires expiry [R3]. A never-used password is a standing
credential for an account whose owner may never sign in.

### Alternative F — The Kernel's Administrator Sets It, as the Scripts Do

**Rejected because:** it goes around the Identity Control API, which records no evidence of it.
The Identity Control Service is the only holder of `manage-users` outside break-glass
(`TDD-identity-control-001`).

## 9. References

### Normative

- **[R1]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator
  Management_, August 2025, <https://pages.nist.gov/800-63-4/sp800-63b.html>, accessed
  2026-10-19.
  - §3.1.1: "Passwords SHALL either be chosen by the subscriber or assigned randomly by the CSP."
  - §3.1.1: "Verifiers and CSPs SHALL NOT require subscribers to change passwords periodically.
    However, verifiers SHALL force a change if there is evidence that the authenticator has been
    compromised."
  - §3.2.12: "random values that reference this section SHALL be generated by an approved random
    bit generator [RBG] that provides at least the minimum security strength specified in the
    latest revision of [SP800-131A] (i.e., 112 bits as of the date of this publication)."
- **[R2]** NIST SP 800-63A-4, _Identity Proofing and Enrollment_,
  <https://pages.nist.gov/800-63-4/sp800-63a.html>, accessed 2026-10-19. "If authenticators are
  bound outside of a single protected session with the user, the CSP SHALL confirm the presence of
  the intended subscriber"; confirmation codes "SHALL be valid for at most … 24 hours when sent to
  a validated email address".
- **[R3]** OWASP, _Application Security Verification Standard 5.0.0_, V6.4.1,
  <https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md>, accessed
  2026-10-19. "Verify that system generated initial passwords or activation codes are securely
  randomly generated, follow the existing password policy, and expire after a short period of time
  or after they are initially used. These initial secrets must not be permitted to become the long
  term password." ASVS 4.0.3 V2.3.1 says the same.

### Informative

- **[R4]** Microsoft, _Reset a user's password_ (Microsoft Entra), accessed 2026-10-19.
  <https://learn.microsoft.com/en-us/entra/fundamentals/users-reset-password-azure-portal>.
  Administrators reset a password "if the user never received a password"; "Microsoft Entra ID
  autogenerates a temporary password for the user."; "Copy the password and give it to the user.
  The user must change the password during the next sign-in process."; "The temporary password
  never expires." _How to create, invite, and delete users_
  (<https://learn.microsoft.com/en-us/entra/fundamentals/how-to-create-delete-users>): "Provide a
  password for the user to use during their initial sign-in."
- **[R5]** Microsoft, _Configure a Temporary Access Pass in Microsoft Entra ID to register
  passwordless authentication methods_, accessed 2026-10-19.
  <https://learn.microsoft.com/en-us/entra/identity/authentication/howto-authentication-temporary-access-pass>.
  "A Temporary Access Pass (TAP) is a time-limited passcode that can be configured for single use
  or multiple sign-ins."; "The most common use for a TAP is for a user to register authentication
  details during the first sign-in or device setup"; "Make a note of the actual TAP value, because
  you provide this value to the user. You can't view this value after you select **Ok**."; lifetimes
  of "10 – 43,200 Minutes (30 days)", 1 hour by default.
- **[R6]** Google, _Add an account for a new user_ and _Reset a user's password_ (Google
  Workspace Admin Help), accessed 2026-10-19.
  <https://knowledge.workspace.google.com/admin/users/add-an-account-for-a-new-user> and
  <https://knowledge.workspace.google.com/admin/users/reset-a-users-password>. "Click **Copy
  Password**, for example, to send the user their password in a chat."; "Check the Ask the user to
  change their password box so they can change it to something more secure when they next sign
  in."
- **[R7]** Okta, _Add users manually_ and the Management API's _Activate a user_, accessed
  2026-10-19. <https://help.okta.com/en-us/content/topics/users-groups-profiles/usgp-add-users.htm>
  and <https://github.com/okta/okta-management-openapi-spec/blob/master/dist/current/management-minimal.yaml>.
  "Select Set by user to allow the user to set their password, or select Set by admin and enter a
  password."; "User must change password on first login: Optional. This is selected by default when
  you select Set by admin"; "Users who don't have a password must complete the welcome flow by
  visiting the activation link"; `activationUrl`: "If `sendEmail` is `false`, returns an activation
  link for the user to set up their account."
- **[R8]** Auth0, _Implement User Invitations for Application Sign-Up using Password Reset Emails_
  and _Create a password change ticket_, accessed 2026-10-19.
  <https://auth0.com/docs/customize/email/send-email-invitations-for-application-signup> and
  <https://auth0.com/docs/api/management/v2/tickets/post-password-change>. "an application
  administrator creates a new user account and then sends an email invitation to a user with an
  activation link"; "Note: This endpoint does not verify the given user's identity."; `ttl_sec`
  "defaults to 432000 seconds (5 days)".
- **[R11]** passkeys.dev (W3C Web Identity & Credentials Adoption Community Group and FIDO
  Alliance), _Bootstrapping_, accessed 2026-10-19.
  <https://passkeys.dev/docs/use-cases/bootstrapping/>. "First, verify that the user is
  sufficiently strongly authenticated using other login methods, including multi-factor
  authentication."

### Kernel

- **[R9]** Keycloak, _Server Administration Guide_, Setting a password for a user, Required actions,
  Password policies, accessed 2026-10-19.
  <https://www.keycloak.org/docs/latest/server_admin/index.html>. "If Temporary is ON, the user must
  change the password at the first login."; "These actions are required after the user provides
  credentials."; _Not recently used_: "Password cannot be already used by the user. Keycloak stores
  a history of used passwords."; "To enable Keycloak to send emails, you provide Keycloak with your
  SMTP server settings."
- **[R10]** Keycloak, _Admin REST API_, accessed 2026-10-19.
  <https://www.keycloak.org/docs-api/latest/rest-api/index.html>.
  `PUT /admin/realms/{realm}/users/{user-id}/reset-password` "Set up a new password for the user.";
  `PUT /admin/realms/{realm}/users/{user-id}/execute-actions-email` "Send an email to the user with
  a link they can click to execute particular actions."
