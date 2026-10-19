---
doc_meta:
  id: ADR-ORG-007
  title: The Invited Person Accepts an Invitation, Signed In as Themselves
  adr_type: foundational
  status: proposed
  created: 2026-10-19
  created_date: 2026-10-19
  created_by: Organization Platform Team
  governed_by: [PAD-PLT-002, PAD-PLT-001]
---

# ADR-ORG-007: The Invited Person Accepts an Invitation, Signed In as Themselves

## 1. Title

The Invited Person Accepts an Invitation, Signed In as Themselves.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                       |
| ---------- | -------- | ------------ | ------------------------- | ------------------------------ |
| 2026-10-19 | proposed | foundational | Architecture Review Board | Enterprise Architect — pending |

## 3. Context

A Tenant administrator invites a person by email address to hold a Membership. Today no invitation
can ever be accepted. It waits until the expiry sweep expires it.

How the flow is built (`TDD-organization-control-004` 1.12.0, §Invitation Flow, and
`internal/httpapi/routes.go`):

- **Issue.** `POST /v1/invitations` is Tenant-scoped. It records the intent, the target address, an
  expiry (`ORGANIZATION_INVITATION_TTL`, 7 days) and the SHA-256 of a 256-bit token. The token is
  returned once to the administrator and never stored.
- **Verify.** `POST /v1/invitations/verify-identity` is provider-scoped. It records that a Principal
  holding the invited address exists, and moves the invitation to `identity_verified`. The design
  says identity-control drives it: identity-control consumes `membership.invitation.requested`,
  resolves or creates the Principal, and publishes `identity.principal.identifier-verified`
  (SAD-004 §5.5).
- **Accept.** `POST /v1/invitations/accept` is Tenant-scoped (`requireTenant`). It takes the token,
  and creates the Membership for the Principal that verification recorded.
- **Look up.** `POST /v1/invitations/lookup` is anonymous, reads nothing, and answers the same for
  every token.

Why it is a dead end:

1. **Nothing verifies.** identity-control produces no `identifier-verified` event and consumes no
   `membership.invitation.requested`. No broker carries either.
2. **The event could not be acted on.** "No invitation event carries the target identifier"
   (`TDD-organization-control-004` §Published Events), by STD-GLB-007. A consumer told only that an
   invitation exists cannot resolve the person it names.
3. **The invitee cannot hold the token accept needs.** The kernel issues `organization:<tenant_id>`
   only for a member (`ADR-IAM-006 §5.2`). The invitee is not one until acceptance.
4. **Accept is not bound to the caller.** It creates the Membership for the recorded Principal,
   whoever presents the token. Any member of the Tenant holding the token could accept for the
   invitee.
5. **No surface calls accept.** No BFF or page in organization-experience or identity-experience
   does.

Three facts bound the choice:

- **Tokens carry no email.** STD-IAM-002 §3.2 closes the claim set, and the kernel's compat suite
  asserts it (`TDD-identity-kernel-001` §Claim Projection). A resource cannot read the caller's
  address from the token.
