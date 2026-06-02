# Scnehaux Architecture

This repository is the authoritative Enterprise Architecture (EA) baseline and governance hub for **ALL** systems within the **Scnehaux Ecosystem**. 

It defines the enterprise architectural principles, governance rules, application capabilities & domain boundaries, system-level architecture requirements, architectural decisions, and engineering standards.

All systems, without exception, MUST align with the policies and constraints defined in this repository.

---

## Purpose

The purpose of this repository is to:

- **Establish Architectural Consistency**: Enforce uniform, deterministic design patterns and standardize the technology paved roads across all systems.
- **Enforce Engineering Discipline & Automated Compliance**: Act as a machine-readable governance hub that enforces production-grade engineering standards and architectural policies automatically via CI/CD pipelines.
- **Define Application Capabilities & Boundaries**: Establish strict domain boundaries and business capability mapping (PAD) to prevent architectural contamination.
- **Provide an Integration SSOT**: Serve as the authoritative, design-time Single Source of Truth for system integration contracts and UI/Backend topologies.
- **Preserve Decision Traceability**: Maintain an immutable, contextual history of all major architectural shifts (ADR).
- **Govern Architectural Evolution**: Define measurable non-functional fitness functions to safely scale and evolve systems over time.

This repository contains architecture artifacts only.
It does not contain implementation code.

---

## Architectural Methodology (The "Hybrid" Metamodel)

This repository uses a specific combination of frameworks to ensure scalability and clarity.

### The C4 Model Enforcement (Governance Boundary)

We strictly enforce the **C4 Model** to define the boundaries of this repository.

| Level | C4 Name | Scnehaux Scope | Location |
| :--- | :--- | :--- | :--- |
| **C1** | **Context** | **EAD** (Enterprise) | Root Repo (`01-enterprise`) |
| **C2** | **Container** | **PAD** (Domain) & **SAD** (System) | Root Repo (`03-platform`, `04-application`) |
| **C3** | **Component** | **TDD** (Detailed Design) | **Specific Project Repository** |
| **C4** | **Code** | Implementation & Source | **Specific Project Repository** |

> **[!IMPORTANT]**
> This repository is a **C1/C2 Architecture & Governance Hub**. We do not document internal components (C3) or source code (C4) here. Level C3 design documents (TDD) and C4 source code must reside in their specific project repositories to ensure "Docs-as-Code" synchronization.

### Meta & Cross-Cutting Layers
- **GDC** (Governance Document Contracts), **ADR** (Architecture Decision Records), and **STD** (Standard Documents) are **Meta Layers**.
- They are **Cross-Cutting**: they define the rules and rationale that bind all C1-C4 levels together.

---

## Document Types (Glossary of Truth)

The Scnehaux architecture ecosystem categorizes technical knowledge into specific, purpose-built document types to prevent overlap and ensure clear ownership. The following is the authoritative glossary of all recognized documents:

| Code | Full Name | Audience & Purpose |
| :--- | :--- | :--- |
| **PRD** | Product Requirements Document | Business "What" and "Why" (Non-technical). Not part of Scnehaux Architecture. |
| **GDC (Vision)** | Global Design Concept | **[DEPRECATED]** High-Level Vision (C1). Integrated into the **System Context & Business Drivers** of **PAD/SAD** documents. |
| **GDC (Gov)** | Governance Document Contract | **ARB & Principal Engineers.** Automated policy definitions, quality gates, and compliance enforcement (`00-governance`). |
| **EAD** | Enterprise Architecture Document | **C-Level & Enterprise Architects.** Strategic "North Star" (C1), cross-domain rules, and enterprise capability models (`01-enterprise`). |
| **PAD** | Platform Architecture Document | **Tech Leads & Managers.** Domain Capability (C2). Defines application capabilities, integration contracts, and system positioning. |
| **SAD** | Software Architecture Document | **DevOps, SREs, SWEs.** System Solution (C2). Defines internal structure, deployment topology, observability, and resilience mechanics. |
| **ADR** | Architecture Decision Record | **Meta.** Rationale for significant technical pivots and trade-offs (`05-decisions`). |
| **STD** | Standard Document | **Meta.** Mandatory engineering policies and guardrails (`02-standards`). |
| **TRD** | Technical Requirements Document | **[NOT USED]** Functional/Technical translation of the PRD. |
| **TDD (Design)** | Technical Design Document | **Implementers & QA.** Component blueprints (C3), API contracts, ERDs, Security, and Failure Handling. |
| **TDD (Testing)**| Test Driven Development | **Engineering Methodology**. The discipline used to implement the Test Strategy. |
| **ERD** | Entity Relationship Diagram | **Data Schema**. The structural foundation of the TDD (Design). |

### The Tale of Two GDCs: Resolving the Acronym Overload

In the Scnehaux ecosystem, the acronym **GDC** historically served two different purposes. To avoid confusion, we explicitly separate them into two distinct concepts:

#### 1. GDC (General Design Concept) — *The Product Vision*
*   **Role**: Contains the overarching business vision and high-level design concept (C1 Product/System).
*   **The Scnehaux Way (Integrated)**: We no longer write standalone GDC Vision documents. To prevent "Vision Drift", the General Design Concept is now directly integrated into the **Application Capability** section of PADs, and the **Context** section of SADs.

