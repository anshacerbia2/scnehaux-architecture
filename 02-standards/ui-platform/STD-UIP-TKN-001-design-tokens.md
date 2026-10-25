---
doc_meta:
  id: STD-UIP-TKN-001
  title: UI Platform Design Tokens Architecture & Pipeline
  owner: Principal Frontend Architect
  version: 2.7.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-25
  governed_by: [PAD-PLT-003]
  authorized_by: [ADR-UIP-PLT-001]
  references:
    - PAD-PLT-003
    - ADR-UIP-VIS-001
---

# UI Platform Design Tokens Architecture & Pipeline (STD-UIP-TKN-001)

> **Implementation boundary:** Sass maps are current. A DTCG 2025.10 source generating CSS, Sass, and Panda contracts remains a migration target, not an implemented guarantee.

---

## 1. Objective & Scope

This standard defines the architecture, compilation pipeline, consumption contracts, and operational governance doctrines for design tokens within the Scnehaux enterprise UI platform (`@scnx/system`).

It defines how visual properties are structured and compiled. Consistency across products depends on tested package output, supported themes, and consumer adoption.

**Authoritative Source**: This document is the normative token standard under PAD-PLT-003. ADR-UIP-TKN-003 owns the canonical taxonomy rationale.

## 2. Design Principles

The design token architecture is governed by four core principles to ensure cross-platform consistency, visual harmony, and operational scaling:

1. **Semantic Isolation**: UI components consume abstract semantic tokens (Tier 2) rather than raw value primitives (Tier 1), shielding component layouts from changes in core visual definitions.
2. **Measured Color Behavior**: OKLCH is an authoring color space; contrast depends on the actual foreground/background pair, alpha, theme, and display conversion.
3. **Interoperability Target**: DTCG 2025.10 JSON is the proposed canonical interchange format. Native-platform outputs require their own implementation and validation before they are claimed.
4. **Symmetrical Theme Paths**: Supported themes supply the same required semantic keys, while brand overrides remain scoped to a declared root and may map any Tier-2 key; the guarded floors hold in every theme and under every component hook (ADR-UIP-VIS-001 items 6 and 7).

## 3. Normative Rules

### Design Token Taxonomy

> **Taxonomy Rationale**: The rationale for the three tiers and the Scheme × Role × Emphasis × State matrix is recorded in **[ADR-UIP-TKN-003](../../05-decisions/ui-platform/ADR-UIP-TKN-003-token-taxonomy-and-naming-convention.md)**. The grammar, vocabularies, and compatibility tables below are the single normative definition; ADR-UIP-TKN-003 uses the same examples.

The platform enforces a strict **3-Tier Token Architecture**:

1. **Tier 1 (Core Primitives)**: Raw scales and values. Components and applications do not consume them directly. Sass is the current authoring implementation, not a permanent architectural requirement.
2. **Tier 2 (Global Semantic Contract)**: The public shared contract, listed per domain below.
3. **Tier 3 (Component Hooks)**: Component aliases use `{component}.{element?}.{property}.{state?}`, require independent semantic intent, and reach CSS as `--scnx-` hooks that a component references with a Tier-2 fallback (Tier-3 Alias Governance, below).

#### Canonical grammar per domain

| Domain     | Tier 1 (internal)                                                     | Tier 2 (public)                                                                   | Tier 2 example                        |
| :--------- | :-------------------------------------------------------------------- | :-------------------------------------------------------------------------------- | :------------------------------------ |
| Color      | `color.{hue}.{axis}.{step}`                                           | `color.{scheme}.{role}.{emphasis}.{state}`                                        | `color.primary.surface.solid.default` |
| Effect     | `effect.shadow.{sm\|md\|lg\|xl}`                                      | `effect.shadow.{low\|medium\|high\|overlay\|focus}`, `effect.material.{material}` | `effect.material.menu`                |
| Dimension  | `dimension.{property}.{step}`, for example `dimension.z-index.{step}` | `dimension.{property}.{intent}`                                                   | `dimension.z-index.modal`             |
| Typography | `typography.{property}.{step}`                                        | `typography.{context}.{variant}`                                                  | `typography.data.compact`             |
| Motion     | `motion.duration.{step}`, `motion.easing.{curve-id}`                  | `motion.{action}.{duration\|easing}`                                              | `motion.enter.duration`               |

