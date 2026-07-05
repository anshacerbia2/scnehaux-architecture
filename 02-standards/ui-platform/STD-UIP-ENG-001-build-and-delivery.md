---
doc_meta:
  id: STD-UIP-ENG-001
  title: UI Platform Build & Delivery Standards
  owner: Principal UI/UX Architect
  version: 1.0.0
  status: adopted
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-06-26
---

# UI Platform Build & Delivery Standards (STD-UIP-ENG-001)

## 1. Objective & Scope

This standard governs the quality, payload, and delivery constraints for all packages within the Scnehaux UI Platform ecosystem (e.g., `@scnx/core-ui`, `@scnx/system`). It defines the absolute boundaries for performance, regression testing, and distribution formats to ensure zero architectural degradation when integrated into downstream consumer portals.

## 2. Design Principles

- **Reproducibility**: All builds must be perfectly reproducible across developer machines and CI servers.
- **Fail-Fast**: The pipeline must fail as early as possible on style, lint, or type errors before running expensive test suites.
- **Immutable Artifacts**: Built UI bundles are immutable. We deploy the same binary/bundle through all environments.

## 3. Standard Policies

### 3.1 Payload Budget & Performance

To guarantee instant execution within federated frontends, UI platform packages must adhere to strict payload limits:

- **Max CSS/JS Gzip Size:** The core design token matrix and primitive layer combined MUST NOT exceed **12KB** compressed (gzip).
- **Latency (Theme Switch):** Context propagation for global theme swaps (Light/Dark/Tenant) MUST execute in under **50ms**.
- **Reflow Ban:** Component entrance/exit transitions MUST utilize Zero-Reflow mechanics (Orthogonal Finite State Machines using double-rAF), achieving `0` layout reflows per transition.

### 3.2 Testing & Quality Gates

The UI Platform acts as the visual root of trust. Its testing strategy is non-negotiable:

- **Visual Regression Testing:** Component changes in `@scnx/system` MUST pass a Visual Regression suite (e.g., Chromatic or Storybook visual tests) before merge.
- **Unit Testing:** Behavior components in `@scnx/core-ui` MUST be covered by Vitest (or equivalent) testing with render-count isolation assertions.
- **Accessibility (A11y):** All interactive primitives MUST pass automated `jest-axe` (or equivalent) WCAG 2.2 AA validations in CI.

### 3.3 Distribution Format

To support modern Module Federation consumers while maintaining legacy fallback compatibility:

- **Dual Formats:** All packages MUST compile and publish in both **ESM** and **CJS** formats.
- **React Directives:** The `"use client"` directive MUST be explicitly restored post-bundle (via esbuild plugins) to guarantee compatibility with React Server Components (RSC) and Next.js App Routers.

## 4. Enforcement & Compliance

These standards are enforced directly by CI/CD pipelines (Quality Gates). Any PR that breaches the 12KB budget or fails Visual Regression will be **Hard Blocked** from merging. Temporary waivers must be escalated to the Architecture Review Board (ARB) via an Architecture Decision Record (ADR).
