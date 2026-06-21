---
doc_meta:
  id: GDC-010
  title: Software Architecture Document (SAD) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Software Architecture Document (SAD) Guideline

## 1. Context & Scope

SADs represent the C2 System/Software Architecture layer of the C4 metamodel, defining the physical execution containment, deployment topology, container boundaries, failure modes, and runtime observability (e.g., backend service monoliths, web SPAs, or mobile clients).

SADs establish the "How". They serve as the definitive physical blueprint for a specific deployable unit. A single logical business capability (PAD) is physically fulfilled by one or more software containers (SADs) in a strict 1-to-N mapping. They establish the concrete technology stack, network isolation, and database engines required to execute the logical contracts defined by the PAD.

---

## 2. Policy Framework

### 2.1 Specificity & Containment

- **Specificity Rule**: Unlike PADs, SADs must completely drop agnosticity. They must explicitly specify the concrete physical deployment topology, technology stacks, cache stores, database engines, and physical container boundaries.
- **Containment Invariant**: SADs must explicitly document failure containment boundaries, specifically defining the Blast Radius for all major failure modes.
- **Physical Container Separation (Beyond Frontend/Backend)**: To prevent logical boundaries from being contaminated by deployment-specific execution mechanics, **every distinct deployable unit must have its own SAD**, even if they serve the same business capability. For example, a single Identity PAD (`scnehaux-iam.pad.md`) might be fulfilled by:
  - **Backend API Service**: `scnehaux-iam.sad.md` (The core HTTP server).
  - **Frontend SPA**: `scnehaux-iam-web.sad.md` (The browser client).
  - **Async Worker**: `scnehaux-iam-worker.sad.md` (Kafka consumer handling background email dispatch).
  - **Data Pipeline/Cron**: `scnehaux-iam-archiver.sad.md` (Nightly job moving old sessions to cold storage).

### 2.2 The Ruleset Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-compliance-engine.md)**, the SAD specification is strictly governed by the following domain-specific linter components:

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (the Single Source of Truth).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`governed_by`</li><li>`owner`</li><li>`version`</li><li>`status`</li><li>`classification`</li><li>`parent_pad`</li><li>`review_cycle_days`</li><li>`last_reviewed`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`proposed`</li><li>`approved`</li><li>`deprecated`</li></ul> |
| **Metadata** | Allowed Classifications | <ul><li>`public`</li><li>`internal`</li><li>`restricted`</li></ul> |
| **Structure** | Required Sections | <ul><li>`Context`</li><li>`Solution Architecture`</li><li>`Deployment & Topology`</li><li>`Runtime Flows`</li><li>`Resilience & Failure Modes`</li><li>`Observability`</li><li>`Security Considerations`</li></ul> |
| **Structure** | Optional Sections | <ul><li>`Assumptions`</li><li>`Alternatives Considered`</li><li>`Compatibility Strategy`</li><li>`Data Classification`</li><li>`Document Lifecycle & Statuses`</li></ul> |
| **Content** | Required Section Keywords | **Resilience**: `['Blast Radius']` |
<!-- AUTO-GENERATED-RULES:END -->


| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-sad.yaml` | Checks for `parent_pad`, enforces `Blast Radius` keywords under the Resilience section, and deployment topologies. |
| **Python Engine** | `validators/sad.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications`.<br>**Domain Validation**: Enforces upward traceability by guaranteeing the presence of a valid `parent_pad` ID. |

**Engine Execution Mechanics**:
1. **Physical Containment Audit**: The linter will verify that SADs contain technology-specific information. Unlike PADs, SADs must specify the concrete database engines, cache stores, and container topologies.
2. **Hold Technology Enforcement**: The automated linter will execute a Hard Block (Exit 1) on any SAD document that implements a technology currently marked as `Hold` in its respective lifecycle phase.

### 2.3 Semantic Definitions

#### 2.3.1 Taxonomy, Directory Structure & Naming Conventions

SADs are **single, cohesive documents** (`[system-name].sad.md` or `[system-name]-[suffix].sad.md`). **The Cohesion Rule:** Splitting a SAD into separate micro-files (e.g., separating it into `security.md` and `operations.md`) is strictly prohibited. All system aspects must be fully encapsulated within the single canonical document's mandated sections to prevent drift.

They must utilize **Asset Container Folders** (`04-application/[system-name]/`), which act as an isolation boundary for the system's `.sad.md` files and supporting assets (e.g., deployment topology diagrams).

> [!NOTE]
> - **Naming Convention**:
>   - `[system-name].sad.md` (no suffix): Represents the **primary/core application** of the system.
>   - `[system-name]-[suffix].sad.md`: Represents **specific applications, clients, or workers** (e.g., `iam-web`, `iam-worker`).
> - **Ambiguity Rule**: If a system contains multiple SADs, **avoid using a suffix-less name**. It is highly recommended to use explicit suffixes for all containers (e.g., `iam-api.sad.md` and `iam-web.sad.md`) to prevent ambiguity.
> - **Grouping Rule**: The implementation of a single logical PAD will often result in multiple physical SADs. To maintain cohesion, **all SADs fulfilling the same domain must be grouped together** within a single `[system-name]` directory. Do not create separate root folders for each container.
  *(Reminder: While they share a folder, each physical container must still be documented by exactly **one** SAD).*

**Example Directory Structure:**
```text
scnehaux-architecture/
└── 04-application/                  # (Asset Container Folders)
    └── iam/                         # (System grouping folder)
        ├── iam-api.sad.md           # (Backend API SAD, explicit suffix)
        ├── iam-web.sad.md           # (Client application SAD)
        └── deployment-topology.png
