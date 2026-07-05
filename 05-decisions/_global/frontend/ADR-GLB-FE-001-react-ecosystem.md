---
doc_meta:
  id: ADR-GLB-FE-001
  title: ADR-GLB-FE-001 Standardization on React and Framework Paved Road
  adr_type: foundational
  status: accepted
  created: 2026-04-04
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-001: Standardization on React and the Framework Paved Road

---

## 1. Title

Standardization on React and the Framework Paved Road

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                              | Approver                  |
| ---------- | -------- | ------------ | -------------------------------------- | ------------------------- |
| 2026-04-04 | proposed | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |
| 2026-04-07 | accepted | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |

## 3. Context

As the enterprise scales its digital ecosystem across dozens of independent product verticals, the lack of a standardized frontend rendering engine has led to fragmented ecosystems. Teams have historically utilized a mix of AngularJS, Vue, and vanilla Web Components, resulting in disconnected design systems, duplicated engineering effort, and an inability to share specialized talent or tooling across boundaries.

## 4. Decision Drivers

- **UI Platform Consolidation**: The Enterprise UI Platform (Design Tokens and Primitives) requires a single, exclusive compilation target to eliminate the overhead of maintaining multiple framework wrappers.
- **Hybrid Rendering Mandate**: The engine must robustly support both high-interactivity Single Page Applications (SPAs) and Server-Side Rendering (SSR) paradigms without fragmenting the component architecture.
- **Talent Acquisition & Mobility**: Enterprise scale demands a technology with a vast, mature global talent pool to accelerate hiring and enable engineers to move fluently between product verticals.
- **Ecosystem Maturity**: The framework must possess an enterprise-grade ecosystem of third-party tooling, testing libraries, and community support to minimize in-house maintenance overhead.

## 5. Decision

We will standardize **React** as the exclusive rendering engine and foundational paved road for all enterprise frontend web applications. Applications must utilize React in conjunction with an approved modern build toolchain or meta-framework as governed by [ADR-GLB-FE-002 (Build Toolchains)](./ADR-GLB-FE-002-build-toolchain.md).

## 6. Consequences

### Positive

- **Talent Liquidity**: Unlocks engineering mobility across teams and product verticals.
- **Unified Ecosystem**: Establishes a single, highly cohesive foundation for the Design System.
- **Tooling Consolidation**: Allows CI/CD pipelines and developer tooling to be standardized centrally.

### Negative & Risks

- **Migration Fatigue**: Legacy teams (Angular/Vue) face steep rewrite costs which may temporarily stall feature delivery.
- **Payload Overhead**: React carries a heavier baseline Javascript payload compared to compiler-first alternatives.
- **Version Fragmentation**: Teams might stall on older legacy versions, failing to adopt the concurrent features required by modern React.

### Operational

- All new repositories must be bootstrapped using the official Enterprise React scaffolding CLI.
- `React.StrictMode` is mandatory in all non-production environments.

## 7. Compliance Impact

### Related Standards

- [ADR-GLB-FE-002 (Build Toolchains)](./ADR-GLB-FE-002-build-toolchain.md) - Dictates the mandatory build and compilation toolchains for React applications.
- [STD-GLB-FE-001 (Tech Stack)](../../../02-standards/_global/frontend/STD-GLB-FE-001-tech-stack.md) - Contains the normative rules for using React and Next.js/Vite.
- STD-GLB-FE-007 (React Standards) - Defines the strict rendering rules and boundaries.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **Vue.js / Nuxt**: Rejected. While offering excellent developer ergonomics, the surrounding enterprise ecosystem and external talent pool are vastly eclipsed by React.
- **Svelte**: Rejected. Despite superior baseline bundle sizes, its meta-framework ecosystem is not yet mature enough to support our complex Micro-Frontend requirements.
- **Vanilla Web Components**: Rejected. Deeply flawed interoperability with complex state management and poor SSR hydration stories.

