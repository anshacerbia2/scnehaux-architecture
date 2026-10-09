---
doc_meta:
  id: ADR-IAM-008
  title: The Privileged Form Selected per Sign-In
  adr_type: foundational
  status: accepted
  created: 2026-10-07
  created_date: 2026-10-07
  created_by: Identity Platform Team
---

# ADR-IAM-008: The Privileged Form Selected per Sign-In

## 1. Title

The Privileged Form Selected per Sign-In.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-07 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

`SAD-012` gives one application, Organization Experience, two kinds of administrative work:

- **Tenant administration** inside one Tenant;
- **provider administration** across Tenants, entered deliberately and left again
  (`TDD-organization-experience-001`).

The tokens these two kinds of work need cannot be the same token:

- `STD-IAM-002 §3.1.1` says "A token MUST declare exactly one form".
- **The tenant-scoped form** carries `tenant_id`. `ADR-IAM-006 §5.2` puts it there per sign-in, from
  the scope `organization:<tenant_id>`.
- **The provider-scope form** MUST NOT carry `tenant_id`.

The registration authority cannot express an application that needs both:

- **A registration names one form.** `TDD-identity-control-003` (1.29.0) attaches either
  `scnehaux-provider` or `scnehaux-privileged` as a default scope.
- **Only the tenant-scoped form may ask for a Tenant.** `organization` is attached only to the
  tenant-scoped form (`ADR-IAM-006 §5.3`).
- **The consequence.** Organization Experience, registered for the provider-scope form, cannot sign
  a Tenant administrator in at all.

Four facts bound the choice:

- **The two forms are told apart only by `tenant_id`.**
  - The kernel declares `scnehaux-provider` and `scnehaux-privileged` with the same four mappers:
    `principal_id`, `subject_type`, `acr` and `auth_time`.
  - `tenant_id` comes only from the `organization` scope (`ADR-IAM-006 §5.3`).
  - The resource classifies the token by that claim, not by the scope's name. The Organization
    Control API takes a human token with `tenant_id` as a Tenant caller, and one without it as a
    provider candidate (`TDD-organization-control-001` §Caller Authority).
  - `STD-IAM-002 §3.5` step 9 refuses a token that carries both a Tenant and a provider authority.
- **The form confers no authority.** A provider-scope token reaches nothing until the resource
  finds an activation in force, or an emergency grant, for its `principal_id` (`ADR-ORG-002 §5.1`).
  A tenant-scoped token reaches nothing without an active Membership, an active Tenant and a Tenant
  administration grant (`ADR-ORG-003`).
- **OAuth puts scope in the request.**
  - "The authorization and token endpoints allow the client to specify the scope of the access
    request using the "scope" request parameter" [R1].
  - A refresh cannot widen it: "The requested scope MUST NOT include any scope not originally
    granted by the resource owner" [R1].
