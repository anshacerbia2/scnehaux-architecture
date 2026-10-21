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

**Amended 2026-10-21, in place, a second time,** on three points identity-control #117 stopped at:
§5.8 gives the limits §5.2 left open and says how the client address reaches identity-control, §5.9
decides an address held but not proven and a kernel username equal to the address, and §5.3 and
`STD-IAM-001` 3.1.0 now name the enrolling person as a second recipient of the temporary password.
Same evidence for editing in place as below.

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
- **The route.** Identity Experience's BFF calls a new identity-control command, anonymous as to the person (§5.8),
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
  client address, with the values and the address path of §5.8. A run of refusals is a signal, beside the invitation lookup count
  (`ADR-ORG-007 §5.4`).

### 5.3 The Principal Is Created, With a Temporary Password Shown Once

On the right code, in one command:

- **The Principal is created through the ordinary path** (`TDD-identity-control-001`). Its
  username is the invited address, lower-cased, and its creation address is that address with
  `verified_at` set, because the code just proved it.
- **A temporary password is issued as `ADR-IAM-010 §5.1` and §5.2 issue it:** random, 120 bits,
  temporary in the kernel, `no-store`, never logged or stored, lapsing within 24 hours. It is shown
  once, to the person who returned the code, in that response. `STD-IAM-001` 3.1.0 §3.1 names that
  person as the exception's second recipient (amended 2026-10-21), on the conditions below.
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
| scnehaux-architecture   | `STD-IAM-001 §3.1`: its exception (2.8.0) gains a second recipient, the person who has just proven the invited address, once this decision is accepted (written 2026-10-21, `STD-IAM-001` 3.1.0). SAD-001 lists the creation path                                        |

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

### 5.8 The Limits, and How the Client Address Reaches identity-control (amended 2026-10-21)

§5.2 asks for limits "per invitation and per client address" and gives no values. They are decided
here. The sources set a ceiling and name the techniques; none sets these values, so each is this
decision's choice, below the ceiling and conservative, and the first review of real traffic may
lower or raise it.

**What the sources say.** NIST SP 800-63B-4 §3.2.2: "the verifier SHALL limit consecutive failed
authentication attempts using a specific authenticator on a single subscriber account to no more
than 100", "The limit of 100 attempts is an upper bound, and agencies MAY impose lower limits" [R15].
It names waiting "after a failed attempt for a period of time that increases", "30 seconds up to an
hour" [R15]. OWASP, for the forgotten-password request, asks for "rate-limiting on a per-account
basis" because "an attacker could make thousands of password reset requests per hour for a given
account, flooding the user's intake system" [R17]. OWASP says a failed-login counter "should be
associated with the account itself, rather than the source IP address, in order to prevent an attacker
from making login attempts from a large number of different IP addresses" [R18], and that blocking by
IP address "should not be used as the sole or primary defense due to the ease in circumvention", with
"Short (i.e. burst) and long time periods" considered [R19].

**The limits.** Every count is kept in this service's own store, under a keyed hash of the invitation
identifier or of the address, and each is deleted when its window ends.

| What is counted                                    | Limit                             | At the limit                                                     |
| -------------------------------------------------- | --------------------------------- | ---------------------------------------------------------------- |
| Codes sent for one invitation                      | 3 in 1 hour, 5 in 24 hours        | `202` as always, and no code is sent                             |
| Failed `:verify` attempts for one invitation       | 5 per code (§5.2), 15 in 24 hours | The same refusal as a wrong code, until the 24 hours have passed |
| Requests to `POST /v1/enrolments` from one address | 5 in 1 minute, 20 in 1 hour       | `429` with `Retry-After`                                         |
| Requests to `:verify` from one address             | 5 in 1 minute, 30 in 1 hour       | `429` with `Retry-After`                                         |

- **Why per invitation is silent and per address is not.** A per-invitation limit that answered
  differently would tell the caller that the token names an invitation, which is the oracle of §5.1
  [R3]. So it answers as always and does nothing. A per-address count includes every request, whatever
  the token, so a `429` tells nothing about any invitation. The per-address count is read before
  Organization Control is asked, so it also bounds that route's calls (§5.7).
- **Why the per-invitation limit cannot be used against a person.** Every call needs the invitation's
  token, so only a holder of the token can reach it. OWASP's warning that "care must be taken to
  prevent it from being used to cause a denial of service by locking out other users' accounts" does
  not arise for an outsider [R18]. The lockout lasts 24 hours
  and is not permanent.
- **Why 15 and not 100.** One invitation allows 15 guesses against 10^8 eight-digit codes in 24 hours,
  where NIST's ceiling of 100 attempts is set for a six-digit code [R15].
