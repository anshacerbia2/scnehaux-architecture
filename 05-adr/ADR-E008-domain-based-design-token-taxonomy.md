---
doc_meta:
  id: ADR-E008
  title: ADR-E008 Domain-Based Design Token Taxonomy Adoptation
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-19
---

# ADR-E008: Domain-Based Design Token Taxonomy Adoption

---

## 1. Title
Adoption of a Technology-Agnostic, Domain-Based Design Token Taxonomy (family.role.variant) over Legacy Flat and Property-Based Naming Systems

## 2. Status
Accepted

## 3. Context
Historically, design token systems inside the Scnehaux platform and downstream web applications utilized a combination of **Property-based** and **Flat Intent-based** naming conventions (e.g., `success-subtle-hover`, `bg-muted-hover`, `bg-canvas`). While requiring minimal setup initially, this flat architecture introduced critical engineering bottlenecks as the system scaled to support multi-brand and white-labeled micro-frontends:
1.  **Token Explosion**: Every new surface or widget context required unique pre-multiplied static state tokens. The token map grew quadratically, leading to high maintenance overhead and a massive bundle footprint.
2.  **Visual Flattening Trap**: A static hover state color (e.g., a solid gray) applied to different base background elements (e.g., green success cards, red alert banners, or white card panels) completely overwrote their background color. This caused elements to lose their color identity and semantic intent upon pointer interaction.
3.  **Lack of Semantic Cohesion**: Without a hierarchical, logical taxonomy, tokens were distributed as a flat list, making it impossible to perform automated contract validation, contextual inheritance, or clean overrides for third-party brands.
4.  **Multi-Platform Translation Friction**: The flat naming scheme was heavily web-centric (specifically SCSS/CSS-focused), presenting severe integration barriers when compiling tokens for native mobile applications (iOS/Android) or feeding them into token pipelines like Style Dictionary.

## 4. Decision
We officially adopt a technology-agnostic, **Domain-Based Design Token Taxonomy** structured around a strict hierarchical **`family.role.variant` (dot-notation)** standard. 

### 4.1 Structural Taxonomy Format
All design tokens must strictly adhere to the dot-notation standard representing distinct visual axes:
*   **Color Families**: `surface.canvas`, `text.primary`, `border.default`, `state.hover`, `feedback.success.subtle`
*   **Dimension Families**: `spacing.md`, `radius.lg`, `stroke.default`, `z.modal`
*   **Typography Families**: `font-size.md`, `font-weight.bold`, `line-height.normal`, `letter-spacing.normal`
*   **Motion Families**: `duration.fast`, `easing.standard`, `transition.hover`

### 4.2 Orthogonal State Separation & Blending Layer Invariant
We decouple the background surface and the interactive state into independent, orthogonal axes. Instead of pre-multiplying them in static tokens (like the legacy `success-subtle-hover`), we apply:
1.  **Alpha Blending Overlay Layer (Standard Hover/Press)**: Interactive states (`state.hover`, `state.pressed`) are registered as semi-transparent alpha overlays (e.g., neutral `300A` or `rgba(0,0,0, 0.04)` in Light Mode; neutral `200A` or `rgba(255,255,255, 0.08)` in Dark Mode).
2.  **GPU-Accelerated Blending**: These overlays are rendered dynamically on top of the base background using pseudo-elements (`::before` / `::after`) or CSS background overlays, allowing the state to organically blend with any underlying surface color without mutating the base background value.
3.  **Contextual Re-binding Scope**: Where direct blending is not viable, design variables are re-bound contextually at the CSS/SCSS scope level using local indirection variables, ensuring clean inheritance and zero layout reflows.

---

## 5. Rationale
Adopting this taxonomy achieves maximum semantic clarity and engineering efficiency. The hierarchical structure allows us to divide primitive values (Tier-1) from global semantic contracts (Tier-2) and unique component overrides (Tier-3). 

By separating **Surfaces** from **States** and employing the **Alpha Overlay Blending standard**, we solve the visual flattening trap once and for all: a single `state.hover` token dynamically scales to darken or lighten any background surface (white canvas, blue brand buttons, green success cards) while fully preserving their semantic color identity and AAA accessibility contrast.

