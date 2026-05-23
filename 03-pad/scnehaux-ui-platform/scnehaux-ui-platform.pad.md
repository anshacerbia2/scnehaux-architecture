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
*   Conceptual Surface Canvas $\rightarrow$ `--ds-color-bg-canvas` / `$color-bg-canvas`
*   Conceptual Primary Hover $\rightarrow$ `--ds-color-primary-hover` / `$color-primary-hover`
*   Conceptual Success Border $\rightarrow$ `--ds-color-success-border` / `$color-success-border`

### 3.2 The Master Semantic Taxonomy

The platform standardizes on a platform-agnostic, hierarchical design token taxonomy. Below is the exhaustive reference mapping of the SCNX Master Semantic Taxonomy as defined in the core token specification:

#### 3.2.1 Architectural Principle
All tokens are modeled in a strict 3-tier system:
1. **Tier-1: Primitive (Raw Values)**: Platform-agnostic raw constants without semantic meaning (e.g., base color scales, fixed spacing increments).
2. **Tier-2: Semantic (Global Meaning)**: The single source of truth mapping primitives to structural UI intents using standard platform-agnostic names.
3. **Tier-3: Component Aliases (Unique Overrides)**: Optional overrides reserved strictly for component-unique behavior where independent styling divergence is structurally justified.

#### 3.2.2 Master Semantic Families
The taxonomy covers the following token families across four major domains:
*   **Color Families**: `surface`, `state`, `feedback`, `overlay`, `brand`, `utility`, `layer`, `text`, `border`, `icon`, `ring`, `shadow`, `chart`.
*   **Dimension Families**: `spacing`, `size`, `radius`, `stroke`, `opacity`, `z`.
*   **Typography Families**: `font-family`, `font-size`, `font-weight`, `line-height`, `letter-spacing`.
*   **Motion Families**: `duration`, `easing`, `transition`, `animation`.

#### 3.2.3 Full Color Semantic Taxonomy

##### 1. Color Semantic Domains
| Family | Purpose | Typical Usage |
| :--- | :--- | :--- |
| `surface` | Structural UI planes | page, cards, panels, drawers |
| `state` | Interactive visual states | hover, selected, disabled |
| `feedback` | Semantic status communication | alert, badge, toast |
| `overlay` | Global visual effects | scrim, glass, backdrop |
| `brand` | Brand identity surfaces | CTA, brand sections |
| `utility` | Special-purpose helper fills | skeleton, highlight |
| `layer` | Elevation abstraction | z-plane orchestration |
| `text` | Semantic text colors | primary, secondary, danger |
| `border` | Semantic strokes | divider, focus, error |
| `icon` | Semantic icon colors | nav, actions, status |
| `ring` | Focus accessibility rings | keyboard focus |
| `shadow` | Depth tokens | card, modal, floating |
| `chart` | Data visualization palette | dashboards, reports |

##### 2. Surface Tokens
| Token | Purpose |
| :--- | :--- |
| `surface.canvas` | Root viewport background |
| `surface.default` | Primary container surface |
| `surface.subtle` | Secondary soft surface |
| `surface.muted` | Less emphasized section |
| `surface.sunken` | Inset/well/editor area |
| `surface.raised` | Elevated card/panel |
| `surface.floating` | Popover/tooltip plane |
| `surface.overlay` | Modal content plane |
| `surface.translucent` | Blur/glass surface |
| `surface.inverse` | Inverted dark surface |

##### 3. State Tokens
| Token | Purpose |
| :--- | :--- |
| `state.hover` | Pointer hover state |
| `state.pressed` | Active press state |
| `state.selected` | Selected entity |
| `state.current` | Current location/navigation |
| `state.checked` | Checked boolean state |
| `state.open` | Open disclosure/menu |
| `state.dragging` | Drag source |
| `state.drop-target` | Drag destination |
| `state.disabled` | Disabled interaction |
| `state.readonly` | Readonly region |
| `state.loading` | Loading active region |
| `state.pending` | Waiting async operation |
| `state.focus-visible` | Keyboard focus state |

##### 4. Feedback Tokens & Emphasis
| Pattern | Purpose |
| :--- | :--- |
| `feedback.info.*` | informational status |
| `feedback.success.*` | success state |
| `feedback.warning.*` | warning state |
| `feedback.danger.*` | destructive/error state |
| `feedback.neutral.*` | neutral semantic status |
| `feedback.accent.*` | promotional/highlight status |

*Emphasis Scale:*
| Emphasis | Purpose |
| :--- | :--- |
| `subtle` | light tint |
| `muted` | medium soft fill |
| `default` | standard fill |
| `strong` | highest emphasis |

