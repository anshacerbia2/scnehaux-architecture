---
doc_meta:
  id: STD-UIP-TKN-001
  title: UI Platform Design Tokens Architecture & Pipeline
  owner: Principal Frontend Architect
  version: 2.0.0
  status: proposed
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-28
  governed_by: [ADR-UIP-PLT-001]
  references:
    - PAD-PLT-003
---

# UI Platform Design Tokens Architecture & Pipeline (STD-UIP-TKN-001)

> **Review draft:** Sass maps are the current implementation. A DTCG 2025.10 source that generates CSS, Sass, and Panda contracts is a migration target, not an implemented guarantee.

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
4. **Symmetrical Theme Paths**: Supported themes supply the same required semantic keys, while brand overrides remain scoped to a declared root.

## 3. Normative Rules

### Design Token Taxonomy

> **Authoritative Taxonomy Source**: The explicit rationale, 3-Tier architecture design, Symmetrical Orthogonal Semantic Matrix (`[Scheme] × [Role] × [Emphasis] × [State]`), and OKLCH color generation math are defined in the Enterprise Architecture Decision **[ADR-UIP-TKN-003](../../05-decisions/ui-platform/ADR-UIP-TKN-003-token-taxonomy-and-naming-convention.md)**. This Standard enforces the execution of that taxonomy.

The platform enforces a strict **3-Tier Token Architecture**:

1. **Tier 1 (Core Primitives)**: Raw scales and values, including color, spacing, typography, and motion. Components and applications do not consume them directly. Sass is the current authoring implementation, not a permanent architectural requirement.
2. **Tier 2 (Global Semantic Contract)**: Color uses `color.{scheme}.{role}.{emphasis}.{state}`. Dimension, typography, and motion use `{domain}.{property}.{intent}`. Declared role/state compatibility limits the color matrix.
3. **Tier 3 (Component Tokens)**: Component aliases use `{component}.{element?}.{property}.{state?}` and require independent semantic intent.

CSS output prefixes `--ds-` and converts logical path separators to hyphens. For example, `color.primary.solid.default.default` emits `--ds-color-primary-solid-default-default`.

#### The State Compatibility Invariant

The Semantic Matrix is governed by a strict, non-symmetric State Compatibility Table. Not all roles support all states. The SASS compile-time validator (`_contract-token.scss`) enforces this table mechanically.

| Element | Hover | Pressed | Selected | Focus | Disabled |
| :------ | :---: | :-----: | :------: | :---: | :------: |
| Surface |  ✅   |   ✅    |    ✅    |  ❌   |    ✅    |
| Border  |  ❌   |   ❌    |    ✅    |  ✅   |    ✅    |
| Text    |  ✅   |   ❌    |    ❌    |  ❌   |    ✅    |
| Icon    |  ✅   |   ❌    |    ❌    |  ❌   |    ✅    |
| Shadow  |  ✅   |   ✅    |    ❌    |  ❌   |    ❌    |

The Sass validator rejects unsupported generated role/state combinations. Consumer lint and package-output checks are target CI gates, not yet proven active.

---

### Token Compilation & Delivery Pipeline

#### Centralized OKLCH Recipe Engine

The current implementation generates color values using Sass maps and a compile-time recipe engine. Mathematical transforms alone do not establish contrast or visual harmony. A future canonical token source must generate the Sass and Panda contracts from the same versioned data.

- **Primitive Isolation**: The recipe engine is the only entity authorized to access Tier-1 OKLCH coordinates.
- **Output Format**: Compiled tokens are emitted as CSS Custom Properties prefixed with `--ds-` (e.g., `--ds-color-primary-solid-default-default`).
- **Build-Time Delivery**: Variables are distributed through documented CSS exports. Consumers import the required theme and component CSS before expecting platform styling.
- **Color and alpha calibration**: Validate generated colors and translucent overlays on their actual background. The implementation may use OKLCH or `color-mix()` where supported, but no solver or byte saving is presumed without an output test.

#### Cascading Multi-Theme & Partial Contracts Invariant

The platform supports multi-theme and multi-brand white-label capabilities under a strict cascading model:

1. **Baseline Theme**: Every public theme supplies required variables below `[data-scnx-theme="<theme-id>"]`. A separate `:root` compatibility output MAY serve a single-brand document.
2. **Cascading Overrides**: Brand themes (for example `achromatic`) may override a documented subset within that scoped root. Shadow DOM is outside v1.
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

| Emphasis Layer | Intended Visual & Semantic Rationale                                                                   | Typical UX/UI Components                                                        |
| :------------- | :----------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **`subtle`**   | Passive contextual surface or border accents representing background canvases and structural sections. | Alert banners, passive cards, table row hover, static badge fills               |
| **`default`**  | Standard interactive element surfaces, outlines, and readable copy.                                    | Standard button surfaces, default input borders, readable body copy, main icons |
| **`strong`**   | Elevated prominence representing active visual priority or highlighted emphasis.                       | Active indicators, bold headings, high-visibility warning borders               |
| **`contrast`** | Maximum readability contrast designed strictly for placement on top of filled surfaces.                | Text/icons inside filled brand buttons, indicators on dark badges               |

