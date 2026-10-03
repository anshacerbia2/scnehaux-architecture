---
doc_meta:
  id: ADR-UIP-BLD-002
  title: tsdown Replaces tsup as the UI Platform Package Builder
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: proposed
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-03
  created: 2026-10-03
  created_date: 2026-10-03
  created_by: UI Platform Team
---

# tsdown Replaces tsup as the UI Platform Package Builder (ADR-UIP-BLD-002)

> **Implementation boundary:** this decision changes the tool that compiles `@scnx/core-ui` and `@scnx/system`. The package contract (entries, exports, directives, declarations, assets) is unchanged and is verified by the existing packed-artifact gates.

---

## 1. Title

Replace tsup, which its maintainer no longer maintains, with tsdown as the builder of the UI Platform packages, completing the GDC-004 sunset of `tsup`.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                | Approver                                         |
| ---------- | -------- | ------------ | ------------------------ | ------------------------------------------------ |
| 2026-10-03 | proposed | foundational | Pending principal review | Pending Architecture Review Board (Ansha Cerbia) |

## 3. Context

The ARB moved `tsup` to `hold` on 2026-10-02 (decision D2) because its README states: "This project is not actively maintained anymore. Please consider using tsdown instead." GDC-004 section 2.2 then requires the ARB to "publish a companion migration guide or successor standard within `30 days`", that is, by 2026-11-01, and gives existing systems "a grace window of maximum `180 days`" (until 2027-03-31).

No ADR selected `tsup`: SAD-003 recorded it as the core and system builder, so this is the first builder decision (GDC-010 section 2.1, Foundational). The UI repository also carried a local patch of tsup 8.5.1 to keep declaration generation within the default heap (PLAN P0 row 2). Two fixtures borrowed esbuild through tsup.

Two candidates were compared, as D2 required: tsdown and Vite library mode. ADR-GLB-FE-011 section 5 item 2 permits a library to use another bundler "when its SAD records it and its packed-consumer tests pass".

## 4. Decision Drivers

- A maintained builder, so security and compatibility fixes keep arriving.
- No change to the published package contract: every packed-artifact gate passes unchanged.
- Two builds per package, client-only and server-safe, with `"use client"` first in every client-only entry and in no server-safe entry (TDD packaging K1–K3).
- Declarations from the build, with no local patch.
- Reproducible content digests (TDD packaging R3).

## 5. Decision

1. **Builder:** both packages build with tsdown, pinned to an exact version through the workspace catalog (0.23.0 at adoption). An upgrade is a reviewed change that must pass every packed-artifact gate.
2. **Configuration:** one `tsdown.config.mjs` per package keeps the two-build shape of TDD packaging K2, from a shared `scripts/tsdown-builds.mjs`. Peers and the sibling package are never bundled (`deps.neverBundle`); declarations come from the TypeScript compiler. Configs are plain ES modules loaded with `--config-loader native`, so no optional config loader is installed.
3. **Directives:** `"use client"` appears only at the top of client-only source entries (TDD packaging K1), and Rolldown outputs it because "the module is a entry module". No output banner is added: it would duplicate that directive, and the packed-artifact inspector checks every emitted entry (K3). Rolldown's scanner warns `MODULE_LEVEL_DIRECTIVE` for every top-level directive, kept or not, so the client build ignores that warning for its own entries only; a directive in any other module reaches the build log, and CI fails on it (K3).
4. **Removed:** tsup, its local patch, and the unused `esbuild-plugin-tsconfig-paths`. The browser fixtures declare esbuild directly.
5. **Sunset record:** this ADR is the `tsup` successor standard under GDC-004 section 2.2. The radar entry for `tsup` names `tsdown` as its successor and this ADR as its migration guide.

## 6. Consequences

### Positive (Pros)

