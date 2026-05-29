---
doc_meta:
  id: DOC-P002
  title: Scnehaux UI Platform Architecture
  owner: Principal UI/UX Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-18
  fulfilled_by:
    - DOC-S003
---

# Scnehaux UI Platform Architecture (PAD-002)

---

## 1. Platform Capability

The **Scnehaux UI Platform** (`@scnx/system` & `@scnx/core-ui`) is the authoritative **Visual Root of Trust** and shared presentation foundation for all Scnehaux applications. It enforces absolute visual consistency, strict structural styling isolation, and robust accessible interaction semantics across both standalone applications and federated micro-frontends.

The platform delivers a unified **3-Layer Visual Engine**:
1.  **Layer 1: Primitive Components (Accessible Headless Core)**: Pure, style-agnostic, and polymorphic headless elements (with built-in WCAG 2.2 AA compliance, keyboard focus-trapping, and ARIA handling) completely decoupled from physical visual styles to serve as the logical layout skeleton.
2.  **Layer 2: Design Tokens (The Design API)**: A platform-agnostic, multi-family token taxonomy structured as a 3-tier engine:
    *   **Tier-1: Core Primitives (Raw Values)**: Platform-agnostic raw constants without semantic meaning, organized as precise mathematical scales:
        *   **Neutral Colors**: 12 solid grades (0 to 1100) and 10 translucent alpha grades (100A to 1000A) across Light/Dark axes, defined as HSL space-separated coordinates to support dynamic runtime opacity modifications.
        *   **Chromatic Colors**: 9 color scales (red, orange, yellow, lime, green, teal, blue, purple, magenta), each comprising 10 solid (100 to 1000) and 10 alpha grades (100A to 1000A) across Light/Dark axes, defined as HSL or OKLCH space-separated coordinates.
        *   **Spacing & Sizing**: 13 grid spacing steps (0 to 20 / 5rem) and 12 element sizing steps (0.625rem to 4.5rem).
        *   **Border & Stroke**: 7 radius curves (none to full) and 5 border thickness steps (0 to 4px).
        *   **Effects & Elevation**: 9 opacity values (0% to 100%) and 5 elevation depth shadows (sm to xl, and inner shadow).
        *   **Z-Index & Motion**: 7 stacking indices (0 to 1060), 4 transition durations (150ms to 400ms), and 4 easing curves (standard, in, out, sharp).
        *   **Typography Families & Scales**: 2 font families (sans/mono), 12 font-size steps ('2xs' to '7xl'), 6 font weights, 3 line heights, and 4 letter-spacing values.
        *   **Layout & Responsive Grid**: 6 responsive viewport breakpoints (480px to 1536px) and 4 semantic container max-width caps (prose to fluid).
    *   **Tier-2: Global Semantics (The Core Taxonomy)**: Standardized single source of truth mapping primitives to visual intent under a strict flat key notation, encompassing Color, Dimension, Typography, and Motion families.
    *   **Tier-3: Component Aliases (Unique Overrides)**: Isolated overrides reserved strictly for component-unique behavior where independent styling divergence is structurally justified, preventing global semantic pollution.
3.  **Layer 3: Styled Engine (Zero-Runtime Compiler)**: A static compilation engine that marries the Headless Primitives (Layer 1) with the Design Tokens (Layer 2) using build-time CSS compilation and static styling orchestration with zero runtime execution overhead.

### 1.1 Fulfilling Systems

This platform capability is physically fulfilled by the following systems:
-   **Scnehaux UI Platform Software Architecture**: Managed under the physical package registry defined in [scnehaux-ui-platform.sad.md](../../03-applications/scnehaux-ui-platform/scnehaux-ui-platform.sad.md) (DOC-S003).
-   **IAM Dashboard (Standalone SPA)**: Housed under `scnehaux-iam-dashboard` which directly integrates and consumes the semantic token suite as a standalone portal ([scnehaux-iam-dashboard.sad.md](../../03-applications/scnehaux-iam-dashboard/scnehaux-iam-dashboard.sad.md)).
-   **ERP Portal (Federated Host)**: The host shell orchestrating HRIS and Finance micro-frontends sharing `@scnx/system` styles.

---

## 2. Trust Boundary & Security

Visual styling and layout architectures represent critical application boundaries. The platform enforces the following security and isolation policies:

-   **Zero Layout Contamination**: All layout frameworks must use strict CSS encapsulation. Component selectors are isolated using CSS Modules or unique domain-specific namespace prefixes (e.g., `scnx-hris-`, `scnx-fin-`) to prevent side-effects, reserving the core `scnx-` prefix exclusively for the shared Scnehaux UI Platform core styles and visual tokens.
-   **CSP (Content Security Policy) Compliance**: The platform prohibits injecting inline `<style>` blocks at runtime. All styles must compile to static, hash-verified external CSS files, mitigating cross-site scripting (XSS) via styling injection.
-   **Anti-Flicker Transitions**: Active page overlays, modal animations, and skeletons must execute with frame sanitization (preventing RequestAnimationFrame queue stacking) to eliminate layout thrashing and rendering flickering.
-   **Data-Driven Aesthetics Protection**: Color contrasts must adhere strictly to **WCAG 2.2 AA** rules, guaranteeing a minimum contrast ratio of 4.5:1 for standard text and 3:1 for large graphical components under both light and dark modes.

