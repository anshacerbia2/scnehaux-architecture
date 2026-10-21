---
doc_meta:
  id: ADR-IAM-011
  title: An Invitee Without an Account Enrols at Redemption, After Proving the Address
  adr_type: foundational
  status: accepted
  created: 2026-10-19
  created_date: 2026-10-19
  created_by: Identity Platform Team
  governed_by: [PAD-PLT-001, PAD-PLT-002]
---

# ADR-IAM-011: An Invitee Without an Account Enrols at Redemption, After Proving the Address

## 1. Title

An Invitee Without an Account Enrols at Redemption, After Proving the Address.

## 2. Status

| Date       | Status            | ADR Type     | Reviewers                 | Approver                       |
| ---------- | ----------------- | ------------ | ------------------------- | ------------------------------ |
| 2026-10-19 | proposed          | foundational | Architecture Review Board | Enterprise Architect — pending |
| 2026-10-20 | accepted          | foundational | Architecture Review Board | Enterprise Architect           |
| 2026-10-21 | accepted, amended | foundational | Architecture Review Board | Enterprise Architect           |

**Amended 2026-10-21, in place,** on one point: §5.7 settles the three points §5.1 left to
`TDD-organization-control-004`, which are how Organization Control recognises identity-control's
workload, the one answer for a token that resolves to nothing, and the read path. It is edited in
place because no system this decision governs is in production (GDC-010 §2.4.2): `SAD-001` §9.1
and `SAD-004` §10.3 record that the only deployment is the development server.

## 3. Context

`ADR-ORG-007` lets a Tenant administrator invite an email address, and lets the person who holds
that address accept, signed in. It leaves one case open (§5.7): the invited person has no account.

Today only a provider can create a Principal (`POST /v1/principals`, `ADR-IAM-010`). A Tenant
administrator cannot. So every invitation to someone new waits for a provider, and a Tenant cannot
onboard its own people.

Facts that bound the choice:

- **The realm has no self-registration.** `registrationAllowed` is false, and identity-control is
  the only creation path, so every kernel user carries a `principal_id`
  (`TDD-identity-kernel-001` §Closing Unauthorized Creation Paths, `TDD-identity-control-001`).
