---
doc_meta:
  id: STD-UIP-ENG-001
  title: UI Platform Build & Delivery Standards
  owner: Principal UI/UX Architect
  version: 2.1.0
  status: approved
  classification: public
  governed_by: [PAD-PLT-003]
  authorized_by: [ADR-UIP-PLT-001]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-29
---

# UI Platform Build & Delivery Standards (STD-UIP-ENG-001)

> **Revision 2.1.0 is pending exact-commit ratification.** It adds section 3.5,
> the release contract (PLAN P1). Under GDC-000 section 2.6.7, revision 2.0.0
> remains binding until the authorized human authority approves the exact
> commit containing this revision. The existing `last_reviewed` is updated
> only in the ratification commit or manifest.

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

### 3.5 Release contract

1. **Public API.** The public API of each package is every subpath in its `exports` map, the TypeScript declarations those entries publish, and the documented CSS contract: custom properties, class and data-attribute hooks, cascade layer names, and token keys. Internal chunks and undocumented names are not public. The API is declared in the package documentation and checked against each release (SemVer 2.0.0 item 1 [1]; GOV.UK Frontend counts HTML, Sass, and JavaScript as its public API [3]).
2. **Stability.** Every public entry is `candidate` or `stable` in the behavior inventory. The compatibility rules below bind `stable` entries only. A `candidate` entry may change in any release; release notes and the evidence packet label it, as Angular does for Developer Preview APIs, which "can change at any time, even in new patch versions" [4].
3. **Versioning.** Both packages follow SemVer 2.0.0 and release together under one version. Before the first stable release, a published version is a pre-release of `1.0.0` (`1.0.0-beta.N`), which "indicates that the version is unstable" [1]; `1.0.0` is the first stable release. A published version is never modified or overwritten [1]. A breaking change to a stable entry is a major release; a new feature or a deprecation is a minor release; a patch release only fixes behavior [1]. Removing or renaming a token, selector, layer, or property is breaking; changing a token value or a component's appearance while keeping its names and structure is a minor change that the release records with its visual diffs [3].
4. **Deprecation.** A stable feature is deprecated only in a minor release, never in a patch [1][3]. The release notes say why and what replaces it; the TypeScript declaration carries `@deprecated`, and a development build warns where the use can be detected [2]. A deprecated feature is removed only in a major release, after at least one minor release carried the deprecation [1] and no sooner than 180 days after that release, the grace window GDC-004 section 2.2 gives existing systems [5]. A feature still used by another platform entry is not deprecated [3].
5. **Support matrix.** Each release declares and tests:
   - React and React DOM: the shared peer range, proven at its lowest and highest version (section 3.4);
   - browsers: the Baseline Widely available set on the release date, as the browserslist query `baseline widely available on <YYYY-MM-DD>` [6], tested in Chromium, Firefox, and WebKit;
   - Node.js for server rendering: the lines in Active LTS or Maintenance LTS on the release date, since "Production applications should only use Active LTS or Maintenance LTS releases" [7];
   - TypeScript for consumers' type checking: the releases less than two years old on the release date, the window DefinitelyTyped tests [8].

   The matrix narrows only in a major release, except that a version reaching its upstream end of life (for example, a Node.js line) may leave it in a minor release.

6. **Release record.** Every release's evidence records its version, the support matrix, the stability of every entry, the public-API difference from the previous release, its deprecations, and its rollback target (the previous immutable package pair). A stable release additionally requires a rehearsed install and rollback in a packed consumer.

## 4. Exceptions

Exceptions name the affected contract, consumer impact, expiry, and reviewer. They cannot convert an untested claim into a guarantee.

## 5. Enforcement Mechanism

The CI pipeline executes the source gate and packed-package gate, stores their evidence, and blocks stable publication on failures. The initial P0 implementation of these gates is tracked in the UI Platform roadmap; this draft does not claim that the current repository already satisfies them.

## 6. References

Retrieved 2026-10-03.

1. Semantic Versioning 2.0.0, `semver.md` at commit `f99d5485190a47c0863949e7da810a5553e0ed4d`: <https://github.com/semver/semver/blob/f99d5485190a47c0863949e7da810a5553e0ed4d/semver.md>. Item 1: "Software using Semantic Versioning MUST declare a public API"; item 3: "Once a versioned package has been released, the contents of that version MUST NOT be modified"; item 7: a minor version "MUST be incremented if any public API functionality is marked as deprecated"; item 9: a pre-release "indicates that the version is unstable"; FAQ: "Before you completely remove the functionality in a new major release there should be at least one minor release that contains the deprecation".
2. React, Versioning policy, at react.dev commit `8c68ae8d2410abe59f351195780c6f8ea9f50904`: <https://github.com/reactjs/react.dev/blob/8c68ae8d2410abe59f351195780c6f8ea9f50904/src/content/community/versioning-policy.md>. "Whenever possible, we add warnings in preparation for future breaking changes. That way, if your app has no warnings on the latest release, it will be compatible with the next major release."
3. GOV.UK Frontend, `docs/contributing/versioning.md` and `docs/contributing/managing-change.md` at commit `283cc58ead97f3e3379199976709713914e00b05`: <https://github.com/alphagov/govuk-frontend/tree/283cc58ead97f3e3379199976709713914e00b05/docs/contributing>. "We follow Semantic Versioning but a UI library often has subjective changes such as visual spacing changes"; its public API includes HTML, Sass, and JavaScript; "Wherever possible, deprecate features as part of a minor release, before removing them in the next major release"; "Deprecations should not be made in patch releases"; "Features should not be deprecated while they are relied on by other parts of GOV.UK Frontend."
4. Angular, Releases, at commit `c0dc8c4bbeea70879aef54e9fcc7888359dfd1a5`: <https://github.com/angular/angular/blob/c0dc8c4bbeea70879aef54e9fcc7888359dfd1a5/adev/src/content/reference/releases.md>. Developer Preview APIs "can change at any time, even in new patch versions of the framework"; a deprecated API "is still present in at least the next major release (period of at least 12 months)".
5. GDC-004, Technology Lifecycle and Standards Governance, section 2.2: "a grace window of maximum `180 days`".
6. Browserslist, README at commit `8219dd79df0315feaabba302077a66e236822a3a`: <https://github.com/browserslist/browserslist/blob/8219dd79df0315feaabba302077a66e236822a3a/README.md>. "`baseline widely available on YYYY-MM-DD`: selects browser versions that supported the Widely available feature set on the specified date"; Widely available features "have been interoperable in the Baseline core browser set for at least 30 months".
7. Node.js, Previous releases, at nodejs.org commit `4ffcf0386a1c09e7656c29efe6f66dd9ec153a35`: <https://github.com/nodejs/nodejs.org/blob/4ffcf0386a1c09e7656c29efe6f66dd9ec153a35/apps/site/pages/en/about/previous-releases.mdx>. "Production applications should only use _Active LTS_ or _Maintenance LTS_ releases."
8. DefinitelyTyped, README at commit `ac3977d854a671215b8d3e2d5e4ced9c345bf00b`, "Support Window": "Definitely Typed only tests packages on versions of TypeScript that are less than 2 years old."
