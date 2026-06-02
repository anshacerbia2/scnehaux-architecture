---
doc_meta:
  id: STD-GLB-FE-007
  title: Enterprise Frontend Styling Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-31
---

# Enterprise Frontend Styling Standard (STD-GLB-FE-007)

---

## 1. Objective & Scope

This document establishes the **Supreme Styling Governance** for all browser-executed applications, Micro-Frontends (MFEs), and component libraries within the Scnehaux enterprise.

It dictates the absolute boundaries for styling engines, layout determinism, zero-waste rendering pipelines, and tokenized semantic abstractions. By enforcing a **Hard Boundary for Separation of Concerns (UI ≠ State ≠ Side Effects ≠ Domain Logic)**, this standard ensures that all interfaces are predictable, observable, and strictly component-driven.

**Performance is Everything**: This is the primary mandate. Any styling implementation that introduces implicit cascading, unmanaged global state, runtime parsing overhead, layout thrashing, or non-tokenized arbitrary values is considered a critical architectural violation and will trigger a **Hard Block (auto-rejection)** in CI/CD pipelines.

---

## 2. Design Principles

All frontend styling must strictly adhere to the Supreme Frontend Governance principles. Deviation from these principles is considered a critical architectural violation.

### 2.1 Determinism Over Cleverness
Output must be 100% predictable from input. Clever but unpredictable styling logic is strictly forbidden. Visual state must not rely on hidden side-effects, implicit global cascading, or unstructured DOM mutations. A component's rendered output must be a pure, deterministic reflection of its explicit data props and injected semantic tokens.

### 2.2 Zero Waste System (Performance is Everything)
Every CSS declaration must justify its cost (CPU, Memory, Network, Layout).
- **No dead CSS**: Unused styles must not be shipped to production.
- **No unnecessary renders**: Styling must not trigger JavaScript recalculations during the critical rendering path.
- **No unnecessary DOM**: Avoid "trash DOM" wrappers (e.g., redundant `<div>` tags) solely for the purpose of achieving layout alignment.

### 2.3 Semantic Abstraction (Separation of Concerns)
UI elements consume **Intent**, not **Physical Coordinates**. Hardcoding raw hex values, arbitrary pixel dimensions, or bezier curves is strictly prohibited. 

All styling across the enterprise MUST bind strictly to the semantic layer of the **Scnehaux UI Platform Design Tokens**. Developers must strictly adhere to the established token taxonomies and OKLCH color spaces defined in:
- [STD-UIP-TKN-001 (Design Tokens)](../../ui-platform/design-tokens/STD-UIP-TKN-001-design-tokens.md)
- [STD-UIP-TKN-002 (Consumption Governance)](../../ui-platform/design-tokens/STD-UIP-TKN-002-consumption-governance.md)
- [ADR-UIP-TKN-003 (Token Taxonomy & Naming Convention)](../../../05-decisions/ui-platform/design-tokens/ADR-UIP-TKN-003-token-taxonomy-and-naming-convention.md)

### 2.4 Observability & Strict Encapsulation
Styles must be strictly isolated. Cross-component styling contamination and "specificity wars" are architectural failures. Every visual regression must be traceable to a specific, isolated component boundary.

---

## 3. Normative Rules

### 3.1 Styling Architecture & Recommended Frameworks

The recommended polyglot styling stack for all applications and component libraries comprises **Zero-Runtime Styling (e.g., Panda CSS, Vanilla Extract)**, **Utility-First Frameworks (e.g., Tailwind, UnoCSS)**, and **CSS Preprocessors (e.g., Sass, PostCSS)**. All interfaces must be built using one of these paradigms under strict architectural constraints.

#### Styling Strategy Decision Matrix

