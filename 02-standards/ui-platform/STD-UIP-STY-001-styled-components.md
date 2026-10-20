---
doc_meta:
  id: STD-UIP-STY-001
  title: Enterprise UI Platform Styled Components & Compilation Standard
  owner: Principal Frontend Architect
  version: 2.0.1
  status: approved
  classification: restricted
  governed_by: [PAD-PLT-003]
  authorized_by: [ADR-UIP-PLT-001]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-20
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

## 6. References

Retrieved 2026-10-20.

1. React, `createPortal`, at react.dev commit `ae5e48074d4f73f1e349eda2a66841f9a959023e`: <https://github.com/reactjs/react.dev/blob/ae5e48074d4f73f1e349eda2a66841f9a959023e/src/content/reference/react-dom/createPortal.md>. "A portal only changes the physical placement of the DOM node. In every other way, the JSX you render into a portal acts as a child node of the React component that renders it. For example, the child can access the context provided by the parent tree, and events bubble up from children to parents according to the React tree."
2. W3C, CSS Custom Properties for Cascading Variables Module Level 1, at csswg-drafts commit `160a00acff045d99796606f502812c9462e110e2`: <https://github.com/w3c/csswg-drafts/blob/160a00acff045d99796606f502812c9462e110e2/css-variables-1/Overview.bs>. "Custom properties are ordinary properties, so they can be declared on any element, are resolved with the normal inheritance and cascade rules"; the custom property definition table states "Inherited: yes".
3. W3C, CSS Cascading and Inheritance Level 4, same commit: <https://github.com/w3c/csswg-drafts/blob/160a00acff045d99796606f502812c9462e110e2/css-cascade-4/Overview.bs>. "Inheritance propagates property values from parent elements to their children."
4. Radix Themes, `packages/radix-ui-themes/src/components/theme.tsx` and `dialog.tsx` at commit `1faff10ac26ae17f09944d418c6949b93fc6b566`: <https://github.com/radix-ui/themes/tree/1faff10ac26ae17f09944d418c6949b93fc6b566/packages/radix-ui-themes/src/components>. The theme renders `asChild ? Slot.Root : 'div'` with its `data-*` attributes; dialog content renders `<DialogPrimitive.Portal container={container} forceMount={forceMount}>` followed by `<Theme asChild>`.
5. Radix Primitives, `packages/react/portal/src/portal.tsx` at commit `eb3a2b7091293e27df8f9ba906632d8daa3d81a3`: <https://github.com/radix-ui/primitives/blob/eb3a2b7091293e27df8f9ba906632d8daa3d81a3/packages/react/portal/src/portal.tsx>. The default container is `document.body` (`containerProp || (mounted && globalThis?.document?.body)`); the `container` prop is "An optional container where the portaled content should be appended."
