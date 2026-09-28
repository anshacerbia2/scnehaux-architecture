---
doc_meta:
  id: ADR-UIP-TKN-001
  title: ADR-UIP-TKN-001 Three-Tier Design Token Isolation Architecture
  adr_type: foundational
  status: proposed
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
  governed_by: [PAD-PLT-003]
---

# ADR-UIP-TKN-001: Adoption of a Three-Tier Design Token Architecture (Core, Semantic, Component) to Isolate Raw Visual Values from Semantic Intent.

> **Pre-production correction candidate:** the three tiers remain the logical architecture. This wording carries no authority until the UI Platform Lead records actual approval.

---

## 1. Title

Adoption of a Three-Tier Design Token Architecture (Core, Semantic, Component) to Isolate Raw Visual Values from Semantic Intent.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                 | Approver                   |
| ---------- | -------- | ------------ | ----------------------------------------- | -------------------------- |
| 2026-09-28 | proposed | foundational | Consolidated principal review in progress | UI Platform Lead — pending |

## 3. Context

As the Scnehaux ecosystem scales across multiple standalone portals and federated micro-frontends (e.g., HRIS, Finance, IAM), maintaining a unified visual language becomes exponentially difficult. Hardcoding raw color hexes or generic variables (e.g., `$blue-9`) directly into component stylesheets creates severe technical debt:

1. **Semantic Ambiguity:** `$blue-9` provides no context on _why_ the color is used (is it a primary button, an info alert, or a selected row?).
2. **Theming & White-labeling Blockers:** Switching a brand's primary color from Blue to Purple requires finding and replacing `$blue-9` across hundreds of files, often causing unintended side-effects where Blue was used for structural purposes instead of brand identity.
3. **Loss of Central Governance:** Frontend engineers invent local color assignments, destroying the unified Visual Root of Trust.

## 4. Decision Drivers

This boundary separates the naming of a design value from the naming of its intended use. Correct theme output and consumer usage still require tests.

- **Enterprise Theming:** A brand can remap `color.primary.solid.default.default` at Tier 2 when consumers use the semantic contract and the new theme passes visual and accessibility checks.
- **Predictable Maintenance:** Developers consume contextual intent (`color.danger.surface.subtle.default`), making the reason for a color choice reviewable across themes.

## 5. Decision

The UI Platform uses a **Three-Tier Design Token Isolation Architecture** for governed shared visual decisions. Product-specific values without a meaningful shared role follow STD-UIP-TKN-002's documented exception path.

### Tier 1: Core Primitives (The Raw Values)

- **Definition:** Pure, platform-agnostic mathematical scales without UI context (for example `color.blue.light.9` and `dimension.spacing.4`).
- **Rule:** Shared components consume semantic roles rather than referencing Tier-1 scales directly.

### Tier 2: Semantic Tokens (The Global Intent)

- **Definition:** The shared mapping from Tier 1 primitives to structural UI intent (for example `color.primary.solid.default.default` and `dimension.spacing.compact`).
- **Rule:** This is the default consumption layer for governed shared styling. Theme overrides preserve semantic meaning; justified Tier-3 aliases may vary independently.

### Tier 3: Component Aliases (Unique Overrides)

- **Definition:** Specific aliases scoped to one component (for example `checkbox.indicator.color.checked`).
- **Rule:** Introduced for independently governed component semantics, with rationale, fallback, theme coverage, and migration impact. No arbitrary numeric cap applies.

---

## 6. Consequences

- **Positive:** Theme and component changes can be isolated through stable semantic contracts when the compiled outputs and supported contexts are verified. Dark-mode symmetry is a contract to test, not an automatic consequence of the tier model.
- **Negative:** Increased initial cognitive load for engineers who must learn the Semantic Taxonomy instead of using raw colors.
- **Enforcement target:** Code-level checks reject prohibited raw color literals and direct Tier-1 references in component source. The packed-package gate verifies that emitted CSS variables resolve and that declared semantic color pairs satisfy the release contrast target. These checks must be implemented before they are claimed as active.

### Negative / Risks

- **Developer Friction**: Developers might find dot-notation and multi-layered token resolution more complex than writing standard CSS.
  - _Mitigation_: Mitigated by providing comprehensive IDE autocomplete configurations and strongly-typed SCSS/TypeScript utility helpers.

### Operational

- Mandated as the standard design token consumption boundary starting with version `1.0.0`.
- All CSS compilation tools (Style Dictionary, custom compilers) must output variables aligned to this 3-tier boundary structure.

## 7. Compliance Impact

### Related Standards

- [Documentation Governance Standard (GDC-000)](../../00-governance/GDC-000-governance-policy.md)
- [Enterprise Standards Guideline (GDC-007)](../../00-governance/GDC-007-std-guideline.md)
- [Design Token Standard (STD-UIP-TKN-001)](../../02-standards/ui-platform/STD-UIP-TKN-001-design-tokens.md)

### Compliance Status

Architecture accepted; implementation conformance pending executable source and packed-package evidence.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Flat Design Token Dictionary

- **Pros**: Flat structure, straightforward compilation, low learning curve for new developers.
- **Cons**: Lacks structural isolation, leading to token explosion and high maintenance overhead when scaling to support multi-brand and white-labeled portals.
- **Why Rejected**: Fails to provide architectural decoupling between design values and design intent, rendering multi-tenant brand re-skinning highly error-prone.

### Alternative B: Direct CSS Custom Properties in Components

- **Pros**: Native browser support and direct stylesheet consumption.
- **Cons**: Raw-value custom properties used directly by components omit the shared semantic boundary.
- **Why Rejected**: The design needs governed semantic names; CSS custom properties remain the selected output format for those names.
