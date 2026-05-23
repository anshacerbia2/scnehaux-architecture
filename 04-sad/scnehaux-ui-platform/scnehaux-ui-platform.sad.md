---
doc_meta:
  id: DOC-S003
  title: Scnehaux UI Platform Software Architecture (SAD)
  owner: Principal UI/UX Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-19
parent_pad: DOC-P002
---

# Scnehaux UI Platform Software Architecture (SAD-003)

---

## 1. Context

The **Scnehaux UI Platform** is the concrete physical styling compiler and component infrastructure that fulfills the logical capabilities defined in the [Scnehaux UI Platform Architecture Platform Document (PAD-002)](../../02-platform/scnehaux-ui-platform/scnehaux-ui-platform.pad.md). 

It provides the physical visual foundation consumed by all frontend portals across the monorepo—including the [Scnehaux IAM Dashboard (SAD-002)](../scnehaux-iam-dashboard/scnehaux-iam-dashboard.sad.md) and the federated ERP Portal. It is developed as a set of isolated packages to guarantee zero runtime visual pollution, maximum build-time optimization, and strict style encapsulation.

### 1.1 Architectural Principles & Core Philosophy

The platform operates at a high performance tier, inheriting and enforcing the global [Enterprise Frontend Performance and Rendering Standard (STD-E006)](../../05-standards/STD-E006-frontend-performance-rendering-standard.md) across all component and compilation layers:

1. **Zero Layout Thrashing (60FPS Render Guarantee)**: The platform prohibits synchronous geometry queries during high-frequency cycles. All dynamic layout adjustments are deferred and batched using `requestAnimationFrame`.
2. **Polymorphic Rendering Safety**: The platform prefers the dynamic `as` prop pattern for high-performance polymorphism. The React `asChild` composition pattern is deprecated in high-frequency rendering loops due to children array mapping and cloning execution overhead.
3. **Compound & Headless UI Separation**: Component logic, states, and event orchestration hooks are separated from visual markup. Headless engines remain blind to HTML wrappers, delegating structure layout composition to the downstream consumer.
4. **Panda CSS & Data Contract Strictness**: Styling definitions must resolve back to established design tokens, avoiding hardcoded properties or raw layout declarations.

---

## 2. Solution Architecture

The platform architecture is structured into two main physical package containers, married by a build-time Zero-Runtime styling extraction pipeline:

```mermaid
graph TD
    subgraph Packages_Layer [Physical Packages]
        DS["@scnx/system (packages/design-system)"]
        CoreUI["@scnx/core-ui (packages/core-ui)"]
    end

    subgraph Build_Compiler [Zero-Runtime Build Pipeline]
        AST["Panda CSS AST Scanner"]
        Sass["Sass Preprocessor"]
        OptimizedCSS["Optimized CSS Asset Bundle"]
    end

    subgraph Consumer_Apps [Downstream Portal Consuming Layer]
        IAM["scnehaux-iam-dashboard"]
        ERP["ERP Portal Host"]
    end

    DS -->|Token maps & variables| AST & Sass
    CoreUI -->|Polymorphic markup| AST
    AST & Sass -->|Extract & Compile| OptimizedCSS
    OptimizedCSS -->|Statically Inject| IAM & ERP

    style Packages_Layer fill:#1e1b4b,stroke:#4f46e5,stroke-width:2px,color:#fff
    style Build_Compiler fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff
```

### 2.1 Physical Package Boundaries
-   **`@scnx/system` (`packages/design-system`)**: The visual core of the enterprise. Housed under `packages/design-system`, it declares the raw core primitives (Tier-1), the global semantic theme contracts (Tier-2), and compiles them to CSS Custom Properties. It orchestrates all build-time configuration variables for static layout compilers.
-   **`@scnx/core-ui` (`packages/core-ui`)**: The physical component library containing style-agnostic, accessible, and polymorphic React primitives (e.g., `<Box>`, `<Flex>`, `<Grid>`, `<Text>`). It relies 100% on `@scnx/system` for visual styling and is completely decoupled from any direct vendor CSS frameworks.

### 2.2 Zero-Runtime Build Pipeline
To ensure maximum client-side performance, the platform rejects runtime CSS-in-JS style injection. It utilizes a dual build-time engine:
1.  **Panda CSS AST Scanner**: Scans downstream Javascript/TypeScript source files at compile time. It extracts utility token classes from markup and compiles them directly into static atomic utility CSS rules, avoiding runtime execution overhead.
2.  **Sass Preprocessor**: Orchestrates global static structures, custom layout grids, and complex theme contracts (`_core-token.scss` and `_default-token.scss`). It outputs a consolidated, highly optimized CSS bundle containing custom properties and layout grids.

### 2.3 Design System Base Layer & Reset Isolation
The `@scnx/system` package ships a dedicated **Base Layer** (housed under `packages/design-system/src/styles/base/`) to clean and equalize default browser rendering before styling components or applying styling utilities.
1.  **Normalization & Reset Strategy**: 
    - Normalization rules (`_normalize.scss`) equalize styling inconsistencies between client viewports.
    - Core structural resets (`_reset.scss`) clean the native padding, margin, border, and typography properties of native interactive elements (`button`, `input`, `select`, `textarea`, `a`).
    - Typographical and baseline alignments (`_base.scss` and `_typography.scss`) define global default weights, line heights, and SVG vertical alignments.
