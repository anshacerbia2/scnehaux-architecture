---
doc_meta:
  id: ADR-UIP-WKS-001
  title: Storybook Component Workshop with Story Tests and Chromatic Visual Review
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-02
  created: 2026-10-01
  created_date: 2026-10-01
  created_by: UI Platform Team
---

# Storybook Component Workshop with Story Tests and Chromatic Visual Review (ADR-UIP-WKS-001)

> **Implementation boundary:** this decision adds a producer-side tool. It never ships in `@scnx/core-ui` or `@scnx/system`, and a story passing in the workshop is not packed-consumer evidence.

---

## 1. Title

Adopt Storybook as the UI Platform component workshop, run every story as a browser test with accessibility checks, and use Chromatic for visual regression review.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                               | Approver                                         |
| ---------- | -------- | ------------ | --------------------------------------- | ------------------------------------------------ |
| 2026-10-01 | proposed | foundational | Pending principal review                | Pending Architecture Review Board (Ansha Cerbia) |
| 2026-10-02 | accepted | foundational | Architecture Review Board (decision D2) | Ansha Cerbia (Architecture Review Board)         |

## 3. Context

The UI Platform has two packages and no place where a person can see and operate a component. Every check so far is automated: unit tests and headless packed-browser fixtures. Reviewers therefore cannot inspect the visual result of a token, CSS-delivery, or theme change before merge.

Three standards already require capabilities that need such a place:

- STD-GLB-FE-008 section 3.5 requires automated visual regression for design-system component libraries and names Chromatic or Percy.
- STD-UIP-STY-001 (Build Pipeline Visual Testing) and STD-UIP-ENG-001 require a visual regression suite for supported component states across the declared theme and browser matrix.
- STD-GLB-FE-008 section 3.6 requires automated accessibility assertions.

Tooling constraints:

- Vitest and Playwright are `adopt` in the Technology Radar; a new tool should reuse them rather than add a third test engine.
- The UI repository keeps no Markdown outside its five TDDs, PLAN, ROADMAP, and navigation READMEs; documentation must not fork into a second site.
- Published packages contain only declared entries (TDD packaging); nothing a workshop needs may enter a tarball.

## 4. Decision Drivers

- A human-operable view of every supported component, state, theme, and mode before merge.
- Story-level browser tests and accessibility checks on the adopted Vitest and Playwright engines.
- Visual regression that satisfies STD-GLB-FE-008 section 3.5 with review and baseline approval.
- Evidence from production design systems, not novelty.
- No effect on published artifacts, consumer CSP, or package boundaries.

## 5. Decision

1. **Workshop:** Storybook 10 with the `@storybook/react-vite` framework is the UI Platform component workshop. Its configuration lives at the UI repository root; stories sit beside the component they render (`*.stories.tsx`).
2. **Faithful rendering:** the workshop preview loads the built `@scnx/system/styles/components.css` and `tokens/css/<theme-id>.css` artifacts, not Sass or Panda source, so it shows what a consumer loads. Every story renders inside the `@scnx/core-ui` ThemeProvider; toolbar controls select each supported theme ID and mode.
3. **Story tests:** `@storybook/addon-vitest` runs every story as a test in Vitest browser mode with Playwright Chromium. `@storybook/addon-a11y` runs axe-core on every story with `parameters.a11y.test: "error"`; a violation fails CI. A story may set `"todo"` only with a recorded reason and owner.
4. **Visual regression:** Chromatic tests every story on each push and blocks merge on unreviewed visual changes (`exitZeroOnChanges: false`). TurboSnap (`onlyChanged: true`) captures only the stories affected by the change and copies the rest from the baseline. Baselines are accepted in Chromatic by the UI Platform owner. Chromatic receives the built static Storybook only: component stories rendered with fixture content, never Product data or secrets.
5. **Boundary:** Storybook, its addons, and Chromatic are development dependencies of the private workspace root. Stories, the Storybook configuration, and the static build never enter a package tarball; the packed-artifact inspector enforces this. Documentation pages use Storybook autodocs from component types and stories; no MDX or Markdown documentation is added.
6. **Hosting:** each CI run uploads the static Storybook build as a workflow artifact. The workshop is not published to a public site by this decision.

