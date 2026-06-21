---
doc_meta:
  id: GDC-009
  title: Platform Architecture Document (PAD) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Platform Architecture Document (PAD) Guideline

## 1. Context & Scope

PADs represent the C2 Domain Architecture layer of the C4 metamodel, defining the logical business capabilities, bounded contexts, trust boundaries, and strategic positioning of a business domain (e.g., `identity`, `ui-platform`, `hris`, `finance`).

PADs establish the "What". They serve as the design-time single source of truth (SSOT) for domain-level contracts. A single logical business capability (PAD) governs one or more physical software containers (SADs) in a strict 1-to-N mapping. They establish conceptual integration rules (such as trust boundaries and SLA targets) *before* physical systems are built. While concrete API specifications are delegated downstream via Web Developer Portals, the PAD remains the stable, logical anchor.

---

## 2. Policy Framework

### 2.1 Agnosticity & Stability

- **Agnosticity Rule**: PADs must remain technology-agnostic at the physical infrastructure level. They establish logical capabilities, trust boundaries, and conceptual integration rules (e.g., SLA targets). Concrete API specifications must be delegated to downstream Web Developer Portals, and physical container details belong in SADs.
- **Stability**: Because they govern logical rather than physical boundaries, PADs are designed to be highly stable. Future physical decompositions (e.g., splitting a monolithic HRIS backend into separate Payroll and Employee microservices) must require zero modification to the core domain contracts established within the PAD.

### 2.2 The Ruleset Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-compliance-engine.md)**, the PAD specification is strictly governed by the following domain-specific linter components:

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (the Single Source of Truth).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`governed_by`</li><li>`owner`</li><li>`version`</li><li>`status`</li><li>`classification`</li><li>`fulfilled_by`</li><li>`review_cycle_days`</li><li>`last_reviewed`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`proposed`</li><li>`approved`</li><li>`deprecated`</li></ul> |
| **Metadata** | Allowed Classifications | <ul><li>`public`</li><li>`internal`</li><li>`restricted`</li></ul> |
| **Structure** | Required Sections | <ul><li>`Business Capability`</li><li>`Trust Boundary & Security`</li><li>`Integration Contract`</li><li>`Strategic Architecture`</li><li>`Quality Attributes`</li></ul> |
| **Structure** | Optional Sections | <ul><li>`Assumptions`</li><li>`Alternatives Considered`</li><li>`Data Classification`</li><li>`Document Lifecycle & Statuses`</li></ul> |
<!-- AUTO-GENERATED-RULES:END -->


| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-pad.yaml` | Enforces C1/C2 macro-topology boundaries and integration contracts. |
| **Python Engine** | `validators/pad.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications`.<br>**Domain Validation**: Enforces that `fulfilled_by` exists and is a populated list of SAD IDs, guaranteeing C1 to C2 boundary composition. |

**Engine Execution Mechanics**:
1. **Logical Boundary Isolation**: The linter will flag any PAD that hardcodes physical server names, specific deployment ports, database index structures, or specific library versions.

### 2.3 Semantic Definitions

#### 2.3.1 Taxonomy, Directory Structure & Naming Conventions

PADs are **single, cohesive documents** (`[domain].pad.md`). **The Cohesion Rule:** Splitting a PAD into separate micro-files (e.g., separating it into `security.md` and `operations.md`) is strictly prohibited. All domain aspects must be fully encapsulated within the single canonical document's mandated sections to prevent drift.

**Naming Convention:**
The filename must strictly adhere to the `pad_pattern` regex: `^[a-z0-9-]+\.pad\.md$`.

They must utilize **Asset Container Folders** (`03-platform/[domain]/`), which act as an isolation boundary for the `.pad.md` file and its supporting assets (e.g., architecture diagrams, PlantUML files).

**Example Directory Structure:**
```text
scnehaux-architecture/
└── 03-platform/                     # (Asset Container Folders)
    └── ui-platform/
        ├── ui-platform.pad.md
        └── architecture-diagram.png