- **The kernel sends no mail and verifies no address** (`ADR-IAM-007 §5.4`). identity-control holds
  each Principal's notification addresses: the address it was created with, and addresses proven
  by a one-time code (`TDD-identity-control-008` §A Person's Own Addresses).
- **A person with no Tenant can already be admitted to one route.** `ADR-ORG-005` admits the self
  caller to `GET /v1/principals/{principal_id}/contexts` and to nothing else.

## 4. Decision Drivers

- **The invited person accepts, signed in as themselves.**
  - GitHub's acceptance route "Converts the authenticated user to an active member of the
    organization, if that user has a pending invitation from the organization" [R1].
  - Microsoft Entra B2B: "The guest uses their own credentials to sign in to your directory" [R3].
  - Google Workspace's transfer invitation prompts the person "to sign in to their personal Google
    account, if they are not already signed in" [R5].
- **Acceptance is bound to the invited address, as the account holds it.**
  - GitHub: "the invitee will only be able to accept the invitation if the email address matches
    with a verified email address" [R2].
  - Auth0: "Invited users must log in or create an account with the email address to which the
    invitation was sent" [R4].
  - Keycloak Organizations: a new user "is forced to provide the same email address used to send
    the invitation" [R6].
- **Possession of the token is not authorization.**
  - OWASP: "even with complex identifiers, access control checks are essential" and "Verify the
    user's permission every time an access attempt is made" [R8].
  - ASVS 5.0 8.2.2: data-specific access "is restricted to consumers with explicit permissions to
    specific data items to mitigate insecure direct object reference (IDOR)" [R9].
  - SAD-004 §5.5: "Invitation possession alone never proves identity."
- **The token is a one-time secret, and it lapses.**
  - ASVS 5.0 11.5.1: non-guessable values come from a CSPRNG "and have at least 128 bits of
    entropy. Note that UUIDs do not respect this condition" [R9].
  - ASVS 5.0 6.5.1: one-time codes "are only successfully usable once" [R9].
  - OWASP: tokens are "Single use and expire after an appropriate period"; the page "adds the
    Referrer Policy tag with the no-referrer value"; and a service must "prevent users from
    brute-forcing tokens in the URL, such as rate limiting" [R7].
  - GitHub expires an invitation after seven days [R2]. Auth0 defaults to 604800 seconds, 7 days,
    with a "Max value: 2592000 seconds (30 days)" [R4].
- **A refusal tells nothing about other people.** WSTG-IDNT-04: "Ensure the application returns
  consistent generic error messages" [R10].
- **Least privilege for a caller with no Tenant** (`ADR-ORG-005 §5.1`).

## 5. Decision

### 5.1 Acceptance Is a Self Command

`POST /v1/invitations/accept` admits the self caller of `ADR-ORG-005 §5.1` and no one else.

- **Who.** A human token, with or without a Tenant, holding no provider grant or one. The
  Membership is created for the caller's own `principal_id`, never for another.
- **Who is refused.** A workload, and a request on behalf of someone else. A provider or Tenant
  administrator who wants a person to hold a Membership grants it with `POST /v1/memberships`.
- **Commands as before.** It requires an `Idempotency-Key`, and the token is in the body. A token
  is never in a path or a query.

### 5.2 The Token Finds One Invitation, and Nothing Else

- **A narrow read.** The token's SHA-256 selects at most one row (`token_hash` is unique across the
  table). The read runs in a role with no login, entered as `organization_self_rt` is
  (`ADR-ORG-005 §5.4`). It reaches the invitation row by its token hash alone, and returns its
  Tenant, Workspace, target address, state and expiry.
- **The Tenant comes from the row.** The Membership is then written under the Tenant scope of the
  invitation, which the token selected, and not from the caller's token or a request field.

### 5.3 The Caller Must Hold the Invited Address

Organization Control asks the Identity Control API whether the caller holds the invited address.

- **The question.** A new identity-control route,
  `POST /v1/principals/{principal_id}/identifiers:match`, admits Organization Control's workload
  alone, as `POST /v1/deliveries` does (`TDD-identity-control-006`). It takes one address and
  answers `{"match": true}` or `{"match": false}`. It discloses no address.
