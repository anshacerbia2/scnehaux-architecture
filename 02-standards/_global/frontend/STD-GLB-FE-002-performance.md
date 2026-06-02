---
doc_meta:
  id: STD-GLB-FE-004
  title: Enterprise Frontend Performance and Rendering Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-20
---

# Enterprise Frontend Performance and Rendering Standard (STD-GLB-FE-004)

---

## 1. Objective & Scope

This standard defines the mandatory performance limits, layout safety mechanics, memory management rules, and polymorphic constraints for all browser-executed frontend applications and shared component libraries within the Scnehaux enterprise ecosystem. 

It establishes rendering efficiency and memory discipline as core platform behaviors, targeting a consistent 60FPS presentation, Cumulative Layout Shift (CLS) $\le 0.1$, and Interaction to Next Paint (INP) $\le 200ms$ across all portals.

The scope of this standard applies to all production builds, design systems, and client runtime engines.

---

## 2. Design Principles

All frontend performance architectures must strictly adhere to the Supreme Frontend Governance principles:
- **Zero Waste System**: Execution must be mercilessly efficient. No unnecessary renders, no unnecessary DOM nodes, and no unnecessary memory allocations. Every line of execution must justify its cost.
- **Determinism Over Cleverness**: Output must be predictable from input. Hidden side-effects and implicit behaviors are prohibited.
- **Zero Trash DOM**: Layouts must be structurally pristine. Redundant wrappers and meaningless nodes degrade rendering performance and must be eliminated.

## 3. Normative Rules

### Zero Layout Thrashing (60FPS Render Guarantee)
To prevent dropped frames and visual stutter during user interactions:
- **Synchronous Geometry Reads Prohibited**: Do not query layout geometry properties (such as `getComputedStyle`, `offsetHeight`, `offsetWidth`, `clientHeight`, `scrollHeight`, or `getBoundingClientRect`) synchronously during high-frequency events (e.g. `onScroll`, `onMouseMove`, `onResize`).
- **Observer-First Layout Checks**: Use asynchronous browser APIs (such as `IntersectionObserver` or `ResizeObserver`) to monitor element visibility and dimensional modifications instead of binding heavy event listeners.

