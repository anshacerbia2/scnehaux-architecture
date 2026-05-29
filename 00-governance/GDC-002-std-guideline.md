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
To prevent rigid compliance grids from stifling innovation, every enterprise standard must declare one of four maturity phases in its `status` field:
- **assessed**: The standard is experimental or undergoing evaluation. Teams are encouraged to run pilots, but adoption is optional. No waivers are required to deviate.
- **trial**: The standard is verified in pilot programs. It is recommended for new services, but existing services are exempt.
- **adopted**: The standard is the default mandatory baseline. Deviations require an approved exception waiver from the Architecture Review Board (ARB).
- **hold**: The standard is deprecated. New implementations are prohibited from adopting it. Existing implementations must schedule a migration path to replacement systems.

---

## 3. Mandatory STD Schema

Every Standard must utilize the standard Markdown template and include the following metadata and sections:

### 3.1 Metadata Frontmatter
```yaml
doc_meta:
  id: STD-GLB-[Seq][Suffix] | STD-[DOM]-[CAP]-[Seq][Suffix]  # e.g., STD-GLB-001 or STD-UIP-TKN-001A
  title: Short Descriptive Title
  owner: Lead Domain Architect Name / Team
  version: Y.Y.Y
  status: adopted | trial | assessed | hold
  classification: public | internal | restricted
```

### 3.2 Standard Document Structure
While the metadata schema is strictly enforced, the document body should follow these logical groupings to maintain enterprise consistency:

1. **Objective & Scope**: Defines what the standard covers and who it applies to.
2. **Design Principles**: The architectural philosophy behind the standard (the "why").
3. **Normative Rules**: The core constraints and DOs/DONTs.
   - *Optional*: Include **Examples** (code snippets, JSON payloads) directly under the relevant rules to provide clarity.
4. **Exceptions & Alternatives**: The fallback or waiver procedure if a team is blocked.
5. **Enforcement Mechanism**: How compliance is measured (e.g., CI/CD Linter, ARB Review).
   - *Optional*: Specify the **Severity** of the violation (e.g., Warning vs. Hard Pipeline Blocker).
