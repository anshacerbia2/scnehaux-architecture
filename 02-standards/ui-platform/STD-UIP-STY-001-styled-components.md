---
doc_meta:
  id: STD-UIP-STY-001
  title: Enterprise UI Platform Styled Components & Compilation Standard
  owner: Principal Frontend Architect
  version: 2.2.0
  status: approved
  classification: restricted
  governed_by: [PAD-PLT-003]
  authorized_by: [ADR-UIP-PLT-001]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-22
---

# Enterprise UI Platform Styled Components & Compilation Standard (STD-UIP-STY-001)

> **Implementation boundary:** these rules define the approved target contract; the copied baseline does not yet satisfy it.

---

## 1. Objective & Scope

This standard defines the implementation rules, build-time compilation constraints, and style isolation boundaries for styled components and visual compilation engines within the Scnehaux enterprise design system.

Styles are emitted as static assets. Theme state and component behavior may still execute JavaScript. Isolation is a property of the emitted selectors and their tested consumer scope, not a consequence of compilation alone.

---

## 2. Design Principles

The styling and compilation engine adheres to four core principles to ensure rendering performance, theme stability, and visual encapsulation:

1. **Static CSS output**: component and theme styling is compiled before publication; the consumer import contract determines which assets load.
2. **Scoped selectors**: shared resets and themes do not target unrelated host or remote markup.
3. **Verified colors**: OKLCH authoring is paired with an explicit browser support policy and contrast tests for declared semantic pairs.
4. **Scoped theme state**: a theme applies to a named subtree root without mutating another brand's root. Document-wide mode is optional and is not multi-brand isolation; portaled UI receives an explicit themed container or equivalent propagation contract. A portal moves only the DOM node [1], while custom properties and other inherited values follow the DOM tree [2][3], so content portaled outside the theme root loses its tokens and scoped styles. Radix Themes, which also renders its theme root as an element rather than on `<html>`, handles the same problem by re-applying the theme inside each portal [4][5].

## 3. Normative Rules

### Zero-Runtime Compilation

All styling engines deployed within the UI platform (such as static CSS-in-JS engines or Sass/SCSS compilers) must compile styles statically during the application build phase.

- **Prohibition of Runtime CSS-in-JS**: Styling libraries that inject styles or evaluate style strings in the React render path are prohibited in the UI Platform (ADR-GLB-FE-013).
- **Output contract**: SCSS component rules and the existing Panda recipe surface coexist during P0. One versioned token source generates both contracts. Panda adds no new recipe ownership until the P0 exit review. `@scnx/system` exports one aggregate component stylesheet plus explicit theme stylesheets. The composition root imports each once; component JavaScript and remotes MUST NOT inject duplicates. Per-component CSS subpaths are outside v1.
- **Producer boundary**: Panda generates assets in the producer workspace. `@scnx/core-ui` MUST remain style-engine agnostic; after verifying it has no Panda callsites, its source MUST NOT be a Panda scan input. Packed consumers MUST NOT run Panda to render shipped components.

---

### Style Encapsulation in Federated Environments

To prevent visual layout conflicts when multiple micro-frontends share the same browser DOM environment:

- **Global Selector Prohibition**: Public multi-brand themes and resets use `[data-scnx-theme="<theme-id>"][data-scnx-resolved-mode="<mode>"]`. A separate `:root` compatibility stylesheet MAY serve a single-brand document and is excluded from multi-brand/federated support. `@layer` controls precedence and does not scope a selector. Shadow DOM is outside v1.
- **Prefix Isolation**: CSS class names must be prefixed uniquely based on the domain boundary:
  - Core design system: `scnx-` prefix.
  - Subdomain remotes: domain-specific prefixes (e.g. `scnx-hris-`, `scnx-fin-`).
- **CSS Modules Naming**: CSS modules must resolve to hash-appended unique classes during compilation.
- **Cascade contract**: The exact order is `reset, tokens, base, components, recipes, utilities, overrides`. Sass components belong to `components`; Panda recipes belong to `recipes`; UI Platform rules outside a declared layer fail the release gate.
- **Theme coexistence**: Packed-package tests render two roots with distinct themes and check computed styles for leakage. Modal, tooltip, and other portal fixtures mount inside the originating theme container.
- **Focus indicator**: Every focusable part renders a `:focus-visible` outline from focus tokens; `effect.shadow.focus` may enhance it but never replaces it. A forced-colors fixture verifies the outline (STD-GLB-FE-005 section 3.9).

