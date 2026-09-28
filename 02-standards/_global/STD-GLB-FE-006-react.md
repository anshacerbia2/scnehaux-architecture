---
doc_meta:
  id: STD-GLB-FE-006
  title: Enterprise React Development Standard
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

# Enterprise React Development Standard (STD-GLB-FE-006)

> **Review candidate:** ADR-GLB-FE-010 must be accepted before this major revision becomes active.

## 1. Objective & Scope

This standard defines React component boundaries, state ownership, effects, reference identity, context, server/client entry contracts, error containment, and measured rendering behavior for applications and shared libraries.

## 2. Design Principles

1. **Semantic correctness:** component APIs preserve native HTML and accessible widget behavior.
2. **Local ownership:** state and side effects stay at the smallest boundary that owns them.
3. **Evidence-based optimization:** memoization, virtualization, and scheduling respond to semantic identity or measured cost.
4. **Explicit environments:** server-safe and client-only modules declare their runtime contract.
5. **Recoverable behavior:** subscriptions, transitions, and failures have cleanup and fallback paths.

## 3. Normative Rules

### 3.1 Component and state boundaries

Components keep rendering concerns separate from domain policy and network authority. State has one owner. Values derived from props or state are computed rather than mirrored into independent state unless the API explicitly captures a snapshot.

Controlled and uncontrolled modes have distinct, documented contracts. A component does not switch modes after mount without an explicit supported transition.

### 3.2 Reference identity and memoization

`useMemo`, `useCallback`, and `React.memo` are used when at least one condition holds:

- reference identity is part of an effect, context, subscription, or memoized-child contract;
- a computation exceeds an approved interaction budget in a representative profile;
- an uncompiled boundary requires stable identity;
- measurement demonstrates a material rendering regression.

New objects, arrays, or closures in render do not require memoization by themselves. Memoization records dependencies correctly and is removed when it adds complexity without semantic or measured benefit.

When React Compiler is enabled, teams follow its diagnostics and preserve manual memoization only for measured computation caching, external identity boundaries, or explicit compiler bailout cases.

### 3.3 Context and shared state

Context carries cohesive state whose update frequency is appropriate for all subscribers. Frequently changing values and stable actions may use separate contexts when profiling or API semantics justify the split.

A shared package preserves one context module identity across supported Module Federation consumers. Host/remote fixtures prove that identity.

Server-originated data uses the approved data-access cache. Product-global client state uses an approved store only when composition or local state cannot own it.

### 3.4 Effects and browser resources

Effects synchronize React with an external system. Derived render values remain outside effects. Every listener, observer, timer, animation frame, subscription, and in-flight operation has cleanup tied to its owner.

Layout effects are reserved for behavior that must observe or update layout before paint. Their interaction trace documents cost when they run on a critical path.

### 3.5 Server and client modules

Server-safe entries contain no browser globals, event handlers, client hooks, or client-only providers. Client entries declare `"use client"` explicitly. Build output preserves this boundary.

Filename lists and hook-name regexes are diagnostic tools and cannot define the release contract. Packed SSR/RSC consumers supply the evidence.

SSR output avoids unstable values from time, randomness, locale, or browser-only state unless a deterministic server/client baseline exists. Element IDs shared between server and client markup come from `useId`.

An application adopts React Server Components or streaming SSR only through a decision recorded in its SAD or an ADR.

### 3.6 Composition and public APIs

Public components inherit relevant native attributes and refs. Component-only props are consumed before DOM spread. Impossible prop combinations use discriminated unions.

Compound widgets use composition when parts share behavior and anatomy. The UI Platform polymorphism rules live in STD-UIP-PRM-001 and remain bounded per component.

Public component props are explicitly typed. `any` is prohibited in exported prop types; `unknown` is narrowed before use.

Every rendered list item has a stable `key` derived from domain identity. Array indexes are used as keys only for static lists that never reorder, insert, or remove items.

### 3.7 Transitions and asynchronous work

Non-urgent rendering may use `useTransition` or `useDeferredValue` when a named scenario shows user-input contention. These APIs do not replace algorithmic improvement or virtualization.

Transition components handle completion events, a bounded timeout fallback, interruption, reduced motion, and unmount cleanup. Callback order is tested.

### 3.8 Error containment

Critical route or feature boundaries provide recoverable error UI and a reset path. Caught failures emit approved telemetry without secrets or sensitive content. A package component documents which errors it contains and which propagate to the consumer.

### 3.9 Performance evidence

A rendering budget identifies component tree, interaction, data size, React mode/compiler state, browser, device class, tool, baseline, and threshold. Universal render-count, tree-depth, allocation, or 16 ms mandates have no authority outside a defined scenario.

### 3.10 Supported React line and security baseline

- **Supported line:** applications and shared packages target React 19. `react` and `react-dom` resolve to the same version. A shared package declares both as peer dependencies with identical ranges, and packed-consumer fixtures prove the lowest and highest versions in that range.
- **Security baseline:** the minimum acceptable version is not fixed in this standard. It is derived on every CI run from the published advisories that apply to the resolved dependency graph.
- **Audit input:** the audit reads the lockfile-resolved graph, or an SBOM generated from it, including transitive and vendored packages. Checking direct dependencies in `package.json` alone does not satisfy this rule.
- **Server components:** `react-server-dom-*` packages are audited as their own entries. Because a meta-framework may bundle them inside its own package, the audit also checks the resolved framework version against that framework's advisories.
- **Blocking threshold:** an advisory rated high or critical against a resolved React, React DOM, `react-server-dom-*`, or meta-framework version blocks merge and release until the resolved version is patched. A moderate advisory is reported and resolved within 30 days.

## 4. Exceptions

An imperative integration may use a dedicated wrapper with effects or layout effects when the external API requires direct DOM ownership. The wrapper must define initialization, update, teardown, error, SSR, and accessibility behavior.

## 5. Enforcement Mechanism

- TypeScript compiles with `strict`, `noUncheckedIndexedAccess`, and `exactOptionalPropertyTypes`.
- ESLint runs `eslint-plugin-react`, `eslint-plugin-react-hooks` (including rules-of-hooks and exhaustive-deps), and `eslint-plugin-jsx-a11y` as errors. A suppression names its reason on the same line.
- Lint rules enforce stable list keys, no `any` in exported prop types, and file naming: PascalCase for component files, kebab-case for directories, hooks, contexts, and other non-component files.
- Development builds render inside `<React.StrictMode>`.
- Source tests cover controlled state, cleanup, error reset, keyboard/focus behavior, and transition interruption.
- Profiler or browser traces enforce only scenario-defined performance budgets.
- Packed consumers verify public types, refs, DOM props, server/client entries, hydration, and supported peer ranges.
- Federation fixtures verify React and context identity.
- A dependency audit over the lockfile-resolved graph or its SBOM, with framework advisories for server-component packages, enforces section 3.10 on every CI run.

A required check that does not execute blocks stable promotion.
