---
doc_meta:
  id: GDC-000
  title: Documentation Governance Policy
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Documentation Governance Policy (The Constitution)

## 1. Context & Scope

This Constitution is the supreme law of the Scnehaux engineering ecosystem.

### 1.1 Core Philosophy

This ecosystem operates on a radical departure from traditional Enterprise Architecture. We do not write documentation, we engineer **Knowledge as Infrastructure**. The framework is governed by seven absolute philosophical pillars:

1. **Predictability over Cleverness**: Architecture must be deterministic. We reject "clever" hacks, magic abstractions, and implicit system behaviors in favor of boring, predictable designs.
2. **Explicit Contracts**: Interfaces, trust boundaries, and failure modes must be explicitly quantified. Hand-wavy abstractions are prohibited.
3. **Fractal Abstraction (Logical vs. Physical Isolation)**: We strictly decouple "What we do" (Business Capabilities/PAD) from "How we do it" (Physical Deployments/SAD). This ensures that physical engineering refactors (e.g., splitting a monolith) do not pollute strategic business blueprints.
4. **Docs-as-Code (Immutable Knowledge)**: Architecture documentation is treated identically to source code. It lives in Git, requires Pull Requests, undergoes peer review, and is validated by CI/CD pipelines. Word documents and static wiki pages are prohibited.
5. **Zero Waste (The Deletion Mandate)**: Redundancy breeds entropy. We enforce a strict Single Source of Truth (SSOT). Execution-level documents that rot quickly (e.g., TDDs) must be aggressively deleted once built. We rely on Git history for forensic audits rather than accumulating dead archives.
6. **Policy-as-Code & Deterministic Enforcement**: A rule without a validation mechanism is merely a suggestion. We enforce compliance through two strict gates: structural integrity is mathematically automated via the Linter (`GDC-001`) to achieve true **Policy-as-Code**, while complex architectural trade-offs are evaluated by humans using a quantifiable Quality Rubric (`GDC-002`).
7. **Circular Governance (Metaprogramming)**: The ecosystem binds itself. The laws that govern the systems must also govern the rulebooks themselves. The Constitution and its Guidelines are audited by the exact same compliance engine they mandate.

### 1.2 The Dual-Axis Enforcement Model

To execute this philosophy, the ecosystem operates on a strict **Circular Governance Model** (Checks & Balances) rather than a top-down pyramid. No single document, including this Constitution, possesses absolute immunity.

It establishes a comprehensive framework that regulates two distinct dimensions of quality, executed across two layers of enforcement:

#### The Two Dimensions of Quality
1. **Governance Quality (The Framework)**: Laws governing the lifecycle, taxonomy, structural integrity, and single source of truth of the documentation itself.
2. **Architecture Quality (The Software Ecosystem)**: Design principles, constraints, and trade-offs governing the actual software systems (e.g., IAM, HCM, ERP) described within those documents.

#### The Two Layers of Enforcement
To ensure extreme scalability, this Constitution logically decentralizes the enforcement of both dimensions into specialized bodies:
- **Automated Enforcement (The Engine)**: The **[GDC-001 - Compliance Engine](./GDC-001-compliance-engine.md)** acts as the absolute first line of defense. It automates both *Governance Quality* (e.g., metadata schema, taxonomy) and *Architecture Quality* (e.g., mandatory design sections, banning ambiguous vocabulary).
- **Human Enforcement (The Rubric)**: The **[GDC-002 - Quality Rubric](./GDC-002-quality-rubric.md)** acts as the final qualitative gate. It provides human reviewers with deterministic rubrics to evaluate complex architectural trade-offs that machines cannot parse (e.g., assessing true Zero-Trust boundaries).

While this document delegates the execution of enforcement to `GDC-001` and `GDC-002`, its own authority over the fundamental laws of **Governance Quality** spans the entire documentation ecosystem (across both the root architecture repository and downstream project repositories). 

> [!IMPORTANT]
> **The Circular Dependency of Trust**: To guarantee absolute integrity, the ecosystem binds itself. The Constitution (`GDC-000`) dictates that all documents must be linted. However, the Constitution itself must pass the Linter (`GDC-001`), which enforces the layout rules defined in the GDC Guideline (`GDC-006`). If the Constitution violates its own laws, the CI/CD pipeline immediately blocks it.

Ephemeral assets (e.g., whiteboard sketches) and code-level documentation (e.g., inline comments, auto-generated Swagger specs) are completely out of scope for this framework, as they are governed by independent code-level fitness functions (see [GDC-005 - Fitness Functions](./GDC-005-fitness-functions.md)).

