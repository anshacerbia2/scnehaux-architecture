---
doc_meta:
  id: ADR-UIP-TKN-002
  title: ADR-UIP-TKN-002 OKLCH Gamut and Dual-Engine Alpha Blending Architecture
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
  governed_by: [PAD-PLT-003]
---

# ADR-UIP-TKN-002: Adoption of OKLCH (P3 Wide-Gamut) Color Space and a Dual-Engine Alpha Architecture (Photometric vs Chromatic) for Enterprise Color Generation.

> **Implementation boundary:** implemented by the UI repository's palette generator (TDD tokens, "Palette generation" PG1–PG10), the only producer of the Tier-1 color scales, whose emitted pairs the token gate verifies on every change.

---

## 1. Title

Adoption of OKLCH (P3 Wide-Gamut) Color Space and a Dual-Engine Alpha Architecture (Photometric vs Chromatic) for Enterprise Color Generation.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                   | Approver                        |
| ---------- | -------- | ------------ | --------------------------- | ------------------------------- |
| 2026-09-29 | accepted | foundational | Principal 1 and Principal 2 | Ansha Cerbia (UI Platform Lead) |

## 3. Context

Legacy UI systems rely on sRGB color spaces (HEX, RGB, HSL). These legacy spaces suffer from the **Helmholtz-Kohlrausch effect**, where colors with identical mathematically-defined lightness (L) appear perceptually different to the human eye (e.g., an HSL Yellow appears blindingly bright, while an HSL Blue appears extremely dark at the same Lightness step). Furthermore, applying standard opacity (Alpha) globally to all colors creates a "Visual Flattening Trap" (muddying colors when overlaid on backgrounds) and breaks WCAG contrast compliance when interacting with different base colors.

## 4. Decision Drivers

HSL scales and static universal opacities are replaced by a perceptual authoring space and a rendered-pair verification step.

- **OKLCH** provides a useful perceptual authoring space for generating candidate light and dark scales; it does not remove the need for theme-specific review.
- **Alpha composition** requires checking the rendered foreground/background pairing. A calculated overlay is a candidate value, not a contrast guarantee.

## 5. Decision

### 4.1. OKLCH & P3 Wide-Gamut Adoption

All Scnehaux Core Primitives (Tier 1) must be generated natively using the **OKLCH Color Space**, targeting the **P3 Wide-Gamut**.

- **Perceptual Authoring:** OKLCH supports more predictable color-scale editing than HSL, while perceived appearance and rendered contrast still depend on hue, chroma, display gamut, and background.
- **Contrast Evidence:** Declared semantic foreground/background pairs must be evaluated after alpha composition and color conversion in each supported theme. The release gate is WCAG 2.2 SC 1.4.3 for text and SC 1.4.11 for non-text UI; APCA may be recorded as additional research evidence, not as a claim of WCAG 3 conformance.

### 4.2. Dual-Engine Alpha Architecture

To solve the issue of Alpha compositing, the UI Platform will employ a strict Dual-Engine split:

1. **The Static Alpha Engine (Black & White):**
   - Treated strictly as **Universal Light Modifiers** (Illumination and Shadow), not as pigments.
   - Utilizes static alpha ramps (e.g., `0.05` to `0.95` opacity) across both Light and Dark axes.
2. **The Chromatic Adaptive Engine (Colors & Neutrals):**
   - Treated as **Pigments**.
   - Alpha variants (e.g., `Red.5A`) are solved against the declared baseline background, `neutral.1` of the same mode. The resulting color is verified in the intended context; other backgrounds require separate evaluation.

---

## 6. Consequences

- **Positive:** A consistent authoring model and explicit candidate-generation process for light, dark, and alpha variants.
- **Negative:** Increased complexity in the Tier 1 Core Token generator. A color outside sRGB is shown by each browser's own gamut handling, which differs between engines (STD-UIP-TKN-001, display paths).
- **Architecture Validation:** The generator and its declared semantic color pairs must be checked by executable tests and a packed-package browser fixture before compliance claims are made.

### Negative / Risks

- **sRGB displays**: a Display P3 color reaches an sRGB display clipped or gamut mapped, depending on the engine.
  - _Mitigation_: every supported browser parses `oklch()`, so no fallback declaration is emitted (STD-UIP-TKN-001); the generator reduces the chroma of a P3 color until its sRGB-clipped rendering is within a bounded OKLab distance of its gamut-mapped one, and the token gate tests contrast on all four display paths.

### Operational

- The generator runs at build time from a versioned configuration; CI fails when the committed scales differ from a fresh generation.
- Alpha steps record their assumed background (`neutral.1` of the mode) and pass the declared contrast gate in every supported theme and state where they are used.

## 7. Compliance Impact

### Related Standards

- [Documentation Governance Standard (GDC-000)](../../00-governance/GDC-000-governance-policy.md)
- [Design Token Standard (STD-UIP-TKN-001)](../../02-standards/ui-platform/STD-UIP-TKN-001-design-tokens.md)
- [Enterprise Design Token Governance (STD-UIP-TKN-002)](../../02-standards/ui-platform/STD-UIP-TKN-002-consumption-governance.md)

### Compliance Status

Implemented. The palette generator solves the WCAG 2.2 SC 1.4.3 and 1.4.11 targets with the token gate's own contrast function, and CI fails on a palette that is not a fresh generation; the token gate verifies every declared and every component-rendered pair in every theme and mode, on each display path (UI repository, TDD tokens G1–G3 and PG1–PG10).

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Standard sRGB/HSL Color Space

- **Pros**: Universal browser compatibility, native support in all design tools.
- **Cons**: Direct numerical adjustments are less aligned with the chosen perceptual authoring workflow; contrast still requires evaluation in every color space.
- **Why Rejected**: OKLCH is the selected authoring model for palette work, with explicit conversion and contrast checks.

### Alternative B: Universal Opacity Scaling

- **Pros**: Single alpha engine, direct multiplier arithmetic.
- **Cons**: A single opacity multiplier can yield poor results across different backgrounds.
- **Why Rejected**: Alpha is calibrated for each declared semantic pairing and verified after composition.