2.  **Cascade Layer Isolation**:
    - To prevent resets and normalizations from interfering with or overriding downstream utilities and components, all reset rules are wrapped in native CSS `@layer reset` and `@layer base`.
    - The compiled bundles (`default-ui.scss`) declare the explicit cascade precedence order (`@layer reset, base, tokens, recipes, utilities;`), guaranteeing that base rules are evaluated first and cannot override design tokens or utility styles.

---

## 3. Physical Primitives & Theme Mappings

To prevent abstraction leakage in logical documents, the physical parameters and scales of the Presentation Platform are exhaustively detailed below.

### 3.1 Tier-1: Core Primitives (Raw Nested SCSS Map Values)

To guarantee build-time optimization and allow seamless dynamic runtime opacity modifiers, all colors are mapped inside `_core-token.scss` as **space-separated HSL values** or **OKLCH coordinates** rather than static hex values.

The physical values of the primitive scales are defined as nested Sass maps in `$color`:

*   **Nested HSL Primitive Map Structure**:
    ```scss
    $color: (
      white: 0 0% 100%,
      black: 0 0% 0%,
      neutral: (
        light: (
          0: 0 0% 100%,   // Pure White
          100: 215 6% 98%, // bg-surface default
          200: 215 6% 95%, // bg-surface raised
          300: 215 6% 92%, // bg-surface sunken
          400: 215 6% 85%,
          500: 215 6% 74%,
          600: 215 6% 68%,
          700: 215 6% 56%,
          800: 212 7% 52%, // calibrated secondary text
          900: 213 7% 36%, // primary body text
          1000: 216 8% 13%, // deep heading
          1100: 210 8% 5%  // near black for inverse
        ),
        dark: (
          0: 210 8% 5%,  // deepest dark
          100: 216 8% 13%, // bg-canvas dark
          200: 218 8% 16%, // bg-surface dark
          300: 216 8% 13%,
          400: 221 11% 39%, // bg-surface-sunken dark
          500: 220 10% 49%,
          600: 221 11% 39%,
          700: 219 12% 32%,
          800: 220 15% 73%,
          900: 210 20% 98%,
          1000: 210 50% 99%,
          1100: 0 0% 100% // near white for inverse on dark
        )
      ),
      // Chromatic Hue Scales (9 families, e.g., blue)
      blue: (
        light: (
          100: 214 95% 97%,
          600: 221 83% 53%,
          700: 224 76% 48%,
          800: 222 71% 40%
        ),
        dark: (
          100: 222 64% 33%,
          500: 221 90% 59%,
          600: 221 83% 53%,
          800: 222 71% 40%
        )
      )
    );
    ```
*   **Translucent Alpha-Equivalent Primitives**: In addition to solid HSL/OKLCH scales, the program compiles alpha-blended transparent coordinates (`100A` to `1000A`) using reverse blending against the light card base and dark card base, outputting format like `214 6% 92% / 0.35` or `0.92 0.02 240 / 0.35` for flawless dynamic layers.
*   **Layout Spacing**: 13 increments (`0` to `20`) mapped using:
    ```scss
    $spacing: (0: 0, 0_5: 0.125rem, 1: 0.25rem, 2: 0.5rem, 3: 0.75rem, 4: 1rem, 5: 1.25rem, 6: 1.5rem, 8: 2rem, 10: 2.5rem, 12: 3rem, 16: 4rem, 20: 5rem);
    ```
*   **Element Sizing**: 12 core height/width constraints (`'10'` [0.625rem] to `'72'` [4.5rem]) mapping to control boundaries, avatars, and icons.
*   **Border Radius**: 7 curvature curves (`none` [0], `xs` [2px], `sm` [4px], `md` [6px], `lg` [8px], `xl` [12px], `full` [9999px]).
*   **Z-Index Planes**: Stacking planes (`0` [0], `10` [1000], `20` [1020], `30` [1030], `40` [1040], `50` [1050], `60` [1060]).

### 3.2 Tier-2: Global Semantic Themes

Theme maps translate raw nested HSL/OKLCH primitives into semantic variables under light/dark modes using the `get-color-tokens` mapping engine in `_default-token.scss` (rendered as CSS Custom Properties in `@scnx/system`):

| CSS Custom Property | Light Mode Mapping | Dark Mode Mapping |
| :--- | :--- | :--- |
| `--ds-bg-canvas` | `neutral-0` (`0 0% 100%`) | `neutral-0` (`210 8% 5%`) |
| `--ds-bg-surface` | `neutral-100` (`215 6% 98%`) | `neutral-100` (`216 8% 13%`) |
| `--ds-text-primary` | `neutral-900` (`213 7% 36%`) | `neutral-900` (`210 20% 98%`) |
| `--ds-border-default` | `neutral-1100 / 0.15` (Alpha blended) | `neutral-1100 / 0.15` (Alpha blended) |
| `--ds-primary-base` | `blue-800` (`222 71% 40%`) | `blue-800` (`222 71% 40%`) |
| `--ds-primary-hover` | `blue-700` (`224 76% 48%`) | `blue-700` (Hover offset) |

