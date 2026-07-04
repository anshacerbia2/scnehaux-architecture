---
doc_meta:
  id: GDC-003
  title: Architecture Review Process
  owner: Architecture Authority
  version: 1.0.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 90
  last_reviewed: 2026-05-22
---

# Architecture Review Process

## 1. Context & Scope

This document defines the formal evaluation process, review rubric, and audit procedures used to assess architectural artifacts (PAD, SAD, TDD, ADR, EAD) against the Scnehaux Architecture Documentation Quality Framework. 

While automated CI/CD linter tools enforce structural syntax, this manual process serves as the qualitative **Strategic Oversight & Human Fallback** mechanism. It is conducted by Certified Reviewers and the Architecture Review Board (ARB).

---

## 2. Policy Framework

### 2.1 Evaluation Rubric & Score Sheet

Reviewers must evaluate the target document against the following 10 parameters. When required, the score sheet must be filled out as a markdown snippet and attached directly to the Pull Request.

| # | Criterion | Enterprise Requirement (10/10 Standard) | Result | Reviewer Notes |
|---|:---|:---|:---|:---|
| 1 | **Clarity & Precision** | Zero ambiguity. Words like "scalable", "fast", or "secure" are banned unless strictly quantified. No motivational filler. | Pass / Fail / N/A | |
| 2 | **Living Scope Boundaries** | System boundaries rigidly defined. For SADs, ensure C4 Level 1/2 topology maps are clear, and prevent implementation encyclopedia leaks. | Pass / Fail / N/A | |
| 3 | **Traceability & Inheritance** | Project-level ADRs/STDs inherit from global standards via the `governed_by` list. SADs map to a governing Platform PAD. | Pass / Fail / N/A | |
| 4 | **Architectural Drivers** | Explicit listing of functional constraints, business goals, assumptions, and **integration of past Incident/COE learnings**. | Pass / Fail / N/A | |
| 5 | **Measurable NFRs** | Latency (P95/P99), Throughput (RPS), Availability (%), and Error Budgets are documented with concrete targets. | Pass / Fail / N/A | |
| 6 | **Cross-Cutting Concerns** | Strictly addresses Observability (SLIs/SLOs/Tracing) and Security (*Data Classification*, **Zero-Trust boundaries**). | Pass / Fail / N/A | |
| 7 | **Trade-Offs** | Documents the *Alternatives Considered* (why other patterns were rejected) and the conscious technical compromises made. | Pass / Fail / N/A | |
| 8 | **Risk & Graceful Degradation**| Blast Radius and SPOFs are mapped. **Must define how the system degrades gracefully under failure.** | Pass / Fail / N/A | |
| 9 | **TDD Lifecycle & Fates** | Ensures the *Ephemeral TDD Matrix* is executed (Class B folded to SAD; Class A archived to `historical/` only if matching strict forensic/incident filters). | Pass / Fail / N/A | |
| 10| **Governance & Namespace Hygiene** | Adheres strictly to structural templates. All files must conform to scalable federated namespaces (e.g. `ADR-SCNX-IAM-GO-SECURITY-003`). | Pass / Fail / N/A | |

---

### 2.2 High-Risk Pivots (ARB Escalation Triggers)

While the Peer Reviewer executes the rubric above, the Architecture Review Board (ARB) must take over if the PR triggers a high-risk pivot. It is the strict responsibility of the **Peer Reviewer** to identify these conditions and escalate the Pull Request by explicitly tagging the ARB for formal review. ARB escalation is **mandatory** under the following conditions:

| Trigger Type | Description & Hard Thresholds |
|:---|:---|
| **Structural Architecture Audits** | Evaluating brand new, or significantly modified, Enterprise Architecture (EAD), Domain (PAD), or core System (SAD) documents. |
| **Exception & Waiver Requests** | Reviewing Pull Requests that explicitly request an exception or waiver from an established engineering standard. |
| **Security & Compliance Risks** | Modifying architectures containing core IAM logic, sensitive data (PCI/PII/HIPAA), or altering network zero-trust boundaries. |
| **Cross-Domain Coupling** | Introducing a new synchronous hard-dependency between two previously isolated bounded contexts (violating PAD isolation). |
| **Public Contract Breaking** | Introducing backward-incompatible changes to external-facing Public APIs or enterprise-wide event schemas. |
| **Significant Financial Impact** | Architectural changes projected to increase cloud infrastructure or vendor licensing costs by $>20\%$ within the domain. |
| **Vendor Lock-In Decisions** | Integrating a deeply-coupled 3rd-party SaaS or managed service where future migration would require $>3$ months of engineering effort. |
| **Technology Radar Shifts** | Moving a core technology standard from `Adopted` to `Hold` or `Deprecated`. |