---

## 3. Integration Contract

Downstream applications and component systems (e.g., `scnehaux-iam-dashboard`, `core-ui`) must consume the design token platform following this strict contract.

### 3.1 Token Mapping and Developer Convenience
The platform maps structural design tokens to standard flat CSS Custom Properties (prefixed with `--ds-color-` and `--ds-spacing-`) and mirrors them as strongly-typed SCSS variables at compile-time to provide an excellent developer experience and eliminate manual string errors.
*   Conceptual Surface Canvas $\rightarrow$ `--ds-color-neutral-canvas-default` / `$color-neutral-canvas-default`
*   Conceptual Primary Hover $\rightarrow$ `--ds-color-primary-surface-hover` / `$color-primary-surface-hover`
*   Conceptual Success Border $\rightarrow$ `--ds-color-success-border-default` / `$color-success-border-default`

### 3.2 The Master Semantic Taxonomy

The platform standardizes on a platform-agnostic, hierarchical design token taxonomy. Below is the exhaustive reference mapping of the SCNX Master Semantic Taxonomy as defined in the core token specification:

#### 3.2.1 Architectural Principle
All tokens are modeled in a strict 3-tier system:
1. **Tier-1: Primitive (Raw Values)**: Platform-agnostic raw constants without semantic meaning (e.g., base color scales, fixed spacing increments).
2. **Tier-2: Semantic (Global Meaning)**: The single source of truth mapping primitives to structural UI intents using standard platform-agnostic names.
3. **Tier-3: Component Aliases (Unique Overrides)**: Optional overrides reserved strictly for component-unique behavior where independent styling divergence is structurally justified.

#### 3.2.2 Master Semantic Families
The taxonomy covers the following token families across four major domains represented in a structured platform matrix:

| Taxonomy Domain | Core Token Families / Members | Primary Architectural Purpose |
| :--- | :--- | :--- |
| **Color (Super-Scheme)** | `neutral` | Structural layout elevations (canvas, surface-raised, surface-floating, surface-sunken) and interaction schemes. |
| **Color (Shared Schemes)** | `primary`, `secondary`, `accent`, `info`, `success`, `warning`, `danger` | High-performance, symmetrical interactive color schemes governed by core anchors and recipes. |
| **Color (Global Helpers)** | `overlay`, `utility`, `chart` | Non-scheme helpers for scrim layers, frosted-glass filters, skeleton loaders, and data-viz. |
| **Dimensions** | `spacing`, `size`, `radius`, `stroke`, `opacity`, `z`, `shadow` | Layout grid steps, element dimensions, corners, outline strokes, opacities, and z-elevations. |
| **Typography** | `font-family`, `font-size`, `font-weight`, `line-height`, `letter-spacing` | Highly readable font families, type sizes, densities, tracking, and leading curves. |
| **Motion** | `duration`, `easing`, `transition`, `animation` | Physics easing curves, duration speeds, and action transitions for GPU-accelerated layers. |


#### 3.2.3 Full Color Semantic Taxonomy

The color platform implements a unified **Orthogonal Symmetrical Color Matrix** designed using **OKLCH Build-Time Generation**. The system completely decouples visual identity from elements, role-specific variants, and interaction states.

##### 1. The Four Orthogonal Layers
Every semantic color token in the system is structured as a composition of four independent design dimensions:

$$\text{[Scheme]} \longrightarrow \text{[Role]} \longrightarrow \text{[Emphasis]} \longrightarrow \text{[State]}$$

| Layer | Primary Architectural Purpose | Token Members / Range |
| :--- | :--- | :--- |
| **1. Scheme** | Color Identity & Semantic Domain | `neutral` (Super-Scheme), `primary`, `secondary`, `accent`, `info`, `success`, `warning`, `danger` (Symmetrical) |
| **2. Role** | Core Visual Function / UI Element Target | `surface` (low contrast fill), `solid` (high contrast fill), `border` (outlines), `text` (typography), `icon` (vector glyphs), `shadow` (depth shadow) |
| **3. Emphasis** | Visual Prominence & Contrast Hierarchy | `subtle` (very low prominence), `default` (normal prominence), `strong` (elevated prominence), `contrast` (maximum readability contrast) |
| **4. State** | Active Pointer Interaction Lifecycle | `default` (resting state), `hover` (pointer hover), `pressed` (active press), `selected` (selected state), `focus` (keyboard focus), `disabled` (disabled state) |

To maintain clean hierarchy and layout depth, the platform enforces a strict visual boundary between low-contrast resting containers and high-prominence action targets:

*   **`surface` (Container Backgrounds)**: Dedicated to low-contrast layout surfaces including page backdrops, cards, panel containers, table rows, and alert/badge backgrounds.
*   **`solid` (Action & Accent Fills)**: Reserved for high-contrast interactive fills including filled buttons, call-to-action triggers, active tab selections, and highlighted status indicators.

##### 2. Token Composition Recipes
Developers consume resolved semantic tokens built at compile-time using the following compositional blueprints:

| Target Component | Semantic Layer Composition Blueprint | Conceptual Resolved Property |
| :--- | :--- | :--- |
| **Danger Subtle Alert** | `danger.surface.subtle.default` <br> `danger.border.default.default` <br> `danger.text.default.default` | Tinted background plane <br> Standard accent border <br> Default readable warning text |
| **Danger Solid Button** | `danger.solid.default.default` <br> `danger.text.contrast.default` | High-contrast solid button background <br> Crisp on-color contrast text |
| **Danger Solid Button Hover** | `danger.solid.default.hover` <br> `danger.text.contrast.default` | Lightness-adjusted solid hover fill <br> Stable on-color contrast text |
| **Danger Selected Row** | `danger.surface.subtle.selected` | Chroma-boosted active selection background |
| **Danger Focus Ring** | `danger.border.default.focus` | Accessibility keyboard focus ring outline |
##### 3. Symmetrical Resolution Mechanics & Combinatorial Math

The marriage of **Scheme $\longrightarrow$ Role $\longrightarrow$ Emphasis $\longrightarrow$ State** resolves at compile-time to yield flat, fully pre-calculated CSS custom properties. This combinatorial space is governed by strict mathematical anchors and transformation modifiers to ensure complete predictability and top-tier visual balance.

###### A. The Combinatorial Space & Payload Optimization
To optimize compile-time performance and prevent visual bloat, the platform enforces a strict **State Compatibility Matrix**. Instead of a generic Cartesian explosion, roles resolve only to their valid physical and interactive states, reducing the compilation space from $1348$ to exactly **$740$ pre-resolved tokens**:

*   **Background Fills (`surface`, `solid`)**: 8 Schemes $\times$ 2 Roles $\times$ 4 Emphases $\times$ 5 States (`default`, `hover`, `pressed`, `selected`, `disabled`) = $320$ pre-resolved tokens.
*   **Typography & Graphics (`text`, `icon`)**: 8 Schemes $\times$ 2 Roles $\times$ 4 Emphases $\times$ 3 States (`default`, `hover`, `disabled`) = $192$ pre-resolved tokens.
*   **Contour Outlines (`border`)**: 8 Schemes $\times$ 1 Role $\times$ 4 Emphases $\times$ 4 States (`default`, `selected`, `focus`, `disabled`) = $128$ pre-resolved tokens.
*   **Depth Simulation (`shadow`)**: 8 Schemes $\times$ 1 Role $\times$ 4 Emphases $\times$ 3 States (`default`, `hover`, `pressed`) = $96$ pre-resolved tokens.
*   **Layout Elevation System (`canvas`, `surface-raised`, `surface-floating`, `surface-sunken`)**: 1 Neutral Scheme $\times$ 4 Roles $\times$ 1 Emphasis $\times$ 1 State = $4$ pre-resolved tokens.
*   **Total Color Surface Space**: **$740$** pre-compiled flat custom properties (e.g., `--ds-color-primary-solid-default-hover`).

###### B. State Compatibility Matrix
The following architectural support matrix governs the compilation phase, establishing the exact combinations of `[Scheme] ⟶ [Role] ⟶ [Emphasis] ⟶ [State]`:

| Role | Default (Resting) | Hover | Pressed | Selected | Focus | Disabled |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`surface`** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **`solid`** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **`border`** | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **`text`** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **`icon`** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **`shadow`** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

###### C. Lightness and Chroma Shift Recipes
Baseline coordinates are established at the `default` emphasis of each Role. When combined with other dimensions, the compilation compiler applies precise mathematical transformations:

1. **Lightness Shifts ($\Delta L$) for Interactive States**:
   *   **`hover`**: Adjusts baseline lightness $L$ to enhance contrast on pointer contact. In Light Mode, lightness is reduced by $-0.04$ ($L_{\text{state}} = L_{\text{emp}} - 0.04$). In Dark Mode, lightness is increased by $+0.04$ ($L_{\text{state}} = L_{\text{emp}} + 0.04$).
   *   **`pressed`**: Deepens the hover transition for a tactile responsive press. In Light Mode, lightness is reduced by $-0.08$ ($L_{\text{state}} = L_{\text{emp}} - 0.08$). In Dark Mode, lightness is increased by $+0.08$ ($L_{\text{state}} = L_{\text{emp}} + 0.08$).
   *   **`disabled`**: Strips visual prominence to signify inactivity. Lightness is locked to exactly `0.90` (Light Mode) or `0.20` (Dark Mode), and Chroma is compressed to `20%` of its baseline value ($C_{\text{state}} = C_{\text{emp}} \times 0.2$).