- A maintained builder. tsdown is "an official project of Rolldown", and Vite's own build guide points to it for advanced library flows.
- The local tsup patch is gone. On the same machine, the full build took 9.2 s with a 623 MB peak, against 10.4 s and 703 MB with patched tsup.
- Every packed-artifact gate passed on tsdown output: the inspector, packed consumers at both React boundaries, the browser token, component, theme, and import gates, the Next.js App Router fixture, the federation fixture, SBOM, licenses, and source tests. Two builds produced the same content digests.

### Negative (Cons)

- tsdown is pre-1.0. Release 0.23.0 carried breaking changes, so every upgrade needs a full gate run.
- Emitted JavaScript grew from 69.3 kB to 87.3 kB (`@scnx/core-ui`) and from 122.0 kB to 130.9 kB (`@scnx/system`), before the consumer's bundler tree-shakes it. No consumer budget is approved at P0 (PLAN), so this is comparative evidence only.

### Operational

- The `tsup` grace window ends 2027-03-31; the migration lands before the stable target (2026-12-04).
- Node 22.18 or later is required for the native config loader; the pinned toolchain runs 22.22.1.

## 7. Compliance Impact

Completes Stage 1 of the GDC-004 section 2.2 sunset for `tsup`. Uses the library exception of ADR-GLB-FE-011 section 5 item 2; SAD-003 records `tsdown` as the core and system builder (revision pending ratification). Keeps ADR-UIP-BLD-001 (deferred minification): tsdown runs with `minify: false`. Adds `tsdown` to the Technology Radar at trial, pending ARB. No waiver is requested.

## 8. Alternatives Considered

- **Vite library mode:** Vite's build guide says "Library mode includes a simple and opinionated configuration for browser-oriented and JS framework libraries. If you are building non-browser libraries, or require advanced build flows, you can use tsdown or Rolldown directly." The packages need two builds per package, a client directive on each client-only entry, declarations, and server-safe entries for Node and React Server Components; the library-mode section does not cover declaration output.
- **Rolldown directly:** the same engine as tsdown, but declarations, dependency externalization, and per-entry configuration would be assembled by hand.
- **Stay on tsup:** unmaintained by its own maintainer's statement, with a local patch to carry; GDC-004 section 2.2 requires a successor.
- **Other builders (unbuild, Rollup with plugins):** not evaluated; the D2 recommendation scoped the comparison to tsdown and Vite library mode.

## 9. References

Retrieved 2026-10-03.

- tsup README: <https://github.com/egoist/tsup/blob/main/README.md>.
- GDC-004, Technology Lifecycle and Standards Governance, section 2.2.
- tsdown, "Migrate from tsup" and options documentation at commit `eb40c95efdf7f98d0aa7b0178a3b7322986bd419`: <https://github.com/rolldown/tsdown/tree/eb40c95efdf7f98d0aa7b0178a3b7322986bd419/docs>. Config loaders: "`native`: Loads TypeScript configuration files using native runtime support. Requires a compatible environment, such as Node.js 22.18.0+". Declarations: "If `isolatedDeclarations` is not enabled, `tsdown` will fall back to using the TypeScript compiler for `.d.ts` generation."
- tsdown guide: <https://tsdown.dev/guide/> ("As an official project of Rolldown").
- Vite, Building for Production, Library Mode: <https://vite.dev/guide/build>.
- Rolldown, Directive, at commit `ffb6509cfd37eb14be3e952626ad8ce310e9a279`: <https://github.com/rolldown/rolldown/blob/ffb6509cfd37eb14be3e952626ad8ce310e9a279/docs/in-depth/directives.md>. "Rolldown will output the directive for any of the following cases: [...] The directive is in the top-level scope and the module is a entry module". At the same commit, `crates/rolldown/src/ast_scanner/impl_visit.rs` raises `module_level_directive` for every top-level directive other than `use strict`.
- GDC-010, ADR Guideline, section 2.1 (ADR types).
- React, `'use client'`: <https://react.dev/reference/rsc/use-client>. "When a `'use client'` module is imported from another client-rendered module, the directive has no effect."
- UI repository prototype (branch `spike/tsdown`, 2026-10-03): build measurements and gate results above.
