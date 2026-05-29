---
doc_meta:
  id: STD-UIP-STY-001
  title: Enterprise UI Platform Styled Components & Compilation Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-21
---

# Enterprise UI Platform Styled Components & Compilation Standard (STD-UIP-STY-001)

---

## 1. Objective & Scope

This standard defines the implementation rules, build-time compilation constraints, and style isolation boundaries for styled components and visual compilation engines within the Scnehaux enterprise design system.

It guarantees that styles are resolved at compile-time with zero runtime overhead, and prevent styling conflicts in federated or multi-tenant browser environments.

---


## 2. Design Principles

*(TBD - Architectural philosophy guiding these rules)*

## 3. Normative Rules

### Zero-Runtime Compilation

All styling engines deployed within the UI platform (such as static CSS-in-JS engines or Sass/SCSS compilers) must compile styles statically during the application build phase.
- **Prohibition of Runtime CSS-in-JS**: Using styling libraries that perform runtime style injection or dynamic evaluation in the React render path (such as legacy runtime CSS-in-JS libraries) is prohibited on performance-sensitive paths.
- **Atomic Extraction**: Styling rules must compile down to atomic static CSS class strings.

---

### Style Encapsulation in Federated Environments

To prevent visual layout conflicts when multiple micro-frontends share the same browser DOM environment:
- **Global Selector Prohibition**: Micro-frontends and shared component libraries are prohibited from using global CSS selectors. Style boundaries must use local CSS Modules or unique class prefixes.
- **Prefix Isolation**: CSS class names must be prefixed uniquely based on the domain boundary:
  - Core design system: `scnx-` prefix.
  - Subdomain remotes: domain-specific prefixes (e.g. `scnx-hris-`, `scnx-fin-`).
- **CSS Modules Naming**: CSS modules must resolve to hash-appended unique classes during compilation.

---

### Build Pipeline Visual Testing

- **Visual Regression Suite**: Modifying core styled components requires passing visual regression tests (such as Playwright visual comparison check) in the CI pipeline before merging.
- **Bundle Size Checks**: Build processes must track styling output bundles to prevent layout CSS bloat.

---


## 4. Exceptions & Alternatives

Deviations from these normative rules require an approved exception waiver from the Architecture Review Board (ARB).

## 5. Enforcement Mechanism

- **Static Analysis**: CI/CD pipelines must check Rspack/Webpack configurations to block non-static styling libraries.
- **Waiver Protocol**: Deviations from the zero-runtime mandate or style prefix boundaries require a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
