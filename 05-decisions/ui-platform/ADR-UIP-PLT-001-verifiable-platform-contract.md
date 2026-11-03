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

| Date       | Status   | ADR Type            | Reviewers                                           | Approver                  |
| ---------- | -------- | ------------------- | --------------------------------------------------- | ------------------------- |
| 2026-09-29 | accepted | conflict_resolution | Principal 1 and Principal 2                         | UI Platform Lead          |
| 2026-10-21 | accepted | conflict_resolution | Architecture Review Board (revision of UIP-DEC-001) | Architecture Review Board |

Revision of UIP-DEC-001, 2026-10-21: the owner directed that composite widgets be implemented without React Aria ("manual aja", in reply to the choice between React Aria hooks and a custom implementation for the Combobox). UIP-DEC-001 is revised in place, because no system governed by this ADR is in production (GDC-000 section 2.6, item 4). Acceptance, stated by the owner on 2026-10-21: "aya, sebagai ARB, menerima revisi ADR-UIP-PLT-001 UIP-DEC-001 (komponen composite tanpa React Aria) per 2026-10-21." ("As ARB, I accept the revision of ADR-UIP-PLT-001 UIP-DEC-001 (composite components without React Aria) as of 2026-10-21.")

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

1. **UIP-DEC-001 — Interaction foundation:** every primitive is implemented in `@scnx/core-ui` without a third-party interaction library. A primitive renders the native element when it provides the semantics and behavior (for example `dialog` for Dialog); otherwise it implements the WAI-ARIA Authoring Practices pattern for its widget [R1]. Combobox, Select, Menu, Popover, Listbox, and Tabs each ship with a behavior matrix run in every engine of the support matrix before their entry is published, and stable promotion additionally requires manual NVDA and VoiceOver results (STD-UIP-PRM-001). React Aria is a reference for known assistive-technology behavior, not a dependency [R3]. Revised in place and accepted on 2026-10-21; until then, this item named selected React Aria hooks for those widgets.
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
- Selected React Aria hooks for Combobox, Select, Menu, Dialog, Popover, Listbox, and Tabs (this item before 2026-10-21): rejected on 2026-10-21. They would be the first runtime dependency of `@scnx/core-ui`, enter lien L1 (license policy) and the payload budget, and Dialog and Tabs had already shipped without them (native `dialog`; TDD primitives P16–P17). The cost of the choice is that assistive-technology differences React Aria has already found, such as NVDA falling silent on text edits while an option is active and VoiceOver's limited `aria-activedescendant` support [R3], must be avoided by design and checked manually: incorrect ARIA "misrepresents visual experiences, with potentially devastating effects" [R2].

## 9. References

Retrieved 2026-10-21.

- [R1] W3C WAI-ARIA Authoring Practices Guide, Combobox Pattern, `content/patterns/combobox/combobox-pattern.html` at w3c/aria-practices commit `0f765e4dc33e966026114ac12a8380db1de3b787`: <https://github.com/w3c/aria-practices/blob/0f765e4dc33e966026114ac12a8380db1de3b787/content/patterns/combobox/combobox-pattern.html>. "if a combobox supports text input, it is referred to as editable"; "If the combobox is editable, it supports standard single line text editing keys appropriate for the device platform."
- [R2] W3C WAI-ARIA Authoring Practices Guide, Read Me First, same commit: <https://github.com/w3c/aria-practices/blob/0f765e4dc33e966026114ac12a8380db1de3b787/content/practices/read-me-first/read-me-first-practice.html>. "No ARIA is better than Bad ARIA"; "Incorrect ARIA misrepresents visual experiences, with potentially devastating effects on their corresponding non-visual experiences."
- [R3] React Aria, "Building a ComboBox", `packages/dev/s2-docs/pages/react-aria/blog/building-a-combobox.mdx` at adobe/react-spectrum commit `2eb4e0e9154943e92466daf9213183af84b6e6ad`: <https://github.com/adobe/react-spectrum/blob/2eb4e0e9154943e92466daf9213183af84b6e6ad/packages/dev/s2-docs/pages/react-aria/blog/building-a-combobox.mdx>. "testing sessions revealed varied support across screen readers"; with an option focused through `aria-activedescendant`, NVDA did not announce "character deletions and text cursor movement in the ComboBox input"; "VoiceOver has limited support for `aria-activedescendant`", and in Chrome announces it "only [...] if `aria-selected="true"` is applied to the focused item"; on touch screen readers `role="combobox"` led to an erroneous "double tap to close" announcement; "manual testing is irreplaceable for surfacing these behavioral differences".
