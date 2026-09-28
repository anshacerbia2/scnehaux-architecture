---
doc_meta:
  id: ADR-UIP-TKN-003
  title: ADR-UIP-TKN-003 Token Taxonomy & Naming Convention
  adr_type: foundational
  status: proposed
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
  governed_by: [PAD-PLT-003]
---

# ADR-UIP-TKN-003: Adoption of a unified Design Token Taxonomy & Naming Convention across all UI platform tiers.

> **Pre-production correction candidate:** taxonomy is a naming contract, not proof of emitted bytes, accessibility, or cross-platform generators. This wording carries no authority until the UI Platform Lead records actual approval.

---

## 1. Title

Adoption of a unified Design Token Taxonomy & Naming Convention across all UI platform tiers.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                 | Approver                   |
| ---------- | -------- | ------------ | ----------------------------------------- | -------------------------- |
| 2026-09-28 | proposed | foundational | Consolidated principal review in progress | UI Platform Lead — pending |

## 3. Context

Historically, design token systems inside the Scnehaux UI Platform and downstream web applications utilized a combination of **Property-based** and **Flat Intent-based** naming conventions (e.g., `success-subtle-hover`, `bg-muted-hover`, `bg-canvas`). While requiring minimal setup initially, this flat architecture introduced critical engineering bottlenecks as the system scaled to support multi-brand and white-labeled micro-frontends:

1.  **Token Explosion**: Every new surface or widget context required unique pre-multiplied static state tokens. The token map grew quadratically, leading to high maintenance overhead and a massive bundle footprint.
2.  **Visual Flattening Trap**: A static hover state color (e.g., a solid gray) applied to different base background elements (e.g., green success cards, red alert banners, or white card panels) completely overwrote their background color. This caused elements to lose their color identity and semantic intent upon pointer interaction.
3.  **Lack of Semantic Cohesion**: Without a hierarchical, logical taxonomy, tokens were distributed as a flat list, making it impossible to perform automated contract validation, contextual inheritance, or clean overrides for third-party brands.
4.  **Multi-Platform Translation Friction**: The flat naming scheme was heavily web-centric (specifically SCSS/CSS-focused), presenting severe integration barriers when compiling tokens for native mobile applications (iOS/Android) or feeding them into token pipelines like Style Dictionary.

## 4. Decision Drivers

Adopting this combinatorial taxonomy achieves maximum semantic clarity and architectural predictability. By grouping tokens into strict Design Domains (Color, Dimension, Typography, Motion), we prevent cross-contamination of token values.

The hierarchical structure separates raw scales (Tier 1), shared semantic intent (Tier 2), and component aliases (Tier 3). A brand may change Tier-2 mappings when the relevant component styles use those mappings and the emitted theme is verified.

---

## 5. Decision

We officially adopt a unified, technology-agnostic **Design Token Taxonomy** across all three isolation tiers of the UI Platform.

### 4.1 The "Design Domain-Based" Root Principle

Tier 1 and Tier 2 use a design-domain root to prevent value-type collisions. Tier 3 starts with component ownership and carries the relevant property in its path.

1. **Color Domain**: Governs all paints, fills, and shadows.
2. **Dimension Domain**: Governs all physical layout space (spacing, sizing, radii, borders, z-index).
3. **Typography Domain**: Governs all text rendering properties.
4. **Motion Domain**: Governs all temporal transitions and physics.

The domain segment prevents mixing values such as z-index and font weight. Generated types and documentation provide autocomplete.

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

- **Color Domain**: `color.[color].[axis].[step]`
  - _Examples:_ `color.blue.light.9`, `color.neutral.dark.1A`
  - _Axis Layer:_ Required to support Dual-Axis Symmetrical Palette Generation.
  - _Step Variant:_ The `step` defines the scale grade, which consists of **Solid** steps (`1` to `12`) and **Alpha/Translucent** steps (`1A` to `12A`).
- **Dimension Domain**: `dimension.[property].[size]` (for example `dimension.spacing.4` and `dimension.radius.lg`)
- **Typography Domain**: `typography.[property].[size]` (for example `typography.font-size.16`)
- **Motion Domain**: `motion.[property].[speed]` (for example `motion.duration.fast`)