| Styling Approach | Authorizations & Restrictions | Target Use Case |
|---|---|---|
| **Zero-Runtime Styling** | **PRIMARY MANDATE**. Compiles to static Atomic CSS via AST scanning. Guarantees zero runtime overhead while providing type-safe macros. | UI Component Libraries, Core Design Systems, and High-Performance Portals. |
| **Utility-First Frameworks** | **ALLOWED** for rapid layout assembly and application-level composition layers in isolated consumer applications. Arbitrary utility values (e.g., `w-[245px]`) are forbidden. | Isolated Feature SPAs, rapid composition. |
| **CSS Modules (via Preprocessors)** | **APPLICATION OVERRIDES**. Recommended for consumer applications requiring complex structural overrides or custom designs where atomic utilities are insufficient. | Application-specific features, design system overrides. |
| **Global BEM Stylesheets** | **RESTRICTED**. Permitted only for application-level global layouts, typography foundations, and CSS resets. Risk of specificity wars. | Application foundations, legacy migrations. |
| **Shadow DOM** | **DISCOURAGED**. Native encapsulation comes with heavy styling interoperability issues and framework integration complexity. | Independent Web Components. |
| **Design Tokens** | **ALWAYS MANDATORY**. No hardcoded hex colors, arbitrary spacing units, or custom font sizes are allowed. All visual properties must reference the **Scnehaux UI Platform** design tokens as governed by [STD-UIP-TKN-001 (Design Tokens)](../../ui-platform/design-tokens/STD-UIP-TKN-001-design-tokens.md). | Color, typography, spacing, border-radius, z-indices. |
| **Inline Styles** | **RARE**. Restricted strictly to dynamic coordinates calculated by JavaScript (e.g., tracking mouse positions or canvas heights). Static styling via `style` attributes is prohibited. | JavaScript-calculated runtime dimensions. |
| **`!important` Rule** | **FORBIDDEN** on component-level declarations. Allowed ONLY on system utility helpers (e.g., `.sr-only`). | Screen readers, absolute visibility overrides. |

### 3.2 Framework-Specific Constraints

#### Zero-Runtime Styling (e.g., Panda CSS, Vanilla Extract)
- **Colocated Macros**: Styling must be authored using type-safe macros (e.g., `css()`, `cva()`) colocated directly within the `.tsx` component files.
- **Static Extraction**: The engine must be configured to statically analyze the AST and extract atomic classes at build-time. Runtime injection is prohibited.

#### Utility-First Framework Standard (e.g., Tailwind CSS, UnoCSS)
- **Utility-First Assembly**: Utility-first styling frameworks are permitted for rapid layout assembly and application-level composition layers.
- **Token Consistency**: All utility classes must map strictly to configured enterprise design tokens. Arbitrary JIT values (e.g., `bg-[#3f51b5]`, `h-[320px]`) are prohibited.
- **Class Merging**: Long class strings must be formatted cleanly using deterministic merging functions (e.g., `tailwind-merge`) to prevent specificity conflicts during conditional rendering.

#### CSS Preprocessors & CSS Modules Standard
- **CSS Modules (Preferred)**: File names must end with `.module.css` or `.module.scss` (e.g., `Card.module.scss`). Classes inside modules are auto-scoped by default to prevent naming collisions.
- **Global (Non-Module) Stylesheets**: Global stylesheets (with `.css` or `.scss` extension) are permitted for base layout foundations, generic normalizations, and global resets.
- **Global Selector Encapsulation**: Declaring `:global` rules inside a CSS Module is restricted to third-party styles that cannot be styled using props.

#### CSS Scoping & Naming Convention
- **Core Library Class Prefixing**: Reusable components in the core design system library must use the namespace prefix `scnx-` (e.g., `.scnx-btn`, `.scnx-card`) to separate system-level styles from application-level styles.
- **Global Stylesheet Namespacing**: To prevent style collisions in federated applications, all classes declared in global (non-module) stylesheets must be namespaced using the following naming structure:
  ```css
  .scnx-[app-name]-[class-name]
  ```
  *Examples*: `.scnx-hris-card`, `.scnx-iam-modal`. Using generic, un-namespaced classes (such as `.card` or `.modal`) in global stylesheets is strictly prohibited.
- **Global Component Structure**: When writing complex components in global stylesheets, developers are encouraged to use a structured methodology like BEM (`.block__element--modifier`) to indicate relationships, provided the application namespace is maintained (e.g., `.scnx-hris-card__header`).
- **CSS Modules Naming**: Inside CSS Modules, developers must use short, semantic, locally-scoped class names (e.g., `.root`, `.header`, `.title`, `.isActive`). Because the bundler automatically generates collision-free hashes (e.g., `Card_header__3aX9`), manually applying BEM or global namespaces inside a CSS Module is a redundant anti-pattern and is prohibited.

### 3.3 Specificity, Cascade & Colocation Strategy

#### Inverted Triangle CSS (ITCSS) Principles
Global stylesheets are encouraged to adopt the core principles of the **ITCSS (Inverted Triangle CSS)** methodology to organize styles logically by specificity. This helps prevent specificity wars and maintains predictability.