- **What matches: a proven address only (2026-10-19).** An address of an active Principal that is
  `active` and has `verified_at` set (`TDD-identity-control-008` §Data Model), compared without
  case as that design compares them. An address is proven when the person returned the one-time
  code that was sent to it.
  - **The creation address does not count until proven.** A provider records it
    (`ADR-IAM-007 §5.2`), and nobody has shown the person reads it. The person proves it from the
    account application with the same code, through a new command that sends a code to an
    `active` address with no `verified_at`. ADR-IAM-011's enrolment proves it at creation.
  - **Why.** Every product compared binds acceptance to an address the account has proven. GitHub
    accepts "only … if the email address matches with a verified email address associated with the
    invitee's personal account" [R2]. Auth0 requires the invited address, and "When a user accepts
    an invitation, their email address will be marked as verified" [R4]. Keycloak forces "the same
    email address used to send the invitation" [R6]. OpenID Connect defines a verified address as
    one where the provider "took affirmative steps to ensure that this e-mail address was
    controlled by the End-User" [R11].
  - **How the code proves it.** NIST: "Confirmation codes are used to confirm that an applicant has
    access to a postal address, email address, or phone number". They "SHALL include at least 6
    decimal digits" and are valid "24 hours when sent to a validated email address" at most, and
    "Upon its use, the CSP SHALL invalidate the confirmation code" [R12]. identity-control's code
    has 8 digits and lasts 10 minutes and five attempts, inside those bounds.
  - **The match is keyed to the Principal, not to the address.** The caller is its `principal_id`,
    and the address is only checked against it. OpenID Connect: "The RP MUST NOT rely upon this
    value being unique" [R11].
- **Unknown is not no.** If identity-control cannot be reached, acceptance answers `503` and
  changes nothing.

### 5.4 One Transaction, Used Once

Acceptance is the whole join. `verify-identity` and the `identity_verified` state are removed.

```text
accept(token, caller):
    resolve the invitation by the token's hash (§5.2)
    refuse unless it is pending and not past expires_at by the clock
    refuse unless identity-control matches the caller to target_identifier (§5.3)
BEGIN, in the invitation's Tenant scope
    reload the invitation FOR UPDATE; refuse unless still pending
    refuse unless the Tenant is active
    refuse if the caller already holds an active Membership for this context
    create the Membership for the caller's principal_id
    set state 'accepted', principal_id, accepted_at
    outbox: invitation.accepted, membership.lifecycle.granted
COMMIT
```

- **Used once.** A second acceptance finds the invitation `accepted` and is refused.
- **One refusal for every failed lookup.** An unknown, expired, revoked, already-accepted, or
  mismatched token answers the same `404` problem, `invitation-not-acceptable`. The page tells the
  person to ask whoever invited them. A refused Tenant or an existing Membership is answered `409`,
  because by then the caller has proved they hold the invited address.
- **Refusals are counted per caller,** beside the anonymous lookup count, and rate-limited like the
  other commands. Many refusals from one caller signal token guessing
  (organization-control `docs/runbooks/invitation-token-enumeration.md`).

### 5.5 How the Link Reaches the Person

- **Its form.** `https://<organization-experience>/invitations/accept#<token>`. The token is in the
  fragment, which a browser does not send to a server, and the page sends
  `Referrer-Policy: no-referrer` [R7]. The page's script sends the token to its BFF in a command.
- **Production: the Notification Platform delivers it to the invited address.** Organization
  Control requests the delivery when it issues the invitation (`PAD-PLT-005`). The administrator
  then never handles the token. Delivery to that address alone is a production gate, like
  `ADR-IAM-007 §5.6`.
- **A development server: the administrator relays it.** The Notification Platform's stand-in
  delivers nothing. Organization Experience shows the link once, when the invitation is issued.
  The administrator sends it to the person by a channel of their own. It is never shown again; a
  lost link is revoked and issued again.

### 5.6 Where the Person Accepts

Organization Experience serves the page, to any signed-in person.

- The BFF signs the person in without a Tenant, as it does to list their contexts (`ADR-ORG-005`).
- After acceptance, the page offers the new Tenant. Choosing it is a sign-in for that Tenant
  (`ADR-IAM-006 §5.2`).
- A person who is not signed in signs in first, and the page keeps the token in the browser's
  session storage across the redirect, never in a URL the BFF sees.

### 5.7 An Invitee Without an Account

