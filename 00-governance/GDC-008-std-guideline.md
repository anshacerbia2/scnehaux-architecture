---
doc_meta:
  id: GDC-008
  title: Enterprise Standards (STD) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-29
---

# Enterprise Standards (STD) Guideline

## 1. Context & Scope

The `02-standards` directory is the authoritative collection of mandatory rules, constraints, patterns, and methodologies governing software development and architecture across the Scnehaux enterprise. Its scope encompasses lower-level technical instructions such as API Design guidelines, coding styles, and database schemas.

### 1.1 STD vs ADR (Living Law vs Historical Log)
- **ADR (Architecture Decision Record)** captures a point-in-time decision, explaining *why* a choice was made and its context. ADRs may become superseded or deprecated, but their historical text remains immutable.
- **STD (Standard)** is a *living document*. It represents the active, mandatory ruleset that engineers must follow *today*. When rules change, the STD file is updated to reflect the current state of truth.

---

## 2. Policy Framework

### 2.1 Specificity & Opinionation

- **Specificity Rule**: Standards (STDs) are **not** meant to be agnostic. They exist to enforce strict, concrete, and opinionated technical baselines. If a rule is purely abstract, it belongs in an Enterprise Architecture Document (EAD) as a Principle.
- **Global Standards (`STD-GLB*`)**: Define enterprise-wide technical constraints (e.g., universal API payloads, central logging schemas). While they may start as high-level abstract rules, once a specific technology becomes an enterprise baseline (e.g., via an ADR), global STDs must aggressively mandate its usage.
- **Domain & Local Standards**: Must be fiercely technology-specific and framework-opinionated. They map global requirements directly to concrete code implementations (e.g., "Use React 18", "Use Prisma" in the `ui-platform` repo).

### 2.2 The Ruleset Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-compliance-engine.md)**, the STD specification is strictly governed by the following domain-specific linter components:

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (the Single Source of Truth).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`owner`</li><li>`version`</li><li>`status`</li><li>`classification`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`adopted`</li><li>`trial`</li><li>`assessed`</li><li>`hold`</li></ul> |
| **Metadata** | Allowed Classifications | <ul><li>`public`</li><li>`internal`</li><li>`restricted`</li></ul> |
| **Structure** | Required Sections | <ul><li>`Objective & Scope`</li><li>`Design Principles`</li><li>`Normative Rules`</li><li>`Exceptions`</li><li>`Enforcement Mechanism`</li></ul> |
| **Content** | Prohibited Section Keywords | **Exceptions**: `['waiver', 'ADR', 'ARB', 'Approval Requirements']` |
<!-- AUTO-GENERATED-RULES:END -->


| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-std.yaml` | Validates normative rule structures and exact exception tracking. |
| **Python Engine** | `validators/std.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications`.<br>**Domain Validation**: Triggers `operational_stability_violation` if a document's status is `hold`, explicitly preventing adoption of retired components. |

**Engine Execution Mechanics**: The automated linter will execute a Hard Block (Exit 1) on any STD document that mandates a technology currently marked as `Hold` in its respective lifecycle phase.

### 2.3 Semantic Definitions

#### 2.3.1 Taxonomy, Directory Structure & Naming Conventions

Because STDs are authored at both the Root Enterprise level and the Local Project level, they must utilize different structural taxonomies appropriate for their scope.

**Enterprise Level (Root Repo)**
Enterprise standards must strictly adhere to a **Domain-Driven Taxonomy** within the `02-standards/` directory.

- **Naming Convention**: `STD-GLB-[N]-[slug].md` (Global) or `STD-[DOMAIN]-[CAPABILITY]-[N]-[slug].md` (Domain).
- **Rule 1 (Max Depth)**: Directory nesting is strictly capped at Level 3 (`Root -> Domain -> Capability`). Creating further subdirectories inside a capability folder (Level 4+) is prohibited to prevent the "Russian Doll" anti-pattern.
- **Rule 2 (Lexicographical Suffixing)**: To group multi-part documents without violating the Max Depth rule, use alphanumeric suffixing on the sequence ID (e.g., `001A`, `001B`).

**Example Directory Structure:**
```text
scnehaux-architecture/
└── 02-standards/                    # (Domain-Driven Taxonomy)
    ├── _global/
    │   └── STD-GLB-001-api-design.md
    └── ui-platform/
        └── design-tokens/
            ├── STD-UIP-TKN-001A-architecture.md
            └── STD-UIP-TKN-001B-tier1-core-tokens.md
```

**Project Level (Local Repo)**
Because a project repository inherently represents a single Domain or System, Domain-Driven Taxonomy is redundant. Local standards must utilize **Module/Feature-Driven Taxonomy** to closely mirror the source code structure.

- **Naming Convention**: `STD-[REPO]-[COMPONENT]-[N]-[slug].md`.
- **Location**: Must reside in the `docs/01-standards/` directory.

**Example Directory Structure:**
```text
scnehaux-ui-platform/                # (Project Repository)
└── docs/
    └── 01-standards/                # (Module-Driven Taxonomy)
        ├── core-components/
        │   └── STD-UIP-CORE-001-button-api.md
        └── form-components/
            └── STD-UIP-FORM-001-validation.md