---

### Governed values

STD-GLB-FE-005 section 3.2 requires tokens for the governed decisions (color, typography, spacing rhythm, radius, shadow, z-index, and motion) and permits "local geometry with no reusable semantic role" when its purpose is recorded. In component Sass and Panda recipes this means:

- **Use the scale.** Spacing uses the `dimension.spacing` token of its relationship (inset for padding, stack or inline for gaps, section or page for regions; STD-UIP-TKN-001, "Dimension vocabulary"); typography uses a typography role; radius and motion use their tokens. Design systems that publish a spacing scale treat values off it as exceptions: "deviating from the spacing scales should be avoided whenever possible" [6]; "Each space token should be used in place of the raw pixel or REM values" [7], and hard-coded values are reported as violations [8].
- **Round an off-scale value.** A literal off the scale becomes the nearest step of its relationship; a tie takes the smaller step. The change is a visual change and passes the visual review of section 3.
- **Keep targets usable.** If rounding would make a pointer target smaller than 24 by 24 CSS pixels, the size WCAG 2.2 SC 2.5.8 requires [9], the value rounds up instead.
- **Record local geometry.** A value stays a literal only when it is geometry of one element rather than rhythm: a positioning offset, an icon glyph size, a list-marker gutter, an inset or size relative to the surrounding text (for example inline code in `em`), or a unitless `line-height: 1` that collapses an icon or badge box. Each such value is recorded with its selector, property, purpose, and removal condition, and the stylesheet gate rejects every unrecorded literal.

### Component specification

Every styled component of `@scnx/system` declares one `<name>.spec.json` of kind `styled` in its source folder (ADR-UIP-CMP-001): the primitive specification it styles, its anatomy, options with their values and default, slots, states with how each is entered, and, for each option value, part, and state, every CSS property and the semantic token it takes. Design systems already declare these as data: Spectrum's component declaration is "a single JSON object in a `.json` file. One file per component", with options, slots, anatomy, and states [10]; Carbon requires that "Component styles use tokens available in the system" before a component is stable [11].

- **Complete bindings**: The tokens a component's stylesheet references and the tokens its bindings name are the same set; an option's values equal its published TypeScript union.
- **Computed conformance**: The packed browser fixture renders every option value in every state, in every theme root and supported engine, and requires each bound property to compute its token's value.
- **Contrast from use**: Every bound text color and the background of the same part, option value, and state form a token-gate contrast case at the STD-UIP-TKN-001 minimum in every theme and mode; disabled states are exempt.
- **Stability**: A styled component is not `stable` without a specification that passes these checks.

### Build Pipeline Visual Testing

- **Visual Regression Suite**: Modifying core styled components requires passing visual regression tests (such as Playwright visual comparison check) in the CI pipeline before merging.
- **Bundle Size Checks**: Build processes track raw, minified, compressed, and incremental styling cost for named import scenarios. No numeric threshold is valid without its tool and environment.
- **Artifact checks**: Test that all documented CSS entry points resolve after packing, the composition root styles imported components with one intended stylesheet set, remote load order does not change cascade results, and every required token reference resolves to a value valid for its consuming CSS property.

---

## 4. Exceptions

Exceptions identify the affected selector or theme contract, supported consumer scenarios, expiry, and test evidence.

## 5. Enforcement Mechanism

- **Source checks**: Static analysis checks token usage, selector scoping, and unintended runtime CSS injection.
- **Packed-package checks**: A separate consumer verifies CSS exports, computed styling, two-root isolation, and override precedence in the supported browser matrix.
- **Specification gate**: Each styled specification passes its schema, the cross-reference rules, computed conformance, and contrast from use (section 3, "Component specification").

## 6. References

References 1–5 retrieved 2026-10-20; 6–9 retrieved 2026-10-21; 10–11 retrieved 2026-10-22.

