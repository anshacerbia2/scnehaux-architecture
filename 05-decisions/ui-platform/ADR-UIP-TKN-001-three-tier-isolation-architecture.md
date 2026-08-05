---
doc_meta:
  id: ADR-UIP-TKN-001
  title: ADR-UIP-TKN-001 Three-Tier Design Token Isolation Architecture
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Enterprise Architect
---

# ADR-UIP-TKN-001: Adoption of a Three-Tier Design Token Architecture (Core, Semantic, Component) to Isolate Raw Visual Values from Semantic Intent.

---

## 1. Title

Adoption of a Three-Tier Design Token Architecture (Core, Semantic, Component) to Isolate Raw Visual Values from Semantic Intent.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

As the Scnehaux ecosystem scales across multiple standalone portals and federated micro-frontends (e.g., HRIS, Finance, IAM), maintaining a unified visual language becomes exponentially difficult. Hardcoding raw color hexes or generic variables (e.g., `$blue-9`) directly into component stylesheets creates severe technical debt:

1. **Semantic Ambiguity:** `$blue-9` provides no context on _why_ the color is used (is it a primary button, an info alert, or a selected row?).
2. **Theming & White-labeling Blockers:** Switching a brand's primary color from Blue to Purple requires finding and replacing `$blue-9` across hundreds of files, often causing unintended side-effects where Blue was used for structural purposes instead of brand identity.
3. **Loss of Central Governance:** Frontend engineers invent local color assignments, destroying the unified Visual Root of Trust.

## 4. Decision Drivers

By enforcing this architectural boundary, we completely decouple the _Design Value_ from the _Design Intent_.

- **Enterprise Theming:** When a new white-label tenant requires a Purple theme, the platform simply maps `primary.solid.default` to `purple.9` instead of `blue.9` at the Tier 2 level. Zero application code needs to change.
- **Predictable Maintenance:** Developers consume contextual intent (`danger.surface.subtle`), ensuring that alerts will always look like alerts regardless of the underlying color palette or dark/light mode context.

## 5. Decision

We mandate a strict **Three-Tier Design Token Isolation Architecture** across all Scnehaux frontend systems. Raw visual values must never be consumed directly by application components.

### Tier 1: Core Primitives (The Raw Values)

- **Definition:** Pure, platform-agnostic mathematical scales without any UI context (e.g., `blue.9`, `spacing.4`, `radius.lg`).
- **Rule:** **Forbidden** from direct use in any UI component or application code.

### Tier 2: Semantic Tokens (The Global Intent)

- **Definition:** The single source of truth mapping Tier 1 Core Primitives to structural UI intent (e.g., `primary.solid.default`, `surface.sunken.default`).
- **Rule:** This is the **standard consumption layer** for 95% of all styling. All themes and white-labeling overrides must target this layer.

### Tier 3: Component Aliases (Unique Overrides)

- **Definition:** Highly specific tokens scoped to a single component (e.g., `checkbox.border.checked`).
- **Rule:** Strictly budgeted and restricted. Only permitted for truly unique semantic behaviors that require independent visual divergence from global Tier 2 semantics.

---

## 6. Consequences

- **Positive:** Infinite horizontal scaling of UI themes without touching component source code. Guaranteed Dark Mode symmetry.
- **Negative:** Increased initial cognitive load for engineers who must learn the Semantic Taxonomy instead of using raw colors.
- **Enforcement:** The governance linter and CI pipelines will reject pull requests containing hardcoded CSS colors or direct references to Tier 1 Core Tokens inside application components.

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

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Flat Design Token Dictionary

- **Pros**: Flat structure, straightforward compilation, low learning curve for new developers.
- **Cons**: Lacks structural isolation, leading to token explosion and high maintenance overhead when scaling to support multi-brand and white-labeled portals.
- **Why Rejected**: Fails to provide architectural decoupling between design values and design intent, rendering multi-tenant brand re-skinning highly error-prone.

### Alternative B: Direct CSS Custom Properties in Components

- **Pros**: Native browser support, zero build-time dependency.
- **Cons**: Lacks semantic validation, no compile-time contract enforcement, high risk of inconsistent visual tokens leaking into components.
- **Why Rejected**: Bypasses the centralized design system governance and token contract validation pipeline.
