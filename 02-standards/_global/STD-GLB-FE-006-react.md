---
doc_meta:
  id: STD-GLB-FE-006
  title: Enterprise React Development Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-05-21
---

# Enterprise React Development Standard (STD-GLB-FE-002)

---

## 1. Objective & Scope

This standard defines the mandatory development practices, lifecycle rules, rendering optimization constraints, component composition patterns, and architectural boundaries for all browser-executed applications and component libraries built using the React framework within the Scnehaux enterprise.

It establishes a uniform engineering contract to guarantee that all React components are deterministic, resource-optimized, type-safe, and maintainable across all development teams.

### 1.1 React Framework Version Baseline

- **Mandatory React 19.2.4+**: All applications and libraries must declare React version **19.2.4 or higher** as a core dependency.
- **Vulnerability Remediation**: Versions below 19.2.4 are prohibited due to critical security vulnerabilities:
  - **Remote Code Execution (RCE) / [CVE-2025-55182](https://nvd.nist.gov/vuln/detail/CVE-2025-55182)**: Critical vulnerability permitting unauthenticated attackers to execute arbitrary code on the server side via specially crafted HTTP requests targeting the React Server Components (RSC) Flight protocol.
  - **Denial of Service (DoS) / [CVE-2025-55184](https://nvd.nist.gov/vuln/detail/CVE-2025-55184), [CVE-2025-67779](https://nvd.nist.gov/vuln/detail/CVE-2025-67779), & [CVE-2026-23864](https://nvd.nist.gov/vuln/detail/CVE-2026-23864)**: Vulnerabilities permitting attackers to cause server hangs, excessive CPU consumption, and out-of-memory crashes.
  - **Source Code & Secrets Leakage**: Vulnerability permitting backend source code disclosure, risking exposure of embedded environment variables or API keys.
- **SSR and Platform Stability**: React 19.2.4+ is mandated to establish a stable baseline for server-side rendering execution, modern resource loading patterns, and unified ref resolution properties.

---

## 2. Design Principles

The Scnehaux Enterprise React Standard is governed by the **Supreme Frontend Governance**. This architectural philosophy enforces Deterministic Systems, Clean Architecture, and Zero Waste Execution. All React implementations must adhere to these five non-negotiable principles:

1. **Determinism Over Cleverness**: Output must be perfectly predictable from input. No hidden side-effects.
2. **Explicit State Only**: No implicit, duplicated, or shadow state. Single source of truth. Derived state MUST be computed inline.
3. **Strict Separation of Concerns**: UI $\neq$ State $\neq$ Side Effects $\neq$ Domain Logic. Enforcing the strict layer: `UI (Pure) -> Hooks (State Orchestration) -> Services (IO) -> External Systems`. Business logic inside JSX is strictly prohibited.
4. **Zero Waste System**: No unnecessary re-renders, no meaningless DOM wrappers, and no unnecessary memory allocations.
5. **Observability First**: Zero silent failures. Every failure, mutation, and async flow must be traceable and surfaced to the UI boundary.

## 3. Normative Rules

### Component Architecture

#### Cohesive Component Locality

- **Locality of Behavior (LoB)**: Components should group related concerns (such as local visual structures, interactive handlers, accessibility labels, and local state management) to preserve context and readability. Over-fragmenting a component into artificial sub-modules solely to enforce a dogmatic separation of concerns is prohibited.
- **Complexity Boundaries**: Component composition is governed by responsibility boundaries, cyclomatic complexity (target limit of 10), and single-responsibility cohesion. Components must be evaluated for decomposition based on render branch counts and state orchestration complexity.
  - **Presentational/Leaf Components**: Maintain strict cohesion around a single visual element.
  - **Orchestration Components**: Complex layout orchestrators, dynamic form builders, and data tables must maintain clean internal helper segregation and delegate side-effects to custom hooks.
- **Pure & Idempotent Renders**: Given the same props and state, a component must always produce the same output. Side-effects inside the render path are prohibited.
- **Shared Utilities Extraction**: Any pure helper function, formatting utility, data transformer, or validation check that is consumed by more than one component must be extracted from the component scope and placed in a dedicated, unit-tested utility module. Duplicating helper functions within multiple component files is prohibited.
- **Custom Hook Promotion**: Shared logic that encapsulates React state, refs, or lifecycle effects (such as DOM event observers, timers, or window dimensions) must be promoted to a custom hook (`hooks/`) rather than static utility files.

#### Composition Patterns

- **Layout Composition (Children & Element Props)**: Layout flexibility must be achieved through `children`, render props, or props accepting React elements/nodes (e.g., `header={<Header />}`). Prop drilling through more than 2 intermediate components (calculated as wrapper/layout components that receive props solely to pass them down without using or mutating them) is prohibited.
  - _Compliant (drill depth <= 2)_: `Parent (State Owner) -> LayoutWrapper -> LeafComponent (Consumer)` (1 intermediate layer).
  - _Prohibited (drill depth > 2)_: `Parent (State Owner) -> PageLayout -> CardWrapper -> TabContainer -> LeafComponent` (3 intermediate layers). Use layout composition or React Context instead.
- **Compound Components & Slot Architecture (Inversion of Control)**: Multi-part widgets must use composition rather than flat configuration props. Passing monolithic configuration props (e.g., `<Dropdown items={data} isOpen={true} theme="dark" showIcon={false} />`) is strictly prohibited. Instead, components must expose a declarative parent-child API (e.g., `<Dropdown><Dropdown.Trigger>...</Dropdown.Trigger><Dropdown.Menu>...</Dropdown.Menu></Dropdown>`) sharing state via scoped context. This adheres to the Open-Closed Principle (OCP), making the system highly flexible, easily testable, and eliminating the need to modify core components for minor layout changes.

#### Ref Forwarding

- **Mandatory `forwardRef`**: All primitive and reusable components that render a single DOM element must forward refs using `React.forwardRef` (or the React 19+ ref-as-prop pattern) to allow parent consumers direct DOM access for measurement, focus management, and animation binding.
- **`useImperativeHandle` Constraint**: Exposing imperative handles must be restricted to cases where DOM access alone is insufficient (such as programmatic scroll-to or complex focus orchestration). Overuse of imperative APIs breaks declarative data flow.

#### Casing & File Naming Conventions

- **Directories & Non-Component Files**: Directory names, utility files, custom hooks, and context providers must use **kebab-case** (e.g., `create-context.tsx`, `use-on-click-outside.ts`, `string-formatter.ts`). File names using snake_case or camelCase are prohibited.
- **React Component Files**: React component files must use **PascalCase** matching the component's function/class identifier (e.g., `SidebarNavItem.tsx`, `TransitionBase.tsx`).
- **Shared Utility Functions**: Shared pure utility helper functions exported from utility files (e.g., in `utils/` or domain helper modules) must use **camelCase** (e.g., `formatCurrency`, `calculateTotal`). Standardizing on camelCase preserves consistency with the TypeScript/JavaScript ecosystem and prevents ESLint configuration conflicts.
- **Local Scope & Hook Identifiers**: Local functions, variables, custom hooks, and objects inside component or hook scopes must use **camelCase** (e.g., `handleClick`, `useActiveSession`, `activeUser`). Using snake_case for local scope variables or functions is prohibited, except when referencing raw backend API payloads or environment configuration variables.

---

### State Management & Data Flow

#### Single Source of Truth

- Component state must reside in exactly one location. Storing duplicated or mirrored values derived from parent props in local `useState` is prohibited. If a value can be computed from existing state or props, it must be computed — not stored.

#### Derived State Computation

- Calculations derived from existing state or props must be computed inline during the render cycle.
- **Non-Primitive Derived Structures**: Computations producing non-primitive structures (new arrays or object references, such as `.filter()`, `.map()`, or object spread operations) that are consumed by memoized children or context providers:
  - **In Legacy Mode (Without Compiler)**: Must be wrapped in `useMemo` to preserve reference stability and prevent unnecessary downstream reconciliation cycles.
  - **In Modern Mode (With Compiler)**: Do not require manual `useMemo` as the compiler automatically stabilizes these references, unless passed across uncompiled boundaries.
- **Expensive Computations**: Synchronous computations that significantly degrade rendering performance (such as heavy tree flattening, sorting large datasets, or parsing complex documents) must use `useMemo` with correct dependency arrays. If the synchronous computation duration blocks a frame refresh window (exceeding 16ms under standard browser execution limits), offloading the work to a Web Worker or using `useDeferredValue` is mandatory to keep the main thread responsive.

#### Context API Boundaries

- React Context must be restricted to static or low-frequency state updates (such as theme configurations, user session metadata, locale, or feature flag bundles).
- High-frequency state propagation (such as real-time form input, drag coordinates, or animation progress) must use localized state, component composition, or optimized atomic stores (such as Zustand with selector subscriptions) to prevent unnecessary subtree re-renders.
- **Context Splitting**: Contexts combining frequently-changing values with stable values must be split into separate providers (e.g., `<StateContext.Provider>` and `<ActionsContext.Provider>`) to isolate re-render boundaries.
  - **React Compiler Context Behavior**: While the React Compiler automatically memoizes the `value` prop passed to a context provider (removing the need for manual `useMemo` on the provider's value), the runtime Context API still triggers re-renders for all subscribing consumers whenever the value reference changes. Splitting the context remains the mandatory pattern to prevent consumers of stable actions from re-rendering when state changes.

#### State Lifting & Colocation

- State must be colocated to the lowest common ancestor component that requires access to the data. Lifting state prematurely to global contexts or top-level layout components is prohibited.

#### Normalized Data Graphs

- **Flat Relational State (Normalized Data Graph)**: Collections of complex entities must be stored in a normalized, flat relational graph (using ID-based dictionaries) rather than deeply nested JSON trees. Storing duplicated data entities across different state slices is strictly prohibited. Components must reference the single source of truth via ID lookups (similar to a relational database in the browser). This guarantees that modifying an entity (e.g., updating a user's name in a comment) instantly updates all other references across the UI without requiring re-renders or redundant network fetches (e.g., utilizing Apollo Cache or Redux Toolkit normalized state).

#### Finite State Machines (FSM)

- **Critical Flow Orchestration**: Complex, multi-step interactive flows (such as Authentication, Payment Checkouts, or multi-step Wizards) must be modeled using deterministic Finite State Machines (FSM). Relying on disparate boolean flags (e.g., `isLoading`, `isError`) to represent mutually exclusive states is an anti-pattern and strictly prohibited.

#### Orthogonal Finite State Machines (OFSM) for UI Transitions

- **Parallel Transition Constraints**: Structural UI transition components (such as Modals or Overlays) that orchestrate animations alongside DOM mutations must utilize Orthogonal Finite State Machines (OFSM). This ensures that parallel state dimensions (such as the current visual phase, layout readiness, and momentum interruption) are synchronized deterministically against the browser's paint cycle.
- **Standardized Phase Contract**: To prevent visual layout flickering, transition components must adhere to a strict, bounded multi-phase contract. The phase progression must deterministically map to the component's physical mounting and unmounting lifecycle. Hardcoding arbitrary or ad-hoc transition states in product-level code is prohibited.

---

### Hook Lifecycle Rules

#### useEffect — Strict Boundary

- `useEffect` must be restricted to synchronizing with external non-React systems:
  - Direct DOM measurements and mutations (such as `getBoundingClientRect`, `ResizeObserver` subscriptions).
  - Network socket connections (WebSocket, EventSource).
  - Third-party non-React library integrations (such as chart engines or map SDKs).
  - Browser API subscriptions (such as `matchMedia`, `IntersectionObserver`, `MutationObserver`).
- **Prohibited Uses**: Synchronizing internal React states using `useEffect` (such as `useEffect(() => setX(props.y), [props.y])`) is prohibited. Use derived computation or event handlers instead.

#### Cleanup & Resource Release

- All hooks establishing subscriptions, timers, event listeners, observers, or polling operations must return a clean-up callback to release all resources upon component unmount or dependency change.
- **AbortController Binding**: Asynchronous data operations triggered within a component lifecycle (such as `fetch` inside `useEffect`) must be linked to an `AbortController` signal. The abort must fire in the cleanup function.

#### Dependency Array Integrity

- Hook dependency arrays must be declared with complete reference accuracy. Every value from the component scope used inside the effect callback must appear in the dependency array.
- Bypassing linting rules (such as `// eslint-disable-next-line react-hooks/exhaustive-deps`) is prohibited without a formally documented exception in the codebase.
- **Ref Stability Awareness**: Values stored in `useRef` do not trigger re-renders and must not be listed in dependency arrays. However, the `.current` value must not be read asynchronously without checking for staleness.

#### Custom Hook Design

- Custom hooks must be deterministic, reusable, and composable. Each custom hook must own a single concern (such as `useDebounce`, `usePagination`, `useMediaQuery`).
- Custom hooks must not contain JSX or rendering logic. They orchestrate state and side-effects, returning values and handlers for consumption by components.
- **State and Actions Separation**: Complex custom hooks that expose both state data and mutator handlers must structure their return values by separating read-only data (**State**) and stable mutator functions (**Actions**), typically returning an object of shape `{ count, actions }` or `[state, actions]`.
  - **Actions Memoization**:
    - **In Legacy Mode (Without Compiler)**: The `actions` object must be wrapped in `useMemo` (or its child functions wrapped in `useCallback`) to preserve reference stability and prevent unnecessary re-renders in memoized children or context consumers.
    - **In Modern Mode (With Compiler)**: Manual actions memoization is discouraged as the compiler automatically analyzes and stabilizes the returned action references.
  - **Functional State Updates**: To avoid stale closures and keep the `actions` dependency array empty (`[]`) or stable, mutator actions must execute state updates function-wise (e.g., `setState(prev => prev + value)` instead of `setState(state + value)`).
  - **Prohibit Return Wrapper Memoization**: Wrapping the entire array/object hook return value itself in `useMemo` (e.g., `return useMemo(() => [state, actions], [state, actions])`) is prohibited in Legacy Mode, as it adds redundant allocations without rendering benefit for consumers destructuring the output immediately. Under Modern Mode, the compiler automatically manages this optimization.
- **Naming Convention**: All custom hooks must start with the `use` prefix. Hooks that subscribe to external sources must clearly document their cleanup behavior in TSDoc.

#### Hook Execution Order

- Hooks must never be called conditionally (inside `if`, `for`, `switch`, or early returns). React's hook identity depends on stable call order across renders. Violations cause corrupted state and unpredictable behavior.

---

### Render Optimization (Zero-Waste)

#### Rendering Optimization & Memoization Modes

Performance optimization strategy depends on whether the build-time **React Compiler** is active or inactive in the application's toolchain.

##### Legacy Mode (Without React Compiler)

For codebases or modules where the build-time React Compiler is not integrated or has been disabled, developers must strictly manage rendering performance manually to prevent redundant update cascades:

- **Reference Integrity Enforcement**: Callbacks passed as props to memoized components must be wrapped in `useCallback`. Objects, arrays, and complex configurations declared inside component rendering bodies must be wrapped in `useMemo`.
- **Subtree Optimization**: Leaf and orchestration components subject to frequent rendering or high prop change frequency must be wrapped in `React.memo`.
- **Inline JSX Restrictions**: Declaring inline arrow functions (e.g. `onClick={() => handleClick(item)}`) or inline objects inside JSX props is prohibited when passing them to memoized child components, as it invalidates reference stability.

##### Modern Mode (With React Compiler)

When the build-time React Compiler is active (via `babel-plugin-react-compiler` or bundler plugins), manual memoization hooks (`useMemo`, `useCallback`) and `React.memo` wrappers must be avoided by default to prevent optimization redundancy. They must only be introduced if profiling demonstrates necessity, when interfacing across uncompiled boundaries, or in explicit compiler bailout scenarios. The compiler automatically optimizes component rendering boundaries and reference arrays.

- **Compiler Architecture**: React Compiler operates as a build-time transpilation step, scanning component code and injecting code block caches. It relies on React 19's native runtime cache framework.
- **Inline Closures Stabilization**: Passing inline arrow functions in JSX (e.g. `onClick={() => handleClick(item)}`) is permitted. The compiler automatically optimizes these inline callbacks, preserving reference stability without manual `useCallback` wraps.
- **Automatic Element Caching**: Passing JSX elements as props (e.g., `sidebar={<Sidebar user={user} />}`) is stabilized at compile-time, removing the need for manual `useMemo` wrappers around markup trees.

##### Mandatory Cases for Manual Memoization under React Compiler

Even when the compiler is active, manual memoization is mandatory under the following two parameters:

- **High-Computational Caching**: React Compiler stabilizes references to prevent child re-renders, but it does not cache the CPU execution cost of heavy calculations. Pure algorithms processing datasets (e.g., sorting, transforming, or filtering arrays of $100+$ items) must be wrapped in `useMemo` to prevent execution on every render cycle.
- **Explicit Compiler Bailouts**: Components that violate React's rules (e.g., mutating props directly or violating hook order rules) cause the compiler to skip compilation (bail out). If a bailed-out component experiences performance issues, manual memoization must be applied and accompanied by a code comment.

##### Wrapping Uncompiled External Components with `React.memo`

When consuming external, uncompiled components (such as third-party library imports) in a compiled application, developers must wrap them manually in `React.memo` to establish re-render boundaries. The three approved wrapping patterns are:

###### Pattern A: Direct Module-Level Wrapper (Standard)

Wrap the imported component directly in a constant at the module level (outside the render function):

```tsx
import React from 'react';
import { ExternalUncompiledChart } from 'third-party-chart-library';

const MemoizedChart = React.memo(ExternalUncompiledChart);

export const AnalyticsWidget = ({ data }) => {
  return <MemoizedChart data={data} />;
};
```

###### Pattern B: Custom Comparison Wrapper

Provide a custom equality comparison function as the second argument to `React.memo` for fine-grained control over prop updates:

```tsx
import React from 'react';
import { ExternalUncompiledChart } from 'third-party-chart-library';

const MemoizedChart = React.memo(ExternalUncompiledChart, (prevProps, nextProps) => {
  return prevProps.dataId === nextProps.dataId;
});
```

###### Pattern C: Adaptor Wrapper with Reference Passing (React 19 Native)

If the external component requires default prop injection or reference forwarding, wrap it inside a local adaptor component. In React 19, `ref` is passed as a standard prop, eliminating the need for `forwardRef`:

```tsx
import React from 'react';
import { ExternalUncompiledChart } from 'third-party-chart-library';

// In React 19, 'ref' is consumed as a standard prop
const ChartAdaptor = ({ ref, ...props }: { ref?: React.Ref<any>; [key: string]: any }) => {
  return <ExternalUncompiledChart {...props} ref={ref} />;
};

const MemoizedChart = React.memo(ChartAdaptor);
```

##### Evaluation Metrics for Performance Tuning

To prevent over-memoization or missing critical rendering bottlenecks, developers must use the following quantitative parameters to identify expensive computations, expensive subtrees, and memoization targets:

###### 1. CPU-Expensive Computation Parameters

A synchronous calculation running within the render path is classified as expensive and requires `useMemo` if it meets any of the following criteria:

- **Execution Time Threshold**: Synchronous processing taking **> 1ms** to complete under a standard desktop CPU profile (or **> 0.5ms** on a mobile profile). Any computation exceeding **10ms** must be offloaded to a Web Worker or deferred via `useDeferredValue`.
- **Complexity and Data Volume Heuristic**:
  - Linear operations $O(N)$ executing on arrays containing **$\ge 1000$ items**.
  - Quadratic operations $O(N^2)$ or higher (e.g., nested lookups, matrix comparisons) on datasets containing **$\ge 50$ items**.
  - Deep comparisons or deep structural cloning (e.g., `JSON.parse(JSON.stringify(obj))` or `structuredClone`) on nested objects of any scale.
- **Cryptographic & Vector Math**: Any calculation executing coordinate transformations, canvas pixel analysis, cryptographic hashing, or dynamic regex compilations on variable inputs.

###### 2. Expensive Component Subtree Parameters

A component or its nested children is classified as expensive to render (making reference stability in the parent and `React.memo` wrapping on the child mandatory in Legacy/Bailout modes) if it meets any of the following criteria:

- **DOM Node Count**: The component and its descendants render **$\ge 100$ DOM elements** in total.
- **Render Tree Depth**: The component tree structure exceeds **8 layers** of nesting.
- **Visual Rendering Overhead**: The component contains active canvas rendering, complex SVG vector graphics, or dynamic animations (e.g., Framer Motion loops) that trigger GPU redraws.
- **Layout Reflow Invocations**: Components executing DOM measurements (such as `getBoundingClientRect` or `ResizeObserver` callbacks) during initialization or rendering, which can trigger browser layout recalculations.

###### 3. Memoization Targets Beyond Prop Passing

Aside from stabilizing data or callbacks passed to children, manual memoization must be applied to:

- **Internal Rendering Boundaries**: Wrapping heavy calculations that transform local rendering arrays (e.g., sorting logs before local mapping) to protect them from executing when unrelated local states (such as toggling a modal, a tooltip, or a sidebar) trigger a parent re-render.
- **Hook Dependency Stability**: Stabilizing dynamic objects or arrays that are passed as dependencies to downstream hooks (`useEffect`, `useLayoutEffect`, `useMemo`) to prevent continuous re-registration or infinite invocation loops.
- **State Store Selector Subscriptions**: Caching selector functions passed to global state stores (such as Zustand) to guarantee that reference updates do not trigger unnecessary component updates when unrelated segments of the global state change.

#### Allocation Discipline

- **Scope Constants Outside Rendering**: Static objects, arrays, configuration maps, and unchanging handler references must be declared outside the component function scope (at module level) to bypass per-render allocation cycles.
- **Targeted Allocation Optimization**: Inline declaration of object literals (`style={{ ... }}`), array literals, and anonymous arrow functions directly inside JSX templates is prohibited only on hot paths (components subject to high-frequency updates, active animations, or virtualized list items). They are permitted in static or low-frequency layouts to maintain behavioral locality.
- **Event Handler Extraction**: Event handlers performing complex logic must be extracted to named functions. The React Compiler optimizes inline arrow function reference stability automatically, but extraction is mandated to keep component files readable.

#### List Rendering & Key Stability

- **Stable Unique Keys**: Every element in a rendered list must have a stable, unique `key` derived from domain identity (such as database ID or UUID). Using array index as `key` is prohibited — index keys cause incorrect DOM recycling, corrupted component state, and broken animations.
- **Virtualization Threshold**: Virtualization becomes mandatory when rendering list size degrades interaction latency or violates the 16ms frame budget. As empirical heuristics to ensure target performance:
  - **Rich Component Lists**: Lists rendering complex layouts (e.g., cards with nested components, images, or interactive elements) must implement virtualization (using `@tanstack/virtual` or `react-window`) if the list size exceeds **50 items**.
  - **Plain Text or Tabular Lists**: Lists rendering plain text, key-value rows, or single-line textual elements must implement virtualization if the list size exceeds **200 items**.

#### Concurrent Rendering

- **`useTransition`**: Non-urgent state updates (such as filtering a large dataset or switching tabs with heavy content) must be wrapped in `useTransition` to keep the UI responsive during expensive reconciliation.
- **`useDeferredValue`**: Derived values driving expensive subtree renders (such as search result lists) must use `useDeferredValue` to defer their visual update without blocking user input.
- **Policy**: Concurrent features must not be used as a substitute for proper algorithmic optimization or virtualization. They defer work — they do not eliminate it.

---

### Component Typings & Props Contracts

#### Strict TypeScript Contracts

- Component props must be typed explicitly using dedicated `type` or `interface` declarations. Using `any`, `unknown` (without narrowing), or untyped object signatures (`Record<string, any>`) in prop contracts is prohibited.
- Prop types must inherit from standard React element typings (such as `ComponentPropsWithoutRef<'button'>`) to preserve native HTML attribute pass-through (such as `aria-*`, `data-*`, `className`).

#### Context-Aware Prop Contracts

- **Cohesive Entity Rendering**: Components rendering cohesive domain entities (e.g., `<UserCard user={user} />`, `<InvoiceRow invoice={invoice} />`) must receive the domain object directly to prevent prop explosion and maintain api design cleanliness.
- **Minimal Primitive Props**: Generic, highly reusable UI primitives (e.g., Buttons, Inputs, Alerts, Layout Grid cells) must accept only primitive leaf properties (such as `label`, `onClick`, `status`) to maximize reuse and isolation.
- **Large Object Rejection Rationale**: Restricting props to leaf primitives on UI primitives is mandated due to three architectural factors:
  - **Memoization Boundary Isolation**: Unrelated mutations on domain objects bypass memoization checks in compiler opt-out scenarios.
  - **Explicitness of Contract**: Destructuring parameter fields forces consumer components to declare exactly what data is required.
  - **Unit Testing Isolation**: Restricting props to leaf primitives streamlines unit testing by allowing developers to mock only the relevant properties, eliminating complex mock domain entities.

#### Discriminated Unions for Variant Props

- Components with mutually exclusive behavioral modes must use TypeScript discriminated unions to guarantee compile-time exhaustive checking. Loose optional props that create impossible state combinations are prohibited.

#### Generic Components

- Components operating on dynamic data structures (such as table renderers, select lists, or autocomplete widgets) must declare explicit TypeScript generic type parameters (`<T>`) to guarantee type-safety throughout rendering callbacks.

---

### Error Handling & Resilience

- **Error Boundaries**: Critical application features must be wrapped in React Error Boundaries (configured with fallback components) to isolate rendering failures. A rendering crash in an isolated sub-component must not cause the entire application runtime to fail.
- **Recovery & Reset Mechanics**: Error boundaries must expose a reset handler to allow users to retry the failed action or re-render the crashed subtree (e.g. on route change or explicit retry button click) without forcing a full page reload.
- **Graceful Degradation**: Component rendering states must handle partial, empty, or failed data payloads gracefully. Render states must check for nullability (`data?.value`) and render fallback empty states or skeleton wrappers instead of throwing runtime exceptions.
- **Telemetry and Error Tracking**: All unhandled exceptions caught by Error Boundaries must be logged to the telemetry platform with correlation IDs, tracing state context, and execution details.

---

### Server Components & Streaming (Future Readiness)

- **Server Components Boundary**: Components importing APIs that access server-exclusive resources (such as filesystem access, secure server credentials, or direct database connections) must reside in a file prefixed with the `'use server'` directive. Client-side elements (such as DOM event listeners, browser hooks, or state variables) are prohibited within Server Components and must be extracted to separate files starting with the `'use client'` directive.
- **Render-as-You-Fetch (Suspense & Error Boundaries)**: The legacy "Fetch-on-Render" pattern (waiting for a component to render before triggering its API fetch, causing request waterfalls) is prohibited. Applications must trigger API requests at the Route/Router level in parallel with code downloading. Combined with `<Suspense>`, this drastically reduces Time To Interactive (TTI) and automatically displays UI skeletons without writing repetitive `if (isLoading)` blocks.
- **Partial Hydration / Islands Architecture (Edge Rendering)**: To enforce a Zero Waste System, applications adopting SSR/RSC should prioritize sending JavaScript only for interactive "islands" (e.g., carousels, buttons) while keeping static content (e.g., articles) as pure HTML. Sending megabytes of JavaScript to hydrate static DOM elements wastes CPU cycles and degrades mobile performance.
- **Streaming & Progressive Rendering**: Applications adopting streaming SSR must structure their component trees to maximize early HTML flushing — placing heavy data-dependent subtrees inside dedicated `<Suspense>` shells that stream independently.
- **Adoption Policy**: Server Components and streaming SSR are not currently mandated for Scnehaux enterprise SPAs (which default to CSR). Adoption requires an approved Architecture Decision Record (ADR) justifying the operational complexity trade-off.
- **SSR Hydration Determinism**: Non-deterministic rendering during server-side rendering (SSR) that triggers client-side hydration mismatches is prohibited. Developers must enforce the following rules:
  - **Browser Globals Access**: Referencing client-only globals (`window`, `document`, `localStorage`, `matchMedia`) inside the rendering path is prohibited. Access must be deferred to `useEffect` or synchronized via `useSyncExternalStore` with a server-safe fallback value.
  - **Non-Deterministic Generators**: Using `Date.now()`, `new Date()`, or `Math.random()` to generate DOM content, classes, or keys during rendering is prohibited. Element IDs must be generated using the native React `useId` hook to guarantee matching server and client identifiers.
  - **Locale & Timezone Stability**: Executing dynamic locale or timezone conversions during render without a fixed baseline configuration is prohibited. Locale formatting must be locked to a stable server-client configuration to prevent mismatched output.

---

### Accessibility Integration

> **Document Authority Notice**: Comprehensive accessibility mandates (including Semantic HTML prioritization, Focus Management, Keyboard Interaction, and WAI-ARIA APG compliance) have been consolidated into **[STD-GLB-FE-009 (Accessibility & Internationalization)](STD-GLB-FE-009-accessibility-i18n.md)**.
>
> React components must strictly comply with the universal access principles defined in that authoritative standard.

---

### Form Orchestration

- **Prohibited "Controlled-Only" Patterns**: Enforcing controlled state (`useState` updating key-by-key) for all input fields in complex forms is prohibited due to rendering performance degradation (keystroke input lag). Controlled inputs are permitted only for low-frequency inputs, conditional field switches, or single search bars.
- **Uncontrolled & Hybrid Forms**: Complex or multi-field forms must use uncontrolled components or hybrid form managers (such as React Hook Form) utilizing Refs to isolate rendering boundaries.
- **React 19 Actions Integration**: Applications must leverage React 19 Form Actions (`<form action={actionFn}>`) and standard `FormData` payloads to manage submissions, asynchronous loading states (`useActionState`), and pending transitions (`useFormStatus`) natively.

---

### Async Data Consistency & Race-Condition Governance

> **Document Authority Notice**: Comprehensive network and data access mandates (including HTTP client architecture, AbortController cancellation, Optimistic UI Updates, and Cache Engine usage) have been consolidated into **[STD-GLB-FE-010 (Data Access & Network)](STD-GLB-FE-010-data-access.md)**.
>
> React components must strictly delegate all network IO and caching logic to the patterns defined in that authoritative standard.

---

### Performance Profiling & Monitoring

- **React DevTools Profiler**: Components exhibiting more than 3 unnecessary re-renders per user interaction (renders where no inputs, state, or context values have changed) must be investigated and optimized using the React DevTools Profiler flame graph.
- **React Strict Mode**: Development builds must run with `<React.StrictMode>` enabled to surface impure renders, missing cleanup functions, and deprecated API usage through intentional double-invocation.
- **Production Monitoring**: Real User Monitoring (RUM) must track component-level rendering latency for critical user flows. Components consistently exceeding 16ms render time must be flagged for architectural review. This monitoring must comply with the trace propagation and telemetry rules defined in [STD-GLB-FE-004 (Frontend Observability & Telemetry)](./STD-GLB-FE-004-observability.md#35-frontend-observability--telemetry) and respect the execution boundaries in [STD-GLB-FE-002 (Zero Layout Thrashing)](./STD-GLB-FE-002-performance.md#zero-layout-thrashing-60fps-render-guarantee).

---

## 4. Exceptions

Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk.

### Exception to "External Sync (useEffect Constraints)" (Rule 3.3)

- **Condition for Deviation**: You are initializing or synchronizing a heavy, imperative non-React canvas engine or library (e.g., D3.js, Chart.js, Google Maps) that requires direct DOM manipulation outside of React's render cycle.
- **Mandatory Alternative**: `useEffect` is strictly permitted for this synchronization, provided the hook is isolated within a dedicated wrapper component that _only_ manages the initialization, reference binding, and teardown lifecycle of that specific instance.

### Exception to "Rendering Optimization (Memoization)" (Rule 3.1 & 3.4)

- **Condition for Deviation**: The memory allocation and garbage collection cost of instantiating the `useMemo` hook demonstrably outweighs the CPU cost of the child component re-rendering.
- **Mandatory Alternative**: Omission of `useMemo` is permitted exclusively for trivial, primitive calculations (e.g., fundamental string concatenation, boolean flips) where the output is passed to a leaf node that does not trigger cascading renders.

### Exception to "Form Management (Controlled Components)" (Rule 3.6)

- **Condition for Deviation**: You are integrating a highly complex data-grid engine that manages its own internal virtual DOM and fundamentally requires uncontrolled `ref` assignments to maintain 60FPS scroll performance.
- **Mandatory Alternative**: Uncontrolled forms via `refs` are permitted exclusively for these specific high-density engines, provided they are encapsulated behind a controlled interface boundary exposed to the rest of the React application.

## 5. Enforcement Mechanism

- **Linting Rules**: CI/CD pipelines must enforce strict ESLint suites (including `eslint-plugin-react`, `eslint-plugin-react-hooks`, and `eslint-plugin-jsx-a11y`) with error severity configured for hook dependency validation, accessibility violations, and key stability checks.
- **TypeScript Strictness**: All React projects must compile under `strict: true` with `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` enabled. Type assertions (`as`) must be minimized and justified with inline comments.
- **Telemetry Integration**: Error Boundaries must automatically capture unhandled component errors and transmit them to the centralized logging endpoint complete with tenant and transaction contexts.
- **Waiver Protocol**: Deviations from this standard (such as integrating legacy non-compliant libraries or suppressing lint rules) must be documented in a local project ADR. The Architecture Review Board (ARB) must respond with a review decision within **5 business days** of the ADR submission.
