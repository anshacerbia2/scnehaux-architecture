---
doc_meta:
  id: STD-GLB-FE-010
  title: Enterprise Frontend Data Access & Network Standard
  owner: Principal Frontend Architect
  version: 2.0.0
  status: assessed
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-10
---

# Enterprise Frontend Data Access & Network Standard (STD-GLB-FE-010)

## 1. Objective & Scope

Define the frontend boundary for REST, GraphQL, WebSocket, SSE, streaming, and BFF-mediated data access without assuming that every application exposes bearer tokens to browser JavaScript.

## 2. Design Principles

- Components consume typed domain/data-access abstractions rather than embedding protocol behavior everywhere
- BFF/server-session and direct-browser API profiles are both supported where explicitly selected
- Requested tenant/workspace context never becomes authorization proof
- Retry, caching, optimistic update, and streaming behavior follow operation semantics and business risk
- Loading, failure, cancellation, and stale-context behavior are explicit

## 3. Normative Rules

### 3.1 Data-Access Boundary

- Applications MUST centralize cross-cutting network concerns in an approved data-access layer, generated client, SDK adapter, BFF boundary, or equivalent abstraction
- UI components SHOULD NOT construct authentication, tenant, tracing, retry, or protocol policy ad hoc
- Native `fetch` is permitted inside approved network/domain infrastructure; the standard does not require Axios
- Third-party SDKs MUST be wrapped behind a domain/integration boundary when they bypass the normal client stack

### 3.2 Authentication & Context Propagation

- BFF/server-session applications SHOULD rely on secure server-managed session state and MUST NOT inject browser bearer tokens merely for architectural uniformity
- Direct browser-token applications inject `Authorization` only through the approved public-client profile
- `X-Tenant-Id`, `Scnehaux-Account`, workspace, or equivalent headers MAY carry **requested context** but MUST NOT be treated by the backend as authority
- The server MUST validate requested context against trusted identity/session claims or authoritative/projected Membership context
- Trace/correlation identifiers MAY be propagated from the client but trusted tracing metadata is normalized at the server boundary

### 3.3 Cancellation & Stale Request Control

- Requests whose results can become stale after navigation, search changes, or context switching SHOULD support cancellation or sequence invalidation
- Principal/Tenant/Workspace switch MUST invalidate outstanding context-sensitive requests and relevant caches
- Cancellation mechanics belong to the data-access/query layer rather than being duplicated across every component

### 3.4 Retry & Idempotency

- Automatic retries are allowed only when the operation is safe to repeat or protected by an explicit idempotency contract
- HTTP method alone MUST NOT be treated as sufficient proof that a business operation is safe to retry
- Mutations with duplicate-processing risk require idempotency keys, server-side deduplication, or explicit no-retry behavior
- Retries use bounded attempts, exponential backoff, jitter where appropriate, and respect server retry guidance
- Repeated backend failure MUST degrade gracefully rather than creating browser retry storms

### 3.5 Server-State Cache

- Remote server state SHOULD use an approved query/cache abstraction where caching, deduplication, invalidation, or background refresh provide value
- Raw lifecycle effects MAY be used for simple one-off IO when they do not recreate a server-state engine
- Cache keys and invalidation MUST encode the validated Principal/Tenant/Workspace boundary for context-sensitive data
- Optimistic updates are permitted only where rollback, reconciliation, and duplicate-processing behavior are understood

### 3.6 Error Handling

- `401` means the current authentication/session is not usable for the request and MUST be handled according to the selected BFF or browser-token profile
- `403` MUST NOT automatically redirect users in a way that hides actionable authorization context; products define the appropriate denied experience
- `429` and transient `5xx` handling follows retry policy and server guidance
- Errors MUST be normalized without leaking credentials, secrets, sensitive claims, or client data

### 3.7 Real-Time & Streaming

- WebSocket, SSE, polling, and streaming are selected by interaction semantics rather than mandated globally
- Long-lived connections MUST authenticate using an approved session/token profile
- Long-lived connections MUST declare a maximum lifetime that does not exceed the access token lifetime of their profile; on expiry the connection is closed and re-authentication is required
- A long-lived connection MUST revalidate Principal, Tenant, and Workspace context on every reconnection and on any server-signalled context change; an open connection MUST NOT outlive the authority that established it
- Termination of long-lived connections MUST be treated as a revocation enforcement mechanism and counted in the enforcement delay defined by the identity security standard
- Reconnection is bounded and uses backoff to prevent storms
- AI or large-response streaming MUST handle cancellation, partial output, failure, and audit requirements appropriate to the product

### 3.8 Schema & Type Safety

- API clients SHOULD be generated or validated from versioned contracts where practical
- GraphQL, REST, event, and streaming clients MUST handle backward-compatible contract evolution according to their protocol standards
- Production GraphQL may use persisted/allowlisted operations where threat model and platform support justify it

## 4. Exceptions

Exceptions follow the formal GDC-000 exception process when strict compliance creates disproportionate technical, accessibility, security, or business risk. Third-party SDKs and legacy integrations require an explicit wrapping and lifecycle strategy.

## 5. Enforcement Mechanism

- static checks for unauthorized network/authentication logic in components where practical
- contract/type checks in CI
- E2E tests for context switch, cache invalidation, authentication expiry, and denied access
- retry/idempotency tests on critical mutations
- telemetry for retry storms, request failures, and stale-context defects
