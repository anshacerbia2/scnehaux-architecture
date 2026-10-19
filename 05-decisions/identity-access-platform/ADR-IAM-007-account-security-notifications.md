---
doc_meta:
  id: ADR-IAM-007
  title: Account Security Notifications, Decided by Identity and Delivered by Notification
  adr_type: foundational
  status: accepted
  created: 2026-10-06
  created_date: 2026-10-06
  created_by: Identity Platform Team
---

# ADR-IAM-007: Account Security Notifications, Decided by Identity and Delivered by Notification

## 1. Title

Account Security Notifications, Decided by Identity and Delivered by Notification.

## 2. Status

| Date       | Status            | ADR Type     | Reviewers                 | Approver             |
| ---------- | ----------------- | ------------ | ------------------------- | -------------------- |
| 2026-10-06 | accepted          | foundational | Architecture Review Board | Enterprise Architect |
| 2026-10-19 | accepted, amended | foundational | Architecture Review Board | Enterprise Architect |

**Amended 2026-10-19, in place,** on two points: §5.2 no longer promises a provider path for adding
an address, and §5.3 gains a development-only exception for a mail catcher. It is edited in place
because no system this decision governs is in production (GDC-010 §2.4.2): identity-control runs on
development servers only, and the Notification Platform is not built (§5.6).

## 3. Context

Two accepted decisions leave the same gap open, and both make it a production gate.

- `ADR-IAM-004 §5.5`: a new authenticator must be notified "via a mechanism independent of the
  transaction binding the new authenticator" [R1], and "the realm sends no mail".
- `ADR-IAM-005 §5.7`: "In all cases, account recovery SHALL cause a notification to be sent to the
  subscriber or their designee" [R1], and it is "not met yet".

NIST SP 800-63B-4 §4.6 states what such a notification is [R1]:

- Which events. Binding an authenticator and account recovery require it. So does issuing a
  replacement recovery code, which "SHALL result in an account recovery notification". The CSP
  "SHOULD notify the subscriber when an authenticator is invalidated".
- Where it goes. It is sent "to the notification addresses stored in the subscriber account", and
  "CSPs SHALL support at least two notification addresses per subscriber account". "Notifications
  SHALL be sent to all notification addresses except postal addresses".
- Who may change the addresses. The CSP "SHOULD allow subscribers with authentication at AAL2 or
  higher … to update their notification addresses".
- What it says. It "SHALL provide clear instructions, including contact information, in case the
  recipient repudiates the event".

The established platforms send these as a matter of course. Okta sends an email "when an
authenticator has been enrolled for their account", to "help end users verify whether the
enrollment is legitimate or not", and another "when one or more authenticators have been reset or
removed" [R2].

Three facts about this estate bound the choice:

1. **The kernel can mail, but not all of this.** Keycloak's `email` event listener mails a user on
   six user event types: `LOGIN_ERROR`, `UPDATE_PASSWORD`, `REMOVE_TOTP`, `UPDATE_TOTP`,
   `UPDATE_CREDENTIAL` and `REMOVE_CREDENTIAL` [R3]. Its handler for admin events is empty, so an
   authenticator a provider removes through the Admin API is mailed to no one. It sends only to the
   user's one address, and only "if user.getEmail() != null && user.isEmailVerified()". A failure
   is logged, "Failed to send type mail", and nothing retries it or records it [R3].
2. **Two of the events start outside the kernel.** Assisted recovery (`ADR-IAM-005 §5.5`) and the
   removal of an authenticator by containment (`TDD-identity-control-005`) are Identity Control
   commands. They reach the kernel as admin events, which point 1 excludes.
3. **The estate has a communication platform.** `PAD-PLT-005` gives "Products own why a
   communication is needed … and business-recipient eligibility. Notification owns how an accepted
   communication is rendered and delivered" [R4]. It holds sender and provider configuration, keeps
   "Passwords, OAuth refresh tokens, private keys, and API secrets" in Trust Services, tracks
   delivery outcomes, and gives "mandatory security/transactional communication" its own suppression
   policy. It lists "Identity account lifecycle or authentication" as out of its scope.