```

#### 2.3.2 Document Template Schema (Metadata Frontmatter)

**Enterprise Level (Root Repo)**
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

**Project/Local Level (Project Repo)**
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

#### 2.3.3 Document Section Semantics

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
|---|---|---|
| **Objective & Scope** | Defines what the standard covers and who it applies to. | Must define the boundary of the standard and explicitly list any exclusions. |
| **Design Principles** | The architectural philosophy behind the standard (the "why"). | Must justify the technical axioms guiding the standard. |
| **Normative Rules** | The core constraints and DOs/DONTs. *(Optional: Include Examples/Snippets directly under the relevant rules to provide clarity).* | Must use RFC-2119 terminology (MUST, SHOULD, MUST NOT) for clear compliance. |
| **Exceptions** | A direct mapping of normative rules to the specific technical conditions under which they may be bypassed. If no valid exceptions exist, this section must explicitly state `None.`.<br>**Constraint**: Prohibited keywords include `waiver`, `ADR`, `ARB`, `Approval Requirements`. Governance procedures must NOT be documented here; this section only describes technical boundary edges. | Must strictly define boundary conditions for deviation. Do NOT include governance procedures. |
| **Enforcement Mechanism** | How compliance is measured (e.g., CI/CD Linter, ARB Review). *(Optional: Specify the Severity of the violation).* | Must specify the automated linter, pipeline hook, or review process enforcing the standard. |

#### 2.3.4 Metadata Schema Properties
| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `id` | String | Unique identifier. |
| `title` | String | Descriptive title of the document. |
| `owner` | String | Lead System Engineer / Team Name. |
| `version` | String | Must comply with Semantic Versioning (e.g., 1.0.0). |
| `status` | Enum | The current lifecycle state (must match Allowed Statuses below). |
| `classification` | Enum | The data sensitivity (must match Allowed Classifications below). |

#### 2.3.5 Allowed Lifecycle Statuses
| Status | Meaning / Lifecycle Stage |
|---|---|
| `adopted` | Formally accepted and enforced. |
| `trial` | In evaluation or POC phase. |
| `assessed` | Evaluated but not necessarily adopted. |
| `hold` | Suspended or pending retirement. (Triggers linter block for new adoptions). |

#### 2.3.6 Allowed Classifications
| Classification | Meaning / Data Sensitivity |
|---|---|
| `public` | Available to anyone. |
| `internal` | Restricted to company employees. |
| `restricted` | Restricted to specific teams or roles. |

#### 2.3.7 Semantic Versioning Classification

| Version | Trigger / Architectural Change |
|---|---|
| **Major (2.0.0)** | Radically changing a mandatory baseline (e.g., swapping approved database engines or introducing a new mandatory compliance layer). Breaks existing systems. |
| **Minor (1.1.0)** | Adding a new supplemental best-practice or an optional paved road. Backwards-compatible. |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, fixing dead links. |


### 2.4 Lifecycle & Audit

#### 2.4.1 Standard Maturity Model
To prevent rigid compliance grids from stifling innovation, every enterprise standard must declare a maturity phase in its `status` field.

> **Authoritative Source**: The canonical definitions of the four maturity phases (Assessed, Trial, Adopted, Hold), including their adoption requirements, deviation policies, and sunset procedures, are defined and maintained in **[GDC-004 — Technology Lifecycle & Standards Governance](./GDC-004-tech-lifecycle.md)**.

All STD documents must declare one of the four phases defined in GDC-004 in their `status` metadata field.

#### 2.4.2 The Living Specification Principle (Mutability & Versioning)
Unlike ADRs (which are immutable historical logs of a specific point-in-time decision), **STDs are living specifications** that represent the *currently active* engineering mandates.

1. **Direct Mutability**: When technologies, standards, or rules evolve, the existing STD file is edited directly. Creating new standard files for minor/major updates to the same domain is prohibited.
2. **Versioning Doctrine (SemVer)**: Every update to an STD must increment the `version` metadata field following Semantic Versioning (X.Y.Z):
   - **Major (X.0.0)**: Introducing new mandatory restrictions, breaking changes, or deprecating existing active paths.
   - **Minor (1.X.0)**: Adding optional recommendations, non-breaking rules, or clarifying examples.
   - **Patch (1.0.X)**: Fixing typos, broken links, or minor metadata updates.
3. **ADR Authorization Invariant**: Any change resulting in a **Major (X.0.0)** version bump of an enterprise standard MUST be authorized by an approved ADR. The `governed_by` metadata field of the STD must be updated to point to the new ADR.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this STD Guideline:

1. **Living Mutability vs. Immutable Standard Versions**
   - *Why rejected*: Storing every past version of a standard as a separate immutable file creates a "graveyard" of documents, leading to engineer confusion about which standard is currently active.
   - *The Trade-Off*: We lose out-of-the-box visibility into historical rules. In exchange, we guarantee that the `02-standards/` folder is always the definitive "Current State of Truth." Historical context is preserved in Git, while structural pivots are managed via Immutable ADRs.
