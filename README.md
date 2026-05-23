# Scnehaux Architecture

This repository is the authoritative architectural baseline for all systems under the Scnehaux Foundation with **EA (Enterprise Architecture) standards**.

It defines architectural principles, governance rules, shared platform foundations,
system-level architecture requirements, architectural decisions, and engineering standards.

All systems MUST align with the policies and constraints defined in this repository.

---

## Purpose

The purpose of this repository is to:

- Establish architectural consistency across systems
- Enforce production-grade engineering discipline
- Provide traceability for architectural decisions
- Define measurable non-functional expectations
- Govern architectural evolution

This repository contains architecture artifacts only.
It does not contain implementation code.

---

## Architectural Methodology (The "Hybrid" Metamodel)

This repository uses a specific combination of frameworks to ensure scalability and clarity.

### The C4 Model Enforcement (Governance Boundary)

We strictly enforce the **C4 Model** to define the boundaries of this repository.

| Level | C4 Name | Scnehaux Scope | Location |
| :--- | :--- | :--- | :--- |
| **C1** | **Context** | **EAD** (Enterprise) / **GDC** (Vision) | Root Repo (`01-enterprise`) |
| **C2** | **Container** | **PAD** (Domain) & **SAD** (System) | Root Repo (`02-platform`, `03-applications`) |
| **C3** | **Component** | **TDD** (Detailed Design) | **Specific Project Repository** |
| **C4** | **Code** | Implementation & Source | **Specific Project Repository** |

> [!IMPORTANT]
> This repository is a **C1/C2 Governance Hub**. We do not document internal components (C3) or source code (C4) here. Level C3/C4 documentation must reside alongside the code in the specific project repository to ensure "Docs-as-Code" synchronization.

### Meta & Cross-Cutting Layers
- **ADR** (Architecture Decision Records) and **STD** (Standard Documents) are **Meta Layers**.
- They are **Cross-Cutting**: they define the rules and rationale that bind all C1-C4 levels together.

---

## Document Types (Glossary of Truth)