### 1.3 The Fractal Boundary (Logical vs. Physical Decentralization)

The boundary between Centralized Policy and Federated Execution operates simultaneously across two dimensions: **Logically** (via Separation of Concerns within Governance) and **Physically** (across Git repositories for Artifacts).

#### 1. Logical Decentralization (The Governance Federation)
Even though all overarching policies physically reside in the root repository, they are *logically* decentralized to prevent `GDC-000` from becoming a bloated bottleneck. The ecosystem operates on a federated model:

- **The Constitution (`GDC-000`)**: Owns the supreme laws of *Governance Quality* that bind the entire repository together.
- **The Enforcement Layers (e.g., Linter and Rubric)**: Execute both Automated and Human validation to enforce the Constitution across the ecosystem.
- **The Decentralized Context Guidelines (e.g., EAD, PAD, SAD Guidelines)**: Define the specific structural schemas, metadata properties, and *Architecture Quality* expectations for each distinct layer.

*(See **Section 3.2: The Governance Ecosystem** for the complete directory of these documents).*

~~~mermaid
graph TD
   subgraph Dimensions ["The Dimensions of Quality"]
      GovQuality["GDC-000 (Governance Quality)"]
      ArchQuality["Context Guidelines (Architecture Quality)<br>e.g., GDC-012, GDC-010"]
   end

   subgraph Enforcement ["The Layers of Enforcement"]
      Linter["GDC-001 (Automated Engine)"]
      Rubric["GDC-002 (Human Rubric)"]
   end

   GovQuality -->|Delegates automation to| Linter
   ArchQuality -->|Statically analyzed by| Linter
   ArchQuality -->|Qualitatively judged by| Rubric

   style GovQuality fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
   style Linter fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
   style Rubric fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
~~~

#### 2. Physical Decentralization (The Execution Boundary)
This governs where the actual architecture description files physically reside to balance strategic consistency with engineering velocity:
- **Strictly Centralized (The Root Repo)**: Macro-level blueprints (EAD, PAD, SAD) that define cross-system integration and physical container topologies.
- **Strictly Localized (Downstream Repos)**: Downstream engineering teams author component-level designs (TDD) that adhere to central policies. These live directly in their specific application repositories (e.g., `scnehaux-iam`).
- **Context-Dependent (The Blast Radius Split)**: Decisions (ADR) and Standards (STD) can be centralized or localized. If a decision affects multiple domains, it lives centrally. If a standard only applies to one microservice, it lives locally.

~~~mermaid
graph TD
   subgraph Decentralized ["Decentralized Scope (Micro & Local)"]
      ProjGo["Project Repo (e.g., scnehaux-iam)"]
      ProjGo -->|Component Designs| LocalTDD["TDD (Local Blueprints)"]
      ProjGo -->|Local Decisions| ProjADR["ADR (Local/Component)"]
      ProjGo -->|Local Standards| ProjSTD["STD (Local/Component)"]
   end

   subgraph Centralized ["Centralized Scope (Macro & Global)"]
      Root["Root Architecture Repo (scnehaux-architecture)"]
      Root -->|Governance Engine| CentralGDC["GDC (The Constitution)"]
      Root -->|Macro Blueprints| CentralDocs["EAD, PAD, SAD"]
      Root -->|Strategic Decisions| GlobalADR["ADR (Global/Domain)"]
      Root -->|Global Guardrails| GlobalSTD["STD (Global/Domain)"]
   end

   style Root fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
   style ProjGo fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
~~~

### 1.3 Repository Taxonomies & Authority

Based on the physical federation above, each repository tier operates under a strict structural taxonomy:

