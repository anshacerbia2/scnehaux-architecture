---
doc_meta:
  id: ADR-UIP-TKN-002
  title: ADR-UIP-TKN-002 OKLCH Gamut and Dual-Engine Alpha Blending Architecture
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-UIP-TKN-002: Adoption of OKLCH (P3 Wide-Gamut) Color Space and a Dual-Engine Alpha Architecture (Photometric vs Chromatic) for Enterprise Color Generation.

---

## 1. Title
Adoption of OKLCH (P3 Wide-Gamut) Color Space and a Dual-Engine Alpha Architecture (Photometric vs Chromatic) for Enterprise Color Generation.

## 2. Status
| Date | Status | ADR Type | Reviewers | Approver |
|---|---|---|---|---|
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |


## 3. Context
Legacy UI systems rely on sRGB color spaces (HEX, RGB, HSL). These legacy spaces suffer from the **Helmholtz-Kohlrausch effect**, where colors with identical mathematically-defined lightness (L) appear perceptually different to the human eye (e.g., an HSL Yellow appears blindingly bright, while an HSL Blue appears extremely dark at the same Lightness step).
Furthermore, applying standard opacity (Alpha) globally to all colors creates a "Visual Flattening Trap" (muddying colors when overlaid on backgrounds) and breaks WCAG contrast compliance when interacting with different base colors.

## 4. Decision Drivers
By abandoning HSL and static universal opacities, we eradicate guesswork from the design system. 
- The **OKLCH space** allows the mathematical generation of perfectly symmetrical Light/Dark modes without manual tweaking. 
- The **Dual-Engine Alpha** ensures that Glassmorphism and contextual hover states remain crisp, maintaining their brand identity and APCA contrast ratios even when translucent.

## 5. Decision
### 4.1. OKLCH & P3 Wide-Gamut Adoption
All Scnehaux Core Primitives (Tier 1) must be generated natively using the **OKLCH Color Space**, targeting the **P3 Wide-Gamut**. 
- **Perceptual Uniformity:** A Lightness (L) of 0.60 in OKLCH guarantees the exact same perceived brightness across Red, Green, and Blue hues.
- **APCA Compliance:** This uniformity is mandatory to guarantee algorithmically stable Advanced Perceptual Contrast Algorithm (APCA) scores across all generated palettes.

### 4.2. Dual-Engine Alpha Architecture
To solve the issue of Alpha compositing, the UI Platform will employ a strict Dual-Engine split:
1. **The Photometric Absolute Engine (Black & White):**
   - Treated strictly as **Universal Light Modifiers** (Illumination and Shadow), not as pigments.
   - Utilizes static alpha ramps (e.g., `0.05` to `0.95` opacity) across both Light and Dark axes.
2. **The Chromatic Adaptive Engine (Colors & Neutrals):**
   - Treated as **Pigments**.
   - Alpha variants (e.g., `Red.5A`) are **not** created by applying static opacity to `Red.5`. Instead, they are reverse-engineered via a `solveAlpha` calculation against the baseline Application Background (`neutral.1`). This mathematical mutation ensures that a translucent color, when overlaid on the background, visually replicates its solid counterpart perfectly without color-shifting or muddying.

---

## 6. Consequences
- **Positive:** Unprecedented accuracy in color generation. WCAG 3.0 (APCA) contrast compliance is mathematically guaranteed at compile-time.
- **Negative:** Increased complexity in the Tier 1 Core Token generator scripts. Browsers lacking `color(display-p3)` or `oklch()` support will require fallback compilation strategies (graceful degradation to sRGB).
- **Architecture Validation:** The internal mechanics and solving algorithms for this decision are detailed deeply within the project-level TDD (`TDD-SCNX-UI-JS-002`) and Guide (`GD-SCNX-UI-JS-003`).

### Negative / Risks
- **Legacy Browser Support**: Older devices/browsers do not support OKLCH or Display-P3 gamuts.
  - *Mitigation*: Compile-time post-processors automatically generate fallback sRGB custom properties for legacy rendering contexts.

### Operational
- Requires post-processors (like PostCSS or custom token engines) to build display-p3 and sRGB color tables.
- All alpha tokens must be pre-resolved utilizing the `solveAlpha` algorithm during the compilation phase.

## 7. Compliance Impact
### Related Standards
- [Documentation Governance Standard (GDC-000)](../../../00-governance/GDC-000-documentation-governance.md)
- [Design Token Standard (STD-UIP-TKN-001)](../../../02-standards/ui-platform/design-tokens/STD-UIP-TKN-001-design-tokens.md)
- [Enterprise Design Token Governance (STD-UIP-TKN-002)](../../../02-standards/ui-platform/design-tokens/STD-UIP-TKN-002-consumption-governance.md)

### Compliance Status
Compliant.

### Required Waivers
None.

## 8. Alternatives Considered
### Alternative A: Standard sRGB/HSL Color Space
*   **Pros**: Universal browser compatibility, native support in all design tools.
*   **Cons**: Lacks perceptual uniformity, resulting in inconsistent perceived brightness across different hues and breaking contrast compliance validation.
*   **Why Rejected**: Helmholz-Kohlrausch effect creates visual contrast imbalances that cannot be resolved algorithmically.

### Alternative B: Universal Opacity Scaling
*   **Pros**: Single alpha engine, direct multiplier arithmetic.
*   **Cons**: Causes color-shifting and visual muddying when transparent colors are overlaid on complex or saturated backgrounds.
*   **Why Rejected**: Destroys semantic brand integrity and breaks accessibility (APCA) contrast compliance.
