---
doc_meta:
  id: STD-UIP-STY-001
  title: Enterprise UI Platform Styled Components & Compilation Standard
  owner: Principal Frontend Architect
  version: 2.0.0
  status: proposed
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-28
---

# Enterprise UI Platform Styled Components & Compilation Standard (STD-UIP-STY-001)

> **Review draft:** these rules describe the target contract; the copied baseline does not yet satisfy it.

---

## 1. Objective & Scope

This standard defines the implementation rules, build-time compilation constraints, and style isolation boundaries for styled components and visual compilation engines within the Scnehaux enterprise design system.

Styles are emitted as static assets. Theme state and component behavior may still execute JavaScript. Isolation is a property of the emitted selectors and their tested consumer scope, not a consequence of compilation alone.

---

## 2. Design Principles

The styling and compilation engine adheres to four core principles to ensure rendering performance, theme stability, and visual encapsulation:

1. **Static CSS output**: component and theme styling is compiled before publication; the consumer import contract determines which assets load.
2. **Scoped selectors**: shared resets and themes do not target unrelated host or remote markup.
3. **Verified colors**: OKLCH authoring is paired with an explicit browser support policy and contrast tests for declared semantic pairs.
4. **Scoped theme state**: a theme can be applied to a named root without mutating another brand's root. The exact multi-brand implementation remains open.

## 3. Normative Rules

### Zero-Runtime Compilation

All styling engines deployed within the UI platform (such as static CSS-in-JS engines or Sass/SCSS compilers) must compile styles statically during the application build phase.

- **Prohibition of Runtime CSS-in-JS**: Using styling libraries that perform runtime style injection or dynamic evaluation in the React render path (such as legacy runtime CSS-in-JS libraries) is prohibited on performance-sensitive paths.
- **Output contract**: SCSS component rules and Panda recipes MAY coexist while they have named ownership, a single token contract, deterministic cascade order, and a measured cost. Consolidation into one engine is an open decision.

---

### Style Encapsulation in Federated Environments

To prevent visual layout conflicts when multiple micro-frontends share the same browser DOM environment:

- **Global Selector Prohibition**: A shared reset or theme must be scoped to a documented root. `@layer` controls precedence but does not scope a selector. Unscoped element selectors and unconditional `:root` theme overrides cannot be treated as isolated in a federated DOM.
- **Prefix Isolation**: CSS class names must be prefixed uniquely based on the domain boundary:
  - Core design system: `scnx-` prefix.
  - Subdomain remotes: domain-specific prefixes (e.g. `scnx-hris-`, `scnx-fin-`).
- **CSS Modules Naming**: CSS modules must resolve to hash-appended unique classes during compilation.
- **Cascade contract**: The relative order of reset, tokens, component rules, recipes, and consumer overrides must be documented and tested. Component SCSS outside declared layers is measured for override conflicts.
- **Theme coexistence**: Packed-package tests render two roots with distinct themes and check computed styles for leakage. A global callback or document-wide theme mutation cannot establish multi-brand isolation.

---

### Build Pipeline Visual Testing

- **Visual Regression Suite**: Modifying core styled components requires passing visual regression tests (such as Playwright visual comparison check) in the CI pipeline before merging.
- **Bundle Size Checks**: Build processes must track styling output bundles to prevent layout CSS bloat.
- **Artifact checks**: Test that all documented CSS entry points resolve after packing, a single imported component is styled, and every required token reference resolves to a value valid for its consuming CSS property.

---

## 4. Exceptions

Exceptions identify the affected selector or theme contract, supported consumer scenarios, expiry, and test evidence.

## 5. Enforcement Mechanism

- **Source checks**: Static analysis checks token usage, selector scoping, and unintended runtime CSS injection.
- **Packed-package checks**: A separate consumer verifies CSS exports, computed styling, two-root isolation, and override precedence in the supported browser matrix.
