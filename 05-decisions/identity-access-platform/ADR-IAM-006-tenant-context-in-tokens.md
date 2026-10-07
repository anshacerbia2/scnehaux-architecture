---
doc_meta:
  id: ADR-IAM-006
  title: Tenant Context in Tokens, Selected per Sign-In
  adr_type: foundational
  status: accepted
  created: 2026-10-04
  created_date: 2026-10-04
  created_by: Identity Platform Team
---

# ADR-IAM-006: Tenant Context in Tokens, Selected per Sign-In

## 1. Title

Tenant Context in Tokens, Selected per Sign-In.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-04 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

`STD-IAM-002 §3.2` puts one active Tenant into a token: `tenant_id`, an optional `workspace_id`, and
two version claims, `membership_version` and `tenant_security_version`. A resource compared the
versions with those it learned from Organization's events and refused a lower one (§3.5 step 8).

How the active Tenant reaches the token was left open. `TDD-identity-control-002` names three
proof-of-concept questions:

1. **Representation.** Keycloak Organizations, Groups, or user attributes.
2. **Session removal granularity.** Per Principal and Tenant, or per Principal only.
3. **The context switch.** How a person who belongs to several Tenants chooses the active one.

Organization owns the Tenant and the Membership, and Keycloak holds only a bounded projection of
them (`ADR-IAM-001 §5.3`, `ADR-ORG-001`).

Three facts bound the choice:

- **What the pinned kernel can do.** Keycloak 26.7.5 was read at its source:
  - Organizations is a supported feature, enabled by default [R7].
  - A client selects an organization per authorization request with the scope
    `organization:<alias>` [R7].
  - An organization has no storage for a value per member, and no built-in mapper puts an
    organization or group attribute into a token as a flat integer [R8].
  - The Admin API removes all of a user's sessions or one session, nothing per organization [R8].
- **How established platforms do it.** Every platform below that serves a person in several tenants
  selects the tenant per sign-in or per token request, and carries it as one claim:
  - Auth0 `org_id`, through the `organization` parameter [R1];
  - Microsoft Entra ID `tid`, through the tenant-specific authority [R2];
  - Google Identity Platform `firebase.tenant`, through the tenant set before each sign-in [R4].

  Only Amazon Cognito keeps the tenant as a user attribute. It asks that the attribute be "immutable
  or read-only", which assumes one tenant per user [R5].

- **No platform puts membership version numbers in its tokens.** None of these platforms carries a
  per-membership or per-tenant version in a token. They rely on short-lived tokens and on refresh
  and session revocation [R2][R4]. OWASP asks the resource to bind the tenant to "current tenant
  membership" [R6].

## 4. Decision Drivers

- **A person in several Tenants works in one at a time, per sign-in.** That is the established
  pattern [R1][R2][R4]. A per-user setting would switch every session the person holds at once.
- **The active Tenant is never browser input.** `STD-IAM-001 §3.3` requires context claims to be "an
  authority-derived or approved projection, never untrusted browser input". OWASP agrees: "Treat
  client-supplied tenant identifiers as selectors only. Verify that the authenticated principal is
  authorized to act in the selected tenant" [R6].
- **A revocation is enforced at the resource, now.** OWASP: "Bind tenant context to a
  server-verified identity and current tenant membership or service authorization" [R6].
- **Supported kernel interfaces only.** `ADR-IAM-001 §5.7` forbids extensions, scripts and preview
  features without their own decision.

## 5. Decision

### 5.1 One Keycloak Organization per Tenant

Each Tenant is a Keycloak Organization:

- Its alias is the `tenant_id`.
- Its members are the Principals holding an active Membership in that Tenant.
- It is enabled while the Tenant is active.

identity-control maintains these from Organization's events, through the Admin API. Organization
remains the authority; the Organization in Keycloak is a projection (`ADR-IAM-001 §5.3`).

### 5.2 The Active Tenant Is Chosen per Sign-In