- **Established platforms let one client choose the context per request:**
  - Keycloak applies an optional client scope "only when requested by the scope parameter in the
    OpenID Connect authorization request" [R4]. A client asks for one organization with
    `organization:<alias>`, and the request "will be rejected" for a non-member [R4].
  - Auth0 selects the organization per request ("you pass an `organization` parameter in a call to
    the `/authorize` endpoint"). One application may take both kinds of sign-in: "Choose Both if your
    end user may maintain both a personal and business account with your application" [R5].
  - Microsoft's library chooses the tenant per token request: "it is useful to specify the Microsoft
    Entra tenant in the request builder instead of the application builder" [R6].
  - Azure Lighthouse has provider operators "sign in to their own tenant with authorization to work
    in delegated customer subscriptions", a token naming no customer, with the reach decided at the
    resource [R7].
  - No vendor source found requires a separate application for each context.

## 4. Decision Drivers

- **One application, one session, one form at a time.** The operator sees a single scope, and
  provider administration is entered and left in place (`TDD-organization-experience-001`).
- **Least privilege per token.** "The privileges associated with an access token SHOULD be
  restricted to the minimum required for the particular application or use case" [R2]. Every token
  carries one form, and the application asks for only the form the work needs.
- **The client checks what it was given.** Auth0's guidance: "on callback, ensure that the
  organization returned in the ID token is the same one that was sent in the `/authorize` request"
  [R5].
- **Elevation needs a fresh authentication.**
  - OpenID Connect `max_age` makes the provider "actively re-authenticate the End-User" [R3].
  - Entra Privileged Identity Management, to "enforce reauthentication on every role activation",
    sets the sign-in frequency to "Every time" [R8].
- **A registration states what its client may obtain.** A client that may obtain both forms is
  registered as such. Tenant-scoped clients do not gain the provider form by leaving a scope out.

## 5. Decision

### 5.1 A Registration May Name the `per-sign-in` Form

A `privileged` registration names one of three forms:

- `provider-scope`
- `tenant-scoped`
- `per-sign-in`, new. It is open only to the `confidential` profile: a backend that holds the tokens
  server-side, as `SAD-012 §4.4` and `TDD-identity-experience-001` require.

A `per-sign-in` client's scope sets are these:

| Set      | Scopes                                                                             |
| :------- | :--------------------------------------------------------------------------------- |
| Default  | `basic`, `acr`                                                                     |
| Optional | `scnehaux-provider`, `scnehaux-privileged`, `organization`, and `scnehaux-profile` |

No form scope is a default, so a token carries a form only when the request names one. A request
that names neither form gets a token without `principal_id`, and every resource refuses it
(`STD-IAM-002 §3.5`).

### 5.2 Each Sign-In Names Exactly One Form

| Work                    | Authorization request                                                                       |
| :---------------------- | :------------------------------------------------------------------------------------------ |
| Tenant administration   | `scnehaux-privileged organization:<tenant_id>`, for one Tenant                              |
| Provider administration | `scnehaux-provider`, with no `organization` scope, `acr_values=aal2` and `max_age=0` (§5.4) |

The rules for a request:

- **One form only.** A request never names both forms, never `organization` without
  `scnehaux-privileged`, and never `organization:*` or more than one Tenant. Keycloak refuses a
  request that mixes the `organization` formats [R4].
- **No chooser yet.** The bare `organization` scope, which has the kernel prompt the person to
  choose, is not used. Its behaviour against the pinned kernel is not asserted by `compat/`. Adopting
  it needs that assertion first.

### 5.3 The Client Checks the Form It Was Given

On the callback, before a session starts, the client refuses the sign-in:

- **For a Tenant sign-in**, unless the ID token's `tenant_id` equals the Tenant it asked for [R5].
- **For a provider sign-in**, if the ID token carries any `tenant_id`.

The application knows which form a session holds from this check, never from browser input
(`STD-IAM-001 §3.3`).

### 5.4 Switching Is a New Sign-In

**Changing the form or the Tenant is a new authorization request, never a refresh** [R1]. The
session it starts replaces the one before, which the BFF pattern already ends at every sign-in
(`TDD-identity-experience-001`).

**Entering the provider form is a step-up.** The request asks for `aal2` with `max_age=0`, and the
callback holds the ID token to both, as `ADR-IAM-004` does for a step-up:

- `acr` at `aal2` or above;
- `auth_time` no earlier than the request.

The authentication that opens provider administration therefore happens at the moment it opens. It
is not inherited from an earlier sign-in.

### 5.5 Authority Stays at the Resource

The form decides which records the resource reads. It grants nothing:

- **Provider administration** still needs an activation in force, requested with its reason and
  duration and approved by another provider (`ADR-ORG-002 §5.1`).
- **Tenant administration** still needs the Tenant administration grant (`ADR-ORG-003`).

An application that leaves provider administration ends the activation, so authority never
outlives the work it was opened for.

### 5.6 A Tenant Sign-In on an Existing Session Is Answered by the Session (2026-10-09)

§6 says "Within the SSO session a Tenant switch needs no credential". Against the pinned kernel it
did not hold: a Tenant sign-in on the session of a provider sign-in got the kernel's error page,
"Invalid username or password", while the same request in a new browser succeeded. Organization
Experience's stack proof found it, and `compat/` in identity-kernel reproduced it on an `aal1`
session made without `max_age` too. The cause is the `organization` scope on a session, not
`max_age=0` and not the level.

- **Why the kernel refused.** The kernel's _Cookie_ step does not finish a sign-in that names an
  Organization. It attaches the session and leaves the Organization to a later step: "if
  re-authenticating in the scope of an organization, an organization must be resolved prior to
  authenticating the user" [R10]. Keycloak adds that step, _Organization Identity-First Login_, only
  to the flows it creates for a realm: "When a realm is created, the authentication flows are
  automatically updated", but "you also need to manually update your existing (custom)
  authenticating flows" [R9]. The kernel's browser flow is its own and had no such step. Its forms
  had nothing left to ask, so the flow ended without success, and Keycloak reports an unsuccessful
  flow as invalid credentials [R10].
- **The kernel's browser flow adds the organization step between the cookie and the forms.** On a
  session, the step resolves the Organization the request names and completes the sign-in: "if
  re-authenticating in the scope of an organization" it succeeds [R10]. It is a conditional
  sub-flow that runs only when both conditions hold:
  - the request asks for the `organization` scope;
  - a person is already identified, by the session: the condition is the realm's default role,
    which Keycloak assigns "when any user is newly created" [R9], and a role condition with no user
    is false [R10].
- **Not Keycloak's own condition.** Keycloak's procedure guards the step with _Condition - user
  configured_ [R9], which is true for this step with no user. Every sign-in in a new browser would
  then meet the identity-first page, since "The main change to the _browser_ flow is that it
  defaults to an identity-first login so that users are identified before prompting for their
  credentials" [R9]. The realm has no identity provider or domain routing to use that page for, so
  the role condition keeps the step to a session.
- **A step-up still asks.** Past `max_age`, or with `prompt=login`, the cookie does not answer the
  sign-in, the organization step defers as well, and the forms ask for what the level needs. OpenID
  Connect requires it: past `max_age`, "the OP MUST attempt to actively re-authenticate the
  End-User", and with `prompt=login` "the Authorization Server MUST reauthenticate the End-User even
  if the End-User is already authenticated" [R3]. A session is otherwise a way the provider may
  authenticate: "The methods used by the Authorization Server to Authenticate the End-User (e.g.,
  username and password, session cookies, etc.) are beyond the scope of this specification" [R3].
  Entering the provider form (§5.4) is unchanged.
