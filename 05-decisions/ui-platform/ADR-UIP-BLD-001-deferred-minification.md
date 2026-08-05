---
doc_meta:
  id: ADR-UIP-BLD-001
  title: Deferred Minification
  adr_type: foundational
  owner: Principal UI/UX Architect
  version: 1.0.0
  status: accepted
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-06-26
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Staff Engineer
---

# Deferred Minification Strategy for UI Libraries (ADR-UIP-BLD-001)

---

## 1. Title

Deferred Minification Strategy for UI Libraries to Enhance Debugging

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                  |
| ---------- | -------- | ------------ | ------------------------- | ------------------------- |
| 2026-06-20 | accepted | foundational | Architecture Review Board | Principal UI/UX Architect |

## 3. Context

The Scnehaux UI Platform distributes two core shared packages: `@scnx/core-ui` (React primitives) and `@scnx/system` (tokens/styling logic). Originally, the Technical Design Document (STD-GLB-FE-008) specified that the build compiler (`tsup`) should run `minify: true` to compress output JS/CSS assets prior to publishing to the NPM registry.

However, minifying source code at the library distribution level introduces significant debugging friction for consuming applications and can conflict with application-level bundler optimizations.

## 4. Decision Drivers

- Superior Developer Experience (DX) for deep stack-trace debugging.
- Efficient Dead Code Elimination downstream.
- Avoidance of double-minification bugs.

## 5. Decision

We will **deliberately disable minification** (`minify: false`) for all UI library package builds. The responsibility for final code minification, obfuscation, and source-mapping is formally deferred to the downstream Host/Consumer application's bundler (e.g., Vite, Next.js, Rspack).

## 6. Consequences

### Positive (Pros)

- **Superior Developer Experience (DX):** Consuming engineers can step through unminified library source code inside `node_modules` during deep stack-trace debugging.
- **Efficient Tree-Shaking:** Modern application bundlers perform Dead Code Elimination (Tree-Shaking) much more efficiently on clean, unminified ESM code.
- **Elimination of Double-Minification:** Prevents edge-case variable mangling bugs caused when a library is minified, and then the consuming application minifies it again during production build.

### Negative (Cons)

- **Increased NPM Package Size:** The raw bytes transferred during `npm install` (and stored on disk) will be slightly larger. This is acceptable as it does not affect the end-user production payload.
- **False Positive Size Checks:** Developers inspecting the raw library bundle might mistakenly assume the code is unoptimized. Size limits (e.g., the 12KB budget defined in STD-UIP-ENG-001) must be measured post-bundling/gzip via tools like `size-limit`, rather than by checking raw file sizes.

## 7. Compliance Impact

No regulatory compliance impact. Code is still ultimately minified and obfuscated during the final application production build.

## 8. Alternatives Considered

- **Minifying Library Code (Status Quo):** Rejected because the minor savings during `npm install` do not justify the massive loss in debuggability and the risk of tree-shaking failures downstream.
