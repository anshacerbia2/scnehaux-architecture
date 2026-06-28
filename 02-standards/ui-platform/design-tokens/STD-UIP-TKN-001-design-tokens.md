---
doc_meta:
  id: STD-UIP-TKN-001
  title: UI Platform Design Tokens Architecture & Pipeline
  owner: Principal Frontend Architect
  version: 2.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-25
  governed_by:
    - GDC-000
    - GDC-010
  references:
    - DOC-P002
---

# UI Platform Design Tokens Architecture & Pipeline (STD-UIP-TKN-001)

---

## 1. Objective & Scope

This standard defines the architecture, compilation pipeline, consumption contracts, and operational governance doctrines for design tokens within the Scnehaux enterprise UI platform (`@scnx/system`).

It guarantees that visual properties — colors, dimensions, typography, and motion — are structured, compiled, and delivered consistently across all products, enabling design changes without manual style refactoring and preventing semantic drift as the platform scales to multi-brand environments with hundreds of components and federated micro-frontends.

**Authoritative Source**: This document is the single source of truth for all token standards. The Product Architecture Document (PAD-002) references this document for governance details and must not replicate these rules.

## 2. Design Principles

The design token architecture is governed by four core principles to ensure cross-platform consistency, visual harmony, and operational scaling:

1. **Semantic Isolation**: UI components consume abstract semantic tokens (Tier 2) rather than raw value primitives (Tier 1), shielding component layouts from changes in core visual definitions.
2. **Perceptual Color Uniformity**: Color specifications utilize the photometric OKLCH color space to guarantee consistent contrast ratios and predictable color mixing across light and dark interfaces.
3. **Platform Agnosticity**: Token structures are defined as technology-agnostic keys and values, decoupled from execution environments (such as CSS, Swift, or Android XML) to enable unified enterprise-wide delivery.
4. **Symmetrical Theme Alignment**: Light and dark themes utilize identical semantic token paths, enabling runtime theme switching through stylesheet replacement without modifying application logic.

## 3. Normative Rules

### Design Token Taxonomy

> **Authoritative Taxonomy Source**: The explicit rationale, 3-Tier architecture design, Symmetrical Orthogonal Semantic Matrix (`[Scheme] × [Role] × [Emphasis] × [State]`), and OKLCH color generation math are defined in the Enterprise Architecture Decision **[ADR-UIP-TKN-003](../../../05-decisions/ui-platform/design-tokens/ADR-UIP-TKN-003-token-taxonomy-and-naming-convention.md)**. This Standard enforces the execution of that taxonomy.

The platform enforces a strict **3-Tier Token Architecture**:

1. **Tier 1 (Core Primitives)**: Raw OKLCH coordinates. **Prohibited** from being consumed directly by components or application layers. Must only be accessed via the build-time SASS compiler (`get-color()`).
2. **Tier 2 (Global Semantic Contract)**: Symmetrical, orthogonal semantic tokens (`--ds-{scheme}-{role}-{emphasis}-{state}`). This is the **mandatory** consumption layer for all downstream components.
3. **Tier 3 (Component Tokens)**: Component-bound aliases. Strongly restricted by the Component Alias Budget.

#### The State Compatibility Invariant

The Semantic Matrix is governed by a strict, non-symmetric State Compatibility Table. Not all roles support all states. The SASS compile-time validator (`_contract-token.scss`) enforces this table mechanically.

| Element | Hover | Pressed | Selected | Focus | Disabled |
| :------ | :---: | :-----: | :------: | :---: | :------: |
| Surface | ✅    | ✅      | ✅       | ❌    | ✅       |
| Border  | ❌    | ❌      | ✅       | ✅    | ✅       |
| Text    | ✅    | ❌      | ❌       | ❌    | ✅       |
| Icon    | ✅    | ❌      | ❌       | ❌    | ✅       |
| Shadow  | ✅    | ✅      | ❌       | ❌    | ❌       |

*Any attempt to generate or consume an illegal state (e.g., `text.selected` or `surface.focus`) must fail the CI build with a CRITICAL error.*

---

### Token Compilation & Delivery Pipeline

#### Centralized OKLCH Recipe Engine

Token values must be generated via a **compile-time OKLCH Recipe Engine**
(SASS mixin: `generate-scheme-matrix`) residing in `_default-token.scss`.
The engine applies mathematically consistent lightness, chroma, and hue
transforms across all 32 semantic anchors to guarantee contrast ratios and
visual harmony without manual hand-tuning per-token.

