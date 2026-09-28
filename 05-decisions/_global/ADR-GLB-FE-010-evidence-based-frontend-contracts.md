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
  authorizes: [STD-GLB-FE-001, STD-GLB-FE-002, STD-GLB-FE-005, STD-GLB-FE-006, STD-GLB-FE-007, STD-GLB-FE-009]
---

# ADR-GLB-FE-010: Evidence-Based Frontend Contracts and UI Platform Alignment

## 1. Title

Authorize the version 2.0.0 revisions of six global frontend standards, rule by rule.

## 2. Status

| Date       | Status   | ADR Type            | Reviewers                                                                          | Approver                            |
| ---------- | -------- | ------------------- | ---------------------------------------------------------------------------------- | ----------------------------------- |
| 2026-09-28 | proposed | conflict_resolution | Principal review: approve with required changes; consolidated verification pending | Architecture Review Board — pending |

## 3. Context

The approved frontend documents at commit `b70f519` contain mutually exclusive rules:

- ADR-GLB-FE-006 mandates Panda CSS or Vanilla Extract and rejects Sass, while the UI Platform produces Sass component rules and Panda recipes.
- STD-GLB-FE-005 defines a six-layer order and document-root themes, while the UI Platform needs a named recipe layer and multiple scoped brands in one DOM.
- STD-GLB-FE-006 mandates broad manual memoization, while STD-GLB-FE-002 requires profiling and identity evidence.
- ADR-GLB-FE-002 requires Rsbuild for every federated application, and ADR-GLB-FE-004 binds Module Federation to Webpack or Rsbuild, while the federated applications compile with Rspack directly.
- STD-GLB-FE-009 applies one contrast ratio to text and non-text UI, although WCAG 2.2 separates SC 1.4.3 and SC 1.4.11.
- STD-GLB-FE-001 prohibits every hardcoded presentation value, while token governance permits reviewed structural values.

These standards and ADRs govern every frontend, including the approved Experience systems SAD-002, SAD-012, SAD-014, and SAD-015. Their production status is not recorded in this repository. GDC-010 section 2.4.2 therefore requires the three conflicting ADRs to be replaced rather than edited in place: ADR-GLB-FE-011, ADR-GLB-FE-012, and ADR-GLB-FE-013 replace ADR-GLB-FE-002, ADR-GLB-FE-004, and ADR-GLB-FE-006 on ratification. GDC-007 section 2.4.2 requires this ADR to authorize the major standard revisions.

## 4. Decision Drivers

- One coherent rule set across global frontend and UI Platform documents.
- No security or correctness rule removed without a recorded reason.
- Measurable package, page, and application contracts.
- Accessible behavior defined by widget and page responsibility.
- Bundler and vendor choices that evolve behind stable public contracts.

## 5. Decision

**Proposed pending ARB approval.** This ADR authorizes the version 2.0.0 revisions of STD-GLB-FE-001, STD-GLB-FE-002, STD-GLB-FE-005, STD-GLB-FE-006, STD-GLB-FE-007, and STD-GLB-FE-009 exactly as listed in the rule delta below. Each standard names this ADR in `authorized_by`; this ADR names each standard in `authorizes`. A change to a standard that is not in the delta needs a revision of this ADR before ratification.

The coherent frontend contract is:

1. Governed shared visual decisions use semantic tokens. Reviewed structural literals remain valid where a token would misrepresent intent.
2. Performance requirements identify the scenario, environment, tool, representation, baseline, and threshold; user-facing pages meet the Core Web Vitals "good" thresholds at the 75th percentile.
3. The canonical cascade order is `reset, tokens, base, components, recipes, utilities, overrides`.
4. Public multi-brand themes use scoped `[data-scnx-theme]` roots; portals stay inside their originating scope.
5. Shared UI styling produces static CSS (ADR-GLB-FE-013).
6. Module Federation follows the runtime contract in ADR-GLB-FE-012, compiled with the toolchain in ADR-GLB-FE-011.
7. WCAG 2.2 SC 1.4.3 governs text contrast and SC 1.4.11 governs non-text contrast; focus indicators are outlines.
8. The React security baseline is derived from advisories against the resolved dependency graph, not fixed in a standard.

