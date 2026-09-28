---
doc_meta:
  id: ADR-GLB-FE-013
  title: Static CSS Output and Token-Bound Styling
  adr_type: replacement
  status: proposed
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [EAD-005]
  supersedes: [ADR-GLB-FE-006]
---

# ADR-GLB-FE-013: Static CSS Output and Token-Bound Styling

## 1. Title

Replace ADR-GLB-FE-006 with a styling decision governed by output ownership instead of tool identity.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                                 | Approver                            |
| ---------- | -------- | ----------- | ----------------------------------------- | ----------------------------------- |
| 2026-09-28 | proposed | replacement | Consolidated principal review in progress | Architecture Review Board — pending |

## 3. Context

Runtime CSS evaluation and render-path style injection add client work, need relaxed Content Security Policy, and make style order uncertain across server rendering and federated applications. Static CSS can be produced by Sass, PostCSS, CSS Modules, Panda CSS, Vanilla Extract, or other build tools.

ADR-GLB-FE-006 mandated Panda CSS or Vanilla Extract and rejected Sass. The UI Platform baseline already uses Sass for component skins and Panda for recipes. Tool identity alone does not prove token discipline, selector isolation, payload size, or server-component compatibility.

The production status of every frontend governed by ADR-GLB-FE-006 cannot be established from the architecture repository (see ADR-GLB-FE-011 section 3). GDC-010 section 2.4.2 therefore requires a replacement ADR: ADR-GLB-FE-006 stays `accepted` and binding until this record is ratified.

## 4. Decision Drivers

- Static, deterministic assets for every consumer.
- Compatibility with a Content Security Policy that rejects `unsafe-eval` and `unsafe-inline`.
- One token contract across producer tools.
- Explicit ownership of selectors, cascade layers, and assets.
- Migration cost decided by measured output.

## 5. Decision

1. **Shared UI Platform styling** is distributed as static CSS assets. Runtime string evaluation and render-path style injection are prohibited in shared UI.
2. **Applications** produce static CSS. Runtime CSS-in-JS that injects styles during render is prohibited in new applications; an existing application that uses it records a migration plan in its SAD.
3. **UI Platform during the pre-release remediation milestone:**
   1. Sass owns the current skinned component rules.
   2. Panda owns only its existing recipe surface; new Panda recipes are frozen.
   3. Sass-facing and Panda-facing token names are generated from one versioned token source.
   4. Sass component rules use the `components` layer; Panda recipes use the `recipes` layer.
   5. Panda runs only in the producer. Packed consumers never scan source or run Panda.
   6. `@scnx/core-ui` stays independent of any styling engine and is removed from Panda scan inputs.
   7. The milestone exit review compares CSS size per import scenario, `staticCss` output, duplicate declarations, unresolved variables, override behavior, build time, and migration cost, and either keeps the bounded two-engine model or selects consolidation through an implementation decision.
4. The stable public styling contracts are CSS assets, token names, selectors and data attributes, and package exports.

## 6. Consequences

- **Positive:** consumers receive deterministic static assets without producer tooling.
- **Positive:** a strict Content Security Policy needs no styling exception.
- **Negative:** two-engine governance adds temporary build and review work.
- **Operational:** layer order, generated token names, and CSS exports become release contracts.

## 7. Compliance Impact

Supersedes ADR-GLB-FE-006 on ratification. Related standards: STD-GLB-FE-005, STD-UIP-STY-001, STD-UIP-TKN-001, and STD-UIP-ENG-001. No waiver is requested.

## 8. Alternatives Considered

- Mandate Panda CSS or Vanilla Extract: rejected because a tool mandate does not establish output quality and would force an unmeasured rewrite.
- Reject Sass globally: rejected because static Sass output satisfies the same public contract.
- Runtime CSS-in-JS for shared UI: rejected because it breaks the static-output and Content Security Policy contract.
- Consolidate before measuring: rejected because it would commit to a migration cost without consumer measurements.
