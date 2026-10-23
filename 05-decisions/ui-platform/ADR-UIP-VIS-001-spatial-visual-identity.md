---
doc_meta:
  id: ADR-UIP-VIS-001
  title: Spatial Visual Identity with Materials and a Concentric Radius Ladder
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-24
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: UI Platform Team
---

# Spatial Visual Identity with Materials and a Concentric Radius Ladder (ADR-UIP-VIS-001)

> **Implementation boundary:** this decision changes no package by itself. STD-UIP-TKN-001 2.4.0 adds the token vocabulary; the UI repository's tokens and styled TDDs implement the values, and each component adopts the identity through its specification.

---

## 1. Title

Give Scnehaux UI one recognizable visual identity: every container is one of eight materials bound as a single token set; corner radii follow the ladder 4 · 8 · 12 · 16 · 24 and nest concentrically; the main action is ink and Scnx Blue is reserved for meaning.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                                 |
| ---------- | -------- | ------------ | ------------------------- | ---------------------------------------- |
| 2026-10-24 | accepted | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |

Accepted under the rule Ansha Cerbia stated on 2026-10-22 (ADR-UIP-CMP-001, section 2). On 2026-10-23 Ansha Cerbia asked for an identity that people recognize at a glance ("Gw mau kita punya identity dari design kita sendiri yg membuat ketika org liat design kita lgsg tau, oh ini scnehaux ui"), delegated the radius decision ("Buat rekomendasi lo sesuai design aja"), and agreed to implement the design-system reference built from this decision in the platform ("setuju").

## 3. Context

On 2026-10-23 the platform's visual language existed in three places that disagreed:

- The system tokens set radius `element` 4px, `control` 6px, `container` 8px; the achromatic theme 4, 8, 12px.
- The documentation site, the product people see, set cards at 24px, panels at 28px, and inner blocks at 16px as Sass literals outside the tokens, on a tinted ground with a 22px dot grid.
- Shadows were four generic elevations (`effect.shadow.low` to `overlay`) that each component combined with its own border, so a card, a menu, and a dialog drew three unrelated edges.

No document named what makes a screen Scnehaux, so each new component chose again. Nine P1 components were next, and ui-platform's Figma path (ADR-UIP-TKN-004) would copy whatever the tokens say.

Precedent, retrieved 2026-10-23 and 2026-10-24:

- Vercel Geist defines "Materials", "Presets for radii, fills, strokes, and shadows": surfaces "on the page" (base and small 6px, medium and large 12px) and floating materials "above the page" (tooltip 6px with "Lightest shadow", menu 12px "Lift from page", modal 12px "Further lift", fullscreen 16px "Biggest lift") [R1]. It publishes no values.
- Material Design 3 defines one shape scale for every component: `corner-extra-small` 4px, `small` 8px, `medium` 12px, `large` 16px, `extra-large` 28px, `full` 9999px [R2].
- Apple's SwiftUI `ConcentricRectangle` (iOS 26) defines a corner as concentric "when the corner's radius shares a common center with the containing shape's rounded corner radius", and computes it from the container instead of a hard-coded value [R3].

## 4. Decision Drivers

- Recognition comes from a few rules applied everywhere, not from decoration.
- Every value is a token checked by the gate, in every theme and mode; a brand theme may change values but not the rules.
- Nested shapes must not collide: a radius that ignores its parent's padding looks wrong at every size.
- Color must keep its meaning: a hue used for decoration cannot also signal focus or selection.
- What the documentation site already shows (24px cards with 16px insets, the dot grid, mono eyebrows) is the identity people have seen; the system adopts it rather than diverging from it.

## 5. Decision

