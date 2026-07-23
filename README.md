# Scnehaux Architecture

This repository is the **Single Source of Truth (SSOT)** for the **Scnehaux Enterprise Architecture**. It houses the definitive business capabilities, system topologies, technology standards, and architectural decisions for the entire ecosystem.

To ensure this architecture never becomes outdated or drifts from reality, this repository is governed by a strict **Circular Governance Framework**.

Unlike a traditional static wiki, this repository operates as an **Executable Architecture** via a _Docs-as-Code_ methodology. Every artifact's structural integrity and compliance is automatically validated through CI/CD linters and _Policy-as-Code_ before it can be merged.

**In summary:** This repository contains the **Enterprise Architecture**, and the **Circular Governance Framework** ensures that architecture remains pristine, verifiable, and strictly enforced across all engineering teams.

---

## Purpose

This repository has a **bipartite purpose**, serving both as the architecture of our systems and the governance engine that protects it:

### 1. Purpose of the Architecture (The Artifacts)

- **Establish Architectural Consistency**: Enforce uniform, deterministic design patterns and standardize the technology paved roads across all systems (STD).
- **Define Business Capabilities & Boundaries**: Establish strict logical domain boundaries (PAD) to prevent capability leakage and architectural contamination.
- **Provide an Integration SSOT**: Serve as the authoritative, design-time Single Source of Truth for system integration contracts, trust boundaries, and physical topologies (SAD).
- **Preserve Decision Traceability**: Maintain an immutable, contextual history of all major architectural shifts and explicitly track technical debt via Architecture Decision Records (ADR).

### 2. Purpose of the Governance (The Engine)

- **Execute a Circular Governance Model**: Establish a deterministically self-validating ecosystem where policies, linters, and rubrics mutually regulate each other without absolute immunity (_Eat Our Own Dog Food_).
- **Enforce Engineering Discipline (Shift-Left)**: Act as a machine-readable hub that enforces strict quality standards across two distinct artifact types: **Governance Quality** (the architecture and integrity of the governance framework itself) and **Architecture Quality** (the architecture and integrity of the actual software systems).
- **Govern Architectural Evolution**: Define measurable non-functional fitness functions, failure modes, and NFRs to safely scale and evolve systems over time.

This repository contains architecture artifacts only. It does not contain implementation code.

---

## Repository Map (The Hybrid Metamodel)

This repository synthesizes the core concepts and mental models of industry-standard frameworks (C4 Model, TOGAF, arc42, AWS Well-Architected) into a custom, context-aware execution model to ensure scalability and clarity.

> [!IMPORTANT]
>
> **Architecture Scope Limit:** This repository strictly houses **High-Level System Design (C1 Context & C2 Container levels)**. We do not document internal application components (C3) or source code (C4) here. Low-level Technical Design Documents (TDD) must reside locally in their specific code repositories to maintain strict _Docs-as-Code_ proximity and prevent documentation rot.

### 00-governance / GDC (The Constitutional Hub)

The central nervous system of the architecture. It contains the fundamental laws, the automated CI/CD engine (`06-fitness-function/engine/cli.py`), and the qualitative human rubrics that govern all other documents in the ecosystem.

- **The Constitution**: [GDC-000 — Documentation Governance Policy](00-governance\GDC-000-governance-policy.md)
- **The Automated Engine**: [GDC-001 — Fitness Functions & Compliance Engine](00-governance\GDC-001-fitness-functions.md)
- **The Human Rubric**: [GDC-002 — Quality Rubric](00-governance\GDC-002-quality-rubric.md)
- **The Review Process**: [GDC-003 — Review Process](00-governance\GDC-003-review-process.md)
- **Technology Lifecycle**: [GDC-004 — Tech Lifecycle](00-governance\GDC-004-tech-lifecycle.md)
- **Guideline**: [GDC-005 — Governance Document Contract (GDC) Guideline](00-governance\GDC-005-gdc-guideline.md)

### 01-enterprise / EAD (The Strategic Layer - C1 Context)

Defines the global "City Map" and the enterprise-wide macro directives (Business, Data, Application, Technology).

- **Guideline**: [GDC-006 — Enterprise Architecture Description (EAD) Guideline](00-governance\GDC-006-ead-guideline.md)

### 02-standards / STD (The Guardrail & Baseline Layer)

Mandatory granular policies that establish the architecture baseline and supplement EAD paved roads. This layer sets the minimum technical bar for quality, security, and operational excellence (e.g., API Design guidelines, database isolation rules).

- **Guideline**: [GDC-007 — Enterprise Standard (STD) Guideline](00-governance\GDC-007-std-guideline.md)

### 03-domain / PAD (Logical Domain - C2 Context)

Defines the logical business capabilities, bounded contexts, system trust contracts, and strategic positioning of a business domain (e.g., `identity`, `finance`).

- **Guideline**: [GDC-008 — Product Architecture Document (PAD) Guideline](00-governance\GDC-008-pad-guideline.md)

### 04-system / SAD (Physical System - C2 Context)

Defines the physical deployment topology, container boundaries, runtime execution flows, failure modes, observability, and concrete systems fulfilling the PAD.

- **Guideline**: [GDC-009 — System Architecture Document (SAD) Guideline](00-governance\GDC-009-sad-guideline.md)

### 05-decisions / ADR (The Rationale Layer)

The immutable history of "Why". This layer captures foundational architectural decisions, tracks implementation rationale, resolves conflicts, and serves as the formal escape hatch for paved road exceptions.

- **Guideline**: [GDC-010 — Architecture Decision Record (ADR) Guideline](00-governance\GDC-010-adr-guideline.md)

### Local Implementation (C3 Context)

Defines the component-level blueprints built downstream.

- **Guideline**: [GDC-011 — Technical Design Document (TDD) Guideline](00-governance\GDC-011-tdd-guideline.md)

---

## Quick Start: The Governance Engine

To ensure seamless "Shift-Left" validation, install the pre-commit hook. This will automatically scan your files before allowing a `git commit`:

```bash
# Install dependencies
make install

# Install the native git hook (Run this once)
make install-hooks
```

You can also execute the automated compliance engine locally to scan the repository manually:

```bash
# Run locally for human-readable output
make lint
```

To ensure the linter engine itself remains robust, execute the high-coverage test suite:

```bash
# Run the Linter Engine Test Suite (FAANG Standard: >=95% coverage)
make test
```

For CI/CD pipeline integration, the engine supports a structured machine-readable format:

```bash
scnehaux-lint --format json
```

### What the Linter Enforces

Our automated compliance engine (`06-fitness-function/engine/cli.py`) aggressively verifies **Governance Quality** and **Architecture Quality**, including:

- **Taxonomy & Metadata**: Naming conventions, YAML schema validity, and cross-reference traceability.
- **Structural Compliance**: Mandatory design sections, minimum content length, and link rot prevention.
- **Content Quality**: Prohibition of vague vocabulary, mandatory quantifiable metrics, and temporal waiver expiration.

For the exhaustive list of automated rules, see **[GDC-001 — Fitness Functions & Compliance Engine](00-governance\GDC-001-fitness-functions.md)**.

---

## How to Contribute & Modify Rules

Please read **[CONTRIBUTING.md](CONTRIBUTING.md)** for the definitive workflows on how to:

1. **Author Architecture Documents** (PAD, SAD, ADR, etc.)
2. **Modify Governance Rules** (The 4-step Docs-as-Code reconciliation flow)

---

This repository represents the current architectural baseline.
