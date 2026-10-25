---
doc_meta:
  id: ADR-UIP-CMP-001
  title: Component Specification as Code for UI Platform Components
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-22
  created: 2026-10-22
  created_date: 2026-10-22
  created_by: UI Platform Team
---

# Component Specification as Code for UI Platform Components (ADR-UIP-CMP-001)

> **Implementation boundary:** this decision changes no package by itself. It is implemented by SAD-003 2.3.0 (sections 2.1, 5.1, and 10), STD-UIP-PRM-001 2.2.0 and STD-UIP-STY-001 2.2.0 (section 3, "Component specification"), and the UI repository's primitives and styled TDDs, which own the schemas, the rules, and the gates.

---

## 1. Title

Record the contract of every public entry of `@scnx/core-ui` and `@scnx/system` as one machine-readable specification in that entry's source folder, in the package that owns it: behavior for a primitive, presentation (anatomy, options, slots, states, and the token every part uses per option and state) for a styled component. Verify each specification against the packed artifacts in every supported theme and engine, publish it with its package, and generate the normative sections of the documentation from it.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                                         |
| ---------- | -------- | ------------ | ------------------------- | ------------------------------------------------ |
| 2026-10-22 | proposed | foundational | Pending principal review  | Pending Architecture Review Board (Ansha Cerbia) |
| 2026-10-22 | accepted | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board)         |

Acceptance, stated by Ansha Cerbia on 2026-10-22: "Lo rubah aja, gausah terlalu formal di status, gw butuh first class grade design, klo memang udh based on best practice, battle tested solution, first class grade, dan ada referencenya, lgsg approved aja, gausah pake proposed2" ("Change it; the status need not be formal. I need a first-class design: when it is based on best practice and battle-tested solutions, first-class, and referenced, approve it directly without the proposed step.") SAD-003 2.3.0, STD-UIP-PRM-001 2.2.0, and STD-UIP-STY-001 2.2.0 implement it in the same change.

## 3. Context

PAD-PLT-003 section 4.1 guarantees "Styled UI: Token-bound visual states". SAD-003 section 5.1 assigns the component contract ("Public name, semantic root, state/ARIA, styling hooks, stability") to "TDD and generated documentation". On 2026-10-22 the UI repository records that contract in three places, none of which says which token a part uses:

- `packages/core-ui/behavior-inventory.json` holds one PrimitiveContract for each of the 9 interactive primitives (`name`, `entry`, `stability`, `root`, `parts` with selectors, `controlledProps`, `states`, `keys`, `focus`, `accessibleName`, `dataHooks`), executed by tests, and one stability record for each of the other 42 public entries of both packages. Stability of the 25 `@scnx/system` component entries is therefore held in `@scnx/core-ui`, and every component change edits one shared file. `ButtonBase` has a contract; the styled `Button` has only a stability record.
- `packages/design-system/api/css-contract.json` lists the published stylesheets' layers, classes, and token names, not the relation between them.
- The TDDs record decisions with their tradeoffs. Per-component styling facts written there (for example the Button rows BR1–BR3 of TDD styled, 2026-10-22) are prose that no gate reads, and twenty-five styled components (nine more planned) would make the TDD a component catalogue.

The generated documentation the SAD names does not exist, and SAD-003 section 2.1 gives the documentation site no location, although PAD-PLT-003 section 1.2 makes "consumer guidance" part of the capability.

The cost of the gap is measured. On 2026-10-22 the primary Button used `color.neutral.text.contrast.default`, the label of the neutral solid fill, instead of the primary scheme's. In the dark `default` theme (renamed `industrial` on 2026-10-25) it computed `oklch(0.07 0.0057 252)` on `oklch(0.47 0.3116 263.6)`, 2.6:1, below the 4.5:1 of WCAG 2.2 SC 1.4.3 [R7]. It passed every gate: the token gate tests the pairs the token doctrine names (each scheme's `contrast` on its own `solid`), not the pairs a component uses; the story tests run axe-core in the initial light mode only; Chromatic captures every mode but measures nothing. In the same review, disabled was `opacity: 0.5`, its selector `[data-disabled="true"]` never matched the empty `data-disabled` that ButtonBase renders, and `text.contrast.disabled` measured about 1.2:1 on the disabled fill. Nothing stated the intended binding, so nothing could check it. Nine new components are next: component wave 1 (ui-platform PLAN, "Component waves"; this sentence cited PLAN "Later work" until 2026-10-24, where P1 is the release contract, not components).

Industry precedent, 2026-10-22:

- Adobe Spectrum Design Data defines a "component declaration" as "a single JSON object in a `.json` file. One file per component", with `options`, `slots`, `anatomy`, `states`, and `tokenBindings`, validated by a JSON Schema, a rules catalog, and conformance fixtures [R1][R2]. Its stated motivation is this gap: "a token referencing `component: "button"` with `variant: "foo"` was undetectable as invalid because no machine-readable component contract existed in the same spec" [R2]. It is `1.0.0-draft` [R1], and its bindings are a flat list whose rule is that each token "MUST resolve to a declared token" [R2]: a static check, not a check of the shipped CSS.
- IBM Carbon defines Stable as "Complete across code, kit, docs, design, and ready for production use" and requires "Component styles use tokens available in the system" and specs for "hover, focus, selected, disabled, read-only, error, warning" [R3], verified by review. Its component pages are tabbed Usage, Style, Code, Accessibility [R4].
- Radix documents each primitive with Anatomy, API Reference (props and data-attribute tables), Examples, and Accessibility with a keyboard table rendered from structured data [R5].
- GitHub Primer's shared component metadata carries an id, name, description, guidelines link, and implementation links, and is a "Work in progress" [R6].

No precedent found verifies a declared binding against the computed style of the published artifact in each theme and engine. The UI repository already does so for keyboard behavior (behavior inventory) and, on the Button fix branch, for one component's recipe.

## 4. Decision Drivers

- One authority per fact: a fact stated in two records can disagree, so a styled contract references its primitive's contract and the API reports, never copies them.
- The contract is checked against the packed artifact, as every UI Platform gate is (TDD packaging), not against source or a picture.
- Contrast is proven for the pairs components actually render, in every theme and mode.
- Package boundary: styling belongs to `@scnx/system`, behavior to `@scnx/core-ui` (SAD-003 section 4.2); each package owns the records of its own entries.
- Component-driven ownership: a component's code, stories, tests, and contract change together in one folder, so independent component changes do not edit one shared file.
- No second normative source in Markdown inside the UI repository (SAD-003 section 2.1).
- Documentation cannot drift from the release it documents.
- Tools and agents can read the contract without parsing CSS or prose.

## 5. Decision

1. **One specification per public entry, next to its source.** Every public entry of both packages has exactly one specification, `<name>.spec.json`, in its source folder, in the package that owns the entry, conforming to a versioned JSON Schema. There are three kinds, distinguished by `kind`:
   - `primitive` (`@scnx/core-ui`, an interactive primitive; schema owned by TDD primitives): the PrimitiveContract fields of TDD primitives P12 (root, parts with selectors, controlled props, states, keys with their expected effect, focus, accessible name, data hooks) and `stability`;
   - `styled` (`@scnx/system`; schema owned by TDD styled): `primitive`, the primitive specification it styles, or none; `anatomy`, each part's name and selector, referencing the primitive's part when one exists, plus styled-only parts (for example an icon slot); `options`, each styling option with its `values` and `default` (for example `variant: primary | secondary`); `slots`, named content positions; `states`, each visual state with how it is entered (a prop, an attribute, or an interaction such as hover or pressed) and its selector; `bindings`, for each option value, part, and state, each CSS property and the semantic token it takes (for example `variant=primary`, `root`, `disabled`: `background-color` takes `color.primary.surface.solid.disabled`); and `stability`;
   - `entry` (any other public entry, for example a presentational primitive, a layout, a provider, or a hook): its `kind` of entry and `stability`, plus `anatomy` when it renders parts.

   Names, entry subpaths, and the vocabulary (anatomy, options, slots, states) follow Spectrum's component declaration [R2], so the two can be mapped later; the binding granularity and the three kinds are this decision's own.