```

#### 2.3.2 Document Template Schema (Metadata Frontmatter)

Every SAD must begin with a YAML frontmatter block containing these fields:
```yaml
doc_meta:
  id: SAD-XXX                       # Unique software system ID
  title: [Application Title]          # Descriptive title of the application
  owner: [System Team/Role]           # Authoritative system owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: internal            # public | internal | restricted
  parent_pad: PAD-XXX               # Referencing the Parent Business Capability PAD ID
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
```

#### 2.3.3 Document Section Semantics

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
|---|---|---|
| **Context** | Explain the technical "Why" behind the system boundary. | Must explicitly link to the governing business capability PAD. |
| **Solution Architecture** | Concrete C2 container diagrams detailing the physical technology stack. | Must illustrate all physical containers, network zones, and persistence layers. |
| **Deployment & Topology** | Document network boundaries, scaling assumptions, resource limits (CPU/Memory), and scaling triggers. | Must contain a physical topology diagram and specific hardware/container limits. |
| **Runtime Flows** | Detail request lifecycles, asynchronous event publishing, and degradation paths. | Must contain sequence diagrams for critical operations. |
| **Resilience & Failure Modes** | Identify SPOFs, fallback strategies, and the exact **Blast Radius**. | Must document circuit breaker configurations and fallback states.<br>**Constraint**: Must contain the exact keyword `Blast Radius`. |
| **Observability** | Mandate specific SLIs, SLOs, alert thresholds, and distributed tracing spans. | Must define specific SLI/SLO metrics, tracing spans, and alert thresholds. |
| **Security Considerations** | Detail system-level threat mitigations, input validation, secrets management, and data classification boundaries. | Must address threat models, data encryption at rest/transit, and IAM boundaries. |
| **Assumptions *(Optional)*** | Document external operational assumptions. | Must list business, external, or operational assumptions the design relies upon. |
| **Alternatives Considered *(Optional)*** | Document technical trade-offs of the chosen deployment architecture. | Must list rejected technologies/designs and the rationale for rejection. |
| **Compatibility Strategy *(Optional)*** | Detail schema migration or API versioning compatibility rules. | Must outline API versioning or schema migration paths to avoid breaking changes. |
| **Data Classification *(Optional)*** | Detail sensitivity levels of data stored/processed (PII, confidential). | Must declare if PII, PHI, or sensitive financial data is present. |

#### 2.3.4 Metadata Schema Properties
| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `id` | String | Unique identifier (e.g., `SAD-001`). |
| `title` | String | Descriptive title of the document. |
| `owner` | String | Lead Owner (e.g., System Architect). |
| `version` | String | Must comply with Semantic Versioning (e.g., 1.0.0). |
| `status` | Enum | The current lifecycle state (must match Allowed Statuses below). |
| `classification` | Enum | The data sensitivity (must match Allowed Classifications below). |
| `parent_pad` | String | The parent PAD ID this system fulfills (e.g., `PAD-001`). |
| `review_cycle_days` | Integer | The frequency in days for required review. |
| `last_reviewed` | Date | The date of the last formal review (YYYY-MM-DD). |

#### 2.3.5 Allowed Lifecycle Statuses
| Status | Meaning / Lifecycle Stage |
|---|---|
| `proposed` | The system architecture is under design or ARB review. |
| `approved` | The system architecture is formalized and approved for production deployment. |
| `deprecated` | The system is being sunset, decommissioned, or has been replaced. |

#### 2.3.6 Allowed Classifications
| Classification | Meaning / Data Sensitivity |
|---|---|
| `public` | Available to anyone. |
| `internal` | Restricted to company employees. |
| `restricted` | Restricted to specific teams or roles. |

#### 2.3.7 Semantic Versioning Classification

| Version | Trigger / Architectural Change |
|---|---|
| **Major (2.0.0)** | Changing core physical infrastructure (e.g., VM to Kubernetes), swapping core databases, or altering Zero-Trust physical boundaries. |
| **Minor (1.1.0)** | Adding a new physical container (e.g., adding a Redis cache sidecar) that does not break existing components. |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, fixing dead links. |


### 2.4 Lifecycle & Audit

All SAD documents must undergo a periodic review every `review_cycle_days` (default 180 days) to ensure structural integrity and relevance against the enterprise capability map.

**Qualitative Enforcement (ARB Audit)**
*Note: Qualitative scoring is inherited from **[GDC-002 §2 — Scoring Criteria](./GDC-002-quality-rubric.md)**.*

SADs have the following custom overriding audit metric:
1. **Blast Radius Analysis**: Under the Resilience section, every major failure mode must specify the *Blast Radius* (e.g., "Single User Session", "Full Tenant Isolation", "Entire Platform Outage") to pass the review gate.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this SAD Guideline:

1. **Manual Blast Radius Enforcement vs. Automated Chaos Engineering**
   - *Why rejected*: Fully automated Chaos Engineering requires significant infrastructure maturity and cannot run effectively during the design phase before code is written.
   - *The Trade-Off*: We rely on the architect's manual, theoretical calculation of the "Blast Radius" during the design phase. In exchange, we force engineers to confront and document failure boundaries proactively, preventing SPOFs from entering the codebase in the first place.
