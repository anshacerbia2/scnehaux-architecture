---
doc_meta:
  id: ADR-GLB-FE-007
  title: ADR-GLB-FE-007 Next-Generation Frontend Testing Toolchain
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-007: Transitioning to the Next-Generation Frontend Testing Toolchain

---

## 1. Title

ADR-GLB-FE-007: Transitioning to the Next-Generation Frontend Testing Toolchain

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                     |
| ---------- | -------- | ------------ | ------------------------- | ---------------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Principal Frontend Architect |

## 3. Context

Maintaining testing velocity and reliability is critical. Historically, we relied on Jest for unit testing and Cypress for E2E testing. As the enterprise transitioned to ESM and Vite, Jest's heavy reliance on CommonJS caused severe execution slowdowns. Simultaneously, Cypress's architectural limitations (inability to handle multi-tab flows, cross-origin iframes) have caused high rates of flaky tests and CI timeouts.

## 4. Decision Drivers

Vitest integrates natively with Vite's HMR and compilation pipeline, eliminating Babel transpilation overhead. Playwright's out-of-process architecture natively supports multi-tab testing, cross-origin iframe manipulation, and full browser coverage without memory leaks. MSW allows identical mock definitions to be reused across local development, Vitest, and Playwright.

## 5. Decision

We will standardize our frontend testing ecosystem on a next-generation toolchain: **Playwright** for E2E and Browser Integration, **Vitest** for Unit and Component Integration, and **Mock Service Worker (MSW)** for network mocking across all layers.

## 6. Consequences

- **Positive**: Test execution speeds are drastically improved (up to 5x faster for unit tests), and flaky E2E tests are stabilized due to strict architectural isolation in Playwright.
- **Negative**: Rewriting hundreds of Cypress assertions into Playwright's async/await syntax requires a dedicated migration effort.

### Negative / Risks

- **Migration Delays**: Teams may resist migrating off Cypress due to the sheer volume of legacy test cases.
- **Snapshot Discrepancies**: Legacy Jest snapshot utilities may not have exact parity in Vitest, requiring manual snapshot recreation.

### Operational

- All new repositories must initialize Playwright and Vitest as the default testing runners.
- MSW handlers should be centralized in a shared `mocks/` directory to maximize reusability across test types.

## 7. Compliance Impact

### Related Standards

- [STD-GLB-FE-008 (Testing)](../../../02-standards/_global/frontend/STD-GLB-FE-008-testing.md) - This document dictates the normative rules on how the testing toolchain is implemented in CI/CD.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **Cypress**: Rejected. Its synchronous-like command queue, lack of native cross-tab support, and difficulty handling modern third-party OAuth popups make it insufficient for complex B2B portal integrations.
- **Jest**: Rejected. The heavy startup overhead and poor native ESM support make it incompatible with our high-velocity Vite-based development pipelines.
- **Selenium**: Rejected. Too slow, overly verbose, and lacks the modern developer ergonomics and tracing capabilities provided by Playwright.