- **A non-member is refused, as in a new browser.** `organization:<tenant_id>` resolves to nothing
  for a person who is not a member, so the step does not run and the request "will be rejected"
  [R4].
- **Nothing changes in a consumer.** The BFFs already send §5.2's requests and need no
  `prompt=login`.

`compat/` in identity-kernel asserts it against the pinned kernel: a Tenant sign-in on a provider
sign-in's session is answered without a page and carries the Tenant; a provider sign-in after it
carries none; `max_age=0` asks for the password and the code; a non-member gets no token
(`TDD-identity-kernel-001` 1.18.0 §Authentication Levels).

## 6. Consequences

### Positive

- One application serves both kinds of work. Its operator holds one form at a time, and holds the
  provider form only after a fresh `aal2` authentication.
- No token changes: the kernel's scopes and mappers are those `ADR-IAM-006` already proves.
- Tenant-scoped and provider-scope clients keep their closed scope sets. Only a registration that
  says `per-sign-in` can obtain both.

### Negative

- **The kernel does not enforce one form per request.** A `per-sign-in` client could ask for both
  form scopes, or for `scnehaux-provider` with `organization`. Two things contain it:
  - the client is a confidential backend whose requests are code, checked by its own callback
    (§5.3);
  - a resource refuses a token carrying both a Tenant and a provider authority (`STD-IAM-002 §3.5`
    step 9).
- **Switching costs a round trip.** It is a round trip to the kernel. Within the SSO session a Tenant
  switch needs no credential, but entering the provider form always asks for one.

### Operational

- identity-control accepts `per-sign-in`, attaches §5.1's sets, and its reconciler holds them closed.
- `compat/` in identity-kernel asserts, against the pinned kernel, that one client holding §5.1's
  sets gets each form from §5.2's requests, with `tenant_id` in the ID token for the Tenant form and
  none for the provider form.

## 7. Compliance Impact

### Related Standards

- `STD-IAM-002` 1.7.0 §3.1.1: the `per-sign-in` registration, and the one-form-per-request rule.
- [ADR-IAM-006](ADR-IAM-006-tenant-context-in-tokens.md) §5.3: the `organization` scope is also held
  by a `per-sign-in` client, which asks for it only with `scnehaux-privileged`.
- [ADR-IAM-004](ADR-IAM-004-authentication-assurance-and-step-up.md): entering the provider form is
  a step-up.