- **Primitive Isolation**: The recipe engine is the only entity authorized to
  access Tier-1 OKLCH coordinates.
- **Output Format**: Compiled tokens are emitted as CSS Custom Properties
  prefixed with `--ds-` (e.g., `--ds-color-primary-solid-default-default`).
- **Build-Time Delivery**: Generated variables must be injected via the global
  `@scnx/system` stylesheet bundle prior to DOM parsing.
- **Dual-Axis Calibration**: The compilation pipeline enforces a dual-axis scaling scheme. The **Lightness Axis** maps theme curves in perceptually uniform OKLCH space, and the **Transparency/Alpha Axis** resolves translucent overlays via browser-level `color-mix()` in OKLCH space. The compile-time solver validates the precise overlay ratio ($X\%$) to prevent CSS code bloat and avoid generating static transparent tokens.

#### Cascading Multi-Theme & Partial Contracts Invariant

The platform supports multi-theme and multi-brand white-label capabilities
under a strict cascading model:

1. **Global Baseline Theme (Visual Root of Trust)**: The default theme
   registers and injects all core CSS variables onto the `:root` selector.
2. **Cascading Overrides**: Brand or contextual themes (e.g., `achromatic`)
   only override the specific visual characteristics they require (colors,
   shadows, radii). All other variables cascade from the baseline.
3. **Partial Contract Invariant**: Override themes are validated against a
   brand-specific contract map that is a **partial subset of the core
   `$system` contract**. It may contain fewer keys, but it must **not
   introduce any undocumented keys** absent from the core `$system` contract,
   ensuring zero visual leakage and strict compile-time safety.

#### Build-Time Contract Validation

The `_contract-token.scss` validator enforces role-specific state legality
at compile time:

- Schemas are declared as SASS maps (e.g., `$states-text-icon`) and passed
  to the `generate-scheme-matrix` mixin.
- The mixin raises a `@error` on any attempt to generate a state that is
  absent from the role's valid compatibility map.
- **Result**: Impossible state tokens are structurally eliminated from the
  output bundle, enforcing the State Compatibility Table without runtime
  checks.

---

### Consumption Contracts

#### Token Consumption Laws (Zero-Bypass Rule)

To maintain the visual root of trust, the platform enforces an absolute
zero-bypass styling rule across all consumer layers:

- **Semantic Supremacy**: Component styles must rely 100% on Tier-2 semantic
  CSS custom properties (e.g., `var(--ds-color-primary-solid-default-default)`
  or the `get-color()` SASS accessor).
- **Primitive Isolation**: Declaring raw OKLCH, HSL, HEX, or RGB color
  literals in any component, portal, or layout file is strictly prohibited.
- **Utility Styling Compliance**: Utility-class configurations must resolve
  styling through token-bound utility maps, not arbitrary values.

#### Semantic Usage Doctrine (Preventing Semantic Drift)

To ensure consistent design decisions across product teams, the `Emphasis`
layers must obey explicit behavioral guidelines. Misusing layers (e.g.,
rendering body copy with `contrast` emphasis) is a semantic violation:

| Emphasis Layer | Intended Visual & Semantic Rationale | Typical UX/UI Components |
| :------------- | :----------------------------------- | :----------------------- |
| **`subtle`**   | Passive contextual surface or border accents representing background canvases and structural sections. | Alert banners, passive cards, table row hover, static badge fills |
| **`default`**  | Standard interactive element surfaces, outlines, and readable copy. | Standard button surfaces, default input borders, readable body copy, main icons |
| **`strong`**   | Elevated prominence representing active visual priority or highlighted emphasis. | Active indicators, bold headings, high-visibility warning borders |
| **`contrast`** | Maximum readability contrast designed strictly for placement on top of filled surfaces. | Text/icons inside filled brand buttons, indicators on dark badges |

#### Domain Semantic Layer (Logical Intent Mapping)

To prevent global color roles from colliding with domain-specific logic in
complex systems (HRIS, ERP, Finance), portals must implement a thin logical
mapping layer on top of the global color schemes:

```
[Domain State Layer] ──▶ [Global Semantic Layer] ──▶ [Core Primitives]
(e.g., state.fraud)       (danger.solid.default)      (0.55 0.24 25 oklch)
```