### Memory & Reference Stability (React Ecosystem)
- **Zero Inner Scope Allocations**: Prohibit declaring new function expressions, object literals, or array literals directly inside the component render cycle (such as inline event handlers or properties in templates), unless they are stabilized using reference stabilization mechanisms (e.g., React `useCallback` or `useMemo`). This guarantees stable memory references and prevents unnecessary cascading re-renders of memoized child components.
- **Batching Writes**: Layout updates and DOM manipulations must be batched and synchronized using the browser V-Sync lifecycle via `requestAnimationFrame` (RAF) or framework-specific scheduler queues (such as React's concurrent batching).
- **Dynamic Event Lifecycle Deregistration**: All dynamic event listeners (such as click-outside handlers, window resize hooks, or document-level keyboard event captures) must be unsubscribed immediately when the associated component changes state to closed or hidden, preventing hidden components from running layout calculations in the background.

---

### Heap Memory Allocation and Reference Stability

To reduce Garbage Collection (GC) pauses and prevent memory leaks in long-running browser sessions:
- **Zero Inner Scope Allocations**: Prohibit declaring new function expressions, object literals, or array literals directly inside the component render cycle (such as inline event handlers or properties in templates), unless they are stabilized using reference stabilization mechanisms (e.g., React `useCallback` or `useMemo`).
- **Stable Constants**: Static data arrays, configurations, and unchanging callback targets must be declared outside the component rendering function scope to guarantee reference stability.
- **Derived State Classification**:
    *   *Primitive Derived State*: Direct calculations resulting in primitive values (such as numbers, strings, or booleans, e.g., checking length or active IDs) must be computed directly inline without memoization.
    *   *Non-Primitive Derived State*: Computations that generate new array or object references (such as `.filter()`, `.map()`, or object factories) must be stabilized (e.g., using `useMemo` in React) to prevent downstream child components from undergoing unnecessary update cycles due to reference mismatches.
- **Cleanup Enforcement**: All component subscription or registration patterns utilizing asynchronous loops, intervals, timers, observers, or window listeners must execute a teardown lifecycle callback to clear all reference allocations on component unmount or state transitions.

---

### Polymorphic Rendering Safety

To preserve rendering efficiency in reusable component trees and layout containers:
- **Enforce Dynamic Tag Polymorphism**: Elements requiring polymorphic representation must use the dynamic tag pattern (e.g. `const Component = as || 'div'`) as the primary composition standard in performance-sensitive cycles.
- **Restrict Children Cloning**: The `asChild` composition pattern utilizing child element cloning and array mapping is prohibited in high-frequency rendering loops (such as animations, transitions, or active drag-and-drop zones) due to the CPU execution overhead of dynamic prop merging and array traversal.
- **Static Exemption**: The use of `asChild` composition is restricted to static document boundaries and layouts where rendering frequency is near-zero.

---

### Style & Token Contract Compliance

To protect the host application environment from styling collision and guarantee brand consistency:
- **Strict Token Binding**: Components must only use color, dimension, and motion values mapped to Tier-1 or Tier-2 custom properties (`--ds-*`). Hardcoding hexadecimal colors or ad-hoc style values is prohibited.
- **Layout Encapsulation**: Style modifications must use local CSS Modules or scoped custom property values, safeguarding the host application environment from layout contamination.

---


## 4. Exceptions

Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk. 

### Exception to "Zero Layout Thrashing" (Rule 3.1)
- **Condition for Deviation**: You are implementing a high-frequency, physics-based interaction engine (e.g., 60FPS Drag-and-Drop, or real-time Canvas overlay) where calculating immediate bounding box coordinates is strictly required before the next paint cycle.
- **Mandatory Alternative**: You must implement **Double-Sync Measurement**. Read all layout geometries in a single synchronous batch, cache the coordinates in a mutable reference, and execute all corresponding DOM mutations inside the subsequent `requestAnimationFrame` queue. Synchronous reads followed immediately by synchronous writes are still strictly prohibited.

### Exception to "Zero Trash DOM" (Rule 2.1)
- **Condition for Deviation**: Additional, non-visual DOM wrapper elements are strictly required to construct a valid WAI-ARIA interaction model or to manage assistive technology focus.
- **Mandatory Alternative**: Provide explicit documentation linking the wrapper nodes to the specific WCAG success criterion. Accessibility constraints permanently waive the performance penalty of additional DOM depth.

### Exception to "Heap Memory Allocation" (Rule 3.2)
- **Condition for Deviation**: The overhead of allocating a memoization hook (`useMemo` or `React.memo`) demonstrably exceeds the cost of allowing the child component to re-render.
- **Mandatory Alternative**: The calculation must be mathematically trivial (e.g., string concatenation or boolean checks) and the child component must be a leaf node (no further cascading updates). Performance claims must be supported by DevTools Profiler trace evidence attached to the Pull Request.

## 5. Enforcement Mechanism

- **Lighthouse CI Budget Gates**: Build pipelines must execute Lighthouse CI (`lhci`) checks against static assets on every pull request. Budgets must be defined in `lighthouserc.json` and enforce a minimum score of `95` on the Performance category and block builds if Cumulative Layout Shift (CLS) exceeds `0.1` or Largest Contentful Paint (LCP) exceeds `2500ms`.
- **Web-Vitals CLI Integration**: Pull requests deploying changes to core user paths must execute automated headless browser tests using the Web-Vitals CLI. The build must fail if Interaction to Next Paint (INP) under simulated interactions exceeds `200ms`.
- **Bundle-Size Thresholds & Budgets**: Automated bundle-size budget checks (using tools like `bundlesize` or `size-limit`) must run on every build compilation:
  - *Core Shared UI Library*: Capped at `50KB` gzipped.
  - *Independent Remote Micro-Frontends (MFEs)*: Capped at `150KB` for initial bundle size, and `100KB` for individual lazy-loaded chunks.
  - *Build Failure*: If a pull request exceeds these budgets by more than `5%`, the build must fail.
- **Code Review Audits**: Component pull requests introducing new global event listeners or dynamic element cloning must explicitly document cleanup lifecycles and performance justifications.
