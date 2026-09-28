---
doc_meta:
  id: STD-GLB-FE-005
  title: Enterprise Frontend Styling Standard
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

# Enterprise Frontend Styling Standard (STD-GLB-FE-005)

> **Review candidate:** ADR-GLB-FE-010 must be accepted before this major revision becomes active.

## 1. Objective & Scope

This standard defines styling ownership, token consumption, selector isolation, cascade order, theme scope, CSS delivery, responsive behavior, and measurable budgets for web applications, shared libraries, and federated frontends.

## 2. Design Principles

1. **Static and inspectable output:** shared library styles are produced before publication and remain debuggable as CSS assets.
2. **Semantic decisions:** reusable visual intent uses governed semantic tokens.
3. **Scoped effects:** selectors, resets, and themes declare the subtree they affect.
4. **Deterministic precedence:** named cascade layers make ownership and override order explicit.
5. **Measured cost:** payload and runtime limits identify a real consumer scenario.

## 3. Normative Rules

### 3.1 Tool and ownership boundaries

Applications may use CSS Modules, token-bound utilities, Sass, PostCSS, or approved static CSS generators. Shared UI libraries publish compiled CSS and do not require consumers to run their producer toolchain.

Runtime style evaluation or render-path style injection is prohibited for the shared UI Platform and for new applications. An existing application that injects styles at render time records a migration plan in its SAD. A tool choice does not establish selector isolation, accessibility, tree shaking, or performance by itself.

The UI Platform may use Sass component rules and Panda recipes during the pre-release remediation milestone under ADR-GLB-FE-013. One generated token contract owns names across both outputs.

### 3.2 Token and local-value contract

Governed shared decisions for color, typography, spacing rhythm, radius, shadow, z-index, and motion use Tier-2 semantic tokens or justified Tier-3 aliases.

Context-specific structural values remain valid for intrinsic sizing, percentages, grid tracks, responsive calculations, media/container breakpoints, and local geometry with no reusable semantic role. A local value records its purpose when the reason is not self-evident. It must not duplicate or bypass an existing semantic token.

Hardcoded color literals in shared component styles are prohibited. Data visualization with product-specific palettes requires declared contrast and product ownership.

`z-index` values use Tier-2 `dimension.z-index.*` tokens or Tier-3 component aliases; integer literals are prohibited. Custom properties in shared and application styles are either `--ds-*` tokens or documented Tier-3 aliases; ad-hoc custom properties are prohibited. Inline `style` props carry only values computed at runtime, such as pointer coordinates or measured sizes.

### 3.3 Selector and theme isolation

Shared selectors use a documented `scnx-` class/data contract or locally scoped CSS Modules. Classes in an application's global (non-module) stylesheets use the `scnx-<app>-` namespace, for example `.scnx-hris-card`. Shared resets and base element rules live below a declared composition root.

Selectors contain no ID selectors, no type-qualified classes such as `button.card`, at most specificity `0,4,0`, at most three compound selectors, and at most two levels of nesting.

Public multi-brand themes use `[data-scnx-theme="<theme-id>"][data-scnx-resolved-mode="<mode>"]`. A separate `:root` compatibility stylesheet may serve a single-brand document and is excluded from multi-brand and federated support. Theme portals mount inside the originating theme container. Shadow DOM is outside the v1 UI Platform contract.

`@layer` controls precedence and never substitutes for selector scope.

### 3.4 Cascade layers

An application entry that consumes UI Platform CSS declares this exact order. Other applications may omit layers they do not use but keep the relative order of the layers they declare:

```css
@layer reset, tokens, base, components, recipes, utilities, overrides;
```

- `reset`: scoped normalization.
- `tokens`: theme and semantic variables.
- `base`: scoped element defaults.
- `components`: Sass/CSS component rules.
- `recipes`: generated Panda recipe rules.
- `utilities`: token-bound single-purpose helpers.
- `overrides`: explicit consumer composition overrides.

UI Platform declarations outside these layers fail the release gate. Additional layers require a revision of this standard.

`!important` is prohibited in tokens and UI Platform components. A narrowly defined accessibility or visibility utility may use it when its override contract is documented and tested.

### 3.5 CSS delivery

A shared library declares CSS assets through package exports. The UI Platform v1 contract publishes one aggregate component stylesheet and explicit theme stylesheets. A standalone shell or federation host composition root imports each required asset once. Component JavaScript and remotes do not import duplicate CSS side effects.

Per-component CSS subpaths are outside the UI Platform v1 contract.

### 3.6 Responsive and directional layout

Reusable components prefer intrinsic sizing, flex/grid, logical properties, and container queries where the component's behavior depends on its container. Application layouts may use viewport media queries. Supported components pass the declared 320 CSS px reflow scenario when WCAG 2.2 SC 1.4.10 applies.

Physical left/right properties require a justified non-directional use. Direction-aware spacing and positioning use logical properties.

### 3.7 Payload and runtime budgets

Every budget records:

- application or library import scenario;
- raw, minified, gzip, Brotli, or parsed representation;
- measurement tool and version;
- environment/device class;
- approved baseline and regression threshold.

A fixed enterprise-wide CSS byte limit has no authority without those fields. Runtime evidence names the interaction and records style recalculation, layout, paint, CLS, or INP where applicable.

### 3.8 Motion

Motion uses semantic duration/easing tokens and honors `prefers-reduced-motion`. Structural transitions may animate dimensions when the interaction requires them. Their implementation includes interruption, completion-event, timeout fallback, and cleanup tests. Browser traces determine whether layout work is acceptable.

### 3.9 Focus indicators

Every focusable element shows a `:focus-visible` indicator drawn with `outline`, using tokenized width, offset, and color. A shadow may add emphasis but never replaces the outline, because forced-colors mode computes `box-shadow` as `none`. Under `@media (forced-colors: active)` the outline uses a system color such as `Highlight` or `CanvasText`. The indicator meets WCAG 2.2 SC 1.4.11 non-text contrast against adjacent colors.

## 4. Exceptions

A charting, canvas, or vendor integration may use a local adapter when it cannot consume the normal token or selector contract. The adapter must isolate its selectors, document its inputs, provide required accessibility behavior, and include a removal or migration condition.

## 5. Enforcement Mechanism

- Stylelint and source analysis check prohibited shared color literals, integer `z-index`, ad-hoc custom properties, unscoped shared selectors, ID and type-qualified selectors, specificity above `0,4,0`, more than three compound selectors or two nesting levels, layer placement, and `!important` policy.
- Producer tests verify generated Sass/Panda parity and layer ownership.
- Packed browser consumers verify exports, computed values, theme isolation, portal scope, and consumer overrides.
- Federation fixtures assert one aggregate component stylesheet hash and one instance of each selected theme asset under both remote load orders.
- A forced-colors browser fixture asserts a visible outline on every focusable supported component.
- Payload reports enforce only scenario-defined baselines and thresholds.

Rules become release gates when their configured checks run in CI. Missing required checks fail stable promotion.