### 5.1 Rule delta

Status values: **Retained** (same obligation), **Restored** (dropped in the first review draft, now back), **Changed** (obligation altered), **Moved** (obligation now lives elsewhere), **Removed** (obligation withdrawn), **Added** (new obligation). Rules marked ▲ are new or stricter obligations for product teams.

**STD-GLB-FE-001 (Tech Stack)**

| Baseline rule                                                                                                  | Status   | Result and reason                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| React 19+ as the UI framework                                                                                  | Retained | Security floor moved to STD-GLB-FE-006 §3.10                                                                                                  |
| TypeScript with strict compilers                                                                               | Retained | Compiler flags enforced by STD-GLB-FE-006 §5                                                                                                  |
| TanStack Query for server state; Zustand for client-global state                                               | Retained | Unchanged                                                                                                                                     |
| CSS Modules mandatory for the core component library                                                           | Changed  | Applications may use CSS Modules or Tailwind; the UI Platform emits static CSS under ADR-GLB-FE-013                                           |
| Radix UI mandatory for interactive primitives                                                                  | Changed  | Shared widgets meet a tested behavior contract; a headless foundation may sit behind the platform API after a recorded decision (UIP-DEC-001) |
| Domain layer decoupled and pure; layered architecture                                                          | Retained | Unchanged                                                                                                                                     |
| All hardcoded values prohibited in components                                                                  | Changed  | Governed visual decisions use semantic tokens; structural literals allowed (STD-GLB-FE-005 §3.2)                                              |
| No global selectors inside component styles                                                                    | Retained | Unchanged                                                                                                                                     |
| Interactive elements keyboard navigable with ARIA                                                              | Changed  | Per widget pattern; complete-page conformance stays with the consumer                                                                         |
| Server-state mirroring prohibited; optimistic rollback; HTTP interceptors; route guards; dependency boundaries | Retained | Unchanged                                                                                                                                     |
| V-Sync schedulers bypass the framework for all motion                                                          | Changed  | Measured scheduling for high-frequency paths                                                                                                  |
| Visual token scanner blocks all HEX/RGB/HSL literals                                                           | Changed  | Blocks color literals in shared and product styles; documented adapters and data-visualization palettes are reported, not blocked             |
| —                                                                                                              | Added ▲  | Dependency security audit (STD-GLB-FE-006 §3.10)                                                                                              |

**STD-GLB-FE-002 (Performance)**

| Baseline rule                                                                     | Status     | Result and reason                                                                                                         |
| --------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------- |
| Synchronous geometry reads prohibited ("zero layout thrashing", 60 FPS guarantee) | Changed    | Measured reads allowed when behavior requires them; interleaving avoided in high-frequency paths; no frame-rate guarantee |
| Observer-first layout checks                                                      | Changed    | Used when the observation semantics fit                                                                                   |
| Zero inner-scope allocations in render                                            | Removed    | Not measurable as a release rule; memoization conditions live in STD-GLB-FE-006 §3.2                                      |
| All DOM writes batched through `requestAnimationFrame`                            | Changed    | Batched when traces show interleaving or missed frames                                                                    |
| Listener, timer, and observer cleanup                                             | Retained   | Unchanged                                                                                                                 |
| Static values hoisted; non-primitive derived values memoized                      | Changed    | Required when identity or measurement makes it material                                                                   |
| Dynamic `as` primary; `asChild` restricted                                        | Moved      | UIP-DEC-004 and STD-UIP-PRM-001                                                                                           |
| Components bind to Tier-1 or Tier-2 tokens                                        | Changed    | Tier-2 or Tier-3 only; Tier-1 is a compiler input                                                                         |
| Style encapsulation through CSS Modules                                           | Changed    | Documented root or namespace; CSS Modules are one technique                                                               |
| Lighthouse score gate                                                             | Removed    | A lab score is not a page contract; replaced by Core Web Vitals                                                           |
| Core Web Vitals CI failure                                                        | Restored ▲ | LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile of field data, lab profile when no field data exists          |
| 50 KB shared-library budget; build fails above 5%                                 | Changed    | Budgets name the import scenario, representation, tool, baseline, and threshold                                           |
| Review of listener cleanup and element cloning                                    | Retained   | Unchanged                                                                                                                 |