**1. Enterprise Level (Root Architecture Repo)**:
   - **Authority**: Macro-level architectural guardrails, split into Global (cross-cutting) and Domain-Bounded contexts.
   - **Focus**: Governance rules (GDC), strategic blueprints (EAD, PAD, SAD), and global/domain policies (STD, ADR).
   - **Taxonomy Strategy**: Top-level directories are grouped by **Artifact Type**, and internally subdivided by **Domain-Driven boundaries** (e.g., mapping documents into domains like `ui-platform` or `iam`).

     **Example Enterprise Directory Structure:**

     ```text
     scnehaux-architecture/
     ├── 00-governance/                   # (The Supreme Rules)
     │   └── GDC-000-governance-policy.md
     │
     ├── 01-enterprise/                   # (EADs - Holistic View)
     │   └── EAD-001-value-stream.md
     │
     ├── 02-platform/                     # (PADs - Domain-Driven)
     │   └── ui-platform/
     │       ├── ui-platform.pad.md
     │       └── platform-diagram.png
     │
     ├── 03-software/                     # (SADs - Domain-Driven)
     │   └── iam/
     │       ├── scnehaux-iam.sad.md
     │       └── deployment-topology.png
     │
     ├── 04-standards/                    # (STDs - Domain-Driven)
     │   ├── _global/
     │   │   └── STD-GLB-001-api-design.md
     │   └── ui-platform/
     │       └── STD-UIP-001-design-tokens.md
     │
     └── 05-decisions/                    # (ADRs - Domain-Driven)
         ├── _global/
         │   └── ADR-GLB-001-modular-monolith.md
         └── iam/
             └── ADR-IAM-001-use-keycloak.md
     ```

