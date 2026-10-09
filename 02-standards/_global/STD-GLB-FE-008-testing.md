---
doc_meta:
  id: STD-GLB-FE-008
  title: Enterprise Frontend Testing & Quality Assurance Standard
  owner: Principal Frontend Architect
  version: 1.2.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-09
---

# Enterprise Frontend Testing & Quality Assurance Standard (STD-GLB-FE-008)

---

## 1. Objective & Scope

This standard defines the mandatory testing strategies, automation frameworks, and quality gates required for all frontend applications and shared component libraries within the Scnehaux enterprise.

It establishes a rigorous, automated testing pyramid designed to ensure application stability, prevent visual regressions, and guarantee accessibility compliance before deployment.

The scope of this standard covers unit testing, component testing, integration testing, end-to-end (E2E) testing, visual regression testing, and accessibility (a11y) audits.

---

## 2. Design Principles

All frontend testing architectures must strictly adhere to the Supreme Frontend Governance principles:

- **Shift-Left Quality**: Quality assurance is an engineering responsibility. Defects must be caught at the lowest possible layer of the testing pyramid.
- **Behavior Over Implementation**: Tests must verify user-facing behavior and domain invariants, not private component state or internal DOM structures. Refactoring internal implementation details must not break tests.
- **Zero Flakiness Tolerance**: Flaky tests destroy CI/CD trust. Tests that fail non-deterministically must be quarantined and repaired immediately.

---

## 3. Normative Rules

### 3.1 The Testing Pyramid

Applications must implement a comprehensive testing strategy adhering to the enterprise testing pyramid:

- **Base (Unit Tests)**: High volume, sub-millisecond execution. Focused on pure domain logic.
- **Middle (Component & Integration Tests)**: Moderate volume. Focused on UI behavior, state transitions, and mocked network boundaries.
- **Top (E2E Tests)**: Low volume, high execution cost. Focused on critical user journeys across real network boundaries.

### 3.2 Unit Testing

- **Engines**: Projects must utilize **Vitest** (or Jest for legacy systems) for unit testing.
- **Scope**: All pure functions, utility modules, custom hooks, business rule engines, and domain state selectors must be fully unit tested.
- **Coverage Mandate**: Critical domain logic, authorization policies, and utility functions must maintain $\ge 90\%$ statement coverage.

### 3.3 Component & Integration Testing

- **Engines**: Projects must utilize **React Testing Library** for component testing.
- **Testing Contract**: Components must be queried by accessible roles (e.g., `getByRole`, `getByLabelText`) rather than CSS selectors or test IDs, enforcing accessibility-first testing.
- **Snapshot Prohibition**: Snapshot testing (capturing serialized DOM output) is prohibited for dynamic UI components due to high false-positive rates and maintenance overhead.
- **Network Boundaries**: Integration tests must mock network responses at the network boundary using **Mock Service Worker (MSW)**. Bypassing network boundaries by directly mocking internal HTTP clients (e.g., mocking `axios`) is discouraged.

### 3.4 End-to-End (E2E) Testing

- **Engines**: **Playwright** is the enterprise standard for E2E testing (Cypress is permitted for legacy projects).
- **Scope**: E2E tests must be strictly limited to critical user journeys (e.g., Login, Checkout, Multi-step Form Submission). Testing exhaustive edge cases via E2E is prohibited; these must be covered by Unit or Integration tests.
- **Environment**: E2E tests must execute against a fully deployed ephemeral preview environment or a local production build.
- **Against the stack (1.1.0)**: A journey that crosses services, such as signing in through the identity kernel's hosted login and acting through a Control API, runs against those services' stacks brought up in CI by a stack-level proof (STD-GLB-009 §Stack-Level Proofs), the ephemeral environment this rule names. The sign-in is the kernel's own pages, typed into as a person types, never a mocked login or a token injected into the browser.
- **Browsers in CI (1.1.0)**: The job installs the browser it runs with Playwright's own command, `playwright install --with-deps chromium`, which installs "the browsers and OS dependencies … with a single command" [R2], and does not cache it: "Caching browser binaries is not recommended, since the amount of time it takes to restore the cache is comparable to the time it takes to download the binaries" [R1]. It runs one worker, as Playwright recommends "to prioritize stability and reproducibility" [R1], and retries nothing: a failure is triaged, never retried away.
- **Chromium alone, unless a journey's design names more.** A stack-level journey proves the services, not the browser engines, and each engine added multiplies its run. A rendering or compatibility concern is tested where §3.5 and the application's own suite place it.
- **The stack's certificate authority is trusted, never ignored.** A stack whose proxy serves TLS from a local authority adds that authority to the browser's trust store; on Linux, Chromium "uses the NSS Shared DB" [R3]. Ignoring certificate errors would take a path no deployment takes.

### 3.5 Visual Regression Testing

- **Engines**: Design System component libraries and core application flows must implement automated visual regression testing (e.g., using **Chromatic** or **Percy**).
- **Scope**: Commits modifying foundational CSS, Tier-1/Tier-2 Design Tokens, or shared primitive components must pass a pixel-level comparison audit before merge.

### 3.6 Accessibility & Performance Testing

