---
doc_meta:
  id: STD-GLB-FE-003
  title: Enterprise Frontend Security Standard
  owner: Enterprise Security Architect
  version: 2.1.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-08
---

# Enterprise Frontend Security Standard (STD-GLB-FE-003)

## 1. Objective & Scope

Define mandatory browser and frontend security controls for Scnehaux web applications across privileged/admin, internal, client-facing, and public application profiles.

The browser is an untrusted execution environment. Frontend controls improve safety and user experience but never become the final authority for authentication, Tenant/Membership truth, entitlement, or business authorization.

## 2. Design Principles

- **Server authority** — authentication/session and business authorization are enforced by trusted server-side components
- **Least bearer exposure** — avoid exposing long-lived bearer credentials to browser JavaScript
- **Requested context is not authority** — tenant/workspace values supplied by the browser are hints that must be validated against authoritative or trusted projected context
- **Cache isolation** — user, tenant, and workspace changes invalidate or partition cached data deterministically
- **Defense in depth** — CSP, output encoding, secure cookies, dependency controls, and safe DOM practices reduce browser compromise impact

## 3. Normative Rules

### 3.1 Application Security Profiles

- Privileged and administrative applications SHOULD use a BFF or server-managed session profile when practical
- Server-managed session cookies MUST be `HttpOnly`, `Secure`, and use an appropriate `SameSite`, path, domain, and expiry policy
- Direct browser OAuth clients MAY be used when justified but MUST use Authorization Code + PKCE `S256`, no client secret, and the approved public-client token profile
- Refresh tokens or equivalent long-lived bearer secrets MUST NOT be stored in `localStorage`
- Sensitive authentication/session material MUST NOT be logged, persisted in analytics payloads, or exposed through client error telemetry

### 3.2 Tenant & Operating-Context Isolation

- Browser-supplied tenant, workspace, account, or operating-context identifiers are **requested context**, not authorization proof
- The backend MUST resolve and validate requested context against trusted token claims, server session, or bounded authoritative projection
- Switching Principal, Tenant, Workspace, or other authority context MUST invalidate or partition server-state caches and sensitive client state
- Query/cache keys for tenant-scoped data MUST include the validated context boundary where client caching is used
- Sensitive cross-context data MUST NOT remain renderable after a context switch

### 3.3 Authorization in the UI

- Client-side permission checks are UX and defense-in-depth only
- Protected backend actions MUST independently authorize the authenticated Principal and validated operating context
- UI gates MUST fail closed while permission/context state is unresolved
- The frontend MUST NOT infer business permission solely from route, menu visibility, hidden controls, or untrusted local state

### 3.4 Browser Storage

- `localStorage` MUST NOT hold access tokens, refresh tokens, passwords, recovery codes, private keys, or equivalent bearer secrets
- `sessionStorage` MAY hold non-secret ephemeral UI state; storing access tokens requires an explicitly approved direct-browser token profile
- IndexedDB or other persistent browser storage containing sensitive domain data requires explicit data-classification, encryption/lifecycle, and offline-access justification
- Preference storage MUST be partitioned where cross-tenant leakage could reveal sensitive context

### 3.5 Browser Defenses

- Applications MUST deploy a restrictive, application-specific Content Security Policy
- Clickjacking protection MUST use CSP `frame-ancestors` and/or equivalent approved controls
- A BFF-served application keeps `form-action 'self'`, and a control that starts a sign-in is a navigation, a link or a script setting the location, never a form submitted to the BFF's sign-in route (2.1.0). That route answers with a redirect to the identity kernel, and Chrome checks the redirect's target against `form-action`: GitLab found that Chrome "takes the redirection target into account when evaluating CSP violations" [R3]. MDN: "Whether `form-action` should block redirects after a form submission is debated and browser implementations of this aspect are inconsistent (e.g., Firefox 57 doesn't block the redirects whereas Chrome 63 does)" [R1], and the question has been open in the specification since 2015 [R2]. A form there is refused in Chrome and works elsewhere.
  - _Rejected: widening `form-action` to the kernel's origin._ The policy is the BFF pattern's, the same for every application, and the kernel's origin is each deployment's own. A form that may submit off the origin is what the directive exists to stop.
  - _Found by_ organization-experience's stack-level proof, which signs in through Chromium (STD-GLB-FE-008 §3.4): its Tenant sign-in form was refused before it reached the kernel, and no test without a browser could see it.
  - _Residual risk._ A form whose answer redirects off the origin still passes every test that runs no browser, and every browser but Chrome. Only a browser journey through the redirect finds one.
- `X-Content-Type-Options: nosniff` and an approved `Referrer-Policy` are required for external web applications
- Unsafe HTML insertion is prohibited unless content is sanitized by an approved boundary
- Dependencies and build artifacts MUST pass software-supply-chain security checks

### 3.6 Network & Resource Safety

- Requests SHOULD support cancellation where stale in-flight work could update invalid UI state
- Retries MUST be bounded and based on operation semantics, idempotency, and business risk
- Authentication/session renewal MUST use one coordinated mechanism appropriate to the application's security profile
- Frontend network code MUST NOT implement a second independent identity/session engine

## 4. Exceptions

Deviations require formal exception approval under GDC-000 with threat model, compensating controls, and explicit ownership.

## 5. Enforcement Mechanism

- ESLint/static checks for prohibited browser credential storage and unsafe DOM usage
- E2E suites for Principal/Tenant/Workspace switching and cache isolation
- security-header and CSP tests
- browser OAuth/BFF profile conformance tests
- backend authorization tests proving UI controls are non-authoritative

## 6. References

- **[R1]** MDN Web Docs, _Content-Security-Policy: form-action directive_, accessed 2026-10-08. <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/form-action>. "The HTTP Content-Security-Policy (CSP) `form-action` directive restricts the URLs which can be used as the target of form submissions from a given context"; "Whether `form-action` should block redirects after a form submission is debated and browser implementations of this aspect are inconsistent (e.g., Firefox 57 doesn't block the redirects whereas Chrome 63 does)." Supports §3.5.
- **[R2]** W3C WebAppSec, issue #8, _CSP: form-action and redirects_, open since 2015-10-07, accessed 2026-10-08. <https://github.com/w3c/webappsec-csp/issues/8>. "Perform some action by doing a `POST` to `self`"; "Based on request params/backend state, redirect the user to another site." W3C, _Content Security Policy Level 3_, §6.4.1: "The form-action directive restricts the URLs which can be used as the target of a form submissions from a given context", <https://www.w3.org/TR/CSP3/>. Supports §3.5.
- **[R3]** GitLab, merge request 90082, _Allowlist OAuth application redirect URI in CSP_, merged 2022-06-17, accessed 2026-10-08. <https://gitlab.com/gitlab-org/gitlab/-/merge_requests/90082>. "our OAuth page submits the form to `/oauth/authorize` however the page immediately redirects to the OAuth application's `redirect_uri` and Chrome takes the redirection target into account when evaluating CSP violations." Supports §3.5.