## 4. Decision Drivers

- Meet NIST SP 800-63B-4 §4.6 for every event it names, whether the event starts in the kernel or
  in the Identity Control API.
- At least two notification addresses, each one the person has shown they control.
- A notification that cannot be delivered is visible, retried, and reported, never only logged.
- One communication capability in the estate, with credentials in Trust Services (`PAD-PLT-005`).
- No kernel extension unless a requirement cannot be met without one (`ADR-IAM-001 §5.7`).

## 5. Decision

### 5.1 The Events

The Identity Control API requests a notification for each of these events, in every case and
whoever acted:

| Event                                                                               | NIST SP 800-63B-4                   | Begins in                                      |
| :---------------------------------------------------------------------------------- | :---------------------------------- | :--------------------------------------------- |
| An authenticator is bound: a TOTP, a passkey or security key, or a new password     | §4.1.2.1 SHALL                      | The kernel, or an application-initiated action |
| Recovery codes are issued or replaced                                               | §4.2.1.1 SHALL, as account recovery | The kernel                                     |
| An account is recovered: a recovery code is used, or a provider's assisted recovery | §4.2.3 SHALL                        | The kernel, or an Identity Control command     |
| An authenticator is removed or invalidated, by the person or by a provider          | §4.5 SHOULD, taken as required here | The kernel, or an Identity Control command     |
| A notification address is added or removed                                          | Not named by NIST; decided here     | An Identity Control command                    |

A password replaces a bound authenticator, so it is notified as a binding. The last row is this
decision's own: an attacker who can add an address can then receive every later notification, so the
existing addresses are told.

`TDD-identity-control-007` maps each row to the kernel's event types and Identity Control's
commands, and the compatibility suite proves that each event is recorded with what the mapping
needs. The kernel event record already holds every kernel user and admin event (`STD-IAM-001 §3.8`),
so the notification is decided from that record and from Identity Control's own commands. It is
not decided from the token or the browser.

### 5.2 Notification Addresses Belong to the Principal Record

- **The Identity Control API keeps them, not the kernel.** A Keycloak user carries one email. NIST
  asks for at least two addresses, so they are a list on the Principal record.
- **The first one is the email the Principal was created with.** It is a notification address from
  creation.
- **Every address added later must be proven.** It receives notifications only after its holder
  returns a one-time code that was sent to it.
- **Changes need aal2 and are themselves notified.** An address is added or removed by the
  Principal at `aal2` through the Identity Experience, which follows NIST's "SHOULD allow
  subscribers with authentication at AAL2 or higher". Either change is notified to every address
  held before the change.
- **No provider adds an address (amended 2026-10-19).** This decision once said "A provider can do
  it through assisted recovery", and no design specified it. It is withdrawn. Assisted recovery
  restores the person's sign-in (`ADR-IAM-005 §5.5`), and the person then adds and proves an
  address at `aal2` themselves. A provider's only address is the creation address, and it counts as
  proven only once its holder returns a code (`ADR-ORG-007 §5.3`). The reasons:
  - NIST gives the change to the person: "The CSP SHOULD allow subscribers with authentication at
    AAL2 or higher … to update their notification addresses" [R1].
  - Where administrators may set a contact value, the platforms are moving to what the person
    registers. Entra lets an administrator "manually set the authentication contact information for
    anyone", and users "can immediately use those values", but "Starting Oct 5, 2026, SSPR will only
    accept explicitly registered authentication methods" [R5]. Okta enrolls an administrator's
    factor in `PENDING_ACTIVATION` unless `activate` skips it, and "Some factors (`call`, `email`,
    `push`, `sms`, …) require activation to complete the enrollment process" [R6]. Auth0 sends "a
    verification email" when `verify_email` is set [R7].
  - An address a provider set would be the one place an attacker who deceives a provider could
    receive every later notification.