- **Automated A11y**: Unit and integration tests must run automated accessibility assertions (e.g., `jest-axe`).
- **Automated A11y in a browser (1.2.0)**: Component tests run axe on a DOM without layout: jsdom does not implement "Layout: the ability to calculate where elements will be visually laid out as a result of CSS" [R5]. Each main page of an application is therefore also scanned in Chromium, served from its built bundle, with `@axe-core/playwright`, the integration Playwright's accessibility guide uses [R4], in CI.
  - The scan fails on any violation of the WCAG 2.0, 2.1 and 2.2 A and AA rules axe implements.
  - What axe cannot decide, such as a colour contrast over a gradient or a translucent panel, is recorded on the test as needing review, never counted as a pass.
  - It is automated evidence only. Playwright: "Note that automated testing cannot detect all types of WCAG violations", and "many accessibility problems can only be discovered through manual testing" [R4]. Keyboard order, focus, zoom, colour contrast and a screen reader stay with the manual audit of STD-GLB-FE-009 §3.5.
- **Performance Budgets**: E2E pipelines must incorporate performance audits (e.g., Lighthouse CI) to assert that Core Web Vitals remain within the budgets defined in [STD-GLB-FE-002 (Performance)](STD-GLB-FE-002-performance.md).

---

## 4. Exceptions

Exceptions are granted exclusively when strict compliance with a normative rule introduces disproportionate technical, accessibility, or business risk.

### Exception to "Snapshot Testing Prohibition" (Rule 3.3)

- **Condition for Deviation**: You are verifying the output of a deterministic configuration generator where the payload is not a DOM tree but a complex data structure (e.g., JSON ASTs, GraphQL schema strings, compiled CSS).
- **Mandatory Alternative**: Snapshot Testing is strictly permitted exclusively for these non-DOM data payloads.

### Exception to "Exploratory Prototyping (Unit/Integration Mandates)" (Rule 3.1 & 3.2)

- **Condition for Deviation**: The project is in a highly exploratory "Spike" phase or Proof of Concept (PoC) architecture where requirements are volatile.
- **Mandatory Alternative**: Automated testing mandates may be waived temporarily. However, the CI/CD pipeline must enforce a hard block preventing the PoC branch from merging into `main` or any production release branch until full test coverage is retrofitted.

### Exception to "Environment Integration" (Rule 3.1 & 3.4)

- **Condition for Deviation**: An external dependency (e.g., a legacy library or heavy WebGL engine) is fundamentally incompatible with headless Node.js DOM emulators (JSDOM/Happy-DOM) and requires a full browser context to evaluate.
- **Mandatory Alternative**: The specific test suite for that module must be shifted up the Testing Pyramid from Integration to the E2E (Playwright) layer where a real browser runtime is guaranteed.

## 5. Enforcement Mechanism

- **CI/CD Quality Gates**: Build pipelines must enforce minimum test coverage thresholds. PRs dropping coverage below the established baseline must be blocked automatically.
- **Quarantine Protocol**: CI pipelines must implement a quarantine mechanism for flaky tests. Tests failing intermittently must be automatically skipped in the main branch to prevent deployment blockages and must generate an immediate high-priority repair ticket.
- **Waiver Protocol**: Deviations from testing standards must be documented in a local project ADR. The Architecture Review Board (ARB) must respond with a review decision within **5 business days** of the ADR submission.

## 6. References

- **[R1]** Playwright, _Continuous Integration_, accessed 2026-10-08. <https://playwright.dev/docs/ci>. "We recommend setting workers to "1" in CI environments to prioritize stability and reproducibility. Running tests sequentially ensures each test gets the full system resources, avoiding potential conflicts"; "Caching browser binaries is not recommended, since the amount of time it takes to restore the cache is comparable to the time it takes to download the binaries. Especially under Linux, operating system dependencies need to be installed, which are not cacheable." Supports §3.4, Browsers in CI.
- **[R2]** Playwright, _Browsers_, "Install system dependencies", accessed 2026-10-08. <https://playwright.dev/docs/browsers>. "You can also install the dependencies for a single browser by passing it as an argument"; "It's also possible to combine `install-deps` with `install` so that the browsers and OS dependencies are installed with a single command": `npx playwright install --with-deps chromium`. Supports §3.4, Browsers in CI.
- **[R3]** Chromium, _Linux Cert Management_, `docs/linux/cert_management.md`, accessed 2026-10-08. <https://chromium.googlesource.com/chromium/src/+/main/docs/linux/cert_management.md>. "On Linux, Chromium uses the NSS Shared DB"; "Since M146, Chromium defaults to $HOME/.local/share/pki/nssdb for the NSS Shared DB. If you still have an existing $HOME/.pki/nssdb database, Chromium will use that instead"; "to trust a root CA certificate for issuing SSL server certificates, use `certutil -d sql:$HOME/.local/share/pki/nssdb -A -t "C,," -n <certificate nickname> -i <certificate filename>`". Supports §3.4, the stack's certificate authority.
- **[R4]** Playwright, _Accessibility testing_, accessed 2026-10-09. <https://playwright.dev/docs/accessibility-testing>. Its examples use the `@axe-core/playwright` package. "Note that automated testing cannot detect all types of WCAG violations"; "many accessibility problems can only be discovered through manual testing"; "We recommend using a combination of automated testing, manual accessibility assessments, and inclusive user testing." Supports §3.6.
- **[R5]** jsdom, _README_, "Unimplemented parts of the web platform", accessed 2026-10-09. <https://github.com/jsdom/jsdom#unimplemented-parts-of-the-web-platform>. "**Layout**: the ability to calculate where elements will be visually laid out as a result of CSS, which impacts methods like `getBoundingClientRects()` or properties like `offsetTop`"; "jsdom has dummy behaviors for some aspects of these features, such as … returning zeros for many layout-related properties." Supports §3.6.
