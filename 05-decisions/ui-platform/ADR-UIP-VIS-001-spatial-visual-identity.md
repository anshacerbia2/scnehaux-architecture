---
doc_meta:
  id: ADR-UIP-VIS-001
  title: Spatial Visual Identity with Materials and a Fixed Square Structure
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-25
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: UI Platform Team
---

# Spatial Visual Identity with Materials and a Fixed Square Structure (ADR-UIP-VIS-001)

> **Implementation boundary:** this decision changes no package by itself. STD-UIP-TKN-001 2.6.0 records the token rules (2.4.0 added the vocabulary); the UI repository's tokens and styled TDDs implement the values, and each component adopts the identity through its specification. The visual target built from this decision is kept in the design reference repository (ADR-UIP-VIS-002).

---

## 1. Title

Give Scnehaux UI one recognizable visual identity: every container is one of eight materials bound as a single token set; the structure of every component is the system's, square, and the same in every theme and mode; a theme changes only colour; the main action is ink and Scnx Blue is reserved for meaning.

## 2. Status

| Date       | Status                | ADR Type     | Reviewers                 | Approver                                 |
| ---------- | --------------------- | ------------ | ------------------------- | ---------------------------------------- |
| 2026-10-24 | accepted              | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |
| 2026-10-25 | accepted (revision 2) | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |

Accepted under the rule Ansha Cerbia stated on 2026-10-22 (ADR-UIP-CMP-001, section 2). On 2026-10-23 Ansha Cerbia asked for an identity that people recognize at a glance ("Gw mau kita punya identity dari design kita sendiri yg membuat ketika org liat design kita lgsg tau, oh ini scnehaux ui"), delegated the radius decision ("Buat rekomendasi lo sesuai design aja"), and agreed to implement the design-system reference built from this decision in the platform ("setuju").

Revision 2 was decided by Ansha Cerbia on 2026-10-25: the structure of a component is not a theme's to change ("default di tier3/component variable terkait struktur gausah dioverride, jadi ga ada perubahan bentuk seperti radius"), and the designed theme becomes the default under its own name ("ubah default nya menjadi theme yg udah kita rancang, yaitu industrial, sementara untuk yg default ganti namanya"). The proposal it adopts is `design-system/proposals/industrial-structure.md` in the design reference repository (ADR-UIP-VIS-002), at commit `a62d27a`.

### Revision history

- **Revision 1 (2026-10-24):** materials with a 1px ring, contact, and ambient shadow on every on-page material except `well`; the concentric radius ladder `mark` 4px, `element` 8px, `control` 12px, `container` 16px, `panel` 24px, `pill`, strictly ascending, with a child's radius equal to its parent's minus the parent's padding, and a brand theme allowed to shift the ladder while keeping its order; ink acts, blue signals; the stage; the type voice; control, row, and icon sizes as component geometry.
- **Revision 2 (2026-10-25):** the radius ladder is flat at 0 and `pill` stays fully rounded only where roundness carries meaning (item 2); on-page materials are a ring only (item 1); the structural invariants are fixed in every theme and mode (item 6); a theme supplies colour only (item 7); the theme `default` becomes `industrial`. The concentric ladder moves to Alternatives Considered.

## 3. Context

On 2026-10-23 the platform's visual language existed in three places that disagreed:

- The system tokens set radius `element` 4px, `control` 6px, `container` 8px; the achromatic theme 4, 8, 12px.
- The documentation site, the product people see, set cards at 24px, panels at 28px, and inner blocks at 16px as Sass literals outside the tokens, on a tinted ground with a 22px dot grid.
- Shadows were four generic elevations (`effect.shadow.low` to `overlay`) that each component combined with its own border, so a card, a menu, and a dialog drew three unrelated edges.

No document named what makes a screen Scnehaux, so each new component chose again. Nine components (component wave 1, ui-platform PLAN "Component waves") were next, and ui-platform's Figma path (ADR-UIP-TKN-004) would copy whatever the tokens say.

On 2026-10-25, after revision 1 was implemented for nine components, two problems with letting a theme own the shape remained:

- The two themes drew the same component in two shapes (the `control` radius was 12px in `default` and 8px in `achromatic`), so a product's look depended on its colour theme, and every structural property had to be proven again in each theme.
- The documentation site's new expression (Instrument · Square, ADR-UIP-VIS-002) is square, while the components it shows were rounded: a component page could not show a component as it ships and keep its own chrome consistent.

Precedent, retrieved 2026-10-23 to 2026-10-25:

- Vercel Geist defines "Materials", "Presets for radii, fills, strokes, and shadows": surfaces "on the page" (base and small 6px, medium and large 12px) and floating materials "above the page" (tooltip 6px with "Lightest shadow", menu 12px "Lift from page", modal 12px "Further lift", fullscreen 16px "Biggest lift") [R1]. It publishes no values.
- Material Design 3 defines one shape scale for every component: `corner-extra-small` 4px, `small` 8px, `medium` 12px, `large` 16px, `extra-large` 28px, `full` 9999px [R2].
- Apple's SwiftUI `ConcentricRectangle` (iOS 26) defines a corner as concentric "when the corner's radius shares a common center with the containing shape's rounded corner radius", and computes it from the container instead of a hard-coded value [R3].
- IBM Carbon's current themes are White, Gray 10, Gray 90, and Gray 100, and `@carbon/themes` "provides a set of color tokens that are pre-defined for a specific theme" [R4]; Carbon's button style specification gives heights from 24 to 80px and no corner radius [R5].
- Radix Themes lets a theme set a radius from `none` to `full`, but "a Checkbox will never become fully rounded to prevent any confusion between it and a Radio" [R6]: some roundness carries meaning and is not a theme's to change.