2. **Chroma Shifts ($\Delta C$) for Selection Locking**:
   *   **`selected`**: Boosts saturation to locked elements (e.g., active tabs, selected table rows) without altering depth. Chroma is increased by $+0.03$ ($C_{\text{state}} = C_{\text{emp}} + 0.03$).

3. **Asymmetric State Mapping Invariants**:
   *   **Elevation Shadows (`shadow`)**: Compiles exclusively for `default`, `hover`, and `pressed` states, tracking physical viewport depth elevations as elements lift on hover or sink on click. Focus or selected states do not affect structural shadows.
   *   **Focus Ring Outlines (`border` focus)**: Keyboard focus ring styling resolves as the `focus` state of the `border` role (yielding translucent focus outlines mapped to `--ds-color-{scheme}-border-default-focus` dynamically). Focus states do not generate focus indicators on other element roles.

4. **Contrast Safeguard Rule for On-Color Text (`contrast` emphasis)**:
   *   To guarantee compliance with WCAG 2.2 AA contrast rules on filled interactive elements (like primary or success buttons), the compiler implements dynamic contrast overrides.
   *   If the target background (`solid`) is highly light-reflective (e.g. `warning` or `neutral` in dark mode), the overlay `text.contrast` or `icon.contrast` lightness is forced to a deep $L = 0.10$ coordinate (providing outstanding >`8:1` readability).
   *   If the target background is deep or chromatic (e.g. `primary`, `success`, `danger`), the overlay text/icon lightness is set to $L = 0.99$, ensuring standard white contrast text.

5. **OKLCH Dual-Axis Palette Calibration**:
   *   **Lightness Axis (Light / Dark Themes)**: OKLCH Lightness ($L \in [0.0, 1.0]$) is perceptually uniform. This allows theme transitions to maintain identical relative contrast values along the lightness curves, preventing the dark mode from becoming either washed out or oversaturated.
   *   **Transparency/Alpha Axis**: Instead of compiling hundreds of static transparent custom properties (like the legacy `--ds-palette-neutral-100A` from v1.0), SCNX v2.0 utilizes runtime browser-level blending via `color-mix()` in the OKLCH interpolation space (e.g., `color-mix(in oklch, var(--ds-color-...) X%, transparent)`). The mathematical dual-axis solver is executed at compile-time solely to calibrate the precise overlay percentage ($X\%$), reducing the compiled CSS payload and maintaining the visual root of trust.

##### 4. The Symmetrical Shared Matrix
For all **Shared Color Schemes** (`primary`, `secondary`, `accent`, `info`,
`success`, `warning`, `danger`), the platform enforces a strict, fully
symmetrical matrix. Every Scheme $\times$ Role $\times$ Emphasis $\times$
State combination is compiled to its own pre-calculated OKLCH Custom Property,
maintaining complete predictability across all visual anchors.

The full structural tree (identical per scheme, applied to all 7) is:

```
Shared Scheme Structure  (× 7: primary, secondary, accent, info, success, warning, danger)
├── surface
│   ├── subtle
│   │   ├── default
│   │   ├── hover
│   │   ├── pressed
│   │   ├── selected
│   │   └── disabled
│   ├── default
│   │   ├── default
│   │   ├── hover
│   │   ├── pressed
│   │   ├── selected
│   │   └── disabled
│   ├── strong
│   │   ├── default
│   │   ├── hover
│   │   ├── pressed
│   │   ├── selected
│   │   └── disabled
│   └── contrast
│       ├── default
│       ├── hover
│       ├── pressed
│       ├── selected
│       └── disabled
├── solid
│   ├── subtle
│   │   ├── default
│   │   ├── hover
│   │   ├── pressed
│   │   ├── selected
│   │   └── disabled
│   ├── default
│   │   ├── default
│   │   ├── hover
│   │   ├── pressed
│   │   ├── selected
│   │   └── disabled
│   ├── strong
│   │   ├── default
│   │   ├── hover
│   │   ├── pressed
│   │   ├── selected
│   │   └── disabled
│   └── contrast
│       ├── default
│       ├── hover
│       ├── pressed
│       ├── selected
│       └── disabled
├── border
│   ├── subtle
│   │   ├── default
│   │   ├── selected
│   │   ├── focus
│   │   └── disabled
│   ├── default
│   │   ├── default
│   │   ├── selected
│   │   ├── focus
│   │   └── disabled
│   ├── strong
│   │   ├── default
│   │   ├── selected
│   │   ├── focus
│   │   └── disabled
│   └── contrast
│       ├── default
│       ├── selected
│       ├── focus
│       └── disabled
├── text
│   ├── subtle
│   │   ├── default
│   │   ├── hover
│   │   └── disabled
│   ├── default
│   │   ├── default
│   │   ├── hover
│   │   └── disabled
│   ├── strong
│   │   ├── default
│   │   ├── hover
│   │   └── disabled
│   └── contrast
│       ├── default
│       ├── hover
│       └── disabled
├── icon
│   ├── subtle
│   │   ├── default
│   │   ├── hover
│   │   └── disabled
│   ├── default
│   │   ├── default
│   │   ├── hover
│   │   └── disabled
│   ├── strong
│   │   ├── default
│   │   ├── hover
│   │   └── disabled
│   └── contrast
│       ├── default
│       ├── hover
│       └── disabled
└── shadow
    ├── subtle
    │   ├── default
    │   ├── hover
    │   └── pressed
    ├── default
    │   ├── default
    │   ├── hover
    │   └── pressed
    ├── strong
    │   ├── default
    │   ├── hover
    │   └── pressed
    └── contrast
        ├── default
        ├── hover
        └── pressed
```