- **The minimum is two.** The Identity Experience asks for a second address until one is proven.
  A Principal with only one address still receives every notification there.

### 5.3 Identity Decides, Notification Delivers

- **Identity Control owns why and to whom.** It detects the event, takes the Principal's
  notification addresses at that instant as the recipients, and submits one intent per event to the
  Notification Platform. It does not render or send anything itself, with one development-only
  exception below.
- **Development-only exception: a mail catcher (2026-10-19).** On a development server, and never
  in production, Identity Control's development adapter may render a plain message and hand it by
  SMTP to a mail catcher in the development stack. That is the only way a proof code can reach a
  reader there, as it will reach an inbox in production (`TDD-identity-control-008` 1.6.0 §Proving an
  Address on a Development Server, option A). Its conditions:
  - **A catcher that delivers nothing.** Mailpit "acts as an SMTP server, provides a modern web
    interface to view & test captured emails, and includes an API for automated integration
    testing"; relaying is opt-in, because "the configuration file (yaml syntax) must be provided to
    Mailpit" [R8]. No relay is configured. Keycloak's own testsuite works the same way: "a standalone
    mock mail server for testing email-related features such as email verification, password reset,
    and other email notifications" [R9].
  - **Refused in production at startup,** as `standin` is. ASVS 5.0 13.4.2: "debug modes are disabled
    for all components in production environments" [R10].
  - **Its API serves the development proof.** Mailpit is an "email & SMTP testing tool with API for
    developers", for "Integration testing using the REST API to view, read and process messages"
    [R8], so `deploy-dev` can prove `:verify` end to end.
  - **No code or address in a log.** ASVS 5.0 16.2.5: "it may not be allowed to log certain data,
    such as credentials" [R10]; ASVS 4.0.3 7.1.1: "Verify that the application does not log
    credentials or payment details" [R11]; the OWASP Logging Cheat Sheet's data to exclude includes
    "Authentication passwords", "Access tokens" and "Encryption keys and other primary secrets"
    [R12]. The catcher's mailbox is the only place the code is readable.
  - **Why an inbox, and not a file or a response.** NIST's notification addresses "may be any means
    by which the subscriber can be reliably contacted" [R1], and a code proves control of an address
    only when it is read at that address. ASVS 4.0.3 14.3.2 asks that "debug modes are disabled in
    production" [R11], which is what option C would have to rely on.
  - **On the stack's internal network,** and its web interface on `127.0.0.1` only, as every port is
    (`STD-GLB-009`).
  - **It renders nothing in production.** The rendering, templates and delivery remain the
    Notification Platform's (§5.3 above, `PAD-PLT-005`).

  Options B (a code in a file), C (a code in a response) and D (no proof on a development server)
  are rejected: B leaves a secret at rest on the disk, C is the disclosure ASVS 13.4.2 guards
  against, and D leaves the add path, and with it `ADR-ORG-007`'s proven-address match, unusable on
  a development server.

- **The intent says what happened.** It names a template family per event type and carries the
  bounded values the message needs: the event, its time, the authenticator's type and label, and
  whether a provider acted. It also carries the repudiation instruction and the contact that NIST
  requires. It carries no credential value and no code.
- **The communication class is mandatory security.** Under `PAD-PLT-005 §3.6`, such a message is
  not subject to marketing opt-out. A recipient cannot unsubscribe from being told that their account
  changed.
- **Every intent is evidence.** Identity Control records each intent beside the event that caused
  it, keyed by the event, so each event is requested once. It records the Notification Platform's
  identifier and final status too. An intent that is refused, or not delivered within its retry
  policy, is reported to the operator. It is never silently dropped.

### 5.4 The Kernel Sends No Mail

The realm has no SMTP server, the `email` event listener is not enabled, and no email theme is
built.

- **Point 1 rules it out as the mechanism.** It cannot see admin events, it addresses one mailbox,
  and its failures disappear into a log.