**STD-GLB-FE-005 (Styling)**

| Baseline rule                                                                                                 | Status    | Result and reason                                                                                                     |
| ------------------------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------- |
| Zero-runtime tools (Panda CSS, Vanilla Extract) recommended; colocated macros                                 | Changed   | Any tool that produces static CSS (ADR-GLB-FE-013)                                                                    |
| Runtime style injection prohibited                                                                            | Changed ▲ | Prohibited for the UI Platform and new applications; an existing application records a migration plan                 |
| No hardcoded colors, spacing, or font sizes                                                                   | Changed   | Semantic tokens for governed decisions; structural literals allowed; color literals still prohibited in shared styles |
| Inline styles only for runtime-computed values                                                                | Restored  | §3.2                                                                                                                  |
| Tailwind classes map to tokens; no arbitrary values                                                           | Retained  | Token-bound utilities (§3.1)                                                                                          |
| CSS Modules preferred; module naming                                                                          | Changed   | One option among static approaches                                                                                    |
| `scnx-` prefix; `scnx-<app>-` global namespace                                                                | Restored  | §3.3                                                                                                                  |
| ITCSS directory guidance; colocation guidance                                                                 | Removed   | Non-normative organization advice                                                                                     |
| Exact six-layer order; no extra layers                                                                        | Changed ▲ | Seven layers including `recipes` for applications that consume UI Platform CSS; others may omit unused layers         |
| `!important` policy                                                                                           | Retained  | §3.4                                                                                                                  |
| Container queries, mobile-first, fluid grids                                                                  | Changed   | §3.6, including the 320 CSS px reflow scenario                                                                        |
| No ID selectors; specificity ≤ `0,4,0`; no type-qualified classes; ≤ 3 compound selectors; ≤ 2 nesting levels | Restored  | §3.3, enforced by Stylelint                                                                                           |
| CSS runtime monitoring in production                                                                          | Changed   | Runtime evidence names the interaction (§3.7)                                                                         |
| No layout thrashing in CSS-driven measurement                                                                 | Moved     | STD-GLB-FE-002                                                                                                        |
| Ad-hoc custom properties prohibited                                                                           | Restored  | §3.2                                                                                                                  |
| Token ownership by the Token Review Board                                                                     | Changed   | Token Lead role in the UI Platform SOT                                                                                |
| Theme switching on `<html>`                                                                                   | Changed   | Scoped `[data-scnx-theme]` roots (§3.3)                                                                               |
| Semantic z-index tokens; integer z-index prohibited                                                           | Restored  | §3.2                                                                                                                  |
| Prefer transform and opacity; tokenized easing                                                                | Changed   | Dimension animation allowed with interruption, timeout, and trace evidence (§3.8)                                     |
| Third-party widgets isolated with Shadow DOM or `all: initial`                                                | Changed   | Isolated adapter with documented inputs (§4)                                                                          |
| Stylelint and AST checks                                                                                      | Retained  | §5                                                                                                                    |
| Visual regression for core system changes                                                                     | Moved     | STD-UIP-STY-001                                                                                                       |
| —                                                                                                             | Added ▲   | Focus indicators drawn with `outline`; forced-colors fixture (§3.9)                                                   |

**STD-GLB-FE-006 (React)**

