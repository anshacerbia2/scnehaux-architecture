---
doc_meta:
  id: ADR-GLB-FE-004
  title: Conditional Micro-Frontend Integration with Module Federation
  adr_type: foundational
  status: proposed
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Principal Frontend Architect
  governed_by: [EAD-005]
---

# ADR-GLB-FE-004: Conditional Micro-Frontend Integration with Module Federation

> **Pre-production correction candidate:** ADR-GLB-FE-010 proposes authorization for this in-place revision. This wording carries no authority until the ARB records actual approval in the single status row.

## 1. Title

Use Module Federation for approved micro-frontend compositions.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                 | Approver                            |
| ---------- | -------- | ------------ | ----------------------------------------- | ----------------------------------- |
| 2026-09-28 | proposed | foundational | Consolidated principal review in progress | Architecture Review Board — pending |

## 3. Context

STD-GLB-FE-007 permits a micro-frontend architecture only when organizational and release-autonomy criteria justify its operational cost. Approved MFE systems need a standard runtime composition protocol, explicit shared-module identity, and controlled remote failure behavior.

The architectural contract must survive bundler evolution. Webpack, Rspack, Rsbuild, and Vite integrations can implement Module Federation with different configuration surfaces.

## 4. Decision Drivers

- Independent deployment for approved MFE boundaries.
- One React and shared-context identity where the UI contract requires it.
- Explicit version negotiation and failure behavior.
- Deterministic CSS ownership.
- Bundler evolution behind integration fixtures.

## 5. Decision

Approved micro-frontend systems use the **Module Federation protocol**. The implementing bundler and federation plugin are selected and recorded by the system design; this ADR does not mandate Webpack or Rsbuild.

The composition host owns the federation policy:

1. `react` and `react-dom` are singleton shared modules.
2. Every supported public package request that carries React context or shared state is an explicit singleton share key generated from the package export inventory.
3. `requiredVersion` comes from the relevant package manifest range.
4. Remotes remain lazy. Only the host may choose eager loading for an entry required before any remote executes.
5. Incompatible required versions produce a controlled route/feature failure and telemetry event.
6. UI Platform component and theme CSS is imported by the composition root. Remotes do not inject another copy.
7. Cross-application communication uses versioned public contracts, scoped context, or documented custom events. A remote never imports another application's internal source.

A host and two remotes installed from packed artifacts must prove identity, version behavior, both load orders, remote unavailability handling, and stylesheet ownership before production adoption.

## 6. Consequences

- **Positive:** the durable decision concerns protocol behavior and module identity.
- **Positive:** compatible bundlers can evolve behind the fixture.
- **Negative:** explicit share inventories and integration fixtures require maintenance.
- **Operational:** host configuration is release-critical and changes require compatibility review.

## 7. Compliance Impact

Related standards: STD-GLB-FE-007, STD-UIP-ENG-001, and STD-UIP-STY-001. ADR-GLB-FE-010 authorizes the pre-production correction. No waiver is requested.

## 8. Alternatives Considered

- Bundler-specific mandate: rejected because the protocol and verified runtime behavior are the lasting contracts.
- Iframes: rejected for isolated document semantics, focus/portal boundaries, and integration cost.
- Route-level full-page composition: valid for systems that do not require runtime component composition; it remains outside this ADR's approved MFE scenario.
