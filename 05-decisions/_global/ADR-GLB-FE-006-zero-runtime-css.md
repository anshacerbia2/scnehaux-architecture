---
doc_meta:
  id: ADR-GLB-FE-006
  title: ADR-GLB-FE-006 Zero-Runtime CSS and Utility-First Compilation
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-006: Adopting Zero-Runtime CSS and Utility-First Compilation for UI Performance

---

## 1. Title

ADR-GLB-FE-006: Adopting Zero-Runtime CSS and Utility-First Compilation for UI Performance

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                     |
| ---------- | -------- | ------------ | ------------------------- | ---------------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Principal Frontend Architect |

## 3. Context

Historically, teams have relied heavily on Runtime CSS-in-JS libraries (e.g., Styled Components, Emotion). These libraries execute intensive style compilation and class injection on the client-side during the render cycle, causing severe layout thrashing and blocking compatibility with modern React Server Components (RSC).

## 4. Decision Drivers

Moving CSS compilation from the client's browser to the CI/CD build pipeline eliminates style-related layout thrashing and unblocks 60FPS rendering performance. Zero-runtime CSS is fundamentally compatible with React Server Components and Next.js App Router streaming architectures.

## 5. Decision

We will standardize on a **Zero-Runtime Styling Strategy** for the core enterprise UI Platform, mandating libraries like Panda CSS or Vanilla Extract. We conditionally authorize **Constrained Utility-First Frameworks** (e.g., TailwindCSS) for end-consumer SPAs to facilitate rapid layout composition, provided the configuration is mapped to central Design System tokens.

## 6. Consequences

- **Positive**: Rendering supremacy, native RSC compatibility, and strict type-safety blocking invalid token usage at compile time.
- **Negative**: Dynamic styles must be knowable at build-time. Complex string interpolation in class names will fail the static AST analyzer.

### Negative / Risks

- **Migration Cost**: Rewriting thousands of legacy `styled.div` components into zero-runtime macros requires significant engineering effort.
- **Build Times**: AST parsing of every file to generate static CSS can increase build pipeline duration.

### Operational

- Utility classes with arbitrary/magic values (e.g., `w-[13px]`) are prohibited and must be blocked by Linter rules.
- Legacy charting libraries that cannot consume CSS variables must be strictly isolated via Shadow DOM.

## 7. Compliance Impact

### Related Standards

- STD-GLB-FE-007 (Styling)
- [ADR-UIP-TKN-002 (OKLCH)](../ui-platform/ADR-UIP-TKN-002-oklch-and-dual-engine-alpha.md)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **Runtime CSS-in-JS (Styled Components / Emotion)**: Rejected. The performance penalty of parsing ASTs in the browser during render is too high for enterprise dashboards.
- **Global BEM (Sass/SCSS)**: Rejected. Lacks the type-safety and colocation benefits required by modern React development, inevitably leading to dead code.
- **CSS Modules**: Rejected as the primary global mechanism because it lacks the strict token constraint enforcement provided by typed compiler macros.