A person with no Principal enrols from the invitation, proving the invited address with a code,
and then accepts as in §5.1 (`ADR-IAM-011`, proposed). There is still no open self-registration.
Until ADR-IAM-011 is built, a provider creates the Principal and issues the first credential
(`ADR-IAM-010`), and the person proves the creation address before accepting.

### 5.8 What Each Repository Changes

| Repository              | Change                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| organization-control    | `TDD-organization-control-004`: acceptance as §5.1 to §5.4. The self caller on `accept`; the token-hash read (§5.2); the identity-control client (§5.3); `verify-identity`, `identity_verified` and its unique-index state removed; the lookup's constant `next` becomes `accept`; the issue command requests delivery (§5.5). `TDD-organization-control-001` lists the route under the self caller. SAD-004 §5.5's diagram is redrawn |
| identity-control        | `TDD-identity-control-008` (or 001): `POST /v1/principals/{principal_id}/identifiers:match`, Organization Control's workload alone, a boolean answer, counting only `active` addresses with `verified_at` set, no address in a response or a log. `TDD-identity-control-008`: a command that sends a proof code to an `active`, unproven address, so a creation address can be proven                                                  |
| identity-kernel         | None. The claim set and the no-mail rule stay                                                                                                                                                                                                                                                                                                                                                                                          |
| organization-experience | `TDD-organization-experience-002`: the link shown once on issue (§5.5); the acceptance page and its BFF route for a person with no Tenant (§5.6). The BFF guard's provider-only list loses `/v1/invitations/verify-identity`                                                                                                                                                                                                           |
| identity-experience     | `TDD-identity-experience-002`: the account application offers to prove an unproven creation address                                                                                                                                                                                                                                                                                                                                    |

The route `verify-identity` has no caller outside organization-control's own tests and
organization-experience's guard list, so removing it breaks no consumer.

## 6. Consequences

### Positive

- An invitation can be accepted, by the person it names and by nobody else.
- Each fact that admits the person is checked when it is used: the token, the address, the
  Tenant's state and the existing Memberships. No half-join waits in a state.
- No broker flow, kernel extension or mail from the kernel is added.

### Negative

- **Acceptance depends on identity-control at that moment.** If it is down, acceptance waits. The
  invitation's 7 days absorb an outage.
- **A person must prove an address before accepting.** One more step for someone whose creation
  address was never proven. The account application asks for it, and the acceptance page sends a
  person who has no proven match there.
- **Proving needs a delivered code.** On a development server the code reaches a mail catcher
  (`ADR-IAM-007 §5.3`, 2026-10-19). In production it waits on the Notification Platform, as every
  notification does.
- **An invitee with no Principal waits for a provider** until ADR-IAM-011 is built (§5.7).
- **On a development server the administrator handles the token.** It is development only, and is
  why delivery is a production gate.

### Operational

- The match route is counted and logged without the address. A run of `false` answers for one
  Principal is a signal, like the refusals of §5.4.
- A refused acceptance is never retried by the BFF.

## 7. Compliance Impact

### Related Standards

- SAD-004 §5.5 and §8.1: possession proves nothing; the anonymous lookup stays the only anonymous
  route.
- `STD-IAM-002 §3.2`: the address is asked of identity-control, not read from a token.
- `STD-GLB-007`: no event carries the address; the match answer carries none either.
- [ADR-ORG-005](ADR-ORG-005-a-person-lists-their-own-contexts.md): the self caller and its narrow
  role.
- [ADR-IAM-006](../identity-access-platform/ADR-IAM-006-tenant-context-in-tokens.md) §5.2: choosing
  the new Tenant is a sign-in.
- [ADR-IAM-007](../identity-access-platform/ADR-IAM-007-account-security-notifications.md): the
  addresses, and the Notification Platform's role in delivery.
- [ADR-IAM-010](../identity-access-platform/ADR-IAM-010-first-credential-for-an-administrator-created-person.md):
  how the invitee gets a credential to sign in with.