2. **The inventory becomes generated.** `behavior-inventory.json` is split into the primitive and entry specifications of item 1 without changing any recorded fact, and is then produced from them, never edited (SAD-003 section 4.2: "Generated files have one producer and are never hand-edited"). Each package generates its own index of its specifications. The P13 rule "exactly one stability record per public entry" becomes "exactly one specification per public entry".
3. **No duplicated fact.** A styled specification references its primitive's parts and states by name and never restates keyboard, ARIA, focus, or accessible name; prop types stay in the API reports. A specification that restates a fact owned by another record fails validation.
4. **Static rules.** A specification fails when a part or state does not exist in its primitive's specification; an option's values differ from the published TypeScript union; a public entry has no specification or two; for a styled specification, a bound token is missing from any supported theme or mode, a public class of the component in `css-contract.json` belongs to no declared part, or the component's stylesheet references a token that no binding names, or a binding names a token the stylesheet never references. Bindings and stylesheet are equal sets, so the specification is complete, not illustrative.
5. **Executed conformance.** The behavior fixtures execute every primitive specification's keys and parts, as the behavior inventory is executed today. The packed browser fixture renders every styled option value in every declared state, in every theme root and every engine of the support matrix, and fails unless each bound property computes the value of its token in that root.
6. **Contrast from bindings.** Every pair of a bound `color` and the `background-color` of the same part, option value, and state is a token-gate contrast case at the doctrine minimum (STD-UIP-TKN-001), in every theme and mode; disabled states stay exempt [R7].
7. **Stable requires conformance.** No entry is promoted to `stable` (TDD primitives P13) without a specification that passes items 4 to 6.
8. **Publication.** Each package publishes its specifications as explicit JSON exports, `./specs/<name>.json`, plus an index export, `./specs` (SAD-003 section 4.2 prohibits wildcard exports). A specification is part of the public contract: a changed binding is a visual change and a changed key or part a behavior change, each following the compatibility classification of SAD-003 section 6.3.
9. **Documentation.** The documentation site, a separate repository that installs the published tarballs, generates the normative sections of every page from the specifications, the API reports, and the release evidence: a Primitives page from a primitive specification (anatomy, parts and data attributes, keyboard, ARIA, focus, API), a Components page from a styled specification and the primitive it references (anatomy, options and bindings per state, measured contrast per theme, API, accessibility inherited from the primitive), and the status of every entry. Usage guidance (when to use, content, examples) is informative MDX in that repository and never restates a generated fact. Page order: Overview, Usage, Anatomy and specification, API, Accessibility, Status.
10. **TDD scope.** TDD rows record decisions and tradeoffs only. A row that only lists bindings or parts is replaced by the specification; the Button rows BR1–BR3 keep their rationale and point to `button.spec.json`.
11. **Rollout.** First the schemas, the rules, and the split of the behavior inventory into specifications with no change of fact; then `button.spec.json` and the generic conformance check; then the rest of the reference slice (TextField, Dialog, Tabs). Every P1 component is born with its specification; every other entry has one before promotion.

## 6. Consequences

### Positive (Pros)

- The Button defect class (a wrong but existing token, contrast below minimum in one mode only, a selector that never matches) fails a gate before review.
- Contrast is proven for rendered pairs in every theme and mode, closing the light-only axe-core gap for bound colors.
- Component pages cannot disagree with the release they document, and tools and agents read one JSON contract.
- Each new component costs one JSON file in its own folder; the gates are generic, and parallel component changes no longer edit one shared inventory.
- Primitives and styled components are documented from the same kind of record, so the Primitives and Components pages of the documentation have one source each.

### Negative (Cons)

- Every styling change edits two files (stylesheet and specification); item 4 makes forgetting one a failure, not drift.
- Splitting the behavior inventory touches every primitive test once; item 11 makes the split a fact-preserving step of its own.
- The fixture grows with options × states × themes × engines; TDD styled sets the budget.
- A published specification widens the public surface, and binding changes need compatibility classification.
- The schema is this platform's own; mapping to Spectrum's format, if wanted, is later work.

### Operational

- TDD primitives owns the `primitive` and `entry` schemas, TDD styled the `styled` schema; a schema change follows its own compatibility rules.
- The documentation repository pins the package version it renders; its build fails when a specification does not validate.

## 7. Compliance Impact

No standard is violated and no waiver is requested. Revised with this acceptance:

- SAD-003 section 2.1 gains the specification files (normative, gated, next to source, in both packages) and the documentation repository (generated normative sections; informative usage); section 5.1's component contract names the specifications, with the TDDs for decisions.
- STD-UIP-PRM-001 and STD-UIP-STY-001 section 3 each gain a rule: every primitive, respectively styled component, declares a specification that passes items 4 to 6 before `stable`.
- TDD primitives records the `primitive` and `entry` schemas and the inventory split, and P12 and P13 move from the inventory to the specifications; TDD styled records the `styled` schema, rules, conformance check, and budget.
- PAD-PLT-003 is unchanged: section 4.1 already guarantees token-bound visual states, and section 1.1 keeps component detail out of the capability.

## 8. Alternatives Considered

- **Per-component TDD rows (the status quo):** prose no gate reads; twenty-five styled components make the TDD a catalogue; the Button defect shipped under it.
- **Extend `behavior-inventory.json` with styling:** one file, but it belongs to `@scnx/core-ui`, which has no styling, and it would mix the two packages' contracts.
- **One registry file per package (`behavior-inventory.json` plus a styled inventory):** no new layout, but every component change edits a shared file, a component's contract lives away from its code, and the stability of `@scnx/system` entries either stays in `@scnx/core-ui` or is copied.
- **A separate specification package or repository (as Spectrum keeps its design data apart from its implementations [R2]):** suited to several implementations of one design (Spectrum declares `implementations` per component [R2]); here there is one implementation, and every specification is verified against the packed artifacts of the same commit, which a separate release cycle would break.
- **Adopt Spectrum Design Data as is:** a draft whose normative text "may change before `1.0.0`" [R1], with token naming of its own and flat bindings checked statically [R2]. The vocabulary is aligned instead (item 1).
- **Derive the specification from the CSS:** it would document whatever the stylesheet does, defects included; the specification states intent and the gate compares.
- **Storybook stories and Chromatic baselines as the specification:** approval of a picture names no token and measured nothing in the Button case.
- **Hand-written documentation only:** cheapest, and the documentation would restate facts that drift from the release.
- **Design files (for example Figma) as the source:** outside the repository and its gates.

