---
doc_meta:
  id: STD-GLB-FE-009
  title: Enterprise Accessibility & Internationalization Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: assessed
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-05-31
---

# Enterprise Accessibility & Internationalization Standard (STD-GLB-FE-009)

---

## 1. Objective & Scope

This standard defines the mandatory requirements for Universal Access across the Scnehaux enterprise frontend ecosystem. It combines two closely related architectural domains:

1. **Accessibility (a11y)**: Ensuring applications are fully usable by individuals with disabilities, including those relying on screen readers, keyboard-only navigation, and specialized display modes.
2. **Internationalization (i18n) & Localization (l10n)**: Ensuring applications can adapt dynamically to varying languages, regional formats, and reading directions without requiring codebase forks.

The scope of this standard applies to:

- **Design Tokens**: Governing color contrast math (e.g., OKLCH lightness thresholds) and spacing minimums for touch targets.
- **Primitive Components**: Serving as the absolute baseline for ARIA semantics, focus trapping, and keyboard event matrices.
- **Application Layouts**: Defining logical document structure, semantic landmarks, and rendering order.
- **Content Strings**: Governing the externalization and pluralization of user-facing text.

---

## 2. Design Principles

- **Inclusive by Default**: Accessibility is not a feature or a post-launch enhancement; it is a foundational human right and a legal compliance requirement. Features that cannot be navigated via keyboard or screen reader are considered broken.
- **Semantic First**: The browser's native HTML elements are inherently accessible. ARIA attributes must only be used as a last resort to patch gaps in native HTML semantics or to describe complex interactive widgets.
- **Cultural Agnosticism**: Application logic must remain decoupled from specific languages, currencies, or timezones. Code must rely on standard `Intl` APIs and externalized translation dictionaries.

---

## 3. Normative Rules

### 3.1 WCAG Compliance Tier

- All user-facing web interfaces must achieve strict compliance with the **WCAG 2.2 AA** standard.
- Compliance with WCAG 2.2 AAA is aspirational for public portals but not strictly enforced across internal dashboards unless dictated by specific government contracts.

### 3.2 Semantic HTML & ARIA Governance

- **Native Elements**: Developers must prioritize native HTML elements (e.g., `<button>`, `<dialog>`, `<nav>`) over building custom ARIA-role div constructs (e.g., `<div role="button">`).
- **No ARIA Abuse**: The first rule of ARIA is: _No ARIA is preferable to bad ARIA_. Incorrectly applied ARIA attributes that conflict with native semantics are strictly prohibited.
- **Live Regions**: Dynamic UI updates that do not trigger focus shifts (e.g., toast notifications, form submission success messages) must utilize `aria-live` regions to announce changes to assistive technologies.

### 3.3 Keyboard Navigation & Focus Engineering

- **Focus Indicators**: All interactive elements must implement clear focus indicators using `:focus-visible`. Disabling focus outlines (`outline: none`) without providing a visible, compliant alternative is a critical violation.
- **Focus Trapping**: Modals, dialogs, and intrusive overlays must trap keyboard focus within the overlay until closed.
- **Focus Restoration**: Upon closing an overlay or modal, the browser focus must automatically return to the exact element that triggered the overlay.

### 3.4 Screen Reader Support

- **Hidden Labels**: Icon-only buttons or visual-only indicators must provide visually hidden text (`.sr-only`) or descriptive `aria-label` attributes for screen reader consumption.
- **Decorative Images**: Images that do not convey essential information must utilize empty alt attributes (`alt=""`) to remove them from the accessibility tree.

### 3.5 Assistive Display Modes

- **Reduced Motion (`prefers-reduced-motion`)**: All layout-shifting animations and continuous loops must be disabled or replaced with crossfades when the user's OS requests reduced motion.
- **Forced Colors Mode**: Applications must remain visually usable and structurally intact under forced-colors mode (`@media (forced-colors: active)`), ensuring borders and SVGs do not disappear in high-contrast environments.
- **Contrast Ratios**: Text and interactive elements must maintain a minimum contrast ratio of 4.5:1 against their backgrounds.

### 3.6 Translation Key Abstraction (i18n)

- **No Hardcoded Strings**: Hardcoding user-facing text strings directly inside component logic or templates is strictly prohibited. All strings must be extracted to dictionary files and accessed via a localization hook/function (e.g., `t('auth.login.submit')`).

### 3.7 Pluralization & Locale-Aware Formatting

- **ICU MessageFormat**: Complex string interpolation involving plurals, gender, or grammatical cases must utilize the ICU MessageFormat standard. Manual string concatenation or ternary operators for plurals are prohibited.
- **Formatting APIs**: Applications must rely exclusively on the native `Intl` browser APIs (`Intl.DateTimeFormat`, `Intl.NumberFormat`, `Intl.RelativeTimeFormat`) for formatting dates, times, and currencies. Custom formatting logic is prohibited.

### 3.8 RTL & Bidirectional Layout

- **Logical CSS Properties**: CSS stylesheets must use logical properties (e.g., `margin-inline-start`, `padding-block-end`) rather than physical directional properties (`margin-left`, `padding-bottom`) to ensure automatic layout mirroring for Right-to-Left (RTL) languages like Arabic and Hebrew.

---

## 4. Exceptions

Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk.

### Exception to "Semantic HTML Foundations" (Rule 3.1)

- **Condition for Deviation**: You are integrating a highly complex imperative widget (e.g., custom data grids or canvas-based editors) that lacks a native HTML equivalent.
- **Mandatory Alternative**: Native ARIA role overrides are permitted, provided the implementation perfectly mirrors the exact keyboard interaction and focus matrix defined in the WAI-ARIA Authoring Practices Guide (APG).

### Exception to "Dynamic DOM Traversal Limits" (Rule 3.3)

- **Condition for Deviation**: A high-density data application (e.g., trading terminals) requires rendering 10,000+ nodes where strict ARIA DOM mapping causes severe screen-reader traversal hangs.
- **Mandatory Alternative**: You may bypass strict ARIA mapping on the primary visual interface _only if_ a fallback, visually hidden Accessible Data Table view is provided in parallel exclusively for assistive technologies.

## 5. Enforcement Mechanism

- **Automated A11y Audits**: CI/CD pipelines must execute automated accessibility assertion tools (e.g., `axe-core`) against component libraries and critical application routes. PRs introducing new WCAG violations will be blocked.
- **Translation Coverage**: Build tools must fail the compilation step if unresolved translation keys or missing locale dictionaries are detected.
- **Waiver Protocol**: Deviations from this standard must be documented in a local project ADR. The Architecture Review Board (ARB) must respond with a review decision within **5 business days** of the ADR submission.