While the exact directory structure below is **not strictly enforced** (projects may adapt it to fit framework-specific setups or domain-driven designs), developers should conceptually group and import stylesheets in order of increasing specificity:
1. **Settings**: Global variables, design tokens, typography scales, and color maps (generates no output CSS).
2. **Tools**: Globally useful mixins, helper functions, and keyframe animations (generates no output CSS).
3. **Generic**: CSS resets, browser normalizations, and box-sizing overrides.
4. **Elements**: Bare HTML element selectors without class names (e.g., `body`, `button`, `input`).
5. **Objects**: Non-visual layout wrappers, grid systems, and flex container structures.
6. **Components**: Class-based, visual designs for independent UI elements (e.g., cards, dialogs, buttons).
7. **Utilities**: High-specificity utility helpers and overrides (e.g., `.sr-only`, `.truncate`).

```text
styles/
├── 1-settings/
│   ├── tokens.css            <-- font-sizes, spacing values
│   └── colors.css            <-- color channels, themes
├── 2-tools/
│   ├── mixins.css            <-- screen-reader, flex helpers
│   └── functions.css         <-- rem-conversion functions
├── 3-generic/
│   ├── reset.css             <-- global browser reset
│   └── normalize.css         <-- box-sizing normalization
├── 4-elements/
│   ├── base.css              <-- body, html tag styling
│   └── typography.css        <-- bare heading structures (h1, h2)
├── 5-objects/
│   ├── layout.css            <-- page wrapper structures
│   └── grid.css              <-- general grid layouts
├── 6-components/
│   ├── card.css              <-- scnx-[app]-card styles
│   └── button.css            <-- scnx-[app]-button styles
└── 7-utilities/
    ├── helpers.css           <-- single-purpose display helpers
    └── overrides.css         <-- absolute visual overrides
```

#### CSS Specificity & Cascade Layers (`@layer`)
- **Cascade Layer Order**: Custom styles must be declared within CSS Cascade Layers (`@layer`) to manage specificity deterministically and prevent specificity conflicts. The layer order must be declared at the application entry point exactly as:
  ```css
  @layer reset, tokens, base, components, utilities, overrides;
  ```
- **Layer Governance**: Additional cascade layers (e.g., `@layer hacks;`) are strictly prohibited unless explicitly approved by the Architecture Review Board. The enterprise standard layers are:
  - `reset`: Base normalizations and global resets (e.g., box-sizing).
  - `tokens`: CSS custom properties / design tokens.
  - `base`: Bare HTML tag selectors (e.g., `body`, `h1`).
  - `components`: Core component styles (e.g., `.scnx-card`).
  - `utilities`: Single-purpose helper classes (e.g., `.truncate`, `.sr-only`).
  - `overrides`: Downstream application overrides.

#### Specificity Enforcement & `!important` Policy
- **Usage Restrictions**: The `!important` flag is strictly restricted to prevent cascading bugs. It is governed by the following rules:
  | Style Context | Permission | Rationale |
  |---|---|---|
  | **Utility Classes** (e.g., `.hidden`, `.sr-only`) | ✅ Permitted | Utilities must always override component-level layout values. |
  | **Reset / Normalizations** | ✅ Permitted | Allowed only within the `@layer reset` context for cross-browser normalization. |
  | **UI Platform Components** | ❌ Prohibited | Core components must not force styles using `!important`. This guarantees downstream applications can override them cleanly without specificity wars. |
  | **Theme / Design Tokens** | ❌ Prohibited | Tokens must be configurable and overrideable by themes. |

#### Style Centralization vs. Colocation Strategy
To maintain a clean and structured codebase, styles must follow a hybrid model of centralization and colocation:
- **Centralized Core Foundations**: Global configurations, design tokens, utility classes, animations, global resets, and general mixins (ITCSS Layers 1 to 4, and helper objects/utilities) must be centralized in a single shared directory or a dedicated npm package (e.g., a shared theme package `@scnx/theme` in a monorepo, or `src/styles/` at the root of a standalone project). This serves as the single source of truth for the styling variables and configs.
- **Colocated Component Styles**: Component-specific styles (e.g., CSS Modules) must be decentralized and colocated in the exact same directory as the component code file (e.g., `/components/Card/Card.tsx` and `/components/Card/Card.module.css`). Colocation ensures that components are highly encapsulated, self-contained, and easily distributable under Module Federation. Storing component-specific styles in a centralized global directory is strictly prohibited.

