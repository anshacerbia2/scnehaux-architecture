---
doc_meta:
  id: GDC-008
  title: Product Architecture Document (PAD) Guideline
  owner: Architecture Authority
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Product Architecture Document (PAD) Guideline

## 1. Context & Scope

PADs represent the C2 Domain Architecture layer of the C4 metamodel, defining the logical domain capabilities, bounded contexts, trust boundaries, and strategic positioning of a business domain (e.g., `identity`, `ui-platform`, `hris`, `finance`).

PADs establish the "What". They serve as the design-time single source of truth (SSOT) for domain-level contracts. A single logical domain capability (PAD) governs one or more physical software containers (SADs) in a strict 1-to-N mapping. They establish conceptual integration rules (such as trust boundaries and SLA targets) _before_ physical systems are built. While concrete API specifications are delegated downstream via Web Developer Portals, the PAD remains the stable, logical anchor.

### 1.1 Philosophy & Decision Horizon

**Decision question:** _"What capability does this product or platform own, where are its boundaries, and what does it promise — independent of how any system builds it?"_ A PAD is the domain charter tier: the logical plan, not the solution.

**Every product AND platform has exactly one PAD.** A platform is simply a product whose consumers are internal; it is not a separate document type.

**Position on the three governing dimensions:**

- **Stability / half-life — 10+ years (one-way door).** The longest-lived C2 artifact. To stay durable it must remain thin — capability, boundaries, contracts, NFR promises — and exclude implementation detail.
- **Abstraction — C2 logical.** Bounded contexts and contracts only; never containers, deployment, or technology choices (those are the SAD).
- **Ownership — one stream-aligned domain team.**

**Litmus test (PAD vs SAD):** _"Does this fact survive a complete technology rewrite?"_ If yes → PAD. If it would change when you swap technology or topology → SAD.

**Stability guardrail:** a PAD boundary is drawn by **bounded-context (capability) cohesion**, not by commercial or marketing packaging. Re-bundling products does not merge PADs — PADs follow domains, which keeps the 10-year horizon credible.

**Traceability:** a PAD fulfills one or more EAD capabilities (upward) and is realized by one or more SADs via `fulfilled_by` (downward, 1-to-N).

---

## 2. Policy Framework

### 2.1 Agnosticity & Stability

- **Agnosticity Policy**: PADs must remain technology-agnostic at the physical infrastructure level. They establish logical capabilities, trust boundaries, and conceptual integration policies (e.g., SLA targets). Concrete API specifications must be delegated to downstream Web Developer Portals, and physical container details belong in SADs.
- **Stability**: Because they govern logical rather than physical boundaries, PADs are designed to be highly stable. Future physical decompositions (e.g., splitting a monolithic HRIS backend into separate Payroll and Employee microservices) must require zero modification to the core domain contracts established within the PAD.

### 2.2 The Schema Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-fitness-functions.md)**, the PAD specification is strictly governed by the following domain-specific linter schemas:

> [!WARNING]
>
> **DO NOT EDIT THIS TABLE MANUALLY.** This table is automatically generated from the JSON Schema (`schemas/pad.schema.json`). If you need to update a rule, modify the schema file and run: `python 06-fitness-function/generators/generate_rules_doc.py`

<!-- AUTO-GENERATED-SCHEMA:START -->

| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata Policies** | Metadata Policies | <ul><li>doc_meta (object)</li></ul> |
| **Metadata Policies** | Required Fields | <ul><li>id (string)</li><li>title (string)</li><li>governed_by (string &#124; array[string])</li><li>owner (string &#124; array[string])</li><li>version (string &#124; number)</li><li>status (string)</li><li>classification (string)</li><li>realizes_capability (string &#124; array[string])</li><li>fulfilled_by (string &#124; array[string])</li><li>review_cycle_days (integer)</li><li>last_reviewed (string)</li></ul> |
| **Metadata Policies** | Allowed Statuses | <ul><li>proposed</li><li>approved</li><li>deprecated</li></ul> |
| **Metadata Policies** | Allowed Classifications | <ul><li>public</li><li>internal</li><li>restricted</li></ul> |
| **Content Quality Policies** | Trust & Data Boundaries (Recommended) | <ul><li>Identity</li></ul> |
| **Content Quality Policies** | Domain Model (Recommended) | <ul><li>Domain Event</li></ul> |
| **Content Quality Policies** | Integration Contracts (Recommended) | <ul><li>Event</li><li>Provider</li><li>External</li></ul> |
| **Content Quality Policies** | NFR Derivatives (Recommended) | <ul><li>SLA</li><li>SLO</li><li>Availability</li><li>Scalability</li><li>Compliance</li><li>Data Privacy</li><li>RTO</li><li>RPO</li><li>Budget</li></ul> |

<!-- AUTO-GENERATED-SCHEMA:END -->

| Linter Component | File | Enforcement Logic |
| :-- | :-- | :-- |
| **JSON Schema** | `schemas/pad.schema.json` | Enforces C1/C2 macro-topology boundaries and integration contracts. |
| **Python Engine** | `engine/validators/domains/pad_validator.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications`.<br>**Domain Validation**: Enforces that `fulfilled_by` exists and is a populated list of SAD IDs, guaranteeing C1 to C2 boundary composition. |

**Engine Execution Mechanics**:

1. **Logical Boundary Isolation**: The linter will flag any PAD that hardcodes physical server names, specific deployment ports, database index structures, or specific library versions.

### 2.3 Semantic Definitions

#### 2.3.1 Naming Conventions

The filename must strictly adhere to the `pad_pattern` regex: `^[a-z0-9-]+\.pad\.md$`.

#### 2.3.2 Taxonomy

PADs are **single, cohesive artifacts** (`[domain].pad.md`). **The Cohesion Rule:** Splitting a PAD into separate micro-files (e.g., separating it into `security.md` and `operations.md`) is strictly prohibited. All domain aspects must be fully encapsulated within the single canonical artifact's mandated sections to prevent drift.

#### 2.3.3 Directory Structure

They must utilize **Asset Container Folders** (`03-domain/[domain]/`), which act as an isolation boundary for the `.pad.md` file and its supporting assets (e.g., architecture diagrams, PlantUML files).

**Example Directory Structure:**

```text
scnehaux-architecture/
└── 03-domain/                     # (Asset Container Folders)
    └── ui-platform/
        ├── ui-platform.pad.md
        └── architecture-diagram.png
```

#### 2.3.4 Metadata Schema Properties

Every PAD must begin with a YAML frontmatter block containing these fields:

```yaml
doc_meta:
  id: PAD-XXX # Domain capability ID
  title: [Capability Title] # Descriptive title of the Domain Capability
  owner: [Domain Team/Role] # Authoritative team owner
  version: 1.0.0 # Semantic versioning format
  status: approved # proposed | approved | deprecated
  classification: public # public | internal | restricted
  fulfilled_by: # List of physical SAD IDs fulfilling this domain capability
    - SAD-XXX
  review_cycle_days: 180 # Review cycle period
  last_reviewed: YYYY-MM-DD # Last audit date
```

| Metadata Field | Type | Description / Purpose |
| --- | --- | --- |
| `id` | String | Unique identifier (e.g., `PAD-001`). |
| `title` | String | Descriptive title of the artifact. |
| `owner` | String | Lead Owner (e.g., Domain Architect). |
| `version` | String | Must comply with Semantic Versioning (e.g., 1.0.0). |
| `status` | Enum | The current lifecycle state (must match Allowed Statuses below). |
| `classification` | Enum | The data sensitivity (must match Allowed Classifications below). |
| `fulfilled_by` | List[String] | Array of child SAD IDs that fulfill this domain architecture (e.g., `[SAD-AUTH-01]`). |
| `review_cycle_days` | Integer | The frequency in days for required review. |
| `last_reviewed` | Date | The date of the last formal review (YYYY-MM-DD). |

##### Allowed Lifecycle Statuses

| Status       | Meaning / Lifecycle Stage                                                 |
| ------------ | ------------------------------------------------------------------------- |
| `proposed`   | The domain architecture is under design or Architecture Authority review. |
| `approved`   | The domain architecture is formalized and acts as the official contract.  |
| `deprecated` | The domain capability is being phased out or has been replaced.           |

##### Allowed Classifications

| Classification | Meaning / Data Sensitivity             |
| -------------- | -------------------------------------- |
| `public`       | Available to anyone.                   |
| `internal`     | Restricted to company employees.       |
| `restricted`   | Restricted to specific teams or roles. |

##### Semantic Versioning Classification

| Version | Trigger / Architectural Change |
| --- | --- |
| **Major (2.0.0)** | Redesigning the boundary, shifting significant logical responsibilities to another domain, or breaking integration contracts (e.g., API rewrites). |
| **Minor (1.1.0)** | Adding a new subsystem or capability without breaking existing integrations. |
| **Patch (1.0.1)** | Editorial updates, formatting, mapping a new `fulfilled_by` SAD ID, fixing dead links. |

#### 2.3.5 Artifact Section

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
| --- | --- | --- |
| **Context & Scope** | Define the boundaries, goals, non-goals, and stakeholders of this capability. | Must explicitly outline the purpose and target audience. |
| **Business Capability** | Define the business value, bounded context, and macro-level features that define this domain capability. Focus on logical boundaries. | Must remain technology-agnostic. Focus on logical boundaries rather than libraries or infrastructure. |
| **Domain Model** | Establish the bounded contexts, context mapping, and primary domain events. | Must define the conceptual models and context mappings. |
| **Trust & Data Boundaries** | Map the isolation levels, identity propagation, compliance, and tenant separation models. | Must detail how user contexts traverse boundaries and state compliance levels. |
| **Integration Contracts** | Specify strict API boundaries, event publishing, and external dependencies. | Must define retry envelopes, API endpoints, and event payloads. |
| **Capability NFR Targets** | Explicit, quantifiable Non-Functional Requirements (NFR) targets. | Must quantify metrics (e.g., "99.99% Availability", "Scalability up to 5000 TPS"). |
| **Ownership & Realizing Systems** | Map the logical capability to the physical systems (SADs) that fulfill it. | Must explicitly document the authoritative owner and list the `fulfilled_by` physical systems. |
| **Assumptions _(Optional)_** | Document any external dependencies or business assumptions. | Must list business, external, or operational assumptions the design relies upon. |
| **Alternatives Considered _(Optional)_** | Document technical alternatives evaluated and their trade-offs. | Must list rejected technologies/designs and the rationale for rejection. |

### 2.4 Lifecycle & Audit

As the Single Source of Truth (SSOT) for Product Architecture Documents (PAD), the PAD represents highly stable domain capabilities. They must undergo a periodic review every `review_cycle_days` (default 180 days) to ensure structural integrity and relevance against the enterprise capability map.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the Architecture Authority explicitly documents the compromises of this PAD Guideline:

1. **C1/C2 Separation (PAD vs. SAD) vs. Unified Architecture Artifacts**
   - _Why rejected_: A unified artifact containing both logical capabilities and physical servers rapidly decays. When physical servers scale or database engines change, the logical boundary artifact requires constant, unnecessary updates.
   - _The Trade-Off_: We accept the cognitive overhead of maintaining two separate but linked artifacts (PAD for logical, SAD for physical). In exchange, we gain highly stable logical contracts (PADs) that do not break when physical infrastructure topologies mutate.
