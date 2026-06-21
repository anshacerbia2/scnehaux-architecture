---
doc_meta:
  id: GDC-011
  title: Architecture Decision Record (ADR) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Architecture Decision Record (ADR) Guideline

## 1. Context & Scope

**Mandate**: All major architectural shifts or paved road deviations must be traceable to an ADR.

It applies to all engineers, product leads, and architects documenting system decisions across global and local repository contexts.

---

## 2. Policy Framework

### 2.1 ADR Taxonomy & Types

Every ADR must declare its `adr_type` to clarify the intent of the decision. The allowed types are:

| ADR Type | Purpose |
|---|---|
| **Foundational** | Makes a core architectural decision for the first time when no prior decision exists. |
| **Implementation** | Selects an implementation or option that is mandated/permitted by an STD. |
| **Exception** | Approves a deviation (waiver) against an active STD. |
| **Conflict Resolution** | Resolves conflicting constraints between an STD, ADR, or business requirement. |
| **Replacement** | Replaces a pre-existing architectural decision. |

### 2.2 The Ruleset Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-compliance-engine.md)**, the ADR specification is strictly governed by the following domain-specific linter components:

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (the Single Source of Truth).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`adr_type`</li><li>`status`</li><li>`created`</li><li>`created_by`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`proposed`</li><li>`accepted`</li><li>`rejected`</li><li>`superseded`</li><li>`deprecated`</li></ul> |
| **Metadata** | Exception Info Required Fields | <ul><li>`approved_by`</li><li>`expiry_date`</li><li>`risk_classification`</li><li>`exception_reason`</li></ul> |
| **Metadata** | Allowed Types | <ul><li>`foundational`</li><li>`implementation`</li><li>`exception`</li><li>`conflict_resolution`</li><li>`replacement`</li></ul> |
| **Structure** | Required Sections | <ul><li>`Title`</li><li>`Status`</li><li>`Context`</li><li>`Decision Drivers`</li><li>`Decision`</li><li>`Consequences`</li><li>`Compliance Impact`</li><li>`Alternatives Considered`</li></ul> |
<!-- AUTO-GENERATED-RULES:END -->


| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-adr.yaml` | Enforces the `decision_record` properties and specific `allowed_statuses` for the ADR lifecycle. |
| **Python Engine** | `validators/adr.py` | **Conditional Schema**: Injects `exception_info` requirements if `adr_type` is `exception`.<br>**Temporal Enforcement**: Executes time-based checks against `expiry_date` to trigger expired waiver errors. |

**Engine Execution Mechanics**:
1. **Conditional Schema Validation**: The CI linter dynamically shifts its validation rules based on the `adr_type`. If `exception` is selected, the pipeline automatically enforces the presence and validity of the `exception_info` block.
2. **Automated Waiver Expiration (Hard Block)**: The CI pipeline performs temporal validation on Exception ADRs. If an active (`accepted`) waiver ADR reaches its `expiry_date`, the linter triggers a **Hard CI Block (Exit 1)** with an `exception_expired` error. To clear this block, the team must either resolve the technical debt or secure a waiver renewal. In either case, the expired ADR's `status` MUST be transitioned from `accepted` to either `deprecated` (if the debt is resolved and the waiver is no longer needed) or `superseded` (if a new Exception ADR is approved to extend the timeline). It cannot revert to `proposed` or be arbitrarily deleted.

### 2.3 Semantic Definitions

#### 2.3.1 STD vs ADR Implementation Scenarios

To resolve confusion on when to write an ADR vs an STD, teams must follow this matrix:

| Scenario | Global STD | Global ADR | Project ADR | Notes |
|---|---|---|---|---|
| Organization establishes a new enterprise-wide rule | ✅ Create | ⚠️ Optional | ❌ | Board can create an STD without an ADR |
| Organization selects an enterprise strategic platform/tech | ✅ Update/Create | ✅ Create | ❌ | E.g., React, PostgreSQL, Kubernetes |
| Organization adopts an external regulation | ✅ Create | ❌ Usually No | ❌ | PCI-DSS, ISO27001, GDPR |
| Organization resolves a conflict between enterprise standards | ✅ Update | ✅ Create | ❌ | Enterprise-level conflict resolution |
| Organization shifts enterprise architectural direction | ✅ Update | ✅ Create | ❌ | E.g., monolith → microservices |
| STD dictates a single, exclusive solution | ✅ Existing | ❌ | ❌ | Project simply complies |
| STD provides multiple approved options | ✅ Existing | ❌ | ✅ Create | Project selects an option |
| STD mandates a capability but does not specify a product | ✅ Existing | ❌ | ✅ Create | Project selects the implementation |
| Project adopts technology not covered by an STD | ❌ | ❌ | ✅ Create | Local architecture decision |
| Project makes a local, isolated decision | ❌ | ❌ | ✅ Create | E.g., adopting an internal library |
| Project deviates from an STD (waiver) | ✅ Existing | ❌ | ✅ Create | Exception decision |
| Multiple projects request the exact same waiver | ✅ Update | ✅ Create | Existing | Indicates the STD needs revision |
| Project faces a conflict between two STDs | ✅ Existing | ❌ | ✅ Create | Local conflict resolution |
| Conflict applies across the entire enterprise | ✅ Update | ✅ Create | ❌ | Global conflict resolution |
| Internal refactoring without architectural changes | ❌ | ❌ | ❌ | ADR not required |
| Minor version upgrades that don't alter architecture | ❌ | ❌ | ❌ | ADR not required |
| Replacing a strategic library in a single project | ❌ | ❌ | ✅ Create | E.g., Redux → Zustand |
| Replacing a strategic library enterprise-wide | ✅ Update | ✅ Create | ❌ | Enterprise migration |
| Project follows the STD fully without needing a choice | ✅ Existing | ❌ | ❌ | No decision necessary |

#### 2.3.2 Directory Structure & Naming Conventions

Because ADRs are authored at both the Root Enterprise level and the Local Project level, they must utilize different structural taxonomies appropriate for their scope.

**Enterprise Level (Root Repo)**
Enterprise ADRs must reside in the `05-decisions/` directory of the architecture-description repository, strictly adhering to a **Domain-Driven Taxonomy**.

- **Naming Convention**: `ADR-GLB-[N]-[slug].md` (Global) or `ADR-[DOMAIN]-[CAPABILITY]-[N]-[slug].md` (Domain).

**Example Directory Structure:**
```text
scnehaux-architecture/
└── 05-decisions/                    # (Domain-Driven Taxonomy)
    ├── _global/
    │   └── ADR-GLB-001-modular-monolith.md
    └── ui-platform/
        └── design-tokens/
            └── ADR-UIP-TKN-001-domain-based-taxonomy.md
```

**Project Level (Local Repo)**
Local project ADRs must reside in the `docs/04-decisions/` directory of local workspaces, utilizing a **Module/Feature-Driven Taxonomy**.

- **Naming Convention**: `ADR-[REPO]-[COMPONENT]-[N]-[slug].md`.

**Example Directory Structure:**
```text
scnehaux-ui-platform/                # (Project Repository)
└── docs/
    └── 04-decisions/                # (Module-Driven Taxonomy)
        ├── auth-module/
        │   └── ADR-UIP-AUTH-001-jwt-rotation.md
        └── core-components/
            └── ADR-UIP-CORE-001-button-api.md
