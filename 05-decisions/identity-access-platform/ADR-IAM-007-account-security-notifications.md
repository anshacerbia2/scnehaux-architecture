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

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-06 | accepted | foundational | Architecture Review Board | Enterprise Architect |

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
  subscribers with authentication at AAL2 or higher". A provider can do it through assisted
  recovery. Either change is notified to every address held before the change.
- **The minimum is two.** The Identity Experience asks for a second address until one is proven.
  A Principal with only one address still receives every notification there.

### 5.3 Identity Decides, Notification Delivers

- **Identity Control owns why and to whom.** It detects the event, takes the Principal's
  notification addresses at that instant as the recipients, and submits one intent per event to the
  Notification Platform. It does not render or send anything itself.
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

On a development server, a stand-in records the intents it is sent. The gap of `ADR-IAM-004 §5.5`
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
    notification addresses except postal addresses"; "The notification SHALL provide clear
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
