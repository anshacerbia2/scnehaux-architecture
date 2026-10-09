---
doc_meta:
  id: ADR-IAM-003
  title: Client Registration Ownership and the Developer Console's Authority
  adr_type: foundational
  status: accepted
  created: 2026-10-01
  created_date: 2026-10-01
  created_by: Identity Platform Team
---

# ADR-IAM-003: Client Registration Ownership and the Developer Console's Authority

## 1. Title

Client Registration Ownership and the Developer Console's Authority.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

The Identity Control Service registers every protocol client and protected resource, holds their public keys, and reconciles them against the identity kernel (`ADR-IAM-001 §5.12`, `§5.13`). Every one of its routes requires a provider-scope token naming `provider:identity-control` (`STD-IAM-002 §3.1.1`), so only a provider can register a client, rotate its key or change its redirect URIs.

`SAD-002` gives application teams a Developer Console for that work, and `TDD-identity-experience-004` designs it: registration, redirect URIs, audiences, the lifetime class, and the client's key rotation, with approval required for a production client. Nothing decides which team may act on which registration. Until something does, the console could only be used by providers, and an application team rotating its own key waits on an operator, which is how keys reach their expiry.

Three facts bound the choice:

- The Identity Control Service is the registration authority, and the kernel is not to become a second one (`ADR-IAM-001 §5.6`, `§5.7`).
- A token carries no role (`STD-IAM-002 §3.2`), and the resource that holds a grant checks its own record (`STD-IAM-002 §3.1.1`, `ADR-ORG-001 §5.11`).
- The Software Catalog, which would say which team owns which Application, is unchartered. A registration's `application_ref` is entered administratively and proves nothing about who owns it.

## 4. Decision Drivers

- **Least privilege.** A team manages its own clients and nothing else [R2].
- **Separation of duties.** The person who proposes a change to a production client's trust configuration does not also approve it [R1].
- **Bounded, attributable authority.** Every grant names a Principal, a target, who granted it and why, and ends when the person does [R3].
- **No new kernel authority and no role in a token.**
- **A path to grouping.** When the Software Catalog exists, ownership moves to the Application without redesign.

## 5. Decision

### 5.1 A Registration Has Owners

The Identity Control Service records the owners of each registration: active human Principals, each granted by a provider with a reason, in an insert-only history that names who granted and who revoked. This is the model Microsoft Entra uses, where owners assigned to an application can manage that application and only that one [R4][R5], and the one Okta reaches with an administrator role constrained to a set of applications [R6].

- **An owner is a person.** A workload, and a Principal that is not active, holds no ownership.
- **Ownership ends with the person.** A Principal retired, quarantined or disabled confers nothing from the next request, and its ownerships are reported for reassignment.
- **A production registration keeps at least two owners**, so one departure does not orphan it. Removing the second-to-last owner of a production registration is refused.
- **Ownership is reviewed at least quarterly** by the owners, as account reviews are required at a defined frequency [R3]. A registration with no active owner is reported.

### 5.2 What an Owner May Do

| Action                                                                                     | Owner                                          | Provider                                       |
| :----------------------------------------------------------------------------------------- | :--------------------------------------------- | :--------------------------------------------- |
| Read the registration, its keys and its findings                                           | yes                                            | yes                                            |
| Rotate to a new public key; revoke a key                                                   | yes                                            | yes                                            |
| Suspend the client, which is reversible                                                    | yes                                            | yes                                            |
| Restore a suspended client                                                                 | yes                                            | yes                                            |
| Propose a redirect URI, audience, lifetime-class or back-channel logout URI change (§5.10) | yes                                            | yes                                            |
| Apply that change to a non-production registration                                         | yes                                            | yes                                            |
| Apply that change to a production registration                                             | approved by a provider other than the proposer | approved by a provider other than the proposer |
| Change the profile or audience class; retire; adopt; grant or revoke ownership             | no                                             | yes                                            |

Key rotation needs no approval. It is the operation the console exists to make routine, it changes no trust relationship, and a rotation that waits for someone is a rotation that waits until the key expires. Suspension is offered to owners because a team that finds its key leaked contains the client first and asks afterwards. Retirement, which deletes the client, stays a provider's.

