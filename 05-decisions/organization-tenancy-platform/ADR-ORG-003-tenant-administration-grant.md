---
doc_meta:
  id: ADR-ORG-003
  title: Tenant Administration Is a Recorded Grant, Checked with Current Membership
  adr_type: foundational
  status: accepted
  created: 2026-10-04
  created_date: 2026-10-04
  created_by: Organization Platform Team
---

# ADR-ORG-003: Tenant Administration Is a Recorded Grant, Checked with Current Membership

## 1. Title

Tenant Administration Is a Recorded Grant, Checked with Current Membership.

## 2. Status

| Date       | Status            | ADR Type     | Reviewers                 | Approver             |
| ---------- | ----------------- | ------------ | ------------------------- | -------------------- |
| 2026-10-04 | accepted          | foundational | Architecture Review Board | Enterprise Architect |
| 2026-10-20 | accepted, amended | foundational | Architecture Review Board | Enterprise Architect |

**Amended 2026-10-20, in place,** on two points the owner approved on 2026-10-20 as recommended: §5.5
adds how a restore moves Tenant versions, Tenant security versions and provider grant versions past
what consumers hold, and how a consumer orders a Tenant by both of its versions, and §5.6 lets a provider suspend or revoke one Membership inside a Tenant. §6 no longer leaves
the second open. It is edited in place because no system this decision governs is in production
(GDC-010 §2.4.2): `SAD-004` §10.3 records that the only deployment is the development server.

## 3. Context

The Organization Control API recognizes its callers by record (`ADR-ORG-001 §5.11`). Its design reads a
record for two of them:

- **A provider** holds a provider grant in force.
- **A projection consumer** is a registered workload.

The third, the **Tenant administrator**, is decided by the token alone: "Tenant administrator |
`tenant_id` | — (no record read)" (`TDD-organization-control-001 §Caller Authority`). Any token that
carries a `tenant_id` administers that Tenant. It can grant, suspend and revoke Memberships there.

That was safe while nothing issued a `tenant_id`. `ADR-IAM-006` changed that:

- The kernel now issues one to **every member** of a Tenant who signs in for it.
- The membership comes from Organization's own records, projected into the kernel.

So once a client whose audience names `organization-control-api` asks for a Tenant, every member of
that Tenant administers it. The resource would also accept a token for a Membership revoked since
the token was issued, because it reads nothing (`STD-IAM-002 §3.5` step 8).

The architecture already separates the two:

- `PAD-PLT-002` defines a "Tenant Administrator: Role authorized only for governed tenancy
  administration".
- It also states: "Membership does not imply Subscription, Entitlement, Product role, or business
  authorization."

No record carries the role.

## 4. Decision Drivers

- **Membership is not authority.** Established platforms keep the two apart:
  - Auth0 scopes roles to one Organization and gives them to "certain members" [R1].
  - Microsoft Entra: "A role assignment is a Microsoft Entra resource that attaches a role definition
    to a security principal at a particular scope" [R2].
  - Google Cloud: "You can't directly grant permissions to a principal. Instead, you give principals
    permissions by granting them roles" [R3].
- **Deny by default.** "By default, all requests are implicitly denied" [R4]. "An application should
  be configured to deny access by default" [R5].
- **The tenant identifier is a selector.** OWASP lists, among what not to do: "Treat tenant IDs from
  client headers or request parameters as authorization proof; they are selectors that require
  server-side verification" [R6]. It also asks: "Verify that the authenticated principal is
  authorized to act in the selected tenant" [R6].
- **Checked on every request,** at the resource: "Permission should be validated correctly on every
  request" [R5].
- **Privileged roles are governed.** NIST asks to "Monitor privileged role or attribute assignments
  … and … Revoke access when privileged role or attribute assignments are no longer appropriate"
  (AC-2(7)) and to grant least privilege (AC-6) [R7].

## 5. Decision

### 5.1 A Tenant Administrator Holds a Tenant Administration Grant

A Tenant administrator is a Principal holding a **tenant administration grant** that Organization
Control records:

- the grant names the Principal and one Tenant;
- it carries who granted it, when and why;
- it may be revoked, recording who revoked it, when and why.

It is the Tenant-scoped counterpart of the provider grant (`ADR-ORG-001 §5.11`). The record is the
authority. It is not projected into the kernel, and no claim carries it.

### 5.2 Who Grants It

**A provider grants and revokes it**, through the API, with a reason. That is cross-tenant
administration, which `PAD-PLT-002` already governs: bounded provider scope, elevated assurance,
reason and evidence.

- **The first administrator of a Tenant** is granted the same way, together with a Membership in
  that Tenant.
- **No Tenant administrator grants it, for now.** Letting one name another inside the same Tenant
  (Auth0's "Organization editors can assign … Organization roles for members within their
  Organization" [R1]) is a separate decision. It is reopened when a Tenant needs to manage its
  administrators itself.

### 5.3 What a Tenant-Scoped Request Must Satisfy

A token with a `tenant_id` is admitted as that Tenant's administrator only when all of these hold,
each read from Organization's own records for the request:

1. **The Principal holds an active Membership in that Tenant.** This is `STD-IAM-002 §3.5` step 8's
   current-state check, at the authority itself. A Membership revoked since the token was issued
   stops the next request.
2. **The Tenant is active.** A suspended or offboarding Tenant is administered only by a provider.
3. **A tenant administration grant for that Principal and Tenant is in force.**
4. **The token carries `acr` `aal2` and `auth_time`.** Tenant administration is privileged access,
   in `STD-IAM-002`'s tenant-scoped privileged form, and `ADR-IAM-004` requires two factors of
   privileged access under NIST IA-2(1).

Any other tenant-scoped token is refused with `403`, and nothing is read on its behalf.

- **Nothing is served to a plain member.** Organization Control serves no route to a member who is
  not an administrator.
- **How reads happen.** The checks are indexed reads by `principal_id` and `tenant_id`, in the
  read-only transaction where the provider and consumer records are already read.

### 5.4 Evidence

Every grant and revocation is recorded, insert-only except for its revocation columns, as a
provider grant is. Each tenant-scoped request is attributed to its `principal_id`, as every request
already is.

The grants are reviewable per Tenant, which is what AC-2(7)(b) asks [R7].

### 5.5 A Provider Pauses Tenant Administration While a Restore Is Reconciled (2026-10-09)

`SAD-004 §9.1.1` has a restore to an older point reconciled and contained "before normal
operation". The containment is a pause of every Tenant administrator's commands, so authority does
not change under the operator while security versions are reconciled (`SAD-004 §6.6`).

- **A provider pauses and lifts it**, with a reason and an `Idempotency-Key`. Each decision is an
  insert-only row naming the provider, the reason and the correlation identifier, and the latest row
  is the state. No row means not paused.
- **Commands are refused, reads continue.** Every request a Tenant administrator makes with a method
  other than `GET`, `HEAD` or `OPTIONS` is refused before it reaches a handler. Those three are safe:
  "Request methods are considered "safe" if their defined semantics are essentially read-only; i.e.,
  the client does not request, and does not expect, any state change on the origin server" [R8].
  `TRACE`, the fourth safe method [R8], is served by no route.
- **The refusal is `503`, with a detail saying the same command can be sent again once the pause is
  lifted.** `503` "indicates that the server is currently unable to handle the request due to a
  temporary overload or scheduled maintenance, which will likely be alleviated after some delay"
  [R8]. A `403` would tell the administrator its authority is gone, which it is not.
- **It is read where the caller is admitted**, beside the grant of §5.3, for each request, so a
  pause takes effect at the next command and so does its lifting. A pause that cannot be read
  refuses the command: a command let through because the record was unreachable is the change the
  pause exists to stop.
- **Provider acts and consumers' protocol calls continue.** The operator's repairs are provider acts.
- **It can start before the service serves.** The restore procedure may record the pause in the
  restored database before the service starts, as a row naming no actor. Only a pause may name none,
  so lifting one is always a provider's named decision.

**Tenant and provider grant versions are bumped before the service serves (amended 2026-10-20).** A
restore to an older point gives back Tenant versions, Tenant security versions and provider grant
versions that consumers have already seen superseded, and a consumer discards a lower version as already applied.
Memberships are advanced from the consumer's report (`SAD-004 §6.6`). Tenants and grants are moved
past what any consumer holds by a margin, as etcd restores its revision: "In order to ensure the
revisions are never decreasing after a restore, you can supply the --bump-revision option" [R9]. etcd
names the danger this avoids: "Restoring to an older revision may not correctly refresh the caches,
causing unpredictable and inconsistent behavior in the controllers" [R9]. The restore, before the
service serves and beside the pause above:

1. **Adds a margin to every version.** Every Tenant's `version` and `tenant_security_version`, and
   every `grant_version`, gains M = 10^9. Both Tenant versions move, because a consumer orders a
   Tenant by both (below). etcd sizes its own margin the same way: "you may cover a week old snapshot with bumping
   by 1'000'000'000 assuming that etcd runs with less than 1500 writes per second" [R9]. The versions
   are `bigint`, and no row changes 10^9 times within a backup window.
2. **Publishes the withdrawn ones.** Each suspended, offboarding or retired Tenant, and each revoked or
   ended grant, is published at its new version. That only narrows access.
3. **Publishes no active row.** Publishing an active row could grant again what a lost withdrawal
   took away. It is the same rule as for Memberships: a restore never widens access.
4. **Makes every consumer reconcile.** etcd marks the bumped revisions compacted so that "all watches
   are terminated" and caches are invalidated [R9]. Here every consumer runs its reconciliation
   (`ADR-ORG-001 §5.7`).

The rows and their outbox entries are written in one transaction with no actor, as the pre-serve
pause is. identity-control and foundation-reference apply only a higher version and check no gap. The bump also ends "the same version, two states" for Tenants and grants,
because no version a consumer holds can equal a new one. Extending the consumer report to Tenants and
grants is rejected: it changes identity-control and foundation-reference, and gains nothing the bump
lacks.

**A consumer orders a Tenant by the pair (`tenant_security_version`, `tenant_version`).** It applies a
Tenant event or snapshot row only when the pair it carries is greater than the pair it holds,
compared as PostgreSQL compares two row constructors: "the row elements are compared left-to-right,
stopping as soon as an unequal or null pair of elements is found" [R14]. Ordered by one version alone,
a consumer loses a change either way. By `tenant_security_version` alone, an activation, which moves
only `tenant_version`, is discarded when it follows a snapshot of the Tenant in provisioning. By
`tenant_version` alone, a restored Tenant's withdrawal can be discarded when its `tenant_version` was
not bumped past what the consumer holds. Every Tenant event and snapshot row therefore carries both
versions. identity-control orders by the pair (identity-control #114), and so does foundation-reference
(foundation-reference #30, merged 2026-10-20). The consumer contract changes only in requiring `tenant_version`, which
Organization Control already publishes.

### 5.6 A Provider May Suspend or Revoke One Membership Inside a Tenant (2026-10-20)

A provider in force may suspend or revoke one Membership inside a Tenant, with
`POST /v1/tenants/{tenant_id}/memberships/{membership_id}/suspend` and `…/revoke`. It contains: a
lost withdrawal after a restore, or a compromised member in a cross-tenant exposure.

- **Suspend and revoke only.** Never grant and never restore. Least privilege allows "only authorized
  accesses … that are necessary to accomplish assigned organizational tasks" [R7], and the task is
  containment: AC-2(13) asks to "Disable accounts of individuals within [Assignment: time period] of
  discovery of [Assignment: significant risks]" [R10]. Giving access back stays the Tenant
  administrator's act.
- **An ordinary provider act, not break-glass.** In this estate break-glass means the emergency grants
  (`ADR-ORG-002 §5.2`). The route needs a provider in force: an approved activation with its reason,
  as Entra's just-in-time activation asks for a justification [R13], or an emergency grant, whose
  use is then reviewed like any emergency use. Privileged accounts stay restricted to providers
  (AC-6(5) [R10]).
- **Usable at any time,** not only during a pause.
- **Its command shape.** It requires `X-Administrative-Reason`, an `Idempotency-Key` and the
  Membership's `expected_version`, as `STD-GLB-001` asks of a command on another actor's record. It
  goes through the Membership state machine and its events, on the priority lane.
- **Recorded where the Tenant sees it.** It runs through `db.WithProviderInTenant`, so the
  privileged-access row names the Tenant, and the Tenant's administrators see it in
  `GET /v1/provider-access`. AC-6(9): "Log the execution of privileged functions" [R10]. Google's
  Access Transparency is the model: its logs "include details such as the affected resource and
  action, the time of the action, the reason for the action, and information about the accessor"
  [R11].
- **No Tenant approval first.** It only narrows access, and it is used in incidents. Google's Access
  Approval itself lets a request "be automatically approved without the customer's action to address
  time-sensitive outages", and such requests "are logged in an auto approved state" [R12].

## 6. Consequences

### Positive

- **Membership no longer confers administration**, so ADR-IAM-006's Tenant selection can reach the
  Organization Control API safely.
- **Revocation is immediate.** A revoked Membership or administration grant, or a suspended Tenant,
  stops the next tenant-scoped request.
- **Administration is governed.** Who administers each Tenant is a reviewable record.

### Negative

- **Each Tenant's first administrator needs a provider.** Until a Tenant may manage its own
  administrators, every change goes through a provider.
- **The reference system proof changes.** foundation-reference's proof acts as a Tenant
  administrator with a token alone. It must first grant itself a Membership and an administration
  grant through a provider, and present `aal2`.

- **A paused Tenant administrator cannot re-apply a withdrawal the restore lost (§5.5).** A provider
  re-applies it instead, through §5.6, which widens what a provider does inside a Tenant to
  suspending and revoking one Membership (amended 2026-10-20). A provider cannot grant or restore
  one.
- **A restore bumps every Tenant and grant version by 10^9 (§5.5).** The numbers jump, and every
  consumer reconciles before normal operation.

### Operational

- Organization Control adds the grant table and the provider routes that grant, list and revoke it.
- It reads three facts per tenant-scoped request: the Membership, the Tenant and the grant.

## 7. Compliance Impact

### Related Standards and Decisions

- `PAD-PLT-002`: implements its "Tenant Administrator" role. Its rule that Membership implies no
  authorization now holds at the API.
- [ADR-ORG-001](ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) §5.11: the
  Tenant administrator becomes the third caller that is a record, beside the provider and the
  consumer.
- `STD-IAM-002 §3.5` step 8: Organization Control, as a resource accepting `tenant_id`, makes the
  current-state check against its own authority.
- `ADR-IAM-004`: Tenant administration is privileged access, at `aal2`.
- `ADR-IAM-006`: Tenant selection reaches this API only under this decision.
- `TDD-organization-control-001` §Caller Authority, and foundation-reference's system proof, change
  to implement it.
- `SAD-004 §6.6`, §9.1.1: the containment of a restore to an older point, which §5.5 is.
  `TDD-organization-control-001` 1.22.0 §Pausing Tenant Administration implements it.

### Compliance Status

Compliant once Organization Control implements §5.

Until then, no client may hold both the kernel's `organization` scope and `organization-control-api`
in its audience. Today none does: the only callers naming that API are provider and workload
clients.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Any Member Administers Their Tenant

**Rejected because:**

- `PAD-PLT-002` says Membership implies no authorization.
- Every source above separates the two [R1][R2][R3].

### Alternative B — A Role Claim in the Token

**Benefits:** no read per request.

**Rejected because:**

- `ADR-ORG-001 §5.11` forbids reading authority from a role in the token.
- A claim outlives a revocation by the token's lifetime.

### Alternative C — A Membership Type of "administrator"

**Rejected because:** `PAD-PLT-002` defines Membership Type as a "classification of the contextual
relationship, not a Product permission". Folding authority into it would make every Membership
change an authority change, and every consumer of the projection would carry it.

### Alternative D — Extend the Consumer Report to Tenants and Grants (§5.5)

**Benefits:** the versions move only as far as a consumer holds them.

**Rejected because:** it changes identity-control's and foundation-reference's report contract, and
the bump needs no contract change. The margin is the bound etcd sizes explicitly [R9].

### Alternative E — The Restore Runbook Alone (§5.5)

**Rejected because:** a person repairing versions by hand leaves "the same version, two states" open,
and the runbook would carry what a script should run (`STD-GLB-009` §A procedure step is a script).

### Alternative F — A Provider May Change One Membership Any Way, Restore and Grant Included (§5.6)

**Rejected because:** the task is containment, and least privilege gives no more than the task needs
[R7][R10]. Restoring access is the Tenant administrator's decision.

### Alternative G — A Pause That Exempts Named Tenants, or a Tenant Suspension Alone (§5.6)

**Rejected because:** both act on a whole Tenant to fix one Membership, and neither helps outside a
pause.

## 9. References

- **[R1]** Auth0, _Organization Roles_ and _Add Roles to Organization Members_,
  <https://auth0.com/docs/manage-users/organizations/organization-roles>,
  <https://auth0.com/docs/manage-users/organizations/configure-organizations/add-member-roles>,
  accessed 2026-10-04:
  - "Organization Roles allow you to define roles that exist only within a specific Organization.
    Unlike tenant roles, which apply across your entire tenant, Organization roles are scoped to a
    single Organization."
  - "Organization editors can assign and remove Organization roles for members within their
    Organization but cannot create or modify the roles themselves."
  - From _Organizations overview_: "you could assign an administrator role to certain members and
    allow them to self-manage their organizations".
- **[R2]** Microsoft, _Overview of custom roles in Microsoft Entra ID_,
  <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/custom-overview>,
  accessed 2026-10-04:
  - "A role assignment is a Microsoft Entra resource that attaches a role definition to a security
    principal at a particular scope to grant access to Microsoft Entra resources. Access is granted
    by creating a role assignment, and access is revoked by removing a role assignment."
  - "If the user doesn't have a role with the action at the requested scope, access is not granted."
- **[R3]** Google Cloud, _IAM overview_, <https://cloud.google.com/iam/docs/overview>, accessed
  2026-10-04:
  - "You can't directly grant permissions to a principal. Instead, you give principals permissions by
    granting them roles."
  - "When an authenticated principal attempts to access a resource, IAM checks the resource's allow
    policy to determine whether the principal has the required permissions."
- **[R4]** Amazon Web Services, _Policy evaluation logic_,
  <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html>,
  accessed 2026-10-04: "By default, all requests are implicitly denied".
- **[R5]** OWASP, _Authorization Cheat Sheet_,
  <https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html>, accessed
  2026-10-04:
  - "For security purposes an application should be configured to deny access by default."
  - "Permission should be validated correctly on every request".
- **[R6]** OWASP, _Multi-Tenant Application Security Cheat Sheet_,
  <https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html>, accessed
  2026-10-04:
  - "Treat client-supplied tenant identifiers as selectors only. Verify that the authenticated
    principal is authorized to act in the selected tenant."
  - Don't: "Treat tenant IDs from client headers or request parameters as authorization proof; they
    are selectors that require server-side verification."
- **[R7]** NIST SP 800-53 Rev. 5, from the OSCAL catalog
  <https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>,
  accessed 2026-10-04:
  - AC-2(7): "(b) Monitor privileged role or attribute assignments; (c) Monitor changes to roles or
    attributes; and (d) Revoke access when privileged role or attribute assignments are no longer
    appropriate."
  - AC-6: "Employ the principle of least privilege, allowing only authorized accesses for users …
    that are necessary to accomplish assigned organizational tasks."
- **[R8]** IETF RFC 9110, _HTTP Semantics_, June 2022. <https://www.rfc-editor.org/rfc/rfc9110>,
  accessed 2026-10-09.
  - §9.2.1: "Request methods are considered "safe" if their defined semantics are essentially
    read-only; i.e., the client does not request, and does not expect, any state change on the origin
    server as a result of applying a safe method to a target resource." "Of the request methods
    defined by this specification, the GET, HEAD, OPTIONS, and TRACE methods are defined to be safe."
  - §15.6.4: "The 503 (Service Unavailable) status code indicates that the server is currently unable
    to handle the request due to a temporary overload or scheduled maintenance, which will likely be
    alleviated after some delay."
- **[R9]** etcd, _Disaster recovery_ (v3.6 operations guide), §Revision Difference and §Restoring
  with revision bump, <https://etcd.io/docs/v3.6/op-guide/recovery/>, accessed 2026-10-20.
  - "When you are restoring a cluster, existing clients may perceive the revision going back by many
    hundreds or thousands"; "Restoring to an older revision may not correctly refresh the caches,
    causing unpredictable and inconsistent behavior in the controllers."
  - "When restoring from a snapshot in the context of either: known consumers of the watch API, local
    cached copies of etcd data or when using Kubernetes in general - it is highly recommended to
    restore using “revision bumps” below."
  - "In order to ensure the revisions are never decreasing after a restore, you can supply the
    --bump-revision option"; "Since each write to etcd increases the revision by one, you may cover a
    week old snapshot with bumping by 1'000'000'000 assuming that etcd runs with less than 1500
    writes per second."
  - "In the context of Kubernetes controllers, it is important to also mark all the revisions,
    including the bump, as compacted using --mark-compacted . This ensures that all watches are
    terminated and etcd does not respond to requests about revisions that happened after taking the
    snapshot - effectively invalidating its informer caches."
- **[R10]** NIST SP 800-53 Rev. 5, from the OSCAL catalog
  <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>,
  accessed 2026-10-20:
  - AC-2(13): "Disable accounts of individuals within [Assignment: time period] of discovery of
    [Assignment: significant risks]."
  - AC-6(5): "Restrict privileged accounts on the system to [Assignment: personnel or roles]."
  - AC-6(9): "Log the execution of privileged functions." Its guidance: "Logging and analyzing the
    use of privileged functions is one way to detect such misuse and, in doing so, help mitigate the
    risk from insider threats and the advanced persistent threat."
- **[R11]** Google Cloud, _Access Transparency overview_,
  <https://cloud.google.com/assured-workloads/access-transparency/docs/overview>, accessed
  2026-10-20: "Access Transparency logs record the actions that Google personnel take when accessing
  Customer Data. Access Transparency log entries include details such as the affected resource and
  action, the time of the action, the reason for the action, and information about the accessor."
- **[R12]** Google Cloud, _Access Approval overview_, §Access Approval exclusions,
  <https://cloud.google.com/assured-workloads/access-approval/docs/overview>, accessed 2026-10-20:
  "the approval request may be automatically approved without the customer's action to address
  time-sensitive outages. Such auto-approved Access Approval requests are logged in an auto approved
  state."
- **[R13]** Microsoft, _What is Microsoft Entra Privileged Identity Management?_,
  <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure>,
  accessed 2026-10-20: "Provide just-in-time privileged access to Microsoft Entra ID and Azure
  resources"; "Use justification to understand why users activate"; "Get notifications when
  privileged roles are activated"; "Download audit history for internal or external audit". The
  pattern §5.6 relies on: a provider in force only through an activation with a reason.
- **[R14]** PostgreSQL 17 Documentation, _Comparison Functions and Operators_ / _Row and Array
  Comparisons_, §9.25.5 Row Constructor Comparison,
  <https://www.postgresql.org/docs/17/functions-comparisons.html>, accessed 2026-10-20. "For the <,
  <=, > and >= cases, the row elements are compared left-to-right, stopping as soon as an unequal or
  null pair of elements is found."