- `TDD-identity-control-003`, `TDD-identity-experience-001`, `TDD-organization-experience-001`
  and `TDD-identity-kernel-001` change to implement it.

### Compliance Status

Compliant once identity-control registers `per-sign-in` and identity-kernel's `compat/` asserts §5.2
and §5.3. The BFF pattern must also select and check the form per sign-in.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Two Clients, One per Form

**Benefits:**

- The registration authority keeps one form per client.
- The kernel then enforces the form, because each client holds one default form scope.

**Rejected because:**

- No vendor source requires it. Each of [R4] to [R7] chooses the context per request on one client.
- It isolates nothing. The two scopes emit the same claims, and the authority is the resource's
  record either way (§5.5).
- It doubles the registrations, keys, redirect URIs and back-channel logout endpoints of one
  application. The BFF would also have to refresh and log out through whichever client issued each
  session.

### Alternative B — Two Applications

**Benefits:**

- Each application has one client and one form, so neither the BFF pattern nor the registration
  changes.

**Rejected because:**

- Provider administration becomes another application, not a mode the operator enters and leaves.
  That gives up `TDD-organization-experience-001`'s single scope banner and its in-place entry
  ceremony.
- Lighthouse's provider operators work in the same portal they use for their own tenant [R7].

### Alternative C — A Tenant-Scoped Client That Omits `organization` for Provider Work

**Benefits:** no registration change. A tenant-scoped client's token without `organization` already
carries the provider form's claims.

**Rejected because:**

- Every tenant-scoped client could then obtain a provider-form token by leaving a scope out.
  [R2] asks for the minimum privilege per token, and the registration should say what a client may
  obtain.

### Alternative D — The Kernel's Organization Chooser

**Benefits:** a person in several Tenants picks one on the kernel's page, with no identifier typed or
linked.

**Deferred because:**

- `compat/` does not assert it against the pinned kernel (§5.2).
- It can be adopted by its own amendment once asserted. The Tenant would then be checked against the
  person's Memberships rather than against a request value.

## 9. References

### Normative

- **[R1]** IETF RFC 6749, _The OAuth 2.0 Authorization Framework_, October 2012.
  <https://www.rfc-editor.org/rfc/rfc6749>.
  - §3.3: "The authorization and token endpoints allow the client to specify the scope of the access
    request using the "scope" request parameter."
  - §6: "The requested scope MUST NOT include any scope not originally granted by the resource owner,
    and if omitted is treated as equal to the scope originally granted by the resource owner."
- **[R2]** IETF RFC 9700 (BCP 240), _Best Current Practice for OAuth 2.0 Security_, January 2025.
  <https://www.rfc-editor.org/rfc/rfc9700>. §2.3: "The privileges associated with an access token
  SHOULD be restricted to the minimum required for the particular application or use case."
- **[R3]** OpenID Foundation, _OpenID Connect Core 1.0 incorporating errata set 2_, December 2023.
  <https://openid.net/specs/openid-connect-core-1_0.html>, accessed 2026-10-09.
  - §3.1.2.1 `max_age`: "If the elapsed time is greater than this value, the OP MUST attempt to
    actively re-authenticate the End-User"; "Note that max_age=0 is equivalent to prompt=login."
    `prompt=login`: "The Authorization Server SHOULD prompt the End-User for reauthentication."
  - §3.1.2.3: "the Authorization Server attempts to Authenticate the End-User or determines whether
    the End-User is Authenticated, depending upon the request parameter values used. The methods
    used by the Authorization Server to Authenticate the End-User (e.g., username and password,
    session cookies, etc.) are beyond the scope of this specification." When "The Authentication
    Request contains the prompt parameter with the value login. In this case, the Authorization
    Server MUST reauthenticate the End-User even if the End-User is already authenticated."

### Informative

- **[R4]** Keycloak, _Server Administration Guide_, accessed 2026-10-07.
  <https://www.keycloak.org/docs/latest/server_admin/index.html>.
  - _Link client scope with the client_: "Optional client scopes are applied when issuing tokens for
    this client but only when requested by the scope parameter in the OpenID Connect authorization
    request."
  - _Mapping organization claims_, `organization:<alias>`: "Maps to a specific organization with the
    given alias … If any of the aliases does not match an existing organization or the user is not a
    member, the request will be rejected."
  - The same section: "Mixing different scope formats (for example, organization with
    organization:org-a, or organization:org-a with organization:\*) is not allowed and will result in
    an error."