## 9. References

Retrieved 2026-10-22.

Informative:

- [R1] Adobe, Spectrum Design Data specification, `packages/design-data-spec/spec/index.md` at adobe/spectrum-design-data commit `900b522b5ef746f7d5f9640359a29089884db31e`: <https://github.com/adobe/spectrum-design-data/blob/900b522b5ef746f7d5f9640359a29089884db31e/packages/design-data-spec/spec/index.md>. "**Version:** `1.0.0-draft`"; "Draft — normative text and schemas may change before `1.0.0`"; validation layers start with "`schemas/*.json` | Per-instance structural shape (JSON Schema Draft 2020-12)". Supports the context and the third alternative.
- [R2] Adobe, Spectrum Design Data, Component format, `packages/design-data-spec/spec/component-format.md`, same commit: <https://github.com/adobe/spectrum-design-data/blob/900b522b5ef746f7d5f9640359a29089884db31e/packages/design-data-spec/spec/component-format.md>. A declaration covers "platform implementations (`implementations`), API options (`options`), named content slots (`slots`), anatomy parts (`anatomy`), state model (`states`)"; "A component declaration is a **single JSON object** in a `.json` file. One file per component"; "Before this chapter, a token referencing `component: "button"` with `variant: "foo"` was undetectable as invalid because no machine-readable component contract existed in the same spec"; each `tokenBindings[].token` "MUST resolve to a declared token in the dataset" (SPEC-027). Supports the context, item 1, and the alternatives.
- [R3] IBM, Carbon Design System, Component checklist, `src/pages/contributing/component-checklist/index.mdx` at carbon-design-system/carbon-website commit `5e9cd1da43c32d3d3b991dc947b427f674da61a8`: <https://github.com/carbon-design-system/carbon-website/blob/5e9cd1da43c32d3d3b991dc947b427f674da61a8/src/pages/contributing/component-checklist/index.mdx>. Stable: "Complete across code, kit, docs, design, and ready for production use"; "Component styles use tokens available in the system"; "Designs include specs for states such as hover, focus, selected, disabled, read-only, error, warning, etc."; "All text colors pass 4.5:1 color contrast with the exceptions of disabled states". Supports the context and items 6 and 7.
- [R4] IBM, Carbon Design System, Button, `src/pages/components/button/usage.mdx`, same commit: <https://github.com/carbon-design-system/carbon-website/blob/5e9cd1da43c32d3d3b991dc947b427f674da61a8/src/pages/components/button/usage.mdx>. Front matter: "tabs: ['Usage', 'Style', 'Code', 'Accessibility']". Supports item 9.
- [R5] Radix UI, Radix Primitives documentation, Tabs, `data/primitives/docs/components/tabs.mdx` at radix-ui/website commit `402e749613ab2e7ab7139c65b0029842b0360f07`: <https://github.com/radix-ui/website/blob/402e749613ab2e7ab7139c65b0029842b0360f07/data/primitives/docs/components/tabs.mdx>. Sections "Anatomy", "API Reference" (`PropsTable`, data attributes such as `[data-state]`), "Examples", "Accessibility" with "Keyboard Interactions" rendered by `KeyboardTable` from a data array. Supports item 9.
- [R6] GitHub, `@primer/component-metadata` 0.5.1, README: <https://cdn.jsdelivr.net/npm/@primer/component-metadata@0.5.1/README.md>. Fields `id`, `displayName`, `description`, `guidelines`, and `implementations` (React, ViewComponent, CSS, Figma); "Work in progress". Supports the context.
- [R7] W3C, WCAG 2.2, Success Criterion 1.4.3 Contrast (Minimum): <https://www.w3.org/TR/WCAG22/>. Text has "a contrast ratio of at least 4.5:1", except text that is "part of an inactive user interface component". Supports the context and item 6.

In-repository evidence (2026-10-22): `packages/core-ui/behavior-inventory.json` and `packages/design-system/api/css-contract.json` at ui-platform `main` `5287188`; `.storybook/preview.tsx` (`initialGlobals: { theme: THEMES[0], mode: "light" }`, axe-core `test: "error"`); the Button fix on branch `fix/button-tonal-secondary`, whose packed browser check fails on all four theme roots of `main`'s packages.
