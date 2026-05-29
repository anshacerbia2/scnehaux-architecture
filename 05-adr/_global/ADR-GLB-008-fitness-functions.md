---
doc_meta:
  id: ADR-GLB-008
  title: ADR-GLB-008 Implementing Automated Architecture Fitness Functions and Exception Waiver Governance
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# ADR-GLB-008: Implementing Automated Architecture Fitness Functions and Exception Waiver Governance

---

## 1. Title
Automating Architectural Integrity via CI-Driven Fitness Functions and Standardizing the Exception Waiver Process

## 2. Status
Accepted

## 3. Context
Enforcing enterprise architecture standards manually through human code reviews is prone to errors, subjective interpretations, and operational bottlenecks. Over time, codebases suffer from architectural decay, including dependency boundary violations (e.g. UI layers importing database models), hardcoded styling variables instead of design tokens, and accidental logs containing sensitive PII data. Additionally, when valid project constraints require deviating from global standards, teams often implement silent workarounds without documenting the rationale or setting migration timelines. We need automated enforcement mechanisms paired with a structured, auditable waiver process.

## 4. Decision
We officially establish CI-driven automated Architecture Fitness Functions and a formalized Exception Waiver workflow:
1.  **Automated Fitness Functions**: Code integration pipelines must execute blocking validation checks:
    - *PII Scanning (Semgrep)*: Blocks logs attempting to output variables carrying sensitive suffixes.
    - *Dependency Boundaries (Dependency Cruiser)*: Validates directory imports, blocking cross-feature and layer-bypass imports.
    - *Policy-as-Code (OPA)*: Validates Terraform configurations and Kubernetes manifests.
    - *AST Styling Scanners*: Blocks styles containing hardcoded color values or non-tokenized z-index declarations.
2.  **Gate Blocking Status**: All fitness functions operate in blocking mode. Warnings are allowed in local development, but CI pipeline failures block pull request merging.
3.  **Formal Exception Waiver Process**: Teams requiring deviations must submit a dedicated local ADR detailing the context, mitigation, and target migration date.
4.  **Time-Bound Waiver Approvals**: Waivers must carry an expiration date not exceeding `365 days` and require approval from the designated authority (Principal Architect or ARB).

## 5. Rationale
Automating enforcement via fitness functions prevents architectural decay early in the development lifecycle. Blocking PR merges guarantees compliance without relying on manual checks. The Exception Waiver workflow provides a safe, documented path for necessary deviations, ensuring that technical debt is acknowledged, approved, and tracked with a clear remediation path.

## 6. Alternatives Considered

### Alternative A: Post-Merge Architecture Audits
*   **Pros**: Zero impact on developer commit times or PR build durations.
*   **Cons**: Drift is discovered weeks or months after code merges, making remediation costly and resource-intensive.
*   **Why Rejected**: Fails to prevent architectural decay, shifting the burden of compliance checks to late audit cycles.

### Alternative B: Non-Blocking Warnings
*   **Pros**: Informs developers of violations without blocking deployment pipelines.
*   **Cons**: Warning fatigue leads to developers ignoring alerts, resulting in accumulation of style and boundary violations.
*   **Why Rejected**: Fails to guarantee compliance, as teams prioritize feature delivery over warning cleanup.

## 7. Consequences

### Positive
- **Instant Compliance Feedback**: Developers identify and resolve standard violations before merging code.
- **Zero Silent Drift**: The architecture remains consistent across all repositories.
- **Auditable Technical Debt**: Bypasses are documented, approved, and tracked in a centralized register.

### Negative
- **Build Duration Overhead**: Executing scanners increases CI pipeline run times.
- **Initial Friction**: Developers must resolve lint and boundary violations to complete builds.

### Tradeoffs
- We trade slight developer friction and pipeline execution duration for long-term codebase consistency, security compliance, and zero structural drift.

### Operational Impact
- Requires maintaining linter rule sets and scanning tools. Pipeline metrics are analyzed to ensure compliance checks do not exceed `300 seconds` (5 minutes).

### Security Impact
- Enhances security by preventing PII leaks in logging channels and stopping un-encrypted cloud resources from being provisioned.

### Scalability Impact
- Ensures codebases remain modular and decoupled, facilitating maintenance and scaling as teams grow.

## 8. Risks
- **Overly Strict Rule Sets**: Rules that block legitimate work can lead to developer frustration or workaround attempts.
  - *Mitigation*: Teams can request exceptions through the waiver process, and rules are updated quarterly based on project feedback.

## 9. Implementation Notes
- Codified in the Architecture Fitness Functions Standard (`STD-E020`) and the ADR Governance Standard (`STD-E019`).
- Custom AST scanners parse code styles to enforce HSL/OKLCH token validation.

## 10. Related Documents
- [Enterprise Architecture Fitness Functions Standard (STD-E020)](file:///d:/Ansha/architecture-description/scnehaux-architecture/05-standards/STD-E020-architecture-fitness-functions-standard.md)
- [Enterprise Architecture Decision Record Governance Standard (STD-E019)](file:///d:/Ansha/architecture-description/scnehaux-architecture/05-standards/STD-E019-architecture-decision-record-governance-standard.md)
- [Enterprise-wide Adoption of the Context-Aware Documentation Governance Standard (ADR-E000)](file:///d:/Ansha/architecture-description/scnehaux-architecture/04-decisions/ADR-E000-architectural-governance-taxonomy.md)
