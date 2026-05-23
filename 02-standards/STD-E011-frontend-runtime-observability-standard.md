---
doc_meta:
  id: STD-E011
  title: Enterprise Frontend Runtime, Security & Observability Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-21
---

# Enterprise Frontend Runtime, Security & Observability Standard (STD-E011)

---

## 1. Objective & Scope

This standard defines the mandatory build pipelines, security policies, dependency audits, micro-frontend runtime communication interfaces, and frontend observability frameworks for all web applications built within the Scnehaux enterprise.

It ensures that frontend deliverables are secure, optimized for loading latency, and monitored to identify and remediate production performance anomalies.

The scope of this standard applies to all production build configurations, CI/CD pipeline audits, runtime configurations, and telemetry deployments.

---

## 2. Bundling & Performance Budgets

To protect client-side execution from loading lag and layout blocks, applications must adhere to strict build budgets categorized by application type.

### 2.1 Application Class Budgets
- **Tier 1 (Customer-Facing Pages)**: Initial route bundle size must not exceed **50KB gzipped**. Any non-critical asset must be loaded lazily.
- **Tier 2 (Internal Portals & Dashboards)**: Initial route bundle size must not exceed **250KB gzipped**.
- **Tier 3 (Heavy Interactive Editors & Chart Portals)**: Exempt from initial load budgets, but must implement route-level lazy loading and code splitting.

### 2.2 Code Splitting & Dynamic Imports
- Routes must be split into dynamic chunks using lazy loading (e.g. `React.lazy` or dynamic `import()`). Layout wrappers must load independently from page content.
- Critical assets must use resource hints (such as `modulepreload`) to begin downloading assets before execution.

---

## 3. Environment & Configuration Security

Frontend configurations must separate build-time variables from runtime configurations to prevent sensitive credential exposure.

### 3.1 Environment Variable Prefixing
- **Public Variables**: Variables destined for browser exposure must be explicitly prefixed using the build framework prefix (e.g., `NEXT_PUBLIC_*` or `VITE_*`).
- **Secrets Prohibitions**: Variables containing private signing keys, database passwords, or third-party integration secrets must not use these public prefixes. They must never be packaged into client-side bundles.

### 3.2 Runtime Configuration Isolation
- Applications requiring dynamic environment configurations must fetch configuration properties from a secure endpoint during initialization, or read them from a single, isolated configuration script injected at HTML rendering time.

### 3.3 Production Environment Variables Ban on `.env` Files
- **No Local `.env` Files in Production or Staging**: The deployment, mounting, or execution use of local configuration files (e.g., `.env`, `.env.production`, `.env.staging`) is strictly prohibited in production and staging runtimes.
- **OS/System Variable Mandate**: All runtime configuration properties must be loaded directly from system environment variables (OS system variables, Kubernetes ConfigMaps/Secrets, or cloud container platform parameters).
- **Local Development Restriction**: Local `.env` files are permitted exclusively in Local Development (DX) environments. Centralized `.gitignore` templates must block any configuration files from entering source control repositories.

---

## 4. Risk-Based Dependency Security

Supply chain security must verify package credibility while avoiding unnecessary CI pipeline blocks.

### 4.1 Production Scoped Audits
- Dependency vulnerability audits in CI (such as `npm audit` or `yarn audit`) must be configured to check production dependencies (`dependencies`).
- **DevDependencies Exemption**: Unused development tooling (`devDependencies`) containing unexploitable vulnerabilities must not block production builds.

### 4.2 Reachability Analysis
- High or critical vulnerability alerts must be evaluated using reachability analysis tools (such as Snyk or Socket) to verify if the vulnerable function is actually imported or invoked inside the application bundle. Harmless, un-reached alerts must not block development pipelines and must be managed through security waiver documentation.

---

## 5. Typed Micro-Frontend (MFE) Communication

Micro-frontend architectures must communicate using typed interfaces to prevent runtime crashes and simplify message tracing.

### 5.1 Shared EventBus SDK
- Micro-frontends must exchange data using a centralized, typed EventBus SDK or a shared message broker interface.
- **No Raw Browser Events**: Exchanging data through raw, string-based custom browser events (e.g., `window.dispatchEvent(new CustomEvent('user-login'))`) is prohibited due to the lack of compile-time typing and payload verification.

### 5.2 Payload Verification
- All event payloads must be declared as TypeScript types or interfaces within a shared contract repository.
- Receivers must validate incoming payloads at the boundary using schema validation libraries (such as Zod) before processing the event.

---

## 6. Frontend Observability & Telemetry

Production runtimes must emit telemetry data to track performance metrics and diagnose runtime failures.

### 6.1 Core Web Vitals Tracking
- Runtimes must track Core Web Vitals, prioritizing:
  - **Interaction to Next Paint (INP)**: Target latency under 200ms.
  - **Cumulative Layout Shift (CLS)**: Target score under 0.1.
  - **Largest Contentful Paint (LCP)**: Target paint duration under 2.5s.
- These metrics must be reported automatically to the telemetry collector.

### 6.2 OpenTelemetry & Trace Propagation
- HTTP requests originating from the frontend must propagate correlation trace IDs (e.g., using `traceparent` headers conforming to W3C Trace Context specifications) to backend services.
- This propagation ensures that frontend user interactions can be traced end-to-end across backend microservices.

---

## 7. Compliance & Enforcement

- **Build Violations**: Build pipelines must reject pull requests that exceed defined budget limits unless accompanied by a approved architectural waiver.
- **Security Scoping**: CI pipelines must run production-scoped security checks on every build.
- **Waiver Protocol**: Deviations from the runtime budgets, security rules, or communication standards require a documented ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
