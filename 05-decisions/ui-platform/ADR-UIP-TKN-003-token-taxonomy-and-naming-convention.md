---
doc_meta:
  id: ADR-UIP-TKN-003
  title: ADR-UIP-TKN-003 Token Taxonomy & Naming Convention
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
---

# ADR-UIP-TKN-003: Adoption of a unified Design Token Taxonomy & Naming Convention across all UI platform tiers.

---

## 1. Title

Adoption of a unified Design Token Taxonomy & Naming Convention across all UI platform tiers.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

Historically, design token systems inside the Scnehaux UI Platform and downstream web applications utilized a combination of **Property-based** and **Flat Intent-based** naming conventions (e.g., `success-subtle-hover`, `bg-muted-hover`, `bg-canvas`). While requiring minimal setup initially, this flat architecture introduced critical engineering bottlenecks as the system scaled to support multi-brand and white-labeled micro-frontends:

1.  **Token Explosion**: Every new surface or widget context required unique pre-multiplied static state tokens. The token map grew quadratically, leading to high maintenance overhead and a massive bundle footprint.
2.  **Visual Flattening Trap**: A static hover state color (e.g., a solid gray) applied to different base background elements (e.g., green success cards, red alert banners, or white card panels) completely overwrote their background color. This caused elements to lose their color identity and semantic intent upon pointer interaction.
3.  **Lack of Semantic Cohesion**: Without a hierarchical, logical taxonomy, tokens were distributed as a flat list, making it impossible to perform automated contract validation, contextual inheritance, or clean overrides for third-party brands.
4.  **Multi-Platform Translation Friction**: The flat naming scheme was heavily web-centric (specifically SCSS/CSS-focused), presenting severe integration barriers when compiling tokens for native mobile applications (iOS/Android) or feeding them into token pipelines like Style Dictionary.

## 4. Decision Drivers

Adopting this combinatorial taxonomy achieves maximum semantic clarity and architectural predictability. By grouping tokens into strict Design Domains (Color, Dimension, Typography, Motion), we prevent cross-contamination of token values.

Furthermore, the strict hierarchical structure allows us to cleanly divide raw, mode-agnostic mathematical scales (Tier-1 Core/Primitive Tokens) from the human-readable global semantic contracts (Tier-2 Semantic/System Tokens) and the highly specific overrides (Tier-3 Component/Alias Tokens). This isolation guarantees that brand re-skinning or theme generation can occur entirely at Tier-2 without ever touching a component's source code or the raw primitive scales.

---

## 5. Decision

We officially adopt a unified, technology-agnostic **Design Token Taxonomy** across all three isolation tiers of the UI Platform.

### 4.1 The "Design Domain-Based" Root Principle

To prevent semantic collision and massive flat-lists, the taxonomy enforces a strict **Design Domain-Based** root grouping (also known as Token Families) across all tiers. Every token must strictly belong to one of four technical design domains:

1. **Color Domain**: Governs all paints, fills, and shadows.
2. **Dimension Domain**: Governs all physical layout space (spacing, sizing, radii, borders, z-index).
3. **Typography Domain**: Governs all text rendering properties.
4. **Motion Domain**: Governs all temporal transitions and physics.

By isolating tokens into these four domains at the root level, we prevent cross-contamination (e.g., mixing a z-index number with a font-weight number) and establish a highly predictable, auto-completable developer experience.

### 4.2 Naming Convention Vocabulary (The Bracket Variables)

Before defining the tier structures, we must establish the precise definitions for the variables used in the naming convention brackets `[...]`:

- **`[property]`**: The specific CSS or design property being scaled (e.g., `spacing`, `radius`, `font-weight`, `shadow`).
- **`[scale]`**: The general magnitude or variant of a property. Depending on the domain, this is specifically expressed as:
  - **`[size]`**: Can be a numeric value (e.g., `spacing.4`, `opacity.60`) or a T-shirt size (e.g., `radius.sm`, `shadow.lg`).
  - **`[speed]`**: Used for motion properties (e.g., `duration.fast`, `easing.standard`).
  - **`[intent]`**: Used for context-driven semantic magnitudes (e.g., `container-width.prose`, `font-weight.bold`).
- **`[color]`**: The hue family (e.g., `blue`, `neutral`).
- **`[step]`**: The monotonic grade (`1-12` for Solid, `1A-12A` for Alpha) used exclusively for color contrast scaling. See [ADR-UIP-TKN-002](ADR-UIP-TKN-002-oklch-and-dual-engine-alpha.md).
- **`[axis]`**: The lighting context (`light` or `dark`) required for Symmetrical Palette Generation. See [ADR-UIP-TKN-002](ADR-UIP-TKN-002-oklch-and-dual-engine-alpha.md).

### 4.3 Tier-1: Core/Primitive Tokens (The Raw Scales)

The taxonomy format diverges based on the domain:

- **Color Domain**: `[color].[axis].[step]`
  - _Examples:_ `blue.light.9`, `neutral.dark.1A`
  - _Axis Layer:_ Required to support Dual-Axis Symmetrical Palette Generation.
  - _Step Variant:_ The `step` defines the scale grade, which consists of **Solid** steps (`1` to `12`) and **Alpha/Translucent** steps (`1A` to `12A`).