**A production change is a proposal until a second person approves it** [R1]. The proposal records the configuration, the proposer, the reason and the validated preview, and the approver sees the same preview. A provider proposing a production change does not approve their own. Whether a deployment is production is the deployment's setting, not the request's.

### 5.3 Creating a Registration

A provider grants a Principal **application developer** standing, with a reason, as Entra's Application Developer role grants the ability to create registrations once self-service is restricted [R4]. Such a Principal creates non-production registrations and becomes their first owner. An application developer's production registration is created only by approval: the developer proposes it, naming at least two owners, and a provider other than the proposer approves it.

**A provider creates a registration directly**, in production too, as Entra's Application Administrator "can create and manage all aspects of … application registrations" [R4]. The role carries no approval of its own; Entra adds a second person, where an organization wants one, when the role is activated (§5.7) [R8]. A provider is already the privileged administrator of the registration authority, and its direct creation is recorded under its `principal_id`. A provider's direct creation in production is reported each time, so a review sees every one. §5.7 records where two-person control over providers belongs instead.

### 5.4 Where Authority Is Checked, and the Token

The Identity Control Service holds ownership and application-developer grants and reads them for each request, by the token's `principal_id` and the registration the request names, as Organization Control reads its provider grants (`ADR-ORG-001 §5.11`). Nothing is projected into the kernel, and no claim or role names an owner.

The token is the `privileged` class in a third form, `STD-IAM-002 §3.1.1`'s **`resource-scoped`** form: `principal_id`, `subject_type` `human`, `acr` and `auth_time`, no `tenant_id`, and an authority the resource looks up rather than reads. A token that also carries `provider_scope` naming `provider:identity-control` is a provider's, and is served as one.

**The two authorities are separated by route, not by trust in the caller.** A route a provider alone may call refuses an owner token before any record is read, and an owner route reads the ownership of the registration it names, never of one the body names. Organization Control learned this when a consumer token that added a reason header reached its provider routes, before each route checked the caller's authority (organization-control ROADMAP item 17a).

### 5.5 Not the Kernel's Fine-Grained Permissions

Keycloak can grant an administrator permission over individual clients [R7]. That would put the ownership decision in the kernel, where the Identity Control Service does not record it, and send owners to the Admin Console, which `ADR-IAM-001 §5.7` keeps away from controller-owned configuration. Ownership is a registration fact and lives with the registration.

### 5.6 From Registration to Application

When the Software Catalog exists and says which team owns an Application, ownership moves from the registration to the Application: every registration of the Application has the Application's owners. The rules above do not change, only the scope of a grant, as an Entra custom role is assigned to one application or to all of them [R4].

### 5.7 Two-Person Control Over Providers Belongs at Activation

Requiring a second provider to approve each of a provider's registrations is not how the established platforms constrain their own administrators. Entra puts the second person at the moment administrative authority is activated: Privileged Identity Management can "require approval for activation of an eligible assignment", recommending "at least two approvers" [R8], after which the administrator acts without approval per action. NIST SP 800-53 AC-5 asks an organization to identify the duties it separates and to define access authorizations that support the separation [R1]. It does not ask for every privileged action to be approved by a second person.

So provider authority, not each registration, is where two-person control is added: a provider grant that is eligible rather than standing, activated for a bounded time with another provider's approval. That changes how Organization Control and the Identity Control Service hold provider authority (`ADR-ORG-001 §5.11`), and `ADR-ORG-002` decides it. A provider grant becomes eligible, and it is activated for a bounded time with another provider's approval. Until that is built, providers are few, every grant is recorded with its reason, and a provider's direct production registration is reported.

### 5.8 A Workload's Owner Reads What It Reviews

A workload names one accountable owner, an active human Principal, on the workload itself and in its token as `workload_owner` (`STD-IAM-001 §3.7`). That owner attests at least quarterly that the workload is still needed, that its purpose holds, and that its owner and team are right. NIST SP 800-53 AC-2(j) requires accounts to be reviewed at a defined frequency [R3]. The owner could make that attestation through the Identity Control API but could not read the workload: every workload read was a provider's. So an owner who was not a provider attested to a record it could not see, and the Developer Console offered no review. This section gives the Developer Console the workload owner's authority, by the rules §5.1 and §5.4 set for a registration's owners.