- **[R5]** Auth0, accessed 2026-10-07.
  - _Use Organizations with tokens_, <https://auth0.com/docs/manage-users/organizations/using-tokens>:
    "To authenticate a user through an Organization, you pass an `organization` parameter in a call to
    the `/authorize` endpoint."
  - _Custom development_, <https://auth0.com/docs/manage-users/organizations/custom-development>: "on
    callback, ensure that the organization returned in the ID token is the same one that was sent in
    the /authorize request by validating the org_id claim in the same way that other claims like exp
    and nonce are validated."
  - _Login flows for Organizations_,
    <https://auth0.com/docs/manage-users/organizations/login-flows-for-organizations>: "Choose Both if
    your end user may maintain both a personal and business account with your application."
- **[R6]** Microsoft, _Overriding authority_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/entra/msal/dotnet/how-to/overriding-authority>: "In many
  scenarios, such as client credential flow in multi-tenant apps, it is useful to specify the
  Microsoft Entra tenant in the request builder instead of the application builder."
- **[R7]** Microsoft, _Azure Lighthouse architecture_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/azure/lighthouse/concepts/architecture>: "This lets authorized
  service provider users sign in to their own tenant with authorization to work in delegated
  customer subscriptions and resource groups."
- **[R8]** Microsoft, _Configure Microsoft Entra role settings in Privileged Identity Management_,
  accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings>:
  "To enforce reauthentication on every role activation, configure the Conditional Access policy
  targeting your authentication context with sign-in frequency set to Every time under Session
  controls."
- **[R9]** Keycloak 26.7.5, _Server Administration Guide_, _Authenticating members_, source
  `docs/documentation/server_admin/topics/organizations/authenticating-members.adoc` at tag 26.7.5,
  accessed 2026-10-09.
  <https://github.com/keycloak/keycloak/blob/26.7.5/docs/documentation/server_admin/topics/organizations/authenticating-members.adoc>.
  "When a realm is created, the authentication flows are automatically updated to enable specific
  steps to authenticate and onboard organization members"; "The main change to the _browser_ flow is
  that it defaults to an identity-first login so that users are identified before prompting for
  their credentials"; for existing realms "you also need to manually update your existing (custom)
  authenticating flows". The procedure adds a sub-flow "right after the _Identity Provider
  Redirector_ execution step", with _Condition - user configured_ and the _Organization
  Identity-First Login_ step. _Default roles_, source `topics/roles-groups/con-default-roles.adoc`:
  "Default roles allow you to automatically assign user role mappings when any user is newly created
  or imported through Identity Brokering."
- **[R10]** Keycloak 26.7.5 source, <https://github.com/keycloak/keycloak/tree/26.7.5>, read
  2026-10-09.
  - `services/.../authentication/authenticators/browser/CookieAuthenticator.java`, `authenticate`:
    "context.attachUserSession(authResult.session()); if (isOrganizationContext(context)) { // if
    re-authenticating in the scope of an organization, an organization must be resolved prior to
    authenticating the user context.attempted(); } else { context.success(); }".
  - `services/.../organization/authentication/authenticators/browser/OrganizationAuthenticator.java`,
    `action`: "if (isSSOAuthentication(authSession)) { // if re-authenticating in the scope of an
    organization context.success(); } else { attempted(context, username); }".
  - `services/.../authentication/AuthenticationProcessor.java`: an unsuccessful flow throws "new
    AuthenticationFlowException(authenticationFlow.getFlowExceptions())", answered by
    "event.error(Errors.INVALID_USER_CREDENTIALS)" and "ErrorPage.error(session,
    authenticationSession, Response.Status.BAD_REQUEST, Messages.INVALID_USER)".
  - `services/.../authentication/authenticators/conditional/ConditionalRoleAuthenticator.java`,
    `matchCondition`: "if (user != null && authConfig!=null && authConfig.getConfig()!=null) { … return
    negateOutput != user.hasRole(role); } return false;". `ConditionalUserConfiguredAuthenticator`:
    "if (authenticator.requiresUser() && context.getUser() == null) { return false; } return
    authenticator.configuredFor(context.getSession(), context.getRealm(), context.getUser());".