### 3.4 Responsive Layout Strategy

- **Container Queries First**: Container queries (`@container`) should be preferred for reusable components to guarantee portability across different layouts and Micro-Frontends. Viewport media queries remain valid and necessary for application-level layouts.
- **Mobile-First Breakpoints**: Global layout scaffolds (e.g., page grids, navigation shells) must use mobile-first styling. Desktop configurations must be applied progressively using media queries (`@media`) or Tailwind prefix utilities (e.g., `md:flex-row`).
- **Fluid Grid Systems**: Grids and flex structures must use fluid percentages or CSS Grid layouts with relative units (`fr`, `em`, `rem`) instead of hardcoded pixel widths (`px`).

### 3.5 Global Styling Quality Guidelines

#### CSS Code Quality Budgets
To protect rendering performance and maintain predictable specificity, all applications must enforce the following strict CSS budgeting metrics via automated CI/CD static analysis (e.g., `stylelint`):

```yaml
css_budget:
  critical_css_brotli_kb: 20 # Measured per independently deployable MFE/Route
  route_css_brotli_kb: 50 # Measured per independently deployable MFE/Route
  max_selector_depth: 3 # e.g., .card > .header > .title (depth of 3 allowed)
  max_nesting_depth: 2 # e.g., .a { .b { .c {} } } (this is depth 3, so it will fail)
  max_specificity: "0,4,0" # No IDs, Max 4 Classes/Attributes (e.g., .card[data-state="open"]:hover:focus-visible), No Tags

forbidden_patterns:
  - id_selectors: true # e.g., #header
  - tag_class_combinations: true # e.g., button.btn-primary
  - universal_descendants: true # e.g., .container *
  - chained_descendants_over_3: true # e.g., .a .b .c .d
```

- **Maximum Specificity (`0,4,0`)**: Selectors must never use IDs (`#id`), must not exceed 4 class/attribute combinations (allowing for complex accessibility states like `.card[data-state="open"]:hover:focus-visible`), and must avoid raw HTML tag selectors where possible.
- **Forbidden Patterns**: Tag-class combinations (e.g., `button.card`) destroy component portability and are strictly prohibited. Style components by contract (e.g., `.card`, `.btn`), not by DOM structure. Universal descendant selectors (e.g., `.container *`) cause massive layout recalculation costs and are forbidden (note: root-level `* { box-sizing: border-box; }` resets are standard and permitted).