- **Running it as well would split one capability in two.** Two senders would mean two templates,
  two credentials and two delivery records, for the same person and the same event.
- **The kernel's own mail flows stay unused.** Email verification, reset of credentials and
  execute-actions email all stay off. Recovery is the recovery code or assisted recovery
  (`ADR-IAM-005`), and proof of an address is §5.2's code.

### 5.5 How Soon

The kernel event record is read by sweep (`TDD-identity-control-007`), so a kernel event is notified
within one sweep interval of being recorded. An Identity Control command requests its notification
in its own transaction. Production sets the sweep interval to 5 minutes. That is this decision's
choice of a bound close enough for a person to act on, and it is within the maximum
`TDD-identity-kernel-003` allows.

The listener extension of `TDD-identity-kernel-003` is the next step if a tighter bound is required.
It is not built for this decision.

### 5.6 Until the Notification Platform Exists

The Notification Platform is designed (`PAD-PLT-005`, its SAD) and not yet built. Identity Control
builds its side against that contract:

- the events;
- the addresses and their proof;
- the intents and their evidence.

On a development server, a stand-in records the intents it is sent, and the mail catcher of §5.3
(2026-10-19) receives the messages that carry a code. The gap of `ADR-IAM-004 §5.5`
and `ADR-IAM-005 §5.7` closes when both sides are in production, and it remains a production gate
until then.

## 6. Consequences

### Positive

- Every event NIST names is notified, including those a provider causes through the Admin API.
- A person can learn of a change through a second address an attacker has not taken over.
- Delivery has a record and retries, and a failure reaches an operator.
- One capability renders and sends for the whole estate, with its credentials in Trust Services.

### Negative

- **It depends on a platform that is not built.** The production gate now waits on the Notification
  Platform as well as on Identity Control's side.
- **A kernel event is notified one sweep late.** That is up to 5 minutes in production, against
  Keycloak's listener, which sends after the transaction commits.
- **Addresses are a new record to secure.** They are as sensitive as the authenticators they protect,
  so adding one needs `aal2` and its proof, and every change is notified.

### Operational

- An undelivered security notification is an alert, as an undeliverable recovery path would be.
- The repudiation contact in every message reaches the people who run assisted recovery
  (`ADR-IAM-005 §5.5`).

## 7. Compliance Impact

### Related Standards

- `STD-IAM-001 §3.1`: "secure recovery" and MFA include their notifications.
- `ADR-IAM-004 §5.5` and `ADR-IAM-005 §5.7`: the gap they record is closed by this design, once it
  is built.
- `PAD-PLT-005`: Identity is a consumer that owns the intent and the recipients.
- `ADR-IAM-001 §5.7`: no kernel extension is added.

### Compliance Status

- **Designed to meet NIST SP 800-63B-4 §4.6, §4.1.2.1, §4.2.1.1 and §4.2.3** once built.
- **Not met in production until** Identity Control's side and the Notification Platform are both
  delivered.

### Required Waivers

None. The gap remains a production gate, as `ADR-IAM-004` and `ADR-IAM-005` already record.

## 8. Alternatives Considered

### Alternative A — The Kernel Mails: Realm SMTP and the `email` Event Listener

**Benefits:** built in and supported, with no new service. It sends right after the transaction
commits.

**Rejected because:** of §3 point 1.

- It is blind to admin events, so a provider's removal of an authenticator and assisted recovery
  would go unnotified.
- It addresses one mailbox, where NIST requires support for two.
- A failure is only logged.
- It would hold the SMTP credential in the realm, outside Trust Services.

### Alternative B — Identity Control Sends Mail Itself

**Benefits:** it covers every event, with no dependency on another platform.

**Rejected because:** it would be a second communication capability. It would need its own
templates, provider configuration, retries, bounce handling and credentials, which is everything
`PAD-PLT-005` exists so that each product does not build.

### Alternative C — The Notification Platform Subscribes to Identity's Events and Decides