## 6. Consequences

### Positive (Pros)

- Reviewers can operate every component state, theme, and mode before merge, locally (`pnpm storybook`) or from the CI artifact.
- Stories become executable browser tests and accessibility checks on the adopted engines.
- STD-GLB-FE-008 section 3.5 visual regression is met with a reviewed baseline workflow.

### Negative (Cons)

- Storybook adds a large development dependency tree and its own upgrade cadence (major versions roughly yearly).
- Chromatic is a third-party SaaS: snapshot counts are metered, and the repository depends on its availability for the visual gate. On the Free plan, "Review and testing will be paused once you use all 5,000 included billed snapshots per month"; a full build captures one snapshot per story and theme-and-mode combination (128 on 2026-10-02). Because the visual review is a required check, a paused account blocks every merge. TurboSnap bills "each copied snapshot at 1/5th the cost of a captured snapshot" and is included in the Free plan ("Equivalent to 25k turbosnaps").
- Story maintenance is ongoing work for every component change.

### Operational

- The `CHROMATIC_PROJECT_TOKEN` repository secret is provisioned by the repository owner. Until it exists, the visual-review job fails visibly rather than passing without a comparison.
- A Chromatic outage blocks the visual gate only; the owner may record a time-bound release exception under GDC-004 rather than skip it silently.

## 7. Compliance Impact

Implements STD-GLB-FE-008 sections 3.5 and 3.6 and the visual-regression rules of STD-UIP-STY-001 and STD-UIP-ENG-001 for the UI Platform. Uses Vitest and Playwright as adopted in the Technology Radar; adds `storybook` and `chromatic` as `trial` entries pending ARB. No waiver is requested. The Chromatic data flow is limited to the static Storybook build described in section 5.

## 8. Alternatives Considered

- **Ladle:** a fast Vite-based story runner using the Component Story Format, but with no first-party test runner, accessibility addon, or visual-review integration; the gate would be assembled by hand.
- **Histoire:** Vue-first, with React support behind it; a weaker fit for a React library.
- **React Cosmos:** a capable fixture explorer, but without the story-test and visual-review ecosystem the standards require.
- **A custom Vite playground:** fully controlled, but every capability above (controls, docs, a11y, story tests, visual review) would be reimplemented and maintained by the platform team.
- **Percy instead of Chromatic:** equally named in STD-GLB-FE-008; Chromatic is chosen for its first-party Storybook integration and TurboSnap. Percy remains a substitute if Chromatic becomes unavailable.
- **Self-hosted Playwright screenshot baselines:** no third-party service, but committed PNG baselines require pinned runners and fonts to avoid flakiness, and offer no review UI.

## 9. References

- Storybook Vitest addon: <https://storybook.js.org/docs/writing-tests/integrations/vitest-addon>
- Storybook accessibility testing: <https://storybook.js.org/docs/writing-tests/accessibility-testing>
- Chromatic GitHub Actions: <https://www.chromatic.com/docs/github-actions/>
- Chromatic billing and TurboSnap (retrieved 2026-10-02): <https://www.chromatic.com/docs/billing/>, <https://www.chromatic.com/docs/turbosnap/>, <https://www.chromatic.com/pricing>
- Production precedent: IBM Carbon React (<https://react.carbondesignsystem.com/>) and Microsoft Fluent UI React (<https://storybooks.fluentui.dev/react/>) publish their component documentation as Storybook.
- npm registry, 2026-10-01: `storybook` and `@storybook/react-vite` 10.6.1, MIT license, React peer range including `^19.0.0`.
