---
doc_meta:
  id: GDC-010
  title: Architecture Review Process
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: internal
  review_cycle_days: 90
  last_reviewed: 2026-05-22
---

# Architecture Review Process

## 1. Context & Scope

This document defines the formal evaluation process, review rubric, and audit procedures used to assess architectural artifacts (PAD, SAD, TDD, ADR, EAD) against the Scnehaux Architecture Documentation Quality Framework. 

While automated CI/CD linter tools enforce structural syntax, this manual process serves as the qualitative **Strategic Oversight & Human Fallback** mechanism. It is conducted by Certified Reviewers and the Architecture Review Board (ARB).

---

## 2. Policy Framework

### 2.1 When the Review Process is Triggered

This manual review process is not required for minor, local documentation fixes. It is **mandatory** under the following conditions:

1. **Architecture Review Board (ARB) Audits**: Evaluating new or significantly modified EADs, PADs, or core SADs.
2. **Waiver Request Reviews**: Reviewing pull requests that request an exception or waiver from an engineering standard.
3. **High-Risk Implementations**: Systems containing core IAM logic, sensitive data (PCI/PII), or significant operational blast radius.
4. **Technology Lifecycle Transitions**: Moving a core technology standard from `Adopted` to `Hold`.

---

### 2.2 Evaluation Rubric & Score Sheet

Reviewers must evaluate the target document against the following 10 parameters. When required, the score sheet must be filled out as a markdown snippet and attached directly to the Pull Request.

| # | Criterion | Enterprise Requirement (10/10 Standard) | Result | Reviewer Notes |
|---|:---|:---|:---|:---|
| 1 | **Clarity & Precision** | Zero ambiguity. Words like "scalable", "fast", or "secure" are banned unless strictly quantified. No motivational filler. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 2 | **Living Scope Boundaries** | System boundaries rigidly defined. For SADs, ensure C4 Level 1/2 topology maps are clear, and prevent implementation encyclopedia leaks. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 3 | **Traceability & Inheritance** | Project-level ADRs/STDs inherit from global standards via the `governed_by` list. SADs map to a governing Platform PAD. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 4 | **Architectural Drivers** | Explicit listing of the functional constraints, business goals, and implicit *Assumptions* driving the design. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 5 | **Measurable NFRs** | Latency (P95/P99), Throughput (RPS), Availability (%), and Error Budgets are documented with concrete targets. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 6 | **Cross-Cutting Concerns** | Strictly addresses Observability (SLIs/SLOs/Tracing) and Security (*Data Classification*, Secrets Management). | [ ] Pass / [ ] Fail / [ ] N/A | |
| 7 | **Trade-Offs** | Documents the *Alternatives Considered* (why other patterns were rejected) and the conscious technical compromises made. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 8 | **Risk & Exception Justification**| Blast Radius and SPOFs are mapped. For active Exception ADRs, a clear `exception_reason` capsule, risk level, and `expiry_date` are mandatory. | [ ] Pass / [ ] Fail / [ ] N/A | |
| 9 | **TDD Lifecycle & Fates** | Ensures the *Ephemeral TDD Matrix* is executed (Class B folded to SAD; Class A archived to `historical/` only if matching strict forensic/incident filters). | [ ] Pass / [ ] Fail / [ ] N/A | |
| 10| **Governance & Namespace Hygiene** | Adheres strictly to structural templates. All files must conform to scalable federated namespaces (e.g. `ADR-SCNX-IAM-GO-SECURITY-003`). | [ ] Pass / [ ] Fail / [ ] N/A | |

---

## 3. Enforcement Mechanism

### 3.1 Scoring & Action Protocols

* **Score Calculation**: Sum the "Pass" counts. Max score is 10. Minimum approval threshold is 9/10.
* **Reject (Score < 9)**: The document fails to meet the minimum threshold and must be revised. It cannot be merged.
* **Approve (Score $\ge$ 9)**: The document is approved as Governance-Grade.
* **Exceptions**: If a criterion is fundamentally "Not Applicable" (N/A) for a specific document type, the reviewer must mark it as Pass but explicitly document the justification in the Reviewer Notes.

---

## 4. Severity & Exceptions

### 4.1 Critical Fail Conditions

A document is immediately **Rejected** regardless of its overall score if it triggers any of the following critical fail conditions:

1. **Security Isolation Breach**: Recommending or leaving open an unmitigated database RLS bypass, unsafe token signing rotation, or encryption violation.
2. **CQRS Boundary Breach**: Recommending patterns where application read queries bypass domain boundary API layers to load database structures directly.
3. **Expired Exception Waivers**: Reference to an Exception ADR that is expired or missing the mandatory `exception_reason` metadata.
4. **Missing Metadata Headers**: Absence of the required YAML frontmatter fields or incorrect sequential ID indexing.
