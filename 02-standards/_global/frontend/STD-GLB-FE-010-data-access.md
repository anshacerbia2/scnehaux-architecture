---
doc_meta:
  id: STD-GLB-FE-010
  title: Enterprise Frontend Data Access & Network Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: assessed
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-31
---

# Enterprise Frontend Data Access & Network Standard (STD-GLB-FE-010)

---

## 1. Objective & Scope

This standard defines the mandatory network policies, HTTP client architecture, data fetching mechanics, and real-time transport protocols for all browser-executed frontend applications within the Scnehaux enterprise ecosystem.

It establishes a rigorous boundary layer between the frontend UI and the backend APIs to ensure resilience against transient network failures, strict type safety for data contracts, and deterministic control over async request lifecycles.

The scope of this standard applies to all REST, GraphQL, WebSocket, SSE, and streaming data consumption mechanisms originating from the client.

---

## 2. Design Principles

All frontend network IO architectures must strictly adhere to the Supreme Frontend Governance principles:
- **Absolute IO Isolation**: Components must never directly negotiate with the network. All API interactions must route through centralized infrastructure services or caching hooks.
- **Zero Silent Failure**: Every asynchronous request must explicitly account for loading, success, and failure states. Unhandled promise rejections are strictly prohibited.
- **Transactional Consistency**: If a mutation (e.g., POST/PUT/DELETE) fails, the local UI state must deterministically roll back to its pristine condition without leaving shadow artifacts.

---

## 3. Normative Rules

### 3.1 HTTP Client Architecture
- **Centralized Wrapper**: Applications must use a single, centrally configured HTTP client instance (e.g., Axios or a customized `fetch` wrapper). Directly calling native `fetch()` or instantiating ad-hoc Axios instances inside component files is strictly prohibited.
- **Global Interceptors**: The centralized client must utilize interceptors to globally handle concern-crossing requirements:
  - **Request**: Injecting `Authorization` bearer tokens, `X-Tenant-Id`, `X-Trace-Id` (for OpenTelemetry), and `Accept-Language` headers.
  - **Response**: Global error handling logic (e.g., `401 Unauthorized` triggering an automated silent token refresh, `403 Forbidden` triggering a redirect, and `5xx` triggering retry logic).

### 3.2 Network Cancellation & AbortController
- **Lifecycle Binding**: All asynchronous requests initiated by a component must be bound to an `AbortController`. If the component unmounts before the network responds, the request must be explicitly aborted to prevent memory leaks and state updates on unmounted components.
- **Sequence Invalidation (Race Conditions)**: When multiple identical requests are triggered in rapid succession (e.g., typeahead search), previous pending requests must be aborted so only the final response resolves.

### 3.3 Retry & Circuit Breaker Strategies
- **Idempotent Retries**: Failed idempotent requests (e.g., `GET`, `PUT`, `DELETE`) must automatically retry using an **Exponential Backoff with Jitter** strategy.
- **Non-Idempotent Rules**: Requests that alter state without idempotency guarantees (e.g., `POST`) must not be automatically retried without explicit user consent.
- **Circuit Breakers**: If a specific backend service continuously returns `5xx` errors, the frontend client must trip a circuit breaker to halt requests for a defined cooldown period, protecting the backend from cascading failure.

### 3.4 Data Cache Engine (Stale-While-Revalidate)
- **Engine Mandate**: The management of remote server state inside raw component lifecycles (e.g., `useEffect`) is prohibited. Applications must utilize standardized query engines (such as **TanStack Query** or **SWR**) to manage request deduplication, background revalidation, and caching.
- **Optimistic UI Updates**: UI state mutations (e.g., toggling a "Like" button) must update the UI instantly without waiting for the server response, creating an illusion of zero latency. Components must implement transactional rollbacks (e.g., via React Query `onMutate`/`onError`) so that if the background network request fails, the cache state automatically reverts to the pre-optimistic snapshot.

### 3.5 Real-Time Transports
- **WebSockets**: Must be used for bidirectional, low-latency, full-duplex communication. The WebSocket client must implement automatic reconnection logic with exponential backoff and continuous heartbeat pings to detect stale connections.
- **Server-Sent Events (SSE)**: Must be used for unidirectional server-to-client streaming (e.g., live logs, notification feeds) due to its built-in browser reconnection capabilities and ability to traverse standard HTTP proxies.
- **Streaming & Chunked Responses**: Applications consuming progressive data (e.g., AI text streaming or large dataset exports) must process the data progressively using the browser's native `ReadableStream` API.

### 3.6 GraphQL & Type Safety
- **Schema-Driven Code Generation**: For GraphQL architectures, all client queries and mutations must be type-checked against the remote schema at compile time using code generators (e.g., GraphQL Codegen).
- **Persisted Queries**: Production applications should utilize Persisted Queries to reduce request payload sizes and prevent arbitrary query injection.

---

## 4. Exceptions
Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk. 

### Exception to "Centralized HTTP Client Wrapper" (Rule 3.1)
- **Condition for Deviation**: You are integrating proprietary third-party SDKs (e.g., Stripe, Firebase, AWS Amplify) that enforce their own internal HTTP clients which cannot be intercepted by the central Axios/fetch wrapper.
- **Mandatory Alternative**: The SDK is permitted to bypass the central wrapper, provided its logic is strictly abstracted behind a custom Domain Service hook that manually handles the `AbortController` cancellation lifecycle.

### Exception to "Idempotent Retries (Exponential Backoff)" (Rule 3.3)
- **Condition for Deviation**: A failed network request occurs on a highly critical transaction path (e.g., Payment processing gateways, final checkout submissions, or ledger updates) where duplicate processing introduces severe business risk.
- **Mandatory Alternative**: Automatic retries must be strictly disabled (`0` retries) for these endpoints. The system must fail immediately and surface a localized error instructing the user on manual intervention.

## 5. Enforcement Mechanism

- **AST Linting**: CI/CD pipelines must enforce AST-based linting rules (e.g., `no-restricted-globals`) to flag and block the usage of raw `fetch` or `XMLHttpRequest` outside of the authorized `core/network` infrastructure directory.
- **Waiver Protocol**: Deviations from this standard (such as integrating legacy non-compliant libraries) must be documented in a local project ADR. The Architecture Review Board (ARB) must respond with a review decision within **5 business days** of the ADR submission.