- **The owner lists the workloads it owns and reads each one.** Each shows its state, purpose, team, last authentication, last review, and the date the next review is due. AC-2(j) leaves the frequency to the organization [R3]. Showing the due date lets an owner review on time, before the sweep reports the review overdue. Google Cloud advises managing a service account with "the same processes, same lifecycle, and same diligence" as the resource it belongs to, "and use the same tools to manage them" [R11]. So the Developer Console shows a person's workloads beside the registrations they own, and the owner reviews an active workload there.
- **The owner is the workload's recorded owner, counted only while its mapping is an active human one**, as §5.1 counts a registration's owners. A retired, quarantined or suspended owner confers nothing from the next request, and the next workload sweep orphans the workload. No registration owner is granted on a workload's client. A second ownership record for one workload could name a different person from the one its token names.
- **A workload the caller does not own is not found.** The route reads the owner of the workload its path names, never one the body names, and answers 404 for any other workload. That is the same answer as for a workload that does not exist. OWASP API1:2023 asks every endpoint that receives an object's identifier to "validate that the logged-in user has permissions to perform the requested action on the requested object" [R9]. RFC 9110 lets an origin server that "wishes to 'hide' the current existence of a forbidden target resource" answer 404 instead of 403 [R10]. A 403 would tell anyone holding an account which workload identifiers exist. Entra's application owners likewise "can manage only the enterprise applications they own" [R5]. Access is enforced at the resource, as AC-3 asks [R12], and no more than the review needs is granted, as AC-6 asks [R2].
- **Everything else stays a provider's**, at `aal2` (`ADR-IAM-004`): reading a workload one does not own, reassigning, suspending, restoring, retiring and rebuilding. Each of these changes who answers for a running workload or stops it. An owner who finds that a workload is no longer needed, or that its owner or team is wrong, asks a provider, who acts with a reason. A provider who owns a workload sees it in the console's list like any owner. Opening one of its workloads is a provider read, so that provider steps up to `aal2` first.

### 5.9 A Resource's Lifetime Class Changes as a Registration Change

§5.2 lets an owner propose a lifetime-class change. The class is a resource's, and a client's access token lifespan is derived from the shortest class among the resources its audience names (`STD-IAM-002 §3.3`). So one change to a resource moves the lifespan of every client that calls it, and with it the delay before a revocation reaches that resource.

- **It takes the route of the other changes.** An owner of the resource or a provider proposes the next class with a reason, against the version it read. Outside production it applies at once. In production a provider other than the proposer approves it, shortening and lengthening alike. A shorter class takes access away sooner and a longer one leaves it longer, and both change what every caller's tokens do.
- **The proposal names a class, never a number.** The four classes and their figures are the standard's, and a lifetime "MUST NOT be configured per client" (`STD-IAM-002 §3.3`). Entra splits the same way: defining a token lifetime policy needs `Policy.ReadWrite.ApplicationConfiguration`, an administrator's permission, while assigning one to an application needs only `Application.ReadWrite.OwnedBy` and `Policy.Read.All` [R14]. Okta sets the lifetime per API, on its authorization server's access policy, and gives the reason: "an access token for a banking API may include a transactions:read scope with a multi-hour token lifetime. By contrast, the lifetime of an access token for transferring funds should be only a matter of minutes" [R15]. The resource's owners know which of those it is.
- **The change states the delay it sets.** Each class shows its access token lifetime and its revocation target, so a proposer and an approver see the increase that `STD-IAM-002 §3.3` requires "into the stated maximum enforcement delay". Microsoft states the trade the number makes: "Adjusting the lifetime of an access token is a trade-off between improving system performance and increasing the amount of time that the client retains access after the user's account is disabled" [R13].
- **The apply moves every caller with it.** The resource's class and version are written, then the lifespan of every client whose audience names the resource, under the clients' row locks, before the commit. A kernel that refuses rolls the change back and puts back the lifespans already written, as an audience change rolls back (`TDD-identity-control-003` §Registration Changes).

The class bounds more than revocation. An access token outlives the session that issued it: NIST SP 800-63B-4 has a session terminated "When either timeout expires" [R16], and AC-12 terminates one after "[Assignment: organization-defined conditions or trigger events requiring session disconnect]" [R17], but a token already issued is accepted until it expires. RFC 9700 values a short lifetime because it reduces "the potential impact of access token leakage" [R18]. A longer class is therefore a security decision of the resource's, and is held to the second person a production trust change gets.