Tier-1 steps are numeric or opaque identifiers; Tier-2 names carry intent. A Tier-1 name never reuses a Tier-2 intent word, so `motion.duration.fast` and `dimension.z.modal` are not valid names in either tier.

Each domain's Tier-2 vocabulary is listed below: color and effect in this section, dimension in _Dimension vocabulary_, typography in _Typography & Motion Semantic Families_, and motion in _Semantic Motion Language_. A Tier-2 name outside these vocabularies is invalid.

Tier-3 examples: `button.surface.hover`, `checkbox.indicator.color.checked`, `dialog.root.z-index.default`.

**CSS emission:** the emitted custom property is `--ds-` followed by the logical path with separators converted to hyphens. `color.primary.surface.solid.default` emits `--ds-color-primary-surface-solid-default`; `effect.shadow.low` emits `--ds-effect-shadow-low`; `dimension.z-index.modal` emits `--ds-dimension-z-index-modal`. Every emitted `--ds-*` name must parse back to a valid path in this grammar. A composite typography token emits one custom property per member, suffixed with the CSS property name: `typography.body.default` emits `--ds-typography-body-default-font-size` and the four other members listed under _Typography & Motion Semantic Families_.

#### Color vocabularies

- **Scheme:** `primary`, `neutral`, `info`, `success`, `warning`, `danger`.
- **Role:** `surface`, `border`, `text`, `icon`, `shadow`.
- **Emphasis:** `subtle`, `default`, `strong`, `solid`, `contrast`, and the neutral-only elevation values `canvas`, `sunken`, `raised`, `floating`. The usage doctrine below defines each value.
- **State:** `default` (rest), `hover`, `pressed`, `selected`, `focus`, `disabled`.

#### Role × Emphasis Compatibility

| Role    | subtle | default | strong | solid | contrast | canvas / sunken / raised / floating |
| :------ | :----: | :-----: | :----: | :---: | :------: | :---------------------------------: |
| Surface |   ✅   |   ✅    |   ✅   |  ✅   |    ❌    |         ✅ (`neutral` only)         |
| Border  |   ✅   |   ✅    |   ✅   |  ❌   |    ❌    |                 ❌                  |
| Text    |   ✅   |   ✅    |   ✅   |  ❌   |    ✅    |                 ❌                  |
| Icon    |   ✅   |   ✅    |   ✅   |  ❌   |    ✅    |                 ❌                  |
| Shadow  |   ✅   |   ✅    |   ✅   |  ❌   |    ✅    |                 ❌                  |

#### The State Compatibility Invariant

Not all roles support all states. The Sass compile-time validator (`_contract-token.scss`) enforces this table and the emphasis table above.

| Role    | Hover | Pressed | Selected | Focus | Disabled |
| :------ | :---: | :-----: | :------: | :---: | :------: |
| Surface |  ✅   |   ✅    |    ✅    |  ❌   |    ✅    |
| Border  |  ❌   |   ❌    |    ✅    |  ✅   |    ✅    |
| Text    |  ✅   |   ❌    |    ❌    |  ❌   |    ✅    |
| Icon    |  ✅   |   ❌    |    ❌    |  ❌   |    ✅    |
| Shadow  |  ✅   |   ✅    |    ❌    |  ❌   |    ❌    |

Every role supports the `default` rest state.

#### Effect contract

Every public theme emits the identical Tier-2 shadow set: `effect.shadow.low`, `effect.shadow.medium`, `effect.shadow.high`, `effect.shadow.overlay`, and `effect.shadow.focus`. Every public theme also emits the material set of ADR-UIP-VIS-001: `effect.material.flat`, `effect.material.raised`, and `effect.material.panel` (surfaces on the page) and `effect.material.tooltip`, `effect.material.menu`, `effect.material.modal`, and `effect.material.sheet` (floating surfaces). A material's layers are Tier-2 values that a theme maps. In the `industrial` theme an on-page material is a 1px ring in `color.neutral.border.subtle.default` and nothing else, and a floating material composes that ring, except `tooltip`, which has none, with contact and ambient layers whose colors are Tier-2 `color.neutral.shadow.*` tokens; in dark mode, `menu`, `modal`, and `sheet` add a 1px inset top edge in `color.neutral.border.default.default`, because shadows read weakly on dark grounds; no other layer color is allowed. A component that draws a material's fill, radius, and edge uses its material token, not a separate border and shadow. The Tier-1 sizes `sm`, `md`, `lg`, and `xl` are internal inputs and are never emitted as public names. `effect.shadow.focus` is an enhancement; the focus indicator itself is an `outline` (STD-GLB-FE-005 section 3.9).