```

**Unified Indexing Invariant**
- **Requirement**: Every repository (both Enterprise and Local) must maintain a root-level index catalog linking to every ADR with its current status. The index must be updated prior to merging any new ADR.

#### 2.3.3 Document Template Schema (Metadata Frontmatter)

**Enterprise Level (Root Repo)**
```yaml
doc_meta:
  id: ADR-GLB-[Seq] | ADR-[DOM]-[CAP]-[Seq]  # e.g. ADR-GLB-001 or ADR-UIP-TKN-001
  title: Short Descriptive Title
  adr_type: foundational | implementation | exception | conflict_resolution | replacement
  status: proposed | accepted | rejected | superseded | deprecated
  created: YYYY-MM-DD
  created_by: Creator Name | [Name1, Name2]
```

**Project/Local Level (Project Repo)**
```yaml
doc_meta:
  id: ADR-[REPO]-[COMPONENT]-[Seq]  # e.g. ADR-SCNX-IAM-GO-001 or ADR-UIP-AUTH-001
  title: Short Descriptive Title
  adr_type: foundational | implementation | exception | conflict_resolution | replacement
  status: proposed | accepted | rejected | superseded | deprecated
  created: YYYY-MM-DD
  created_by: Creator Name | [Name1, Name2]
  parent_sad: [Parent SAD ID]       # Optional: Mapped parent Software Architecture Document

  # Required ONLY if adr_type is "exception" (Waiver Approval)
  exception_info:
    approved_by: [Sponsor/Approver Name or ARB]
    expiry_date: YYYY-MM-DD           # Waiver validity cap (max 365 days)
    risk_classification: low | medium | high
    exception_reason: Brief rationale explaining standard deviation
```

#### 2.3.4 Document Section Semantics

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
|---|---|---|
| **Title** | The ADR ID and a descriptive title header. | Must follow the naming convention and clearly state the architecture decision. |
| **Status** | Chronological table tracking state transitions (`Date`, `Status`), the `ADR Type`, the `Reviewers` (or SMEs) consulted, and the final `Approver`. | Must track the chronological state transitions, reviewers, and approvers. |
| **Context** | The technical problem, constraints, and business requirements driving the decision. | Must objectively describe the problem space and constraints driving the decision. |
| **Decision Drivers** | The core technical and business factors forcing the decision. | Must list the critical technical and business factors forcing the choice. |
| **Decision** | The chosen course of action with concrete, binding statements. | Must explicitly define the chosen course of action in binding terms. |
| **Consequences** | The results (Positive, Negative, Operational) of the decision. | Must analyze the positive, negative, and operational impacts of the decision. |
| **Compliance Impact** | Defines related standards, compliance status, and required waivers. | Must list any standards violated and link to the required waivers. |
| **Alternatives Considered** | Analysis of alternate paths rejected during review. | Must provide a comparative analysis of rejected options. |

#### 2.3.5 Metadata Schema Properties

| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `id` | String | Unique identifier (e.g., `ADR-001`). |
| `title` | String | Descriptive title of the document. |
| `adr_type` | Enum | The intent of the decision (must match Allowed Types in §2.1). |
| `status` | Enum | The current lifecycle state (must match Allowed Statuses below). |
| `created` | Date | The creation date (YYYY-MM-DD). |
| `created_by` | String | The author of the ADR. |

**Exception Info Required Fields (Conditional)**
*Required only if `adr_type` is `exception`.*

| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `approved_by` | String | The Sponsor, Approver Name, or ARB granting the waiver. |
| `expiry_date` | Date | Waiver validity cap (max 365 days). |
| `risk_classification` | Enum | The evaluated risk (`low`, `medium`, `high`). |
| `exception_reason` | String | Brief rationale explaining the standard deviation. |

#### 2.3.6 Allowed Lifecycle Statuses

| Status | Meaning / Lifecycle Stage |
|---|---|
| `proposed` | Under review or initial draft state. |
| `accepted` | Formalized and active. |
| `rejected` | The proposed decision was rejected. |
| `superseded` | Replaced by a newer ADR. |
| `deprecated` | Phased out and no longer applicable. |

### 2.4 Lifecycle & Audit

#### 2.4.1 Document Lifecycle & Statuses

Every architectural decision must progress through a managed, auditable lifecycle. An ADR must exist in one of five explicit states:

```
    [Proposed] ──► [Accepted] ──► [Superseded]
         │              │
         ▼              ▼
    [Rejected]     [Deprecated]