---

### 2.3 ARB Strategic Audit Dimensions

While Peer Reviewers enforce the 10 parameters above (Micro/Document Quality), the Architecture Review Board (ARB) evaluates the proposal against **7 Macro Dimensions**. 

> [!IMPORTANT] The Core Philosophy of the ARB Audit
> The ARB does not audit syntax or formatting, it audits **Time and Liability**. Every new framework, database, or architectural pivot introduces technical debt that accelerates system decay. The ultimate essence of an ARB Audit is to serve as the **"Timekeeper of the Architecture"**, ensuring that a decision made today does not degrade a 10-year enterprise architecture into a 5-year legacy burden.

The ARB assumes the document is already structurally perfect before interrogating the following dimensions:

1. **Enterprise Alignment (EAD/STD Compliance)**: 
   - Does this pivot contradict the Enterprise Architecture (EAD)?
   - If requesting a standard waiver, is the justification mathematically sound and fully compliant with the Exception criteria defined in GDC-010?
2. **Systemic Blast Radius & Coupling**: 
   - Does this decision tightly couple two previously decoupled domains (violating PAD boundaries)?
   - If this component fails, does the failure cascade globally?
3. **TCO & Tech Lifecycle (GDC-004)**: 
   - Does this introduce a fragmented technology that Platform Engineering/SRE cannot support? 
   - Does it align with the `Invest` or `Hold` rings of the technology radar?
4. **Enterprise Risk Posture**: 
   - Does this introduce unacceptable security, compliance, or data sovereignty risks (e.g., exposing PII to a lower trust zone)?
5. **Reversibility (One-Way vs. Two-Way Doors)**:
   - Is this an irreversible "One-Way Door" decision (e.g., core database engine, public API contract)? If so, it requires extreme scrutiny.
   - Can we roll back from this decision gracefully if the hypothesis fails?
6. **Build vs. Buy vs. Adopt (Opportunity Cost)**:
   - Are we falling into the "Not Invented Here" syndrome? 
   - Why are we building a custom solution instead of leveraging an existing Enterprise Standard or managed cloud service?
7. **Scalability Ceiling (The 10x Horizon)**:
   - Does this architecture have a known structural upper bound? 
   - At what exact traffic scale (10x, 100x) will this design fundamentally break and require a complete rewrite?

---

## 3. The Git Workflow & Access Control

Because Scnehaux uses a Docs-as-Code ecosystem, the Architecture Review Process is entirely executed via Git Pull Requests. We do not use external ticketing systems for formal document approvals.

### 3.1 Branching Strategy
This repository (`scnehaux-architecture`) follows a simplified Trunk-Based Development model. 
- **The `main` Branch**: The absolute source of truth. It is strictly protected. Direct pushes to `main` are universally blocked.
- **Short-Lived Branches**: All changes must be made on feature branches (e.g., `feature/add-payment-sad` or `update/iam-pad-v1.1`). 
- **No Environment Branches**: Because this is documentation and not executable code, there are no `dev`, `staging`, or `release` branches.

### 3.2 Branch Protection & Merge Rules
Every Pull Request targeting `main` must satisfy the following algorithmic and human gates:

1. **The Machine Gate (GDC-001)**: The CI/CD Linter must return an `Exit 0`. If the linter fails, the Pull Request is hard-blocked.
2. **The Human Gate (Lead Approval)**: Because architecture documentation acts as a binding contract, standard "Peer Review" is insufficient. Every Pull Request must be explicitly approved by the **Lead** of the respective owning team according to the following matrix. **CRITICAL:** This must be enforced via GitHub Branch Protection Rules requiring at least 1 review from a `CODEOWNERS` matched team.

