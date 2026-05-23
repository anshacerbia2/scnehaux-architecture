---
doc_meta:
  id: STD-E010
  title: Enterprise Frontend Security Standard
  owner: Enterprise Security Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# Enterprise Frontend Security Standard (STD-E010)

---

## 1. Objective & Scope

This standard defines the mandatory security controls, runtime mitigations, and multi-tenant isolation rules for all browser-executed Single Page Applications (SPAs) within the Scnehaux enterprise ecosystem. It establishes the browser not merely as a presentation layer, but as a critical execution runtime requiring zero-trust discipline.

The scope of this standard applies to all client-side storage, outbound API communications, rendering logic, and local data persistence.

---

## 2. Multi-Tenant Isolation

Cross-tenant data leakage on the client side is a critical security vulnerability. All frontends must enforce structural boundaries to prevent contamination.

- **Tenant-Scoped Storage**: Global browser storage (`sessionStorage`, `localStorage`) is shared across the origin. Therefore, all sensitive state keys (tokens, preferences) must be dynamically prefixed with the active tenant ID (e.g., `auth_token:{tenant_id}`).
- **Query Cache Purging**: To guarantee complete eviction of stale data, the application's central data fetching cache (e.g., React Query's `QueryClient`) must be programmatically cleared upon any tenant context switch (`queryClient.clear()`).
- **Header Injection**: All outgoing HTTP requests must automatically inject the `Scnehaux-Account` header identifying the active tenant context.
- **Query Key Segregation**: All internal cache keys must include the `tenantId` as the first segment to prevent accidental cross-tenant cache hits (e.g., `[tenantId, 'users', 'list']`).

---

## 3. Token & Session Security

- **Token Refresh Mutex Queue**: To prevent Refresh Token Rotation (RTR) theft-detection false positives, HTTP interceptors must implement a single-flight mutex lock. Concurrent 401 Unauthorized responses must be queued behind a single refresh network request, and replayed once the new token is acquired.
- **Epoch Validation**: Frontends must parse the `epc` (epoch) claim in JWTs and gracefully terminate the session if the backend signals a global epoch revocation.
- **Storage Preference**: Access tokens must prioritize in-memory storage. If persistence is required for cross-tab continuity, it must be restricted to `sessionStorage` (never `localStorage`) and scoped to the tenant.

---

## 4. Authorization & Policy Execution

- **Policy Evaluator Bounds**: Client-side authorization logic must utilize a bounded cache (e.g., LRU Cache) for permission decisions to prevent memory leaks in long-running administrative sessions.
- **Explicit DENY-First**: The policy engine must evaluate explicit `DENY` rules before checking `ALLOW` grants or roles.
- **Render-Nothing-While-Loading**: Authorization gate components (e.g., `PermissionGate`) must return `null` while evaluating permissions. Optimistic rendering of protected UI elements is strictly prohibited to prevent authorization state leakage.

---

## 5. Network & Resource Management

- **Lifecycle Binding**: All outbound HTTP requests must be bound to the lifecycle of the initiating UI component using `AbortController` signals. If a component unmounts, its associated pending network requests must be immediately aborted.
- **No Hardcoded Timeouts**: Repositories must not use hardcoded `AbortSignal.timeout()`. They must accept and propagate the signal provided by the calling hook or orchestration layer.
- **Request Deduplication**: The architecture must utilize a request deduplication engine (like React Query) to prevent duplicate identical GET requests during rapid component mounting phases.

---

## 6. Browser Defenses

All SPAs must be served with the following hardened HTTP security headers:

- **Content-Security-Policy (CSP)**: `default-src 'none'; script-src 'self'; connect-src 'self' api.scnehaux.com; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self';`
- **X-Frame-Options**: `DENY` (prevents Clickjacking).
- **Referrer-Policy**: `strict-origin-when-cross-origin`.
- **XSS Prevention**: Direct DOM manipulation and `dangerouslySetInnerHTML` are prohibited unless wrapping a strictly validated Markdown sanitizer (e.g., DOMPurify).

---

## 7. Compliance & Enforcement

- **Linting Rules**: ESLint configurations must prohibit direct, unscoped access to `window.sessionStorage` and `window.localStorage`.
- **Integration Testing**: E2E testing pipelines (e.g., Playwright) must include explicit "Tenant Isolation" suites that simulate logging into Tenant A, switching to Tenant B, and verifying that no data from Tenant A renders on the screen.
