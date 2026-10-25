---
doc_meta:
  id: ADR-UIP-VIS-001
  title: Spatial Visual Identity with Materials, Design-Agnostic Components, and Guarded Floors
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-26
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: UI Platform Team
---

# Spatial Visual Identity with Materials, Design-Agnostic Components, and Guarded Floors (ADR-UIP-VIS-001)

> **Implementation boundary:** this decision changes no package by itself. STD-UIP-TKN-001 2.8.0 records the token rules and the theme naming (2.4.0 added the vocabulary); the UI repository's tokens and styled TDDs implement the values, and each component adopts the identity through its specification. The visual target built from this decision is kept in the design reference repository (ADR-UIP-VIS-002).

---

## 1. Title

Give Scnehaux UI one recognizable visual identity that each product can carry: every container is one of eight materials bound as a single token set; styled components are design-agnostic and read every presentational value through a component hook that falls back to a semantic token; the default theme, `scnx-platform`, is square; what must hold is guarded as a floor, not locked as a value; the main action is ink and Scnx Blue is reserved for meaning.

## 2. Status

| Date       | Status                | ADR Type     | Reviewers                 | Approver                                 |
| ---------- | --------------------- | ------------ | ------------------------- | ---------------------------------------- |
| 2026-10-24 | accepted              | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |
| 2026-10-25 | accepted (revision 2) | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |
| 2026-10-25 | accepted (revision 3) | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |
| 2026-10-26 | accepted (revision 4) | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |

Accepted under the rule Ansha Cerbia stated on 2026-10-22 (ADR-UIP-CMP-001, section 2). On 2026-10-23 Ansha Cerbia asked for an identity that people recognize at a glance ("Gw mau kita punya identity dari design kita sendiri yg membuat ketika org liat design kita lgsg tau, oh ini scnehaux ui"), delegated the radius decision ("Buat rekomendasi lo sesuai design aja"), and agreed to implement the design-system reference built from this decision in the platform ("setuju").

Revision 2 was decided by Ansha Cerbia on 2026-10-25: the structure of a component is not a theme's to change ("default di tier3/component variable terkait struktur gausah dioverride, jadi ga ada perubahan bentuk seperti radius"), and the designed theme becomes the default under its own name ("ubah default nya menjadi theme yg udah kita rancang, yaitu industrial, sementara untuk yg default ganti namanya").

Revision 3 was decided by Ansha Cerbia the same day and replaces revision 2's model. In the owner's words, as the proposal records them: a styled component applies no design value of its own ("styled component dilarang mengapply radius atau apapun property yg mengacu ke spesifik design ... jadi agnostic"); Tier 3 reads Tier 2, which is 0 in industrial, and a uniform change goes through the theme's Tier 2 ("tier 3 untuk radiusnya ngelock ke tier 2 radius yg by defaultnya 0 di theme industrial ... klo butuh keseragaman besar maka theme harus set tier 2 radiusnya"); nothing else is locked ("ga perlu ada yg di lock lagi ... semua radius, spacing dll kebuka"); Tier 3 gets its own prefix ("variable tier 3 ... ganti jgn --ds lagi"); and the system follows modern solutions for five to ten years ("tetap mengacu ke modern solution ... 5 - 10 tahun"). The proposal it adopts is `design-system/proposals/industrial-structure.md` in the design reference repository (ADR-UIP-VIS-002), revision 2, merged in scnehaux-design#24 and corrected in #25.

Revision 4 was decided by Ansha Cerbia on 2026-10-26 and keeps revision 3's model. In the owner's words, as the proposal's revision 3 records them: the industrial theme is for the platform ("yg industrial itu akan gw pake buat scnehaux platform, iam, ai-runtime, dll"), achromatic holds the tokens of the SaaS design ("achromatic itu tokennya untuk design ini"), the two are renamed after who owns them ("mungkin yg industrial diganti code name scnx-platform dan yg achromatic diganti jadi scnx-saas"), and a brand book is per theme, not per product ("brandbook artinya per theme kan bukan lagi per product"). The proposal it adopts is the same `design-system/proposals/industrial-structure.md`, revision 3, merged in scnehaux-design#27.

