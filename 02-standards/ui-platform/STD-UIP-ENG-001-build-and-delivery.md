---
doc_meta:
  id: STD-UIP-ENG-001
  title: UI Platform Build & Delivery Standards
  owner: Principal UI/UX Architect
  version: 2.0.0
  status: approved
  classification: public
  governed_by: [PAD-PLT-003]
  authorized_by: [ADR-UIP-PLT-001]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-29
---

# UI Platform Build & Delivery Standards (STD-UIP-ENG-001)

> **Implementation boundary:** this approved release contract does not establish that existing packages pass its CI and consumer gates.

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
- Contrast checks fail the build for declared foreground/background pairs in every supported theme and state: WCAG 2.2 SC 1.4.3 (4.5:1 for normal text, 3:1 for large text) and SC 1.4.11 (3:1 for user interface components and meaningful graphics). APCA results may be recorded as research evidence and never replace this gate. Unspecified arbitrary consumer combinations are outside this guarantee.
- Treat Panda as a producer build tool. Verify that `@scnx/core-ui` contains no Panda callsites and exclude its source from Panda scanning. A consumer never runs Panda to render published components.
- Diagnose declaration-build heap growth and record peak memory. Increasing `--max-old-space-size` is a temporary diagnostic aid, not a fix or memory budget.

### 3.2 Packed-package quality gate

Build both packages, create tarballs with the pinned `pnpm pack` command, and install them in consumers with no workspace or source alias. Packed manifests MUST contain publishable versions instead of `workspace:` ranges. Against those installed artifacts, verify:

1. Every documented JS, type, CSS, theme, Sass, font, and `@scnx/system/tokens/*` export resolves in the declared module formats.
2. Components render with their expected styles after the composition root imports aggregate component CSS and the selected theme CSS once. Component JavaScript and remotes do not inject another copy. The consumer does not compile library Sass or run Panda.
3. Every required `--ds-*` reference resolves in its intended theme scope. Validate the substituted value at the consuming CSS property. Every emitted `--ds-*` name parses against the STD-UIP-TKN-001 grammar, and every public theme emits the identical Tier-2 key set, including `effect.shadow.low|medium|high|overlay|focus`. Any unresolved reference, invalid substituted value, unparseable name, or key-set mismatch fails the build.
4. SSR and React Server Component consumers import server-safe entries and receive explicit `"use client"` boundaries for client entries. Source-file-name or hook-name regexes are not a release contract.
5. `fixtures/federation/host` with `remote-a` and `remote-b` installs packed artifacts and follows ADR-GLB-FE-012. The host shares `react`, `react-dom`, `@scnx/core-ui`, and every other context-bearing public entry as singletons with a strict compatible range, using explicit share keys generated from the export inventory; `requiredVersion` is the consuming application's peer or dependency range; remotes remain lazy. Both load orders retain one React and context identity, exactly one aggregate component stylesheet content hash, one instance of each selected theme asset, deterministic layers, and scoped portals. A remote built against an incompatible version renders its controlled fallback and emits a telemetry event while the host keeps working.
6. `fixtures/consumers/csp` serves a policy whose `script-src` and `style-src` reject both `unsafe-eval` and `unsafe-inline`. The theme bootstrap runs only through a nonce or hash supplied by the consumer, or from an external file, and no component injects an unhashed `<style>`. The page renders with zero CSP violation reports.
7. An import-only test loads every public entry without rendering and asserts no DOM mutation, global assignment, network request, or stylesheet insertion occurs at import or module evaluation, and that no asset required at render time is dropped by a bundler honoring `sideEffects`. DOM work performed while a component renders is outside this test.
8. A forced-colors browser fixture asserts a visible `:focus-visible` outline on every focusable supported component (STD-GLB-FE-005 section 3.9).
9. The dependency audit in STD-GLB-FE-006 section 3.10 runs against the lockfile-resolved graph of each fixture, including `react-server-dom-*` and framework advisories for the Next.js consumer.

### 3.3 Payload and runtime evidence

- Publish raw, minified, gzip/Brotli, and parsed-size measurements for defined consumer import scenarios, including a single component, a layout, and a representative page. Identify the tool and incremental consumer cost, compare with an approved baseline, and record material regressions.
- Capture interaction traces for dynamic-height transitions. A layout read is permitted when required for behavior, but claims about forced layout count, frame rate, and theme-switch latency require named scenarios and trace evidence.
- Do not claim `0` reflows, fixed 60 FPS, a universal `<2 KB` or 12 KB budget, or sub-50 ms theme switching without the corresponding supported-scenario evidence.
- Library minification remains deferred to the consumer build as decided in ADR-UIP-BLD-001; measure final consumer output, not only raw `dist` files.

### 3.4 Distribution and release report

- Published ESM/CJS formats, React peer ranges, subpaths, CSS assets, token exports, and fonts must match the package manifest and pass packed-package resolution tests.
- `@scnx/core-ui` and `@scnx/system` declare identical `react` and `react-dom` peer ranges, proven at the lowest and highest version of the range. `@scnx/system` declares `@scnx/core-ui` as a peer dependency and a dev dependency, never as a bundled dependency.
- Public exports are explicit. Wildcard subpath patterns are not published.
- A stable release publishes a conformance report linking source-test results, packed-package tests, Component Accessibility Conformance Reports and known limits, contrast pairs, visual diffs, payload measurements, API changes, and supported consumer scenarios. Component reports are not labeled VPATs and do not certify a complete page.
- A failed or missing required gate prevents promotion to the stable channel. Experimental components may be excluded from stable exports with their scope documented.

## 4. Exceptions

Exceptions name the affected contract, consumer impact, expiry, and reviewer. They cannot convert an untested claim into a guarantee.

## 5. Enforcement Mechanism

The CI pipeline executes the source gate and packed-package gate, stores their evidence, and blocks stable publication on failures. The initial P0 implementation of these gates is tracked in the UI Platform roadmap; this draft does not claim that the current repository already satisfies them.