**Benefits:** Identity only publishes. It submits no intents.

**Rejected because:** `PAD-PLT-005` gives the "why" and the recipients to the producing domain, and
excludes "Identity account lifecycle or authentication" from Notification. The addresses and their
proof are identity data. Who must be told of a recovery is an identity rule.

### Alternative D — A Kernel Listener Extension for Immediate Notification

**Benefits:** the kernel's events reach Identity Control at once, not one sweep later.

**Deferred, not rejected:** §5.5's bound is met by the sweep. The extension stays the next step,
already designed, if a tighter bound is required.

## 9. References

### Normative

- **[R1]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator
  Management_, August 2025, <https://pages.nist.gov/800-63-4/sp800-63b.html>, accessed 2026-10-06.
  - §4.6 Account Notifications: "Certain subscriber account events (e.g., the binding of an
    authenticator, account recovery) require the subscriber or someone designated by them to be
    independently notified. These notifications help the subscriber detect possible fraud associated
    with their subscriber account. Events that require notification SHALL cause a notification to be
    sent to the notification addresses stored in the subscriber account"; "CSPs SHALL support at least
    two notification addresses per subscriber account"; "The CSP SHOULD allow subscribers with
    authentication at AAL2 or higher (or at AAL1 if that is the highest AAL available for the
    subscriber account) to update their notification addresses"; "Notifications SHALL be sent to all
    notification addresses except postal addresses"; "Notification addresses may be any means by
    which the subscriber can be reliably contacted" (accessed again 2026-10-19, through
    <https://pages.nist.gov/800-63-4/sp800-63b/events/>); "The notification SHALL provide clear
    instructions, including contact information, in case the recipient repudiates the event
    associated with the notification."
  - §4.1.2.1: "When an authenticator is added, the CSP SHALL notify the subscriber via a mechanism
    independent of the transaction binding the new authenticator, as described in Sec. 4.6."
  - §4.2.1.1: "The issuance of a replacement recovery code SHALL result in an account recovery
    notification, as described in Sec. 4.6."
  - §4.2.3: "In all cases, account recovery SHALL cause a notification to be sent to the subscriber or
    their designee, as described in Sec. 4.6."
  - §4.5: "The CSP SHOULD notify the subscriber when an authenticator is invalidated, as described in
    Sec. 4.6."

- **[R10]** OWASP, _Application Security Verification Standard 5.0.0_, V13 and V16, accessed
  2026-10-19. <https://github.com/OWASP/ASVS/tree/v5.0.0/5.0/en>. 13.4.2: "Verify that debug modes
  are disabled for all components in production environments to prevent exposure of debugging
  features and information leakage."; 16.2.5: "For example, it may not be allowed to log certain
  data, such as credentials or payment details."

- **[R11]** OWASP, _Application Security Verification Standard 4.0.3_, V7 and V14, accessed
  2026-10-19. <https://github.com/OWASP/ASVS/tree/v4.0.3/4.0/en>. 7.1.1: "Verify that the
  application does not log credentials or payment details. Session tokens should only be stored in
  logs in an irreversible, hashed form."; 14.3.2: "Verify that web or application server and
  application framework debug modes are disabled in production to eliminate debug features,
  developer consoles, and unintended security disclosures." The sources of
  `TDD-identity-control-008` 1.6.0.
- **[R12]** OWASP, _Logging Cheat Sheet_, Data to exclude, accessed 2026-10-19.
  <https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html>. "Session
  identification values (consider replacing with a hashed value if needed to track session specific
  events)"; "Access tokens"; "Authentication passwords"; "Encryption keys and other primary secrets".

### Informative

- **[R2]** Okta, _Authenticator enrolled notification email for end users_,
  <https://help.okta.com/oie/en-us/content/topics/identity-engine/healthinsight/notifications-authenticator-enroll.htm>:
  "Okta sends an email to the end user when an authenticator has been enrolled for their account";
  "Enable this email notification to help end users verify whether the enrollment is legitimate or
  not." _Authenticator reset notifications for end users_,
  <https://help.okta.com/oie/en-us/Content/Topics/identity-engine/healthinsight/notifications-authenticator-reset.htm>:
  "Enable this email notification to inform end users when one or more authenticators have been
  reset or removed." Both accessed 2026-10-06.
