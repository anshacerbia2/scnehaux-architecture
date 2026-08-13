---
doc_meta:
  id: STD-GLB-FE-001
  title: Enterprise Frontend Technology Stack & Layered Architecture Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-05-21
---

# Enterprise Frontend Technology Stack & Layered Architecture Standard (STD-GLB-FE-001)

---

## 1. Objective & Scope

This standard defines the mandatory frontend technology stack selections, 4-layer structural architecture model, state management taxonomy, rendering systems topology, and routing guidelines for all web applications built within the Scnehaux enterprise.

It establishes strict separation of concerns, framework-agnostic domain logic isolation, and hardware-aligned rendering paths to guarantee performance, maintainability, and security across all codebases.

The scope of this standard applies to all frontend applications, including standalone Single Page Applications (SPAs) and federated micro-frontend portals.

---

## 2. Design Principles

The frontend technology stack prioritizes long-term maintainability, ecosystem maturity, and deterministic build reproducibility. Framework selections are governed by the Technology Lifecycle phases defined in GDC-005.

## 3. Normative Rules

### Technology Stack Definition

To prevent technology fragmentation and ensure consistent platform optimization, all web applications must compile under the following core technologies. Deviations are prohibited unless backed by an approved Architecture Decision Record (ADR).

- **Core UI Framework (React 19+)**: React is the designated framework for UI composition. Applications must target React 19+ to take advantage of native compiler optimizations, asynchronous form actions, and advanced hydration controls.
- **Static Typing (TypeScript)**: TypeScript must be used across all source files, configured with strict compilers.
- **Server State Management (TanStack Query)**: Server-originated data fetching, query caching, and mutations must be managed via TanStack Query.
- **Client-Global State Management (Zustand)**: Global client state (e.g., UI layout states) must be managed using selector-bound Zustand stores.
- **Visual Presentation (CSS Modules & Tailwind CSS)**: CSS Modules must be utilized for core component library isolation. Tailwind CSS is permitted for rapid application layout assembly.
- **Accessible Headless UI (Radix UI)**: Interactive primitives (e.g. `Dialog`, `Dropdown`, `Popover`, `Select`, `Combobox`) must build upon Radix UI primitives to leverage their WCAG 2.2 AA accessibility, keyboard focus traps, and screen reader behaviors. Styling-only layout primitives (e.g. `Box`, `Flex`, `Grid`, `Text`, `Slot`) must remain dependency-free to ensure absolute bundle optimization and styling purity.

---

### Core Architecture Layers

To prevent abstraction leakage, eliminate rendering bottlenecks, and enforce structural boundaries, all frontend applications must organize their codebases and runtime operations into the following four distinct layers.

```
+-----------------------------------------------------------------+
| Layer 1: Application Domain Layer (Agnostic Domain Logic)       |
+-----------------------------------------------------------------+
| Layer 2: Presentation & Composition Layer (Pure UI & CSS)       |
+-----------------------------------------------------------------+
| Layer 3: State & Synchronization Layer (Query Cache & Global)   |
+-----------------------------------------------------------------+
| Layer 4: Infrastructure & Platform Layer (rAF & Web APIs)       |
+-----------------------------------------------------------------+
```

#### Layer 1: Application Domain Layer

- **Responsibility**: Bounded business logic, entity models, input validation schemas, policy evaluations, and user workflows.
- **Architectural Rules**:
  - The Domain Layer must be decoupled from UI frameworks. Importing React packages, JSX templates, or styling engine APIs is prohibited.
  - All domain rules and validations must be written as pure, side-effect-free TypeScript functions, enabling isolated unit testing.

#### Layer 2: Presentation & Composition Layer

- **Responsibility**: UI markup template assembly, component composition, style containment, and static transition declarations.
- **Architectural Rules**:
  - Components must derive styling from platform-wide design tokens. Declaring hardcoded values is prohibited.
  - Declaring global CSS selectors inside individual component styles is prohibited. Style boundaries must utilize CSS Modules or unique class name prefixes.
  - Interactive elements must be keyboard navigable and support semantic ARIA attributes to satisfy WCAG 2.2 AA standards.

