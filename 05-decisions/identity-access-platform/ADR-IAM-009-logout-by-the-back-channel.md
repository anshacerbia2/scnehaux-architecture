---
doc_meta:
  id: ADR-IAM-009
  title: Logout Reaches a Relying Party by the Back Channel
  adr_type: foundational
  status: accepted
  created: 2026-10-08
  created_date: 2026-10-08
  created_by: Identity Platform Team
---

# ADR-IAM-009: Logout Reaches a Relying Party by the Back Channel

## 1. Title

Logout Reaches a Relying Party by the Back Channel.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-08 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

A session ended in the identity kernel has to end at every relying party that holds a session of its own. OpenID Connect defines three ways to tell a relying party: front-channel logout, where the provider renders the relying party's logout URI in an iframe in the user's browser [R1]; back-channel logout, where the provider posts a signed logout token to the relying party directly [R2]; and session management, where the relying party polls the provider from an iframe of its own [R1].

`TDD-identity-experience-001` names front-channel logout among the duties of its `LogoutController` and specifies no endpoint for it. The same design sends `frame-ancestors 'none'` on every page, which refuses the frame front-channel logout needs, and its session cookie is `SameSite=Lax`. It receives back-channel logout at `POST /auth/back-channel-logout`, but no repository registers that URL on a client: neither the Identity Control Service's registration nor any script writes it. Every relying party therefore relies on the refresh path alone, which `STD-IAM-001 §3.4` bounds by the remaining access token lifetime.

Three facts decide the question:

- **The kernel ends sessions without a browser.** The Identity Control Service removes sessions through the Admin API when a person ends one of their own or all of them, and when a provider suspends a Principal or ends its sessions (`TDD-identity-control-005`). A Membership revocation removes no session; it refuses the Tenant's refresh (`ADR-IAM-006 §5.5`). Keycloak can tell a relying party about such a removal only by the back channel: front-channel logout "is not supported" when "session of the specific user is logged-out by the administrator", because "Keycloak can propagate logout to the client by front-channel just when the logout is triggered in the same browser session, which is being logged out" [R3].
- **The pinned kernel does one or the other for each client.** In Keycloak 26.7.5 a client with front-channel logout on is skipped by the back-channel path (`AuthenticationManager.backchannelLogoutClientSession` returns before sending), and its back-channel URL "is applicable just if Front channel logout option is OFF" [R3], [R4]. Turning front-channel logout on for a client would remove the only notification that reaches it on an administrative removal.
- **Browsers no longer give a cross-site frame its cookies.** Safari blocks "cookies for cross-site resources … by default across the board" [R5]. Firefox "double-keys all client-side state by the origin of the resource being loaded and by the top-level site" [R6]. A `SameSite=Lax` cookie is not sent on "navigations inside `<iframe>` elements" [R7]. The front-channel specification says so of itself: the logout URI "might not be able to access the RP's login state when rendered by the OP in an iframe", while back-channel logout "is not known to be affected by these developments" [R1].

## 4. Decision Drivers

- **A session removal reaches the relying party whoever ended the session**, the person or a provider, and whether or not the person's browser is open.
- **The notification is authenticated.** A relying party acts only on a request the kernel signed.
- **No relying party weakens its browser defences** (frame ancestors, `SameSite`) to receive one.
- **The refresh path stays the bound**, so a lost notification never extends access (`STD-IAM-001 §3.4`).

## 5. Decision

### 5.1 A Server-Side Relying Party Registers a Back-Channel Logout URI

A `confidential` client, which keeps its sessions server-side, may register a `backchannel_logout_uri` with the Identity Control Service, which records it as desired state. The service writes it to the kernel client as the client's back-channel logout URL, with "Backchannel logout session required" on, so the logout token names the session by `sid` [R2], [R3], and with offline-session revocation off. A relying party that holds sessions and that the kernel can reach registers one.

- **Only a confidential client registers one.** The specification defines the URI as an "RP URL that will cause the RP to log itself out when sent a Logout Token" [R2]. A `public` client has no back end to receive it, and a `workload` or a `resource` holds no person's session.
- **It is an absolute URI without a fragment**, as the specification requires [R2]. It is `https` in production. Outside production it may be `http`: the specification permits `http` "provided that the Client Type is confidential" and the provider allows it [R2], and a development kernel reaches its relying parties over a private network.
- **The drift sweep holds it**, with front-channel logout off (§5.2), as one field class. A URL changed or removed in the console is a notification that no longer arrives, so it is repaired when the change is attributed, as a token lifespan is.

### 5.2 No Client Uses Front-Channel Logout

Every client the Identity Control Service creates, adopts or recreates has front-channel logout off, written explicitly rather than left to the Admin API's default, and the sweep repairs a client on which it was turned on. `TDD-identity-experience-001` keeps `frame-ancestors 'none'` and its `SameSite=Lax` cookie, and specifies no front-channel endpoint.

### 5.3 A Relying Party the Kernel Cannot Reach Registers None