##### 5. Overlay Tokens
| Token | Purpose |
| :--- | :--- |
| `overlay.scrim` | dark modal backdrop |
| `overlay.scrim-light` | light image overlay |
| `overlay.glass` | translucent blur |
| `overlay.glass-dark` | dark blur |
| `overlay.backdrop` | generic overlay filter |

##### 6. Brand Tokens
| Token | Purpose |
| :--- | :--- |
| `brand.primary` | primary brand fill |
| `brand.secondary` | secondary brand fill |
| `brand.subtle` | subtle brand area |
| `brand.inverse` | inverted brand fill |

##### 7. Utility Tokens
| Token | Purpose |
| :--- | :--- |
| `utility.skeleton` | loading placeholder |
| `utility.skeleton-shimmer` | skeleton animation |
| `utility.highlight` | text/content highlight |
| `utility.selection` | selected region |
| `utility.mask` | temporary blocked area |
| `utility.placeholder` | empty preview |
| `utility.debug` | internal dev/debug |

##### 8. Layer Tokens
| Token | Purpose |
| :--- | :--- |
| `layer.base` | normal page layer |
| `layer.raised` | elevated card |
| `layer.sticky` | sticky headers |
| `layer.dropdown` | dropdown menus |
| `layer.popover` | floating contextual panel |
| `layer.toast` | notification layer |
| `layer.tooltip` | tooltip layer |
| `layer.overlay` | drawer layer |
| `layer.modal` | modal dialog |
| `layer.scrim` | backdrop plane |
| `layer.max` | emergency top-most |

##### 9. Text Tokens
| Token | Purpose |
| :--- | :--- |
| `text.primary` | primary readable text |
| `text.secondary` | secondary text |
| `text.tertiary` | muted supporting text |
| `text.disabled` | disabled text |
| `text.inverse` | text on dark bg |
| `text.placeholder` | placeholder |
| `text.link` | anchor text |
| `text.link-hover` | hovered anchor |
| `text.success` | success text |
| `text.warning` | warning text |
| `text.danger` | error text |

##### 10. Border Tokens
| Token | Purpose |
| :--- | :--- |
| `border.default` | standard border |
| `border.subtle` | low-emphasis border |
| `border.strong` | emphasized border |
| `border.inverse` | border on dark bg |
| `border.focus` | accessibility focus |
| `border.disabled` | disabled border |
| `border.success` | success border |
| `border.warning` | warning border |
| `border.danger` | error border |

##### 11. Icon Tokens
| Token | Purpose |
| :--- | :--- |
| `icon.primary` | primary icons |
| `icon.secondary` | supporting icons |
| `icon.tertiary` | muted icons |
| `icon.disabled` | disabled icons |
| `icon.inverse` | icon on dark bg |
| `icon.brand` | brand icon |
| `icon.success` | status success |
| `icon.warning` | status warning |
| `icon.danger` | status danger |

##### 12. Ring Tokens
| Token | Purpose |
| :--- | :--- |
| `ring.focus` | focus ring |
| `ring.focus-inset` | inset focus ring |
| `ring.error` | error ring |
| `ring.drag` | drag highlight ring |

##### 13. Shadow Tokens
| Token | Purpose |
| :--- | :--- |
| `shadow.low` | subtle depth |
| `shadow.medium` | standard elevation |
| `shadow.high` | strong elevation |
| `shadow.overlay` | modal shadow |
| `shadow.focus` | focus shadow |

##### 14. Chart Tokens
| Token | Purpose |
| :--- | :--- |
| `chart.categorical.*` | categorical data series |
| `chart.sequential.*` | sequential data |
| `chart.diverging.*` | diverging values |
| `chart.threshold.*` | threshold markers |

#### 3.2.4 Dimension Semantic Families

##### 1. Spacing Tokens
| Token | Purpose / Scale Increments |
| :--- | :--- |
| `spacing.xxxs` | Extreme micro spacing (e.g., tight border adjustments) |
| `spacing.xxs` | Very small spacing / tight content gap |
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
(Raw HSL / OKLCH coordinates) (71 Semantic Axis Tokens)             (Direct Component consumes)
```

---

## 5. Quality Attributes

-   **Performance Constraints**: CSS compilation output must be lightweight. The compressed global design system token bundle must not exceed `12KB` (gzip).
-   **Zero Layout Thrashing**: Any transition or animation must execute using GPU-accelerated CSS properties (`transform` and `opacity` only). Layout reflow triggers (e.g., modifying `width`, `height`, or `margin` inside animations) are prohibited to ensure p95 frame rendering completes within `16ms`.
-   **Theme Switching Latency**: Theme swaps (e.g., Light to Dark mode) must execute in under `50ms` by mutating a single global data-attribute (`data-theme`) on the root elements, avoiding application-wide component re-renders.
-   **Sub-Pixel Precision Styling**: All padding, spacing, and typography boundaries must match a strict 4px grid system, ensuring flawless visual alignment at any desktop screen resolution.