- **[R3]** Keycloak 26.7.5 source, `org.keycloak.events.email.EmailEventListenerProviderFactory` and
  `EmailEventListenerProvider`, <https://github.com/keycloak/keycloak/tree/26.7.5/services/src/main/java/org/keycloak/events/email>:
  the supported events `LOGIN_ERROR, UPDATE_PASSWORD, REMOVE_TOTP, UPDATE_TOTP, UPDATE_CREDENTIAL,
REMOVE_CREDENTIAL`; the admin event handler `onEvent(AdminEvent event, boolean
includeRepresentation)` has an empty body; the send condition `user.getEmail() != null &&
user.isEmailVerified()`; a failure is `log.error("Failed to send type mail", e)`.
- **[R4]** `PAD-PLT-005` Enterprise Notification Platform 2.4.1, §1 Purpose & Scope, §1.1 Out Of
  Scope, §3.6 Suppression Decision Order, §4.2 Integration Consumed.
- **[R5]** Microsoft, _Prepopulate Contact Information for Self-Service Password Reset_ (Microsoft
  Entra ID), accessed 2026-10-19.
  <https://learn.microsoft.com/en-us/entra/identity/authentication/howto-sspr-authenticationdata>.
  "users who are assigned at least the Privileged Authentication Administrator role can manually
  set the authentication contact information for anyone."; "If you provided a value for Mobile
  phone or Alternate email, users can immediately use those values to reset their passwords, even
  if they haven't registered for the service."; "Starting Oct 5, 2026, SSPR will only accept
  explicitly registered authentication methods."
- **[R6]** Okta, _Okta API_ (OpenAPI specification in `okta-sdk-java`), Enroll a factor and Activate
  a factor, accessed 2026-10-19.
  <https://github.com/okta/okta-sdk-java/blob/master/src/swagger/api.yaml>. "All responses return
  the enrolled factor with a status of either `PENDING_ACTIVATION` or `ACTIVE`."; `activate`: "If
  `true`, the factor is immediately activated as part of the enrollment. An activation process isn't
  required."; "Some factors (`call`, `email`, `push`, `sms`, `token:software:totp`, `u2f`, and
  `webauthn`) require activation to complete the enrollment process."
- **[R7]** Auth0, _Management API: Update a User_, accessed 2026-10-19.
  <https://auth0.com/docs/api/management/v2/users/patch-users-by-id>. `email_verified`: "If set to
  false the user will not receive a verification email unless verify_email is set to true.";
  `verify_email`: "Whether this user will receive a verification email after creation (true) or no
  email (false)."
- **[R8]** Mailpit, home page, _README_ and _SMTP relaying_, accessed 2026-10-19.
  <https://mailpit.axllent.org/>, <https://github.com/axllent/mailpit/blob/develop/README.md> and
  <https://mailpit.axllent.org/docs/configuration/smtp-relay/>. "It acts as an SMTP server, provides
  a modern web interface to view & test captured emails, and includes an API for automated
  integration testing."; "Mailpit - email & SMTP testing tool with API for developers"; "Integration
  testing using the REST API to view, read and process messages"; "Configuring an SMTP relay enables the message “release” feature, which
  allows you to relay the message via another pre-configured SMTP server."; "To enable SMTP
  relaying, the configuration file (yaml syntax) must be provided to Mailpit".
- **[R9]** Keycloak, _docs/tests.md_, Mail server, accessed 2026-10-19.
  <https://github.com/keycloak/keycloak/blob/main/docs/tests.md>. "The Keycloak testsuite includes a
  standalone mock mail server for testing email-related features such as email verification,
  password reset, and other email notifications."
