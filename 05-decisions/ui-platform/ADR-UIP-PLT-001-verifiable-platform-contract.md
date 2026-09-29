---
doc_meta:
  id: ADR-UIP-PLT-001
  title: Verifiable UI Platform Package and Release Contract
  adr_type: conflict_resolution
  status: accepted
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [PAD-PLT-003]
  authorizes: [STD-UIP-ENG-001, STD-UIP-PRM-001, STD-UIP-STY-001, STD-UIP-TKN-001, STD-UIP-TKN-002]
---

# ADR-UIP-PLT-001: Verifiable UI Platform Package and Release Contract

## 1. Title

Authorize the UI Platform package, interaction, theme, styling, and release contract.

## 2. Status

| Date       | Status   | ADR Type            | Reviewers                   | Approver                        |
| ---------- | -------- | ------------------- | --------------------------- | ------------------------------- |
| 2026-09-29 | accepted | conflict_resolution | Principal 1 and Principal 2 | Ansha Cerbia (UI Platform Lead) |

## 3. Context

The baseline contains two physical packages and three logical token tiers. Review found malformed shadow values, a shadow-key mismatch, font drift, incomplete CSS delivery, placeholder tests, unsafe theme evaluation, a singleton global callback, fragile RSC boundary inference, federation identity gaps, primitive defects, and incomplete widget behavior.

The repository uses pnpm and declares `workspace:*`. A release harness must use `pnpm pack` so packed manifests contain publishable dependency versions. The platform has never governed a production system.

## 4. Decision Drivers

- Publish artifacts that work from an external consumer.
- Preserve the dependency direction from `@scnx/system` to `@scnx/core-ui`.
- Make accessibility, theming, CSP, RSC, federation, CSS, and token output falsifiable.
- Keep public APIs stable while implementation tools evolve.
- Assign every open decision an owner, authority, evidence gate, and deadline.

## 5. Decision

This ADR authorizes version 2.0.0 of STD-UIP-TKN-001, STD-UIP-TKN-002, STD-UIP-PRM-001, STD-UIP-STY-001, and STD-UIP-ENG-001. Each standard names this ADR in `authorized_by` and keeps its `governed_by` attachment to PAD-PLT-003; this ADR names each standard in `authorizes`.

The v1 decisions are:

1. **UIP-DEC-001 — Interaction foundation:** Button, Disclosure/Accordion, Navigation, Sidebar, and layout primitives use native/custom behavior. Combobox, Select, Menu, Dialog, Popover, Listbox, and Tabs use selected React Aria hooks behind `@scnx/core-ui`, subject to this recorded decision. Vendor types and props stay private.
2. **UIP-DEC-002 — Theme isolation:** public themes use `[data-scnx-theme="<theme-id>"][data-scnx-resolved-mode="<mode>"]` roots; the URL-safe theme ID identifies the brand and the resolved mode is a separate attribute. Resets are scoped; portals mount inside the originating root. A separate `:root` compatibility stylesheet may support a single-brand document. Shadow DOM is outside v1.
3. **UIP-DEC-003 — Styling ownership:** one versioned token source generates Sass-facing and Panda-facing contracts. Panda is frozen to its existing recipe surface during P0. Sass components and Panda recipes use named cascade layers. The P0 exit review decides consolidation against the dual-engine eligibility rule in the following paragraph and the Styled Component Delivery TDD.
4. **UIP-DEC-004 — Polymorphism:** interactive parts use `asChild` only at approved composition points. Typography/layout may use a closed `as` tag union. No component exposes both. Other components keep fixed elements.
5. **UIP-DEC-005 — Token package:** tokens remain in `@scnx/system` and publish explicit `@scnx/system/tokens/css/<theme-id>.css`, `tokens/json/<theme-id>.json`, and `tokens/scss` subpaths. Each theme asset contains the declared modes under separate resolved-mode selectors. Independent non-component consumers or release cadence trigger extraction review.
6. **UIP-DEC-006 — CSS delivery:** v1 publishes one aggregate component stylesheet and explicit theme stylesheets. A host or standalone composition root imports them once. Component JavaScript and remotes do not import CSS side effects. Per-component CSS subpaths are outside v1.
7. **UIP-DEC-007 — Federation sharing:** under ADR-GLB-FE-012, the host shares `react`, `react-dom`, `@scnx/core-ui`, and every other context-bearing public entry as singletons with a strict compatible range, using explicit keys generated from the export inventory. Wildcard exports are removed. `@scnx/system` declares `@scnx/core-ui` as a peer and dev dependency. `requiredVersion` is the consuming application's declared range. Remotes remain lazy; only the host may choose eager loading. An incompatible version produces a controlled failure.

Module Federation remains in the enterprise `assess` radar ring. Item 7 governs
the bounded P0 fixture and any federation scope separately authorized by an
owning SAD/ADR; it neither mandates federation nor changes that radar status.
The fixture must pass the same strict CSP policy as the standalone consumer,
including nonce/hash handling for bootstrap and dynamically loaded chunks.

The P0 exit evidence may compare measured sizes and costs, but this ADR does
not authorize universal 15 KB, 10%, or 2x thresholds. Every comparative result
retains its import path, fixture, baseline, compression representation, tool,
runner, and parse/evaluation context. Eligibility follows accessibility,
security, licensing, correctness, and approved consumer performance gates.

P0 means the **pre-release blocking remediation milestone** in the UI Platform execution plan. Evidence can keep a component or capability outside stable exports; it does not silently change these decisions.

Source tests prove interaction and state logic. Producer tests prove generated assets. Isolated `pnpm pack` consumers prove exports, types, CSS, fonts, token subpaths, SSR/RSC, and CSP. A host with two packed remotes proves shared identity, version behavior, theme portals, load-order independence, and exactly one intended stylesheet set.

## 6. Consequences

- **Positive:** consumers receive an explicit, testable v1 contract.
- **Positive:** stable token subpaths preserve a future extraction path.
- **Negative:** fixtures, manual assistive-technology checks, and dual-engine measurements add release work.
- **Operational:** every unresolved public variable, invalid substituted property, missing export, duplicate stylesheet, or required fixture failure blocks stable promotion.
- **Operational:** a larger Node heap is diagnostic evidence and never a release fix or budget.
- **Operational:** deterministic installation is the P0 entry gate. A clean checkout must pass `pnpm install --frozen-lockfile` with lifecycle scripts enabled, no `--ignore-scripts`, and no lockfile change before package feature work begins.

## 7. Compliance Impact

Authorized UI standards: STD-UIP-TKN-001, STD-UIP-TKN-002, STD-UIP-PRM-001, STD-UIP-STY-001, and STD-UIP-ENG-001.

Related global authority: ADR-GLB-FE-010 and its revised frontend standards, and the replacement decisions ADR-GLB-FE-011, ADR-GLB-FE-012, and ADR-GLB-FE-013. The UI Platform token and build decisions (ADR-UIP-TKN-001, -002, -003, ADR-UIP-BLD-001) govern only the unreleased UI Platform packages and are corrected in place under the pre-production rule. No waiver is requested.

## 8. Alternatives Considered

- Three packages for v1: rejected until an independent token-only consumer or release cadence exists.
- CSS side-effect imports in component JavaScript: rejected because the composition root owns deterministic loading.
- Per-component CSS subpaths in v1: rejected because the current release needs one verifiable delivery contract.
- Shadow DOM in v1: rejected because portal, font, and cross-root ARIA behavior add unresolved integration constraints.
- Public vendor-shaped component APIs: rejected because they turn an internal implementation choice into a migration constraint.