Per scheme token payload: **surface** (4 × 5) + **solid** (4 × 5) + **border**
(4 × 4) + **text** (4 × 3) + **icon** (4 × 3) + **shadow** (4 × 3) = **92**
tokens × 7 schemes = **644** tokens (plus 96 neutral interactive tokens + 4
elevation tokens = **744** total — aligned with the math in §3.2.3A).

##### 5. The Neutral Super-Scheme Elevation System
To prevent architectural collisions between page depth elevations and interactive colors, the `neutral` scheme functions as a **Super-Scheme**. It isolates layout elevations under a dedicated **Elevation System**, while sharing the standard **Shared Matrix** for other element roles:

```
Neutral Super-Scheme Structure
├── 1. Layout Elevation System
│   ├── canvas
│   │   └── default
│   ├── surface-raised
│   │   └── default
│   ├── surface-floating
│   │   └── default
│   └── surface-sunken
│       └── default
│
└── 2. Common Interactive Elements (Shared Matrix)
    ├── surface
    │   ├── subtle
    │   │   ├── default
    │   │   ├── hover
    │   │   ├── pressed
    │   │   ├── selected
    │   │   └── disabled
    │   ├── default
    │   │   ├── default
    │   │   ├── hover
    │   │   ├── pressed
    │   │   ├── selected
    │   │   └── disabled
    │   ├── strong
    │   │   ├── default
    │   │   ├── hover
    │   │   ├── pressed
    │   │   ├── selected
    │   │   └── disabled
    │   └── contrast
    │       ├── default
    │       ├── hover
    │       ├── pressed
    │       ├── selected
    │       └── disabled
    ├── solid
    │   ├── subtle
    │   │   ├── default
    │   │   ├── hover
    │   │   ├── pressed
    │   │   ├── selected
    │   │   └── disabled
    │   ├── default
    │   │   ├── default
    │   │   ├── hover
    │   │   ├── pressed
    │   │   ├── selected
    │   │   └── disabled
    │   ├── strong
    │   │   ├── default
    │   │   ├── hover
    │   │   ├── pressed
    │   │   ├── selected
    │   │   └── disabled
    │   └── contrast
    │       ├── default
    │       ├── hover
    │       ├── pressed
    │       ├── selected
    │       └── disabled
    ├── border
    │   ├── subtle
    │   │   ├── default
    │   │   ├── selected
    │   │   ├── focus
    │   │   └── disabled
    │   ├── default
    │   │   ├── default
    │   │   ├── selected
    │   │   ├── focus
    │   │   └── disabled
    │   ├── strong
    │   │   ├── default
    │   │   ├── selected
    │   │   ├── focus
    │   │   └── disabled
    │   └── contrast
    │       ├── default
    │       ├── selected
    │       ├── focus
    │       └── disabled
    ├── text
    │   ├── subtle
    │   │   ├── default
    │   │   ├── hover
    │   │   └── disabled
    │   ├── default
    │   │   ├── default
    │   │   ├── hover
    │   │   └── disabled
    │   ├── strong
    │   │   ├── default
    │   │   ├── hover
    │   │   └── disabled
    │   └── contrast
    │       ├── default
    │       ├── hover
    │       └── disabled
    ├── icon
    │   ├── subtle
    │   │   ├── default
    │   │   ├── hover
    │   │   └── disabled
    │   ├── default
    │   │   ├── default
    │   │   ├── hover
    │   │   └── disabled
    │   ├── strong
    │   │   ├── default
    │   │   ├── hover
    │   │   └── disabled
    │   └── contrast
    │       ├── default
    │       ├── hover
    │       └── disabled

    └── shadow
        ├── subtle
        │   ├── default
        │   ├── hover
        │   └── pressed
        ├── default
        │   ├── default
        │   ├── hover
        │   └── pressed
        ├── strong
        │   ├── default
        │   ├── hover
        │   └── pressed
        └── contrast
            ├── default
            ├── hover
            └── pressed
```

