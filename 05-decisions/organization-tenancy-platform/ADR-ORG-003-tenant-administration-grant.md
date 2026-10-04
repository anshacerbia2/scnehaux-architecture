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

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-04 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

The Organization Control API recognizes three callers (`ADR-ORG-001 §5.11`). Its design reads a
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