The Sass validator rejects unsupported generated role/state combinations. Packed-output checks for grammar, key parity across themes, and value validity are release gates in STD-UIP-ENG-001.

#### Dimension vocabulary

Tier-2 dimension names are `dimension.{property}.{intent}`. The property and intent vocabularies are closed:

| Property       | Intents                                                                         | Intended use                                                                                                                                                                                                |
| :------------- | :------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `spacing`      | `inset-compact`, `inset-default`, `inset-comfortable`                           | Padding between a container's edge and its content                                                                                                                                                          |
| `spacing`      | `stack-compact`, `stack-default`, `stack-comfortable`                           | Block-axis gap between sibling elements                                                                                                                                                                     |
| `spacing`      | `inline-compact`, `inline-default`, `inline-comfortable`                        | Inline-axis gap between sibling elements                                                                                                                                                                    |
| `spacing`      | `control-compact`, `control-default`, `control-comfortable`                     | Inline padding between a control's edge and its label, value, or icon; compact, default, and comfortable pair with small, medium, and large controls                                                        |
| `spacing`      | `section`, `page`                                                               | Gap between major page regions; gutter between the viewport edge and content                                                                                                                                |
| `size`         | `control-compact`, `control-default`, `control-comfortable`                     | Block size of a small, medium, and large control (a button, a field, a tab); a component enforces the 24px target floor on it                                                                               |
| `radius`       | `mark`, `element`, `control`, `container`, `panel`, `pill`                      | Marks such as checkboxes and inline code; elements such as badges, tooltips, and small controls; controls and rows; containers such as cards, menus, and popovers; panels and dialogs; fully rounded shapes |
| `border-width` | `default`, `strong`                                                             | Dividers and outlines; emphasized indicators such as an active-item marker                                                                                                                                  |
| `z-index`      | `base`, `dropdown`, `sticky`, `overlay`, `modal`, `popover`, `tooltip`, `toast` | Stacking layers                                                                                                                                                                                             |

Values within each spacing relationship, and the `size` control relationship, ascend from `compact` to `comfortable`. `z-index` values strictly ascend in the listed order. In every theme, `radius` values are non-decreasing from `mark` to `panel`, with `pill` excluded; the `industrial` theme sets them to 0 (ADR-UIP-VIS-001 item 2), and `pill` is fully rounded for the shapes whose roundness carries meaning. Intents are single path segments; a hyphen inside an intent joins its relationship and density.

#### Guarded floors

Nothing presentational is locked: a theme may map any Tier-2 key, and a product may set a component hook on a scope. These floors hold in every theme and mode and under every hook (ADR-UIP-VIS-001 item 6). A component enforces each in its own CSS where CSS can; the token gate checks the rest per theme and mode.

1. **Target size**: the interactive box is at least 24 by 24 CSS pixels, `max(24px, …)` around its size (WCAG 2.2 SC 2.5.8).
2. **Visible focus**: a minimum outline width with `max()`; the outline's colour pair is a contrast case (SC 2.4.7, 2.4.11).
3. **Contrast**: every declared colour pair meets its minimum, per theme and mode (SC 1.4.3, 1.4.11).
4. **Reduced motion**: under `prefers-reduced-motion: reduce` a component drops movement, whatever the motion tokens say (SC 2.3.3).
5. **Shapes that carry meaning** are anatomy, not hooks: the radio indicator, the switch thumb, the status dot, and the spinner.
6. **State mechanics**: which states exist, and that disabled controls do not react.

