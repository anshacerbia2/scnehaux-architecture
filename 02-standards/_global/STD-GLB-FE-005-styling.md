---
doc_meta:
  id: STD-GLB-FE-005
  title: Enterprise Frontend Styling Standard
  owner: Principal Frontend Architect
  version: 2.1.0
  status: approved
  classification: restricted
  governed_by: [GDC-000]
  authorized_by: [ADR-GLB-FE-010]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-20
---

# Enterprise Frontend Styling Standard (STD-GLB-FE-005)

> **Authorization:** ADR-GLB-FE-010 authorizes this revision; implementation conformance still requires verification.

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

Reusable components prefer intrinsic sizing, flex/grid, logical properties, and container queries where the component's behavior depends on its container. Application layouts may use viewport media queries. Supported components pass the declared 320 CSS px reflow scenario when WCAG 2.2 SC 1.4.10 applies. The sizing rules that keep it are in §3.10.

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

### 3.10 Intrinsic sizing and reflow

Added in 2.1.0. identity-experience #57 (`TDD-identity-experience-003` 1.29.0 §Layout) fixed a shared `Panel` that set `container-type: inline-size` with no container query. A panel sized by its content was laid out about 50px wide, and its text ran one character per line. A test of each page as it loaded did not see it: the panels that collapsed were the ones a person opens.

- **No `container-type` without a container query that needs it.** `container-type: inline-size` "Applies layout containment, style containment, and inline-size containment to the principal box" [R1]. Under inline-size containment "the inline-axis intrinsic sizes of the principal box are determined as if the element had no content" [R1]. An element sized by its content then shrinks to its padding and border, because its fit-content size is "clamp(min-content size, stretch-fit size, max-content size)" [R2]. A component that needs a container query sets containment on an element of its own that its parent sizes, never on one that may be sized by its content.
- **Flex and grid children that hold text set `min-inline-size: 0`.** A flex item's automatic minimum "is its content-based minimum size" [R5], and a grid item's is "the content-based minimum size" in the common case [R6]. The grid note warns: "A content-based minimum width could result in a large table or large image stretching the size of the entire content area" [R6]. With `min-inline-size: 0` a long table or string stays inside the row.
- **Long unbreakable strings wrap with `overflow-wrap: anywhere`.** It lets "An otherwise unbreakable sequence of characters" break, and its soft wrap opportunities "are considered when calculating min-content intrinsic sizes" [R3], so an identifier, address or reference does not hold its container wider than the room it has. `break-word` is not enough: its opportunities "are not considered when calculating min-content intrinsic sizes" [R3].
- **Tables are the exception: they keep `overflow-wrap: normal` and scroll in their own region.** With `anywhere` a column would narrow to one character instead. WCAG 2.2 SC 1.4.10 excepts "parts of the content which require two-dimensional layout for usage or meaning", and its Note 2 names "data tables (not individual cells)" [R4].
- **No page scrolls sideways at 320 CSS px.** Content is presented "without requiring scrolling in two dimensions for: Vertical scrolling content at a width equivalent to 320 CSS pixels" [R4] (STD-GLB-FE-009 §3.4).

## 4. Exceptions

A charting, canvas, or vendor integration may use a local adapter when it cannot consume the normal token or selector contract. The adapter must isolate its selectors, document its inputs, provide required accessibility behavior, and include a removal or migration condition.

## 5. Enforcement Mechanism

- Stylelint and source analysis check prohibited shared color literals, integer `z-index`, ad-hoc custom properties, unscoped shared selectors, ID and type-qualified selectors, specificity above `0,4,0`, more than three compound selectors or two nesting levels, layer placement, and `!important` policy.
- Producer tests verify generated Sass/Panda parity and layer ownership.
- Packed browser consumers verify exports, computed values, theme isolation, portal scope, and consumer overrides.
- Federation fixtures assert one aggregate component stylesheet hash and one instance of each selected theme asset under both remote load orders.
- A forced-colors browser fixture asserts a visible outline on every focusable supported component.
- A browser layout test enforces §3.10. It lays each covered page out at its supported widths, 320 CSS px included, with long content and with the panels, forms and confirmations a person opens. It fails when the page scrolls sideways, when a panel is narrower than its declared minimum or its container, or when text runs one or two characters per line. `e2e/tests/layout.spec.ts` in identity-experience is the first such test (`TDD-identity-experience-003` 1.29.0 §Layout).
- Payload reports enforce only scenario-defined baselines and thresholds.

Rules become release gates when their configured checks run in CI. Missing required checks fail stable promotion.

## 6. References

- **[R1]** W3C, _CSS Containment Module Level 3_, Working Draft 18 August 2022, accessed 2026-10-20. <https://www.w3.org/TR/css-contain-3/>. §3.1: "Giving an element inline-size containment applies size containment to the inline-axis sizing of its principal box. This means the inline-axis intrinsic sizes of the principal box are determined as if the element had no content." §4.1, `container-type: inline-size`: "Establishes a query container for container size queries on the container’s own inline axis. Applies layout containment, style containment, and inline-size containment to the principal box." Supports §3.10.
- **[R2]** W3C, _CSS Box Sizing Module Level 3_, Working Draft 4 September 2026, accessed 2026-10-20. <https://www.w3.org/TR/css-sizing-3/>. §2.1, fit-content size: "If the available space in a given axis is definite, equal to clamp(min-content size, stretch-fit size, max-content size)". Supports §3.10.
- **[R3]** W3C, _CSS Text Module Level 3_, Candidate Recommendation Draft 14 August 2026, accessed 2026-10-20. <https://www.w3.org/TR/css-text-3/>. §5.4, `anywhere`: "An otherwise unbreakable sequence of characters may be broken at an arbitrary point if there are no otherwise-acceptable break points in the line"; "Soft wrap opportunities introduced by anywhere are considered when calculating min-content intrinsic sizes." `break-word`: "As for anywhere except that soft wrap opportunities introduced by break-word are not considered when calculating min-content intrinsic sizes." Supports §3.10.
- **[R4]** W3C, _Web Content Accessibility Guidelines (WCAG) 2.2_, SC 1.4.10 Reflow (AA), accessed 2026-10-20. <https://www.w3.org/TR/WCAG22/>. "Content can be presented without loss of information or functionality, and without requiring scrolling in two dimensions for: Vertical scrolling content at a width equivalent to 320 CSS pixels"; "Except for parts of the content which require two-dimensional layout for usage or meaning." Note 2: "Examples of content which requires two-dimensional layout are images required for understanding (such as maps and diagrams), video, games, presentations, data tables (not individual cells), and interfaces where it is necessary to keep toolbars in view while manipulating content." Supports §3.6 and §3.10.
- **[R5]** W3C, _CSS Flexible Box Layout Module Level 1_, Candidate Recommendation Draft 14 October 2025, accessed 2026-10-20. <https://www.w3.org/TR/css-flexbox-1/>. §4.5: "To provide a more reasonable default minimum size for flex items, the used value of a main axis automatic minimum size on a flex item whose computed overflow value is non-scrollable is its content-based minimum size". Supports §3.10.
- **[R6]** W3C, _CSS Grid Layout Module Level 2_, Candidate Recommendation Draft 26 March 2025, accessed 2026-10-20. <https://www.w3.org/TR/css-grid-2/>. §6.6: "To provide a more reasonable default minimum size for grid items, the used value of its automatic minimum size in a given axis is the content-based minimum size if all of the following are true"; "A content-based minimum width could result in a large table or large image stretching the size of the entire content area, potentially into an overflow zone, and thereby making lines of text needlessly long and hard to read." Supports §3.10.