To ensure absolute consistency and prevent documentation bloat, we explicitly reject monolithic templates (like arc42's "Standard-16"). All technical documents MUST follow our **Context-Aware Templates** enforced by the CI/CD Linter:

| Code | Full Name | Audience & Purpose |
| :--- | :--- | :--- |
| **PRD** | Product Requirements Document | Business "What" and "Why" (Non-technical). Not part of Scnehaux Architecture. |
| **GDC (Vision)** | Global Design Concept | **[DEPRECATED]** High-Level Vision (C1). Integrated into the **System Context & Business Drivers** of **PAD/SAD** documents. |
| **GDC (Gov)** | Governance Document Contract | **ARB & Principal Engineers.** Automated policy definitions, quality gates, and compliance enforcement (`00-governance`). |
| **EAD** | Enterprise Architecture Document | **C-Level & Enterprise Architects.** Strategic "North Star" (C1), cross-domain rules, and enterprise capability models (`01-enterprise`). |
| **PAD** | Platform Architecture Document | **Tech Leads & Managers.** Domain Capability (C2). Defines shared foundations, integration contracts, and system positioning. |
| **SAD** | Software Architecture Document | **DevOps, SREs, SWEs.** System Solution (C2). Defines internal structure, deployment topology, observability, and resilience mechanics. |
| **ADR** | Architecture Decision Record | **Meta.** Rationale for significant technical pivots and trade-offs (`04-decisions`). |
| **STD** | Standard Document | **Meta.** Mandatory engineering policies and guardrails (`05-standards`). |
| **TRD** | Technical Requirements Document | **[NOT USED]** Functional/Technical translation of the PRD. |
| **TDD (Design)** | Technical Design Document | **Implementers & QA.** Component blueprints (C3), API contracts, ERDs, Security, and Failure Handling. |
| **TDD (Testing)**| Test Driven Development | **Engineering Methodology**. The discipline used to implement the Test Strategy. |
| **ERD** | Entity Relationship Diagram | **Data Schema**. The structural foundation of the TDD (Design). |

### The Strategic Evolution of GDC (Product Vision)

We have evolved the way we document product vision to ensure it remains actionable and synchronized with technical reality:

*   **GDC (C1 Product/System)**: Contains the overarching business vision and high-level design concept.
*   **The Scnehaux Way (Integrated)**: To prevent "Vision Drift", the GDC is directly integrated into the **System Context & Business Drivers** of both **PAD** and **SAD** documents.

### GDC (Governance): The Quality Safeguard

While the Vision (Concept) is integrated into technical docs, the **Governance** aspect of GDC remains the central engine for quality enforcement:
*   **Role**: Defines the "Guardrails" for the entire ecosystem, ensuring all artifacts meet the 10/10 Governance-Grade maturity.
*   **Implementation**: Housed within the `00-governance` folder, it provides the automated Linters, Score Sheets, and Audit Toolkit.
*   **Mandate**: No PAD or SAD is considered "Approved" without passing the GDC Governance audit.

> **[NOTE]**
> This integration applies **STRICTLY to PAD and SAD** documents. It ensures that any developer reading the Container Architecture (C2) immediately understands the High-Level Vision (C1) that drives it. 
> 
> *ADR, STD, and TDD documents remain focused on their specific meta-roles and do not carry the full GDC context.*

### PAD vs SAD: The Functional Distinction

In a high-maturity ecosystem, **PAD and SAD are not mutually exclusive.** A platform system (like IAM) requires both:
1.  **PAD (Domain Architecture)**: Defines the "Position & Connectivity". It explains how an app fits into the platform and its relationships with other enterprise capabilities. (e.g., "What is Identity at Scnehaux?").
2.  **SAD (System Architecture)**: Defines the "Internal Reality". It explains how the specific app is built, its internal components, and its operational behavior. (e.g., "How is the IAM Service built?").

### The Redundancy of TRD (Technical Requirements Document)

At Scnehaux, we **do not use** a standalone TRD. We believe that technical requirements are inseparable from the architecture that addresses them.

*   **Reasoning**: Separate TRDs often lead to documentation fragmentation and "stale requirements" that do not reflect the actual architectural solution.
*   **The Integrated Approach**: All functional and technical translations of the PRD are integrated directly into the **SAD** or **PAD** (specifically within the **Scope & Context** and **Solution Strategy** sections).
*   **Benefit**: This ensures that every technical requirement is mapped directly to an architectural decision or container structure, maintaining a single source of truth for the entire system lifecycle.

---

## Architectural Layers

The architecture is structured into the following layers to prevent "Domain Contamination" and ensure strict, automated policy enforcement:

### 00-governance / GDC Gov (The Enforcement Layer)

Provides the **automated instruments** and quality standards required to maintain a **Grade 10/10** architecture.
- **Standard**: Follows the GDC template (`GDC-*`).
- **Toolkit**: Policy-as-Code Linter (`linter.py`), Automated YAML Linting Rules (`linting-rules.yaml`), and the Architecture Review Score Sheet.
- **Purpose**: To provide the automated "Rule of Law" for the entire foundation.

---

### 01-enterprise / EAD (The Strategic Layer - C1 Context)

Defines the global "City Map" and the enterprise-wide directives.
- **Standard**: Follows the 5-section EAD template (`EAD-*`) mapping strictly to the **4 Core TOGAF Domains**:
  1. **`EAD-001` (Business)**: Capability maps, enterprise principles.
  2. **`EAD-002` (Data)**: Database engines, persistence guidelines, and data sovereignty.
  3. **`EAD-003` (Application)**: mTLS mandates, gateway policies, integration, and security boundaries.
  4. **`EAD-004` (Technology)**: Go and Node.js dual core paved roads, exception paths, and evolutionary strategies.
- **Rule**: Must remain at a high level of abstraction. Strict SLA metrics (e.g., `P95 <= 200ms` or `>= 99.95%` availability) are mandated, but implementation-specific details are prohibited.

---

### 02-platform & 03-applications (Architecture Domains - C2 Context)

Organizes systems into domain-specific subfolders to ensure clean ownership and discoverability.

*   **Platform Domain (`02-platform/domain-name/`)**:
    *   **PAD (C2 Domain Architecture)**: A **single, cohesive document** (`*.pad.md`) defining horizontal integration contracts, trust boundaries, capabilities, and positioning.
*   **Application Domain (`03-applications/app-name/`)**:
    *   **SAD (C2 System Architecture)**: A **single, cohesive document** (`*.sad.md`) defining vertical system topologies, runtime flows, failure modes, observability, and container boundaries.

**The Cohesion Rule**: Splitting PAD/SAD into separate micro-files (like `security.md` or `operations.md`) is prohibited to prevent architectural drift and maintenance waste. All aspects (including Security and Operations) are fully encapsulated within the single canonical document's mandated sections.

---

### 04-decisions / ADR (The Rationale Layer)

The immutable history of "Why" and the formal escape hatch for paved road exceptions.
- **Rule**: All major architectural shifts or paved road deviations must be traceable to an ADR here.
- **Status**: Once approved, an ADR is immutable. Changes require a superseding ADR.

---

### 05-standards / STD (The Guardrail Layer)

Mandatory granular policies that supplement EAD paved roads.
- **Scope**: Lower-level technical instructions (API Design guidelines, coding styles, database schemas).
- **Enforcement**: Deviation without an approved ADR and ARB waiver is a Critical Governance Violation.

---


## Governance Model

### Architectural Authority

This repository is the single source of truth for architectural governance.

No system may:

- Enter production without an approved SAD.
- Deviate from standards without an ADR.
- Introduce breaking architectural changes without review.

---

### Review Workflow (The 5-Layer Governance Model)

In a mature architecture ecosystem, we rely on **Policy-as-Code** for absolute consistency, reserving human intellect for strategic judgment:

1.  **Draft Creation**: Author drafts the document using the Context-Aware Template defined by the file prefix (PAD/SAD/TDD).
2.  **Linter / Policy Engine (Primary Enforcement)**: Run `python linter.py`. The linter blocks vague wording and enforces mandatory structures.
3.  **CI/CD Gates**: Document must pass the linter pipeline (100% pass) to be eligible for merge.
4.  **Manual Score Sheet (Human Fallback)**: Used by Reviewers only for high-risk approvals or evaluating exceptions (`lint_disable`).
5.  **ARB Review (Strategic Oversight)**: Formal Architecture Review Board approval for strategic EAD/PAD pivots.
6.  **Approval**: Document status is updated to `approved` in YAML metadata.

---

### Running the Linter

To ensure all documentation complies with the Governance Standard, you must run the local linter before submitting any changes:

```bash
python linter.py
```

The linter will verify that:
- The structure matches the exact Context-Aware Template defined by the file ID (e.g., SAD sections vs TDD sections).
- Prohibited vague or ambiguous words ("highly scalable", "fast") are not used.
- Mandatory `doc_meta` YAML headers exist and are valid.

---

### Traceability Model

- EAD defines strategic constraints.
- PAD defines shared foundational capabilities.
- SAD defines system-specific architecture.
- ADR documents decision rationale.
- Standards define mandatory engineering policy.

All layers must remain consistent.

---

## Versioning

The architecture baseline is version-controlled.

Major architectural shifts must:

- Update EAD (if strategic)
- Include corresponding ADR
- Be explicitly reviewed and approved

---

## Non-Functional Discipline

All systems must define measurable targets for:

- Availability
- Performance
- Scalability
- Security
- Observability
- Resilience

Vague or non-measurable requirements are not acceptable.

---

## Change Management

Architectural evolution must be:

- Explicit
- Traceable
- Reviewed
- Documented

This repository represents the current architectural baseline.
