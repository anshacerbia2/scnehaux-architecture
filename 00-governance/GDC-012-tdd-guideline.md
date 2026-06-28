---
doc_meta:
  id: GDC-012
  title: Technical Design Document (TDD) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-06-01
---

# Technical Design Document (TDD) Guideline

## 1. Context & Scope

TDDs represent the component-level (C3) blueprints, API contracts, ERDs, security boundaries, and failure handling mechanisms for specific implementations before code is written.

---

## 2. Policy Framework

### 2.1 Directory Taxonomy

- **Requirement**: Because TDDs are Project-level documents, they must utilize **Asset Container Folders** within the `docs/02-designs/` directory.

**Example Directory Structure:**
```text
scnehaux-ui-platform/                # (Project Repository)
└── docs/                            # (Root)
    └── 02-designs/                  # (Asset Container Folders - Level 2)
        └── auth-module/             # (Level 3 - Max Depth)
            ├── TDD-UIP-AUTH-001-jwt-rotation.md
            └── flow-diagram.png
```

### 2.2 The Ruleset Architecture

In addition to the global structural enforcement defined in **[GDC-002](./GDC-002-compliance-engine.md)**, the TDD specification is strictly governed by the following domain-specific linter components:

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (the Single Source of Truth).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`owner`</li><li>`version`</li><li>`status`</li><li>`classification`</li><li>`parent_sad`</li><li>`review_cycle_days`</li><li>`last_reviewed`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`proposed`</li><li>`approved`</li><li>`deprecated`</li></ul> |
| **Metadata** | Allowed Classifications | <ul><li>`public`</li><li>`internal`</li><li>`restricted`</li></ul> |
| **Structure** | Required Sections | <ul><li>`Context & Requirements`</li><li>`Design Details`</li><li>`API / Schema Contracts`</li><li>`Security & Privacy`</li><li>`Failure Handling`</li><li>`Observability`</li><li>`Testing Strategy`</li><li>`Rollout Strategy`</li></ul> |
| **Structure** | Optional Sections | <ul><li>`Alternatives Considered`</li><li>`Compatibility Strategy`</li><li>`Document Lifecycle & Statuses`</li></ul> |
<!-- AUTO-GENERATED-RULES:END -->


| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-tdd.yaml` | Validates `parent_sad` attributes to prevent orphan designs. |
| **Python Engine** | `validators/tdd.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications` ensuring proper baseline governance. |

**Engine Execution Mechanics**:
1. **Hold Technology Enforcement**: The automated linter will execute a Hard Block (Exit 1) on any TDD document that implements a technology currently marked as `Hold` in its respective lifecycle phase.
2. **Traceability**: The linter ensures that a `parent_sad` attribute exists in the TDD metadata, preventing isolated or "orphan" components.
3. **Remote Execution (Security Constraint)**: Downstream project repositories must not maintain local copies of the linter. Local CI/CD pipelines must invoke the central linter remotely. See **[GDC-002: Downstream Integration](./GDC-002-compliance-engine.md#41-downstream-integration-remote-execution)** for detailed setup instructions.

### 2.3 Semantic Definitions

#### 2.3.1 Naming Conventions

The filename must strictly adhere to the `tdd_pattern` regex: `^TDD-[a-z0-9-]+-[a-z0-9-]+-\d{3}[A-Z]*-[a-z0-9-]+\.md$`.

#### 2.3.2 Taxonomy

TDDs are **single, cohesive documents** (`TDD-[REPO]-[COMPONENT].md`). **The Cohesion Rule:** Splitting a TDD into separate micro-files (e.g., separating it into `schema.md` and `tests.md`) is strictly prohibited. All component design aspects must be fully encapsulated within the single canonical document's mandated sections to prevent drift.

#### 2.3.3 Directory Structure

Must reside in a `docs/02-designs/` directory adjacent to the source code.

#### 2.3.4 Metadata Schema Properties

Every TDD must begin with a YAML frontmatter block containing these fields:
```yaml
doc_meta:
  id: TDD-[REPO]-[COMPONENT]-[Seq]    # Unique system ID
  title: [Component Title]            # Descriptive title of the component
  owner: [Engineer/Role]              # Authoritative owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: internal            # public | internal | restricted
  parent_sad: SAD-XXX               # Referencing the Parent SAD ID
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
```

| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `id` | String | Unique identifier (e.g., `TDD-001`). |
| `title` | String | Descriptive title of the document. |
| `owner` | String | Lead Owner (e.g., Software Engineer). |
| `version` | String | Must comply with Semantic Versioning (e.g., 1.0.0). |
| `status` | Enum | The current lifecycle state (must match Allowed Statuses below). |
| `classification` | Enum | The data sensitivity (must match Allowed Classifications below). |
| `parent_sad` | String | The parent SAD ID this design implements (e.g., `SAD-001`). |
| `review_cycle_days` | Integer | The frequency in days for required review. |
| `last_reviewed` | Date | The date of the last formal review (YYYY-MM-DD). |

##### Allowed Lifecycle Statuses

| Status | Meaning / Lifecycle Stage |
|---|---|
| `proposed` | The design is under review. |
| `approved` | The design is approved for implementation. |
| `deprecated` | The implementation is being phased out or has been replaced. |

##### Allowed Classifications

| Classification | Meaning / Data Sensitivity |
|---|---|
| `public` | Available to anyone. |
| `internal` | Restricted to company employees. |
| `restricted` | Restricted to specific teams or roles. |

##### Semantic Versioning Classification

| Version | Trigger / Architectural Change |
|---|---|
| **Major (2.0.0)** | Breaking API contract changes (e.g., removing a required field, changing an endpoint path, fundamentally altering a database schema). |
| **Minor (1.1.0)** | Adding an optional field to an API response, adding a new non-breaking endpoint. |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, fixing dead links. |

#### 2.3.5 Document Section

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
|---|---|---|
| **Context & Requirements** | Define the upstream and downstream context, what the feature accomplishes, and the specific functional requirements. | Must link to the Parent SAD. |
| **Design Details** | Provide the C3 component blueprints. Include sequence diagrams, internal interactions, and structural class/module design. | Must be technology-specific. |
| **API / Schema Contracts** | Outline the exact payloads, database schemas (ERD), API endpoints, or event formats. | Must define validation rules. |
| **Security & Privacy** | Detail how PII is handled, what specific RBAC or RLS policies apply, and encryption requirements. | Must detail specific RBAC policies, encryption keys, and PII handling routines. |
| **Failure Handling** | Describe component-level retries, circuit breakers, degradation, and edge case mitigation. | Must be mapped to the SAD Blast Radius. |
| **Observability** | Document exact metric names, log formats, and distributed tracing spans that will be emitted. | Must define specific SLI/SLO metrics, tracing spans, and alert thresholds. |
| **Testing Strategy** | Outline unit, integration, and E2E testing approaches. | Must mention edge cases and security testing. |
| **Rollout Strategy** | Document feature flags, rollout phases, schema migration steps, and backward compatibility. | Must detail rollback procedures. |
| **Alternatives Considered *(Optional)*** | Analysis of alternate paths rejected during review. | Must list rejected technologies/designs and the rationale for rejection. |
| **Compatibility Strategy *(Optional)*** | Detailed backward compatibility plans for API changes. | Must outline API versioning or schema migration paths to avoid breaking changes. |


### 2.4 Lifecycle & Audit

#### 2.4.1 TDD Fate Matrix

TDDs are ephemeral. Their lifecycle must follow the **Ephemeral TDD Matrix**:

- **Class A (Strategic Transition)**: Designs governing core architectural shifts, major security FSMs, or schema migrations. Once fully implemented in production, their metadata `status` is transitioned to `deprecated` and the physical file is moved to `docs/02-designs/historical/` to serve as a permanent forensic audit trail.
- **Class B (Component & Feature Detail)**: Standard feature implementation layouts. Folded into the parent SAD and the physical TDD file is deleted once verified in production.
- **Class C (Exploratory & Spike)**: Prototype or exploratory designs. Deleted immediately after the Pull Request merges.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this TDD Guideline:

1. **The Ephemeral TDD Matrix vs. Permanent TDD Archives**
   - *Why rejected*: Archiving every component-level design forever leads to thousands of obsolete files. When a new engineer joins, they cannot distinguish between active architecture and legacy spikes.
   - *The Trade-Off*: We intentionally destroy (delete) historical design context for Class B/C implementations once they merge to main. In exchange, we radically reduce search latency and ensure that only high-level abstractions (PADs/SADs) and foundational shifts (Class A TDDs) are permanently maintained.