#### Layer 3: State & Synchronization Layer

- **Responsibility**: Cache synchronization, client-global memory state management, and mutation transaction control.
- **Architectural Rules**:
  - **Server State**: Managed exclusively by cache-aware engines (such as TanStack Query). Local mirroring of server state is prohibited.
  - **Global State**: Restricted to application-wide client concerns (such as UI layout states). High-frequency mutations must use optimized stores (such as Zustand).
  - **Optimistic Updates**: Must include programmatic transactional rollbacks to revert the UI state if the server operation fails.

#### Layer 4: Infrastructure & Platform Layer

- **Responsibility**: Low-level browser adapters, HTTP client configurations, route authorization guards, event listeners, and hardware-synchronized rendering.
- **Architectural Rules**:
  - **HTTP Interceptors**: All outgoing requests must route through a centralized wrapper injecting authorization tokens, tenant headers, and correlation trace IDs (e.g. `X-Trace-Id`).
  - **V-Sync & Motion Schedulers**: Active animations, drag-and-drop operations, and coordinate calculations must bypass UI framework rendering lifecycles. They must execute mutations directly on DOM elements using stable references (Refs) scheduled within `requestAnimationFrame` (rAF).
  - **Event Target Registry**: Low-level browser event subscriptions (such as keyboard keys or resize triggers) must bind to infrastructure handlers that enforce cleanup on component unmounting.

---

### State Taxonomy

All data elements inside a frontend application must be categorized into one of five distinct state classifications. Combining these classifications or managing them through incorrect storage models is prohibited.

```
+----------------------------------------------------------------------------+
| State Class    | Core Engine / Storage Model                               |
+----------------|-----------------------------------------------------------|
| Server State   | TanStack Query Cache (QueryClient)                        |
| Client-Global  | Zustand Store (Selector-bound)                            |
| URL State      | Browser History API (URL Query & Path Parameters)         |
| Form State     | Uncontrolled Refs / Local Form Schema Controller          |
| Ephemeral      | Local useState / useReducer (Component Scope)             |
+----------------|-----------------------------------------------------------+
```

#### Server State & Cache Topology

- **Cache Ownership**: The server state cache (QueryClient instance) represents a read-only local replica of remote databases.
- **Stale Time Configuration**: Queries must establish a default `staleTime` of at least 5000ms. Defaulting `staleTime: 0` is prohibited, as it triggers redundant server-bound requests on every component re-render or layout change.
- **Cache Invalidation**: Post-mutation invalidations must target specific queries (`queryClient.invalidateQueries`) rather than executing global cache flushes.
- **Mutation Orchestration**: Asynchronous mutations must handle success, failure, and execution states explicitly. Optimistic updates must define a rollback mutation (using `onMutate` to store previous values and `onError` to restore the state) to prevent visual state drift during network failure.

#### Client-Global State

- **Zustand Selector-Bound Stores**: Client-global state must use selector-based state managers (such as Zustand). Importing global state objects directly without utilizing selector functions (e.g. `useAuthStore(state => state.user)`) is prohibited, as it forces the consuming component to re-render on any unrelated store mutation.

#### URL State

- **Single Source of Truth**: Sorting parameters, active tab IDs, search filter keywords, and pagination page numbers must be stored in URL parameters (path or query params) rather than local React state. Using URL state ensures that page states are deep-linkable, bookmarkable, and persist across navigation cycles.

#### Form State

- **Uncontrolled Isolation**: Large-scale or data-heavy inputs must keep form values isolated within DOM elements using Refs or specialized form state engines. Running key-by-key component re-renders for multi-field forms is prohibited.

#### Ephemeral State