1. React, `createPortal`, at react.dev commit `ae5e48074d4f73f1e349eda2a66841f9a959023e`: <https://github.com/reactjs/react.dev/blob/ae5e48074d4f73f1e349eda2a66841f9a959023e/src/content/reference/react-dom/createPortal.md>. "A portal only changes the physical placement of the DOM node. In every other way, the JSX you render into a portal acts as a child node of the React component that renders it. For example, the child can access the context provided by the parent tree, and events bubble up from children to parents according to the React tree."
2. W3C, CSS Custom Properties for Cascading Variables Module Level 1, at csswg-drafts commit `160a00acff045d99796606f502812c9462e110e2`: <https://github.com/w3c/csswg-drafts/blob/160a00acff045d99796606f502812c9462e110e2/css-variables-1/Overview.bs>. "Custom properties are ordinary properties, so they can be declared on any element, are resolved with the normal inheritance and cascade rules"; the custom property definition table states "Inherited: yes".
3. W3C, CSS Cascading and Inheritance Level 4, same commit: <https://github.com/w3c/csswg-drafts/blob/160a00acff045d99796606f502812c9462e110e2/css-cascade-4/Overview.bs>. "Inheritance propagates property values from parent elements to their children."
4. Radix Themes, `packages/radix-ui-themes/src/components/theme.tsx` and `dialog.tsx` at commit `1faff10ac26ae17f09944d418c6949b93fc6b566`: <https://github.com/radix-ui/themes/tree/1faff10ac26ae17f09944d418c6949b93fc6b566/packages/radix-ui-themes/src/components>. The theme renders `asChild ? Slot.Root : 'div'` with its `data-*` attributes; dialog content renders `<DialogPrimitive.Portal container={container} forceMount={forceMount}>` followed by `<Theme asChild>`.
5. Radix Primitives, `packages/react/portal/src/portal.tsx` at commit `eb3a2b7091293e27df8f9ba906632d8daa3d81a3`: <https://github.com/radix-ui/primitives/blob/eb3a2b7091293e27df8f9ba906632d8daa3d81a3/packages/react/portal/src/portal.tsx>. The default container is `document.body` (`containerProp || (mounted && globalThis?.document?.body)`); the `container` prop is "An optional container where the portaled content should be appended."
6. Carbon Design System, Spacing, FAQ "Are spacing increments outside of the scale allowed?": <https://carbondesignsystem.com/elements/spacing/overview/> (retrieved 2026-10-21). "There are always exceptions to the rule, but deviating from the spacing scales should be avoided whenever possible."
7. Atlassian Design System, Spacing: <https://atlassian.design/foundations/spacing> (retrieved 2026-10-21). "Each space token should be used in place of the raw pixel or REM values when adding space between components or objects on a page."
8. Atlassian Design System, ESLint rule `ensure-design-token-usage`: <https://atlassian.design/components/eslint-plugin-design-system/ensure-design-token-usage/usage> (retrieved 2026-10-21). "Using anything other than design tokens such as hardcoded values or legacy theme colors will be considered violations."
9. W3C, WCAG 2.2, Success Criterion 2.5.8 Target Size (Minimum), `guidelines/sc/22/target-size-minimum.html` at w3c/wcag commit `457cece22d8219be32d29c5c1313e71aa6b61eae`: <https://github.com/w3c/wcag/blob/457cece22d8219be32d29c5c1313e71aa6b61eae/guidelines/sc/22/target-size-minimum.html>. "The size of the target for pointer inputs is at least 24 by 24 CSS pixels", with exceptions for spacing, equivalents, inline targets, user-agent control, and essential presentation.
10. Adobe, Spectrum Design Data, Component format, `packages/design-data-spec/spec/component-format.md` at adobe/spectrum-design-data commit `900b522b5ef746f7d5f9640359a29089884db31e`: <https://github.com/adobe/spectrum-design-data/blob/900b522b5ef746f7d5f9640359a29089884db31e/packages/design-data-spec/spec/component-format.md>. "A component declaration is a **single JSON object** in a `.json` file. One file per component"; it covers "API options (`options`), named content slots (`slots`), anatomy parts (`anatomy`), state model (`states`)".
11. IBM, Carbon Design System, Component checklist, `src/pages/contributing/component-checklist/index.mdx` at carbon-design-system/carbon-website commit `5e9cd1da43c32d3d3b991dc947b427f674da61a8`: <https://github.com/carbon-design-system/carbon-website/blob/5e9cd1da43c32d3d3b991dc947b427f674da61a8/src/pages/contributing/component-checklist/index.mdx>. "Component styles use tokens available in the system"; Stable is "Complete across code, kit, docs, design, and ready for production use".
