---
doc_meta:
  id: STD-GLB-FE-002
  title: Enterprise Frontend Performance and Rendering Standard
  owner: Principal Frontend Architect
  version: 2.0.0
  status: proposed
  classification: restricted
  governed_by: [ADR-GLB-FE-010]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-28
---

# Enterprise Frontend Performance and Rendering Standard (STD-GLB-FE-002)

> **Review draft:** universal zero-allocation, zero-reflow, and fixed-FPS claims are replaced with measured, scenario-specific contracts.

---

## 1. Objective & Scope

This standard defines the mandatory performance limits, layout safety mechanics, memory management rules, and polymorphic constraints for all browser-executed frontend applications and shared component libraries within the Scnehaux enterprise ecosystem.

It establishes rendering efficiency and memory discipline as measurable platform behaviors. Page-level Web Vitals are evaluated in representative consumers; component trace budgets name the interaction, browser, device class, and workload.

The scope of this standard applies to all production builds, design systems, and client runtime engines.

---

## 2. Design Principles

All frontend performance architectures must strictly adhere to the Supreme Frontend Governance principles:

- **Measured Cost**: Optimize interactions whose traces show material work, rather than mandating unmeasured zero-allocation or zero-render rules.
- **Determinism Over Cleverness**: Output must be predictable from input. Hidden side-effects and implicit behaviors are prohibited.
- **Semantic Structure**: Extra DOM nodes require a semantic, layout, or accessibility purpose. Their measured cost is balanced against the interaction contract.

## 3. Normative Rules

### Layout Measurement and Frame Budget

To prevent dropped frames and visual stutter during user interactions:

- **Controlled Geometry Reads**: Avoid repeated read/write interleaving in high-frequency events. A measured synchronous read is permitted when necessary for behavior; capture forced-layout count and frame cost in a named interaction trace.
- **Observer-First Monitoring**: Use `IntersectionObserver` or `ResizeObserver` when their observation semantics fit. They do not eliminate browser layout or automatically replace one-time geometry measurements.

### Memory & Reference Stability (React Ecosystem)

- **Reference Stability**: Stabilize values when identity affects memoized children or an effect, and when profiling shows meaningful cost. `useMemo` and `useCallback` also have overhead and are not mandatory for every render-scope value.
- **Batching Writes**: High-frequency layout writes are grouped when traces show read/write interleaving or missed frames. RAF is one scheduling tool; ordinary React state updates need not all use it.
- **Dynamic Event Lifecycle Deregistration**: Event listeners and observers are cleaned up when their owning lifecycle ends. Hidden components should not retain needless global work.

---

### Heap Memory Allocation and Reference Stability

To reduce Garbage Collection (GC) pauses and prevent memory leaks in long-running browser sessions:

- **Allocation Discipline**: Avoid repeated expensive serialization or allocation in a measured hot path. An allocation by itself is not a release failure.
- **Stable Constants**: Hoist genuinely static values when identity matters to consumers or measurement supports the change.
- **Derived State Classification**:
  - _Primitive Derived State_: Trivial calculations may be computed inline; memoization is justified by measured or semantic identity needs.
  - _Non-Primitive Derived State_: Memoize when the computation or reference identity is material to a consumer; a new array is not by itself proof of a regression.
- **Cleanup Enforcement**: Subscriptions, timers, observers, and window listeners release owned resources on unmount or when their registration is replaced.

---

### Polymorphic Rendering Safety

To preserve rendering efficiency in reusable component trees and layout containers:

- **Choose for semantics first**: A fixed native tag, dynamic `as`, or `asChild` must preserve the documented DOM, ref, and event contract.
- **Measure hot paths**: Where polymorphic composition appears in a measured high-frequency path, compare allocations and render cost before constraining the API. Cloning alone is not a measured budget.

---

### Style & Token Contract Compliance

To protect the host application environment from styling collision:

- **Strict Token Binding**: Shared component visual intent resolves through Tier-2 semantic tokens or justified Tier-3 aliases. Tier-1 values remain compiler inputs, not direct component dependencies.
- **Layout Encapsulation**: Shared selectors and custom properties use a documented root or namespace; CSS Modules are one possible technique. Cascade layers alone do not scope selectors.

---

## 4. Exceptions

An exception names the affected consumer, interaction, measurement, risk, owner, and review date. Accessibility requirements are not waived by a DOM-node budget. A necessary synchronous geometry read is documented and measured, not automatically treated as a violation.

## 5. Enforcement Mechanism

- Consumer scenarios declare their device/browser profile, interaction workload, metric, baseline, and threshold before a numeric gate is enforced. Core Web Vitals are measured on representative pages, not inferred from a library build.
- Package budgets cover each supported import path and its incremental cost in a consumer bundle. Remote and application budgets belong to their owning systems.
- CI records bundle changes and browser traces for material regressions; thresholds are ratified from baseline data. A universal Lighthouse score or unscoped byte limit is not a substitute for a scenario contract.
- Code review checks event-listener cleanup, dynamic cloning, geometry reads, and style scope when those paths are changed.