The platform certifies the themes it ships in every mode; a product's own theme or hooks run the same gates in that product's CI. The radius order above is checked per theme.

#### Values that are not Tier-2 tokens

- **Component geometry**, such as a sidebar width, a navigation-bar height, icon and avatar sizes, and container maximum widths, is a documented structural value of its component (STD-UIP-TKN-002 section 3.1), not a token, until a theme needs to change it; it then moves to Tier 2 through the alias review. Control heights are Tier 2 (`dimension.size.control-*`), and a control's inline padding is the `control` spacing relationship.
- **Breakpoints** are not emitted as custom properties, because `var()` is not valid in a media-query condition. Responsive thresholds are build-time constants of the consuming layer.
- **Opacity** has no Tier-2 token. A translucent state is a color token whose alpha is part of its value and is verified on its actual background.
- **Transition shorthands** are not tokens. Components compose `motion.{action}.duration` and `motion.{action}.easing` with the properties they animate.

---

### Token Compilation & Delivery Pipeline

#### Centralized OKLCH Recipe Engine

The current implementation generates color values using Sass maps and a compile-time recipe engine. Mathematical transforms alone do not establish contrast or visual harmony. A future canonical token source must generate the Sass and Panda contracts from the same versioned data.

- **Primitive Isolation**: The recipe engine is the only entity authorized to access Tier-1 OKLCH coordinates.
- **Output Format**: Compiled tokens are emitted as CSS Custom Properties prefixed with `--ds-` (e.g., `--ds-color-primary-surface-solid-default`).
- **Build-Time Delivery**: Variables are distributed through documented CSS exports. Consumers import the required theme and component CSS before expecting platform styling.
- **Color and alpha calibration**: Validate generated colors and translucent overlays on their actual background. The implementation may use OKLCH or `color-mix()` where supported, but no solver or byte saving is presumed without an output test.

#### Cascading Multi-Theme & Partial Contracts Invariant

The platform supports multi-theme and multi-brand white-label capabilities under a strict cascading model:

1. **Baseline Theme**: Every public theme uses a URL-safe brand identifier and supplies required variables for each declared mode below `[data-scnx-theme="<theme-id>"][data-scnx-resolved-mode="<mode>"]`. Preference values such as `system` are resolved before selector application and are not CSS selector identities. A separate `:root` compatibility output MAY serve a single-brand document.
2. **Cascading Overrides**: Brand themes (for example `achromatic`) may override any Tier-2 key within that scoped root: colour, radius, spacing, size, type, motion, and materials. The guarded floors hold under every override (Guarded floors, above). Shadow DOM is outside v1.
3. **Partial Contract Invariant**: An override may define fewer keys than the baseline. It must document inheritance and any additional public keys. Compile-time map checks do not alone prove CSS selector isolation or valid computed values.

#### Build-Time Contract Validation

The `_contract-token.scss` validator enforces role-specific state legality at compile time:

- Schemas are declared as SASS maps (e.g., `$states-text-icon`) and passed to the `generate-scheme-matrix` mixin.
- The mixin raises a `@error` on any attempt to generate a state that is absent from the role's valid compatibility map.
- **Result**: Impossible state tokens are structurally eliminated from the output bundle, enforcing the State Compatibility Table without runtime checks.

---

### Consumption Contracts

#### Token Consumption Laws (Zero-Bypass Rule)

Shared styling follows the semantic consumption boundary. Source enforcement is a target gate until connected to CI:

- **Semantic Supremacy**: Component visual intent resolves through Tier-2 variables or justified Tier-3 aliases. Compiler values, consumer overrides, and structural literals have explicit contracts rather than an untestable blanket percentage.
- **Primitive Isolation**: Governed shared component colors use semantic tokens. Product-specific data visualization or other justified local colors require review and measured contrast, not an invented shared token.
- **Utility Styling Compliance**: Utility-class configurations must resolve styling through token-bound utility maps, not arbitrary values.

#### Semantic Usage Doctrine (Preventing Semantic Drift)

To ensure consistent design decisions across product teams, the `Emphasis` layers must obey explicit behavioral guidelines. Misusing layers (e.g., rendering body copy with `contrast` emphasis) is a semantic violation:

| Emphasis Layer                             | Intended Visual & Semantic Rationale                                                                   | Typical UX/UI Components                                                                                   |
| :----------------------------------------- | :----------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| **`subtle`**                               | Passive contextual surface or border accents representing background canvases and structural sections. | Alert banners, passive cards, table row hover, static badge fills                                          |
| **`default`**                              | Standard interactive element surfaces, outlines, and readable copy.                                    | Standard button surfaces, dividers, readable body copy, main icons                                         |
| **`strong`**                               | Elevated prominence representing active visual priority or highlighted emphasis.                       | Text-input and other control boundaries, active indicators, bold headings, high-visibility warning borders |
| **`solid`**                                | Opaque, full-chroma fill that carries the scheme's identity. Surface role only.                        | Filled primary buttons, filled badges, selected segmented-control items                                    |
| **`contrast`**                             | Text, icon, or shadow color designed to sit on a `solid` surface of the same scheme.                   | Label of a filled primary button, icon on a filled danger badge                                            |
| **`canvas`**                               | Neutral page background. Neutral surface only.                                                         | Application page background                                                                                |
| **`sunken`**, **`raised`**, **`floating`** | Neutral elevation steps below or above the canvas. Neutral surface only.                               | Inset wells; cards; popovers and menus                                                                     |

Every `contrast` token is tested against the `solid` surface of its scheme in each theme and state; every `text` and `icon` token at `subtle`, `default`, or `strong` is tested against the neutral surfaces it is declared for. The neutral `border` token at `strong` emphasis in its default state is the boundary of a control that has no other visual indicator, such as a text input, and is tested at 3:1 against every declared neutral surface in each theme and mode (WCAG 2.2 SC 1.4.11 [1]: "Where a text-input has an indicator such as a complete border […], that indicator must meet 3:1 contrast ratio" [2]). Scheme borders (`primary`, `danger`, and the others) mark states that text or another cue also carries, and are not tested for 3:1.

A color outside the sRGB gamut is tested on every display path a supported browser can take, and the lowest ratio counts. CSS Color 4 requires a color to be gamut mapped when its destination is an RGB display or a unorm8 canvas, and specifies chroma-reducing mapping [3]; Chromium 153 and Firefox 155 were measured on 2026-10-20 to clip instead (UI repository, TDD tokens G2). The paths are therefore sRGB clipped, sRGB gamut mapped, Display P3 clipped, and Display P3 gamut mapped, each composited in its own space. Relative luminance is "the relative brightness of any point in a colorspace, normalized to 0 for darkest black and 1 for lightest white" [4], taken in each path's color space. No fallback value is declared for such a color: every supported browser parses `oklch()`, which is Baseline Widely available since 2025-11-09 [5], so the browser's own gamut handling is the fallback, and the paths above test it.

#### Domain Semantic Layer (Logical Intent Mapping)

To prevent global color roles from colliding with domain-specific logic in complex systems (HRIS, ERP, Finance), portals must implement a thin logical mapping layer on top of the global color schemes:

```
[Domain State Layer] ──▶ [Global Semantic Layer] ──▶ [Core Primitives]
(e.g., state.fraud)       (color.danger.surface.solid.default)      (0.55 0.24 25 oklch)
```

Portals declare semantic logical aliases that internally map directly to scheme tokens, preventing business domain requirements from leaking into and corrupting the core global matrix:

- `state.approved` → `color.success.surface.solid.default`
- `state.pending` → `color.warning.surface.subtle.default`
- `state.fraud` → `color.danger.surface.solid.default`
- `state.archived` → `color.neutral.surface.strong.default`

---

### Typography & Motion Semantic Families

#### Semantic Reading Density (Typography)

Typography tokens must be grouped by **semantic reading layout**, not by linear sequential text scaling. This prevents teams from scaling fonts arbitrarily across dense dashboards and article-style portals:

| Group       | Tokens                                                                      | Intended Reading Context                                             |
| :---------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| **Body**    | `typography.body.large`, `typography.body.default`, `typography.body.small` | Running text in components and pages                                 |
| **Label**   | `typography.label.default`, `typography.label.small`                        | Control labels, captions, and metadata                               |
| **Heading** | `typography.heading.{xxlarge\|xlarge\|large\|medium\|small\|xsmall}`        | Titles; the size is independent of the heading element's level       |
| **Code**    | `typography.code.default`, `typography.code.small`                          | Inline and block code                                                |
| **Data**    | `typography.data.compact`                                                   | High-density data-grids, tabular controls, dense dashboard summaries |
| **Article** | `typography.article.readable`                                               | Sustained reading of text-heavy prose, articles, documentation       |
| **Metric**  | `typography.metric.display`                                                 | Standalone numeric KPIs, scores, and display indicators              |

Each token above is a composite with exactly five members: `font-family`, `font-size`, `font-weight`, `line-height`, and `letter-spacing`. Every theme defines all five for every composite. Heading sizes descend from `xxlarge` to `xsmall` in every theme.

A component that varies only the weight of a composite uses `typography.weight.{regular|medium|semibold|bold}`. This family is the one single-member typography family; each token is a font weight, and the four values ascend in the listed order.

#### Semantic Motion Language

Timing durations and mathematical easing curves must map to high-level communicative actions, not arbitrary numeric values:

Each action emits a `duration` and an `easing` token, for example `motion.enter.duration` and `motion.enter.easing`.

| Motion Action       | Communicative Action                                                                                   |
| :------------------ | :----------------------------------------------------------------------------------------------------- |
| `motion.enter`      | Mounting actions such as a drawer sliding in or a dropdown opening; content decelerates into place     |
| `motion.exit`       | Dismissed or unmounted content; it accelerates away and takes no longer than the matching enter        |
| `motion.attention`  | Scale or opacity emphasis on a critical action without moving surrounding layout                       |
| `motion.disclosure` | Height expand/collapse for accordions, menus, and detail triggers                                      |
| `motion.feedback`   | State feedback on the same element, such as hover, press, focus, and selection color or shadow changes |

`motion.enter.easing` is a decelerating curve and `motion.exit.easing` an accelerating one. `motion.exit.duration` does not exceed `motion.enter.duration`, and `motion.feedback.duration` is the shortest of the five durations.

**Performance Constraint**: Dynamic-height motion may involve layout. Reduced-motion behavior and interaction traces determine whether a transition is acceptable. Claims about forced layout and frame rate require named scenarios and measurements.

---

### Tier-3 Alias Governance

#### Component Alias Review

To prevent unbounded aliases, the platform reviews their semantics and reuse:

- **Alias review**: Record the component purpose, Tier-2 fallback, theme/state coverage, and migration impact. A numerical cap and an ADR for each alias are not required.
- **Listed in the specification**: every hook a component reads appears in its `*.spec.json`, with its Tier-2 fallback and the floors that bound it. A hook is public API; renaming or removing one is a breaking change.

#### Hook mechanics

- **Prefix**: Tier 3 is `--scnx-{component}-{part?}-{property}`, the component namespace of the `.scnx-*` classes and `data-scnx-*` attributes. Tier 2 stays `--ds-*`. Tier 1 is a compiler input and is never emitted (ADR-GLB-FE-010).
- **Referenced with a fallback, never declared**: a component reads `var(--scnx-button-radius, var(--ds-dimension-radius-control))`; the package emits no Tier-3 declaration, so a hook costs nothing until a product sets it.
- **Never registered**: a hook is never registered with `@property`, because a registered property always has a value and its Tier-2 fallback would never apply.
- **Set on a scope**: a product sets a hook on the element or region it changes, not on `:root`, when the value changes at runtime.
- **No literal design value**: a styled component's stylesheet holds no literal design value outside the hook-and-fallback pattern; the source gate fails one that does.

#### Alias Naming Convention

All Tier-3 logical aliases follow:

```
{component}.{element?}.{property}.{state?}
```

Examples:

- `button.radius` → `var(--scnx-button-radius, var(--ds-dimension-radius-control))`
- `button.surface.hover` → `--scnx-button-surface-hover`
- `checkbox.indicator.color.checked` → `--scnx-checkbox-indicator-color-checked`
- `input.root.border.focus` → `--scnx-input-root-border-focus`

---

## 4. Exceptions