| Elevation Role | Architectural Purpose | Typical UI Viewport Placement |
| :--- | :--- | :--- |
| `neutral.canvas` | Root viewport background | Base page backdrop canvas plane |
| `neutral.surface` | Primary container surface | Baseline cards, main content panels |
| `neutral.raised` | Elevated container surface | Floating panels, active card states, main headers |
| `neutral.floating` | Topmost overlay surface | Dropdown lists, tooltips, dialogs, modals |
| `neutral.sunken` | Inset/well viewport surface | Recessed code blocks, input editors, search wells |

##### 5. Global Non-Scheme Families
Visual assets that reside outside the symmetrical schemes matrix for global layout filtering and developer tracing.

###### Rumpun `overlay` (Frosted Glass & Scrim filters)
| Token | Purpose | Typical Usage |
| :--- | :--- | :--- |
| `overlay.scrim` | Dark modal backdrop | Background mask behind active modal containers |
| `overlay.scrim-light` | Light backdrop mask | Bright visual masking under text banners |
| `overlay.glass` | Translucent frosted glass | Semi-transparent light-theme frosted blur panels |
| `overlay.glass-dark` | Dark frosted glass | Semi-transparent dark-theme frosted blur panels |
| `overlay.backdrop` | General backdrop filter | Global CSS blur filter overlay |

###### Rumpun `utility` (Loading Skeletons & Debug)
| Token | Purpose | Typical Usage |
| :--- | :--- | :--- |
| `utility.skeleton` | Loading placeholder | Backdrop block for unrendered text/image nodes |
| `utility.skeleton-shimmer` | Shimmer glow anim | Moving linear gradient highlight strip |
| `utility.selection` | Selected text highlight | Color selection range on user click-and-drag |
| `utility.mask` | Temporary viewport block | Absolute block container covering content |
| `utility.placeholder` | Empty input preview | Grayed out text inside empty input fields |
| `utility.debug` | Developer trace outline | Magenta debug stroke to outline misalignments |

###### Rumpun `chart` (Data Visualization Palette)

| Chart Token Family | Visual Representation | Target Visualization Context |
| :--- | :--- | :--- |
| `chart.categorical.1` to `6` | Symmetrical, distinct hues | Multi-series bar, line, and pie chart series |
| `chart.sequential.1` to `6` | Light-to-dark monotonic gradients | Value density, heatmaps, and progress grids |
| `chart.diverging.1` to `6` | Dual-axis high-contrast scales | Positive/negative splits, deviations, and comparative series |
| `chart.threshold.1` to `6` | Dynamic accent indicators | Limit boundaries, targets, warning/critical zones |



#### 3.2.4 Dimension Semantic Families

##### 1. Spacing Tokens
| Token | Purpose / Scale Increments |
| :--- | :--- |
| `spacing.3xs` | Extreme micro spacing (e.g., tight border adjustments) |
| `spacing.2xs` | Very small spacing / tight content gap |
| `spacing.xs` | Micro margins / small horizontal gaps |
| `spacing.sm` | Small container gap / default element padding |
| `spacing.md` | Standard/medium element padding and layout gaps |
| `spacing.lg` | Large container padding / visual grid gap |
| `spacing.xl` | Major layout sections / panel separators |
| `spacing.2xl` | Extra-large section padding |
| `spacing.3xl` | Massive page padding gaps |
| `spacing.4xl` | Maximum section margin bounds |

##### 2. Size Tokens
| Token | Purpose / Description |
| :--- | :--- |
| `size.control-xs` | Extra-small action control/input height |
| `size.control-sm` | Small button/input height |
| `size.control-md` | Standard select/button control height |
| `size.control-lg` | Large input/button control height |
| `size.control-xl` | Extra-large control height |
| `size.icon-xs` | Mini vector icon box frame |
| `size.icon-sm` | Small supporting icon box frame |
| `size.icon-md` | Medium/standard inline icon box frame |
| `size.icon-lg` | Large visual indicator icon frame |
| `size.avatar-xs` | Micro circular avatar frame |
| `size.avatar-sm` | Small supporting avatar frame |
| `size.avatar-md` | Standard inline user avatar frame |
| `size.avatar-lg` | Large profile-page circular avatar frame |

##### 3. Radius Tokens
| Token | Purpose / Description |
| :--- | :--- |
| `radius.none` | Sharp square corner (no rounding) |
| `radius.sm` | Tight checkbox and small indicator rounding |
| `radius.md` | Standard button, select input, and badge rounding |
| `radius.lg` | Elevated card and container panel rounding |
| `radius.xl` | Large dialog box and overlay panel rounding |
| `radius.2xl` | Extra-large rounding for prominent hero banners |
| `radius.full` | Circular pill shape for badges/dynamic avatars |

##### 4. Stroke Tokens
| Token | Purpose / Description |
| :--- | :--- |
| `stroke.none` | Zero border stroke weight |
| `stroke.hairline` | Ultra-thin hairline divider weight |
| `stroke.thin` | Light secondary container outline |
| `stroke.default` | Standard input and card outline weight |
| `stroke.medium` | Emphasized visual highlight outline weight |
| `stroke.thick` | Heavy structural divider outline weight |