#### 2. GDC (Governance Document Contract) — *The Quality Safeguard*
*   **Role**: Defines the absolute "Guardrails" for the entire ecosystem, ensuring all architectural artifacts meet the 10/10 FAANG-Grade maturity. These are the `GDC-XXX` files.
*   **Implementation**: Housed exclusively within the `00-governance` folder, providing the Automated Linters (`linter.py`), Review Score Sheets, and Audit Toolkits.
*   **Mandate**: No PAD or SAD is considered "Approved" without passing the GDC Governance audit.

> **[NOTE]**
> The integration of the *General Design Concept* applies to **EAD, PAD, and SAD** documents. It ensures that any developer reading the Enterprise Strategy (C1) or System Architecture (C2) immediately understands the High-Level Vision that drives it. 


### PAD vs SAD: The Functional Distinction

In a high-maturity ecosystem, **PAD and SAD are not mutually exclusive; in fact, EVERY system in the Scnehaux ecosystem MUST have both.** We do not use PAD exclusively for "shared platforms".

1.  **PAD (Logical Application Capability & Domain Architecture)**: Defines the "Position & Connectivity". It explains **what** the application does from a business capability perspective, **why** it exists within the ecosystem, its logical domain boundaries, and its integration contracts with other systems. (It answers: *"What is the capability of this application, and Why is it needed?"*).
2.  **SAD (Physical System Architecture)**: Defines the "Internal Reality". It explains how the specific application is built, its internal components, deployment topology, and operational behavior. (It answers: *"How is this capability technically executed?"*).

### The Redundancy of TRD (Technical Requirements Document)

At Scnehaux, we **do not use** a standalone TRD. We believe that technical requirements are inseparable from the architecture that addresses them.

*   **Reasoning**: Separate TRDs often lead to documentation fragmentation and "stale requirements" that do not reflect the actual architectural solution.
*   **The Integrated Approach**: All functional and technical translations of the PRD are integrated directly into the **PAD** and **SAD** (specifically within the **Application Capability** and **Solution Architecture** sections). Enterprise Architecture (EAD) is driven by C-Level strategy rather than product-level PRDs.
*   **Benefit**: This ensures that every technical requirement is mapped directly to an architectural decision or container structure, maintaining a single source of truth for the entire system lifecycle.

---

## Architectural Layers

The architecture is structured into the following layers to prevent "Domain Contamination" and ensure strict, automated policy enforcement:

### 00-governance / GDC (Governance Document Contract) - The Enforcement Layer

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
- **Rule**: Must remain at a high level of abstraction. Strict SLA (Service Level Agreement) metrics (e.g., `P95 <= 200ms` or `>= 99.95%` availability) are mandated, but implementation-specific details are prohibited.

---

### 02-standards / STD (The Guardrail Layer)

Mandatory granular policies that supplement EAD paved roads.
- **Scope**: Lower-level technical instructions (API Design guidelines, coding styles, database schemas).
- **Enforcement**: Deviation without an approved ADR and ARB waiver is a Critical Governance Violation.

---

### 03-platform & 04-application (Logical Domain vs. Physical System - C2 Context)

To support a scalable **Platform-First Architecture (FAANG-Style)**, we strictly separate the logical domain definition from the physical software implementation:

*   **Logical Domain Layer (`03-platform/domain-name/`)**:
    *   **PAD (C2 Domain Architecture)**: A **single, cohesive document** (`*.pad.md`) defining the logical capabilities, bounded contexts, trust boundaries, and strategic positioning of a business domain (e.g., `identity`, `ui-platform`, `hris`, `finance`). 
    *   *Purpose*: Establishes the logical capabilities and domain boundaries. It defines conceptual integration rules (such as trust boundaries and SLA targets) while concrete API specifications are published via Web Developer Portals. Designed to be highly stable, ensuring that future decomposition (e.g., splitting HRIS into Payroll and Employee domains) requires zero modification to the core domain contracts.
*   **Physical System Layer (`04-application/app-name/`)**:
    *   **SAD (C2 System/Software Architecture)**: A **single, cohesive document** (`*.sad.md`) defining the physical deployment topology, container boundaries, runtime flows, failure modes, observability, and concrete systems fulfilling the domain.
    *   *Purpose*: Establishes the "How". A single logical domain capability (PAD) is physically fulfilled by one or more software containers (SADs) in a 1-to-N mapping.

**The Cohesion Rule**: Splitting PAD/SAD into separate micro-files (like `security.md` or `operations.md`) is prohibited to prevent architectural drift and maintenance waste. All aspects (including Security and Operations) are fully encapsulated within the single canonical document's mandated sections.

---

### 05-decisions / ADR (The Rationale Layer)

The immutable history of "Why" and the formal escape hatch for paved road exceptions.
- **Rule**: All major architectural shifts or paved road deviations must be traceable to an ADR here.
- **Status**: Once approved, an ADR is immutable. Changes require a superseding ADR.

---

## Governance Model

This repository is the single source of truth for architectural governance. For the full governance policy, see [GDC-000 — Documentation Governance Policy](./00-governance/GDC-000-documentation-governance.md).

No system may:

- Enter production without an approved SAD.
- Deviate from standards without an ADR.
- Introduce breaking architectural changes without review.

---

### Review Workflow (The 5-Stage Review Pipeline)

All architectural changes must undergo a formal peer review via Pull Request.

For the complete evaluation criteria and review process, see:
- [GDC-009 — Documentation Quality Framework](./00-governance/GDC-009-documentation-quality-framework.md)
- [GDC-010 — Architecture Review Process](./00-governance/GDC-010-architecture-review-process.md)

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
- STD defines mandatory engineering policy.
- PAD defines logical domain capabilities and integration boundaries.
- SAD defines system-specific architecture.
- ADR documents decision rationale.

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