#### Domain Semantic Layer (Logical Intent Mapping)

To prevent global color roles from colliding with domain-specific logic in complex systems (HRIS, ERP, Finance), portals must implement a thin logical mapping layer on top of the global color schemes:

```
[Domain State Layer] ──▶ [Global Semantic Layer] ──▶ [Core Primitives]
(e.g., state.fraud)       (danger.solid.default)      (0.55 0.24 25 oklch)
```

Portals declare semantic logical aliases that internally map directly to scheme tokens, preventing business domain requirements from leaking into and corrupting the core global matrix:

- `state.approved` → `success.solid.default`
- `state.pending` → `warning.surface.subtle`
- `state.fraud` → `danger.solid.default`
- `state.archived` → `neutral.surface.strong`

---

### Typography & Motion Semantic Families

#### Semantic Reading Density (Typography)

Typography tokens must be grouped by **semantic reading layout**, not by linear sequential text scaling. This prevents teams from scaling fonts arbitrarily across dense dashboards and article-style portals:

| Group       | Token                         | Intended Reading Context                                             |
| :---------- | :---------------------------- | :------------------------------------------------------------------- |
| **Data**    | `typography.data.compact`     | High-density data-grids, tabular controls, dense dashboard summaries |
| **Article** | `typography.article.readable` | Sustained reading of text-heavy prose, articles, documentation       |
| **Metric**  | `typography.metric.display`   | Standalone numeric KPIs, scores, and display indicators              |

#### Semantic Motion Language

Timing durations and mathematical easing curves must map to high-level communicative actions, not arbitrary numeric values:

| Motion Token        | Communicative Action                                                                                 |
| :------------------ | :--------------------------------------------------------------------------------------------------- |
| `motion.enter`      | Responsive, snappy spring curves for mounting actions (drawer sliding in, dropdown mounting)         |
| `motion.exit`       | Quick, decelerating exits to keep portal interactions efficient and lag-free                         |
| `motion.attention`  | Soft pulsating scale animations to highlight critical visual actions without disturbing layout flows |
| `motion.disclosure` | Smooth height expand/collapse transitions for accordions, menus, and detail triggers                 |

**Performance Constraint**: Dynamic-height motion may involve layout. Reduced-motion behavior and interaction traces determine whether a transition is acceptable. Claims about forced layout and frame rate require named scenarios and measurements.

---

### Tier-3 Alias Governance

#### Component Alias Budget

To prevent unbounded aliases, the platform reviews their semantics and reuse:

- **Alias review**: Record the component purpose, Tier-2 fallback, theme/state coverage, and migration impact. A numerical cap and an ADR for each alias are not required.

#### Alias Naming Convention

All Tier-3 logical aliases follow:

```
{component}.{element?}.{property}.{state?}
```

Examples:

- `button.surface.hover` → `--ds-button-surface-hover`
- `checkbox.indicator.color.checked` → `--ds-checkbox-indicator-color-checked`
- `input.root.border.focus` → `--ds-input-root-border-focus`

---

## 4. Exceptions

Deviations identify the affected consumer contract, rationale, owner, and migration path under enterprise governance.

## 5. Enforcement Mechanism

### 5.7.1 Static AST Verification (Zero-Bypass Enforcement)

Target source checks parse component styling and report bypasses:

- **Blocking Rule**: Governed shared styles with unjustified raw color literals fail the source gate when the rule is implemented.
- **Z-Index Enforcement**: Elements requiring z-index properties must reference system z-index tokens (e.g., `var(--ds-z-index-modal)`). Hardcoded z-index integers are prohibited.

### 5.7.2 Build Contract Validation

The SASS compile pipeline (`pnpm --filter "@scnx/system" build`) is the primary mechanical enforcement gate:

- `@error` directives in `_contract-token.scss` block compilation if any token attempt violates the State Compatibility Table.
- Any build failure from this gate is treated as a `CRITICAL` schema violation requiring an immediate fix before the PR can merge.
- Packed stylesheets are checked for missing required variables, valid resolved values in consuming properties (including shadows and font families), and declared foreground/background contrast pairs in each supported theme and state.
- Until generation and checks are connected to CI, documentation must not claim that palette generation is contrast-guaranteed or fail-closed.

### 5.7.3 Waiver Protocol

Formal exceptions follow GDC-010 and the applicable standard-governance process. Routine justified Tier-3 aliases are reviewed as token-contract changes, not treated as automatic waivers.