---

## 4. Deployment & Topology

The platform packages are developed locally within the monorepo and integrated into downstream applications via local workspace linkages:

-   **Development Isolation**: Downstream applications consume the design packages via **pnpm workspaces** locally. Changes to package files are hot-reloaded automatically inside Vite and Rspack bundlers.
-   **Production Delivery**: Built static assets (minified CSS files and TypeScript declarations) are published to the enterprise private NPM registry. The consuming SPA apps bundle these assets into their physical deployment targets during build time, serving them globally via global CDNs (e.g., AWS S3 and CloudFront).
-   **Encapsulation Boundary**: To prevent layout pollution under Module Federation, `@scnx/system` provides unique namespace classes (e.g., `.scnx-theme-wrapper`). Consuming micro-frontends wrap their entry roots with these classes to enforce isolated styling sandboxes.

---

## 5. Runtime Flows

### 5.1 Build-Time Compilation and Static Style Extraction Flow
Demonstrates how raw SCSS variables and React primitive markups compile down to a zero-runtime static CSS bundle:

```mermaid
sequenceDiagram
    autonumber
    participant Developer as TSX Markup / SCSS Code
    participant Scanner as Panda CSS AST Scanner
    participant Preprocessor as Sass Preprocessor
    participant Bundle as Output Static CSS Bundle
    participant Browser as Browser Client
    
    Developer->>Scanner: Scan React TSX markup (Box/Text props)
    Developer->>Preprocessor: Import _core-token.scss and _default-token.scss
    Scanner->>Scanner: Extract CSS utility names from AST
    Preprocessor->>Preprocessor: Resolve Sass maps to CSS custom variables
    Scanner->>Bundle: Write static utility CSS
    Preprocessor->>Bundle: Write global layout CSS & theme overrides
    Bundle->>Browser: Load index.css static asset
    Browser->>Browser: Fast painting with Zero JavaScript styling execution
```

### 5.2 Transition & Overlays Frame Sanitization Flow
Ensures that all dynamic overlays, modals, and layout transition animations execute with clean momentum without visual queue piling or flickering:

```mermaid
sequenceDiagram
    autonumber
    participant Trigger as Modal / Overlay Trigger
    participant OFSM as Orthogonal Finite State Machine
    participant RAF as requestAnimationFrame Queue
    participant GPU as GPU Paint Layer
    
    Trigger->>OFSM: Dispatch Transition Phase (e.g. entering)
    OFSM->>RAF: Request Frame Sanitization (Clear past animation handles)
    RAF->>RAF: Align to V-Sync frame boundary
    RAF->>GPU: Mutate CSS transform & opacity properties
    GPU-->>OFSM: Animation completed (settled)
    OFSM->>OFSM: Transition stabilized with Zero Flickering
```

---

## 6. Resilience & Failure Modes

-   **Missing CSS Variables Fallback**: For environments with restricted stylesheet imports, Sass maps are pre-compiled into static fallback utility classes, allowing layout systems to degrade gracefully without breaking structural functionality.
-   **Cumulative Layout Shift (CLS) Mitigation**: Unloaded visual components (e.g., dynamic tables, async charts) are matched with strict width/height sizing properties based on Tier-1 primitive values, rendering structured skeletons immediately to keep CLS strictly under `0.1`.
-   **Momentum Reversal Interruption**: If a transition is interrupted mid-flight (e.g., user triggers a close animation while an overlay is still opening), the frame queue immediately purges the active animation handle, recalculates the elapsed transform coordinates, and gracefully reverses the animation without resetting the layout.

---

## 7. Observability & Quality Benchmarks

To maintain peak web performance, the presentation platform enforces strict operational metrics:

-   **Performance Benchmarks (NFRs)**:
    *   **Cumulative Layout Shift (CLS)**: Strictly $\le 0.1$.
    *   **Interaction to Next Paint (INP)**: Strictly $\le 200\text{ms}$.
    *   **P95 Layout Reflow Paint Duration**: Strictly $\le 100\text{ms}$.
    *   **Gzip CSS Bundle Size**: Max limit of `12KB`.
-   **Error Telemetry**: The `@scnx/core-ui` components are wrapped in strict Error Boundary handlers. Unhandled rendering errors or CSS injection failure states trigger Sentry logging events containing specific component tag references and active theme state identifiers.

---

## 8. Security Considerations

-   **Strict Content-Security-Policy (CSP)**: The presentation layer prevents inline style injections (`style-src 'unsafe-inline'`). All compiled utilities are loaded via static assets linked to build-time hashes, or injected using trusted stylesheet nonces.
-   **Polymorphic ARIA Accessibility Core**: Accessible behaviors are built directly into the polymorphic Layer-1 primitives of `@scnx/core-ui` (incorporating focus-trapping inside modal overlays, ARIA state bindings for custom controls, and keyboard navigation support), guaranteeing compliance with WCAG 2.2 AA standards at the visual root of trust.