A client asks for a Tenant with the scope `organization:<tenant_id>` in its authorization request.
The kernel issues the token only for a member. Its claim is the flat `tenant_id`.

- **The mapper.** The kernel's Organization Membership mapper, single-valued, with the claim name
  `tenant_id`. A single-valued mapper emits only the alias, which is the identifier [R8].
- **Switching Tenant** is a new sign-in for the other Tenant, in the same SSO session. A refresh
  keeps the Tenant it was issued for. Asked for another one, it issues a token with no Tenant at
  all, so it never switches silently.
- **A workload** asks for its Tenant the same way, in its client-credentials request, once its
  service-account user is a member.
- **A token without the scope** carries no `tenant_id`.

The identity-kernel proof of concept observed each of these on Keycloak 26.7.5 (compat run
37207537199).

### 5.3 The Organization Scope Is Given Only to Tenant-Scoped Profiles

The kernel's built-in `organization` client scope is the only path by which `tenant_id` reaches a
token.

- **Who may hold it.** The registration authority attaches it, as an optional scope, only to clients
  whose profile may carry `tenant_id` (`STD-IAM-002 §3.2`): `internal`, tenant-scoped `privileged`,
  and tenant-scoped `workload`.
- **Never a realm default.** It is neither a realm default nor a realm default optional scope, so a
  `provider` or `external` client cannot ask for it. The realm definition already holds both sets
  closed (`TDD-identity-kernel-001`).

`ADR-IAM-008` (2026-10-07) adds one holder: a `privileged` client registered for the `per-sign-in`
form. It asks for `organization:<tenant_id>` only together with `scnehaux-privileged`, so each of its
tokens still declares one form.

### 5.4 Version Claims Leave the Token; the Resource Checks Current State

`membership_version` and `tenant_security_version` are no longer token claims. Two reasons:

- **The kernel has nowhere to keep them.** No supported representation keeps a value per member and
  selects it with the active Tenant [R8].
- **No established platform carries them** [R1][R2][R4].

The guarantee they gave is kept by the resource instead. Where `tenant_id` is present, the resource
refuses the token unless both of these hold in its projection:

- the Principal's Membership in that Tenant is active;
- the Tenant is active.

This is OWASP's "current tenant membership" [R6], and `STD-IAM-002 §3.5` step 8 is amended to it.

- **A revoked Membership or a suspended Tenant** is refused as soon as the resource has applied the
  event, whatever the token says. That is what the version comparison did.
- **What the comparison refused and this check accepts.** The comparison also refused a token
  issued before a Membership was restored. That token names a Membership that is active again, so
  accepting it grants nothing the person does not hold.

The versions remain where they are authority: on Organization's events and in every consumer's
projection (`TDD-organization-control-002`).

### 5.5 Revocation in the Kernel

identity-control applies a Membership or Tenant event to the kernel as follows:

| Event                                      | Kernel change                                  |
| :----------------------------------------- | :--------------------------------------------- |
| A Membership suspended or revoked          | The Principal is removed from the Organization |
| A Tenant suspended or entering offboarding | The Organization is disabled                   |
| A grant, restore or reactivation           | The reverse                                    |

The kernel then refuses a refresh token issued for that Tenant with `invalid_grant`. A new token
request for that Tenant gets a token with no `tenant_id`.

- **Other Tenants are unaffected.** The person's sessions in other Tenants carry on. So
  `TDD-identity-control-002`'s fallback, removing every session of the Principal and recording the
  collateral, is not needed for a revocation.
- **No session is removed.** An access token already issued lives out its lifetime class
  (`STD-IAM-002 §3.3`). Within that time the resource's current-state check refuses it (§5.4).
- **Containment of the Principal itself** still removes every session (`TDD-identity-control-005`).

### 5.6 Workspace

