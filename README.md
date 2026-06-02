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

This repository contains architecture artifacts only. It does not contain implementation code.

---

## Quick Start: Running the Linter

To ensure all documentation complies with the Governance Standard, you must run the local linter before submitting any changes:

```bash
python linter.py
```

The linter will verify that:
- The structure matches the exact Context-Aware Template defined by the file ID (e.g., SAD sections vs TDD sections).
- Prohibited vague or ambiguous words ("highly scalable", "fast") are not used.
- Mandatory `doc_meta` YAML headers exist and are valid.

---

## Repository Map (The C4 Ecosystem)

This repository uses a specific combination of frameworks (C4 Model, TOGAF, arc42 (Adapted), AWS Well-Architected) to ensure scalability and clarity.

> **[!IMPORTANT]**
> This repository is a **C1/C2 Architecture & Governance Hub**. We do not document internal components (C3) or source code (C4) here. Level C3 design documents (TDD) and C4 source code must reside in their specific project repositories to ensure "Docs-as-Code" synchronization.

### 00-governance / GDC (Governance Document Contract) - The Enforcement Layer
Provides the automated instruments and quality standards required to maintain a Grade 10/10 architecture.
- **Must Read**: [GDC-000 — Documentation Governance Policy](./00-governance/GDC-000-documentation-governance.md)

### 01-enterprise / EAD (The Strategic Layer - C1 Context)
Defines the global "City Map" and the enterprise-wide directives (Business, Data, Application, Technology).

### 02-standards / STD (The Guardrail & Baseline Layer)
Mandatory granular policies that establish the architecture baseline and supplement EAD paved roads. This layer sets the minimum technical bar for quality, security, and operational excellence (e.g., API Design guidelines, coding styles, database schemas).

### 03-platform / PAD (Logical Domain - C2 Context)
Defines the logical capabilities, bounded contexts, trust boundaries, and strategic positioning of a business domain (e.g., `identity`, `finance`).

### 04-application / SAD (Physical System - C2 Context)
Defines the physical deployment topology, container boundaries, runtime flows, failure modes, observability, and concrete systems fulfilling the domain.

### 05-decisions / ADR (The Rationale Layer)
The immutable history of "Why". This layer captures foundational architectural decisions, tracks implementation rationale, resolves conflicts, and serves as the formal escape hatch for paved road exceptions.

---

## Governance Model & Approvals

No system may:
- Enter production without an approved SAD.
- Deviate from standards without an ADR.
- Introduce breaking architectural changes without review.

All architectural changes must undergo a formal peer review via Pull Request. For the complete evaluation criteria and review process, see:
- [GDC-009 — Documentation Quality Framework](./00-governance/GDC-009-documentation-quality-framework.md)
- [GDC-010 — Architecture Review Process](./00-governance/GDC-010-architecture-review-process.md)

### The 6-Stage Review Pipeline
1.  **Draft Creation**: Author drafts the document using the Context-Aware Template defined by the file prefix (PAD/SAD/TDD).
2.  **Linter / Policy Engine (Primary Enforcement)**: Run `python linter.py`. The linter blocks vague wording and enforces mandatory structures.
3.  **CI/CD Gates**: Document must pass the linter pipeline (100% pass) to be eligible for merge.
4.  **Manual Score Sheet (Human Fallback)**: Used by Reviewers only for high-risk approvals or evaluating exceptions (`lint_disable`).
5.  **ARB Review (Strategic Oversight)**: Formal Architecture Review Board approval for strategic EAD/PAD pivots.
6.  **Approval**: Document status is updated to `approved` in YAML metadata.

---

This repository represents the current architectural baseline.