#### Rendering Cost Governance & Runtime Monitoring
- **Real User Monitoring (RUM)**: Critical applications must actively monitor and budget CSS performance in production environments, specifically tracking Style Recalculation time, Layout Shifts (CLS), and Interaction to Next Paint (INP). This telemetry tracking must be orchestrated in accordance with [STD-GLB-FE-006 (Core Web Vitals Tracking)](./STD-GLB-FE-006-observability.md#core-web-vitals-tracking) and adhere to the threshold budgets mandated by [STD-GLB-FE-004 (Enforcement Mechanism)](./STD-GLB-FE-004-performance.md#5-enforcement-mechanism).
- **Zero Layout Thrashing**: Repeated synchronous DOM measurement inside rendering loops (e.g., `for` loops reading `el.offsetHeight` and writing `el.style.height`) causes severe performance degradation and must be avoided, as strictly governed by [STD-GLB-FE-004 (Zero Layout Thrashing)](./STD-GLB-FE-004-performance.md#zero-layout-thrashing-60fps-render-guarantee). All imperative style mutations must batch DOM reads before DOM writes, synchronized with the browser's paint cycle via `requestAnimationFrame` (rAF).
- **Safe Measurement**: For continuous tracking, dimensions must be observed asynchronously using `ResizeObserver` or `IntersectionObserver`. Synchronous reads (e.g., reading `getBoundingClientRect()` or `offsetHeight`) are permitted when driven by distinct user interactions (such as rapid clicks interrupting an accordion to snap to a current pixel) or deliberate forced reflows, provided they remain outside of continuous high-frequency rendering loops (like `onScroll` or `requestAnimationFrame`).

#### CSS Variable Governance, Theme Routing & Ownership
- **Strict Variable Scoping**: The manual creation of ad-hoc CSS variables (e.g., `--my-custom-color`) is prohibited. All variables must be systematically generated and injected via the UI Platform's Design Token pipeline.
- **Token Ownership & Lifecycle**: The creation, modification, and approval of semantic tokens are exclusively owned by the **Design System Team / Token Review Board**. Application engineers are strictly consumers. The token lifecycle must be explicitly managed through phases: *Proposed → Approved → Active → Deprecated → Removed*.
- **Theme Switching**: Applications must execute theme switching (Light/Dark/High Contrast) at the root level (e.g., `data-theme="dark"` on `<html>`). The hierarchical architecture of tokens (Core → Semantic → Component) is strictly delegated to and governed by [ADR-UIP-TKN-003 (Token Taxonomy & Naming Convention)](../../../05-decisions/ui-platform/design-tokens/ADR-UIP-TKN-003-token-taxonomy-and-naming-convention.md).

#### Z-Index Scale
- Stack contexts must use a centralized, semantic z-index scale to prevent layout overlap issues. The enterprise mandates a standardized semantic layering model (e.g., *Deep, Base, Nav, Overlay, Modal, Toast*).
- **Abstraction Rule**: Frontends must consume these layers via the Enterprise Design Tokens. Declaring arbitrary z-index values (such as `z-index: 9999`) in application code is strictly prohibited.

#### Motion & View Transition Performance
- **GPU Acceleration**: High-performance visual transitions should prioritize GPU-accelerated properties (`transform` and `opacity`). Animating layout dimensions (such as `height`, `width`, `margin`) triggers costly layout reflows and should be minimized, but is permitted for specific structural behaviors (e.g., accordions, collapsible panels) where `transform` scaling is insufficient.
- **Physics-Based Interaction**: For complex micro-interactions (e.g., drag, swipe, interruptible gestures), static time-based CSS transitions (`transition: 300ms`) are discouraged. Developers should prefer Physics-based motion (Spring dynamics) to maintain organic momentum.
  > *Note: The runtime rendering constraints for executing physics loops (via `requestAnimationFrame`) without causing layout thrashing or dropped frames are governed strictly by [STD-GLB-FE-004 (Zero Layout Thrashing)](./STD-GLB-FE-004-performance.md#zero-layout-thrashing-60fps-render-guarantee).*
- **View Transition API**: Modern SPA route transitions and shared element transitions should prefer the native **View Transition API** where browser support and framework constraints permit. Heavy JavaScript-based animation wrappers for routing are discouraged.
- **Tokenized Curves**: Transition timings and easing curves must map to the centralized motion design tokens rather than hardcoded bezier curves.

### 3.7 Accessibility (a11y) Styling Standard

> **Document Authority Notice**: Comprehensive accessibility mandates (including WCAG compliance tiers, Focus Engineering, Reduced Motion, and Forced Colors Mode) have been consolidated into **[STD-GLB-FE-009 (Accessibility & Internationalization)](./STD-GLB-FE-009-accessibility-i18n.md)**.
> 
> All UI styling architectures must strictly comply with the universal access principles and contrast constraints defined in that authoritative standard.

---

## 4. Exceptions
Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk. 

### Exception to "Zero-Runtime Mandate & Token Mapping" (Rules 3.1 & 3.2)
- **Condition for Deviation**: You are integrating an imperative third-party charting library (e.g. D3.js, ECharts) or a legacy web component that injects its own scoped stylesheets and cannot natively consume CSS variables.
- **Mandatory Alternative**: The non-compliant styles must be forcefully isolated. The widget must be wrapped inside a Shadow DOM boundary or encapsulated using a CSS `all: initial` reset to guarantee zero leakage into the host application layout.

---

## 5. Enforcement Mechanism

- **AST Static Analysis**: Build pipelines will execute static analysis on the Abstract Syntax Tree (AST) to detect and block hardcoded colors, arbitrary pixel values, and untokenized strings in styled macros.
- **Linting Rules**: CI/CD pipelines must enforce style rules using strict linter configuration suites (e.g., `eslint-plugin-panda`, `stylelint`). Violations will trigger a Hard Block (Exit 1).
- **Visual Regression Checks**: Core system modifications must pass pixel-perfect visual regression tests inside the CI pipeline before release to prevent visual bugs.
- **Waiver Protocol**: Custom styling engine integrations or deviations from the design token system require a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
