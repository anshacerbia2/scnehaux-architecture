---
doc_meta:
  id: STD-GLB-FE-007
  title: Enterprise Micro Frontend Federation Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-21
---

# Enterprise Micro Frontend Federation Standard (STD-GLB-FE-007)

---

## 1. Objective & Scope

This standard defines the integration boundaries, deployment contracts, remote dependency configurations, and cross-application communication rules for all federated portal applications (micro-frontends) built within the Scnehaux enterprise.

It guarantees that micro-frontends integrate without runtime collision, dependency mismatch, or layout degradation, utilizing **Module Federation** technologies for dynamic composition.

### 1.1 Architecture Default: Monolithic SPA vs. Conditional Module Federation

To avoid premature architectural complexity, shared dependency drift, and runtime latency overhead, the default architectural choice for all frontend applications is a **Monolithic Single Page Application (SPA)**.

The adoption of a federated micro-frontend architecture utilizing **Module Federation** is conditional and only authorized when the following organizational and operational metrics are met:

| Architectural Metric | Monolithic SPA (Default) | Module Federation (Conditional Approval) |
| --- | --- | --- |
| **Organizational Scale** | $\le 3$ independent engineering teams. | $> 3$ independent engineering teams. |
| **Deployment Autonomy** | Deployment coordination overhead is minimal; teams can release on a shared pipeline. | Zero-coordinated deployments are required; teams must deploy updates independently. |
| **Release Cadence** | All components share a common release cycle and sprint schedule. | Teams operate on distinct release schedules and independent hotfix cycles. |
| **Blast Radius Isolation** | A failure in one section of the SPA is acceptable to trigger a full system rollback. | Operational failures must be strictly isolated to individual sub-features. |

Module Federation must **NOT** be adopted as a tooling standard for small teams or standardized systems where a monolithic codebase provides faster feedback loops and lower operational maintenance overhead.

---

## 2. Design Principles

All micro-frontend architectures must strictly adhere to the Supreme Frontend Governance principles:

- **Separation of Concerns (HARD BOUNDARY)**: Remotes must be fully decoupled. Sharing business logic or state directly across federation boundaries is prohibited.
- **Determinism Over Cleverness**: Build and deployment contracts must be explicit. Implicit dependency resolution across remotes leads to runtime chaos.
- **Zero Waste System**: Federation must not result in duplicated runtime dependencies or inflated bundle sizes. The network cost must be strictly budgeted.

## 3. Normative Rules

### Micro Frontend Integration Contracts

#### Host-Remote Boundary

- **Dynamic Imports**: Host applications must load remote micro-frontend entrypoints dynamically to prevent bundle blocking during initialization.
- **Fail-Safe Loading**: Any runtime failure to download a remote entrypoint must be caught at the route boundary using isolated React Error Boundaries, allowing the host application shell to remain interactive.
- **Routing Integration**: Remotes must export their sub-routing tables as declarative route configuration arrays rather than exposing self-managed routers, ensuring the host router owns the primary location state.

---

### Shared Dependency Governance

#### Strict Version Alignments

- To prevent loading multiple instances of core runtime libraries in the browser context:
  - **Singleton Dependencies**: `react`, `react-dom`, and `@tanstack/react-query` must be declared as singleton dependencies inside the Module Federation configuration.
  - **Version Mismatches**: Remote containers must not run on a major React version different from the host shell container.

#### Dynamic Container Isolation

- Remotes must not alter or pollute global prototypes (`Object`, `Array`, `Window`) or overwrite shared global window context properties.

---

### Cross-Application Communication & Data Sharing

#### Typed Event Routing

- Cross-micro-frontend communication must be restricted to the centralized, type-safe event bus mechanism. Direct function references or global state access across boundary contexts is prohibited.
- **Payload Schema Contracts**: All events routed through the EventBus must use strongly typed payloads defined in shared package contracts.
- **Network IO Boundary**: Any data fetching or remote state synchronization triggered via cross-app communication must strictly adhere to **[STD-GLB-FE-010 (Data Access & Network)](./STD-GLB-FE-010-data-access.md)**. Remotes must not implement rogue HTTP clients.

#### Micro-Frontend Authentication Handoff

- **Cookie-Based Token Sharing**: The host application and remote containers must access JWT access and refresh tokens via secure, `HttpOnly`, `SameSite=Lax` cookies bound to the enterprise parent domain.
- **BroadcastChannel Handoff**: For sub-domains operating on separate origins, token updates or logout actions must propagate across active client tabs and remotes using a typed browser `BroadcastChannel` (e.g. `scnehaux_auth_sync`).

#### Contract Versioning & SemVer Check Invariants

- **Remote Version Export**: Every remote micro-frontend entrypoint must expose its build-anchored Semantic Versioning (SemVer) metadata (e.g., in a `remoteEntry.json` manifest).
- **SemVer Compliance Verification**: The host shell must verify that the loaded remote's major version matches the designated dependency range in the host deployment config. If a major mismatch is detected, the host must block loading the remote and fall back to the last known stable cached build.

#### Remote Bundle Budgets

- **Bundle Budgets**: To prevent micro-frontends from degrading host page load speeds or violating [STD-GLB-FE-002 (Performance & Rendering)](./STD-GLB-FE-002-performance.md#451-core-web-vitals) metrics:
  - _Remote Entrypoint Size_: The primary remote entrypoint bundle (`remoteEntry.js`) must not exceed `20KB` gzipped.
  - _Initial Loaded Assets_: The initial shared bundle chunk of a remote must not exceed `150KB` gzipped.
  - _Lazy Chunks_: Individual lazy-loaded asset chunks must not exceed `100KB` gzipped.
- **Enforcement**: Build pipelines must verify these limits using automated bundle size analyzer tools.

---

## 4. Exceptions

Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk.

### Exception to "Module Federation (No Iframes)" (Rule 3.1)

- **Condition for Deviation**: You are migrating a legacy non-React monolith (e.g. AngularJS) or an older React 16 remote that cannot be upgraded to match the host shell's runtime environment.
- **Mandatory Alternative**: Module Federation is strictly prohibited for the non-compliant remote. The remote must be fully isolated using a strict `<iframe>` boundary, and all cross-app communication must be bridged manually via a typed `postMessage` proxy to prevent global prototype pollution.

### Exception to "Strict Bundle Size Limits" (Rule 3.3)

- **Condition for Deviation**: A highly specialized internal-only remote micro-frontend (e.g., a massive data-processing grid) requires complex charting or vendor libraries that fundamentally exceed the 150KB limit.
- **Mandatory Alternative**: The bundle size limits may be exceeded _only_ if the remote is guaranteed to not block the primary interactive shell's initialization (lazy-loaded), and objective profiler benchmarks prove that the host shell's INP and LCP remain unharmed.

## 5. Enforcement Mechanism

- **Configuration Audits**: CI/CD pipelines must audit bundler configuration files to ensure singleton dependency configurations are correctly established.
- **Runtime Dependency Monitoring**: Browser logging must flag any occurrences of duplicate library initialization (e.g. multiple React instances loaded), feeding directly into the telemetry systems defined in **[STD-GLB-FE-004 (Observability & Telemetry)](./STD-GLB-FE-004-observability.md)**.
- **Waiver Protocol**: Custom federation configurations or remote dependency adjustments require a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.

