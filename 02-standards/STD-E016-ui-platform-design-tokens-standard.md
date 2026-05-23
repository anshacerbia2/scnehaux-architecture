---
doc_meta:
  id: STD-E016
  title: Enterprise UI Platform Design Tokens Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-21
---

# Enterprise UI Platform Design Tokens Standard (STD-E016)

---

## 1. Objective & Scope

This standard defines the architecture, compilation pipeline, and consumption rules for design tokens within the Scnehaux enterprise UI platform.

It guarantees that visual properties (colors, dimensions, typography, motion) are structured, compiled, and delivered consistently across all products, enabling design changes without manual style refactoring.

---

## 2. Design Token Taxonomy

Visual tokens must be structured according to a strict **3-Tier Token Architecture**:

1. **Tier 1: Core Primitives**: Raw value tokens mapping directly to design properties (e.g., `blue-500: #0070f3`, `spacing-4: 16px`). These tokens do not carry semantic meaning.
2. **Tier 2: Global Semantics**: Context-dependent tokens mapping Tier 1 values to functional definitions (e.g., `color-primary-bg: var(--ds-core-blue-500)`, `spacing-element-padding: var(--ds-core-spacing-4)`).
3. **Tier 3: Component Overrides**: Immutable tokens bound to specific component boundaries (e.g., `button-primary-bg-hover: var(--ds-semantic-color-primary-bg)`).

---

## 3. Token Compilation & Delivery Pipeline

- **Centralized Definition**: Design tokens must be defined in a platform-agnostic configuration (e.g., JSON schema) in the token repository registry.
- **CSS Custom Properties Compilation**: The token compiler must compile configuration files into standard CSS Custom Properties prefixed with `--ds-` (e.g., `--ds-color-primary`).
- **Build-Time Delivery**: Generated variables must be loaded via stylesheet bundles to ensure availability before DOM parsing.

---

## 4. Consumption Contracts

- **No Hardcoded Visual Values**: Component stylesheet files, inline styles, or layouts must not declare raw hex colors, absolute pixel spacings, or absolute font weights. All styling properties must resolve to compiled custom properties.
- **Utility Styling Compliance**: Utility-based styling libraries and utility configurations (such as Tailwind CSS or static CSS-in-JS libraries) must use custom property tokens (e.g., `bg-primary`, `p-4`) instead of arbitrary values (e.g., `bg-[#0070f3]`).

---

## 5. Compliance & Enforcement

- **Linting & AST Audits**: CSS and component files must run stylelint checkers to block raw visual values.
- **Waiver Protocol**: Custom token declarations or deviation from the 3-tier taxonomy requires a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
