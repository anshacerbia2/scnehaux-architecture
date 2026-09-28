---
doc_meta:
  id: STD-GLB-FE-009
  title: Enterprise Accessibility & Internationalization Standard
  owner: Principal Frontend Architect
  version: 2.0.0
  status: proposed
  classification: restricted
  governed_by: [GDC-000]
  authorized_by: [ADR-GLB-FE-010]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-28
---

# Enterprise Accessibility & Internationalization Standard (STD-GLB-FE-009)

> **Review candidate:** ADR-GLB-FE-010 must be accepted before this major revision becomes active.

## 1. Objective & Scope

This standard defines accessibility, internationalization, localization, directionality, and evidence requirements for user-facing web products and shared UI components.

Complete WCAG 2.2 conformance is evaluated on a full page or product flow. Shared components publish evidence for the criteria and states they own through a Component Accessibility Conformance Report.

## 2. Design Principles

1. Native HTML semantics are the first implementation choice.
2. Widget behavior follows the applicable WAI-ARIA Authoring Practices pattern where native HTML is insufficient.
3. Accessibility evidence includes keyboard, focus, name/role/value, visual presentation, and assistive technology.
4. Content, formatting, and layout support declared locales and writing directions.
5. Automated audits supplement manual evaluation.

## 3. Normative Rules

### 3.1 Conformance target and ownership

User-facing product pages target WCAG 2.2 Level AA. Product teams evaluate complete content and workflows. Shared component owners test applicable criteria across supported states and document consumer responsibilities.

A Component ACR is evidence for a component. VPAT-based reporting is reserved for an evaluated product or procurement scope.

### 3.2 Semantics, keyboard, and focus

Interactive elements use native elements where their semantics and behavior fit. Custom composite widgets document their applicable APG pattern, focus model, required and optional keys, typeahead, disabled behavior, and controlled/uncontrolled state.

Every operable element is reachable and usable with the keyboard. Focus is visible (WCAG 2.2 SC 2.4.7) and the focused element is not entirely hidden by author-created content (SC 2.4.11). The indicator is an `outline`; a shadow may enhance it but never replaces it, because forced-colors mode computes `box-shadow` as `none` (STD-GLB-FE-005 section 3.9). Modal overlays contain focus according to their pattern and restore focus to a valid target on close; non-modal overlays do not trap focus.

Icon-only controls expose an accessible name. Dynamic announcements use an appropriate live region. Decorative images use empty alternative text.

### 3.3 Contrast and color

- Normal text meets WCAG 2.2 SC 1.4.3 at 4.5:1.
- Large-scale text meets SC 1.4.3 at 3:1.
- User interface components and meaningful graphical objects meet SC 1.4.11 at 3:1 against adjacent colors.
- Focus indicators meet SC 1.4.11 at 3:1 against the colors adjacent to the indicator. The Level AAA focus appearance criterion (SC 2.4.13) is outside the AA target.
- Color is not the sole means of conveying information.

Tests use actual foreground/background pairs after alpha composition in each supported theme and state. OKLCH or APCA measurements may provide additional design evidence and do not replace the published WCAG 2.2 release target.

### 3.4 Reflow, target size, and display preferences

Content covered by WCAG 2.2 SC 1.4.10 reflows at 320 CSS px without two-dimensional scrolling, subject to the criterion's exceptions. Pointer targets satisfy SC 2.5.8 at 24 by 24 CSS px or one of its defined exceptions.

Supported UI remains usable under text zoom, browser zoom, forced-colors mode, and `prefers-reduced-motion`. Reduced-motion behavior removes or substitutes non-essential motion while preserving state communication.

### 3.5 Assistive technology evidence

Stable composite widgets receive manual checks with NVDA and VoiceOver for the supported browser matrix. The record includes component version, browser, operating system, assistive-technology version, scenario, expected announcement, actual result, and known limitation.

Automated tools such as axe detect a subset of failures and cannot close manual behavior gates.

### 3.6 Internationalization and localization

User-facing strings come from locale resources. Pluralization and grammatical variants use ICU MessageFormat or an equivalent approved message system. Dates, numbers, relative time, lists, and currencies use `Intl` APIs with an explicit locale and time-zone policy.

Components use logical CSS properties and support declared left-to-right and right-to-left layouts. Public APIs accept localized labels and do not assemble sentences from fragments that translators cannot reorder.

### 3.7 Language and content boundaries

Pages declare their primary language and mark language changes where required. Validation, status, and error messages are programmatically associated with the relevant control. Truncation provides an accessible path to the complete meaningful value.

## 4. Exceptions

Canvas, virtualized, or specialized widgets without a native equivalent may use a custom accessibility representation. The implementation must provide the required name, role, value, keyboard model, focus behavior, and an equivalent accessible view when the visual surface cannot expose the content.

## 5. Enforcement Mechanism

- Source and interaction tests validate semantics, ARIA state, keyboard behavior, focus, and cleanup.
- Browser tests cover reflow, target size, themes, reduced motion, forced colors, direction, and declared contrast pairs.
- Automated accessibility scans (for example axe-core) run on components and critical product routes. A pull request that introduces a new automated violation on a covered component or route is blocked.
- The build fails when a user-facing string resolves to a missing translation key or a declared locale lacks its message resource.
- A forced-colors browser fixture asserts a visible focus outline on every focusable supported component.
- Manual NVDA and VoiceOver evidence is required for stable composite widgets.
- Product release review evaluates full-page WCAG 2.2 conformance and known limitations.

A missing required scenario blocks stable promotion for the affected component or product flow.