A Keycloak Organization carries one identifier, so this decision projects no Workspace.
`workspace_id` stays optional in `STD-IAM-002`, and no token carries it until a further decision
says how a Workspace is selected.

## 6. Consequences

### Positive

- A person works in one Tenant per sign-in and can hold sessions in several at once, as on the
  platforms people already use.
- Revocation takes effect at the kernel and at the resource. Neither needs a token to carry a
  version.
- The kernel does all of it with a supported feature and a built-in mapper. No extension is added.

### Negative

- **Switching Tenant is a new sign-in.** Within the SSO session it needs no password, but it is a
  round trip to the kernel. The BFF asks for the Tenant at sign-in, and an application offers the
  switch.
- **Every resource accepting `tenant_id` holds a projection of Memberships and Tenants.** That was
  already true: step 8 compared against a local projection. Now the projection must say "active",
  not just carry a number.
- **The Organizations feature is newer than Groups.** Its upgrade surface is wider.
  identity-kernel's compat suite asserts each behaviour §5.2 and §5.5 rely on, on every upgrade.

### Operational

- The realm enables Organizations. The `organization` scope's mapper is declared single-valued and
  named `tenant_id`. The realm's declared default and optional scope sets are closed, so they keep the
  scope out of both.
- identity-control's projector, its reconciler, and the registration authority implement §5.1,
  §5.3 and §5.5.

## 7. Compliance Impact

### Related Standards

- `STD-IAM-002` 1.6.0:
  - §3.2: the version claims are removed.
  - §3.2.1: `tenant_id` comes from the `organization` scope.
  - §3.5 step 8: the current-state check replaces the version comparison.
- `STD-IAM-001 §3.3`: the Tenant is selected by the client and admitted only for a member, so the
  claim stays an authority-derived projection.
- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.3: Organizations as a bounded,
  non-authoritative projection. §5.7: supported interfaces only.
- `TDD-identity-control-002`, `TDD-identity-kernel-001`, `TDD-identity-control-003` and
  `TDD-identity-control-004` change to implement it.

### Compliance Status

Compliant once the kernel's realm, identity-control's projector, and every resource's step 8
implement §5.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — User Attributes, One Active Tenant per Person

**Benefits:**

- The kernel's long-supported User Attribute mapper emits a flat `tenant_id` and integer version
  claims [R8].
- `STD-IAM-002` would not change.

**Rejected because:**

- The active Tenant would belong to the person, not the sign-in. Switching it in one application
  would switch every session the person holds at their next refresh.
- The one platform that keeps the tenant as a user attribute does so for one tenant per user [R5].

### Alternative B — Groups

**Benefits:** long supported.

**Rejected because:**

- No built-in mapper selects one group as the active one.
- A group attribute reaches a token only from the first group found [R8].

### Alternative C — Keep the Version Claims Through an Extension

**Benefits:** the comparison stays as written.

**Rejected because:**

- The current-state check gives the same refusal of a revoked context (§5.4).
- An extension that writes claims is an upgrade liability `ADR-IAM-001 §5.7` exists to avoid.

### Alternative D — Parameterized Scopes

**Rejected because:**

- They are experimental in Keycloak 26.7.5: "This feature is currently experimental. Do not use it in
  production" [R8].
- Their mapper echoes the requested value rather than checking it.

## 9. References

- **[R1]** Auth0, _Use Organizations with tokens_, <https://auth0.com/docs/manage-users/organizations/using-tokens>,
  accessed 2026-10-04: "To authenticate a user through an Organization, you pass an `organization`
  parameter in a call to the `/authorize` endpoint"; "ID and access tokens contain both the `org_id`
  and `org_name` claims"; "If the claim cannot be validated, then the API should deem the token
  invalid." And _Authentication_ (multiple-organization architecture),
  <https://auth0.com/docs/get-started/architecture-scenarios/multiple-organization-architecture/single-identity-provider-organizations/authentication>:
  "The Organizations feature does not associate any selected organization with the Auth0 SSO
  session".