The specification states the limit: the URI "must be reachable from all the OPs used", so "the RP cannot be behind a firewall or NAT" [R2]. A BFF run on a developer's machine against the development kernel is such a relying party. It registers no URI, and a session removed in the kernel ends at its next refresh, within the remaining lifetime of the access token it holds. That is the bound `STD-IAM-001 §3.4` states for every relying party, so nothing is lost but the speed.

### 5.4 Sign-Out Stays Server-Side

A person's sign-out from a BFF ends the kernel session server-side, as `TDD-identity-experience-001` specifies. RP-initiated logout through the browser is not adopted: its `id_token_hint` is "RECOMMENDED" and is the ID token itself [R8], which the BFF never gives the browser, and without it the specification has the provider "obtain explicit confirmation from the End-User" [R8]. Ending the kernel session server-side then reaches every other relying party of that session by §5.1: the kernel's logout endpoint sends the back channel for a non-browser logout as its Admin API does [R4].

## 6. Consequences

### Positive

- A person's own session removal and a provider's containment reach a reachable BFF within the kernel's request, not at the next refresh. A Membership revocation, which removes no session, still reaches it at the refresh the kernel refuses (`ADR-IAM-006 §5.5`).
- No page is framed, and no cookie is relaxed, to receive a logout.
- A logout request is a signed token the relying party verifies (`TDD-identity-experience-001`), never an unauthenticated `GET` whose only protection is the entropy of a session identifier [R1].

### Negative

- **Delivery is best effort.** The provider "should not retransmit" except after a recoverable error [R2], so a relying party that was down misses the notification. The refresh path still bounds the session, which `TDD-identity-experience-001` proves without any notification delivered.
- **The kernel sends it inside the removal.** Keycloak 26.7.5 calls the back channel within the Admin API request that removes the session [R4], so a slow or unreachable URI lengthens the removal the Identity Control Service waits on.
- **A relying party on a developer's machine gets none** (§5.3), so the development stacks exercise only the refresh path, and the back channel is proved where the kernel can reach the receiver: identity-kernel's compatibility suite and identity-control's `deploy-dev` job.

### Operational

- `TDD-identity-experience-001`'s back-channel logout runbook starts from whether the client's registration names a URI.
- A changed back-channel URL or front-channel setting is a drift finding.

## 7. Compliance Impact

### Related Standards

- STD-IAM-001 §3.4 — the enforcement delay a lost notification falls back to, and the rule this decision adds.
- STD-IAM-002 §3.2 — `sid` in the access token, the session the logout token names.
- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.12 — the registration authority that writes the client.
- [ADR-IAM-006](ADR-IAM-006-tenant-context-in-tokens.md) §5.5 — a Membership revocation removes no session, and is bounded by the refresh path alone.

### Compliance Status

Compliant. `STD-IAM-001 §3.4` states the rule in the same change.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Front-Channel Logout Beside the Back Channel

**Benefits:** a browser-initiated logout at the kernel clears a relying party that cannot be reached by the back channel, such as a developer's BFF.

**Rejected because:** the pinned kernel does one or the other for a client, so turning it on removes the back channel for every administrative removal [R3], [R4]. It also needs the BFF to be framed by the kernel's origin and to read its session in that frame, which `frame-ancestors 'none'`, `SameSite=Lax` and every major browser's partitioning refuse [R5], [R6], [R7].

### Alternative B — OpenID Connect Session Management

**Benefits:** a single-page application learns of a logout without a back end.

**Rejected because:** it is the same iframe and third-party state the browsers partition [R1], [R6], and no Scnehaux browser application holds tokens (`STD-IAM-001 §3.9`), so none has the session state it polls.

### Alternative C — The Refresh Path Alone

**Benefits:** nothing to register; the bound already holds.

**Rejected because:** the bound is the slow path. A provider containing a compromised account wants the BFF session gone now, and `TDD-identity-experience-001` registers the back channel "for exactly that reason". With no URL registered, the containment runbook has to delete BFF sessions by hand.

### Alternative D — A Notification from the Identity Control Service

**Benefits:** the service already knows when it removes a session, and could call each BFF itself.

**Rejected because:** the kernel already sends a signed, standard logout token for every removal, including those made in its own console or by its own expiry. A second, proprietary notification would duplicate it, need its own signing and verification, and still miss the removals the service does not make.

## 9. References

### Normative

- **[R1]** OpenID Foundation, _OpenID Connect Front-Channel Logout 1.0_, Final, September 12, 2022. <https://openid.net/specs/openid-connect-frontchannel-1_0.html>, accessed 2026-10-08.
  - Abstract: it "uses front-channel communication via the User Agent between the OP and RPs being logged out".
  - §4.1 User Agents Blocking Access to Third-Party Content: "the frontchannel_logout_uri might not be able to access the RP's login state when rendered by the OP in an iframe because the iframe is in a different origin than the OP's page"; "OpenID Connect Back-Channel Logout 1.0 [OpenID.BackChannel] is not known to be affected by these developments."
  - §5 Security Considerations: "Collisions between Session IDs and the guessing of their values by attackers are prevented by including sufficient entropy in Session ID values."