Deviations identify the affected consumer contract, rationale, owner, and migration path under enterprise governance.

## 5. Enforcement Mechanism

### 5.7.1 Static AST Verification (Zero-Bypass Enforcement)

Target source checks parse component styling and report bypasses:

- **Blocking Rule**: Governed shared styles with unjustified raw color literals fail the source gate when the rule is implemented.
- **Z-Index Enforcement**: Elements requiring z-index properties must reference a Tier-2 or Tier-3 z-index token (e.g., `var(--ds-dimension-z-index-modal)` or `var(--scnx-dialog-z-index, var(--ds-dimension-z-index-modal))`). Hardcoded z-index integers are prohibited.
- **Grammar Gate**: A packed-output check parses every emitted `--ds-*` name against the canonical grammar and fails on any name that does not map to a valid path, including legacy names such as `--ds-color-primary-solid-default-default` or `--ds-shadow-lg`.
- **Theme Parity Gate**: The same check fails when two public themes emit different Tier-2 key sets.

### 5.7.2 Build Contract Validation

The SASS compile pipeline (`pnpm --filter "@scnx/system" build`) is the primary mechanical enforcement gate:

- `@error` directives in `_contract-token.scss` block compilation if any token attempt violates the State Compatibility Table.
- Any build failure from this gate is treated as a `CRITICAL` schema violation requiring an immediate fix before the PR can merge.
- Packed stylesheets are checked for missing required variables, valid resolved values in consuming properties (including shadows and font families), and declared foreground/background contrast pairs in each supported theme and state.
- Until generation and checks are connected to CI, documentation must not claim that palette generation is contrast-guaranteed or fail-closed.

### 5.7.3 Waiver Protocol

Formal exceptions follow GDC-010 and the applicable standard-governance process. Routine justified Tier-3 aliases are reviewed as token-contract changes, not treated as automatic waivers.

## 6. References

Retrieved 2026-10-20.

1. W3C, WCAG 2.2, Success Criterion 1.4.11 Non-text Contrast: <https://www.w3.org/TR/WCAG22/>. "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s): User Interface Components Visual information required to identify user interface components and states".
2. W3C WAI, Understanding SC 1.4.11 Non-text Contrast: <https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html>. "Where a text-input has an indicator such as a complete border ( #767676 ), that indicator must meet 3:1 contrast ratio"; for adjacent colours, "if an input has a white internal background, dark border, and white external background the 'adjacent color' to the component would be the white external background".
3. W3C, CSS Color Module Level 4, "Gamut Mapping" and "CSS Gamut Mapping to an RGB Destination", at csswg-drafts commit `160a00acff045d99796606f502812c9462e110e2`: <https://github.com/w3c/csswg-drafts/blob/160a00acff045d99796606f502812c9462e110e2/css-color-4/Overview.bs>. "if the destination is the display device (a screen, or a printer) then out of gamut values must be converted to an in-gamut color"; the CSS gamut mapping algorithms apply to colors out of gamut of "an RGB display" or "a canvas, with unorm8 backing store", and "Gamut mapping will produce a similar, but lower chroma, color"; on clipping, "clipping is commonly done on gamma-encoded values".
4. W3C, WCAG 2.2, definition "relative luminance", at w3c/wcag commit `457cece22d8219be32d29c5c1313e71aa6b61eae`: <https://github.com/w3c/wcag/blob/457cece22d8219be32d29c5c1313e71aa6b61eae/guidelines/terms/20/relative-luminance.html>. "the relative brightness of any point in a colorspace, normalized to 0 for darkest black and 1 for lightest white"; "Unless it is known that another color space will be used to process and display the content, authors should evaluate using sRGB colorspace."
5. web-features 3.43.0 (W3C WebDX Community Group), feature `oklab` "Oklab and OkLCh", at tag commit `3c7e5ff9ed136e4fcf76b4ee54fdffab7c31ab69`: <https://github.com/web-platform-dx/web-features/tree/3c7e5ff9ed136e4fcf76b4ee54fdffab7c31ab69>. Status `baseline: "high"`, `baseline_low_date` 2023-05-09, `baseline_high_date` 2025-11-09, covering `css.types.color.oklch`.