### Compliance Status

Compliant once organization-control, identity-control and organization-experience implement §5.8.
Delivery of the link to the invited address (§5.5) is a production gate.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — identity-control Verifies, Through the Broker (As Designed)

identity-control consumes `membership.invitation.requested`, resolves or creates the Principal,
and calls `verify-identity` or publishes `identifier-verified`.

**Rejected because:**

- the event carries no address, by design (point 2 of §3), so identity-control cannot act on it;
- identity-control would create a Principal on a Tenant administrator's request, which is more
  authority than a Tenant administrator holds;
- it records a half-join and still needs the person to accept, with a token they cannot hold
  (point 3 of §3).

### Alternative B — The Kernel's Organization Invitations

Keycloak sends "an email sent with a link that the person should click to perform the necessary
steps to join an organization" [R6].

**Rejected because:**

- it needs mail, which the kernel does not send (`ADR-IAM-007 §5.4`);
- it makes the kernel's organization membership the authority, the inverse of `ADR-ORG-001`, where
  Keycloak Organizations are a projection;
- a new user goes through self-registration, which the realm does not offer.

### Alternative C — Accept by Holding the Token Alone

**Rejected because:** SAD-004 §5.5 says possession proves nothing, and OWASP requires the check
whatever the identifier [R8]. A forwarded or leaked link would admit whoever opened it.

### Alternative D — Keep Accept Tenant-Scoped, and Give the Invitee a Tenant Token

**Rejected because:** the kernel issues a Tenant only to a member (`ADR-IAM-006 §5.2`). Making the
invitee a member first would grant before acceptance.

### Alternative E — The Administrator Picks a Principal When Inviting

**Rejected because:** a Tenant administrator would need to search every Principal of the estate,
which discloses people outside their Tenant.

### Alternative F — Read the Address From the Token

**Rejected because:** tokens carry no email (`STD-IAM-002 §3.2`), and the kernel verifies none.

## 9. References

### Normative

- **[R7]** OWASP, _Forgot Password Cheat Sheet_, §URL Tokens and §Security Tokens, accessed
  2026-10-19. <https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html>.
  "Generated using a cryptographically secure random number generator."; "Single use and expire
  after an appropriate period."; "Ensure that the reset password page adds the Referrer Policy tag
  with the no-referrer value"; "Implement appropriate protection to prevent users from
  brute-forcing tokens in the URL, such as rate limiting."
- **[R8]** OWASP, _Insecure Direct Object Reference Prevention Cheat Sheet_, accessed 2026-10-19.
  <https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html>.
  "However, even with complex identifiers, access control checks are essential."; "Verify the
  user's permission every time an access attempt is made."
- **[R9]** OWASP, _Application Security Verification Standard 5.0_, accessed 2026-10-19.
  <https://github.com/OWASP/ASVS/tree/master/5.0/en>.
  - 6.5.1: "Verify that lookup secrets, out-of-band authentication requests or codes, and
    time-based one-time passwords (TOTPs) are only successfully usable once."
  - 8.2.2: "Verify that the application ensures that data-specific access is restricted to
    consumers with explicit permissions to specific data items to mitigate insecure direct object
    reference (IDOR) and broken object level authorization (BOLA)."
  - 11.5.1: "Verify that all random numbers and strings which are intended to be non-guessable
    must be generated using a cryptographically secure pseudo-random number generator (CSPRNG) and
    have at least 128 bits of entropy. Note that UUIDs do not respect this condition."
- **[R10]** OWASP, _Web Security Testing Guide_, WSTG-IDNT-04 Testing for Account Enumeration and
  Guessable User Account, accessed 2026-10-19.
  <https://github.com/OWASP/wstg/blob/master/document/4-Web_Application_Security_Testing/03-Identity_Management/04-Account_Enumeration_and_Guessable_User_Account.md>.
  "Ensure the application returns consistent generic error messages in response to invalid account
  name, password or other user credentials entered during the log in process."

