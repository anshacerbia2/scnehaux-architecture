---
doc_meta:
  id: ADR-GLB-FE-006
  title: Static CSS Output and Token-Bound Styling
  adr_type: foundational
  status: proposed
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Principal Frontend Architect
  governed_by: [EAD-005]
---

# ADR-GLB-FE-006: Static CSS Output and Token-Bound Styling

> **Pre-production correction candidate:** ADR-GLB-FE-010 proposes authorization for this in-place revision. This wording carries no authority until the ARB records actual approval in the single status row.

## 1. Title

Produce static CSS for shared UI and govern styling tools by output ownership.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                 | Approver                            |
| ---------- | -------- | ------------ | ----------------------------------------- | ----------------------------------- |
| 2026-09-28 | proposed | foundational | Consolidated principal review in progress | Architecture Review Board — pending |

## 3. Context

Runtime CSS evaluation and render-path injection add client work, complicate strict CSP, and create uncertain order across server rendering and federated applications. Static CSS can be produced by Sass, PostCSS, CSS Modules, Panda CSS, Vanilla Extract, or other build tools.

The previous decision mandated Panda CSS or Vanilla Extract and rejected Sass. The UI Platform baseline already uses Sass for component skins and Panda for recipes. Tool identity alone does not prove token discipline, selector isolation, payload efficiency, or RSC compatibility.

## 4. Decision Drivers

- Static and deterministic consumer assets.
- Strict CSP compatibility.
- One token contract across producer tools.
- Explicit selector, layer, and asset ownership.
- Measured migration and payload cost.

## 5. Decision

Shared UI Platform styling is distributed as **static CSS assets**. Runtime string evaluation and render-path style injection are prohibited.

During the pre-release remediation milestone:

1. Sass owns current skinned component rules.
2. Panda owns only its existing declared recipe surface; new Panda recipe ownership is frozen.
3. Sass-facing and Panda-facing token names are generated from one versioned source.
4. Sass component rules use the `components` layer and Panda recipes use the `recipes` layer.
5. Panda runs only in the producer. Packed consumers never scan source or run Panda.
6. `@scnx/core-ui` remains styling-engine agnostic and is removed from Panda scan inputs after callsite verification.
7. The exit review compares CSS size per import, `staticCss` output, duplicate declarations, undefined variables, override behavior, build time, and migration cost.

The exit review may retain the bounded dual-engine model or select consolidation through a follow-up implementation decision. Stable public contracts remain CSS assets, token names, selectors/data attributes, and package exports.

Applications may use other approved static styling approaches within STD-GLB-FE-005.

## 6. Consequences

- **Positive:** consumers receive deterministic static assets without producer tooling.
- **Positive:** migration decisions use measured output and ownership data.
- **Negative:** dual-engine governance adds temporary build and review work.
- **Operational:** layer order, generated names, and CSS exports become release contracts.

## 7. Compliance Impact

Related standards: STD-GLB-FE-005, STD-UIP-STY-001, STD-UIP-TKN-001, and STD-UIP-ENG-001. ADR-GLB-FE-010 authorizes the pre-production correction. No waiver is requested.

## 8. Alternatives Considered

- Mandate Panda CSS or Vanilla Extract: rejected because a vendor mandate does not establish output quality and would force an unmeasured rewrite.
- Reject Sass globally: rejected because static Sass output can satisfy the same public contract.
- Runtime CSS-in-JS for shared UI: rejected because it violates the static-output and CSP contract.
- Immediate consolidation before evidence: rejected because it would choose migration cost without consumer measurements.
