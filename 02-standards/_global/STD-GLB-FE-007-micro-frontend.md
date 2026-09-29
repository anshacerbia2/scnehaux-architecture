---
doc_meta:
  id: STD-GLB-FE-007
  title: Enterprise Micro-Frontend Federation Standard
  owner: Principal Frontend Architect
  version: 2.0.0
  status: approved
  classification: restricted
  governed_by: [GDC-000]
  authorized_by: [ADR-GLB-FE-010]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-29
---

# Enterprise Micro-Frontend Federation Standard (STD-GLB-FE-007)

> **Authorization:** ADR-GLB-FE-010 authorizes this revision; implementation conformance still requires verification.

## 1. Objective & Scope

This standard defines adoption criteria, host/remote ownership, shared-module identity, routing, CSS, communication, version compatibility, failure containment, and evidence for Module Federation systems.

A standalone application remains the default while one team or coordinated release boundary can deliver it safely. Module Federation is justified when independently owned product areas require separate release and failure boundaries and the integration cost is accepted by the platform owner.

## 2. Design Principles

1. The host owns composition, primary routing, shared-module policy, and cross-remote failure containment.
2. Remotes own their feature UI and versioned public contracts.
3. Shared identity is explicit and verified from built artifacts.
4. Business authority and internal source do not cross remote boundaries.
5. Runtime and payload budgets use named consumer scenarios.

## 3. Normative Rules

### 3.1 Adoption gate

A system design records:

- independently accountable teams and release cadences;
- the coordination cost that federation removes;
- required runtime composition;
- host and remote deployment/rollback ownership;
- failure and security boundaries;
- the measured latency, payload, and operational cost of federation.

Team count may inform the decision and is not a sufficient rule by itself.

### 3.2 Host and remote contract

The host dynamically loads remotes and contains load/render failures at route or feature boundaries. A missing remote leaves the shell and unrelated routes operable.

The host owns primary location state. A remote exports routes or mount contracts through a versioned interface and does not install an independent top-level router over the host.

Every remote exposes build/version metadata. The host validates compatibility before activation and presents a controlled fallback for an incompatible remote.

### 3.3 Shared-module identity

- `react`, `react-dom`, and `@tanstack/react-query` (mandated by STD-GLB-FE-001) are strict singleton shared modules.
- Every supported package request carrying context or shared state is an explicit singleton key generated from the public export inventory.
- `requiredVersion` is the peer or dependency range that the consuming application or package declares for that module. Shared packages publish explicit exports; wildcard subpath exports are not shareable contracts.
- Remotes remain lazy. Only the host may choose eager loading for an entry required before remote execution.
- A shared package preserves one module identity across host and remotes.
- The host handles unsatisfied required versions as a controlled integration failure: the affected route or feature renders its fallback, the rest of the host keeps working, and telemetry records both versions (ADR-GLB-FE-012).

Libraries with no required cross-remote identity remain ordinary remote dependencies unless measured duplication justifies sharing.

### 3.4 CSS and DOM isolation

The composition root imports shared UI component CSS and the selected theme CSS once. Remotes do not inject duplicate shared CSS. Remote-owned application styles use scoped selectors, documented cascade layers, and domain-specific prefixes or CSS Modules.

Portals preserve their originating theme container. Remotes do not mutate global prototypes or undocumented `window` properties.

### 3.5 Cross-application communication

Cross-remote communication uses versioned typed contracts: host-owned context where identity is required, documented custom events, or a published contract package. A remote does not import another remote's internal source or access another domain's state store directly.

Network calls follow STD-GLB-FE-010. Authentication credentials remain under the approved browser/BFF security model. A logout or session revocation reaches every open host tab and every mounted remote without a page reload; remotes on separate origins receive it through an origin-checked channel such as `BroadcastChannel` or `postMessage`. The host fixture verifies propagation. A remote receives identity/session state through approved contracts and never reads `HttpOnly` cookie contents from JavaScript.

### 3.6 Failure and observability

A second instance of React or of any shared singleton at runtime emits a telemetry event and fails the integration fixture. Remote loading, compatibility rejection, render failure, and timeout events emit approved telemetry with host, remote, version, route, and correlation identifiers. Error boundaries provide retry or navigation recovery. Cached fallback behavior is used only when integrity, compatibility, and staleness policies are defined.

### 3.7 Performance budgets

Each remote budget identifies the route/interaction, remote set, cold/warm cache, network/device profile, bundler/plugin, raw/minified/compressed representation, tool, baseline, and threshold.

The evidence separates remote entry metadata, shared chunks, initial route assets, and lazy assets. No universal 20 KB, 100 KB, or 150 KB limit applies without a defined scenario and approved baseline.

## 4. Exceptions

A legacy application that cannot share the host runtime may use a separately isolated document boundary with typed `postMessage` contracts, strict origin checks, sandbox policy, focus/navigation design, and an owned migration or retirement condition.

## 5. Enforcement Mechanism

- Configuration analysis compares explicit singleton keys and `requiredVersion` values with manifests and the export inventory.
- A host plus two packed remotes verifies one React/context identity, both load orders, lazy behavior, controlled version mismatch, remote unavailability, and rollback.
- Browser tests assert one shared UI stylesheet set, scoped remote styles, and portal theme propagation.
- Contract tests validate route, event, and version schemas.
- Scenario reports enforce payload and runtime budgets.
- Required integration fixtures that do not run block production adoption.