- **Component-Local Scope**: Ephemeral UI states (such as dropdown expanded toggles, modal open states, or local list filter selections) must be stored inside component-local state (`useState`).

---

### Rendering Systems Architecture

Applications must align their component hierarchy with modern rendering strategies to optimize Core Web Vitals, minimize Time to Interactive (TTI), and reduce Cumulative Layout Shift (CLS).

#### Rendering Strategy Selection

- **Client-Side Rendering (CSR)**: Mandated for restricted administrative portals, authenticated dashboards, and applications operating behind firewalls.
- **Server-Side Rendering (SSR) & Streaming Hydration**: Required for public landing pages, content-heavy marketing directories, and search-engine-indexed routes to ensure fast First Contentful Paint (FCP).

#### Async Boundaries & Suspense Placement

- Components performing asynchronous data fetching or dynamic module resolution must be wrapped in a `<Suspense>` boundary containing a lightweight fallback skeleton.
- **Layout Stabilization**: Suspense fallbacks must have fixed dimensions matching the expected height and width of the resolved components to prevent Cumulative Layout Shift (CLS) when components hydrate.
- **Isolated Streaming**: Heavy components must be placed within separate `<Suspense>` boundaries to allow progressive streaming of HTML, preventing slower server queries from blocking the load cycle of static layout components.

---

### Routing Architecture

Routing must enforce page isolation, secure authorization boundaries, and streamlined user navigation.

#### Nested Layout Boundaries

- Router hierarchies must implement nested layouts, sharing static scaffolding (such as sidebars, headers, and footer components) while rendering dynamic child routes within isolated Outlet slots.
- Layout boundaries must not contain business logic. They serve as structural scaffolds and error containment boundaries.

#### Authentication & Authorization Boundaries

- **Route Authorization Guards**: Routes requiring active sessions must be wrapped in route-level guards. These guards evaluate user authorization within the infrastructure layer before rendering target page templates.
- **Unauthorized Redirection**: Guard failures must trigger immediate redirection to authentication endpoints, injecting the original request path as a query parameter (e.g., `?redirect=/dashboard`) to enable automatic return mapping post-login.

#### Prefetching Policies

- Standard page links (`<Link>`) must implement viewport-aware prefetching to download destination route assets before user interaction, maximizing transition responsiveness.
- High-volume routes containing expensive computations must disable automatic prefetching (`prefetch={false}`) to conserve client-side bandwidth.

---

### Directory Layout & Dependency Mapping

Application repositories must map their directory structures directly to the defined architectural layers:

```
src/
├── core/         # Map to Layer 3 (State) and Layer 4 (Infrastructure)
├── domain/       # Map to Layer 1 (Application Domain)
└── features/     # Map to Layer 2 (Presentation) and local routing routes
```

#### Strict Dependency Boundaries

- **No Inward UI Dependencies**: Code within `src/core/` and `src/domain/` must have zero dependencies on code within `src/features/` or any UI-framework packages (e.g. React).
- **Feature Isolation**: Features residing in `src/features/[feature-name]/` must be self-contained. Direct cross-imports between separate feature folders are prohibited. Shared utilities and components must reside in a centralized `src/components/` or `src/utils/` directory.

---

## 4. Exceptions

None. All frontend technology stack mandates apply universally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

- **Boundary Linting (ESLint & Dependency Cruiser)**: Build pipelines must run static analysis tools (e.g. Dependency Cruiser) and ESLint plugins (`eslint-plugin-import`) configured with strict boundary rules to block imports that violate the directory layering layout (such as UI elements importing domain logic or cross-feature imports).
- **Automated Visual Token Scanner**: A custom pre-commit and CI scanner script must parse all CSS/SCSS/TSX files, flagging any hardcoded HEX, RGB, or HSL color values and blocking the commit if styling rules do not resolve through centralized design tokens.
- **Waiver Protocol**: Architectural deviations (such as introducing third-party state managers or custom rendering layers) must be documented in a local project ADR and approved by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
