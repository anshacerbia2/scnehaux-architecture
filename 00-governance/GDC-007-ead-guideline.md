---
doc_meta:
  id: GDC-007
  title: Enterprise Architecture Document (EAD) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Enterprise Architecture Document (EAD) Guideline

## 1. Context & Scope

EADs represent the C1 global context layer of the C4 metamodel, defining the global "City Map" and enterprise-wide directives.

EADs establish the "Why". They dictate the Business Drivers, Enterprise Principles, and the "North Star" cross-domain standardization principles that govern all downstream documentation, including Enterprise Standards (STD), Platform Architecture Documents (PAD), System Architecture Documents (SAD), Architecture Decision Records (ADR), and Technical Design Documents (TDD).

### 1.1 Philosophy & Decision Horizon

**Decision question:** *"What must the enterprise become, and under what principles?"* An EAD is the enterprise north-star (the central-planning tier): it sets direction, never a system design.

**Position on the three governing dimensions:**

- **Stability / half-life — Permanent (strategic horizon).** EADs change only when enterprise strategy itself shifts; they are the slowest-moving artifacts in the ecosystem. Volatile detail must not live here.
- **Abstraction — C1, enterprise-wide and implementation-agnostic.** Decomposed per TOGAF BDAT domain (Business / Data / Application / Technology), one file each.
- **Ownership — Architecture Review Board (enterprise).**

**Litmus test (EAD vs PAD/SAD):** *"Is this statement enterprise-wide AND independent of any specific system?"* If it names a concrete system, API, or topology, it has leaked down into a PAD or SAD. `Data Flow Landscape` and `Application Interaction` stay at the macro (cross-domain) level.

**Boundary discipline:** an EAD states **principles and direction**; the enforceable **rules** that implement them live in the STD layer. The `Technology Standards` section therefore references the STD catalog instead of duplicating it (single source of truth), and `Organization Model` expresses durable team-topology principles rather than a volatile org chart.

**Traceability:** the `Business Capability Map` (EAD-001) is the root that every PAD capability traces upward to.

---

## 2. Policy Framework

### 2.1 Agnosticity Rules

EADs must remain conceptually agnostic (e.g., Business, Data, Application layers) and at a high level of abstraction. Strict SLA (Service Level Agreement) metrics (e.g., `P95 <= 200ms` or `>= 95%` availability) are mandated, but implementation-specific details are prohibited. The sole exception is the Technology Architecture domain (`EAD-004`), which must explicitly define the enterprise technology portfolio.

### 2.2 The Ruleset Architecture

In addition to the global structural enforcement defined in **[GDC-001](./GDC-001-compliance-engine.md)**, the EAD specification is strictly governed by the following domain-specific linter rules.

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (the Single Source of Truth).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`governed_by`</li><li>`owner`</li><li>`version`</li><li>`status`</li><li>`classification`</li><li>`review_cycle_days`</li><li>`last_reviewed`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`proposed`</li><li>`approved`</li><li>`deprecated`</li></ul> |
| **Metadata** | Allowed Classifications | <ul><li>`public`</li><li>`internal`</li><li>`restricted`</li></ul> |
| **Structure** | Required Sections | **EAD-001**: <ul><li>`Vision`</li><li>`Mission`</li><li>`Strategic Objectives`</li><li>`Business Capability Map`</li><li>`Value Stream`</li><li>`Operating Model`</li><li>`Team Topology Principles`</li><li>`Stakeholder`</li></ul><br>**EAD-002**: <ul><li>`Enterprise Data Principles`</li><li>`Master Data`</li><li>`Data Ownership`</li><li>`Data Classification`</li><li>`Data Governance`</li><li>`Data Lifecycle`</li><li>`Data Flow Landscape`</li></ul><br>**EAD-003**: <ul><li>`Application Portfolio`</li><li>`Application Interaction`</li><li>`Application Classification`</li><li>`Build vs Buy`</li><li>`Enterprise Integration Strategy`</li></ul><br>**EAD-004**: <ul><li>`Cloud Strategy`</li><li>`Security Principles`</li><li>`Observability Principles`</li><li>`Platform Strategy`</li><li>`Technology Principles`</li><li>`Technology Radar`</li></ul> |
<!-- AUTO-GENERATED-RULES:END -->

### 2.3 Semantic Definitions

#### 2.3.1 Naming Conventions

The filename must strictly adhere to the `ead_pattern` regex: `^EAD-\d{3}-[a-z0-9-]+\.md$`.

#### 2.3.2 Taxonomy

