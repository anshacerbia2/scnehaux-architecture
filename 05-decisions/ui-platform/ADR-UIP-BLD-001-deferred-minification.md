---
doc_meta:
  id: ADR-UIP-BLD-001
  title: Deferred Minification
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: proposed
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-09-28
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Staff Engineer
---

# Deferred Minification Strategy for UI Libraries (ADR-UIP-BLD-001)

> **Pre-production correction candidate:** retaining readable library output is a delivery choice to verify in packed consumers. This wording carries no authority until the UI Platform Lead records actual approval.

---

## 1. Title

Deferred Minification Strategy for UI Libraries to Enhance Debugging

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                 | Approver                   |
| ---------- | -------- | ------------ | ----------------------------------------- | -------------------------- |
| 2026-09-28 | proposed | foundational | Consolidated principal review in progress | UI Platform Lead — pending |

## 3. Context

The Scnehaux UI Platform distributes two core shared packages: `@scnx/core-ui` (React primitives) and `@scnx/system` (tokens/styling logic). Originally, the Technical Design Document (STD-GLB-FE-008) specified that the build compiler (`tsup`) should run `minify: true` to compress output JS/CSS assets prior to publishing to the NPM registry.

Minifying library output may reduce debugging readability. Final consumer output depends on the application bundler and the published module graph.

## 4. Decision Drivers

- Superior Developer Experience (DX) for deep stack-trace debugging.
- Measured consumer bundle cost and source-map quality.

## 5. Decision

The library build keeps JS readable (`minify: false`). The packed-package and application-consumer gates measure tree shaking, final compressed bytes, and usable source maps. Consumer bundlers remain responsible for their final output policy; they may or may not minify every library path.

## 6. Consequences

### Positive (Pros)

- **Superior Developer Experience (DX):** Consuming engineers can step through unminified library source code inside `node_modules` during deep stack-trace debugging.
- **Auditability:** Readable package output can simplify investigation, while source maps and export structure remain necessary for diagnosis.

### Negative (Cons)

- **Package and runtime cost:** Tarballs may be larger, and some consumer builds may retain more bytes. Measure representative application bundles rather than assume the difference is immaterial.

## 7. Compliance Impact

No waiver is requested. Packed exports and representative consumers must be tested under STD-UIP-ENG-001; final minification is not claimed as automatic.

## 8. Alternatives Considered

- **Minifying library code:** May reduce tarball bytes but can hinder direct inspection. Reconsider if measured consumer output, source maps, or distribution requirements favor it.