- **The kernel sends no mail** (`ADR-IAM-007 §5.4`). identity-control already proves an address
  with a one-time code it sends through the Notification Platform (`TDD-identity-control-008` §A
  Person's Own Addresses): 8 digits, 10 minutes, five attempts.
- **Invitation tokens are 256-bit, single-use and expire in 7 days** (`ADR-ORG-007 §5.4`), and in
  production the Notification Platform delivers them to the invited address (`ADR-ORG-007 §5.5`).
- **An address counts for an invitation only once proven** (`ADR-ORG-007 §5.3`).

## 4. Decision Drivers

- **Products let an invitee with no account create one from the invitation.**
  - GitHub: "If they don't have a GitHub account yet, they will be prompted to sign up for one and
    guided through the signup process" [R5].
  - Auth0: "the user will receive an email containing a link that will allow them to create an
    account or log in and join the organization" [R6].
  - Keycloak: "if no user is associated with the given email address, the steps will involve
    creating a new account through the realm's self-registration flow. In this case, the user is
    forced to provide the same email address used to send the invitation" [R8].
  - Okta: "Users who don't have a password must complete the welcome flow by visiting the
    activation link" [R9].
- **The account is bound to the invited address, proven.**
  - Auth0: "Invited users must log in or create an account with the email address to which the
    invitation was sent", and "When a user accepts an invitation, their email address will be
    marked as verified" [R6].
  - Entra B2B, for an invitee with no directory: "a passcode is sent to the user through the invited
    email"; "One-time passcodes are valid for 30 minutes" [R7].
  - NIST: "Confirmation codes are used to confirm that an applicant has access to a postal address,
    email address, or phone number"; at least 6 digits; at most "24 hours when sent to a validated
    email address"; invalidated "Upon its use" [R1].
- **The first credential is temporary.** ASVS 5.0 6.4.1: initial passwords "expire after a short
  period of time or after they are initially used. These initial secrets must not be permitted to
  become the long term password" [R2].
- **An anonymous route tells nothing.** OWASP: "Ensure the application returns consistent generic
  error messages" [R3], and tokens in a URL need protection "from brute-forcing … such as rate
  limiting" [R4].
- **One creation path, through identity-control,** and no open self-registration
  (`TDD-identity-control-001`, `TDD-identity-kernel-001`).

## 5. Decision

### 5.1 Enrolment Begins From a Pending Invitation

- **Where.** The acceptance page of `ADR-ORG-007 §5.6` offers a person who is not signed in **I do
  not have an account**. It hands the token, in the fragment, to Identity Experience's enrolment
  page.
- **The route.** Identity Experience's BFF calls a new, anonymous identity-control command,
  `POST /v1/enrolments`, with the token in the body.
- **What identity-control asks.** It asks Organization Control, as its workload, for the
  invitation the token names: a new route, `POST /v1/invitations/resolve`, which admits
  identity-control's workload alone. It answers the invitation's identifier and target address,
  and only for an invitation that is `pending` and not past its expiry. It names no Tenant.
- **One answer for every outcome.** The command always answers `202` with the same body: if the
  invitation can be redeemed, a code has been sent to the invited address. An unknown, expired,
  revoked or accepted token, and an address a Principal already holds proven, are not told apart
  [R3]. In that last case the message sent to the address says to sign in instead.

### 5.2 The Address Is Proven With a Code

- **The code.** identity-control draws 8 digits from the operating system's random source and
  sends them to the invited address alone, as `TDD-identity-control-008` sends an address proof. It
  keeps the code's SHA-256, sealed while it waits. It is good for 10 minutes and five attempts,
  within NIST's bounds [R1], and is invalidated on use.
- **The person returns it.** `POST /v1/enrolments/{enrolment_id}:verify` with the code. A wrong,
  expired or exhausted code creates nothing, and the person starts again from the link.
- **Limits.** One open enrolment per invitation. Requests are rate-limited per invitation and per
  client address. A run of refusals is a signal, beside the invitation lookup count
  (`ADR-ORG-007 §5.4`).

### 5.3 The Principal Is Created, With a Temporary Password Shown Once

On the right code, in one command:

- **The Principal is created through the ordinary path** (`TDD-identity-control-001`). Its
  username is the invited address, lower-cased, and its creation address is that address with
  `verified_at` set, because the code just proved it.
- **A temporary password is issued as `ADR-IAM-010 §5.1` and §5.2 issue it:** random, 120 bits,
  temporary in the kernel, `no-store`, never logged or stored, lapsing within 24 hours. It is shown
  once, to the person who returned the code, in that response.
- **Evidence.** The enrolment is recorded: the invitation, the address's hash, the Principal
  created and when. The first password binding is notified to the address (`ADR-IAM-007 §5.1`).
- **Nothing else is granted.** The new Principal holds no Membership.

### 5.4 Then the Person Accepts

The person signs in with the temporary password, chooses their own, and accepts as
`ADR-ORG-007 §5.1` decides. The proven address now matches (`ADR-ORG-007 §5.3`). Acceptance stays a
separate, signed-in, single-use command, so the enrolment's anonymous route never creates a
Membership.

### 5.5 Delivery

- **Production.** The code goes through the Notification Platform, as every proof does
  (`ADR-IAM-007`). It is a production gate.
- **A development server.** The code reaches the development mail catcher
  (`ADR-IAM-007 §5.3`, 2026-10-19), where the owner reads it.

### 5.6 What Each Repository Changes

| Repository              | Change                                                                                                                                                                                                                                                                   |
| :---------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| identity-control        | `TDD-identity-control-001`: enrolment as an authorized creation path, beside the ceremony and `POST /v1/principals`. `POST /v1/enrolments` and `:verify` (anonymous, rate-limited, one answer), the client of Organization Control's resolve route, the enrolment record |
| organization-control    | `TDD-organization-control-004`: `POST /v1/invitations/resolve`, identity-control's workload alone, answering only for a pending, unexpired invitation, with no Tenant name                                                                                               |
| identity-experience     | The enrolment page and its anonymous BFF routes: the code form, and the temporary password shown once with `no-store`                                                                                                                                                    |
| organization-experience | The acceptance page offers **I do not have an account** and hands the token to the enrolment page in the fragment                                                                                                                                                        |
| identity-kernel         | None. Registration stays disabled, and the kernel sends no mail                                                                                                                                                                                                          |
| scnehaux-architecture   | `STD-IAM-001 §3.1`: its exception (2.8.0) gains a second recipient, the person who has just proven the invited address, once this decision is accepted. SAD-001 lists the creation path                                                                                  |

### 5.7 How Organization Control Recognises, Answers and Reads for the Resolve Route (amended 2026-10-21)

`POST /v1/invitations/resolve` (§5.1) left three points to `TDD-organization-control-004` 1.16.0 and
organization-control ROADMAP item 56. They are decided here, so that the TDD and the code follow
one rule.

**(a) The caller is a registered workload, admitted from a record, for this route alone.** This
follows `ADR-ORG-001 §5.11`, which admits a registered reporter workload and no role from the token.

- **A registry row, not a scope and not a client identifier.** The reporter registry row of
  `ADR-ORG-001 §5.11` names a workload's `principal_id` and what it may do. It gains one entry,
  `invitation:resolve`. A token is the resolver's when its `subject_type` is `workload` and its
  `principal_id` is that of an active registered entry with that capability. No OAuth scope decides
  it (`STD-IAM-002 §3.2` keeps roles out of tokens), and no `client_id` does: a retired client's
  key is freed, and RFC 9068 warns that an authorization server "should prevent clients from
  registering an arbitrary client_id value, as this would allow malicious clients to select the sub
  of a high-privilege resource owner" [R12].
- **Not the consumer registration.** identity-control is also a registered projection consumer
  (`SAD-004` §7.6), and that admits it to the consumer routes. Resolving an invitation is another
  act, and a consumer admission that also resolved would let every consumer, `foundation-reference`
  included, read an invitation's address. AC-6 asks for "only authorized accesses ... that are
  necessary to accomplish assigned organizational tasks" [R11], so each route has its own entry.
- **Alone, per route.** An entry with `invitation:resolve` reaches this route and nothing else.
  Every other route answers that workload `403`, and every other caller answers `403` on this one.
- **Recorded.** Each call writes a privileged-access row as a reporter's report does, with the
  authority `reporter`, and its detail carries the registry entry's purpose, `invitation:resolve`.
  The authority alone would lose what was done: AU-3 asks that audit records "contain information
  that establishes the following", among it "What type of event occurred" [R14]. It names no Tenant, because a call that
  finds nothing names none and a call that finds an invitation must not differ. It is reviewed
  through the workload's owner (`ADR-ORG-001 §5.11`). The calls are bounded by identity-control's
  own limits per invitation and per client address (§5.2).
- **Development runs production's path.** identity-control registers as a workload with an owner
  (`ADR-IAM-003 §5.8`) and signs in with its own key; no development flag admits another caller.

**(b) One answer for a token that resolves to nothing: `404`, always the same.** An unknown,
expired, revoked or accepted token gets the same status, the same problem type and the same body,
and no field of it derives from the row. The lookup (`TDD-organization-control-004` §Acceptance, and
Enumeration Resistance) already renders every outcome identically, and WSTG-IDNT-04 asks that the
application return "consistent generic error messages" [R3]. `404` is the status HTTP defines for
it: the server "did not find a current representation for the target resource or is not willing to
disclose that one exists" [R10]. The route makes one lookup by the token's hash whatever the
outcome, so its duration does not separate the cases either. A malformed request body is a `400`
that says nothing about invitations. identity-control never forwards the `404`: its own answer is
the `202` of §5.1.

**(c) The read path is a scope of its own, which the database confines to one row.** The route reads
`invitation.invitation`, which is protected by row-level security, before any Tenant is known and
with no person signed in.

- **The scope.** `db.WithInvitationResolver(token_hash)` binds the hash of the token in the
  request, and a dedicated database role is the only role that reads the table through it. A
  `SELECT` policy on that role admits only the row whose `token_hash` equals the bound value and
  that is `pending` and not past its expiry. PostgreSQL shows a row only when the policy's
  expression "returns true", and "any rows for which the expression returns false or null will not
  be visible" [R13]. So the database, not the handler, makes the read return at most one row, and
  makes an absent, expired, revoked or accepted invitation the same empty result, which is what
  (b) needs. The role is granted the invitation's identifier and target address only, and the
  policy is declared by name in the service's posture check, as the other additional policies are.
- **Not the provider scope** (`db.WithProviderScope`): it needs a Tenant, an actor and recorded
  access, and a token is resolved before it has a Tenant. **Not the self scope**
  (`db.WithSelfInvitation`): it is the signed-in invitee's, and none exists yet. **Not an owning
  connection**: a table owner or a superuser bypasses row security by default
  (`STD-GLB-007` R4 quotes PostgreSQL on it).
- **Not a view over the pending invitations.** `STD-GLB-002` §Aggregate Reads Under Row-Level
  Security reads a view that "names no row". A view of pending invitations by token hash would let
  this role list every pending invitation's address across Tenants, which is wider than the task.
  **Not a `SECURITY DEFINER` function**, for the reason that section gives.

## 6. Consequences

### Positive

- A Tenant administrator can bring in someone new without a provider.
- Every new account is bound to an address its holder proved, and to an invitation an administrator
  issued. There is still no open registration.
- The kernel stays as it is: no registration flow, no mail, no extension.

### Negative

- **A second anonymous route,** on identity-control. It reads nothing without a valid invitation,
  answers the same in every case, and is rate-limited.
- **A Tenant administrator causes an account to be created,** but only the holder of the address
  can complete it, by returning the code.
- **It waits on delivery.** In production on the Notification Platform; on a development server on
  the mail catcher.
- **The person's username is their address.** A later change of address does not change it.

### Operational

- Enrolments, codes sent and refusals are counted. Many refusals for one invitation are alerted on.

## 7. Compliance Impact

### Related Standards

- [ADR-ORG-007](../organization-tenancy-platform/ADR-ORG-007-the-invited-person-accepts-signed-in.md):
  this decision closes its §5.7.
- [ADR-IAM-010](ADR-IAM-010-first-credential-for-an-administrator-created-person.md): the temporary
  password's rules.
- [ADR-IAM-007](ADR-IAM-007-account-security-notifications.md): the code's delivery, and the
  development mail catcher.
- `STD-IAM-001 §3.1`: its exception gains the enrolling person as a recipient, on acceptance.

### Compliance Status

Compliant once §5.6 is built and delivery is in production.

### Required Waivers

None, once `STD-IAM-001 §3.1` names the second recipient.

## 8. Alternatives Considered

### Alternative A — The Kernel's Self-Registration, From the Invitation

Keycloak's own pattern [R8].

**Rejected because:** it needs the realm's registration flow, which is closed; a user it creates
carries no `principal_id`, so the reconciler disables it; and Keycloak's invitation is sent by mail,
which the kernel does not send (`ADR-IAM-007 §5.4`).

### Alternative B — A Provider Creates Every Invitee (Today)

**Kept as the fallback, rejected as the only path because:** every person a Tenant onboards would
need a provider. `ADR-ORG-003 §6` accepts that cost for administrators alone ("Each Tenant's first
administrator needs a provider"), not for every member.

### Alternative C — Create the Principal When the Invitation Is Issued

Entra B2B does: "After you send the invitation, the user account is automatically added to the
directory as a guest" [R7].

**Rejected because:** it creates an account for an address nobody has proven, on a Tenant
administrator's request, and leaves it behind when the invitation lapses. Entra's own invitation
"doesn't expire" [R7]; this platform's do.

### Alternative D — The Person Chooses a Password on an Identity Control Page

**Rejected because:** identity-control would then process the person's lasting password, which
`STD-IAM-001 §3.1` gives to the kernel. A temporary value is replaced in the kernel at once.

## 9. References

### Normative

- **[R1]** NIST SP 800-63A-4, _Digital Identity Guidelines: Identity Proofing and Enrollment_,
  Requirements for Confirmation Codes, accessed 2026-10-19.
  <https://pages.nist.gov/800-63-4/sp800-63a.html#ConfirmCodes>. "Confirmation codes are used to
  confirm that an applicant has access to a postal address, email address, or phone number for the
  purposes of future communications."; "Confirmation codes used for these purposes SHALL include at
  least 6 decimal digits (or equivalent) from an approved random bit generator"; "Confirmation codes
  SHALL be valid for at most: … 24 hours when sent to a validated email address Upon its use, the
  CSP SHALL invalidate the confirmation code."
- **[R2]** OWASP, _Application Security Verification Standard 5.0.0_, 6.4.1, accessed 2026-10-19.
  <https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md>. "Verify that system
  generated initial passwords or activation codes are securely randomly generated, follow the
  existing password policy, and expire after a short period of time or after they are initially
  used. These initial secrets must not be permitted to become the long term password."
- **[R3]** OWASP, _Web Security Testing Guide_, WSTG-IDNT-04, accessed 2026-10-19.
  <https://github.com/OWASP/wstg/blob/master/document/4-Web_Application_Security_Testing/03-Identity_Management/04-Account_Enumeration_and_Guessable_User_Account.md>.
  "Ensure the application returns consistent generic error messages in response to invalid account
  name, password or other user credentials entered during the log in process."
- **[R4]** OWASP, _Forgot Password Cheat Sheet_, accessed 2026-10-19.
  <https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html>. "Implement
  appropriate protection to prevent users from brute-forcing tokens in the URL, such as rate
  limiting."

- **[R10]** IETF RFC 9110, _HTTP Semantics_, June 2022, §15.5.5 404 Not Found, accessed 2026-10-21.
  <https://www.rfc-editor.org/rfc/rfc9110>. "The 404 (Not Found) status code indicates that the
  origin server did not find a current representation for the target resource or is not willing to
  disclose that one exists."
- **[R11]** NIST SP 800-53 Rev. 5, AC-6 _Least Privilege_, from the OSCAL catalog, accessed 2026-10-21.
  <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>.
  "Employ the principle of least privilege, allowing only authorized accesses for users (or
  processes acting on behalf of users) that are necessary to accomplish assigned organizational
  tasks."
- **[R12]** IETF RFC 9068, _JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens_, October 2021,
  §5 Security Considerations, accessed 2026-10-21. <https://www.rfc-editor.org/rfc/rfc9068>. "the
  authorization server should prevent clients from registering an arbitrary client_id value, as this
  would allow malicious clients to select the sub of a high-privilege resource owner and confuse any
  authorization logic on the resource server relying on the "sub" value."

### Informative

- **[R5]** GitHub, _Invite members to your organization with an email address_ (GitHub blog, July
  26, 2016, updated January 4, 2019), accessed 2026-10-19.
  <https://github.blog/news-insights/product-news/invite-members-to-your-organization-with-an-email-address/>.
  "If they don't have a GitHub account yet, they will be prompted to sign up for one and guided
  through the signup process."
- **[R6]** Auth0, _Invite Organization Members_, accessed 2026-10-19.
  <https://auth0.com/docs/manage-users/organizations/configure-organizations/invite-members>. "If you
  would like to assign a member to an Organization, but the user does not yet exist in your data
  store … you can invite them to the organization. In this case, the user will receive an email
  containing a link that will allow them to create an account or log in and join the
  organization"; "Invited users must log in or create an account with the email address to which
  the invitation was sent."; "When a user accepts an invitation, their email address will be marked
  as verified."
- **[R7]** Microsoft, _Add B2B collaboration users_, _Microsoft Entra B2B collaboration invitation
  redemption_ and _Email one-time passcode authentication_, accessed 2026-10-19.
  <https://learn.microsoft.com/en-us/entra/external-id/add-users-administrator>,
  <https://learn.microsoft.com/en-us/entra/external-id/redemption-experience> and
  <https://learn.microsoft.com/en-us/entra/external-id/one-time-passcode>. "After you send the
  invitation, the user account is automatically added to the directory as a guest."; "An
  invitation of a user doesn't expire."; "If no home directory is found and the email one-time
  passcode feature is _enabled_ for guests, a passcode is sent to the user through the invited
  email."; "One-time passcodes are valid for 30 minutes."
- **[R8]** Keycloak, _Server Administration Guide_, Managing members, Inviting users, accessed
  2026-10-19. <https://www.keycloak.org/docs/latest/server_admin/index.html>. "if no user is
  associated with the given email address, the steps will involve creating a new account through
  the realm's self-registration flow. In this case, the user is forced to provide the same email
  address used to send the invitation."
- **[R9]** Okta, _Okta Admin Management API_ (OpenAPI specification), Activate a user, accessed
  2026-10-19.
  <https://github.com/okta/okta-management-openapi-spec/blob/master/dist/current/management-minimal.yaml>.
  "Users who don't have a password must complete the welcome flow by visiting the activation link
  to complete the transition to `ACTIVE` status."
- **[R14]** NIST SP 800-53 Rev. 5, AU-3 _Content of Audit Records_, from the OSCAL catalog, accessed
  2026-10-21.
  <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>.
  "Ensure that audit records contain information that establishes the following:"; "What type of
  event occurred;"
- **[R13]** PostgreSQL 17 Documentation, _CREATE POLICY_, accessed 2026-10-21.
  <https://www.postgresql.org/docs/17/sql-createpolicy.html>. "Rows for which the expression returns
  true will be visible. Any rows for which the expression returns false or null will not be visible
  to the user (in a SELECT), and will not be available for modification (in an UPDATE or DELETE)."