##### 5. Opacity Tokens
| Token | Purpose / Description |
| :--- | :--- |
| `opacity.disabled` | Interactive disabilitation state opacity (e.g., 38%) |
| `opacity.subtle` | Soft overlay transparency |
| `opacity.muted` | Muted background card transparency |
| `opacity.overlay` | Contextual panel backdrop translucency |
| `opacity.scrim` | Page scrim mask opacity (e.g., 60%) |

##### 6. Z-Index (Z) Tokens
| Token | Purpose / Layer Depth |
| :--- | :--- |
| `z.base` | Default page layout layer |
| `z.sticky` | Sticky header navigation container level |
| `z.dropdown` | Floating interactive select option popups |
| `z.popover` | Contextual info cards on trigger click |
| `z.toast` | Page floating temporary toast message alert blocks |
| `z.tooltip` | Micro hover context pills |
| `z.overlay` | Dynamic drawer layout sheets |
| `z.modal` | Centered modal viewport dialogue containers |
| `z.max` | Emergency global overlay level |

##### 7. Composite Shadow Tokens

> **Implementation Note**: These tokens are distinct from `color.shadow.*` (Section 3.2.3, #13). `color.shadow.*` stores raw HSL/RGB color coordinates. `shadow.*` stores the **complete `box-shadow` CSS shorthand** (geometry offset, blur radius, spread, and color reference combined), ready for direct consumption by component styles.

| Token | Purpose / Elevation Level |
| :--- | :--- |
| `shadow.low` | Subtle depth — raised cards and interactive elements |
| `shadow.medium` | Standard elevation — dropdowns and floating elements |
| `shadow.high` | Strong elevation — sticky headers and drawers |
| `shadow.overlay` | Modal and dialog viewport shadow depth |
| `shadow.focus` | Inset focus ring shadow for accessibility states |

#### 3.2.5 Typography Semantic Families

##### 1. Font Family Tokens
| Token | Purpose / Description |
| :--- | :--- |
| `font-family.base` | Default application sans-serif body copy font stack |
| `font-family.heading` | Highly readable sans-serif titles font stack |
| `font-family.mono` | Monospaced stack for code blocks and data displays |
| `font-family.brand` | Custom corporate marketing font stack |

##### 2. Font Size Tokens
| Token | Purpose / Typography Scale |
| :--- | :--- |
| `font-size.xs` | Micro copy and footnote captions size |
| `font-size.sm` | Supporting metadata and label descriptions size |
| `font-size.md` | Default body copy text sizing |
| `font-size.lg` | Accent copy and small subtitle sizing |
| `font-size.xl` | Primary widget section title sizing |
| `font-size.2xl` | Large header card titles sizing |
| `font-size.3xl` | Main dialogue modal heading sizing |
| `font-size.4xl` | Hero marketing page title sizing |

##### 3. Font Weight Tokens
| Token | Purpose / Density |
| :--- | :--- |
| `font-weight.regular` | Standard body copy density |
| `font-weight.medium` | Supporting subtitle emphasis density |
| `font-weight.semibold` | Bold heading emphasis density |
| `font-weight.bold` | Dynamic alerts and strong highlights density |

##### 4. Line Height Tokens
| Token | Purpose / Vertical Alignments |
| :--- | :--- |
| `line-height.tight` | Dense block multiline titles vertical padding height |
| `line-height.normal` | Standard readable text vertical padding height |
| `line-height.relaxed` | Comfortable reader articles vertical padding height |

##### 5. Letter Spacing (Tracking) Tokens
| Token | Purpose / Kerning |
| :--- | :--- |
| `letter-spacing.tight` | Compressed letter kerning for large headings |
| `letter-spacing.normal` | Default letter spacing tracking |
| `letter-spacing.wide` | Spread out letter kerning for capitalized titles |

#### 3.2.6 Motion Semantic Families

##### 1. Duration Tokens
| Token | Purpose / Performance Timing |
| :--- | :--- |
| `duration.instant` | Immediate mount transition timing |
| `duration.fast` | Micro hover interactions timing |
| `duration.normal` | Standard card mount / slide-in timings |
| `duration.slow` | Modal fading overlay timing |
| `duration.slower` | Large accordion expand/collapse timing |

##### 2. Easing Curve Tokens
| Token | Purpose / Mathematical Curve |
| :--- | :--- |
| `easing.standard` | Dynamic entry/exit transition velocity curve |
| `easing.enter` | Fast accelerate decelerate entry curve |
| `easing.exit` | Sharp decelerate accelerate exit curve |
| `easing.emphasized` | Responsive deceleration spring-like timing curve |

##### 3. Transition Tokens
| Token | Purpose / Animation Actions |
| :--- | :--- |
| `transition.hover` | Light dynamic pointer scale / border color animation |
| `transition.focus` | Glow outline transition |
| `transition.expand` | Container height collapse reveal animation |
| `transition.modal` | Modal dialog scale overlay timing transition |
| `transition.toast` | Temporary alerts slide/fade interaction transition |

#### 3.2.7 Component Token Policy
Tier-3 component tokens are only allowed under strict conditions:
1. Must represent a truly unique semantic behavior.
2. Must have a clear likelihood of independent visual divergence.
3. Must be reused across multiple products.
*Rule:* If these conditions are not met, components must consume Tier-2 tokens directly. For example, a unique caret color is a valid component token, while a button background that simply mirrors `surface.default` is strictly forbidden.

### 3.3 Cascading Multi-Theme & Partial Contracts Invariant
The platform natively supports multi-theme and multi-brand white-label capabilities under a strict cascading model:
1.  **Global Baseline Theme**: The default theme is the Visual Root of Trust, registering and injecting all 71 core variables onto the global `:root` selector.
2.  **Cascading Overrides**: Brand or contextual themes (such as `achromatic`) only override the specific visual characteristics (e.g. colors, shadows, and radii) they require. All other variables (such as grid spacing, layouts, and typography) cascade (inherit) from the global baseline theme.
3.  **Partial Contract Invariant**: Override themes are validated against a custom, brand-specific contract map. This contract represents a **partial subset of the core `$system` contract**. It can contain a subset of core keys, but **it must not introduce any undocumented keys or variables that are absent from the core `$system` contract**, ensuring strict compile-time design safety and zero visual leakage.

### 3.4 Token Consumption Governance

> **Authoritative Source**: The full operational governance framework,
> consumption doctrines, alias budgeting rules, and enforcement mechanisms
> for design tokens are defined and maintained in
> **[STD-E016 — Enterprise UI Platform Design Tokens Standard](../../02-standards/STD-E016-ui-platform-design-tokens-standard.md)**.
>
> Per the Document Authority Rule (GDC-000 §2.2), this PAD must not replicate
> that content. The following is a normative summary only.

The platform enforces six foundational doctrines to prevent **Semantic
Entropy** as it scales to multi-brand environments with federated
micro-frontends:

1. **Token Consumption Laws** (STD-E016 §4.1): Zero-bypass rule —
   all styling must resolve through Tier-2 semantic custom properties.
   Raw OKLCH/HSL/HEX literals in component files are prohibited.

2. **Semantic Usage Doctrine** (STD-E016 §4.2): The four `Emphasis`
   layers (`subtle`, `default`, `strong`, `contrast`) carry strict
   semantic contracts. Misusing layers is a governance violation.

3. **Domain Semantic Layer** (STD-E016 §4.3): Portals must implement a
   thin logical alias mapping layer (`state.fraud → danger.solid.default`)
   to prevent domain-specific logic from corrupting the global token matrix.

4. **Typography Density Families** (STD-E016 §5.1): Tokens are grouped
   by semantic reading context (`data.compact`, `article.readable`,
   `metric.display`), not by arbitrary font size progression.

5. **Motion Language** (STD-E016 §5.2): Easing curves and durations map
   to communicative motion actions (`motion.enter`, `motion.exit`,
   `motion.attention`, `motion.disclosure`). Animating layout properties
   is prohibited under the Zero Layout Thrashing constraint.

6. **Tier-3 Alias Budgeting** (STD-E016 §6): Each component is limited
   to **5 custom Tier-3 aliases**. Every addition requires an ADR approved
   by the Visual Platform Board.

---

## 4. Strategic Architecture

The `@scnx/system` platform serves as the visual foundation distributed to container applications via Module Federation.

```mermaid
graph TD
    DS[Design System Package] -->|Compile & Publish| NPM[@scnx/system NPM]
    NPM -->|Consume| AppHost[ERP Portal Host]
    NPM -->|Consume| AppRemote[HRIS Micro-App Remote]
    AppHost -->|Module Federation Shared Styles| Web[Web Runtime]
    AppRemote -->|Module Federation Shared Styles| Web
```

The token architecture structure is grouped in isolation to guarantee zero visual contamination:

```
[Tier 1: Core Primitives] -> [Tier 2: Global Semantic Contract] -> [Tier 3: Component Token]
(Raw OKLCH coordinates)      (Symmetrical Semantic Tokens)          (Direct Component consumes)
```

---

## 5. Quality Attributes

-   **Performance Constraints**: CSS compilation output must be lightweight. The compressed global design system token bundle must not exceed `12KB` (gzip).
-   **Zero Layout Thrashing**: Any transition or animation must execute using GPU-accelerated CSS properties (`transform` and `opacity` only). Layout reflow triggers (e.g., modifying `width`, `height`, or `margin` inside animations) are prohibited to ensure p95 frame rendering completes within `16ms`.
-   **Theme Switching Latency**: Theme swaps (e.g., Light to Dark mode) must execute in under `50ms` by mutating a single global data-attribute (`data-theme`) on the root elements, avoiding application-wide component re-renders.
-   **Sub-Pixel Precision Styling**: All padding, spacing, and typography boundaries must match a strict 4px grid system, ensuring flawless visual alignment at any desktop screen resolution.
