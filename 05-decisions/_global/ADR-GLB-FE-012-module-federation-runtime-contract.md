---
doc_meta:
  id: ADR-GLB-FE-012
  title: Module Federation Runtime Contract
  adr_type: replacement
  status: accepted
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [EAD-005]
  supersedes: [ADR-GLB-FE-004]
---

# ADR-GLB-FE-012: Module Federation Runtime Contract

## 1. Title

Replace ADR-GLB-FE-004 with a Module Federation decision defined by shared-module identity, version negotiation, and failure behavior.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                   | Approver                                 |
| ---------- | -------- | ----------- | --------------------------- | ---------------------------------------- |
| 2026-09-29 | accepted | replacement | Principal 1 and Principal 2 | Ansha Cerbia (Architecture Review Board) |

## 3. Context

STD-GLB-FE-007 permits a micro-frontend architecture only when release-autonomy criteria justify its cost. ADR-GLB-FE-004 selected Module Federation and bound it to Webpack or Rsbuild, but did not define which modules are shared, how versions are negotiated, or what happens when they are incompatible.

The UI Platform audit found the practical gap. Hosts declared `@scnx/system` and `@scnx/core-ui` as share keys while applications imported package subpaths, which those keys do not match. The context-bearing modules behind those subpaths were therefore outside the share configuration, and every remote was eager.

The production status of every frontend governed by ADR-GLB-FE-004 cannot be established from the architecture repository (see ADR-GLB-FE-011 section 3). GDC-010 section 2.4.2 therefore required a replacement ADR; acceptance of this record supersedes ADR-GLB-FE-004.

## 4. Decision Drivers

- Independent deployment for approved micro-frontend boundaries.
- Exactly one instance of React, React DOM, and every module that carries React context or shared state.
- Version incompatibility that fails in a controlled, observable way.
- One owner for shared CSS.
- Evidence from installed artifacts, not workspace aliases.

## 5. Decision

Approved micro-frontend systems use the **Module Federation protocol**, compiled with the toolchain in ADR-GLB-FE-011. The composition host owns the federation policy:

1. `react`, `react-dom`, and `@scnx/core-ui` are shared as singletons with a strict compatible range. Every other public package entry that carries React context or shared state is shared the same way.
2. Share keys are explicit and generated from each package's public export inventory. Wildcard public exports are not part of a shared package's contract.
3. `requiredVersion` is taken from the peer or dependency range that the consuming application or package declares for that module.
4. Remotes load lazily. Only the host may load an entry eagerly, and only when it is required before any remote executes.
5. An incompatible version produces a controlled failure: the affected route or feature renders its fallback, the rest of the host keeps working, and a telemetry event records both versions. A remote never silently falls back to its own copy of a singleton.
6. A failing or unreachable remote is contained by the host at its route or feature boundary.
7. UI Platform component and theme CSS is imported once by the composition root. Remotes do not load another copy.
8. Applications communicate through versioned public contracts, scoped context, or documented custom events. A remote never imports another application's internal source.

**Required evidence before production adoption:** one host and two remotes, installed from packed artifacts, prove singleton identity, compatible and incompatible version behavior, both remote load orders, remote unavailability handling, and a single stylesheet instance.

## 6. Consequences

- **Positive:** the decision governs runtime behavior, which is what federated applications depend on.
- **Positive:** context duplication and silent version drift become test failures.
- **Negative:** export inventories, share maps, and host fixtures need maintenance.
- **Operational:** a host share-map change is release-critical and needs a compatibility review.

## 7. Compliance Impact

Supersedes ADR-GLB-FE-004 on ratification. Related decisions: ADR-GLB-FE-011 and ADR-UIP-PLT-001. Related standards: STD-GLB-FE-007, STD-UIP-ENG-001, and STD-UIP-STY-001. No waiver is requested.

## 8. Alternatives Considered

- Keep a bare package name as the share key: rejected because subpath imports bypass it and duplicate context-bearing modules.
- Eager remotes: rejected because they load every remote before the host renders and hide version failures until runtime.
- Iframes: rejected for isolated document semantics, focus and portal boundaries, and integration cost.
- Route-level full-page composition: valid for systems that do not compose components at runtime; it is outside this ADR's scope.
