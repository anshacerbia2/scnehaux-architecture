---
doc_meta:
  id: GDC-002
  title: Enterprise Standards (STD) Guideline
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-29
---

# Enterprise Standards (STD) Guideline

## 1. Context & Scope

The `02-standards` directory is the authoritative collection of mandatory rules, constraints, patterns, and methodologies governing software development and architecture across the Scnehaux enterprise. 

- **Scope**: Lower-level technical instructions (API Design guidelines, coding styles, database schemas).
- **Enforcement**: Deviation without an approved ADR and ARB waiver is a Critical Governance Violation.

This document defines the structural, taxonomic, and maturity requirements for writing and managing Enterprise Standards (STD).

### 1.1 STD vs ADR (Living Law vs Historical Log)
- **ADR (Architecture Decision Record)** captures a point-in-time decision, explaining *why* a choice was made and its context. ADRs may become superseded or deprecated, but their historical text remains immutable.
- **STD (Standard)** is a *living document*. It represents the active, mandatory ruleset that engineers must follow *today*. When rules change, the STD file is updated to reflect the current state of truth.

---

## 2. Policy Framework

### 2.1 Domain-Driven Taxonomy & Suffixing
All standards must strictly adhere to the Domain-Driven Taxonomy and directory constraints defined in `GDC-000`:

1. **Rule 1 (Max Depth)**: Directory nesting is strictly capped at Level 3 (`Root -> Domain -> Capability`). Creating further subdirectories inside a capability folder (Level 4+) is prohibited to prevent the "Russian Doll" anti-pattern and maintain flat discoverability.
   - Example: `02-standards/ui-platform/design-tokens/` (VALID)
   - Example: `02-standards/ui-platform/design-tokens/tier-1/` (INVALID)

2. **Rule 2 (Lexicographical Suffixing)**: To group related or multi-part documents without violating the Max Depth rule, use alphanumeric suffixing on the sequence ID. This keeps related files sequentially grouped in the file explorer.
   - Example: `STD-UIP-TKN-001A-architecture.md`
   - Example: `STD-UIP-TKN-001B-tier1-core-tokens.md`

### 2.2 Standard Maturity Model
To prevent rigid compliance grids from stifling innovation, every enterprise standard must declare a maturity phase in its `status` field.

> **Authoritative Source**: The canonical definitions of the four maturity phases (Assessed, Trial, Adopted, Hold), including their adoption requirements, deviation policies, and sunset procedures, are defined and maintained in **[GDC-008 — Technology Lifecycle & Standards Governance](./GDC-008-architecture-lifecycle.md)**.

All STD documents must declare one of the four phases defined in GDC-008 in their `status` metadata field.

---

### 2.3 The Living Specification Principle (Mutability & Versioning)
Unlike ADRs (which are immutable historical logs of a specific point-in-time decision), **STDs are living specifications** that represent the *currently active* engineering mandates.

1. **Direct Mutability**: When technologies, standards, or rules evolve, the existing STD file is edited directly. Creating new standard files for minor/major updates to the same domain is prohibited.
2. **Versioning Doctrine (SemVer)**: Every update to an STD must increment the `version` metadata field following Semantic Versioning (X.Y.Z):
   - **Major (X.0.0)**: Introducing new mandatory restrictions, breaking changes, or deprecating existing active paths.
   - **Minor (1.X.0)**: Adding optional recommendations, non-breaking rules, or clarifying examples.
   - **Patch (1.0.X)**: Fixing typos, broken links, or minor metadata updates.
3. **ADR Authorization Invariant**: Any change resulting in a **Major (X.0.0)** version bump of an enterprise standard MUST be authorized by an approved ADR. The `governed_by` metadata field of the STD must be updated to point to the new ADR.

---

### 2.4 Mandatory STD Schema
Every Standard must utilize the standard Markdown template and include the following metadata and sections:

### 2.5 Metadata Frontmatter

#### 2.5.1 Enterprise Level (Root Repo)
```yaml
doc_meta:
  id: STD-GLB-[Seq][Suffix] | STD-[DOM]-[CAP]-[Seq][Suffix]  # e.g., STD-GLB-001 or STD-UIP-TKN-001A
  title: Short Descriptive Title
  owner: Lead Domain Architect Name / Team
  version: Y.Y.Y
  status: adopted | trial | assessed | hold
  classification: public | internal | restricted
  governed_by: [Authorizing ADR ID]        # Optional: Mapped authorizing ADR ID (e.g., ADR-GLB-001)
```

#### 2.5.2 Project/Local Level (Project Repo)
```yaml
doc_meta:
  id: STD-[REPO]-[COMPONENT]-[Seq][Suffix]  # e.g., STD-SCNX-IAM-GO-001 or STD-UIP-CORE-001A
  title: Short Descriptive Title
  owner: Lead System Engineer / Team Name
  version: Y.Y.Y
  status: adopted | trial | assessed | hold
  classification: public | internal | restricted
  parent_std: [Parent Enterprise Standard ID] # e.g., STD-GLB-001 or STD-E006 (Traceability link)
  governed_by: [Authorizing ADR ID]        # Optional: Mapped authorizing ADR ID (e.g., ADR-SCNX-IAM-GO-001)
```

### 2.6 Standard Document Structure
While the metadata schema is strictly enforced, the document body must follow these logical groupings to maintain enterprise consistency:

1. **Objective & Scope**: Defines what the standard covers and who it applies to.
2. **Design Principles**: The architectural philosophy behind the standard (the "why").
3. **Normative Rules**: The core constraints and DOs/DONTs.
   - *Optional*: Include **Examples** (code snippets, JSON payloads) directly under the relevant rules to provide clarity.
4. **Exceptions**: A direct mapping of normative rules to the specific technical conditions under which they may be bypassed. Governance procedures (e.g., ADR or ARB approvals) must NOT be documented here. If no valid exceptions exist, this section must explicitly state `None.`.
5. **Enforcement Mechanism**: How compliance is measured (e.g., CI/CD Linter, ARB Review).
   - *Optional*: Specify the **Severity** of the violation (e.g., Warning vs. Hard Pipeline Blocker).

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement
1. **Structural Audit**: The automated pipeline verifies that all STD files contain the metadata header and the mandatory sections. Missing sections or incorrect YAML format will fail the build.
2. **Quality Checklist**:
   - Technical statements must be quantified.
   - Ambiguous marketing terms (e.g., highly-scalable or blazing-fast) are prohibited.

## 4. Severity & Exceptions

### 4.1 Exception Waiver Protocol
- Deviations from STD structures or principles require an approved project Exception ADR and ARB waiver sign-off.
- Approved waivers have a maximum validity of 365 days.
