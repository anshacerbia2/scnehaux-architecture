---
doc_meta:
  id: ADR-GLB-FE-005
  title: ADR-GLB-FE-005 Dual-Engine State Management (Zustand & TanStack Query)
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-005: Dual-Engine State Management (Zustand & TanStack Query)

---

## 1. Title

Dual-Engine State Management (Zustand & TanStack Query)

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                     |
| ---------- | -------- | ------------ | ------------------------- | ---------------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Principal Frontend Architect |

## 3. Context

Global state management has historically been the primary source of rendering bottlenecks and developer friction in our React applications. Relying on monolithic state containers (like Redux) for both remote API data and ephemeral UI state has resulted in excessive boilerplate and over-fetched payloads. The native React Context API triggers severe rendering issues due to its inability to isolate selector updates.

## 4. Decision Drivers

We require a standardized approach to separate the concept of "Server State" from "Client State" using modern, high-performance engines. Zustand's selector-based architecture allows components to subscribe only to specific slices of state, guaranteeing zero-waste renders. TanStack Query automates background refetching and cache invalidation.

## 5. Decision

We will adopt a **Dual-Engine State Management Strategy**, strictly separating state into two isolated paradigms: Server-State Management via **TanStack Query** (mandatory for all asynchronous data fetching/caching) and Client-State Management via **Zustand** (mandatory for complex, globally shared UI state).

## 6. Consequences

- **Positive**: Render performance is protected via strict selectors, and developer velocity is increased due to massive boilerplate reduction compared to Redux.
- **Negative**: Debugging state now requires inspecting two different DevTool extensions instead of a unified Redux timeline.

### Negative / Risks

- **Paradigm Shift Friction**: Engineers accustomed to storing everything in a single Redux store must unlearn that pattern and trust the TanStack Query cache.
- **State Leakage**: Developers might accidentally duplicate server state inside Zustand, leading to desynchronization.

### Operational

- TanStack Query must be configured with a global stale time and unified error handling wrappers as defined in Data Access standards.
- Zustand stores must be heavily granular to prevent unnecessary re-renders.

## 7. Compliance Impact

### Related Standards

- STD-GLB-FE-002 (React Standards)
- [STD-GLB-FE-010 (Data Access)](../../02-standards/_global/STD-GLB-FE-010-data-access.md)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **Redux / Redux Toolkit**: Rejected. The underlying Flux architecture forces a level of indirection and boilerplate that is disproportionate for 90% of our enterprise CRUD applications.
- **React Context API (Global)**: Rejected for global state. Context does not support render-bailing based on object properties (selectors), violating our strict performance benchmarks.
- **Jotai / Recoil**: Rejected. Introduces mental overhead that is unnecessary for standard enterprise dashboards compared to Zustand's familiar structured store.
