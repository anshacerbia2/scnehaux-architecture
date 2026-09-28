---
doc_meta:
  id: ADR-UIP-PLT-001
  title: Verifiable UI Platform Package and Release Contract
  adr_type: conflict_resolution
  status: proposed
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [PAD-PLT-003]
---

# ADR-UIP-PLT-001: Verifiable UI Platform Package and Release Contract

## 1. Title

Authorize the proposed major UI Platform standard revisions for package, token, component, and release evidence.

## 2. Status

| Date       | Status   | ADR Type            | Reviewers                                                                                | Approver                        |
| ---------- | -------- | ------------------- | ---------------------------------------------------------------------------------------- | ------------------------------- |
| 2026-09-28 | proposed | conflict_resolution | Principal review round 1: approve with required changes; remaining consolidation pending | Architecture authority, pending |

## 3. Context

The baseline has two physical packages and three logical token tiers. Static review and emitted CSS reveal defects: some shadow and color values are invalid, font names drift, component CSS delivery is uncertain, the design-system test is a placeholder, ThemeProvider uses unsafe evaluation and a singleton global callback, and RSC boundaries rely on a fragile regex. In the standalone workspace, the core-ui suite runs ten tests, but the design-system declaration build exhausted the default Node heap. Existing standards claim guarantees not supported by package-consumer evidence. The platform has never governed a production system.

## 4. Decision Drivers

- Release what a consumer can actually install and use.
- Preserve the dependency boundary from `@scnx/system` to `@scnx/core-ui`.
- Make accessibility, theming, security, and style delivery testable.
- Avoid binding the platform to premature vendor or engine decisions.

## 5. Decision

**Proposed, not yet authoritative:** Authorize the major revisions of STD-UIP-TKN-001, STD-UIP-TKN-002, STD-UIP-PRM-001, STD-UIP-STY-001, and STD-UIP-ENG-001. Keep three token tiers as a logical model and two packages as the present physical model. Use source tests for interaction and state logic. Use isolated `npm pack` consumers for exports, types, CSS, fonts, SSR/RSC, CSP, and shell/remote integration. Report component evidence in a Component Accessibility Conformance Report without claiming page-level certification. Declare theme scope, styling ownership, performance scenarios, and release exceptions explicitly.

The working CSS delivery contract exports aggregate component CSS and explicit theme CSS. A standalone shell or federated host composition root imports each required stylesheet once. Component JavaScript has no CSS side-effect import, and remotes do not inject another copy. Portaled UI receives an explicit themed container or equivalent propagation contract. Panda runs only in the producer build; a packed consumer never scans source or runs Panda to render shipped components. After verifying that `@scnx/core-ui` has no Panda callsites, its source is removed from Panda scan inputs.

React Aria adoption, multiple brands in one DOM, long-term Sass/Panda ownership, and polymorphism retain empirical gates; this ADR does not resolve them by implication. The working candidates are selected React Aria hooks behind complex-widget APIs, scoped subtree themes, both style engines during P0, and `asChild` where polymorphism is justified. Approval authorizes the standards revision, while each candidate still requires recorded evidence, provenance review, and migration impact.

## 6. Consequences

- Positive: a reproducible release gate for the shipped artifact and clearer package ownership.
- Negative: isolated consumers and scenario matrices add maintenance cost.
- Operational: the extracted baseline cannot be promoted until P0 failures and conformance gaps are resolved.
- Operational: arbitrary size limits and a larger Node heap are not conformance evidence; budgets require a named scenario and heap overrides remain diagnostic only.

## 7. Compliance Impact

Related standards: [token](../../02-standards/ui-platform/STD-UIP-TKN-001-design-tokens.md), [consumption](../../02-standards/ui-platform/STD-UIP-TKN-002-consumption-governance.md), [primitive](../../02-standards/ui-platform/STD-UIP-PRM-001-primitive-components.md), [styled](../../02-standards/ui-platform/STD-UIP-STY-001-styled-components.md), [delivery](../../02-standards/ui-platform/STD-UIP-ENG-001-build-and-delivery.md). No waiver is requested. Current status is pending architecture approval.

## 8. Alternatives Considered

- Treat a passing type check or source build as release proof: misses broken CSS values and export resolution.
- Create a third token package immediately: adds version coordination before consumer value is demonstrated.
- Choose one styling engine immediately: the baseline has measurable drift, but no complete cost comparison yet.