## 4. Decision Drivers

- Recognition comes from a few rules applied everywhere, not from decoration.
- A product is recognizable in any theme: shape, size, spacing, type, and motion are the system's; a theme changes colour.
- Structure is proven once: sizes, targets, and nesting hold in every theme, and the theme gate checks colour pairs.
- Color must keep its meaning: a hue used for decoration cannot also signal focus or selection.
- The documentation site shows components as they ship; its chrome and its specimens never disagree in shape.

## 5. Decision

1. **Materials.** Every container is one of eight materials. On the page: `flat` (raised fill), `raised`, `panel`, and `well` (sunken fill). Above the page: `tooltip` (ink fill), `menu` (menus, listboxes, popovers, toasts), `modal`, and `sheet`. A material binds a fill token, a radius token, and one shadow token `effect.material.{flat|raised|panel|tooltip|menu|modal|sheet}`. On the page, `flat`, `raised`, and `panel` are a 1px ring (`color.neutral.border.subtle.default`) and nothing else; `well` has no edge. Above the page, the floating materials keep their layers: `menu`, `modal`, and `sheet` compose the 1px ring, a contact shadow, and an ambient shadow from the neutral shadow tokens, and in dark mode add a 1px inset top edge in `color.neutral.border.default.default`, because shadows read weakly on dark grounds; `tooltip` has no ring (its ink fill is its edge). Components use a material, never a hand-made border, radius, and shadow; one shadow per stack (a card in a panel is `flat`).
2. **The square structure.** `dimension.radius.mark`, `element`, `control`, `container`, and `panel` are 0 in every theme and mode. `pill` stays fully rounded, and only where roundness carries meaning: a radio's indicator and dot (it tells a radio from a checkbox [R6]), a switch's track and thumb, a status dot, a spinner, a circle avatar, and a circle skeleton. A progress track, a tab underline, and navigation and table-of-contents markers take `mark`. Components keep binding the radius intent that names their role, so the intents stay meaningful; the ladder is non-decreasing from `mark` to `panel`.
3. **Ink acts, blue signals.** The primary action is ink (`color.neutral.surface.solid.*` under `color.neutral.text.contrast.*`). The primary scheme's solid fill marks only meaning: the focus ring, links, checked controls, progress, and the current location in navigation, tabs, and tables of contents. Selection among peers (a segmented thumb, the current page) is the `raised` material, not blue. A destructive confirmation is the danger solid.
4. **The stage.** Marketing, documentation, empty states, and previews sit on a tinted ground (`color.neutral.surface.default.default` in light, `sunken` in dark) with a 1px dot every 22px; product data sits on the plain canvas.
5. **Type voice.** Section kickers, table headers, and metadata are eyebrows: mono, uppercase, +0.12em, subtle text. Marketing headlines are Inter semibold tracked tight (−0.055em at the largest size); Inter is set with the single-storey a (`cv11`).
6. **Structure is fixed.** These are identical in every theme and mode, and no theme and no consumer overrides them:
   1. Radius: `mark` to `panel` 0; `pill` fully rounded (item 2).
   2. Spacing: `dimension.spacing.inset-*`, `stack-*`, `inline-*`, `control-*`, `section`, `page`.
   3. Border width: `dimension.border-width.default` 1px, `strong` 2px.
   4. Stacking: the `dimension.z-index.*` order.
   5. Component geometry: controls 28, 36, and 44px; rows 32px (table bodies 44px); icons 16 and 20px; targets at least 24px; the Navbar 64px; the Sidebar 280px; container widths. These are component geometry, not tokens (STD-UIP-TKN-001, "Values that are not Tier-2 tokens"); each component's specification records them.
   6. Type: every `typography.*` family, size, line height, letter spacing, and weight; Inter with `cv11`.
   7. Material geometry: the layers of item 1.
   8. Focus outline: 2px, offset 2px (inputs 0); its colour may follow the theme.
   9. Motion: every `motion.*` duration and easing; the 4px rise, the 1px pressed sink, and the removal of movement under reduced motion.
   10. Breakpoints.
   11. State mechanics: which states exist, disabled behaviour, cursors.
7. **A theme is colour.** A theme supplies `color.*` per mode, including the colours of shadow layers, and nothing else. The theme `default` is renamed `industrial`; `achromatic` keeps its palette and loses its own radius and shadow values. No rounded theme remains, because radius is no longer a theme value. Density, if it is ever needed, is a separate axis with its own selector, not a theme.

## 6. Consequences

### Positive