- **[R2]** Microsoft, _Access token claims reference_,
  <https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference>, accessed
  2026-10-04: `tid` "Represents the tenant that the user is signing in to." And _Microsoft identity
  platform and OAuth 2.0 authorization code flow_,
  <https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow>: "For guest
  scenarios where you sign a user from one tenant into another tenant, you _must_ provide the tenant
  identifier to sign them into the resource tenant." And _Continuous access evaluation_,
  <https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation>:
  CAE is "an industry standard based on Open ID Continuous Access Evaluation Profile (CAEP)"; "Changes
  made to Conditional Access policies and group membership made by administrators could take up to one
  day to be effective."
- **[R3]** OpenID Foundation, _OpenID Continuous Access Evaluation Profile 1.0_, final, 29 August 2025,
  <https://openid.net/specs/openid-caep-1_0-final.html>. §3.1 Session Revoked, §3.2 Token Claims
  Change. It defines no membership event. Informative: the push signal a later decision may adopt.
- **[R4]** Google Cloud, _Signing in with tenants_ and _Managing tenants_,
  <https://docs.cloud.google.com/identity-platform/docs/multi-tenancy-authentication> and
  <https://docs.cloud.google.com/identity-platform/docs/multi-tenancy-managing-tenants>, accessed
  2026-10-04: "To sign in to a tenant, the tenant ID needs to be passed to the auth object"; "After
  refresh tokens are revoked, no new ID tokens can be issued for that user until they re-authenticate.
  However, existing ID tokens will remain active until their natural expiration time (one hour)."
- **[R5]** Amazon Web Services, _Custom-attribute-based multi-tenancy best practices_,
  <https://docs.aws.amazon.com/cognito/latest/developerguide/custom-attribute-based-multi-tenancy.html>,
  accessed 2026-10-04: "A custom attribute that defines a tenant ID should be immutable or read-only
  to the app client."
- **[R6]** OWASP, _Multi-Tenant Application Security Cheat Sheet_, §1 Tenant Identification & Context
  Management,
  <https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html>, accessed
  2026-10-04: "Treat client-supplied tenant identifiers as selectors only. Verify that the
  authenticated principal is authorized to act in the selected tenant"; "Bind tenant context to a
  server-verified identity and current tenant membership or service authorization."
- **[R7]** Keycloak 26.7.5, _Server Administration Guide_, Managing organizations and Mapping
  organization claims, source `docs/documentation/server_admin/topics/organizations/` at tag 26.7.5:
  - "It enables multi-tenancy within a realm so that users can have access to protected resources
    from a realm but with a more restricted and controlled context, that context being the
    organization to which they belong."
  - `organization:<alias>` "Maps to a specific organization with the given alias … If any of the
    aliases does not match an existing organization or the user is not a member, the request will be
    rejected."
  - `common/src/main/java/org/keycloak/common/Profile.java`:
    `ORGANIZATION("Organization support within realms", Type.DEFAULT)`.
- **[R8]** Keycloak 26.7.5 source:
  - `OrganizationMembershipMapper.java`: not multivalued, "return organizations.get(0).getAlias()".
  - `TokenManager.java`, `validateSelectedOrganization`: "if (organization == null ||
    !organization.isEnabled() || !organization.isMember(user)) { throw new
    ErrorResponseException(OAuthErrorException.INVALID_GRANT, "Invalid organization" …".
  - `UserResource.java`: `POST /users/{id}/logout` "Remove all user sessions associated with the user".
  - `con-parameterized-client-scopes.adoc`: "This feature is currently experimental. Do not use it in
    production."
- **[R9]** IANA, _JSON Web Token Claims_ registry, <https://www.iana.org/assignments/jwt/jwt.xhtml>,
  accessed 2026-10-04. It registers no tenant or organization claim. `tenant_id` is this platform's
  claim, as `org_id` and `tid` are their platforms'.