### 5.10 A Confidential Client's Back-Channel Logout URI Changes as a Registration Change (2026-10-09)

`ADR-IAM-009 §5.1` lets a `confidential` client register a `backchannel_logout_uri`. Until this amendment no change wrote it after registration, so a wrong or moved URI was corrected only by retiring the registration and registering the client again. It is now a fourth change kind beside the redirect URIs, the audience and the lifetime class, set, moved or removed.

- **It is trust configuration, as a redirect URI is.** The URI is where the kernel sends a logout token, and the token names the person and, with "session required" on, the session: the registration parameter `backchannel_logout_session_required` asks "that a sid (session ID) Claim be included in the Logout Token to identify the RP session with the OP" [R19]. A URI moved to an endpoint the client's owners do not run sends that to someone else. A URI removed leaves every session removal to reach the client only at its next refresh (`ADR-IAM-009 §5.3`).
- **It takes the route of the other changes.** An owner of the registration or a provider proposes the whole new value with a reason, against the version it read. Outside production it applies at once. In production a provider other than the proposer approves it [R1]. "Session required" is not part of the change: every client the Identity Control Service writes holds it on.
- **It validates as registration does.** Only an active `confidential` client. The URI "MUST be an absolute URI" and "MUST NOT include a fragment component" [R19], has no credentials or wildcard, and is `https` in production (`ADR-IAM-009 §5.1`). Moving to the registered URI, or removing one that is not registered, is refused.
- **The kernel is written before the commit, and the sweep confirms first.** The apply writes the URI under the registration's row lock, then the kernel client's back-channel logout URL with front-channel logout off, and rolls back on a kernel failure. The drift sweep reads a differing URI again under the registration's share lock before it repairs it, so a sweep between the kernel write and the commit does not put the old URI back.
- **A logout already sent is not repeated.** The kernel "should not retransmit a Back-Channel Logout Request unless the OP suspects that previous transmissions may have failed due to potentially recoverable errors" [R19]. A session removed during the change is told to whichever URI the client held at that instant, and the next one goes to the new URI.

## 6. Consequences

### Positive

- An application team rotates, revokes and contains its own client without an operator.
- Every production trust change has two people on record.
- Ownership is a record with a history, ending with the person, rather than a role in a token or a permission in the kernel.
- A workload's owner sees what it attests to, and when the next attestation is due, without an operator (§5.8).

### Negative

- The Identity Control Service accepts two forms of privileged token, and its routes must keep them apart.
- Owners and proposals are new tables, routes and review work.
- Until the Software Catalog exists, ownership is granted registration by registration.
- A single provider can register a production client alone, and Entra notes that an application administrator can add credentials to an application and use them to impersonate it [R4]. A compromised provider account is therefore a production client takeover until two-person control at activation (§5.7) exists. Reporting every direct production registration makes it visible, not prevented.
- A workload's owner cannot contain its workload (§5.8). A registration's owner suspends a client whose key leaked, but a workload's owner can only ask a provider to suspend it, because the workload's client has no registration owners. Until a decision gives the workload owner containment, a leaked workload key stays usable until a provider acts.
- A compromised owner account can read the owner's workloads and record a false review. Neither stops a workload or changes its access. The review is recorded with who gave it, and an owner whose account is retired, quarantined or suspended confers nothing from the next request.
- Outside production, a client's owner moves its back-channel logout URI alone (§5.10). A URI moved to the wrong endpoint sends that client's logout tokens there until it is corrected, and the change is recorded with who proposed it.
- A lifetime-class change moves the token lifespan of callers whose owners did not propose it (§5.9). In production a provider approves it; outside production a resource's owner moves its callers alone. The approver sees the two classes and their revocation targets, not the list of callers, which no route lists yet.

### Operational

- Registrations without an active owner, ownerships held by an inactive Principal, and overdue reviews are reported.
- Proposals waiting for approval past a threshold are reported.
- Every production registration a provider creates directly is reported, with the provider and the client.

## 7. Compliance Impact

### Related Standards

- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.6, §5.7, §5.12, §5.13 — the registration authority, no kernel authority, keys, and the lifecycle.
- STD-IAM-002 §3.1.1 — the `resource-scoped` privileged form.
- [ADR-ORG-001](../organization-tenancy-platform/ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) §5.11 — a resource checks the grants it holds.
- SAD-002 — the Developer Console.
- STD-IAM-001 §3.7 — a workload's explicit owner.
- [ADR-IAM-009](ADR-IAM-009-logout-by-the-back-channel.md) §5.1, §5.3 — the back-channel logout URI that §5.10 changes. `TDD-identity-control-003` 1.38.0 implements §5.10.

### Compliance Status

Compliant. `STD-IAM-002 §3.1.1` gains the `resource-scoped` form in the same change.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Owners per Application

**Benefits:** one owner list for every client of an Application, which is how teams think.

**Rejected for now because:** `application_ref` is entered administratively and the Software Catalog that would make it trustworthy is unchartered, so an Application-scoped grant would hang on a string anyone registering a client could type. §5.6 adopts it once the catalog exists.

### Alternative B — Developer Authority from Organization Membership

**Benefits:** reuses Organization's roles and its lifecycle.

**Rejected because:** a client registration belongs to the platform, not to a Tenant, so a Tenant role is the wrong boundary, and Organization holds no fact about who owns a client.

### Alternative C — The Kernel's Fine-Grained Admin Permissions

**Benefits:** supported by the pinned kernel [R7], with nothing to build.

**Rejected because:** of §5.5. The decision would live where the registration authority does not record it, and owners would work in the Admin Console.

### Alternative D — Providers Only

**Benefits:** the status quo; one authority.

**Rejected because:** every key rotation waits on an operator, and the Developer Console has no user it can serve.

### Alternative E — Every Production Registration by Approval, a Provider's Too

**Benefits:** no single person creates a production client; separation of duties at the level of each registration.

**Rejected because:** it is not how the platforms the decision follows constrain their administrators. Entra's Application Administrator creates registrations directly [R4], and its two-person control is approval at role activation [R8]. Per-registration approval would also route every workload and every adoption through a second person, so a deployment that registers a client waits on one, and a lone operator during an incident cannot register a replacement client. §5.7 places the control at activation instead, where it constrains everything a provider does, not only registration.

### Alternative F — The Review Stays Where Only a Provider Can Read (§5.8)

**Benefits:** nothing to build. A provider who owns a workload already reviews it in the Admin Portal.

**Rejected because:** an owner who is not a provider could not read what it attested to. The review would either not happen or become a provider's work. AC-2(j) asks for the review [R3], and CIS 5.5 asks the owner, the purpose and the review date to be kept for each service account (`STD-IAM-001` [R19]). An attestation made without the record is a signature, not a review.

### Alternative G — Registration Owners on the Workload's Client (§5.8)

**Benefits:** the owner routes of §5.2 would serve the workload's client unchanged, with key rotation and suspension included.

**Rejected because:** a workload has one accountable owner, carried in its token as `workload_owner`. A second record, granted and revoked separately, could name someone else. A reassignment would then have to move both records, or leave the token naming one owner and the console another. The registration lifecycle also refuses a workload's client, which is stopped through its workload (`ADR-IAM-001 §5.13`).

### Alternative H — Answer 403 for a Workload the Caller Does Not Own (§5.8)

**Benefits:** a person who mistypes an identifier is told it is not theirs rather than that it does not exist.

**Rejected because:** a 403 tells anyone with an account which workload identifiers exist, which is the disclosure OWASP API1:2023 describes [R9]. RFC 9110 lets a server answer 404 to hide that a resource exists [R10], and §5.4 already answers an owner 404 for a registration it does not own.

### Alternative I — The Lifetime Class Fixed at Registration (§5.9)

**Benefits:** nothing to build; a class chosen once cannot be weakened later.

**Rejected because:** the only way to change it would be to retire the resource and register it again. Retirement deletes the kernel client and takes the resource out of every caller's audience, so correcting a class chosen too long would be an outage for every caller, and the correction would wait.

### Alternative J — A Provider's Change Only (§5.9)

**Benefits:** a person outside the team decides every lifetime.