### 4.4 Tier-2: Semantic/System Tokens (The Global Intent)

Unlike Tier-1 which scales mathematically, Tier-2 assigns structural UI intent. The taxonomy format here diverges significantly depending on the family:

- **Color Domain:** `color.[scheme].[role].[emphasis].[state]`.
  - _Examples:_ `color.primary.solid.default.hover`, `color.danger.surface.subtle.default`.
- **Other Domains:** `[domain].[property].[intent]`.
  - _Dimension:_ `dimension.spacing.compact`, `dimension.radius.control`, `dimension.z.modal`
  - _Typography:_ `typography.font-size.body`, `typography.font-weight.strong`
  - _Motion:_ `motion.duration.fast`, `motion.easing.standard`

### 4.5 Tier-3: Component/Alias Tokens (Unique Overrides)

Format: `[component].[element?].[property].[state?]`.

- **Examples (`[component].[property]`)**: `card.shadow`, `dialog.z-index`
- **Examples (`[component].[property].[state]`)**: `button.surface.hover`, `input.border.focus`
- **Examples (`[component].[element].[property].[state]`)**: `checkbox.indicator.color.checked`, `switch.track.surface.disabled`

CSS output prefixes `--ds-` and converts dots to hyphens. `color.primary.solid.default.default` becomes `--ds-color-primary-solid-default-default`; `checkbox.indicator.color.checked` becomes `--ds-checkbox-indicator-color-checked`.

---

## 6. Consequences

### Positive

- **Reviewable names:** The hierarchy makes roles and token ownership easier to inspect. Emitted token count and compressed size are measured for each build.
- **Potential validation:** Structured names support compile-time checks, but checks must exist and execute in CI to establish conformance.
- **Portability target:** Mapping to Figma, CSS, Sass, or native platforms requires explicit converters and tests.

### Negative

- **AOT Build Dependency**: The CSS bundle must be fully recompiled when Lightness/Chroma shift algorithms change, rather than relying on runtime browser calculations.

### Tradeoffs

- The larger semantic dictionary adds authoring and payload cost. Its visual and runtime benefits must be verified against alternatives in representative consumers.

### Operational Impact

- Brand contract checks and emitted CSS validation are release gates to implement and run before production claims.

### Security Impact

- Token names do not restrict CSS injection or prove contrast. Security and accessibility are checked in the actual consumer context.

---

### Operational

- The domain-based taxonomy is formalized as the core design token API standard starting with `version: 1.0.0`.
- The web implementation maps logical names to CSS custom properties. Each emitted value must be valid for its consuming CSS property and supported browser.

## 7. Compliance Impact

### Related Standards

- [Documentation Governance Standard (GDC-000)](../../00-governance/GDC-000-governance-policy.md)
- [Scnehaux UI Platform PAD (PAD-PLT-003)](../../03-domain/PAD-PLT-003-scnehaux-ui-platform/PAD-PLT-003-scnehaux-ui-platform.pad.md)
- [Scnehaux UI Platform Physical SAD (SAD-003)](../../04-system/scnehaux-ui-platform/scnehaux-ui-platform.sad.md)
- SCNX Master Semantic Taxonomy (located in `packages/design-system/src/styles/docs/scnx-master-semantic-taxonomy.md` of the UI Platform Repo)
- SCNX Downstream Integration Standard (located in `packages/docs/05-standards/STD-UIP-ENG-001-developer-integration-standard.md` of the UI Platform Repo)

### Compliance Status

Taxonomy accepted; implementation conformance pending packed-package and consumer evidence.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Legacy DOM-based Pseudo Element Overlays (`::before`/`::after` with `rgba`)

- **Pros**: Doesn't require compiling hundreds of flat CSS state variables.
- **Cons**: Adds styling complexity and can produce unwanted results on varied backgrounds.
- **Why Rejected**: A semantic state contract is easier to govern for current use. No universal DOM or runtime performance claim is made.

### Alternative B: Direct CSS `color-mix` for all States Globally

- **Pros**: Fully native browser-level color mixing.
- **Cons**: Browser support, color output, and paint cost need consumer testing.
- **Why Rejected**: Precompiled variables remain the present implementation. This choice may be revisited after comparative measurement.

---
