---
doc_meta:
  id: SAD-014
  title: Scnehaux Scheduling Experience
  owner: Scheduling Platform Team
  version: 2.0.0
  status: approved
  classification: restricted
  governed_by:
    - GDC-009
  parent_pad: PAD-PLT-011
  review_cycle_days: 90
  created_date: 2026-08-22
  last_reviewed: 2026-08-25
  technologies:
    - name: react
      type: frontend-framework
    - name: golang
      type: backend-language
    - name: kubernetes
      type: orchestration
    - name: opentelemetry
      type: observability
---

# Scnehaux Scheduling Experience

## 1. Purpose & Scope

### 1.1 Objective

Provide a fully Scnehaux-owned administrative and operational user experience for Schedule lifecycle, Occurrence inspection, misfire/replay operations, Tenant/application usage, and Scheduler health through a same-origin web boundary without exposing database, messaging-substrate, or third-party task-queue dashboards.

The physical web boundary is one deployable Go application that serves compiled React assets and a same-origin Backend-for-Frontend (BFF). Browser-facing authentication/session custody, CSRF protection, context enforcement, and Scheduling API mediation remain server-side.

### 1.2 Capability

The application provides:

- Schedule search/list/detail and ownership context
- create/update/pause/resume/cancel operations
- recurrence/time-zone preview
- upcoming Occurrence timeline
- Occurrence/misfire/dispatch/replay history
- per-Tenant/application quota and usage visibility
- target registration visibility
- privileged replay and quota-override workflows
- dispatch-lateness and backlog dashboards
- audit/evidence correlation links
- same-origin browser session and Scheduling API mediation
- hard Tenant/Application context-switch invalidation

### 1.3 Requirement

Every operation must display explicit Tenant and Application scope, preserve server-side authorization, and use only the governed Scheduling Control API. The Experience must remain safe under stale browser tabs, duplicate submit/retry, context switches, expired sessions, API partial failure, replay races, and underlying dispatch-profile changes.

### 1.4 Constraint

- React is the rendering framework
- Go serves compiled React assets and the same-origin BFF in one deployable unit
- the internal-tool build follows the adopted SPA build-toolchain decision
- Scnehaux UI Platform packages provide tokens, primitives, accessibility, and interaction foundations
- browser JavaScript never receives long-lived access/refresh tokens or broker/database credentials
- browser-to-BFF traffic is same-origin
- the BFF is the only browser runtime boundary and calls only governed Scheduling Control APIs
- the browser/BFF never reads Scheduling PostgreSQL, messaging queues/topics, broker admin endpoints, or internal recurrence-library state
- recurrence/DST correctness is server-authoritative; client preview logic is presentation only
- context switch invalidates prior scoped cache, pending mutation state, and form state before the new context becomes active
- Asynqmon, Bull Board, RabbitMQ Management UI, Kafka admin UI, or other vendor/library operational UI is not embedded or exposed as the Scheduler product experience
- authorization is never inferred from hidden/disabled client controls
- access and refresh tokens are not persisted in browser local storage

### 1.5 Assumption

- SAD-013 exposes versioned control/query APIs
- Identity provides browser authentication and step-up capability
- Organization supplies canonical operating context
- UI Platform packages are available

### 1.6 Out of Scope

- Schedule execution
- due claiming
- messaging publication
- database administration
- Product worker monitoring beyond linked correlation facts
- Notification administration
- infrastructure cluster administration

## 2. Enterprise Traceability

### 2.1 Realizes

This system realizes the administrative-experience portion of PAD-PLT-011. Scheduling authority remains in SAD-013.

It inherits Identity, Tenant, application ownership, accessibility, audit, and API-contract rules from the enterprise architecture and global standards.

## 3. Solution Context

### 3.1 System Context

```mermaid
graph LR
    USER[Platform Operator / Tenant Admin / Application Operator]
    WEB[Scheduling Experience]
    IAM[Identity]
    ORG[Organization Context]
    API[Scheduling Runtime Control API]

    USER --> WEB
    WEB -->|OIDC authentication| IAM
    WEB -. context selection .-> ORG
    WEB -->|versioned HTTPS API| API
```

