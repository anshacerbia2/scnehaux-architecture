---
doc_meta:
  id: STD-E012
  title: Enterprise Frontend Styling Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Enterprise Frontend Styling Standard (STD-E012)

---

## 1. Objective & Scope

This standard defines the framework-agnostic styling guidelines, responsive design constraints, z-index context scales, and transition engine rules for all browser-executed applications and component libraries built within the Scnehaux enterprise.

It guarantees that user interfaces are visually cohesive, highly responsive, performance-optimized, and structured consistently across all frontend applications.

---

## 2. Styling Architecture & Recommended Frameworks

The recommended styling stack for all applications and component libraries comprises **Sass (SCSS)** and **Tailwind CSS**. All interfaces must be built using these engines under strict architectural constraints.

### 2.1 CSS Architecture Decision Matrix
To guide developers in selecting the appropriate styling approach, all frontend applications must adhere to the following styling decision matrix:

| Styling Approach | Authorizations & Restrictions | Target Use Case |
|---|---|---|
| **Design Tokens** | **ALWAYS** mandatory. No hardcoded hex colors, arbitrary spacing units, or custom font sizes are allowed. All visual properties must reference design tokens. | Color, typography, spacing, border-radius, z-indices. |
| **Utility Classes** | **ALLOWED** for layout structure, page-level assembly, and rapid composing of UI configurations. Arbitrary Tailwind classes (e.g. `w-[245px]`) are prohibited. | Layout structures, flexbox alignments, responsive spacing. |
| **Inline Styles** | **RARE**. Restricted to dynamic coordinates calculated by JavaScript (e.g. tracking mouse positions, drag-and-drop coordinates, or canvas heights). Static design styling via `style` attributes is prohibited. | JavaScript-calculated runtime dimensions and coordinates. |
| **`!important` Rule** | **FORBIDDEN** on component-level declarations. Allowed ONLY on system utility helpers (e.g. screen reader utilities or visibility states). | Screen readers, absolute visibility overrides. |


### 2.2 Sass (SCSS) & CSS Modules Standard
- **SCSS Modules (Preferred)**: File names must end with `.module.scss` (e.g., `Card.module.scss`). Classes inside modules are auto-scoped by default to prevent naming collisions.
- **Global (Non-Module) SCSS**: Global stylesheets (with `.scss` extension) are permitted for base layout foundations, generic normalizations, and global resets.
- **App-Namespaced Naming Convention**: To prevent style collisions in federated applications, all classes declared in global (non-module) SCSS must be namespaced using the following naming structure:
  ```css
  .scnx-[app-name]-[class-name]
  ```
  *Examples*: `.scnx-hris-card`, `.scnx-iam-modal`, `.scnx-sales-button`. Using generic, un-namespaced classes (such as `.card` or `.modal`) in global SCSS is strictly prohibited.
- **Global Selector Encapsulation**: Declaring `:global` rules inside an SCSS Module is restricted to third-party styles that cannot be styled using props.

### 2.3 Tailwind CSS Standard
- **Utility-First Assembly**: Tailwind CSS is approved for rapid layout assembly and application-level composition layers.
- **Token Consistency**: All Tailwind classes must map to configured design tokens. Arbitrary values (e.g., `bg-[#3f51b5]`, `w-[320px]`) are prohibited.
- **Class Merging**: Long class strings must be formatted cleanly, utilizing helpers like `clsx` or `tailwind-merge` for conditional class joining.

### 2.4 Responsive Layout Strategy
- **Mobile-First Breakpoints**: Layout styles must use mobile-first styling. Mobile viewports represent the base styles, and desktop configurations must be applied progressively using media queries or Tailwind prefix utilities (e.g., `md:flex-row`).
- **Fluid Grid Systems**: Grids and flex structures must use fluid percentages or CSS Grid layouts with relative units (`fr`, `em`, `rem`) instead of hardcoded pixel widths (`px`).

### 2.5 CSS Scoping & Naming Convention
- **Core Library Class Prefixing**: Reusable components in the core design system library must use the namespace prefix `scnx-` (e.g., `.scnx-btn`, `.scnx-card`) to separate system-level styles from application-level styles.
- **BEM Methodology**: Components styled using global SCSS must follow BEM (Block, Element, Modifier) rules:
  - **Block**: The parent component class (e.g., `.scnx-hris-card`).
  - **Element**: Parts of the component, prefixed with double underscores (e.g., `.scnx-hris-card__header`).
  - **Modifier**: State variations, prefixed with double hyphens (e.g., `.scnx-hris-card--compact`).
- **Scoping Selection Matrix**:
  | Strategy | Pros | Cons | Target Use Case |
  |---|---|---|---|
  | **SCSS Modules** | Automatic scoping, zero collisions, CSS nesting | Requires bundler setup | Application-specific components & features |
  | **Global BEM SCSS** | Explicit names, easily debuggable in DevTools | Verbose classes, manual discipline | Reusable core design system libraries |
  | **Shadow DOM** | Native runtime styling encapsulation | Complex to integrate, high overhead | Independent Web Components |

### 2.6 Inverted Triangle CSS (ITCSS) Principles
Global SCSS stylesheets are encouraged to adopt the core principles of the **ITCSS (Inverted Triangle CSS)** methodology to organize styles logically by specificity. This helps prevent specificity wars and maintains predictability.