### Revision history

- **Revision 1 (2026-10-24):** materials with a 1px ring, contact, and ambient shadow on every on-page material except `well`; the concentric radius ladder `mark` 4px, `element` 8px, `control` 12px, `container` 16px, `panel` 24px, `pill`, strictly ascending, with a child's radius equal to its parent's minus the parent's padding, and a brand theme allowed to shift the ladder while keeping its order; ink acts, blue signals; the stage; the type voice; control, row, and icon sizes as component geometry.
- **Revision 2 (2026-10-25):** the radius ladder flat at 0 with `pill` only where roundness carries meaning; on-page materials a ring only; eleven structural invariants fixed in every theme and mode; a theme supplying colour only; the theme `default` renamed `industrial`. STD-UIP-TKN-001 2.6.0 recorded it (scnehaux-architecture#131).
- **Revision 3 (2026-10-25):** components are design-agnostic and read every presentational value through a Tier-3 hook (`--scnx-*`) that falls back to Tier 2 (item 8); a theme maps any Tier-2 key (item 7); industrial's square values are the default theme's values, not a rule (item 2); revision 2's structural invariants become guarded floors (item 6), and its locked structure moves to Alternatives Considered. The rename to `industrial` and industrial's values stay.
- **Revision 4 (2026-10-26):** a theme is named after who owns the look, never after a trait: `industrial` becomes `scnx-platform` and `achromatic` becomes `scnx-saas`, the `scnx-` prefix is reserved for shipped themes, and mode is never part of an id (item 7; STD-UIP-TKN-001 2.8.0, Theme naming). `scnx-saas` maps the concentric radius ladder and soft on-page shadows its design is drawn with (item 7). A brand book belongs to a theme (ADR-UIP-VIS-002). `scnx-platform`'s values, the hooks, and the floors are unchanged.

## 3. Context

On 2026-10-23 the platform's visual language existed in three places that disagreed:

- The system tokens set radius `element` 4px, `control` 6px, `container` 8px; the achromatic theme 4, 8, 12px.
- The documentation site, the product people see, set cards at 24px, panels at 28px, and inner blocks at 16px as Sass literals outside the tokens, on a tinted ground with a 22px dot grid.
- Shadows were four generic elevations (`effect.shadow.low` to `overlay`) that each component combined with its own border, so a card, a menu, and a dialog drew three unrelated edges.

No document named what makes a screen Scnehaux, so each new component chose again. Nine components (component wave 1, ui-platform PLAN "Component waves") were next, and ui-platform's Figma path (ADR-UIP-TKN-004) would copy whatever the tokens say.

On 2026-10-25, after revision 1 was implemented for nine components, two problems with letting a theme own the shape remained: the two themes drew the same component in two shapes (the `control` radius was 12px in `default` and 8px in `achromatic`), and the documentation site's new expression (Instrument · Square, ADR-UIP-VIS-002) is square while the components it shows were rounded. Revision 2 answered by fixing the structure in every theme. That also took away the paths a product needs: a product with fully rounded buttons, or 6 to 8px corners, could not get them from its theme, and a product could not adjust one component locally without selecting its classes. A styled component also still carried design values of its own in its CSS, so its look was partly the component's and partly the theme's. Revision 3 moves every design value out of the component, so the theme decides the look, and keeps only what accessibility and meaning need, as floors.

Precedent, retrieved 2026-10-23 to 2026-10-25:

- Vercel Geist defines "Materials", "Presets for radii, fills, strokes, and shadows": surfaces "on the page" (base and small 6px, medium and large 12px) and floating materials "above the page" (tooltip 6px with "Lightest shadow", menu 12px "Lift from page", modal 12px "Further lift", fullscreen 16px "Biggest lift") [R1]. It publishes no values.
- Material Design 3 defines one shape scale for every component: `corner-extra-small` 4px, `small` 8px, `medium` 12px, `large` 16px, `extra-large` 28px, `full` 9999px [R2].
- Apple's SwiftUI `ConcentricRectangle` (iOS 26) defines a corner as concentric "when the corner's radius shares a common center with the containing shape's rounded corner radius", and computes it from the container instead of a hard-coded value [R3].
- IBM Carbon's themes are colour sets, and its button style specification gives heights and no corner radius [R4][R5].
- Radix Themes lets a theme set a radius from `none` to `full`, but "a Checkbox will never become fully rounded to prevent any confusion between it and a Radio" [R6]: some roundness carries meaning and is the component's anatomy, not a theme's value.
- Fluent UI React v9 themes by remapping its alias (semantic) layer, with no component layer at all [R7]; a product's uniform look belongs in the theme.
- Spectrum CSS, Salesforce SLDS 1, and Material Web each give a component its own custom properties that fall back to the system's tokens: Spectrum maps token-driven properties "to empty `--mod` prefixed variables (for customization) with a fallback to variables prefixed with `--spectrum`" [R8]; SLDS 1 writes `border-radius: var(--slds-c-badge-radius-border, 15rem);`, and SLDS 2 does not support component-level hooks, favouring global ones [R9]; Material Web's button reads `--md-elevated-button-container-shape`, defaulting to `--md-sys-shape-corner-full` [R10]. A component hook is how a product adjusts one component without selecting its classes, and it is public API to keep.
- A write to a custom property on `:root` in a document of about 42,000 elements measured about 77ms, "independent of what reads the variable", against about 0.5ms on the consuming element [R11]; GitLab measured custom properties against none changing rendering by 10ms (1.8%) [R12]. A hook is set on a scope, not on `:root`, when it changes at runtime.

## 4. Decision Drivers

- Recognition comes from a few rules applied everywhere, not from decoration.
- A component carries no design of its own; the theme decides the look, and one theme change reaches every screen of a product.
- A product changes a value product-wide (its theme) or locally (a hook on a scope) without forking a component or selecting its classes.
- What accessibility and meaning need holds under every theme and every hook; the component enforces it where CSS can.
- Color must keep its meaning: a hue used for decoration cannot also signal focus or selection.
- The system follows modern platform solutions for five to ten years (cascade layers, the top layer, container queries, `max()`, DTCG 2025.10).

## 5. Decision

1. **Materials.** Every container is one of eight materials. On the page: `flat` (raised fill), `raised`, `panel`, and `well` (sunken fill). Above the page: `tooltip` (ink fill), `menu` (menus, listboxes, popovers, toasts), `modal`, and `sheet`. A material binds a fill token, a radius token, and one shadow token `effect.material.{flat|raised|panel|tooltip|menu|modal|sheet}`, each a Tier-2 key a theme may map. In the `scnx-platform` theme, `flat`, `raised`, and `panel` are a 1px ring (`color.neutral.border.subtle.default`) and nothing else; `well` has no edge; `menu`, `modal`, and `sheet` compose the ring, a contact shadow, and an ambient shadow from the neutral shadow tokens, and in dark mode add a 1px inset top edge in `color.neutral.border.default.default`, because shadows read weakly on dark grounds; `tooltip` has no ring (its ink fill is its edge). In the `scnx-saas` theme, `raised` and `panel` add soft contact and ambient layers to the ring. Components use a material, never a hand-made border, radius, and shadow; one shadow per stack (a card in a panel is `flat`).
2. **The `scnx-platform` theme is square.** These are the values of the default theme, `scnx-platform`, not a rule: `dimension.radius.mark`, `element`, `control`, `container`, and `panel` are 0; `pill` is fully rounded for the shapes whose roundness carries meaning (a radio's indicator and dot, a switch's track and thumb, a status dot, a spinner, a circle avatar, a circle skeleton); a progress track, a tab underline, and navigation and table-of-contents markers take `mark`. In every theme the radius values are non-decreasing from `mark` to `panel`, with `pill` excluded. Components bind the radius intent that names their role, so a theme's ladder reaches them.
3. **Ink acts, blue signals.** The primary action is ink (`color.neutral.surface.solid.*` under `color.neutral.text.contrast.*`). The primary scheme's solid fill marks only meaning: the focus ring, links, checked controls, progress, and the current location in navigation, tabs, and tables of contents. Selection among peers (a segmented thumb, the current page) is the `raised` material, not blue. A destructive confirmation is the danger solid.
4. **The stage.** Marketing, documentation, empty states, and previews sit on a tinted ground (`color.neutral.surface.default.default` in light, `sunken` in dark) with a 1px dot every 22px; product data sits on the plain canvas.
5. **Type voice.** Section kickers, table headers, and metadata are eyebrows: mono, uppercase, +0.12em, subtle text. Marketing headlines are Inter semibold tracked tight (−0.055em at the largest size); Inter is set with the single-storey a (`cv11`).
6. **Guarded floors.** Nothing presentational is locked. These hold in every theme and under every hook; the component enforces each in its own CSS where CSS can, and the gate checks the rest:
   1. Target size at least 24px: `max(24px, …)` on the interactive box (WCAG 2.2 SC 2.5.8).
   2. A visible focus indicator: a minimum outline width with `max()`, and its colour pair in the contrast gate (SC 2.4.7, 2.4.11).
   3. Contrast of every declared colour pair, per theme and mode (SC 1.4.3, 1.4.11).
   4. Reduced motion: movement drops under `prefers-reduced-motion`, whatever the motion tokens say (SC 2.3.3).
   5. Shapes that carry meaning are anatomy, not hooks: the radio indicator, the switch thumb, the status dot, the spinner.
   6. State mechanics: which states exist; disabled controls do not react.

   The system's own themes ship no glassmorphism or neumorphism; the contrast and boundary floors are why. ui-platform certifies the themes it ships (`scnx-platform`, `scnx-saas`) in every mode; with one square and one rounded theme shipped, its gate also proves that every component follows a theme's shape through its hooks; a product's own theme or hooks run the same gates in that product's CI.

7. **A theme maps any Tier-2 key.** A value changes in one of three ways: product-wide, a theme maps any Tier-2 key (radius, spacing, size, type, motion, materials, colour); locally, a product sets a Tier-3 hook on a scope (for example `.promo { --scnx-button-radius: 9999px; }`) and owns the result; or through a system variant that ui-platform tests, for a shape that carries meaning (for example `data-shape="circular"` on an icon-only Button). A theme is named after who owns the look, never after a trait; `scnx-` is reserved for the themes the platform ships, and mode is never part of an id (STD-UIP-TKN-001, Theme naming). The platform ships two: `scnx-platform`, the default (the Scnehaux platform, IAM, AI runtime, organization, and the documentation site), and `scnx-saas` (the SaaS products). `scnx-platform` was `industrial` (named `default` until 2026-10-25) and `scnx-saas` was `achromatic`; both were renamed on 2026-10-26 with no compatibility alias because the platform is before v1. `scnx-saas` maps an ink palette, the concentric radius ladder (`mark` 0.25rem, `element` 0.5rem, `control` 0.75rem, `container` 1rem, `panel` 1.5rem, plus `pill`), and materials with soft shadows, the shape its design is drawn with; it inherits `scnx-platform`'s other values.
8. **Components are design-agnostic.** A styled component's CSS holds no literal design value. Every presentational property reads a Tier-3 hook that falls back to a Tier-2 token: `border-radius: var(--scnx-button-radius, var(--ds-dimension-radius-control));`. Hooks are named `--scnx-{component}-{part?}-{property}`, the component namespace of the `.scnx-*` classes and `data-scnx-*` attributes; Tier 2 stays `--ds-*`; Tier 1 is a compiler input and is never emitted (ADR-GLB-FE-010). A hook is referenced with a fallback and never declared, so it costs nothing until a product sets it, and it is never registered with `@property`, because a registered property always has a value and its fallback would never apply. A hook is public API: each component lists its hooks in its specification, and each hook passes the existing alias review (STD-UIP-TKN-001, Component Alias Review; STD-UIP-TKN-002), with no numeric cap. Component geometry that a theme should be able to change, such as control heights, moves to Tier 2.

## 6. Consequences

### Positive

- A screen is recognizable from its materials, its edges, and one blue, and a product's whole look changes from its theme.
- A product adjusts one component on a scope without forking it or selecting its classes, and the floors still hold.
- New components choose a material and bind intents and hooks instead of inventing values.
- The documentation site shows components as they ship; its theme switch may change shape when a theme maps it.

### Negative

- Every styled component's CSS is rewritten to the hook pattern, and component geometry moves to Tier 2; Chromatic baselines are re-accepted per component.
- Hooks are public API: each one is a contract to keep through a review, and renaming one is a breaking change.
- The theme id `default` became `industrial` (revision 2), and `industrial` and `achromatic` become `scnx-platform` and `scnx-saas` (revision 4), with no compatibility alias; every consumer changes its theme id, its token stylesheet import, and its `data-scnx-theme` value. The component class names move to the full component name (`.scnx-btn` to `.scnx-button`) before v1.
- A product's own theme can change shape; ui-platform certifies only the themes it ships, so a product runs the floors and contrast gates on its own themes and hooks.

### Operational Impact

- Components adopt the hook pattern one specification at a time; each change records its delta from the previous build.
- The theme gate checks contrast pairs and the floors per theme and mode; it does not require identical structure across themes. A source gate fails a component stylesheet that holds a literal design value outside the hook-and-fallback pattern.

### Security Impact

- None; the change is visual.

## 7. Compliance Impact

STD-UIP-TKN-001 2.4.0 added the radius intents `mark` and `panel` and the `effect.material` family. STD-UIP-TKN-001 2.7.0 replaces 2.6.0's theme-invariant structure with the guarded floors, lets a brand theme override any Tier-2 key, keeps the radius order non-decreasing from `mark` to `panel` per theme, and moves the Tier-3 prefix to `--scnx-` (referenced with a fallback, never declared, never registered, listed in each specification), in the same change as revision 3. ADR-UIP-TKN-003 section 4.5 records the prefix. STD-UIP-TKN-001 2.8.0 adds Theme naming and the shipped ids `scnx-platform` and `scnx-saas`, in the same change as revision 4. No waiver is requested.

## 8. Alternatives Considered

- **Theme-invariant structure (revision 2):** shape, size, spacing, type, motion, and material geometry fixed in every theme and mode, a theme supplying colour only, and a gate failing a theme that sets a structural key. Rejected in revision 3: it kept design values inside components and closed the product-wide and local paths a product needs (a fully rounded product, a 6 to 8px product, one adjusted component). Components must be agnostic, and uniformity belongs in the theme; what must hold is guarded as a floor instead.
- **The concentric ladder (revision 1):** `mark` 4px, `element` 8px, `control` 12px, `container` 16px, `panel` 24px, with a child's radius equal to its parent's minus the parent's padding [R2][R3]. Not `scnx-platform`'s values: that theme is square and needs no concentric rule. `scnx-saas` maps this ladder since revision 4, and any brand theme may, within the non-decreasing order.
- **Name themes after a trait (`industrial`, `achromatic`):** a trait name stops being true the day the theme maps another Tier-2 key. Rejected in revision 4; the large systems name a complete look after its product or brand (Spectrum's `spectrum` and `express`, Fluent's `teamsLightTheme`, SLDS 2's Salesforce Cosmos), as the adopted proposal's references 15 to 17 record.
- **Global hooks only (SLDS 2):** no component-level hooks, every change through a theme [R9]. Rejected: a product then cannot adjust one component locally without selecting its classes; the review rule bounds the hooks instead.
- **Register hooks with `@property`:** typed values and animation, but a registered property always has a value, so the fallback to Tier 2 would never apply.
- **Keep the current rounded look as a third theme:** not shipped; a product that wants it maps the radius family in its own theme.
- **Keep the generic shadow scale:** each component keeps choosing its own edge; the drift this decision removes.
- **Blue primary buttons:** the most visible use of the brand hue, but a hue that fills buttons cannot also be the only signal for focus, selection, and location.

## 9. References

Retrieved 2026-10-23 to 2026-10-25. R7 to R12 are cited from the adopted proposal's references (retrieved 2026-10-25), not retrieved again.

- [R1] Vercel, Geist, Materials: <https://vercel.com/geist/materials>. "Presets for radii, fills, strokes, and shadows"; surface materials "On the page" (base, small 6px; medium, large 12px) and floating materials "Above the page" (tooltip 6px, "Lightest shadow"; menu 12px, "Lift from page"; modal 12px, "Further lift"; fullscreen 16px, "Biggest lift"). Supports the context and item 1.
- [R2] Google, Material Web 2.4.1, `tokens/versions/v0_192/_md-sys-shape.scss` (npm `@material/web@2.4.1`): `corner-extra-small` 4px, `corner-small` 8px, `corner-medium` 12px, `corner-large` 16px, `corner-extra-large` 28px, `corner-full` 9999px, `corner-none` 0px. Supports the alternatives.
- [R3] Apple, SwiftUI, `ConcentricRectangle`: <https://developer.apple.com/documentation/swiftui/concentricrectangle>. Available from iOS 26.0; "A rounded corner of a rectangle is concentric relative to the container shape's adjacent corner when the corner's radius shares a common center with the containing shape's rounded corner radius". Supports the alternatives.
- [R4] IBM, Carbon Design System, Themes, Code: <https://carbondesignsystem.com/elements/themes/code/>. The current themes are white, gray 10, gray 90, and gray 100; "By default, `@carbon/themes` provides a set of color tokens that are pre-defined for a specific theme." Supports the context.
- [R5] IBM, Carbon Design System, Button, Style: <https://carbondesignsystem.com/components/button/style/>. It gives button heights from 24px (extra small) to 80px (2XL) and states no corner radius. Supports item 2.
- [R6] WorkOS, Radix Themes, Radius: <https://www.radix-ui.com/themes/docs/theme/radius>. "Radius values used in the components are derived from a 6-step scale"; with `full`, a Button is pill-shaped, but "a Checkbox will never become fully rounded to prevent any confusion between it and a Radio". Supports items 2 and 6.
- [R7] Microsoft, Fluent 2, Design tokens: <https://fluent2.microsoft.design/design-tokens> (global and alias tokens); Fluent UI v9 token notes: <https://hackmd.io/@fluentui/SkjrGU6To>. Supports item 7.
- [R8] Adobe, Spectrum CSS, README: <https://github.com/adobe/spectrum-css>. The `--mod` custom properties and their `--spectrum` fallback. Supports item 8.
- [R9] Salesforce, Lightning Design System, Styling hooks (SLDS 1): <https://v1.lightningdesignsystem.com/platforms/lightning/styling-hooks/>; SLDS 2 and component-level hooks: <https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-custom-properties> and <https://lightningdesignsystem.com/dev-guidelines/best-practices>. Supports item 8 and the alternatives.
- [R10] Google, Material Web, Button: <https://material-web.dev/components/button/> (`--md-elevated-button-container-shape`, default `--md-sys-shape-corner-full`); Shape: <https://material-web.dev/theming/shape>. Supports item 8.
- [R11] Sim, "perf(workflow): scope resize CSS-var writes to the container, not :root": <https://github.com/simstudioai/sim/pull/5738>. Supports item 8.
- [R12] GitLab, Investigate performance impact of many CSS variables: <https://gitlab.com/gitlab-org/gitlab-services/design.gitlab.com/-/issues/2344>. Supports item 8.

In-repository evidence (2026-10-23): ui-platform-docs `src/styles/settings/_scale.scss` (`$radius-card: 1.5rem; $radius-panel: 1.75rem; $radius-inner: 1rem`) and `src/styles/elements/_page.scss` (the 22px dot grid); ui-platform `dist/tokens/json/default.json` and `achromatic.json` at `f0ea2c9` (radius and shadow values). Revision 2 (2026-10-25): ui-platform `dist/tokens/json/default.json` and `achromatic.json` at `6ee372f` (`control` 12px and 8px); scnehaux-design `design-system/proposals/industrial-structure.md` at `a62d27a`. Revision 3 (2026-10-25): the same proposal, revision 2, at scnehaux-design `962990d` (#24 and #25). Revision 4 (2026-10-26): the same proposal, revision 3, at scnehaux-design `a446b2a` (#27); the scnx-saas ladder and material values from that repository's earlier snapshot, `design-system/themes/default/tokens.css`.
