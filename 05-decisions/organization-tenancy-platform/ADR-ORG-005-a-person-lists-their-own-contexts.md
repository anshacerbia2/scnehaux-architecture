---
doc_meta:
  id: ADR-ORG-005
  title: A Person Lists Their Own Contexts
  adr_type: foundational
  status: accepted
  created: 2026-10-07
  created_date: 2026-10-07
  created_by: Core Platform Team
---

# ADR-ORG-005: A Person Lists Their Own Contexts

## 1. Title

A Person Lists Their Own Contexts.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-07 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

A person holding Memberships in several Tenants works in one at a time, chosen at sign-in
(`ADR-IAM-006 §5.2`). To choose, they need the list. `TDD-organization-control-002` names the route
that gives it, `GET /v1/principals/{principal_id}/contexts`, and says "The full set is retrieved
through the context API and never placed in a token". It was never built, and nothing decides who
may call it.

The Organization Control API admits three kinds of caller:

- **A Tenant caller**, whose token names a Tenant. Row security confines it to that one Tenant.
- **A provider**, whose authority is in force. It reaches across Tenants and is recorded doing so.
- **An eligible provider**, who reaches the activation routes alone (`ADR-ORG-002`).

A person signed in without a Tenant and holding no provider grant reaches nothing. That is the
person who most needs the list, because they have not chosen a Tenant yet. So today
Organization Experience asks for a Tenant identifier typed by hand.

## 4. Decision Drivers

- **Platforms answer this list for the caller, with the least privilege.**
  - GitHub's `GET /user/orgs` is "List organizations for the authenticated user" [R1].
  - Azure Resource Manager's `GET /tenants` "Gets the tenants for your account" [R2].
  - Microsoft Graph's `/me/memberOf` needs only `User.Read` for the caller's own memberships,
    where another person's need `User.Read.All` [R3].
- **The list is narrowed to what the caller holds, and names their role in it.**
  - Auth0's picker shows "the first 20 organizations they joined" [R4].
  - GitHub returns each membership's `state` and the caller's `role` (`admin`, `member`) [R1].
- **A listed context is not an authorization decision.**
  - Auth0: an API "should validate the claim … If the claim cannot be validated, then the API
    should deem the token invalid" [R5].
  - Microsoft: "Always check that the tid in a token matches the tenant ID used to store data",
    and the subject and actor checks "are still necessary" [R6].
- **The set never enters a token** (`STD-IAM-001 §3.3`).

## 5. Decision

### 5.1 Any Signed-In Person Reads Their Own Contexts

`GET /v1/principals/{principal_id}/contexts` answers a person for themselves.

- **A self caller.** The caller is a human token whose `principal_id` is the one in the path,
  whether or not the token names a Tenant and whether or not it holds a provider grant. This is a
  fourth caller class. It is admitted to this route alone, as an eligible provider is admitted to
  the activation routes alone.
- **A provider** reads anyone's, with its reason, recorded as every provider read is.
- **Everyone else** is refused.
- **A self read is not a provider access.** It reaches only rows whose `principal_id` is the
  caller's, and it writes no privileged-access record.

### 5.2 The List Names Where the Person May Work, Nothing More

One entry per active Membership in an active Tenant:

- the Tenant's identifier, display name and status;
- the Workspace, if the Membership is Workspace-scoped;
- whether the person administers the Tenant (`ADR-ORG-003`).

Nothing else is returned: no grant, no version and no other person. The list is paged in the
`STD-GLB-001` 1.3.0 form.

### 5.3 Choosing Is Still a Sign-In, Checked Again at Use

An entry selects; it does not grant.

- **Choosing a Tenant is a sign-in** for it (`ADR-IAM-006 §5.2`). The kernel issues
  `organization:<tenant_id>` only for a member.
- **Every request is checked again.** The Organization Control API checks the Membership, the
  Tenant and the administration grant on every request (`ADR-ORG-003`), whatever the list said
  ([R5][R6]).

## 6. Consequences

### Positive

- A Tenant administrator chooses a Tenant from a list instead of typing an identifier.
- Reading one's own contexts needs no provider authority and leaves no provider record, which is
  the least privilege the platforms above use.

### Negative

- **A fourth caller class** exists at the API: a route that admits a person with no Tenant and no
  grant. It is one route, keyed to the caller's own identifier.
- **The read spans Tenants for one person,** so it needs a binding that row security can hold to
  that person.

### Operational

- The route is rate-limited like the other reads. A self read is logged and is not alerted on.

## 7. Compliance Impact

### Related Standards

- `STD-IAM-001 §3.3`: the set stays out of tokens.
- [ADR-IAM-006](../identity-access-platform/ADR-IAM-006-tenant-context-in-tokens.md) §5.2: the
  choice is a sign-in.
- `ADR-ORG-002`: the eligible caller's precedent for a narrow admission.
- `ADR-ORG-003`: the administration flag, and the check at use.
- `TDD-organization-control-001` (caller classes), `TDD-organization-control-002` (the route) and
  `TDD-organization-experience-002` (the context switcher) change to implement it.

### Compliance Status

Compliant once the route is served with the self caller, and Organization Experience lists from it.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Only Providers Read Contexts

**Rejected because:** the person choosing a Tenant is rarely a provider. A provider read is recorded
as cross-Tenant access, which a person reading their own list is not.

### Alternative B — Put the Set in the Token

**Rejected because:** `STD-IAM-001 §3.3` forbids it. A token naming every Tenant is the one
stolen token that carries authority everywhere.

### Alternative C — The Kernel's Organization Chooser

**Deferred** by `ADR-IAM-008` Alternative D until `compat/` asserts it. It would list Keycloak
Organizations, which are a projection of these Memberships. This route reads the authority itself.

## 9. References

### Informative

- **[R1]** GitHub, _REST API: Organizations_, accessed 2026-10-07.
  <https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#list-organizations-for-the-authenticated-user>
  and <https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-memberships-for-the-authenticated-user>.
  "List organizations for the authenticated user." / "Lists all of the authenticated user's
  organization memberships." The membership's `role` is one of `admin`, `member`,
  `billing_manager`.
- **[R2]** Microsoft, _Tenants - List_ (Azure Resource Manager), accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/rest/api/resources/tenants/list?view=rest-resources-2022-12-01>.
  "Gets the tenants for your account."
- **[R3]** Microsoft, _List a user's direct memberships_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/graph/api/user-list-memberof?view=graph-rest-1.0>. "Calling the
  `/me/memberOf` endpoint requires a signed-in user and therefore a delegated permission"; the
  least-privileged permission for the caller's own memberships is `User.Read`, and for another
  user's, `User.Read.All`.
- **[R4]** Auth0, _Login Flows for Organizations_, accessed 2026-10-07.
  <https://auth0.com/docs/manage-users/organizations/login-flows-for-organizations>. "Users in
  multiple Organizations are directed to the Organization Picker after the login flow, which
  displays the first 20 organizations they joined."
- **[R5]** Auth0, _Use Organizations with tokens_, §Validate tokens, accessed 2026-10-07.
  <https://auth0.com/docs/manage-users/organizations/using-tokens>. "If an `org_id` claim is present
  in the access token, then your API should validate the claim … If the claim cannot be validated,
  then the API should deem the token invalid."
- **[R6]** Microsoft, _Secure applications and APIs by validating claims_, §Validate the tenant,
  accessed 2026-10-07. <https://learn.microsoft.com/en-us/entra/identity-platform/claims-validation>.
  "Always check that the tid in a token matches the tenant ID used to store data with the
  application." / "Validation of the tenant is the first step, but the checks of the subject and
  actor described in this article are still necessary."