---

## 6. Alternatives Considered

### Alternative A: Legacy Property-Based Flat Tokens (`bg-canvas-hover`)
*   **Pros**: Flat mappings that compile directly to classic Sass variables without nesting hierarchy.
*   **Cons**: Massive token explosion. Introduces high maintenance friction when overriding specific tokens for custom brands, as every hover state has to be manually written and registered. High risk of visual inconsistency.
*   **Why Rejected**: Disallowed due to lack of scalability and inability to perform automated contract validation.

### Alternative B: Direct CSS Color-Mix Globally
*   **Pros**: Fully native browser-level color mixing without extra absolute overlay layers in the DOM.
*   **Cons**: Relies on modern browser support (`color-mix()` in sRGB color space). Can fail or require heavy polyfills in legacy enterprise environments.
*   **Why Rejected**: Retained as a secondary compile-time compiler option, but rejected as the primary global mechanism to guarantee backward compatibility with old micro-frontend hosting engines.

---

## 7. Consequences

### Positive
- **Drastic Token Reduction**: Decoupling surfaces from states reduces the total required token scale by over `70%`, leading to a highly compact CSS bundle size (maximum `12KB` gzip).
- **Flawless Visual Blending**: Guarantees that interactive hovers and presses preserve background color identity and contrast.
- **Strict Contract Validation**: The hierarchical structure enables compile-time linting and automated audits to ensure multi-brand themes only override valid `$system` contract keys.
- **Technology-Agnostic**: Dot-notation compiles perfectly to Figma variables, CSS Custom Properties, SCSS variables, Style Dictionary JSON, and native mobile properties (iOS/Android).

### Negative
- **Layout Precision Discipline**: Developers must wrap interactive elements with relative positioning context to accommodate absolute pseudo-element overlay blending layers, or adhere strictly to the contextual custom property re-binding standard.

### Tradeoffs
- We trade absolute simplicity in naming for a highly structured, scalable, and mathematically consistent token hierarchy.

### Operational Impact
- The CI pipeline automatically validates all custom brand contract overrides (`_achromatic-contract.scss`) using the Python linter, preventing undocumented keys from leaking into production.

### Security Impact
- Restricts custom CSS injection, forcing developers to use governed paved-road design tokens which are pre-audited for accessibility and security contrast compliance.

---

## 8. Risks
- **Developer Friction**: Developers might find dot-notation and overlay layers more complex than writing flat styles.
  - *Mitigation*: Solved by providing auto-compiled strongly-typed Sass variables (like `$color-bg-canvas` mapping to `--ds-color-bg-canvas`) and standard helper mixins (e.g. `@include state-overlay('hover')`) in `@scnx/system`.

## 9. Implementation Notes
- The domain-based taxonomy is formalized as the core design token API standard starting with `version: 1.0.0`.
- The compilation pipeline automatically maps logical dot-notation tokens to physical space-separated HSL or OKLCH custom properties to support dynamic runtime opacity modifiers (`hsl(var(--ds-...) / opacity)` or `oklch(var(--ds-...) / opacity)`).

## 10. Related Documents
- [Documentation Governance Standard (GDC-000)](file:///d:/Ansha/architecture-description/scnehaux-architecture/00-governance/documentation-governance-standard.md)
- [Scnehaux UI Platform Logical PAD (DOC-P002)](file:///d:/Ansha/architecture-description/scnehaux-architecture/02-platform/scnehaux-ui-platform/scnehaux-ui-platform.pad.md)
- [Scnehaux UI Platform Physical SAD (DOC-S003)](file:///d:/Ansha/architecture-description/scnehaux-architecture/03-applications/scnehaux-ui-platform/scnehaux-ui-platform.sad.md)
- [SCNX Master Semantic Taxonomy (scnx-master-semantic-taxonomy.md)](file:///d:/Ansha/js/module_federation_v1.5/packages/design-system/src/styles/docs/scnx-master-semantic-taxonomy.md)
- [SCNX Downstream Integration Standard (STD-SCNX-UI-JS-002)](file:///d:/Ansha/js/module_federation_v1.5/packages/docs/05-standards/STD-SCNX-UI-JS-002-developer-integration-standard.md)