| Baseline rule                                                             | Status              | Result and reason                                                                                                                    |
| ------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| React 19.2.4 or higher, citing CVEs                                       | Changed ▲           | Advisory-driven audit of the resolved graph, `react-server-dom-*`, and framework advisories; high or critical blocks release (§3.10) |
| "Supreme Frontend Governance" principles                                  | Removed             | Rhetoric; replaced by measurable principles                                                                                          |
| Cyclomatic complexity target of 10; utility and hook extraction           | Removed             | Unenforced organization guidance                                                                                                     |
| Pure renders; no side effects in render                                   | Retained            | §3.1, §3.4                                                                                                                           |
| Composition, compound components, ref forwarding                          | Retained            | §3.6                                                                                                                                 |
| File and identifier naming conventions                                    | Restored            | §5 lint                                                                                                                              |
| Single source of truth; derived state computed                            | Retained            | §3.1                                                                                                                                 |
| `useMemo`/`useCallback` mandatory without the compiler                    | Changed             | Condition-based (§3.2)                                                                                                               |
| Context boundaries and splitting; state colocation                        | Retained            | §3.3, §3.1                                                                                                                           |
| Normalized data graphs; state machines for critical flows                 | Removed             | Modelling choices recorded in each system's TDD                                                                                      |
| Orthogonal state machine for transitions                                  | Changed             | Completion event, bounded timeout, interruption, reduced motion (§3.7)                                                               |
| `useEffect` only for external synchronization; cleanup; `AbortController` | Retained            | §3.4                                                                                                                                 |
| Complete dependency arrays; no undocumented suppression                   | Restored            | §5 lint with same-line reason                                                                                                        |
| Hooks never called conditionally                                          | Retained            | Rules-of-hooks lint (§5)                                                                                                             |
| Expensive-computation thresholds (> 1 ms, ≥ 100 DOM nodes, > 8 levels)    | Removed             | Universal numbers without a scenario (§3.9)                                                                                          |
| Stable, domain-derived list keys                                          | Restored            | §3.6                                                                                                                                 |
| Virtualization thresholds; `useTransition` mandate                        | Changed             | Named-scenario evidence (§3.7, §3.9)                                                                                                 |
| No `any` in props; native attribute inheritance; discriminated unions     | Restored / Retained | §3.6                                                                                                                                 |
| UI primitives accept only leaf props                                      | Changed             | STD-UIP-PRM-001 property contract                                                                                                    |
| Error boundaries with reset and telemetry                                 | Retained            | §3.8                                                                                                                                 |
| RSC or streaming SSR adoption requires a decision                         | Restored            | §3.5                                                                                                                                 |
| SSR determinism; no browser globals in render; `useId` for shared IDs     | Retained / Restored | §3.5                                                                                                                                 |
| Uncontrolled forms and React 19 form actions mandated                     | Removed             | Implementation choice; state ownership (§3.1) applies                                                                                |
| Profiler limit of 3 unnecessary renders; 16 ms RUM limit                  | Removed             | Universal numbers without a scenario                                                                                                 |
| `<React.StrictMode>` in development                                       | Restored            | §5                                                                                                                                   |
| ESLint react, hooks, and jsx-a11y suites                                  | Restored            | §5                                                                                                                                   |
| `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`        | Restored            | §5                                                                                                                                   |

**STD-GLB-FE-007 (Micro-Frontend)**

| Baseline rule                                               | Status              | Result and reason                                                   |
| ----------------------------------------------------------- | ------------------- | ------------------------------------------------------------------- |
| Standalone SPA by default; federation only when justified   | Changed             | Adoption gate recorded in the SAD (§3.1)                            |
| Remotes decoupled; no shared business logic                 | Retained            | Principle 4                                                         |
| Dynamic imports; failures contained at route boundaries     | Retained            | §3.2                                                                |
| Remotes export route configuration arrays                   | Changed             | Routes or mount contracts through a versioned interface             |
| `react`, `react-dom`, `@tanstack/react-query` as singletons | Restored            | §3.3, plus explicit keys for every context-bearing entry            |
| Remotes on the host's React major                           | Changed             | Strict compatible range and controlled failure (ADR-GLB-FE-012)     |
| No global prototype or `window` pollution                   | Retained            | §3.4                                                                |
| Communication only through a typed event bus                | Changed             | Typed contracts: host context, custom events, or a contract package |
| Tokens shared through `HttpOnly` cookies                    | Moved               | Approved browser/BFF security model (STD-GLB-FE-003)                |
| Logout propagated across tabs and remotes                   | Restored ▲          | Origin-checked channel; verified by the host fixture (§3.5)         |
| Remote SemVer metadata checked by the host                  | Retained            | §3.2                                                                |
| Remote budgets 20 KB / 150 KB / 100 KB gzipped              | Changed             | Scenario-defined budgets (§3.7)                                     |
| Isolated document boundary for legacy remotes               | Retained            | §4                                                                  |
| Configuration audits; duplicate runtime detection           | Retained / Restored | §5 and §3.6 telemetry                                               |