While the exact directory structure below is **not strictly enforced** (projects may adapt it to fit framework-specific setups or domain-driven designs), developers should conceptually group and import stylesheets in order of increasing specificity:
1. **Settings**: Global variables, design tokens, typography scales, and color maps (generates no output CSS).
2. **Tools**: Globally useful mixins, helper functions, and keyframe animations (generates no output CSS).
3. **Generic**: CSS resets, browser normalizations, and box-sizing overrides.
4. **Elements**: Bare HTML element selectors without class names (e.g., `body`, `button`, `input`).
5. **Objects**: Non-visual layout wrappers, grid systems, and flex container structures.
6. **Components**: Class-based, visual designs for independent UI elements (e.g., cards, dialogs, buttons).
7. **Utilities**: High-specificity utility helpers and overrides (e.g., `.sr-only`, `.truncate`).

**Recommended (Non-Restrictive) ITCSS Directory Blueprint**:
```text
styles/
├── 1-settings/
│   ├── _tokens.scss          <-- font-sizes, spacing values
│   └── _colors.scss          <-- color channels, themes
├── 2-tools/
│   ├── _mixins.scss          <-- screen-reader, flex helpers
│   └── _functions.scss       <-- rem-conversion functions
├── 3-generic/
│   ├── _reset.scss           <-- global browser reset
│   └── _normalize.scss       <-- box-sizing normalization
├── 4-elements/
│   ├── _base.scss            <-- body, html tag styling
│   └── _typography.scss      <-- bare heading structures (h1, h2)
├── 5-objects/
│   ├── _layout.scss          <-- page wrapper structures
│   └── _grid.scss            <-- general grid layouts
├── 6-components/
│   ├── _card.scss            <-- scnx-[app]-card styles
│   └── _button.scss          <-- scnx-[app]-button styles
└── 7-utilities/
    ├── _helpers.scss         <-- single-purpose display helpers
    └── _overrides.scss       <-- absolute visual overrides
```

### 2.7 CSS Specificity & Cascade Layers (`@layer`)
- **Cascade Layer Order**: Custom styles must be declared within CSS Cascade Layers (`@layer`) to manage specificity deterministically and prevent specificity conflicts. The layer order must be declared at the application entry point exactly as:
  ```css
  @layer reset, tokens, base, components, utilities, overrides;
  ```
- **Layer Allocation Rules**:
  - `reset`: Base normalizations and global resets (e.g., box-sizing).
  - `tokens`: CSS custom properties / design tokens.
  - `base`: Bare HTML tag selectors (e.g., `body`, `h1`).
  - `components`: Core component styles (e.g., `.scnx-card`).
  - `utilities`: Single-purpose helper classes (e.g., `.truncate`, `.sr-only`).
  - `overrides`: Downstream application overrides.

### 2.8 Specificity Enforcement & `!important` Policy
- **Usage Restrictions**: The `!important` flag is strictly restricted to prevent cascading bugs. It is governed by the following rules:
  | Style Context | Permission | Rationale |
  |---|---|---|
  | **Utility Classes** (e.g., `.hidden`, `.sr-only`) | ✅ Permitted | Utilities must always override component-level layout values. |
  | **Reset / Normalizations** | ✅ Permitted | Allowed only within the `@layer reset` context for cross-browser normalization. |
  | **Component-Specific Styles** | ❌ Prohibited | Encourages brittle styles and breaks composition patterns. |
  | **Theme / Design Tokens** | ❌ Prohibited | Tokens must be configurable and overrideable by themes. |

### 2.9 Style Centralization vs. Colocation Strategy
To maintain a clean and structured codebase, styles must follow a hybrid model of centralization and colocation:
- **Centralized Core Foundations**: Global configurations, design tokens, utility classes, animations, global resets, and general mixins (ITCSS Layers 1 to 4, and helper objects/utilities) must be centralized in a single shared directory or a dedicated npm package (e.g., a shared theme package `@scnx/theme` in a monorepo, or `src/styles/` at the root of a standalone project). This serves as the single source of truth for the styling variables and configs.
- **Colocated Component Styles**: Component-specific styles (e.g., SCSS Modules) must be decentralized and colocated in the exact same directory as the component code file (e.g., `/components/Card/Card.tsx` and `/components/Card/Card.module.scss`). Colocation ensures that components are highly encapsulated, self-contained, and easily distributable under Module Federation. Storing component-specific styles in a centralized global directory is strictly prohibited.

---

## 3. Global Styling Quality Guidelines

### 3.1 Z-Index Scale
- Stack contexts must use the centralized, semantic z-index scale to prevent layout overlap issues:
  ```css
  --ds-z-index-deep: -1;
  --ds-z-index-base: 0;
  --ds-z-index-nav: 100;
  --ds-z-index-overlay: 500;
  --ds-z-index-modal: 1000;
  --ds-z-index-toast: 2000;
  ```
- Declaring arbitrary z-index values (such as `z-index: 9999`) is prohibited. All layers must map to the semantic tokens.

### 3.2 Motion & Animation Performance
- High-performance visual transitions must run on GPU-accelerated properties (`transform` and `opacity` only). Transitions animating layout dimensions (such as `height`, `width`, `margin`) are prohibited on high-frequency rendering paths to prevent layout thrashing.
- Transition timings and easing curves must use the design tokens (e.g., `var(--ds-motion-easing-standard)`).

---

## 4. Compliance & Enforcement

- **Linting Rules**: CI/CD pipelines must enforce style rules using stylelint configuration suites.
- **Visual Regression Checks**: Design system modifications must pass visual regression checks inside the build pipeline before release to prevent visual bugs.
- **Waiver Protocol**: Custom styling engine integrations or deviations from the design token system require a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
