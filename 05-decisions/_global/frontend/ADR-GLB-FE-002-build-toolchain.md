---
doc_meta:
  id: ADR-GLB-FE-002
  title: ADR-GLB-FE-002 Standardization on Next-Generation Build Toolchains
  adr_type: foundational
  status: accepted
  created: 2026-04-04
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-002: Standardization on Next-Generation Build Toolchains

---

## 1. Title
Standardization on Next-Generation Build Toolchains (Rsbuild & Vite)

## 2. Status
| Date | Status | ADR Type | Reviewers | Approver |
|---|---|---|---|---|
| 2026-04-04 | proposed | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |
| 2026-04-07 | accepted | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |

## 3. Context
Following the standardization of React as our foundational rendering engine ([ADR-GLB-FE-001](../../../05-decisions/_global/frontend/ADR-GLB-FE-001-react-ecosystem.md)), the enterprise faces severe fragmentation in how applications are compiled and bundled. Teams are currently utilizing legacy Webpack setups with build times exceeding 10 minutes, leading to drastically reduced developer velocity. A modern, high-performance build ecosystem is required to support both isolated Single Page Applications (SPAs) and complex Micro-Frontend orchestrations ([ADR-GLB-FE-004](../../../05-decisions/_global/frontend/ADR-GLB-FE-004-module-federation.md)).

## 4. Decision Drivers
- **Developer Velocity**: CI/CD pipelines and local Hot Module Replacement (HMR) times must be aggressively optimized to sub-second thresholds to eliminate idle waiting.
- **Architectural Flexibility**: The enterprise requires a bundler capable of native Module Federation (for complex MFE orchestrations) alongside an ultra-fast, lightweight bundler (for isolated apps and UI libraries).
- **Unified CI/CD Pipeline**: DevOps requires a narrowed set of standardized build toolchains to enforce security scanning, caching, and deployment consistency.
- **Ecosystem Interoperability**: The chosen toolchains must seamlessly compile React, process modern CSS, and integrate with our zero-runtime CSS architecture.

## 5. Decision
We will standardize **Rsbuild** and **Vite** as the official, next-generation build toolchains for all Enterprise React applications.

- **Rsbuild (powered by the Rust-based Rspack compiler)**: Must be used for all Micro-Frontend (MFE) host and remote applications due to its deep native compatibility with the Module Federation architecture.
- **Vite (powered by Go-based esbuild and the Rust-based Rolldown)**: Recommended for isolated SPAs, internal tooling, and UI component libraries where lightning-fast unbundled development server startup is prioritized.

*Note: Server-Side Rendered (SSR) applications may continue to utilize their meta-framework's internal compiler (e.g., Next.js Turbopack).*

## 6. Consequences

### Positive
- **Extreme Performance**: Build times and local HMR speeds will improve by 5x-10x by leveraging Rust (Rspack) and Go (esbuild) compilers.
- **Tailored Tooling**: Teams have the flexibility to choose Vite for maximum DX in simple apps, and Rsbuild for robust MFE architecture.
- **Ecosystem Liquidity**: Both Rsbuild and Vite share a large portion of modern plugins, making it easier to share architectural standards across the enterprise.

### Negative & Risks
- **Migration Effort**: Teams with heavily customized Webpack plugin chains may face friction translating their custom logic to Vite or Rspack plugins.
- **Dual Maintenance**: The Platform Team must maintain two sets of enterprise build presets (one for Vite, one for Rsbuild).

### Operational
- The Platform Team will distribute unified presets (`@scnehaux/build-preset-vite` and `@scnehaux/build-preset-rsbuild`) encapsulating all enterprise security and linting rules.
- Webpack is strictly prohibited for new repositories.

## 7. Compliance Impact
### Related Standards
- [STD-GLB-FE-001 (Tech Stack)](../../../02-standards/_global/frontend/STD-GLB-FE-001-tech-stack.md)
- [ADR-GLB-FE-001 (React Ecosystem)](../../../05-decisions/_global/frontend/ADR-GLB-FE-001-react-ecosystem.md)
- [ADR-GLB-FE-004 (Module Federation)](../../../05-decisions/_global/frontend/ADR-GLB-FE-004-module-federation.md)

### Compliance Status
Compliant.

### Required Waivers
None.

## 8. Alternatives Considered
- **Webpack**: Rejected. Compilation speeds are unacceptably slow for enterprise-scale codebases, degrading Developer Experience (DX) and inflating CI/CD compute costs.
- **Parcel**: Rejected. Its zero-config nature is too opaque for enterprise applications that often require highly specific, low-level build interventions and custom security plugins.