```

- **Proposed**: The decision is drafted and undergoing active peer review. It carries no authority.
- **Accepted**: The decision has been reviewed, approved by the designated authority, and is active.
- **Rejected**: The decision has been evaluated and declined. The record remains as historical context.
- **Superseded**: The decision has been replaced by a newer ADR. The newer ADR must explicitly reference the superseded record by ID.
- **Deprecated**: The decision is no longer recommended or valid, but has not been directly replaced.

#### 2.4.2 The Immutability Principle
An ADR is a strict historical record. Once an ADR reaches the **Accepted** or **Rejected** state, its core substantive content (Context, Decision Drivers, Decision, Consequences) **MUST NEVER BE MODIFIED**. 
- If a decision needs to be reversed or fundamentally changed, you must create a **new ADR** (using the `replacement` type) and update the old ADR's status to `Superseded`. 
- **Administrative Exemption (Decoupled Execution)**: Strategic decisions (ADRs) are decoupled from tactical execution (STDs). An ADR may be approved before its corresponding Standard document is finalized. Appending hyperlinks to newly drafted Standards (STDs) or cross-referencing newer ADRs in the "Related Standards" section is classified as a metadata update and is explicitly permitted.
- Other permissible edits to an existing Accepted ADR include: updating the Status table to reflect a lifecycle transition, or fixing minor typographical errors that do not alter the technical context.

> [!IMPORTANT]
> **Semantic Versioning DOES NOT apply to ADRs.**
>
> Unlike living documents (EAD, PAD, SAD, TDD), ADRs do not use `Major.Minor.Patch` versioning. ADRs are immutable, point-in-time decision records. Once an ADR is accepted, its architectural content must never be modified. If the architectural decision changes in the future, a **NEW** ADR must be authored which explicitly supersedes the old one.

#### 2.4.3 Resolving Expired Waivers (Exception ADRs)

When an Exception ADR reaches its `expiry_date`, the CI pipeline will block the repository. To clear the block, the team must execute one of the following three scenarios:

1. **Scenario A: Resolving Temporary Tech Debt**
   - *Context*: The deviation was a temporary hack (e.g., using an unapproved library to hit a deadline).
   - *Action*: The team refactors the codebase to comply with the global STD.
   - *ADR Update*: The expired Exception ADR's status is changed to `deprecated`.

2. **Scenario B: Paved Road Evolution (Permanent Necessity)**
   - *Context*: The deviation proved to be a permanent necessity and a better architectural choice for the enterprise.
   - *Action*: The organization must update the Global STD to officially permit the new technology or pattern.
   - *ADR Update*: The old Exception ADR is changed to `deprecated` (the waiver is no longer needed), and a new `Implementation` ADR is created under the newly revised STD.

3. **Scenario C: Niche Permanence (Waiver Renewal)**
   - *Context*: The deviation is permanent for this specific team, but the ARB refuses to make it a global standard to prevent widespread adoption.
   - *Action*: The team must submit a new Exception ADR to the ARB, requesting an extension of the waiver for another cycle (paying the "bureaucracy tax").
   - *ADR Update*: The old Exception ADR's status is changed to `superseded`, replaced by the newly approved Exception ADR.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this ADR Guideline:

1. **Decentralized Markdown ADRs vs. Centralized Database Tooling**
   - *Why rejected*: Storing architectural decisions in a centralized system (like Jira or a custom DB) disconnects the decision from the exact commit state of the source code it governs.
   - *The Trade-Off*: We lose robust querying capabilities (e.g., "Show me all ADRs related to React"). In exchange, ADRs live and die alongside the codebase, ensuring that checking out an old branch inherently checks out the architectural context of that exact point in time.