- **[R11]** OpenID Foundation, _OpenID Connect Core 1.0 incorporating errata set 2_, §5.1 and §5.7,
  accessed 2026-10-19. <https://openid.net/specs/openid-connect-core-1_0.html>. `email_verified`:
  "True if the End-User's e-mail address has been verified; otherwise false. When this Claim Value
  is true, this means that the OP took affirmative steps to ensure that this e-mail address was
  controlled by the End-User at the time the verification was performed."; `email`: "The RP MUST
  NOT rely upon this value being unique".
- **[R12]** NIST SP 800-63A-4, _Digital Identity Guidelines: Identity Proofing and Enrollment_,
  Requirements for Confirmation Codes, accessed 2026-10-19.
  <https://pages.nist.gov/800-63-4/sp800-63a.html#ConfirmCodes>. "Confirmation codes are used to
  confirm that an applicant has access to a postal address, email address, or phone number for the
  purposes of future communications."; "Confirmation codes used for these purposes SHALL include at
  least 6 decimal digits (or equivalent) from an approved random bit generator"; "Confirmation codes
  SHALL be valid for at most: … 24 hours when sent to a validated email address Upon its use, the
  CSP SHALL invalidate the confirmation code."

### Informative

- **[R1]** GitHub, _REST API: Organization members_, Update an organization membership for the
  authenticated user, accessed 2026-10-19.
  <https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28>.
  `PATCH /user/memberships/orgs/{org}`: "Converts the authenticated user to an active member of the
  organization, if that user has a pending invitation from the organization."; "Only "active" will
  be accepted."
- **[R2]** GitHub, _Inviting users to join your organization_, accessed 2026-10-19.
  <https://docs.github.com/en/organizations/managing-membership-in-your-organization/inviting-users-to-join-your-organization>.
  "If an invitee does not accept the invitation within seven days, the pending invitation expires
  automatically."; "the invitee will only be able to accept the invitation if the email address
  matches with a verified email address".
- **[R3]** Microsoft, _Microsoft Entra B2B collaboration invitation redemption_, accessed
  2026-10-19. <https://learn.microsoft.com/en-us/entra/external-id/redemption-experience>. "The
  guest uses their own credentials to sign in to your directory."; the account's consent status
  "is initially set to **PendingAcceptance**. This setting remains until the guest accepts your
  invitation".
- **[R4]** Auth0, _Invite Organization Members_ and _Create invitations to an organization_
  (Management API), accessed 2026-10-19.
  <https://auth0.com/docs/manage-users/organizations/configure-organizations/invite-members> and
  <https://auth0.com/docs/api/management/v2/organizations/post-invitations>. "Invited users must
  log in or create an account with the email address to which the invitation was sent."; "When a
  user accepts an invitation, their email address will be marked as verified."; the
  invitation's `ttl_sec` "defaults to 604800 seconds (7 days)", "Max value: 2592000 seconds (30
  days)."
- **[R5]** Google, _Use the transfer tool to migrate unmanaged personal accounts_, accessed
  2026-10-19.
  <https://knowledge.workspace.google.com/admin/users/use-the-transfer-tool-to-migrate-unmanaged-users>.
  "Users get an email when you send them a transfer request. In the email, they can click Transfer
  my account . If they do, they're prompted to sign in to their personal Google account, if they
  are not already signed in."
- **[R6]** Keycloak, _Server Administration Guide_, Managing organizations: Inviting users and
  Managing invitations, accessed 2026-10-19.
  <https://www.keycloak.org/docs/latest/server_admin/index.html>. "An invitation is basically an
  email sent with a link that the person should click to perform the necessary steps to join an
  organization."; for a new user, "the user is forced to provide the same email address used to
  send the invitation."; "When a user successfully accepts an invitation, the invitation is
  automatically deleted from the system."
