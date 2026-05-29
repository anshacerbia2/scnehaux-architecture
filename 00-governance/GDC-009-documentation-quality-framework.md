---
doc_meta:
  id: GDC-009
  title: Documentation Quality Framework
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 365
  last_reviewed: 2026-05-17
---

# Scnehaux Architecture Documentation Quality Framework

## 1. Context & Scope
This document defines the **Qualitative Evaluation Criteria** for all architectural artifacts. While other documents in the `00-governance` suite define *what* sections must exist or *how* to audit them, this Framework defines *the rigorous benchmark* the content must meet to pass the "Quality Gate" before entering the Scnehaux knowledge base. 

### The `00-governance` Ecosystem (Separation of Concerns)
To prevent overlap and ensure a FAANG-grade modular governance model, the Governance Suite is divided into distinct operational boundaries:
1.  **Documentation Governance Standard (DGS)**: *The Law*. Defines the architectural metamodel (C4/TOGAF/AWS) and the structural Context-Aware Templates (PAD/SAD/TDD/EAD).
2.  **Linting Rules (`linting-rules.yaml` & `linter.py`)**: *The Machine Police*. Automated CI/CD enforcement of the DGS structure and semantic baseline (blocking prohibited words).
3.  **Documentation Quality Framework (DQF) - [THIS DOCUMENT]**: *The Qualitative Standard*. Defines the 10 deep architectural parameters (e.g., Trade-offs, Blast Radius, Quantification) that human reviewers must evaluate.
4.  **Governance Audit Toolkit (GAT)**: *The ARB Process*. Defines the formal procedure, risk registers, and macro-dimensions for Architecture Review Board (ARB) audits.
5.  **Architecture Review Score Sheet**: *The Execution Tool*. The physical markdown table filled out by the Certified Reviewer during a Pull Request, derived directly from the 10 DQF criteria.

## 2. Policy Framework
All architecture documents are evaluated against 10 critical parameters. Each parameter is binary (Pass/Fail). The Score Sheet translates these parameters into actionable checks.

### Scoring Criteria (The 10 Parameters)
1. **Clarity & Precision**: Zero ambiguous wording. Adjectives like `highly scalable` or `fast` are strictly banned unless bound to metrics.
2. **Defined Scope & Living Boundaries**: Clear boundaries of what is included. For SADs, ensure it remains boundary-centric (C4 Level 1/2 topology) and does not leak into an implementation encyclopedia or changelog.
3. **Traceability & Federated Linkage**: Forward and backward linkage to governing PADs/SADs. For project-level ADRs/STDs, ensure explicit `governed_by` inheritance tags are present.
4. **Architectural Drivers**: Explicit functional constraints, business goals, and the implicit *Assumptions* driving the design.
5. **Measurable NFRs**: Quantifiable targets for Latency (P95/P99), Availability (%), Throughput, and Error Budgets.
6. **Cross-Cutting Concerns**: Deep integration of Observability (SLIs/SLOs/Tracing) and Security (*Data Classification*, Secrets Management).
7. **Trade-Offs**: Documents the *Alternatives Considered* (why other patterns were rejected) and the conscious technical compromises made.
8. **Risk & Exception Visibility**: Explicitly lists operational risks, SPOFs, and exact *Blast Radius*. For Exception ADRs, ensure `exception_reason` is dynamically documented and the `expiry_date` is active.
9. **Lifecycle & Deprecation Strategy**: Where APIs, schemas, or TDDs are involved, defines backward compatibility. Ensures the *Ephemeral TDD Fate Matrix* is executed (Class B folded into SAD; Class A archived to `historical/` only if matching strict forensic/incident filters).
10. **Governance & Namespace Hygiene**: Strict adherence to structural templates. Verifies that all files conform to the scalable federated namespace (e.g., `ADR-SCNX-IAM-GO-SECURITY-003` for project files) to prevent global namespace collisions.

### Document-Specific Quality Focus
*   **PAD**: Must clearly define Trust Boundaries, integration contracts, and external actor propagation models.
*   **SAD**: Must clearly define C2 Container Topology, network boundaries, and runtime failure modes.
*   **TDD**: Must clearly define API Contracts and code-level failure/retry boundaries.
*   **Exception ADR**: Must declare a documented `exception_reason` capsule, defined `expiry_date`, and specific risk classification.

## 3. Enforcement Mechanism (The Governance Layers)
In a mature architecture ecosystem, manual checklists are not the primary enforcement engine. We rely on **Policy-as-Code** for absolute consistency, reserving human intellect for strategic judgment.

| Governance Layer | Role | Enforcement |
| :--- | :--- | :--- |
| **Linter / Policy Engine** | Primary Enforcement | Blocks non-compliant docs at the CI/CD level (Semantic/Prohibited Words). |
| **Metadata Validation** | Structural Governance | Enforces Context-Aware Templates (PAD/SAD/TDD) based on ID prefix. |
| **CI/CD Gates** | Mandatory Automation | Prevents PR merges if the Policy Engine throws an `ERROR` or `CRITICAL`. |
| **Manual Score Sheet** | Human Fallback & Exceptions | Used by reviewers to evaluate semantic *quality*, business logic, or manual exceptions (`lint_disable` justification). |
| **ARB Review** | Strategic Oversight | Required for high-risk approvals, strategic EAD/PAD pivots, or formal waiver requests. |

## 4. Severity & Exceptions

### Score Classification
*   **0-5**: Draft / Incomplete -> **Reject** (Rewrite required)
*   **6-8**: Needs Work -> **Revision Required**
*   **9**: Enterprise-Ready -> **Approve** (Standard passing grade)
*   **10**: Governance-Grade -> **Gold Standard**

**Enforcement Rule**: Documents failing to meet the minimum score of **9** must not be marked as Approved, must not be referenced as authoritative, and must not guide production implementation.

**Exceptions**: Temporary scratchpads or documents clearly marked as `status: draft` are exempt from scoring until they are submitted for approval.