- **[R2]** OpenID Foundation, _OpenID Connect Back-Channel Logout 1.0 incorporating errata set 1_, December 15, 2023. <https://openid.net/specs/openid-connect-backchannel-1_0.html>, accessed 2026-10-08.
  - §1: "An upside of back-channel communication is that it can be more reliable than communication through the User Agent, since in the front-channel, the RP's browser session must be active for the communication to succeed."
  - §1: "Another significant limitation of back-channel logout is that the RP's back-channel logout URI must be reachable from all the OPs used. This means, for instance, that the RP cannot be behind a firewall or NAT when used with public OPs."
  - §2.2: "The back-channel logout URI MUST be an absolute URI as defined by Section 4.3 of [RFC3986]"; "The back-channel logout URI MUST NOT include a fragment component." `backchannel_logout_uri`: "RP URL that will cause the RP to log itself out when sent a Logout Token by the OP. This URL SHOULD use the https scheme … however, it MAY use the http scheme, provided that the Client Type is confidential, as defined in Section 2.1 of OAuth 2.0 [RFC6749], and provided the OP allows the use of http RP URIs." `backchannel_logout_session_required`: "Boolean value specifying whether the RP requires that a sid (session ID) Claim be included in the Logout Token".
  - §2.5: "The OP should not retransmit a Back-Channel Logout Request unless the OP suspects that previous transmissions may have failed due to potentially recoverable errors."
- **[R8]** OpenID Foundation, _OpenID Connect RP-Initiated Logout 1.0_, Final, September 12, 2022. <https://openid.net/specs/openid-connect-rpinitiated-1_0.html>, accessed 2026-10-08. §2 `id_token_hint`: "RECOMMENDED. ID Token previously issued by the OP to the RP passed to the Logout Endpoint as a hint about the End-User's current authenticated session with the Client." §6: "Logout requests without a valid id_token_hint value are a potential means of denial of service; therefore, OPs should obtain explicit confirmation from the End-User before acting upon them."

### Informative

- **[R3]** Keycloak, _Server Administration Guide_ 26.7.5, <https://www.keycloak.org/docs/26.7.5/server_admin/index.html>, accessed 2026-10-08.
  - _OIDC Logout_, Front-channel Logout: "Logout requests sent by Keycloak to clients rely on the browser and on embedded iframes that are rendered for the logout page. By being based on iframes, front-channel logout might be impacted by Content Security Policies (CSP) and logout requests might be blocked"; "Consider using Back-Channel Logout as it provides a more reliable and secure approach to log out users and terminate their sessions on the clients."
  - _OIDC Logout_, Backchannel Logout: "when the Keycloak logout of specified user is triggered by the administrator from the Admin console (or other use of admin REST API) or by the actual user from the Account console, then Keycloak can propagate a backchannel logout request to the client applications attached to the session being logged out. This scenario is not supported in case of Front-Channel logout because Keycloak can propagate logout to the client by front-channel just when the logout is triggered in the same browser session, which is being logged out."
  - _Logout settings_, Backchannel logout URL: "This option is applicable just if Front channel logout option is OFF." Backchannel logout session required: "Specifies whether a session ID Claim is included in the Logout Token when the Backchannel Logout URL is used."
- **[R4]** Keycloak 26.7.5 source, <https://github.com/keycloak/keycloak/tree/26.7.5>, read 2026-10-08. `services/.../managers/AuthenticationManager.java`, `backchannelLogoutClientSession`: `if (client.isFrontchannelLogout() || …) { return null; }`. `services/.../resources/admin/RealmAdminResource.java`, `deleteSession` ("Remove a specific user session"), calls `AuthenticationManager.backchannelLogout(...)` before it answers, as `protocol/oidc/endpoints/LogoutEndpoint.java` does for a client's non-browser logout with its refresh token (`logout(userSession, offline)`). `services/.../protocol/oidc/OIDCLoginProtocolFactory.java`: a client created through the Admin API with no `frontchannelLogout` gets `setFrontchannelLogout(false)`, and with no back-channel URL gets "session required" `true` and "revoke offline tokens" `false`. `services/.../jose/jws/DefaultTokenManager.java`: a logout token is signed with the client's ID token algorithm and typed `logout+jwt`.
- **[R5]** WebKit, John Wilander, _Full Third-Party Cookie Blocking and More_, March 24, 2020. <https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/>, accessed 2026-10-08. "Cookies for cross-site resources are now blocked by default across the board."
- **[R6]** MDN Web Docs, _State Partitioning_, accessed 2026-10-08. <https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/State_Partitioning>. "Firefox provides embedded resources with a separate storage bucket for every top-level website. More specifically, Firefox double-keys all client-side state by the origin of the resource being loaded and by the top-level site." "Dynamic Partitioning: Enabled by default for all users since Firefox 103."
- **[R7]** MDN Web Docs, _Set-Cookie_, `SameSite=Lax`, accessed 2026-10-08. <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie>. Cross-site requests carry the cookie only for a top-level navigation, which "would exclude, for example, requests made using the fetch() API, or requests for subresources from `<img>` or `<script>` elements, or navigations inside `<iframe>` elements."