```

#### 2.3.2 Metadata Schema Properties

Every PAD must begin with a YAML frontmatter block containing these fields:
```yaml
doc_meta:
  id: PAD-XXX                       # Business capability ID
  title: [Capability Title]           # Descriptive title of the Business Capability
  owner: [Domain Team/Role]           # Authoritative team owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: public              # public | internal | restricted
  fulfilled_by:                       # List of physical SAD IDs fulfilling this business capability
    - SAD-XXX
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
```

#### 2.3.3 Document Section Semantics

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
|---|---|---|
| **Business Capability** | Define the business value, bounded context, and macro-level features that define this business capability. Focus on logical boundaries. |  Must remain technology-agnostic. Focus on logical boundaries rather than libraries or infrastructure. |
| **Trust Boundary & Security** | Map the isolation levels, identity propagation (e.g., Zero Trust), data encryption, and tenant separation models. | Detail how user contexts and application credentials traverse system boundaries. |
| **Integration Contract** | Specify strict API contracts, required proprietary headers (e.g., `Scnehaux-Account`), and authentication handshakes. | Must define retry envelopes and payload validation standards for external clients. |
| **Strategic Architecture** | Illustrate the C1/C2 macro-topology and its relationship with other enterprise systems (diagrams mandatory). | Must contain a clean structural diagram (such as Mermaid or similar) mapping domains. |
| **Quality Attributes** | Explicit, quantifiable Non-Functional Requirements (NFR) targets (e.g., P95 Latency < 200ms). | Must quantify metrics (e.g., "99.99% Availability", "P95 Latency < 200ms", "Maximum throughput of 5000 req/s"). |
| **Assumptions *(Optional)*** | Document any external dependencies or business assumptions. | Must list business, external, or operational assumptions the design relies upon. |
| **Alternatives Considered *(Optional)*** | Document technical alternatives evaluated and their trade-offs. | Must list rejected technologies/designs and the rationale for rejection. |
| **Data Classification *(Optional)*** | Detail sensitivity levels of data processed by the platform. | Must declare if PII, PHI, or sensitive financial data is present. |

#### 2.3.4 Metadata Schema Properties
| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `id` | String | Unique identifier (e.g., `PAD-001`). |
| `title` | String | Descriptive title of the document. |
| `owner` | String | Lead Owner (e.g., Domain Architect). |
| `version` | String | Must comply with Semantic Versioning (e.g., 1.0.0). |
| `status` | Enum | The current lifecycle state (must match Allowed Statuses below). |
| `classification` | Enum | The data sensitivity (must match Allowed Classifications below). |
| `fulfilled_by` | List[String] | Array of child SAD IDs that fulfill this domain architecture (e.g., `[SAD-AUTH-01]`). |
| `review_cycle_days` | Integer | The frequency in days for required review. |
| `last_reviewed` | Date | The date of the last formal review (YYYY-MM-DD). |

#### 2.3.5 Allowed Lifecycle Statuses
| Status | Meaning / Lifecycle Stage |
|---|---|
| `proposed` | The domain architecture is under design or ARB review. |
| `approved` | The domain architecture is formalized and acts as the official contract. |
| `deprecated` | The business capability is being phased out or has been replaced. |

#### 2.3.6 Allowed Classifications
| Classification | Meaning / Data Sensitivity |
|---|---|
| `public` | Available to anyone. |
| `internal` | Restricted to company employees. |
| `restricted` | Restricted to specific teams or roles. |

#### 2.3.7 Semantic Versioning Classification

| Version | Trigger / Architectural Change |
|---|---|
| **Major (2.0.0)** | Altering the trust boundary, merging domains, or changing the fundamental logical integration contract. |
| **Minor (1.1.0)** | Adding a new logical business capability to the domain (e.g., adding an MFA module to an existing Identity domain). |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, fixing dead links. |


### 2.4 Lifecycle & Audit

As the Single Source of Truth (SSOT) for Platform Architecture Documents (PAD), the PAD represents highly stable business capabilities. They must undergo a periodic review every `review_cycle_days` (default 180 days) to ensure structural integrity and relevance against the enterprise capability map.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this PAD Guideline:

1. **C1/C2 Separation (PAD vs. SAD) vs. Unified Architecture Documents**
   - *Why rejected*: A unified document containing both logical capabilities and physical servers rapidly decays. When physical servers scale or database engines change, the logical boundary document requires constant, unnecessary updates.
   - *The Trade-Off*: We accept the cognitive overhead of maintaining two separate but linked documents (PAD for logical, SAD for physical). In exchange, we gain highly stable logical contracts (PADs) that do not break when physical infrastructure topologies mutate.