**Rejected because:** the resource's owners know whether it moves funds or reads a catalogue [R15], and Entra lets an owner assign an administrator-defined lifetime policy [R14]. In production a provider already approves the change, so a provider-only change would add no second person, only take the proposal away from the team.

### Alternative K — A Lifetime per Client (§5.9)

**Benefits:** one caller could get a shorter lifetime without moving the others.

**Rejected because:** `STD-IAM-002 §3.3` forbids configuring a lifetime per client. The derived lifespan already gives each caller the shortest class among its resources.

### Alternative L — Correct a Back-Channel Logout URI by Retiring and Registering Again (§5.10)

**Benefits:** nothing to build; the URI is fixed for the life of the registration.

**Rejected because:** retirement deletes the kernel client, so a moved endpoint would cost the client its sessions, keys and audience for the time a new registration takes. A trust change of the same weight as a redirect URI already has a governed route, with a second person in production [R1].

## 9. References

### Normative

- **[R1]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and Organizations_, AC-5 Separation of Duties. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. Divide functions among different individuals or roles to reduce the risk of abuse of authorized privilege: "Identify and document [organization-defined duties of individuals]" and "Define system access authorizations to support separation of duties".
- **[R2]** NIST SP 800-53 Rev. 5, AC-6 Least Privilege. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Employ the principle of least privilege, allowing only authorized accesses for users (or processes acting on behalf of users) that are necessary to accomplish assigned organizational tasks." Quoted from NIST's OSCAL catalog, release 5.2.0, <https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>, accessed 2026-10-08.
- **[R3]** NIST SP 800-53 Rev. 5, AC-2 Account Management, (j) review at a defined frequency. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "j. Review accounts for compliance with account management requirements [Assignment: organization-defined frequency]". Quoted from NIST's OSCAL catalog, release 5.2.0, accessed 2026-10-08.
- **[R12]** NIST SP 800-53 Rev. 5, AC-3 Access Enforcement. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Enforce approved authorizations for logical access to information and system resources in accordance with applicable access control policies." Quoted from NIST's OSCAL catalog, release 5.2.0, accessed 2026-10-08.

- **[R16]** NIST SP 800-63B-4, _Digital Identity Guidelines: Authentication and Authenticator Management_, August 2025, §5.2 Reauthentication. <https://pages.nist.gov/800-63-4/sp800-63b.html>, accessed 2026-10-08. "An overall timeout limits the duration of an authenticated session to a specific period following authentication or a previous reauthentication. An inactivity timeout terminates a session without activity from the subscriber for a specific period"; "When either timeout expires, the session SHALL be terminated."
- **[R17]** NIST SP 800-53 Rev. 5, AC-12 Session Termination. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Automatically terminate a user session after [Assignment: organization-defined conditions or trigger events requiring session disconnect]." The discussion names among those conditions "targeted responses to certain types of incidents". Quoted from NIST's OSCAL catalog, release 5.2.0, accessed 2026-10-08.
- **[R18]** IETF RFC 9700 (BCP 240), _Best Current Practice for OAuth 2.0 Security_, January 2025, §4.14. <https://www.rfc-editor.org/rfc/rfc9700#section-4.14>. Refresh tokens "allow the authorization server to issue access tokens with a short lifetime and reduced scope, thus reducing the potential impact of access token leakage."
- **[R19]** OpenID Foundation, _OpenID Connect Back-Channel Logout 1.0 incorporating errata set 1_, December 15, 2023. <https://openid.net/specs/openid-connect-backchannel-1_0.html>, accessed 2026-10-09. §2.2: "The back-channel logout URI MUST be an absolute URI as defined by Section 4.3 of [RFC3986]"; "The back-channel logout URI MUST NOT include a fragment component." `backchannel_logout_uri`: "RP URL that will cause the RP to log itself out when sent a Logout Token by the OP." `backchannel_logout_session_required`: "Boolean value specifying whether the RP requires that a sid (session ID) Claim be included in the Logout Token to identify the RP session with the OP when the backchannel_logout_uri is used." §2.5: "The OP should not retransmit a Back-Channel Logout Request unless the OP suspects that previous transmissions may have failed due to potentially recoverable errors (such as network outage or temporary service interruption at either the OP or RP)."

### Informative