- **Dimension Domain**: `[property].[size]` (e.g., `spacing.4`, `radius.lg`, `z-index.10`, `breakpoint.md`)
- **Typography Domain**: `[property].[size]` (e.g., `font-size.16`, `font-weight.bold`, `line-height.relaxed`)
- **Motion Domain**: `[property].[speed]` (e.g., `duration.fast`, `easing.standard`)

### 4.4 Tier-2: Semantic/System Tokens (The Global Intent)

Unlike Tier-1 which scales mathematically, Tier-2 assigns structural UI intent. The taxonomy format here diverges significantly depending on the family:

- **Color Domain (The Scheme-Based Matrix)**: Because color intent is highly complex, it abandons the standard property format and instead uses a strict **Scheme-Based Taxonomy**: `[scheme].[role].[emphasis].[state]`.
  - _Examples:_ `primary.solid.default.hover`, `danger.surface.subtle.default`, `neutral.canvas.default`.
- **Other Domains (Dimension, Typography, Motion)**: These families retain the standard `[property].[scale]` format from Tier-1, but the `[scale]` value transitions from raw primitive numbers into **Semantic/T-Shirt sizes**.
  - _Dimension:_ `spacing.md`, `radius.lg`, `stroke.default`, `z.modal`
  - _Typography:_ `font-size.md`, `font-weight.bold`, `line-height.normal`, `letter-spacing.normal`
  - _Motion:_ `duration.fast`, `easing.standard`, `transition.hover`

### 4.5 Tier-3: Component/Alias Tokens (Unique Overrides)

Format: `[component].[element].[property].[state]` (Note: `[element]` and `[state]` are optional context layers)

- **Examples (`[component].[property]`)**: `card.shadow`, `dialog.z-index`
- **Examples (`[component].[property].[state]`)**: `button.bg.hover`, `input.border.focus`
- **Examples (`[component].[element].[property].[state]`)**: `checkbox.indicator.bg.checked`, `switch.track.bg.disabled`

---

## 6. Consequences

### Positive

- **Predictable Payload**: Matrix compilation generates exactly 740 pre-resolved semantic color tokens, well within the 12KB gzip budget.
- **Zero DOM Bloat**: Eliminates the need for pseudo-element (`::before`) interaction overlays.
- **Strict Contract Validation**: The hierarchical 4-layer structure enables compile-time linting and automated audits to ensure multi-brand themes only override valid `$system` contract keys.
- **Technology-Agnostic**: Dot-notation compiles perfectly to Figma variables, CSS Custom Properties, SCSS variables, Style Dictionary JSON, and native mobile properties (iOS/Android).

### Negative

- **AOT Build Dependency**: The CSS bundle must be fully recompiled when Lightness/Chroma shift algorithms change, rather than relying on runtime browser calculations.

### Tradeoffs

- We trade the simplicity of a tiny token dictionary + runtime pseudo-elements for a larger pre-compiled CSS variable dictionary to guarantee native performance and flawless color blending accuracy.

### Operational Impact

- The CI pipeline automatically validates all custom brand contract overrides (`_achromatic-contract.scss`) using the Python linter, preventing undocumented keys from leaking into production.

### Security Impact

- Restricts custom CSS injection, forcing developers to use governed paved-road design tokens which are pre-audited for accessibility and security contrast compliance.

---

### Operational

- The domain-based taxonomy is formalized as the core design token API standard starting with `version: 1.0.0`.
- The compilation pipeline automatically maps logical dot-notation tokens to physical space-separated HSL or OKLCH custom properties to support dynamic runtime opacity modifiers (`hsl(var(--ds-...) / opacity)` or `oklch(var(--ds-...) / opacity)`).

## 7. Compliance Impact

### Related Standards

- [Documentation Governance Standard (GDC-000)](../../00-governance/GDC-000-governance-policy.md)
- [Scnehaux UI Platform Logical PAD (DOC-P002)](../../03-domain/PAD-PLT-003-scnehaux-ui-platform/PAD-PLT-003-scnehaux-ui-platform.pad.md)
- [Scnehaux UI Platform Physical SAD (SAD-003)](../../04-system/scnehaux-ui-platform/scnehaux-ui-platform.sad.md)
- SCNX Master Semantic Taxonomy (located in `packages/design-system/src/styles/docs/scnx-master-semantic-taxonomy.md` of the UI Platform Repo)
- SCNX Downstream Integration Standard (located in `packages/docs/05-standards/STD-UIP-ENG-001-developer-integration-standard.md` of the UI Platform Repo)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Legacy DOM-based Pseudo Element Overlays (`::before`/`::after` with `rgba`)

- **Pros**: Doesn't require compiling hundreds of flat CSS state variables.
- **Cons**: Introduces massive DOM bloat. Breaks React performance due to extra node rendering. Generic `rgba` black/white causes Hue shifting and muddying on wide-gamut colors, violating the Dual-Engine Photometric rule.
- **Why Rejected**: Disallowed due to poor rendering performance, layout thrashing risks, and color inaccuracy in the OKLCH P3 Gamut.

### Alternative B: Direct CSS `color-mix` for all States Globally

- **Pros**: Fully native browser-level color mixing.
- **Cons**: Doing complex runtime OKLCH math on every single interaction across thousands of DOM nodes can introduce paint lag on lower-end devices.
- **Why Rejected**: Retained strictly for Photometric Alpha utility usage, but rejected as the primary matrix compiler in favor of Ahead-Of-Time (AOT) static CSS variable generation for maximum runtime performance.

---