1. **Materials.** Every container is one of eight materials. On the page: `flat` (raised fill, ring), `raised` (ring, contact and ambient shadow), `panel` (radius `panel`, a softer, wider ambient), and `well` (sunken fill, no shadow). Above the page: `tooltip` (ink fill), `menu` (menus, listboxes, popovers, toasts), `modal`, and `sheet`. A material binds a fill token, a radius token, and one shadow token `effect.material.{flat|raised|panel|tooltip|menu|modal|sheet}`. That token composes a 1px ring (`color.neutral.border.subtle.default`), a contact shadow, and an ambient shadow from the neutral shadow tokens; floating materials in dark mode add a 1px lit top edge, because shadows read weakly on dark grounds. Components use a material, never a hand-made border, radius, and shadow; one shadow per stack (a card in a panel is `flat`).
2. **The concentric ladder.** `dimension.radius.mark` 4px, `element` 8px, `control` 12px, `container` 16px, `panel` 24px, `pill`. A child's radius is its parent's radius minus the parent's padding: a 24px panel padded 8px holds 16px cards; a 16px menu padded 8px holds 8px rows; a 12px track padded 4px holds an 8px thumb. Values ascend strictly in every theme; a brand theme may shift the ladder but keeps the order. Small controls (28px) take `element`, medium and large controls `control`.
3. **Ink acts, blue signals.** The primary action is ink (`color.neutral.surface.solid.*` under `color.neutral.text.contrast.*`). The primary scheme's solid fill marks only meaning: the focus ring, links, checked controls, progress, and the current location in navigation, tabs, and tables of contents. Selection among peers (a segmented thumb, the current page) is the `raised` material, not blue. A destructive confirmation is the danger solid.
4. **The stage.** Marketing, documentation, empty states, and previews sit on a tinted ground (`color.neutral.surface.default.default` in light, `sunken` in dark) with a 1px dot every 22px; product data sits on the plain canvas.
5. **Type voice.** Section kickers, table headers, and metadata are eyebrows: mono, uppercase, +0.12em, subtle text. Marketing headlines are Inter semibold tracked tight (−0.055em at the largest size); Inter is set with the single-storey a (`cv11`).
6. **Geometry stays structural.** Control heights (28, 36, 44px), row heights (32px; 44px for table bodies), and icon sizes are component geometry, not tokens (STD-UIP-TKN-001, "Values that are not Tier-2 tokens"); each component's specification records them.

## 6. Consequences

### Positive

- A screen is recognizable from its corners, edges, and one blue, and every one of those is a token the gate checks.
- New components choose a material and a ladder step instead of inventing an edge.
- The documentation site's literal radii become tokens, so the site and the product stop disagreeing.

### Negative

- Every styled component changes appearance: radius values move (control 6 → 12px), and Button's primary fill moves from blue to ink. Chromatic baselines are re-accepted per component.
- Seven new public shadow tokens and two radius intents widen the token contract.

### Operational Impact

- Components adopt the identity one specification at a time; each change records its delta from the previous build.

### Security Impact

- None; the change is visual.

## 7. Compliance Impact

STD-UIP-TKN-001 2.4.0 adds the radius intents `mark` and `panel` with a strict order, and the `effect.material` family, in the same change. No waiver is requested.

## 8. Alternatives Considered

- **Keep the generic shadow scale:** each component keeps choosing its own edge; the drift this decision removes.
- **Geist's values (6 and 12px):** sharper and familiar, but they are another brand's, and a 6px control radius inside a 12px container breaks concentric nesting at the paddings this system uses.
- **Material 3's scale as is (28px extra-large):** the closest precedent [R2]; 24px is kept because it is the documentation site's card radius and is concentric with 16px at the 8px inset the system uses.
- **Blue primary buttons:** the most visible use of the brand hue, but a hue that fills buttons cannot also be the only signal for focus, selection, and location.
- **Control sizes as tokens:** rejected by STD-UIP-TKN-001; geometry belongs to the component.

## 9. References

Retrieved 2026-10-23 and 2026-10-24.

- [R1] Vercel, Geist, Materials: <https://vercel.com/geist/materials>. "Presets for radii, fills, strokes, and shadows"; surface materials "On the page" (base, small 6px; medium, large 12px) and floating materials "Above the page" (tooltip 6px, "Lightest shadow"; menu 12px, "Lift from page"; modal 12px, "Further lift"; fullscreen 16px, "Biggest lift"). Supports the context and item 1.
- [R2] Google, Material Web 2.4.1, `tokens/versions/v0_192/_md-sys-shape.scss` (npm `@material/web@2.4.1`): `corner-extra-small` 4px, `corner-small` 8px, `corner-medium` 12px, `corner-large` 16px, `corner-extra-large` 28px, `corner-full` 9999px, `corner-none` 0px. Supports item 2 and the alternatives.
- [R3] Apple, SwiftUI, `ConcentricRectangle`: <https://developer.apple.com/documentation/swiftui/concentricrectangle>. Available from iOS 26.0; "A rounded corner of a rectangle is concentric relative to the container shape's adjacent corner when the corner's radius shares a common center with the containing shape's rounded corner radius"; it "automatically calculates each corner's radius relative to the container shape, so your view adapts correctly across devices and sizes without hard-coded values." Supports item 2.

In-repository evidence (2026-10-23): ui-platform-docs `src/styles/settings/_scale.scss` (`$radius-card: 1.5rem; $radius-panel: 1.75rem; $radius-inner: 1rem`) and `src/styles/elements/_page.scss` (the 22px dot grid); ui-platform `dist/tokens/json/default.json` and `achromatic.json` at `f0ea2c9` (radius and shadow values).
