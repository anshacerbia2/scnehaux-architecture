---
doc_meta:
  id: ADR-GLB-FE-010
  title: Evidence-Based Frontend Standards and UI Foundation Choice
  adr_type: conflict_resolution
  status: proposed
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [GDC-000]
---

# ADR-GLB-FE-010: Evidence-Based Frontend Standards and UI Foundation Choice

## 1. Title

Authorize the proposed major revisions of STD-GLB-FE-001 and STD-GLB-FE-002.

## 2. Status

| Date       | Status   | ADR Type            | Reviewers                           | Approver                        |
| ---------- | -------- | ------------------- | ----------------------------------- | ------------------------------- |
| 2026-09-28 | proposed | conflict_resolution | Three principal architects, pending | Architecture authority, pending |

## 3. Context

STD-GLB-FE-001 mandates Radix while STD-UIP-PRM-001 prohibits third-party interaction libraries. They cannot both govern the same UI Platform. Existing performance language also promises universal zero reflow, fixed bundle limits, and frame rates without a scenario or measurement method. No governed UI system has entered production. GDC-010 therefore permits editing accepted ADRs in place, while GDC-007 still requires ADR authorization for major STD changes.

## 4. Decision Drivers

- A coherent global and platform-specific rule set.
- Accessible behavior and consumer evidence over vendor identity.
- Measurable budgets tied to an environment and import scenario.
- Evolution without hiding breaking contract changes.

## 5. Decision

**Proposed, not yet authoritative:** Authorize the major changes in STD-GLB-FE-001 and STD-GLB-FE-002. Global frontend guidance defines behavior and release evidence, not an unconditional Radix dependency. The UI Platform can implement behavior itself or use a reviewed library behind its public API. Vendor choice, including React Aria scope, requires an implementation decision and consumer tests. Performance rules require named scenarios, baselines, metrics, and thresholds; unmeasured universal guarantees are removed.

Approval of this ADR would authorize the edited standards. Until approval, their new wording remains a review draft and does not silently replace the current approved rule set.

## 6. Consequences

- Positive: removes a cross-standard contradiction and makes conformance falsifiable.
- Negative: vendor-neutral language needs a maintained behavior matrix and release fixtures.
- Operational: standard versions increase major; implementations must supply evidence before claiming compliance.

## 7. Compliance Impact

Related standards: [STD-GLB-FE-001](../../02-standards/_global/STD-GLB-FE-001-tech-stack.md), [STD-GLB-FE-002](../../02-standards/_global/STD-GLB-FE-002-performance.md), [STD-UIP-PRM-001](../../02-standards/ui-platform/STD-UIP-PRM-001-primitive-components.md), and GDC-007. No waiver is requested. Current status is pending architecture approval.

## 8. Alternatives Considered

- Mandate Radix across the platform: conflicts with the existing local prohibition and makes vendor choice a proxy for conformance.
- Prohibit all external interaction libraries: prevents adopting a library where comparative evidence shows lower risk.
- Preserve absolute numerical guarantees: lacks a defined consumer scenario and cannot be audited honestly.