- **The address windows are shared-egress aware.** A company's people may leave through one address,
  so the hourly figures are above one person's need. The burst figure, 5 a minute, is the one that
  stops a script. OWASP says a mitigation must "not rely on a single predictable volume limit" [R19], so the address limit is one layer beside the
  per-invitation limit and the code's own bounds, not the only defence.
- **IPv6.** The address is counted as its /64 prefix, so a person with a /64 cannot take a fresh
  address per request. No source gives the prefix length; it is the conservative choice.
- **Options.** (1) Per invitation only: it leaves a script free to spray the route with guessed
  tokens, and rejected. (2) Per address only: it lets one token holder flood an address with codes
  from many addresses, and OWASP's per-account rule [R17] rejects it. (3) Both, as above. Chosen.

**The client address reaches identity-control from the BFF, which presents its own credentials.**
The route stays anonymous as to the person: no one is signed in. It is not anonymous as to the caller.

- **The address the platform's own ingress saw.** The ingress overwrites any forwarding header a
  client sent with the address of the TCP connection it accepted, and the BFF trusts exactly that one
  hop and no chain behind it. RFC 7239 says the header "cannot be relied upon to be correct, as it
  may be modified, whether mistakenly or for malicious reasons, by every node on the way to the
  server, including the client making the request", and that "the chain of IP addresses listed before
  the request came to the proxy cannot be trusted" [R16]. A BFF that trusts a header a browser can set
  gives the attacker the limit's key. A BFF with `trustProxy: false`, as today, sees only the ingress
  and cannot supply the address at all.
- **It is forwarded in `Forwarded: for=<address>`.** The BFF calls the two enrolment routes as a
  registered workload with an owner (`ADR-IAM-003 §5.8`), with its own client key. identity-control
  admits it from a record naming its `principal_id`, as `ADR-ORG-001 §5.11` admits a reporter, for
  these two routes alone, and reads `Forwarded` only on a call carrying that workload's token. On any
  other call the header is ignored. RFC 7239 defines the parameter: "The "for" parameter is used to
  disclose information about the client that initiated the request", and a server that "requires some
  address-based functionality" may receive "an IP address" [R16]. Only the first element's `for` is
  read.
- **Missing or malformed from the trusted workload: `400`.** The count has no key, and one shared
  bucket would stop everyone. The status depends on nothing about the token, so it is no oracle.
- **The address is kept no longer than its window.** RFC 7239 says identifiers that persist
  "SHOULD NOT persist longer than client IP addresses" and treats the address as "privacy sensitive"
  [R16]. The count holds a keyed hash and no address, and is deleted at the window's end. The address
  is never logged with the token.
- **Options.** (1) Trust `X-Forwarded-For` at identity-control: any caller could set it, and
  rejected. (2) Use the connection's source address at identity-control: it is the BFF's, so every
  person shares one count, and rejected. (3) The BFF forwards, authenticated, as above. Chosen.
  (4) The browser calls identity-control directly: it would give the route a CORS and cookie surface
  `ADR-IAM-009` and the BFF pattern exist to avoid, and rejected.

### 5.9 An Address Held but Not Proven, and a Username That Equals the Address (amended 2026-10-21)

§5.1 and §5.3 name one collision, an address a Principal already holds proven. Two more exist. The
realm has `duplicateEmailsAllowed: false`, so the kernel would refuse the new user at `:verify`, and
the command would be left with a mapping that recovery cannot complete.

- **An address a Principal holds but has not proven** (a provider-created Principal's creation
  address with no `verified_at`). **An existing kernel user whose username equals the address**, with
  or without a Principal, such as a user whose mapping is pending or an orphan.
- **Decision: the same as the proven case, in every observable way.** No code is sent, no Principal
  is created, nothing is adopted, and the request answers the `202` of §5.1. The message sent to the
  address says that an account exists for it and how to continue: sign in, confirm the address in the
  account's settings, or ask the person who invited them. It does not say whether the address was
  proven. The message reaches only the holder of the mailbox.
- **Why not adopt it.** A code proves access to a mailbox: NIST says a confirmation code is used "to
  confirm that an applicant has access to a postal address, email address, or phone number" [R1].
  It does not prove the account is theirs. An unproven Principal may already hold a Membership or a
  provider's grant, and adopting it on the code would hand them to whoever reads that mailbox first.
  OWASP says: "Do not automatically link accounts solely because their email, preferred_username,
  or other profile attributes match" [R18]. Adopting an orphan or a pending mapping stays recovery's
  (`TDD-identity-control-001`), by a provider.
- **Why not say so.** "This user ID is already in use." is OWASP's incorrect account-creation
  response; the correct one is "A link to activate your account has been emailed to the address
  provided." [R18]. WSTG-IDNT-04: "the application should respond with the same error message and
  length to the different incorrect requests" [R3]. The response is one body and one status, and the
  work is the same: OWASP asks that "responses return in a consistent amount of time" by "making
  sure that the same logic is followed, instead of using a quick exit method" [R17], so the message
  is sent through the same queue in every case.