**2. Project/Local Level (Project Repo)**:
   - **Authority**: Local Contextualization and Code execution (C3/C4 micro-level).
   - **Focus**: Detailed component designs (TDD), local standards (Local STD), and local decisions (Local ADR).
   - **Taxonomy Strategy**: Architecture artifacts are grouped under `docs/architecture/` and sub-divided by Artifact Type. Internal structure mirrors the repository's **Module-Driven boundaries**.

     **Example Local Project Directory Structure:**

     ```text
     scnehaux-iam/                      # (Project Repository)
     ├── docs/                          # (Root)
     │   ├── 01-standards/              # (Local STDs - Level 2)
     │   │   └── core-auth/             # (Level 3 - Max Depth)
     │   │       └── STD-IAM-AUTH-001-token-expiry.md
     │   │
     │   ├── 02-designs/                # (Local TDDs - Level 2)
     │   │   └── login-module/          # (Level 3 - Max Depth)
     │   │       ├── TDD-IAM-LOG-001-oauth-flow.md
     │   │       └── sequence-diagram.png
     │   │
     │   ├── 03-decisions/              # (Local ADRs - Level 2)
     │   │   └── database/              # (Level 3 - Max Depth)
     │   │       └── ADR-IAM-DB-001-use-redis.md
     │   │
     │   └── linting-rules.yaml         # (Local Linting Rules overlay)
     │
     └── src/                           # (Source Code matching the modules)
         ├── core-auth/
         └── login/
     
### 1.4 The Hybrid Metamodel (C4 + TOGAF + arc42 + AWS WAF)

To balance strategic business alignment with engineering execution, Scnehaux rejects rigid compliance with any single architectural framework. Instead, we **adopt and synthesize the core concepts** from industry-leading frameworks to build our own customized, *Docs-as-Code* ecosystem. We do not use their proprietary tools; we solely adopt their mental models:

- **C4 Model**: Dictates folder navigation and system zoom levels.

  | Level    | C4 Name           | Scnehaux Scope                                 | Location                                    |
  | :------- | :---------------- | :--------------------------------------------- | :------------------------------------------ |
  | **Meta** | **Cross-Cutting** | **[GDC](GDC-006-gdc-guideline.md)**, **[ADR](GDC-011-adr-guideline.md)**, **[STD](GDC-008-std-guideline.md)** (Governance & Rules) | Root Repo (`00`, `02`, `05`)                |
  | **C1**   | **Context**       | **[EAD](GDC-007-ead-guideline.md)** (Enterprise Strategy)                  | Root Repo (`01-enterprise`)                 |
  | **C2**   | **Container**     | **[PAD](GDC-009-pad-guideline.md)** (Domain) & **[SAD](GDC-010-sad-guideline.md)** (System)            | Root Repo (`03-platform`, `04-application`) |
  | **C3**   | **Component**     | **[TDD](GDC-012-tdd-guideline.md)** (Detailed Design)                      | **Specific Project Repository**             |
  | **C4**   | **Code**          | Implementation & Source                        | **Specific Project Repository**             |

- **TOGAF**: We adopt its concept of the 4 Enterprise Architecture Domains (Business, Data, Application, and Technology) to logically structure our `01-enterprise` and `02-standards` layers.
- **arc42 (Adapted)**: Supplies qualitative structural integrity concepts for document contents. We synthesize its philosophy but reject its single monolithic template in favor of our distributed EAD/PAD/SAD/TDD templates.
- **AWS Well-Architected Framework**: We adopt its core concept of the 6 pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability) as the foundational metric in our Quality Rubric (**[GDC-002](GDC-002-quality-rubric.md)**) to evaluate architectural trade-offs, enforcing strict failure mode analysis and blast radius containment.

#### 1.4.1 The C2 Schism: Logical (PAD) vs Physical (SAD)

The most critical departure from standard C4 in the Scnehaux Metamodel is the bifurcation of the C2 (Container) layer. We strictly separate logical business capabilities from physical deployment units to prevent organizational changes from corrupting the architecture description.

1. **PAD (Business Capability & Domain Architecture)**: Defines the "Position & Connectivity". It explains **what** the capability achieves from a business perspective, **why** it exists within the ecosystem, its logical domain boundaries, and its integration contracts with other domains. 
2. **SAD (Physical System Architecture)**: Defines the "Internal Reality". It explains **how** a specific software system is built, its internal components, deployment topology, and operational behavior.

| Attribute        | PAD (Platform Architecture Document)                              | SAD (Software Architecture Document)                      |
| :--------------- | :---------------------------------------------------------------- | :-------------------------------------------------------- |
| **Focus**        | **Business Capability (Logical Domain)**                          | **Physical Containment (Deployable Unit)**                |
| **Abstraction**  | C2 - Business Capability, Integration & Ecosystem Positioning     | C2 - Solution Architecture & Container Topology           |
| **Naming**       | **Domain-Oriented** (`[domain].pad.md`)                           | **Deployable-Oriented** (`[repository-name].sad.md`)      |

---

## 2. Policy Framework

To operate at true enterprise scale, all Scnehaux architecture artifacts must inherently adhere to strict laws governing their lifecycle, existence, and structure.

### 2.1 The Existential Maxims (Lifecycle & Authority)

This subsection defines the absolute laws governing the existence, validation, and lifespan of an architectural document:

1. **The Single Source of Truth (SSOT)**: No orphan concepts and no duplication. If multiple documents cover overlapping architectural concepts, exactly one document must be designated as the authoritative source of truth. All others may only link to it, never redefine it.
2. **Eat Our Own Dog Food (Self-Validating Governance)**: The governance framework must subject itself to the exact same rigorous validation criteria it imposes on downstream systems. Architecture rules are only valid if the documents defining them pass their own CI linters, schemas, and trade-off rubrics. Do not create an engineering mandate that the Governance Board itself cannot or will not comply with.
3. **The Documentation Density Law (The Deletion Mandate)**: *A document's thickness and maintenance cost must be inversely proportional to its speed of change and directly proportional to its blast radius.* Macro-level artifacts that govern strategic boundaries are permanent. Conversely, execution-level artifacts (like component designs) rot quickly. To prevent this, they are subjected to aggressive physical deletion lifecycles.
4. **The Search-Space Purity Law (Aggressive Deletion)**: Dead documents pollute search results. If a system or domain is decommissioned, its living documents (PADs/SADs) MUST be aggressively deleted from the active workspace. We rely entirely on Git History for forensic audits. Only *Immutable Decisions* (ADRs) are exempt from deletion and may be relocated to a `historical/` archive to preserve the unbroken narrative of enterprise choices.
5. **Explicit Ownership**: To prevent architectural drift, every architectural artifact must declare a clear, singular `owner` (e.g., Principal Architect, Core Auth Squad) in its metadata header. Governance without clear ownership is void.

### 2.2 Logical Abstraction & Traceability
Documents must strictly align with their C4-assigned boundary without leaking execution details across layers.

#### 2.2.1 The 1-to-N Mapping Rule
A single Business Capability (PAD) is fulfilled by multiple physical software systems (SADs). To prevent logical boundaries from being contaminated by deployment-specific execution mechanics, **every distinct deployable unit must have its own SAD**, even if they serve the same business capability. Furthermore, every SAD **MUST** strictly trace back to a parent PAD.

~~~mermaid
graph TD
  PAD["identity.pad.md (C2 Business Capability)"]
  PAD --> SAD1["scnehaux-iam.sad.md (Core Auth & Session)"]
  PAD --> SAD2["scnehaux-directory.sad.md (User Cache Service)"]
  PAD --> SAD3["scnehaux-kms-rotator.sad.md (Key Rotator Utility)"]

  style PAD fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
  style SAD1 fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff
  style SAD2 fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff
  style SAD3 fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff
~~~

- **Resilience to Refactoring**: Splitting a backend monolith (e.g., `scnehaux-iam` into separate microservices) requires zero changes to the PAD since the logical integration contracts, trust boundaries, and business capabilities remain identical.
- **Leakage Prevention**: Separating these layers prevents strategic capability documents from being polluted with operational details.

#### 2.2.2 The C4 Traceability Chain

- **C1 Enterprise documents (EAD)** must focus exclusively on macro-level strategic capabilities, enterprise policies, and value streams. They must not contain container topologies, system integration schemas, or API endpoints.
- **Engineering Standards (STD)** serve as cross-cutting guardrails. They define mandatory engineering baselines, compliance rules, and paved roads that apply across all C4 levels.
- **C2 Capability and System documents (PAD/SAD)** must define logical domain capabilities and physical container structures. They must not contain C3 component-level implementation mechanics, database index names, or low-level class/function signatures.
- **C3 Component documents (TDD)** must define concrete component blueprints, API schemas, and entity relationships. They must not override platform-wide integration contracts, trust boundaries, or global protocols established in C2 documents.

Every technical decision must be traceable back to its root cause in the architecture. The **Hierarchy of Authority** (Chain of Command) operates top-down:

1. **EAD & STD (The Supreme Law)**: No downstream document may violate enterprise strategy or global engineering policies.
2. **PAD (The Domain Contract)**: Must comply with EAD/STD. Establishes the logical constraints that downstream physical systems must follow.
3. **SAD (The System Reality)**: Must comply with its parent PAD.
4. **TDD (The Execution Blueprint)**: Must comply with its parent SAD.
5. **ADR (The Orthogonal Ledger)**: Serves a dual-purpose. It either *establishes* the baseline for EAD/STD, or acts as an approved *Exception Waiver* that allows a PAD/SAD to legally break the chain of command.

~~~mermaid
---
title: The C4 Traceability Chain & Exception Workflow
---
graph TD
    subgraph Supreme ["Level 1: Enterprise Strategy & Policy"]
        EAD["EAD (Enterprise Architecture)"]
        STD["STD (Global Standards)"]
    end

    subgraph Domain ["Level 2: Logical Boundaries"]
        PAD["PAD (Platform Architecture)"]
    end

    subgraph System ["Level 3: Physical Implementation"]
        SAD["SAD (Software Architecture)"]
    end

    subgraph Execution ["Level 4: Component Design"]
        TDD["TDD (Technical Design)"]
    end
    
    ADR{{"ADR (Decision Record)"}}

    EAD -->|Establishes| STD
    EAD -->|Dictates| PAD
    STD -->|Constrains| PAD
    PAD -->|Governs| SAD
    STD -->|Constrains| SAD
    SAD -->|Dictates| TDD
    
    ADR -.->|Baseline or Waiver| EAD
    ADR -.->|Baseline or Waiver| STD
    ADR -.->|Baseline or Waiver| PAD
    ADR -.->|Baseline or Waiver| SAD
    ADR -.->|Baseline or Waiver| TDD

    style EAD fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style STD fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style PAD fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style SAD fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#fff
    style TDD fill:#4a5568,stroke:#718096,stroke-width:2px,color:#fff
    style ADR fill:#9b2c2c,stroke:#fc8181,stroke-width:2px,color:#fff,stroke-dasharray: 5 5
~~~

A downstream document (e.g., a SAD) that contradicts an upstream document (e.g., an EAD or PAD) without an approved **ADR** (Architecture Decision Record) granting an explicit exception is a strict governance violation.



### 2.3 The Mutability Matrix
To prevent documentation rot while preserving decision traceability, all documents must adhere to this Mutability Matrix:

| Doc Type | C4 Level       | Mutability           | Mutability Rule                                                                                                                                                                |
| :------- | :------------- | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[EAD](GDC-007-ead-guideline.md)**  | C1 (Context)   | **Mutable (Living)** | Represents the active enterprise architecture blueprint. Updated directly when strategic TOGAF domains or capabilities evolve.                                                 |
| **[STD](GDC-008-std-guideline.md)**  | Meta           | **Mutable (Living)** | Represents current active rules. Modified directly and versioned via SemVer when rules evolve. Major changes require an authorizing ADR.                                       |
| **[PAD](GDC-009-pad-guideline.md)**  | C2 (Domain)    | **Mutable (Living)** | Represents active domain capability boundaries and trust contracts. Updated directly when capabilities are added or when the `fulfilled_by` SAD list changes.                  |
| **[SAD](GDC-010-sad-guideline.md)**  | C2 (System)    | **Mutable (Living)** | Represents active physical system topologies. Updated directly when microservices, containers, or deployment infrastructures are modified.                                     |
| **[ADR](GDC-011-adr-guideline.md)**  | Meta           | **Immutable**        | Represents a point-in-time decision. Once accepted, it must never be modified (except for status updates). Changes require a new replacing ADR.                                |
| **[TDD](GDC-012-tdd-guideline.md)**  | C3 (Component) | **Hybrid**           | Component designs. Class A (strategic) is archived. Class B (feature) is folded into the SAD and deleted. Class C (spike) is deleted upon PR merge. |

### 2.4 Design-Time vs. Consumption-Time Separation

To prevent documentation rot and ensure developers have access to low-level actionable details without polluting the high-level architecture registry:

- **Design-Time (Architecture Git)**: The `scnehaux-architecture` repository serves as the authoritative _Single Source of Truth_ for the ARB and CI/CD linter. It defines the logical domain blueprints (PAD/SAD) and governance constraints before implementation.
- **Consumption-Time (Web Developer Portal)**: Concrete integration manuals, API endpoints, JSON payloads, and SDKs must be published and consumed via Web Developer Portals (e.g., Swagger, ReDoc, Backstage) generated from code annotations, rather than polluting the Git architecture registry.

### 2.5 Versioning & Change Management

The architecture baseline is strictly version-controlled to maintain a traceable history of enterprise decisions. We reject a one-size-fits-all versioning scheme.

1. **Git as the Ultimate Revision History**: We do not maintain manual "Revision History" tables inside markdown files. Git commit history is the single source of truth for who changed what, when, and why.
2. **Immutable Snapshots vs. Semantic Versioning**: Immutable documents (like ADRs) are not versioned, if a decision changes, a *new* document must supersede the old one. Living documents (like PADs and SADs) utilize Semantic Versioning tags inside their YAML frontmatter.
3. **The Version Bump Mandate**: Once a living document reaches an `approved` state, any subsequent modification to its architectural content MUST include a corresponding version bump in its YAML metadata.

> For the exact review processes, ARB escalation triggers, and Git Pull Request mechanics governing these changes, refer to **[GDC-003: Architecture Review Process](GDC-003-review-process.md)**.

### 2.6 Document Lifecycle & State Management

Architecture documents are not static; they represent the evolving truth of the enterprise. Therefore, all documents must adhere to a strict state machine lifecycle.

1. **Mandatory Lifecycle Metadata**: Every document must declare its current lifecycle state (e.g., whether it is a draft under review, an active baseline, or a retired concept) within its YAML frontmatter.
2. **Decentralized State Machines**: The exact allowable statuses (e.g., `proposed`, `approved`, `deprecated`) and the valid transition paths between them are explicitly defined by their respective Document Context Guidelines.

> The mechanical enforcement of these lifecycles—including CI/CD Linter validations and Git-driven state transitions via the ARB—is centrally managed by **[GDC-001: Compliance Engine](GDC-001-compliance-engine.md)** and **[GDC-003: Architecture Review Process](GDC-003-review-process.md)**.

---

## 3. Document Types (Glossary of Truth)

The Scnehaux architecture categorizes technical knowledge into specific, purpose-built document types to prevent overlap and ensure clear ownership.

### 3.1 The Glossary of Truth & Execution Gateways

| Code              | Full Name                        | Authoritative Owner & Purpose                                                                                                                                                                                       |
| :---------------- | :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PRD**           | Product Requirements Document    | **[Owner: Product Managers]** Business "What" and "Why" (Non-technical). Not part of Scnehaux Architecture.                                                                                                         |
| **GDC (Vision)**  | Global Design Concept            | **[REJECTED]** High-Level Vision (C1). Integrated into the **Business Capability** section of **PAD** and **Context** of **SAD** documents.                                                                       |
| **GDC (Gov)**     | Governance Document Contract     | **[Owner: ARB]** Automated policy definitions and compliance enforcement. *(See [Appendix 5.1](#appendix-5-1) for acronym clarification).*                                                    |
| **EAD**           | Enterprise Architecture Document | **[Owner: ARB]** Strategic "North Star" (C1), cross-domain rules, and enterprise capability models.                                                                                             |
| **PAD**           | Platform Architecture Document   | **[Owner: Domain Team]** Domain Capability (C2). Defines business capabilities, integration contracts, and system positioning.                                                                              |
| **SAD**           | Software Architecture Document   | **[Owner: System Team]** System Solution (C2). Defines internal structure, deployment topology, observability, and resilience mechanics.                                            |
| **ADR**           | Architecture Decision Record     | **[Owner: Inherited (ARB or Domain/System Team)]** Meta. Rationale for significant technical pivots and trade-offs (`05-decisions`).                                                                                                                               |
| **STD**           | Standard Document                | **[Owner: Inherited (ARB or Domain Team)]** Meta. Mandatory engineering policies and guardrails (`02-standards`).                                                                                                                                           |
| **TRD**           | Technical Requirements Document  | **[REJECTED]** Scnehaux rejects TRDs to prevent documentation fragmentation. *(See [Appendix 5.2](#appendix-5-2) for rationale).*                                         |
| **TDD (Design)**  | Technical Design Document        | **[Owner: Component Team]** Component blueprints (C3), API contracts, ERDs, Security, and Failure Handling.                                                                                             |
| **TDD (Testing)** | Test Driven Development          | **[Owner: Component Team]** Engineering Methodology. The discipline used to implement the Test Strategy.                                                                                                                                    |
| **ERD**           | Entity Relationship Diagram      | **[Owner: Component Team]** Data Schema. The structural foundation of the TDD (Design).                                                                                                                                                     |

### 3.2 The Governance Ecosystem (The GDC Suite)

As established in **Section 1.1 (Logical Decentralization)**, to prevent `GDC-000` from becoming bloated with operational details, the execution mechanics and template constraints of this architecture are delegated to the broader **GDC Ecosystem**. This ecosystem acts as the central execution engine and consists of two halves:

#### The Core Execution Engine
*   **[GDC-001 — Compliance Engine](./GDC-001-compliance-engine.md)**: The "Machine Police". Defines how the CI/CD linter operates, how rules are deep-merged, and how to execute the Python validators.
*   **[GDC-002 — Quality Rubric](./GDC-002-quality-rubric.md)**: The "Qualitative Standard". Defines the 10 deep architectural parameters (Trade-offs, Blast Radius, etc.) for human review.
*   **[GDC-003 — Review Process](./GDC-003-review-process.md)**: The "ARB Manual". Defines how the Architecture Review Board operates, scores PRs, and handles exception waivers.
*   **[GDC-004 — Tech Lifecycle](./GDC-004-tech-lifecycle.md)**: The "Maturity Model". Governs how technologies transition from Assess -> Trial -> Adopted -> Hold (Sunset).
*   **[GDC-005 — Fitness Functions](./GDC-005-fitness-functions.md)**: The "Code-Level CI Gates". Mandates the use of Semgrep, CodeQL, and Dependency Cruiser to prevent architectural decay in source code.

#### The Context-Aware Templates (Guidelines)
The structural rules and YAML constraints for specific architectural outputs are defined in their respective guideline documents:

*   **[GDC-006 — GDC Guideline (Governance Rules)](./GDC-006-gdc-guideline.md)**: Rules for writing a GDC itself.
*   **[GDC-007 — EAD Guideline (Enterprise Strategy)](./GDC-007-ead-guideline.md)**
*   **[GDC-008 — STD Guideline (Engineering Policy)](./GDC-008-std-guideline.md)**
*   **[GDC-009 — PAD Guideline (Logical Domain)](./GDC-009-pad-guideline.md)**
*   **[GDC-010 — SAD Guideline (Physical System)](./GDC-010-sad-guideline.md)**
*   **[GDC-011 — ADR Guideline (Decision Records)](./GDC-011-adr-guideline.md)**
*   **[GDC-012 — TDD Guideline (Component Design)](./GDC-012-tdd-guideline.md)**

---

## 4. Enforcement Mechanism & Rule Reconciliation

The Linter (`linter.py`) serves as the ultimate, unyielding enforcer of this policy. CI/CD pipelines MUST execute the linter on all documentation changes. If the linter fails, the merge request MUST be blocked. Manual overrides are strictly prohibited. The machine is the law.

### 4.1 Deprecation and Exception Request Workflow

Architecture is not static. However, bypassing standards is a high-risk operation. Any deviation from the governance framework requires:
1. An ADR justifying the technical necessity for the exception.
2. Formal sign-off from the ARB.
3. Documentation of the waiver in the project's local `linting-rules.yaml`.

### 4.2 The Absolute Mandates
The architecture ecosystem operates under three absolute mandates. No system may:

1. Enter production without an approved SAD.
2. Deviate from standards without an ADR.
3. Introduce breaking architectural changes without a formal peer review and ARB approval.

### 4.3 Non-Functional Discipline

All systems must define measurable targets for Availability, Performance, Scalability, Security, Observability, and Resilience. Vague or non-measurable requirements (e.g., "fast" or "highly scalable") are considered governance violations and are not acceptable.

### 4.4 The Three-Gate CI Rule
To maintain high developer velocity, automated validation only triggers a **HARD BLOCK (Exit 1)** if a violation threatens:
1. **Security & Data Isolation** (e.g., bypassing PostgreSQL RLS).
2. **Structural Integrity** (e.g., CQRS Level 1 domain-isolation breach).
3. **Operational Stability** (e.g., missing mandatory SLAs).

Stylistic, naming conventions, or formatting preferences are treated as **WARNINGS**; they flag in PR reviews but do not block the merge.

### 4.5 The Linter Orchestration

The execution of the automated compliance gate is orchestrated by `linter.py`. The CI/CD engine utilizes a dynamic YAML federation where global rules (`linting-rules.yaml`) are deeply merged with domain-specific rules.
Crucially, all specifications regarding the Linter Execution Flow, Modular Ruleset Configurations, and linting enforcement are strictly maintained in the global framework:
👉 **[GDC-001 — Documentation Linter Framework](./GDC-001-compliance-engine.md)**

### 4.6 The Reconciliation Flow (Adding or Modifying Rules)

At Scnehaux, **if an architectural rule is not enforceable by the linter, it is merely a suggestion.** You cannot directly type a new rule (e.g., "Do not use X format") into a Markdown document. Every new rule MUST be reconciled with the automated linting engine.

Because the process of adding or modifying a rule is fundamentally an act of modifying a Governance Document Contract (GDC), the exact 4-step execution flow for updating YAML rules, regenerating documentation, and synchronizing qualitative rubrics is defined strictly within its authoritative guideline:
👉 **[GDC-006 §3 — The Reconciliation Flow](./GDC-006-gdc-guideline.md#3-the-reconciliation-flow-adding-or-modifying-rules)**

---

## 5. Appendix: Architectural Clarifications & Trade-Offs

<a id="appendix-5-1"></a>
### 5.1 Resolving the Acronym Overload (GDC)

To prevent acronym collision with external methodologies where "GDC" is used for "Global/General Design Concept", Scnehaux explicitly establishes that the acronym **GDC** refers **exclusively to Governance Document Contracts** (such as this `GDC-000` policy).

Standalone "Global Design Concept" or "General Design Concept" documents are not used in Scnehaux. Instead, high-level business vision and product capabilities are integrated directly into the **Business Capability** section of PADs and the **Context** section of SADs from day one.

<a id="appendix-5-2"></a>
### 5.2 The Rejection of TRD (Technical Requirements Document)

At Scnehaux, we **do not use** a standalone TRD. We believe that technical requirements are inseparable from the architecture that addresses them.

- **Reasoning**: Separate TRDs often lead to documentation fragmentation and "stale requirements" that do not reflect the actual architectural solution.
- **The Integrated Approach**: All functional and technical translations of the PRD are integrated directly into the **PAD** and **SAD** (specifically within the **Business Capability** and **Solution Architecture** sections). Enterprise Architecture (EAD) is driven by C-Level strategy rather than product-level PRDs.
- **Benefit**: This ensures that every technical requirement is mapped directly to an architectural decision or container structure, maintaining a single source of truth for the entire system lifecycle.

### 5.3 Framework Trade-Offs (Why Docs-as-Code?)

In accordance with the 10th parameter of the Quality Rubric (Trade-Offs), the ARB explicitly documents the rationale and technical compromises accepted when designing this custom, Markdown-based Governance Framework:

1. **Markdown + Custom Linter vs. Spotify Backstage / Structurizr**
   - *Why rejected*: Commercial/Enterprise systems like Backstage or Structurizr require dedicated infrastructure, operational overhead, and steep learning curves for UI-based modeling.
   - *The Trade-Off*: We lose interactive UI graphs and out-of-the-box cataloging. In exchange, we gain absolute **Policy-as-Code execution**. Markdown lives alongside the code, gets version-controlled via Git, and can be strictly validated by our custom Python CI/CD linter, making governance a blocking build step rather than an external chore.
2. **Binary Pass/Fail vs. Weighted Scoring (0-5)**
   - *Why rejected*: A 0-5 scoring system introduces subjectivity and negotiation.
   - *The Trade-Off*: We lose granular "partial credit" for semi-compliant documents. In exchange, we force absolute determinism. A document either meets the FAANG-grade threshold or it does not.
