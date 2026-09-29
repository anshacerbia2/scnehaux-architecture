---
doc_meta:
  id: ADR-UIP-TKN-003
  title: ADR-UIP-TKN-003 Token Taxonomy & Naming Convention
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
  governed_by: [PAD-PLT-003]
---

# ADR-UIP-TKN-003: Adoption of a unified Design Token Taxonomy & Naming Convention across all UI platform tiers.

> **Implementation boundary:** the accepted naming contract is not proof of emitted bytes, accessibility, or cross-platform generators.

---

## 1. Title

Adoption of a unified Design Token Taxonomy & Naming Convention across all UI platform tiers.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                   | Approver                        |
| ---------- | -------- | ------------ | --------------------------- | ------------------------------- |
| 2026-09-29 | accepted | foundational | Principal 1 and Principal 2 | Ansha Cerbia (UI Platform Lead) |

## 3. Context

Historically, design token systems inside the Scnehaux UI Platform and downstream web applications utilized a combination of **Property-based** and **Flat Intent-based** naming conventions (e.g., `success-subtle-hover`, `bg-muted-hover`, `bg-canvas`). While requiring minimal setup initially, this flat architecture introduced critical engineering bottlenecks as the system scaled to support multi-brand and white-labeled micro-frontends:

1.  **Token Explosion**: Every new surface or widget context required unique pre-multiplied static state tokens. The token map grew quadratically, leading to high maintenance overhead and a massive bundle footprint.
2.  **Visual Flattening Trap**: A static hover state color (e.g., a solid gray) applied to different base background elements (e.g., green success cards, red alert banners, or white card panels) completely overwrote their background color. This caused elements to lose their color identity and semantic intent upon pointer interaction.
3.  **Lack of Semantic Cohesion**: Without a hierarchical, logical taxonomy, tokens were distributed as a flat list, making it impossible to perform automated contract validation, contextual inheritance, or clean overrides for third-party brands.
4.  **Multi-Platform Translation Friction**: The flat naming scheme was heavily web-centric (specifically SCSS/CSS-focused), presenting severe integration barriers when compiling tokens for native mobile applications (iOS/Android) or feeding them into token pipelines like Style Dictionary.

## 4. Decision Drivers

The combinatorial taxonomy makes each token's domain, intent, and state readable from its name. Grouping tokens into design domains (Color, Effect, Dimension, Typography, Motion) prevents values of different types from sharing a name.

The hierarchical structure separates raw scales (Tier 1), shared semantic intent (Tier 2), and component aliases (Tier 3). A brand may change Tier-2 mappings when the relevant component styles use those mappings and the emitted theme is verified.

---

## 5. Decision

We officially adopt a unified, technology-agnostic **Design Token Taxonomy** across all three isolation tiers of the UI Platform.

### 4.1 The "Design Domain-Based" Root Principle

Tier 1 and Tier 2 use a design-domain root to prevent value-type collisions. Tier 3 starts with component ownership and carries the relevant property in its path.

1. **Color Domain**: Governs paints and fills, including the color of shadows.
2. **Effect Domain**: Governs composite visual effects, currently shadows.
3. **Dimension Domain**: Governs physical layout space (spacing, sizing, radii, borders, z-index).
4. **Typography Domain**: Governs text rendering properties.
5. **Motion Domain**: Governs durations and easing.

The domain segment prevents mixing values such as z-index and font weight. Generated types and documentation provide autocomplete.

### 4.2 Naming Vocabulary

The normative vocabularies (schemes, roles, emphasis values including `solid` and the neutral elevation values, states) and the Role × Emphasis and Role × State compatibility tables are defined once in [STD-UIP-TKN-001](../../02-standards/ui-platform/STD-UIP-TKN-001-design-tokens.md). This record keeps only the rationale and the examples below, which match that standard.

- **`[hue]`**: The Tier-1 hue family (e.g., `blue`, `neutral`).
- **`[axis]`**: The lighting context (`light` or `dark`) used for symmetrical palette generation. See [ADR-UIP-TKN-002](ADR-UIP-TKN-002-oklch-and-dual-engine-alpha.md).
- **`[step]`**: A Tier-1 scale grade. Color uses `1-12` for solid and `1A-12A` for alpha; other domains use numeric or opaque steps that never reuse Tier-2 intent words.

### 4.3 Tier-1: Core/Primitive Tokens (The Raw Scales)

- **Color**: `color.[hue].[axis].[step]`, e.g. `color.blue.light.9`, `color.neutral.dark.1A`.
- **Effect**: `effect.shadow.[sm|md|lg|xl]`. These sizes are internal and never emitted as public names.
- **Dimension**: `dimension.[property].[step]`, e.g. `dimension.spacing.4`, `dimension.z-index.400`.
- **Typography**: `typography.[property].[step]`, e.g. `typography.font-size.16`.
- **Motion**: `motion.duration.[step]` and `motion.easing.[curve-id]`, e.g. `motion.duration.200`.

### 4.4 Tier-2: Semantic/System Tokens (The Global Intent)

- **Color**: `color.[scheme].[role].[emphasis].[state]`, e.g. `color.primary.surface.solid.default`, `color.danger.surface.subtle.default`, `color.primary.text.contrast.default`.
- **Effect**: `effect.shadow.[low|medium|high|overlay|focus]`. Every public theme emits this identical set.
- **Dimension**: `dimension.[property].[intent]`, e.g. `dimension.spacing.compact`, `dimension.z-index.modal`.
- **Typography**: `typography.[context].[variant]`, e.g. `typography.data.compact`.
- **Motion**: `motion.[action].[duration|easing]`, e.g. `motion.enter.duration`.

### 4.5 Tier-3: Component/Alias Tokens (Unique Overrides)

Format: `[component].[element?].[property].[state?]`.

- `button.surface.hover`
- `input.root.border.focus`
- `checkbox.indicator.color.checked`
- `dialog.root.z-index.default`

CSS output prefixes `--ds-` and converts dots to hyphens. `color.primary.surface.solid.default` becomes `--ds-color-primary-surface-solid-default`, `effect.shadow.low` becomes `--ds-effect-shadow-low`, and `dialog.root.z-index.default` becomes `--ds-dialog-root-z-index-default`.

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
- [UI Platform Token Standard (STD-UIP-TKN-001)](../../02-standards/ui-platform/STD-UIP-TKN-001-design-tokens.md)
- TDD-ui-platform-tokens-003 (theme and token output) in the UI Platform repository

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
