---
doc_meta:
  id: GDC-009
  title: System Architecture Document (SAD) Guideline
  owner: Architecture Authority
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# System Architecture Document (SAD) Guideline

## 1. Context & Scope

SADs represent the C2 System/Software Architecture layer of the C4 metamodel, defining the physical execution containment, deployment topology, container boundaries, failure modes, and runtime observability (e.g., backend service monoliths, web SPAs, or mobile clients).

SADs establish the "How". They serve as the definitive physical blueprint for a specific deployable unit. A single logical domain capability (PAD) is physically fulfilled by one or more software containers (SADs) in a strict 1-to-N mapping. They establish the concrete technology stack, network isolation, and database engines required to execute the logical contracts defined by the PAD.

### 1.1 Philosophy & Decision Horizon

**Decision question:** _"How is one deployable system built to realize (part of) a PAD's capability?"_ A SAD is the solution-planning tier for a single deployable unit: the physical reality.

**Position on the three governing dimensions:**

- **Stability / half-life — 3–5 years (two-way door).** Expected to be refactored as technology and load evolve. Because it is replaceable, it may carry rich physical detail.
- **Abstraction — C2 physical (System Context + Container).** It stops at the container boundary; component- and class-level design (C3) belongs in the TDD.
- **Ownership — one system / service team.**

**Litmus test (SAD vs TDD):** _"Is this about how the system is composed and deployed (SAD), or how a unit is coded (TDD)?"_ Containers, deployment topology, and runtime flows → SAD. Classes, schemas / DDL, algorithms, and queries → TDD.

**Traceability:** every SAD declares its `parent_pad`; one PAD is realized by N SADs. A SAD never redefines a contract owned by its parent PAD — it implements it.

---

## 2. Policy Framework

### 2.1 Specificity & Containment

- **Specificity Rule**: Unlike PADs, SADs must completely drop agnosticity. They must explicitly specify the concrete physical deployment topology, technology stacks, cache stores, database engines, and physical container boundaries.
- **Containment Invariant**: SADs must explicitly document failure containment boundaries, specifically defining the Blast Radius for all major failure modes.
- **Physical Container Separation (Deployable Units Only)**: To prevent logical boundaries from being contaminated by deployment-specific execution mechanics, **every distinct deployable unit must have its own SAD**. Non-deployable components (e.g., shared UI libraries, internal SDKs) are strictly exempt from requiring a standalone SAD (see Section 2.2). For deployable systems, a single Identity PAD (`scnehaux-iam.pad.md`) might be fulfilled by:
  - **Backend API Service**: `scnehaux-iam.sad.md` (The core HTTP server).
  - **Frontend SPA**: `scnehaux-iam-web.sad.md` (The browser client).
  - **Async Worker**: `scnehaux-iam-worker.sad.md` (Kafka consumer handling background email dispatch).
  - **Data Pipeline/Cron**: `scnehaux-iam-archiver.sad.md` (Nightly job moving old sessions to cold storage).

### 2.2 The Master SAD Federation (Multi-Repo & SDKs)

While microservices map neatly (one repo to one deployable unit), modern ecosystems often utilize **multi-repo libraries, SDKs, or Module Federation** where multiple repositories compile into a single deployable artifact. Forcing a SAD for every library repository creates excessive documentation noise and violates the physical deployment definition of a SAD.

To govern this, Scnehaux utilizes the **Aggregator-Component Pattern**:

1. **The Host Repository (The Master SAD)**: The primary repository responsible for compiling or deploying the final execution unit acts as the **Aggregator**. It must maintain the `Master SAD`. This artifact defines the aggregate physical topology, treating the remote SDKs and libraries as internal components within its container boundary.
2. **The Library/SDK Repositories (The Components)**: Repositories producing non-deployable libraries are **exempt** from requiring a SAD. They only require a **TDD** (Technical Design Document, `GDC-011`) to document their internal execution logic and API contracts.
3. **The Traceability Pointer**: To maintain the automated CI/CD Directed Acyclic Graph (DAG) and prevent the linter from flagging the library as an illegal orphan, the library repository must explicitly declare its governance inheritance in its linter configuration:
   ```yaml
   governance:
     master_sad: 'SAD-UIP-001-scnehaux-ui-platform'
   ```
   The Compliance Engine (`engine/cli.py`) will automatically validate that the referenced Master SAD exists in the Root Architecture Registry, and gracefully exempt the local repository from the SAD requirement.

### 2.3 The Schema Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-fitness-functions.md)**, the SAD specification is strictly governed by the following domain-specific linter schemas:

> [!WARNING]
>
> **DO NOT EDIT THIS TABLE MANUALLY.** This table is automatically generated from the JSON Schema (`schemas/sad.schema.json`). If you need to update a rule, modify the schema file and run: `python 06-fitness-function/generators/generate_rules_doc.py`

<!-- AUTO-GENERATED-SCHEMA:START -->

| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata Policies** | Metadata Policies | <ul><li>doc_meta (object)</li></ul> |
| **Metadata Policies** | Required Fields | <ul><li>id (string)</li><li>title (string)</li><li>governed_by (string &#124; array[string])</li><li>owner (string &#124; array[string])</li><li>version (string &#124; number)</li><li>status (string)</li><li>classification (string)</li><li>parent_pad (string &#124; array[string])</li><li>review_cycle_days (integer)</li><li>last_reviewed (string)</li></ul> |
| **Metadata Policies** | Allowed Statuses | <ul><li>proposed</li><li>approved</li><li>deprecated</li></ul> |
| **Metadata Policies** | Allowed Classifications | <ul><li>public</li><li>internal</li><li>restricted</li></ul> |
| **Content Quality Policies** | Context & Scope (Recommended) | <ul><li>Requirement</li><li>Assumption</li></ul> |
| **Content Quality Policies** | System Architecture (Recommended) | <ul><li>Container</li></ul> |
| **Content Quality Policies** | Runtime Flows (Recommended) | <ul><li>Sequence</li></ul> |
| **Content Quality Policies** | Integration (Recommended) | <ul><li>API</li><li>Event</li><li>Consumed</li><li>Published</li></ul> |
| **Content Quality Policies** | Security (Recommended) | <ul><li>Authentication</li><li>Authorization</li><li>Encryption</li><li>Secrets</li><li>Audit</li></ul> |
| **Content Quality Policies** | Deployment (Recommended) | <ul><li>Environment</li><li>Infrastructure</li></ul> |
| **Content Quality Policies** | NFR Derivatives (Recommended) | <ul><li>Latency</li><li>Throughput</li><li>RPS</li><li>Scalability</li><li>Caching</li><li>Observability</li><li>Telemetry</li><li>Alerting</li><li>Runbook</li><li>Circuit Breaker</li><li>Retry</li><li>Timeout</li><li>Resilience</li><li>Failover</li></ul> |

<!-- AUTO-GENERATED-SCHEMA:END -->

| Linter Component | File | Enforcement Logic |
| :-- | :-- | :-- |
| **JSON Schema** | `schemas/sad.schema.json` | Checks for `parent_pad`, enforces `Blast Radius` keywords under the Resilience section, and deployment topologies. |
| **Python Engine** | `engine/validators/domains/sad_validator.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications`.<br>**Domain Validation**: Enforces upward traceability by guaranteeing the presence of a valid `parent_pad` ID. |

**Engine Execution Mechanics**:

1. **Physical Containment Audit**: The linter will verify that SADs contain technology-specific information. Unlike PADs, SADs must specify the concrete database engines, cache stores, and container topologies.
2. **Hold Technology Enforcement**: The automated linter will execute a Hard Block (Exit 1) on any SAD artifact that implements a technology currently marked as `Hold` in its respective lifecycle phase.

### 2.3 Semantic Definitions

#### 2.3.1 Naming Conventions

- **Naming Convention**:
  - `[system-name].sad.md` (no suffix): Represents the **primary/core application** of the system.
  - `[system-name]-[suffix].sad.md`: Represents **specific applications, clients, or workers** (e.g., `iam-web`, `iam-worker`).
- **Ambiguity Rule**: If a system contains multiple SADs, **avoid using a suffix-less name**. It is highly recommended to use explicit suffixes for all containers (e.g., `iam-api.sad.md` and `iam-web.sad.md`) to prevent ambiguity.

#### 2.3.2 Taxonomy

SADs are **single, cohesive artifacts** (`[system-name].sad.md` or `[system-name]-[suffix].sad.md`). **The Cohesion Rule:** Splitting a SAD into separate micro-files (e.g., separating it into `security.md` and `operations.md`) is strictly prohibited. All system aspects must be fully encapsulated within the single canonical artifact's mandated sections to prevent drift.

- **Grouping Rule**: The implementation of a single logical PAD will often result in multiple physical SADs. To maintain cohesion, **all SADs fulfilling the same domain must be grouped together** within a single `[system-name]` directory. Do not create separate root folders for each container. _(Reminder: While they share a folder, each physical container must still be documented by exactly **one** SAD)._

#### 2.3.3 Directory Structure

They must utilize **Asset Container Folders** (`04-system/[system-name]/`), which act as an isolation boundary for the system's `.sad.md` files and supporting assets (e.g., deployment topology diagrams).

**Example Directory Structure:**

```text
scnehaux-architecture/
└── 04-system/                  # (Asset Container Folders)
    └── iam/                         # (System grouping folder)
        ├── iam-api.sad.md           # (Backend API SAD, explicit suffix)
        ├── iam-web.sad.md           # (Client application SAD)
        └── deployment-topology.png
```

#### 2.3.4 Metadata Schema Properties

Every SAD must begin with a YAML frontmatter block containing these fields:

```yaml
doc_meta:
  id: SAD-XXX # Unique software system ID
  title: [Application Title] # Descriptive title of the application
  owner: [System Team/Role] # Authoritative system owner
  version: 1.0.0 # Semantic versioning format
  status: approved # proposed | approved | deprecated
  classification: internal # public | internal | restricted
  parent_pad: PAD-XXX # Referencing the Parent Domain Capability PAD ID
  review_cycle_days: 180 # Review cycle period
  last_reviewed: YYYY-MM-DD # Last audit date
```

| Metadata Field      | Type    | Description / Purpose                                            |
| ------------------- | ------- | ---------------------------------------------------------------- |
| `id`                | String  | Unique identifier (e.g., `SAD-001`).                             |
| `title`             | String  | Descriptive title of the artifact.                               |
| `owner`             | String  | Lead Owner (e.g., System Architect).                             |
| `version`           | String  | Must comply with Semantic Versioning (e.g., 1.0.0).              |
| `status`            | Enum    | The current lifecycle state (must match Allowed Statuses below). |
| `classification`    | Enum    | The data sensitivity (must match Allowed Classifications below). |
| `parent_pad`        | String  | The parent PAD ID this system fulfills (e.g., `PAD-001`).        |
| `review_cycle_days` | Integer | The frequency in days for required review.                       |
| `last_reviewed`     | Date    | The date of the last formal review (YYYY-MM-DD).                 |

##### Allowed Lifecycle Statuses

| Status       | Meaning / Lifecycle Stage                                                          |
| ------------ | ---------------------------------------------------------------------------------- |
| `proposed`   | The software architecture is under design or peer review.                          |
| `approved`   | The software architecture is formalized and acts as the official design blueprint. |
| `deprecated` | The system is being phased out or has been replaced.                               |

##### Allowed Classifications

| Classification | Meaning / Data Sensitivity             |
| -------------- | -------------------------------------- |
| `public`       | Available to anyone.                   |
| `internal`     | Restricted to company employees.       |
| `restricted`   | Restricted to specific teams or roles. |

##### Semantic Versioning Classification

| Version | Trigger / Architectural Change |
| --- | --- |
| **Major (2.0.0)** | Overhauling the core framework, splitting the monolith, changing the persistence layer, or altering physical deployment topologies (e.g., VM to Kubernetes). |
| **Minor (1.1.0)** | Adding a new bounded context, exposing a new major API version, or integrating a new managed service (e.g., adding an S3 bucket or a Redis cache). |
| **Patch (1.0.1)** | Editorial updates, formatting, updating the `parent_pad` reference, fixing dead links. |

#### 2.3.5 Artifact Section

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
| --- | --- | --- |
| **Context & Scope** | Explain the technical "Why" behind the system boundary. | Must explicitly link to the governing domain capability PAD and outline objectives and system context. |
| **System Architecture** | Concrete C2 container diagrams detailing the physical technology stack. | Must illustrate all physical containers and boundaries. |
| **Runtime Flows** | Detail request lifecycles, asynchronous event publishing, and degradation paths. | Must contain sequence diagrams for critical operations. |
| **Data Architecture** | Document data classification, persistence layers, and caching strategies. | Must detail database engines, storage, and data sensitivity (PII/PHI). |
| **Integration** | Specify API endpoints, consumed services, and published events. | Must detail external/internal integrations and data contracts. |
| **Security** | Detail system-level threat mitigations, input validation, and secrets management. | Must address threat models, data encryption at rest/transit, and IAM boundaries. |
| **Resilience & Failure Modes** | Identify SPOFs, fallback strategies, and the exact **Blast Radius**. | Must document circuit breaker configurations and fallback states.<br>**Constraint**: Must contain the exact keyword `Blast Radius`. |
| **Observability & Operations** | Mandate specific SLIs, SLOs, alert thresholds, and distributed tracing spans. | Must define specific monitoring, logging, tracing, and runbook details. |
| **Deployment** | Document CI/CD pipelines, release environments, and scaling triggers. | Must contain deployment strategies and hardware/container limits. |
| **Trade-offs & Alternatives** | Document technical alternatives evaluated and their trade-offs. | Must list rejected technologies/designs and the rationale for rejection. |
| **Assumptions (Optional)** | Document external operational assumptions. | Must list business, external, or operational assumptions the design relies upon. |
| **Compatibility Strategy (Optional)** | Detail schema migration or API versioning compatibility rules. | Must outline API versioning or schema migration paths to avoid breaking changes. |

### 2.4 Lifecycle & Audit

All SAD artifacts must undergo a periodic review every `review_cycle_days` (default 180 days) to ensure structural integrity and relevance against the enterprise capability map.

**Qualitative Enforcement (Architecture Authority Audit)** _Note: Qualitative scoring is inherited from **[GDC-002 §2 — Scoring Criteria](./GDC-002-quality-rubric.md)**._

SADs have the following custom overriding audit metric:

1. **Blast Radius Analysis**: Under the Resilience section, every major failure mode must specify the _Blast Radius_ (e.g., "Single User Session", "Full Tenant Isolation", "Entire Platform Outage") to pass the review gate.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the Architecture Authority explicitly documents the compromises of this SAD Guideline:

1. **Manual Blast Radius Enforcement vs. Automated Chaos Engineering**
   - _Why rejected_: Fully automated Chaos Engineering requires significant infrastructure maturity and cannot run effectively during the design phase before code is written.
   - _The Trade-Off_: We rely on the architect's manual, theoretical calculation of the "Blast Radius" during the design phase. In exchange, we force engineers to confront and document failure boundaries proactively, preventing SPOFs from entering the codebase in the first place.