### 3.2 External

The browser communicates only with the Scheduling Experience origin. The server-side BFF communicates with enterprise Identity/context endpoints and the Scheduling Control API. It has no direct broker/database/provider integration.

### 3.3 Internal

The React application is organized by platform capability rather than vendor UI concepts:

- Schedule Management
- Occurrence Timeline
- Misfire & Replay Operations
- Usage & Quota
- Target Discovery
- Operational Health
- Audit Correlation

UI state does not become Scheduling authority.

## 4. Architecture Model

### 4.1 Container

One independently deployable Go web application serves immutable React assets and a same-origin BFF. The BFF consumes versioned Scheduling APIs and Scnehaux UI Platform packages remain build-time UI foundations.

### 4.2 Component

```text
app-shell
  -> schedule-management
  -> occurrence-operations
  -> quota-usage
  -> platform-health
  -> audit-correlation

browser -> same-origin BFF
BFF -> scheduling-api adapter
feature modules -> same-origin BFF client
feature modules -> scnehaux-ui-platform packages
```

### 4.3 Runtime Flow — Privileged Replay

```mermaid
sequenceDiagram
    participant U as Operator
    participant W as Scheduling Experience
    participant I as Identity
    participant S as Scheduling API

    U->>W: Select occurrence and Replay
    W->>I: Step-up when policy requires
    I-->>W: Fresh assurance
    W->>U: Show occurrence, Tenant, target, reason confirmation
    U->>W: Confirm with reason
    W->>S: Replay command + expected occurrence identity + reason
    S-->>W: Accepted / conflict / forbidden result
    W-->>U: Show per-operation result and evidence correlation
```

## 5. State & Data Architecture

### 5.1 Storage

No authoritative business or Scheduling database exists in the browser application. Durable state is owned by SAD-013.

### 5.2 Cache

Client-side query caching is bounded and invalidated/refetched after mutations. Cached authorization does not grant actions.

### 5.3 Schema

API models are generated or validated from the governed Scheduling API contract. Frontend types are not independent domain schemas.

### 5.4 Stateless Client

Reloading the Experience loses only ephemeral browser state. Schedule/Occurrence state is reconstructed through the same-origin BFF from the Scheduling Control API.

## 6. Integration Contracts

### 6.1 API

The Experience BFF consumes the versioned Scheduling Control API server-to-server for schedules, occurrences, preview, replay, quotas, targets, and operational projections. Browser JavaScript consumes only same-origin Experience routes.

### 6.2 Events

The browser never consumes RabbitMQ, Kafka, or another messaging substrate directly. Near-real-time UI updates, if required, are exposed by a Scheduling-owned HTTP/SSE/WebSocket-style projection rather than broker credentials or broker offsets in the browser.

### 6.3 Consumed

- Identity browser authentication and step-up
- Organization operating-context discovery where required
- Scnehaux UI Platform packages at build time
- Scheduling Control API at runtime

## 7. Security & Trust Boundary

### 7.1 Authentication

Identity remains authoritative for authentication and identity-session validity. The BFF owns only the browser-facing application-session binding and delegated token custody for the Scheduling Experience. Session cookies are Secure, HttpOnly, and SameSite according to enterprise browser policy. Access/refresh tokens are not persisted in browser local/session storage and are not exposed to browser JavaScript.

### 7.2 Authorization

The Scheduling API is authoritative for authorization. The Experience passes context and intent but cannot grant itself Tenant, application, replay, or quota authority.

### 7.3 Browser Security

The Experience enforces:

- anti-CSRF protection for state-changing requests
- Origin and Host validation
- restrictive Content Security Policy
- clickjacking protection
- governed redirect allowlist
- safe output encoding and React rendering defaults
- no permissive wildcard CORS for authenticated routes
- secure cookie attributes and session rotation according to enterprise browser policy

### 7.4 Encryption

All runtime network traffic uses enterprise TLS policy.

### 7.5 Secrets

No Scheduler infrastructure secret, database credential, RabbitMQ/Kafka credential, access token, refresh token, or provider credential is shipped to the browser bundle or client telemetry.

