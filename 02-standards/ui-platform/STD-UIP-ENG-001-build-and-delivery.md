---
doc_meta:
  id: STD-UIP-ENG-001
  title: UI Platform Build & Delivery Standards
  owner: Principal UI/UX Architect
  version: 2.0.0
  status: proposed
  classification: public
  governed_by: [ADR-UIP-PLT-001]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-28
---

# UI Platform Build & Delivery Standards (STD-UIP-ENG-001)

> **Review draft:** this revision records the agreed release contract. Existing metadata is not evidence that these new rules have passed principal review or CI implementation.

## 1. Objective & Scope

This standard governs the build and distribution of `@scnx/core-ui` and `@scnx/system`. A source test proves source behavior; a consumer test against a packed release proves the public package contract. Neither substitutes for the other.

## 2. Design Principles

- **Contract honesty:** documentation states only behavior demonstrated by a repeatable test or a clearly labeled design decision.
- **Reproducibility:** the release candidate is the immutable package artifact tested before publication.
- **Measured performance:** budgets name the import scenario, theme, browser, device class, measurement method, and regression threshold. Raw unminified library bytes are reported separately from consumer payload.
- **Fail closed:** a required test that does not run is a failed gate, not an omitted gate.

## 3. Normative Rules

### 3.1 Source quality gate

- Run type checking, linting, and executable unit/interaction tests for state machines and public primitive behavior.
- Test the keyboard, focus, ARIA, reduced-motion, and cleanup contracts applicable to each stable widget. Automated accessibility checks supplement, but do not replace, manual assistive-technology evaluation.
- Run visual regression for supported component states across the declared theme and browser matrix. A changed snapshot requires review; a missing runner blocks the release.
- Contrast checks fail the build for declared foreground/background pairs in every supported theme and state. Unspecified arbitrary consumer combinations are outside this guarantee.
- Treat Panda as a producer build tool. Verify that `@scnx/core-ui` contains no Panda callsites and exclude its source from Panda scanning. A consumer never runs Panda to render published components.
- Diagnose declaration-build heap growth and record peak memory. Increasing `--max-old-space-size` is a temporary diagnostic aid, not a fix or memory budget.

### 3.2 Packed-package quality gate

Build both packages, create tarballs with the pinned `pnpm pack` command, and install them in consumers with no workspace or source alias. Packed manifests MUST contain publishable versions instead of `workspace:` ranges. Against those installed artifacts, verify:

1. Every documented JS, type, CSS, theme, Sass, font, and `@scnx/system/tokens/*` export resolves in the declared module formats.
2. Components render with their expected styles after the composition root imports aggregate component CSS and the selected theme CSS once. Component JavaScript and remotes do not inject another copy. The consumer does not compile library Sass or run Panda.
3. Every required `--ds-*` reference resolves in its intended theme scope. Validate grammar at the consuming CSS property after substitution. Any unresolved reference, invalid substituted property, or shadow-key mismatch fails the build.
4. SSR and React Server Component consumers import server-safe entries and receive explicit `"use client"` boundaries for client entries. Source-file-name or hook-name regexes are not a release contract.
5. `fixtures/federation/host` with `remote-a` and `remote-b` installs packed artifacts. The host owns explicit singleton keys for React, React DOM, and every context-bearing UI request; `requiredVersion` comes from manifests; remotes remain lazy. Both load orders retain one React/context identity, exactly one aggregate component stylesheet content hash, exactly one selected theme asset, deterministic layers, and scoped portals.
6. A strict Content Security Policy works without `unsafe-eval`; any inline script or style has a documented host-controlled nonce/hash strategy or is externalized.

### 3.3 Payload and runtime evidence

- Publish raw, minified, gzip/Brotli, and parsed-size measurements for defined consumer import scenarios, including a single component, a layout, and a representative page. Identify the tool and incremental consumer cost, compare with an approved baseline, and record material regressions.
- Capture interaction traces for dynamic-height transitions. A layout read is permitted when required for behavior, but claims about forced layout count, frame rate, and theme-switch latency require named scenarios and trace evidence.
- Do not claim `0` reflows, fixed 60 FPS, a universal `<2 KB` or 12 KB budget, or sub-50 ms theme switching without the corresponding supported-scenario evidence.
- Library minification remains deferred to the consumer build as decided in ADR-UIP-BLD-001; measure final consumer output, not only raw `dist` files.

### 3.4 Distribution and release report

- Published ESM/CJS formats, React peer ranges, subpaths, CSS assets, token exports, and fonts must match the package manifest and pass packed-package resolution tests.
- A stable release publishes a conformance report linking source-test results, packed-package tests, Component Accessibility Conformance Reports and known limits, contrast pairs, visual diffs, payload measurements, API changes, and supported consumer scenarios. Component reports are not labeled VPATs and do not certify a complete page.
- A failed or missing required gate prevents promotion to the stable channel. Experimental components may be excluded from stable exports with their scope documented.

## 4. Exceptions

Exceptions name the affected contract, consumer impact, expiry, and reviewer. They cannot convert an untested claim into a guarantee.

## 5. Enforcement Mechanism

The CI pipeline executes the source gate and packed-package gate, stores their evidence, and blocks stable publication on failures. The initial P0 implementation of these gates is tracked in the UI Platform roadmap; this draft does not claim that the current repository already satisfies them.