**STD-GLB-FE-009 (Accessibility and i18n)**

| Baseline rule                                                               | Status   | Result and reason                                                                                    |
| --------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------- |
| WCAG 2.2 AA for user-facing interfaces                                      | Retained | Evaluated per complete page or flow (§3.1)                                                           |
| WCAG AAA aspirational                                                       | Removed  | Non-normative                                                                                        |
| Native elements first; no ARIA misuse; live regions                         | Retained | §3.2                                                                                                 |
| `:focus-visible` indicators; `outline: none` without replacement prohibited | Changed  | Outline-based indicator, SC 2.4.7 and SC 2.4.11, forced-colors fixture                               |
| All overlays trap focus                                                     | Changed  | Modal overlays contain focus; non-modal overlays do not                                              |
| Focus returns to the trigger                                                | Retained | §3.2                                                                                                 |
| Hidden labels; decorative images                                            | Retained | §3.2                                                                                                 |
| Reduced motion; forced colors                                               | Retained | §3.4                                                                                                 |
| 4.5:1 for text and interactive elements                                     | Changed  | SC 1.4.3 for text (4.5:1, large 3:1); SC 1.4.11 for non-text (3:1)                                   |
| No hardcoded strings; ICU MessageFormat; `Intl`                             | Retained | §3.6                                                                                                 |
| Logical properties and RTL                                                  | Retained | §3.6                                                                                                 |
| Exceptions for complex widgets and dense grids                              | Retained | §4                                                                                                   |
| New automated violations block the pull request                             | Restored | §5                                                                                                   |
| Missing translation keys fail the build                                     | Restored | §5                                                                                                   |
| —                                                                           | Added ▲  | Manual NVDA and VoiceOver evidence for stable composite widgets, including product-built ones (§3.5) |

**Replaced decisions**

| Baseline decision                                                               | Status                   | Result                                                                                                            |
| ------------------------------------------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| ADR-GLB-FE-002: Rsbuild required for federated applications; Webpack prohibited | Replaced on ratification | ADR-GLB-FE-011: Rspack-based toolchain (Rsbuild or `@rspack/core`); Webpack still prohibited for new repositories |
| ADR-GLB-FE-004: Module Federation on Webpack or Rsbuild                         | Replaced on ratification | ADR-GLB-FE-012: runtime contract for shared identity, version negotiation, and failure                            |
| ADR-GLB-FE-006: Panda CSS or Vanilla Extract mandated; Sass rejected            | Replaced on ratification | ADR-GLB-FE-013: static CSS output; bounded Sass and Panda for the UI Platform                                     |

## 6. Consequences

- **Positive:** global and UI standards form one enforceable contract, and every withdrawn rule has a recorded reason.
- **Negative:** host and remote fixtures, packed consumers, browser measurements, and accessibility evidence add maintenance cost.
- **Operational:** the proposed standards and the replacement ADRs have no authority until the ARB approves them; the ratification commit changes their statuses together.
- **Operational:** rules marked ▲ need migration notes for established product teams before ratification takes effect.

## 7. Compliance Impact

Authorized standards: STD-GLB-FE-001, STD-GLB-FE-002, STD-GLB-FE-005, STD-GLB-FE-006, STD-GLB-FE-007, and STD-GLB-FE-009. Replacement decisions: ADR-GLB-FE-011, ADR-GLB-FE-012, and ADR-GLB-FE-013. Related UI authority: ADR-UIP-PLT-001, PAD-PLT-003, and SAD-003. No waiver is requested.

## 8. Alternatives Considered

- Preserve the conflicting documents and choose locally: rejected because two active mandates cannot both be enforced.
- Edit ADR-GLB-FE-002, -004, and -006 in place: rejected because the production status of the systems they govern cannot be established.
- Mandate one vendor or bundler globally: rejected because consumer behavior and protocol compatibility are the durable contracts.
- Keep absolute budgets without measurement definitions: rejected because such claims are not reproducible.