- **The check is made twice.** At the request, against this service's Principals (creation address
  and username) and against the kernel user by exact username. At `:verify`, immediately before the
  create, because a provider may have created the Principal in between. A collision at `:verify`
  creates nothing, consumes the enrolment, and answers as a wrong code does. If the kernel still
  refuses the create as a duplicate, the command treats it as that collision and leaves no mapping
  for recovery to finish; the TDD says how the write is ordered.
- **Options.** (1) Create anyway: the kernel refuses it, and rejected. (2) Adopt the held Principal on
  the code: takeover of a held identifier, and rejected. (3) Say "an account exists": an oracle,
  and rejected. (4) The same answer, and a message to the address. Chosen.

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
- `STD-IAM-001` 3.1.0 §3.1: its exception names the enrolling person as a second recipient (written 2026-10-21). The version is minor: it relaxes one exception under conditions and adds no mandatory restriction to anything that conforms, so GDC-007 §2.4.2 does not ask for an authorizing ADR.

### Compliance Status

Compliant once §5.6 is built and delivery is in production.

### Required Waivers

None. `STD-IAM-001` 3.1.0 §3.1 names the second recipient.

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

- **[R15]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator Management_, §3.2.2 Rate Limiting (Throttling) and Binding at Enrollment, accessed 2026-10-21. <https://pages.nist.gov/800-63-4/sp800-63b.html>. "the verifier SHALL limit consecutive failed authentication attempts using a specific authenticator on a single subscriber account to no more than 100 by disabling that authenticator."; "The limit of 100 attempts is an upper bound, and agencies MAY impose lower limits."; "Requiring the claimant to wait after a failed attempt for a period of time that increases as the subscriber account approaches its maximum allowance for consecutive failed attempts (e.g., 30 seconds up to an hour)"; "Binding at the time of enrollment is considered to be part of the enrollment process and is discussed in [SP800-63A]."
- **[R16]** IETF RFC 7239, _Forwarded HTTP Extension_, June 2014, §4, §8.1 and §8.3, accessed 2026-10-21. <https://www.rfc-editor.org/rfc/rfc7239>. §8.1: "The "Forwarded" HTTP header field cannot be relied upon to be correct, as it may be modified, whether mistakenly or for malicious reasons, by every node on the way to the server, including the client making the request."; "First, the chain of IP addresses listed before the request came to the proxy cannot be trusted." §4: "The "for" parameter is used to disclose information about the client that initiated the request and subsequent proxies in a chain of proxies."; "If the server receiving proxied requests requires some address-based functionality, this parameter MAY instead contain an IP address". §8.3: "The client's IP address, that may be forwarded in the "for" parameter of this header field, is considered to be privacy sensitive by many people"; "If identifiers that persist across requests are required, their lifetimes SHOULD be limited and they SHOULD NOT persist longer than client IP addresses."

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
- **[R17]** OWASP, _Forgot Password Cheat Sheet_, §Forgot Password Request, accessed 2026-10-21. <https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html>. "Return a consistent message for both existent and non-existent accounts."; "Ensure that responses return in a consistent amount of time to prevent an attacker enumerating which accounts exist. This could be achieved by using asynchronous calls or by making sure that the same logic is followed, instead of using a quick exit method."; "Implement protections against excessive automated submissions such as rate-limiting on a per-account basis, requiring a CAPTCHA, or other controls. Otherwise an attacker could make thousands of password reset requests per hour for a given account, flooding the user's intake system (e.g., email inbox or SMS) with useless requests."
- **[R18]** OWASP, _Authentication Cheat Sheet_, §Authentication Responses, §Account Lockout and §Secure Federated Account Linking, accessed 2026-10-21. <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>. Account creation, incorrect: "This user ID is already in use."; correct: "A link to activate your account has been emailed to the address provided." Lockout: "The counter of failed logins should be associated with the account itself, rather than the source IP address, in order to prevent an attacker from making login attempts from a large number of different IP addresses."; "care must be taken to prevent it from being used to cause a denial of service by locking out other users' accounts." Linking: "Do not automatically link accounts solely because their email, preferred_username, or other profile attributes match."
- **[R19]** OWASP, _Credential Stuffing Prevention Cheat Sheet_, §IP Mitigation and Intelligence, accessed 2026-10-21. <https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html>. "Blocking IP addresses may be sufficient to stop less sophisticated attacks, but should not be used as the sole or primary defense due to the ease in circumvention."; "not rely on a single predictable volume limit. Short (i.e. burst) and long time periods should be considered".