- A screen is recognizable from its square structure, its edges, and one blue in every theme, and every one of those is a token the gate checks.
- Structure is proven once: a component's sizes, targets, and nesting hold in every theme, and the theme gate checks colour pairs.
- New components choose a material instead of inventing an edge, and choose no corner radius.
- The documentation site shows components as they ship, and its theme switch compares colours only.

### Negative

- Every styled component changes appearance a second time: radius values move to 0 and on-page materials lose their contact and ambient shadows. Chromatic baselines are re-accepted per component.
- The theme id `default` becomes `industrial` with no compatibility alias, because the platform is before v1 (ui-platform TDD tokens-003, "Rollout and Compatibility"); every consumer changes its theme id, its token stylesheet import, and its `data-scnx-theme` value.
- A brand that wants rounded corners cannot get them from a theme; it needs a revision of this decision.

### Operational Impact

- Components adopt the structure one specification at a time; each change records its delta from the previous build.
- The token gate fails when a theme or mode sets a structural key, or when structural values differ between themes or modes.

### Security Impact

- None; the change is visual.

## 7. Compliance Impact

STD-UIP-TKN-001 2.4.0 added the radius intents `mark` and `panel` and the `effect.material` family. STD-UIP-TKN-001 2.6.0 makes the structural families theme-invariant, makes the radius order non-decreasing from `mark` to `panel` (`pill` excluded), and limits a brand theme to colour keys, in the same change as revision 2. No waiver is requested.

## 8. Alternatives Considered

- **The concentric ladder (revision 1):** `mark` 4px, `element` 8px, `control` 12px, `container` 16px, `panel` 24px, with a child's radius equal to its parent's minus the parent's padding, and a brand theme free to shift the ladder [R2][R3]. Rejected in revision 2: a theme that owns the radius makes a product's shape depend on its colour theme, so each structure has to be proven in every theme, and the documentation site cannot show a component as it ships beside square chrome. The flat ladder needs no concentric rule, because every corner is 0.
- **Keep the current rounded look as a third theme:** rejected, because radius is no longer a theme value; keeping it would keep the two-shapes problem this revision removes.
- **Keep the generic shadow scale:** each component keeps choosing its own edge; the drift this decision removes.
- **Geist's values (6 and 12px):** another brand's values [R1], and rounded.
- **Blue primary buttons:** the most visible use of the brand hue, but a hue that fills buttons cannot also be the only signal for focus, selection, and location.
- **Control sizes as tokens:** rejected by STD-UIP-TKN-001; geometry belongs to the component.

## 9. References

Retrieved 2026-10-23 to 2026-10-25.

- [R1] Vercel, Geist, Materials: <https://vercel.com/geist/materials>. "Presets for radii, fills, strokes, and shadows"; surface materials "On the page" (base, small 6px; medium, large 12px) and floating materials "Above the page" (tooltip 6px, "Lightest shadow"; menu 12px, "Lift from page"; modal 12px, "Further lift"; fullscreen 16px, "Biggest lift"). Supports the context and item 1.
- [R2] Google, Material Web 2.4.1, `tokens/versions/v0_192/_md-sys-shape.scss` (npm `@material/web@2.4.1`): `corner-extra-small` 4px, `corner-small` 8px, `corner-medium` 12px, `corner-large` 16px, `corner-extra-large` 28px, `corner-full` 9999px, `corner-none` 0px. Supports the alternatives.
- [R3] Apple, SwiftUI, `ConcentricRectangle`: <https://developer.apple.com/documentation/swiftui/concentricrectangle>. Available from iOS 26.0; "A rounded corner of a rectangle is concentric relative to the container shape's adjacent corner when the corner's radius shares a common center with the containing shape's rounded corner radius". Supports the alternatives.
- [R4] IBM, Carbon Design System, Themes, Code: <https://carbondesignsystem.com/elements/themes/code/>. The current themes are white, gray 10, gray 90, and gray 100; "By default, `@carbon/themes` provides a set of color tokens that are pre-defined for a specific theme." Supports items 6 and 7.
- [R5] IBM, Carbon Design System, Button, Style: <https://carbondesignsystem.com/components/button/style/>. It gives button heights from 24px (extra small) to 80px (2XL) and states no corner radius. Supports item 2.
- [R6] WorkOS, Radix Themes, Radius: <https://www.radix-ui.com/themes/docs/theme/radius>. "Radius values used in the components are derived from a 6-step scale"; with `full`, a Button is pill-shaped, but "a Checkbox will never become fully rounded to prevent any confusion between it and a Radio". Supports item 2 (`pill`).

In-repository evidence (2026-10-23): ui-platform-docs `src/styles/settings/_scale.scss` (`$radius-card: 1.5rem; $radius-panel: 1.75rem; $radius-inner: 1rem`) and `src/styles/elements/_page.scss` (the 22px dot grid); ui-platform `dist/tokens/json/default.json` and `achromatic.json` at `f0ea2c9` (radius and shadow values). Revision 2 (2026-10-25): ui-platform `dist/tokens/json/default.json` and `achromatic.json` at `6ee372f` (`control` 12px and 8px); scnehaux-design `design-system/proposals/industrial-structure.md` at `a62d27a`.
