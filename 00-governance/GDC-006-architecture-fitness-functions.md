---
doc_meta:
  id: GDC-006
  title: Architecture Fitness Functions Guideline
  owner: Principal Software Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Architecture Fitness Functions Guideline

## 1. Context & Scope

This guideline defines the mandatory automated verification rules, continuous integration (CI) gates, static analysis configurations, and infrastructure policy scanners used to enforce architectural integrity across the Scnehaux enterprise ecosystem.

It establishes automated "fitness functions" that run on every code integration to verify compliance with engineering standards, preventing architectural decay.

---

## 2. Policy Framework

### 2.1 Automated Static Code Scanning (Semgrep & CodeQL)

All repositories must execute static code scanning within their pull request pipelines to prevent security vulnerabilities and architectural violations:

- **PII Leak Detection (Semgrep)**:
  - Custom Semgrep rules must scan all logging commands (`logger.Info`, `logger.Error`, `console.log`) to identify and block the output of variables carrying sensitive suffixes (e.g. `*_password`, `*_token`, `*_email`, `*_phone`, `*_ssn`).
  - Semgrep rule compilation:
    ```yaml
    rules:
      - id: detect-pii-in-logs
        pattern: |
          $LOGGER.$METHOD(..., $VAR, ...)
        metavariable-regex:
          metavariable: $VAR
          regex: '(?i)(password|token|email|phone|ssn|creditcard)'
        message: "PII leak detected in logging operation."
        severity: ERROR
    ```
- **Semantic Code Quality (CodeQL)**:
  - CodeQL databases must compile during the build phase. The pipeline must reject compile requests containing high-severity findings, including SQL injections, cross-site scripting (XSS), and insecure cryptographic algorithms.

---

### 2.2 Dependency & Boundary Invariants (Dependency Cruiser)

To enforce clean directory architecture layers:

- **Cruiser Boundary Rules**: Node.js and TypeScript repositories must maintain a `dependency-cruiser.js` configuration in their root directories.
- **Layer Validation**: The configuration must declare rules blocking:
  - *Layer Bypass*: UI components (`/components`) importing domain databases or API data models directly.
  - *Cross-Feature Coupling*: Component packages importing private internal modules from another feature boundary (e.g., `/features/payroll` importing from `/features/attendance/internals`).
- **Pipeline Execution**: The command `depcruise --config .dependency-cruiser.js src` must run on every pull request. The build must fail if any dependency boundary violation is reported.

---

### 2.3 Policy-as-Code Gates (Open Policy Agent)

Infrastructure-as-Code (IaC) templates and deployment definitions must be validated for compliance before resources are provisioned:

- **Terraform / CloudFormation Scans (OPA Conftest)**:
  - OPA policies (written in Rego) must parse Terraform plan files (serialized in JSON).
  - The build must reject configurations that:
    - Instantiate un-encrypted databases or S3 buckets.
    - Expose network ingress ports (`0.0.0.0/0`) on non-gateway security groups.
    - Lack mandatory billing and classification tags (`owner`, `domain`, `classification`).
- **Kubernetes Namespace Baseline**:
  - Rego policies must verify that Kubernetes manifests contain limits on memory and CPU requests, specify non-root user execution, and disable privilege escalation.

---

### 2.4 Custom Abstract Syntax Tree (AST) Styling Parsers

To maintain styling system isolation and enforce the use of design tokens:

- **AST Scanner Execution**: A pre-commit and CI scanner must parse all styling files (CSS, SCSS, LESS) and TSX files containing inline styles.
- **Rules Scanned**:
  - *Hardcoded Color Properties*: Direct color declarations using HEX (`#ffffff`), RGB (`rgb(255, 255, 255)`), or HSL (`hsl(0, 0%, 100%)`) coordinates are prohibited. Styling files must resolve colors exclusively via the custom HSL/OKLCH token variables defined in the design system (e.g., `var(--ds-color-bg-primary)`).
  - *Z-Index Hardcoding*: Elements requiring z-index properties must reference the system z-index tokens (e.g., `var(--ds-z-index-modal)`).
- **Scanner Verification**: The scanner script must fail the build if it detects any CSS property containing hardcoded visual literals.

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Gate Blocking Status**: Fitness functions must operate in blocking mode. Warnings are permitted during local development, but any failure in the CI pipeline blocks merging the pull request.
2. **Metrics Collection**: Execution durations and failure statistics of fitness functions must be reported to the platform team. Any check requiring more than `300 seconds` (5 minutes) to complete must undergo optimization to preserve developer velocity.
3. **Exception Waivers**: Temporary bypasses of fitness functions require an approved, time-bound ADR signed by the Architecture Review Board.

## 4. Severity & Exceptions

### 4.1 Exception Waiver Rules
- Temporary bypasses of fitness functions require an approved, time-bound ADR signed by the Architecture Review Board (ARB).
- Approved waivers have a maximum validity of 365 days.
