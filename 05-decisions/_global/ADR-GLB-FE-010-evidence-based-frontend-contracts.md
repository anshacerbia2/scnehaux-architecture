---
doc_meta:
  id: ADR-GLB-FE-010
  title: Evidence-Based Frontend Contracts and UI Platform Alignment
  adr_type: conflict_resolution
  status: proposed
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [EAD-005]
---

# ADR-GLB-FE-010: Evidence-Based Frontend Contracts and UI Platform Alignment

## 1. Title

Authorize coherent evidence-based frontend standards and pre-production ADR corrections.

## 2. Status

| Date       | Status   | ADR Type            | Reviewers                                                                          | Approver                            |
| ---------- | -------- | ------------------- | ---------------------------------------------------------------------------------- | ----------------------------------- |
| 2026-09-28 | proposed | conflict_resolution | Principal review: approve with required changes; consolidated verification pending | Architecture Review Board — pending |

## 3. Context

The active frontend documents contain mutually exclusive rules:

- ADR-GLB-FE-006 mandates Panda CSS or Vanilla Extract and rejects Sass, while the UI Platform currently produces Sass component rules and Panda recipes.
- STD-GLB-FE-005 defines a six-layer order and document-root themes, while the UI Platform needs a named recipe layer and multiple scoped brands in one DOM.
- STD-GLB-FE-006 mandates broad manual memoization, while STD-GLB-FE-002 requires profiling and identity evidence.
- ADR-GLB-FE-004 binds Module Federation to Webpack/Rsbuild even though the architectural contract is the federation protocol, shared identity, and failure behavior.
- STD-GLB-FE-009 applies one contrast ratio to text and non-text UI even though WCAG 2.2 separates SC 1.4.3 and SC 1.4.11.
- STD-GLB-FE-001 prohibits every hardcoded presentation value, while the token governance standard permits reviewed context-specific structural values.

No governed UI Platform system has entered production. GDC-010 section 2.4.2 permits accepted ADRs to be corrected in place before production. GDC-007 section 2.4.2 requires this ADR to authorize major standard revisions.

## 4. Decision Drivers

- One coherent rule set across global frontend and UI Platform documents.
- Measurable package and application contracts.
- Accessible behavior defined by widget and page responsibility.
- Bundler and vendor choices that can evolve behind stable public contracts.
- Explicit review authority and traceable major-version authorization.

## 5. Decision

**Proposed pending ARB approval.** This ADR authorizes the version 2.0.0 revisions of STD-GLB-FE-001, STD-GLB-FE-002, STD-GLB-FE-005, STD-GLB-FE-006, STD-GLB-FE-007, and STD-GLB-FE-009. Each standard must name this ADR in `governed_by` before approval.

The coherent frontend contract is:

1. Governed shared visual decisions use semantic tokens. Reviewed structural literals remain valid where a shared semantic token would misrepresent intent.
2. Performance requirements identify the scenario, environment, tool, representation, baseline, and threshold. Reference identity is stabilized when semantics or measurement require it.
3. The canonical cascade order is `reset, tokens, base, components, recipes, utilities, overrides`. Sass component rules use `components`; Panda recipes use `recipes`.
4. Public multi-brand themes use scoped `[data-scnx-theme]` roots. A separate `:root` compatibility output may serve a single-brand document. Portals remain inside their originating scope.
5. Shared UI styling produces static CSS. The UI Platform may use Sass and a frozen set of Panda recipes under one generated token contract through the pre-release remediation milestone. Consolidation follows measured output.
6. Module Federation is the selected integration protocol for approved MFE scenarios. The decision is bundler-neutral. The host owns explicit singleton share keys for React and every context-bearing UI request, derives `requiredVersion` from manifests, and keeps remotes lazy.
7. WCAG 2.2 SC 1.4.3 governs text contrast and SC 1.4.11 governs non-text UI contrast. Component evidence supports product evaluation and does not certify a complete page.

This ADR also authorizes pre-production in-place corrections to ADR-GLB-FE-004 and ADR-GLB-FE-006 so their decisions express the protocol and static-output contracts above.

## 6. Consequences

- **Positive:** global and UI standards form one enforceable contract.
- **Negative:** host/remote fixtures, package consumers, browser measurements, and accessibility evidence add maintenance cost.
- **Operational:** proposed standards remain non-authoritative until the ARB approves this ADR and the status changes occur in the same ratification change.
- **Operational:** established consumers require migration notes for layer order, theme selectors, or share-map changes once production begins.

## 7. Compliance Impact

Affected global standards: STD-GLB-FE-001, STD-GLB-FE-002, STD-GLB-FE-005, STD-GLB-FE-006, STD-GLB-FE-007, and STD-GLB-FE-009.

Affected accepted ADRs: ADR-GLB-FE-004 and ADR-GLB-FE-006, edited in place under the pre-production rule.

Related UI authority: ADR-UIP-PLT-001, PAD-PLT-003, and SAD-003. No waiver is requested.

## 8. Alternatives Considered

- Preserve the conflicting documents and choose locally: rejected because two active mandates cannot both be enforced.
- Mandate one vendor or bundler globally: rejected because consumer behavior and protocol compatibility are the durable contracts.
- Keep absolute budgets without measurement definitions: rejected because such claims are not reproducible.