| Document Type | Target Scope | Required Lead Approver (PR Reviewer) |
| :--- | :--- | :--- |
| **GDC** (Governance) | Enterprise Policy | **ARB** (Architecture Review Board) |
| **EAD** (Enterprise) | Enterprise Strategy | **ARB** (Architecture Review Board) |
| **STD** (Standard) | Contextual Policy | **Inherited Lead** (ARB for Global STDs, Domain/System Lead for Local STDs) |
| **PAD** (Platform) | Domain Capability | **Domain Team Lead** |
| **SAD** (Software) | System Solution | **System Team Lead** |
| **TDD** (Technical Design) | Component Blueprint | **Component Team Lead** |
| **ADR** (Decision Record) | Contextual Pivot | **Inherited Lead** (ARB for Global ADRs, Domain/System Lead for Local ADRs) |

3. **The ARB Gate (Two Escalation Paths)**: The Architecture Review Board (ARB) must approve the Pull Request if it reaches their desk via either of these two paths:
   - **Path A (Automated Git Routing)**: The Pull Request modifies globally restricted documents (e.g., GDC, EAD, or ADR). Git will automatically block the merge and assign the ARB via the `CODEOWNERS` file. *Exception for Trivial Changes: If the Pull Request is strictly a typo, formatting, or dead-link fix (a `Patch` version bump), any single ARB member may "Fast-Track" approve the PR in seconds without conducting a formal 7-dimension audit.*
   - **Path B (Human Escalation)**: The Pull Request modifies a standard domain document (PAD/SAD), but its content triggers a "High-Risk Pivot" (see [Section 2.2: High-Risk Pivots (ARB Escalation Triggers)](#22-high-risk-pivots-arb-escalation-triggers)). Because Git cannot read business context, the Peer Reviewer is strictly prohibited from merging and MUST manually escalate the Pull Request by tagging the ARB.
4. **Merge Strategy & Cleanup**: Only `Squash and Merge` is permitted to ensure the `main` branch history remains clean, linear, and readable. Upon a successful merge, the source feature branch MUST be automatically deleted to prevent branch clutter.

### 3.3 Conflict Mitigation Strategy

Merge conflicts in documentation repositories can be highly disruptive. Scnehaux mitigates this risk structurally:

1. **Modular Decentralization**: The architecture is physically decoupled into individual files per system (e.g., `iam.sad.md`, `finance.sad.md`) rather than a monolithic `Architecture.md`.
2. **Domain Ownership**: Engineers primarily edit documents within their specific domain boundaries. Cross-domain concurrent edits are statistically rare.
3. **Short-Lived Branches**: Trunk-based development requires branches to be merged quickly. Holding branches open for extended periods is an anti-pattern.

If a rare collision occurs, standard Git rebasing protocols apply. The later PR must pull the latest `main` and manually resolve the conflict prior to merging.

---

## 4. Enforcement Mechanism

### 4.1 Scoring & Action Protocols

* **Score Calculation**: Sum the "Pass" counts. Max score is 10. Minimum approval threshold is 9/10.
* **Reject (Score < 9)**: The document fails to meet the minimum threshold and must be revised. It cannot be merged.
* **Approve (Score $\ge$ 9)**: The document is approved as Governance-Grade.
* **Exceptions**: If a criterion is fundamentally "Not Applicable" (N/A) for a specific document type, the reviewer must mark it as Pass but explicitly document the justification in the Reviewer Notes.

---

## 5. Severity & Exceptions

### 5.1 Critical Fail Conditions

A document is immediately **Rejected** regardless of its overall score if it triggers any of the following critical fail conditions:

1. **Security Isolation Breach**: Recommending or leaving open an unmitigated database RLS bypass, unsafe token signing rotation, or encryption violation.
2. **CQRS Boundary Breach**: Recommending patterns where application read queries bypass domain boundary API layers to load database structures directly.
3. **Invalid Exception Waivers**: Reference to an Exception ADR that violates the temporal or structural laws established in GDC-010.
4. **Missing Metadata Headers**: Absence of the required YAML frontmatter fields or incorrect sequential ID indexing.

## 6. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this Review Process:

1. **Asynchronous Git PRs vs. Synchronous ARB Meetings**
   - *Why rejected*: Synchronous committee meetings bottleneck engineering velocity and rely on verbal agreements rather than written contracts.
   - *The Trade-Off*: We lose the high-bandwidth face-to-face debate of traditional architecture boards. In exchange, we gain an asynchronous, globally scalable, and fully auditable review process where the Git commit history is the absolute source of truth.