- **[R4]** Microsoft, _Delegate application management administrator permissions_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/delegate-app-roles>. Owners manage a specific application; the Application Developer role grants creation once self-service is restricted; a custom role can be scoped to a single app registration or to all. "Application Administrator: Users in this role can create and manage all aspects of enterprise applications, application registrations, and application proxy settings", and "can add credentials to an application and use those credentials to impersonate the application's identity".
- **[R5]** Microsoft, _Assign enterprise application owners_, accessed 2026-10-08. <https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/assign-app-owners>. "Unlike other Application Administrators, owners can manage only the enterprise applications they own."
- **[R6]** Okta, _Custom admin roles_ and _Create a resource set_, accessed 2026-10-01. <https://help.okta.com/en-us/content/topics/security/custom-admin-role/custom-admin-roles.htm>, <https://help.okta.com/en-us/content/topics/security/custom-admin-role/create-resource-set.htm>. An administrator role constrained to a set of applications.
- **[R7]** Keycloak, _Server Administration Guide_ 26.7.5, fine-grained admin permissions. <https://www.keycloak.org/docs/26.7.5/server_admin/index.html>. Permissions over individual resources, such as a client.
- **[R8]** Microsoft, _Configure Microsoft Entra role settings in PIM_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings>. "Require approval for activation of an eligible assignment … We recommend that you select at least two approvers."
- **[R9]** OWASP, _API Security Top 10 2023_, API1:2023 Broken Object Level Authorization, accessed 2026-10-08. <https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/>. "Every API endpoint that receives an ID of an object, and performs any action on the object, should implement object-level authorization checks. The checks should validate that the logged-in user has permissions to perform the requested action on the requested object." Under How To Prevent: "Use the authorization mechanism to check if the logged-in user has access to perform the requested action on the record in every function that uses an input from the client to access a record in the database."
- **[R10]** IETF RFC 9110, _HTTP Semantics_, June 2022, §15.5.4 and §15.5.5. <https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.4>. "An origin server that wishes to "hide" the current existence of a forbidden target resource MAY instead respond with a status code of 404 (Not Found)." The 404 status "indicates that the origin server did not find a current representation for the target resource or is not willing to disclose that one exists."
- **[R11]** Google Cloud, _Best practices for managing service accounts_, accessed 2026-10-08. <https://docs.cloud.google.com/iam/docs/best-practices-service-accounts>. "Instead, consider them in the context of the resource they're associated with and manage the service account and its associated resource as one unit: Apply the same processes, same lifecycle, and same diligence to the service account and its associated resource, and use the same tools to manage them."
- **[R13]** Microsoft, _Configurable token lifetimes in the Microsoft identity platform_, accessed 2026-10-08. <https://learn.microsoft.com/en-us/entra/identity-platform/configurable-token-lifetimes>. "Adjusting the lifetime of an access token is a trade-off between improving system performance and increasing the amount of time that the client retains access after the user's account is disabled"; a token lifetime policy "controls how long access, SAML, and ID tokens for this resource are considered valid"; the access token lifetime has a minimum of 10 minutes.
- **[R14]** Microsoft, _Assign tokenLifetimePolicy_, Microsoft Graph v1.0, accessed 2026-10-08. <https://learn.microsoft.com/en-us/graph/api/application-post-tokenlifetimepolicies?view=graph-rest-1.0>. "Assign a tokenLifetimePolicy to an application"; least privileged application permissions "Application.ReadWrite.OwnedBy and Policy.Read.All". Creating a policy takes `Policy.ReadWrite.ApplicationConfiguration` (_Create tokenLifetimePolicy_, <https://learn.microsoft.com/en-us/graph/api/tokenlifetimepolicy-post-tokenlifetimepolicies?view=graph-rest-1.0>).
- **[R15]** Okta, _Configure an access policy_, accessed 2026-10-08. <https://developer.okta.com/docs/guides/configure-access-policy/main/>. "Access policies help you secure your APIs by defining different access and refresh token lifetimes for a given combination of grant type, user, and scope"; "Access policies are specific to a particular authorization server"; "an access token for a banking API may include a transactions:read scope with a multi-hour token lifetime. By contrast, the lifetime of an access token for transferring funds should be only a matter of minutes."