EADs follow a strict taxonomy mapped to the **4 Core TOGAF Domains**:
  1. **Business Architecture (`EAD-001`)**: Establishes capability-centric blueprints, mapping domain boundaries strictly to business capabilities and enterprise principles.
  2. **Data Architecture (`EAD-002`)**: Governs system-of-record boundaries, database engines, persistence guidelines, data sovereignty, and sharing constraints.
  3. **Application Architecture (`EAD-003`)**: Establishes mTLS mandates, gateway policies, integration patterns, security boundaries, and UI platform composition patterns.
  4. **Technology Architecture (`EAD-004`)**: Defines the paved road for languages (e.g., Go and Node.js dual core), bundlers, cloud-native execution runtimes, exception paths, and evolutionary strategies.

EAD documents must remain flat or layered by TOGAF (Business, Data, Application, Tech) within the `01-enterprise/` directory. Domain-Driven Design (DDD) subfolders are strictly prohibited to preserve the holistic enterprise view and prevent domain silos at the C1 level.

#### 2.3.3 Directory Structure

**Example Directory Structure:**
```text
scnehaux-architecture/
└── 01-enterprise/                                  # (Flat / Holistic View)
    ├── EAD-001-business-architecture.md
    ├── EAD-002-data-architecture.md
    ├── EAD-003-application-architecture.md
    └── EAD-004-technology-architecture.md
```

#### 2.3.4 Metadata Schema Properties

Every EAD document must include a YAML frontmatter block containing metadata such as `id`, `title`, `owner`, `version`, `status`, and `classification`.

##### Allowed Lifecycle Statuses

| Status | Meaning / Lifecycle Stage |
|---|---|
| `proposed` | Under review or initial draft state. |
| `approved` | Formalized and active. |
| `deprecated` | Phased out and no longer applicable. |

##### Allowed Classifications

| Classification | Meaning / Data Sensitivity |
|---|---|
| `public` | Available to anyone. |
| `internal` | Restricted to company employees. |
| `restricted` | Restricted to specific teams or roles. |

##### Semantic Versioning Classification

| Version | Trigger / Architectural Change |
|---|---|
| **Major (2.0.0)** | Splitting, merging, or fundamentally redefining core strategic business domains. |
| **Minor (1.1.0)** | Adding a new enterprise capability or business domain without breaking existing ones. |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, fixing dead links. |

#### 2.3.5 Document Section

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Objective | Requirement |
|---|---|---|
| **Context & Business Drivers** | Explain the organizational "Why" behind the enterprise standard, mapping it to concrete business outcomes, constraints, and strategic goals. | Must explicitly link technical strategy to business capabilities. Detailed sections must trace constraints to external regulatory compliance (e.g., GDPR, SOC2) and internal business outcomes. |
| **Enterprise Principles** | Establish the non-negotiable, immutable rules that guide all downstream architectural designs. | Principles must be stated as rules and must adhere to a strict three-part schema:<br>- **Statement**: A clear, unambiguous description of the rule.<br>- **Rationale**: The business or engineering reason for the principle.<br>- **Implication**: The direct downstream development and operational requirements. |
| **Strategic Architecture** | Provide macro-level capability models, domain boundaries, and high-level structural diagrams. | Must outline the primary partitions or capabilities of the enterprise, map them to logical bounded contexts, and define their interactions. Visual C1/C2 diagrams or choreography models (e.g., Mermaid sequence diagrams) mapping domain/capability boundaries are mandatory. |
| **Cross-Cutting Standards** | Mandate rules applicable to all domains and platforms (e.g., universal API error formats, central logging specifications, data retention baselines). | Rules must be actionable, prescriptive, and testable by automated fitness functions. All SLA and NFR baselines must be quantified (e.g., latency targets, availability, database recovery bounds). |
| **Decision Log** | Record major strategic pivots, accepted trade-offs, and their enterprise-wide ramifications. | Each log entry must list the date, decision maker, and a reference to the related global or domain ADR (e.g. `ADR-GLB-001`, `ADR-UIP-TKN-001`). |


### 2.4 Lifecycle & Audit

All EAD documents are subject to a maximum `review_cycle_days` to prevent staleness. Enterprise level directives typically carry a 180-day review cycle. When an EAD expires, the pipeline will flag it for architectural audit.

---

## 3. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this EAD Guideline:

1. **Markdown Documents vs. TOGAF ArchiMate / EA Tools**
   - *Why rejected*: Traditional EA tools (e.g., Sparx Enterprise Architect) create a massive disconnect between Enterprise Architects and software engineers, locking capability models in proprietary formats.
   - *The Trade-Off*: We sacrifice strict formal modeling languages (like ArchiMate) and auto-generated dependency matrices. In exchange, we force Enterprise Architecture to live in the same Git repositories as the code, ensuring visibility, democratized access, and CI/CD validation.