### 7.6 Audit

Privileged operations require explicit reason capture and expose resulting evidence correlation. UI telemetry never replaces server-side evidence.

## 8. NFR

### 8.1 Blast Radius

An Experience outage prevents human administration but does not stop existing Schedule materialization or dispatch. SAD-013 continues independently.

### 8.2 Latency and Scalability

- interactive control queries target p95 <= 500 ms excluding explicitly asynchronous aggregation views
- list views use server-side pagination/filtering rather than loading unbounded Schedule history
- timeline/history views use bounded windows and virtualized presentation when needed
- control mutations return explicit accepted/conflict/forbidden outcomes

### 8.3 Observability and Telemetry

OpenTelemetry correlates browser request, BFF span, and Scheduling API span without recording bearer tokens, CSRF material, schedule secrets, or sensitive trigger payloads.

### 8.4 Accessibility and Usability

- Scnehaux UI Platform accessibility baseline applies
- Tenant/Application scope is visually persistent for destructive or privileged operations
- destructive actions require explicit confirmation and safe defaults
- WCAG 2.2 AA is the target baseline
- replay UI makes clear that replay reuses the existing occurrence identity
- recurrence/time-zone preview is rendered from server-authoritative Scheduling output
- time is shown with both user-facing zone context and unambiguous canonical instant on detail screens

### 8.5 Runbook

Operational guidance covers API degradation, stale client cache, authentication/session failures, partial list-query failures, and rollback of the Experience artifact.

## 9. Deployment Strategy

### 9.1 Environment

Immutable Scheduling Experience artifacts containing the Go web boundary and compiled React assets are promoted across governed environments. Environment configuration contains only server-resolved endpoints and intentionally public non-secret browser settings.

### 9.2 Infrastructure

The application is built as one OCI-compatible Go web artifact containing the compiled React assets and same-origin BFF, deployed through the standard Kubernetes web/container delivery path. No third-party scheduler dashboard runtime is required.

### 9.3 CI/CD

Blocking gates include:

- Go format/static/build/race tests
- frontend lint/type/build tests
- browser/BFF auth-session tests
- CSRF/origin/CSP/redirect security tests
- context-switch invalidation tests
- mutation idempotency/duplicate-submit tests
- recurrence/DST preview parity tests
- UI Platform contract tests
- accessibility checks
- API contract compatibility
- authorization-negative-path E2E tests
- Tenant-context isolation E2E tests
- secret scanning and dependency vulnerability checks
- bundle and performance budgets
- architecture governance lint

## 10. Architecture Decisions

### 10.1 Accepted

- fully custom Scnehaux operational experience
- Scheduling Experience BFF is the only Scheduling runtime boundary exposed to the browser
- Scheduling Control API is consumed server-to-server only by the Experience BFF
- single deployable Go web boundary serving React assets and same-origin BFF
- server-side browser token/session custody
- recurrence/DST preview is server-authoritative

### 10.2 Rejected

#### 10.2.0 Pure SPA with Browser Bearer-Token Custody

Rejected for the privileged Scheduling control surface because it expands credential exposure and makes browser JavaScript responsible for long-lived API token handling.

#### 10.2.1 Embedded Third-Party Queue/Scheduler UI

Rejected because it couples the Scnehaux product surface, authorization model, Tenant semantics, and lifecycle to an internal implementation that must remain replaceable.

#### 10.2.2 Direct Database or Messaging-Substrate Administration from Browser

Rejected because it bypasses domain authorization, evidence, contract versioning, and least privilege.

#### 10.2.3 Client-Side Authorization

Rejected because visibility state cannot establish server authority.

## 11. Assumptions

- Scheduler operators and Tenant/application administrators are represented by enterprise Identity/Organization context
- UI Platform primitives satisfy the required accessibility baseline

## 12. Compatibility Strategy

The Experience follows Scheduling API versions and supports the enterprise deprecation window. A replacement of PostgreSQL, RabbitMQ, Kafka, recurrence library, due-claim mechanism, or Direct/Queue/Stream dispatch profile requires no UI rewrite when the Control API remains compatible.