Portals declare semantic logical aliases that internally map directly to
scheme tokens, preventing business domain requirements from leaking into and
corrupting the core global matrix:

- `state.approved` → `success.solid.default`
- `state.pending`  → `warning.surface.subtle`
- `state.fraud`    → `danger.solid.default`
- `state.archived` → `neutral.surface.strong`

---

### Typography & Motion Semantic Families

#### Semantic Reading Density (Typography)

Typography tokens must be grouped by **semantic reading layout**, not by
linear sequential text scaling. This prevents teams from scaling fonts
arbitrarily across dense dashboards and article-style portals:

| Group | Token | Intended Reading Context |
| :---- | :---- | :----------------------- |
| **Data** | `typography.data.compact` | High-density data-grids, tabular controls, dense dashboard summaries |
| **Article** | `typography.article.readable` | Sustained reading of text-heavy prose, articles, documentation |
| **Metric** | `typography.metric.display` | Standalone numeric KPIs, scores, and display indicators |

#### Semantic Motion Language

Timing durations and mathematical easing curves must map to high-level
communicative actions, not arbitrary numeric values:

| Motion Token | Communicative Action |
| :----------- | :------------------- |
| `motion.enter` | Responsive, snappy spring curves for mounting actions (drawer sliding in, dropdown mounting) |
| `motion.exit` | Quick, decelerating exits to keep portal interactions efficient and lag-free |
| `motion.attention` | Soft pulsating scale animations to highlight critical visual actions without disturbing layout flows |
| `motion.disclosure` | Smooth height expand/collapse transitions for accordions, menus, and detail triggers |

**Performance Constraint**: All motion tokens must resolve exclusively to
`transform` and `opacity` CSS properties. Animating layout properties
(`width`, `height`, `margin`) is prohibited under the Zero Layout Thrashing
rule (see PAD-002, Section 5).

---

### Tier-3 Alias Governance

#### Component Alias Budget

To prevent custom styling bloat where federated teams spawn endless Tier-3
aliases for minor adjustments, the platform enforces strict alias budgeting:

- **Alias Budget**: A single component is allowed a maximum of **5 custom
  Tier-3 aliases** (e.g., `--ds-btn-custom-border`).
- **Divergence Proof**: SPAs must present a visual, measurable design
  rationale justifying why Tier-2 semantic tokens cannot satisfy the
  styling contract before any Tier-3 alias is introduced.
- **ADR & Review Mandate**: Introducing any new Tier-3 alias requires an
  Architectural Decision Record (ADR) approved by the Visual Platform Board,
  preventing styling sprawl.

#### Alias Naming Convention

All Tier-3 component aliases must follow the convention:
```
--ds-[component]-[role]-[state]
```
Examples:
- `--ds-btn-surface-hover`
- `--ds-badge-border-selected`
- `--ds-input-text-disabled`

---


## 4. Exceptions

None. All design token architecture rules apply unconditionally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

### 5.7.1 Static AST Verification (Zero-Bypass Enforcement)

Build-time scanners and ESLint/Stylelint AST plugins must actively parse
component source code:

- **Blocking Rule**: Any raw style declaration that bypasses the Tier-2
  semantic layer (e.g., `background: oklch(...)`, `color: #fff`,
  `border-color: hsl(...)`) must fail the CI build with a `CRITICAL` error
  and block PR merging.
- **Z-Index Enforcement**: Elements requiring z-index properties must
  reference system z-index tokens (e.g., `var(--ds-z-index-modal)`).
  Hardcoded z-index integers are prohibited.

### 5.7.2 Build Contract Validation

The SASS compile pipeline (`pnpm --filter "@scnx/system" build`) is the
primary mechanical enforcement gate:

- `@error` directives in `_contract-token.scss` block compilation if any
  token attempt violates the State Compatibility Table.
- Any build failure from this gate is treated as a `CRITICAL` schema
  violation requiring an immediate fix before the PR can merge.

### 5.7.3 Waiver Protocol

Deviations from any rule in this standard (new Tier-3 aliases, partial
schema exceptions, alternative motion properties) require:

1. A documented project ADR approved by the Architecture Review Board (ARB).
2. The ARB must respond within **5 business days** of ADR submission.
3. Approved waivers have a maximum validity of **365 days** before mandatory
   re-evaluation.
