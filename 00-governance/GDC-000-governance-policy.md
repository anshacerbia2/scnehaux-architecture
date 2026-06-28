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

### 1.1 Core Philosophy (The Existential Maxims)

This ecosystem operates on a radical departure from traditional Enterprise Architecture. We do not write documentation, we engineer **Knowledge as Infrastructure**. The framework is governed by seven absolute philosophical pillars:

1. **Predictability over Cleverness**: Serving as *The Goal* of this ecosystem, software architecture, documentation, and governance processes must be deterministic. We reject "clever" system hacks, bespoke documentation formats, and subjective rule enforcement in favor of boring designs, rigidly standardized structures, and mechanically verifiable policies.
2. **Strict Separation of Concerns (SoC)**: To provide *The Structure* for predictability, architectural responsibilities must be ruthlessly isolated across all layers (Fractal Abstraction). Every artifact has a strictly bounded perimeter. We decouple logical intent ("What we do") from physical execution ("How we do it") across the entire ecosystem so that downstream engineering refactors do not pollute upstream strategic artifacts.
3. **Explicit Contracts (Boundaries over Prose)**: Acting as *The Connective Tissue* between those separated concerns, we do not strive for exhaustive conceptual dictionaries. Instead, we demand explicit contracts at the boundaries. Critical integration points, such as structural metadata (YAML), API interfaces, trust boundaries, failure modes, NFR targets, and ownership, must be explicitly quantified. Hand-wavy assumptions in these critical areas are prohibited.
4. **Docs-as-Code (Immutable History)**: Providing *The Medium* for these contracts, architecture documentation is treated identically to source code. It lives in Git, where every change is locked into an immutable commit hash. It requires Pull Requests, undergoes peer review, and is validated by CI/CD pipelines. Un-auditable platforms (like Wikis or Word documents) are prohibited because they lack cryptographic traceability.
5. **Zero Waste (The Deletion Mandate)**: Dictating *The Lifecycle* of the medium, redundancy breeds entropy in both architectural and governance artifacts. We enforce a strict Single Source of Truth (SSOT) through centralized definitions and decentralized references. Execution-level artifacts that rot quickly must be aggressively deleted once built, and duplicated governance rules must be ruthlessly consolidated. We rely on Git history for forensic audits rather than accumulating dead archives.
6. **Policy-as-Code & Deterministic Enforcement**: Acting as *The Enforcer* of these laws, a rule without a validation mechanism is merely a suggestion. We enforce compliance through two strict gates: structural integrity is deterministically automated via the automated Fitness Function to achieve true **Policy-as-Code**, while complex architectural trade-offs are evaluated by humans using a quantifiable Quality Rubric.
7. **Circular Governance (Metaprogramming)**: Serving as *The Meta-Enforcer*, the ecosystem binds itself. The laws that govern the systems must also govern the rulebooks themselves. The Constitution and its Guidelines are audited by the exact same automated Fitness Function they mandate.

### 1.2 SoC Artifact Domain Philosophy

To physically execute the *Separation of Concerns* established in Pillar 2 in Core Philosophy, the boundaries of every Artifact Domain in the Scnehaux ecosystem are strictly measured across nine independent dimensions. Traceability between these bounded perimeters must be explicit:

1. **Asset Owned (Core Responsibility)**: The foundational asset or conceptual domain that the artifact governs. This establishes *what* is being built.
2. **Scope (Coverage)**: Dictated by the Asset Owned, this defines the spatial perimeter or jurisdiction the artifact encapsulates. This establishes *where* the rules apply.
3. **Abstraction**: Driven by the Scope and Asset, this is the architectural zoom level required to describe the asset. This establishes *how deep* the design goes.
4. **Primary Owner**: Based on the required Abstraction, this designates the specific team or collective entity responsible for authoring, maintaining, and defending the artifact.
5. **Target Audience**: Identified by the Primary Owner's intent, this dictates who the primary consumer of the artifact is.
6. **Blast Radius**: Derived from the Scope, this measures the systemic impact and cost of reversing a decision made within this artifact (One-Way vs. Two-Way Doors).
7. **Decision Horizon**: Calibrated against the Blast Radius, this sets the expected longevity of the design (e.g., a strategic multi-year horizon vs. a tactical ephemeral lifespan).
8. **Change Frequency**: Inversely proportional to the Decision Horizon, this dictates how often the artifact is expected to be mutated or become obsolete.
9. **NFR Focus**: Driven by the Target Audience and Blast Radius, this identifies the specific Non-Functional Requirements (e.g., Availability, Latency, Security, Cost) that must be rigorously quantified.

By applying these 9 interconnected dimensions, every architectural artifact is categorized into one of 7 distinct **Artifact Domains** and rigidly mapped in the following matrix:

| Artifact Domain | Asset Owned | Scope | Abstraction | Primary Owner | Target Audience | Blast Radius | Horizon | Change Freq | NFR Focus |
| :------- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[GDC](./GDC-006-gdc-guideline.md)** (Governance Document Contract) | Governance Framework | Ecosystem | Meta-Framework | ARB | All SWEs | Ecosystem | Permanent | Low | Gov SLAs |
| **[EAD](./GDC-007-ead-guideline.md)** (Enterprise Architecture Document) | Enterprise Strategy | Enterprise | Macro-Strategy | ARB | C-Level, VP, ARB | Massive (One-Way) | Strategic | Low | Global Availability |
| **[STD](./GDC-008-std-guideline.md)** (Standard Document) | Standards & Methodologies | Inherited (Enterprise/Domain/System) | Guardrails | Inherited (ARB or Domain/System Team) | Inherited (All SWEs or Local Team) | Inherited (Massive/Domain/System) | Living | Medium | Baseline limits |
| **[PAD](./GDC-009-pad-guideline.md)** (Product Architecture Document) | Domain & Product Capability | Domain | Domain Capability | Domain Team | Domain Team, PMs | Domain-wide | Long-term | Med-Low | RTO/RPO limits |
| **[SAD](./GDC-010-sad-guideline.md)** (System Architecture Document) | Deployable System Architecture | System | Container Topo | System Team | System Team | System-level | Mid-term | Medium | Latency P99, RPS |
| **[TDD](./GDC-012-tdd-guideline.md)** (Technical Design Document) | Component & Implementation Design | Component | Code Contracts | Component Team | Component Team | Component | Ephemeral | High | Retries, Timeouts |
| **[ADR](./GDC-011-adr-guideline.md)** (Architecture Decision Record) | Architectural Decisions | Inherited (Enterprise/Domain/System) | Rationale | Inherited (ARB or Domain/System Team) | Inherited (All SWEs or Local Team) | Inherited (Massive/Domain/System) | Point-in-time | Immutable | Trade-off metrics |

To illustrate this separation of concerns practically, consider the analogy of a nation's infrastructure planning: EAD acts as the national planning agency (Bappenas) setting macro objectives, PAD acts as regional planning (Bappeda) mapping domain capabilities, SAD acts as public works planning (PU Perencanaan) designing physical container topologies, and TDD acts as the public works execution (PU Pelaksanaan) building the granular components.

### 1.3 The Hybrid Metamodel (C4 + TOGAF + AWS WAF)

The 9 dimensions of the SoC Philosophy (Scope, Abstraction, NFR Focus, etc.) are powerful abstract concepts, but they require a pragmatic vehicle to be executed in the real world. To achieve this, Scnehaux rejects rigid compliance with any single architectural framework. Instead, we **adopt and synthesize the core concepts** from three industry-leading frameworks to physically manifest our 9 dimensions. We do not use their proprietary tools; we solely extract their mental models:

- **C4 Model (The Vertical Axis)**: Standard C4 is used as the foundational Y-axis (depth) of our ecosystem. It dictates how we zoom in from the Enterprise level (C1) down to the Component level (C3). This guarantees that every artifact operates at the correct level of abstraction and naturally serves the right audience (from C-Level executives at C1 down to SWEs at C3) without mixing technical depths.
  - *Why not UML or ArchiMate?* UML is too syntax-heavy and demands specialized training, while ArchiMate is often disconnected from the reality of code. C4 provides a lightweight, intuitive "map-like" mental model that developers natively understand without requiring proprietary modeling tools.

  | Level    | C4 Name           | Scnehaux Artifacts                             | SoC Scope               | Location                                    |
  | :------- | :---------------- | :--------------------------------------------- | :---------------------- | :------------------------------------------ |
  | **Meta** | **Cross-Cutting** | **GDC**, **ADR**, **STD** | Ecosystem / Inherited   | Root Repo (`00`, `02`, `05`)                |
  | **C1**   | **Context**       | **EAD**                            | Enterprise              | Root Repo (`01-enterprise`)                 |
  | **C2**   | **Container**     | **PAD** & **SAD**      | Domain & System         | Root Repo (`03-domain`, `04-system`) |
  | **C3**   | **Component**     | **TDD**                            | Component               | **Specific Project Repository**             |
  | **C4**   | **Code**          | Source Code / Implementation                   | Code Base               | **Specific Project Repository**             |

- **TOGAF (The Business Anchor)**: While C4 handles technical zoom, TOGAF provides the strategic anchor. We adopt its 4 Architecture Domains (Business, Data, Application, Technology) to construct the long-term foundations of our EAD and PAD documents. This ensures our architecture always aligns with enterprise business strategy (EAD) and logical domain capabilities (PAD) before any downstream team touches physical code.
  - *Why not Zachman?* The Zachman Framework is a powerful ontological matrix, but it is often too academic for agile engineering teams. TOGAF's 4 domains provide the most pragmatic vocabulary for forcing technologists to answer "What capability are we actually building?" before designing systems.
- **AWS Well-Architected Framework (The Quality Standard)**: We adopt its 6 pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability) as our absolute standard for evaluating Non-Functional Requirements. This framework acts as the scale for our Quality Rubric (**[GDC-003 — Quality Rubric](GDC-003-quality-rubric.md)**), ensuring all NFR trade-offs are objectively scored rather than debated.
  - *Why not ISO/IEC 25010?* While ISO provides an exhaustive list of software quality models, it is theoretical and difficult to quantify. AWS WAF provides battle-tested, cloud-native pillars that translate directly into actionable engineering metrics (e.g., latency, cost, RTO) that modern teams already measure.

---

## 2. Policy Framework

To operate at true enterprise scale, all Scnehaux architecture artifacts must inherently adhere to strict laws governing their lifecycle, existence, and structure.

### 2.1 The Fractal Boundary (Physical vs. Logical Decentralization)

To prevent the Governance Framework from becoming a monolithic bottleneck, we apply the exact same **Separation of Concerns (SoC)** to the rulebooks as we do to our modular artifacts. This creates a "Fractal Boundary", where the rules governing decentralization are themselves decentralized across two dimensions:

#### 2.1.1 Physical Decentralization (Repository Federation)

This dimension governs where the actual architecture description files physically reside to support the hybrid metamodel. The ecosystem is federated into two distinct repository tiers:

~~~mermaid
graph TD
    Root{"Root Architecture Repository"}

    subgraph Hub ["Centralized Meta-Federation"]
        Policies["Governance Policies (GDC Guidelines)"]
        Docs["Architectural Context (SAD, STD, ADR)"]
        Engine["CI/CD Fitness Function (linter.yml)"]
    end

    subgraph Spokes ["Decentralized Project Repositories"]
        Project1["scnehaux-iam (TDDs & Code)"]
        Project2["scnehaux-ui-platform (TDDs & Code)"]
    end

    Root ==>|Houses| Policies
    Root ==>|Houses| Docs
    Root ==>|Houses| Engine

    Policies -.->|Dictates Rules| Project1
    Policies -.->|Dictates Rules| Project2

    Docs -.->|Provides System Context| Project1
    Docs -.->|Provides System Context| Project2

    Engine -.->|CI/CD Validation| Project1
    Engine -.->|CI/CD Validation| Project2

    style Root fill:#805ad5,stroke:#553c9a,stroke-width:2px,color:#fff
    style Policies fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style Docs fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style Engine fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style Project1 fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style Project2 fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
~~~

**A. The Root Architecture Repository (Centralized Meta-Federation)**:
   - **Role**: Acts as the centralized hub and rule-maker for the entire engineering ecosystem. It physically houses the governance and architectural policies, the automated Fitness Function, and the overarching architectural context that all downstream projects must obey.
   - **Artifacts Housed**: Governance Artifacts (GDC), Architectural Artifacts (EAD, STD, PAD, SAD, ADR), and the Fitness Function.
   - **Layout Pattern**: Top-level directories are strictly separated by abstraction level (Enterprise, Domain, System) or cross-cutting concerns (Governance, Standards, Decisions). Sub-directories then group artifacts by logical bounded contexts or business domains.
   - **Map of the Root Architecture Repository:**
     ```text
     scnehaux-architecture/
     ├── 00-governance/                   # (The Supreme Rules)
     │   ├── rules/                       # (Linter YAML Federation)
     │   │   ├── linting-rules.yaml
     │   │   └── linting-rules-[doc_type].yaml
     │   └── GDC-000-governance-policy.md
     │
     ├── 01-enterprise/                   # (EADs - Holistic View)
     │   ├── EAD-001-value-stream.md
     │   └── tech-radar.yaml
     │
     ├── 02-standards/                    # (STDs - Cross-cutting & Domain)
     │   ├── _global/
     │   │   └── STD-GLB-001-api-design.md
     │   └── ui-platform/
     │       └── STD-UIP-001-design-tokens.md
     │
     ├── 03-domain/                       # (PADs - Domain Architecture)
     │   ├── ui-platform/
     │   │   ├── ui-platform.pad.md
     │   │   └── platform-diagram.png
     │   └── iam/
     │       └── iam.pad.md
     │
     ├── 04-system/                       # (SADs - System Architecture)
     │   ├── scnehaux-ui-platform/
     │   │   └── scnehaux-ui-platform.sad.md
     │   ├── scnehaux-iam/
     │   │   ├── scnehaux-iam.sad.md
     │   │   └── deployment-topology.png
     │   └── scnehaux-iam-dashboard/
     │       └── scnehaux-iam-dashboard.sad.md
     │
     ├── 05-decisions/                    # (ADRs - Cross-cutting & Domain)
     │   ├── _global/
     │   │   └── ADR-GLB-001-modular-monolith.md
     │   └── iam/
     │       └── ADR-IAM-001-use-keycloak.md
     │
     ├── scripts/                         # (CI/CD Automations)
     │   └── generate_rules_doc.py
     │
     ├── validators/                      # (Python Validation Logic)
     │   ├── base.py
     │   └── [doc_type].py
     │
     └── linter.py                        # (The Fitness Function Entrypoint)
     ```

**B. Project Repositories (Decentralized Execution)**:
   - **Role**: Downstream application repositories (e.g., `scnehaux-iam`) that act as the local execution environment where engineering teams build and deploy physical components.
   - **Artifacts Housed**: Detailed component designs (TDDs) and executable code only.
   - **Layout Pattern**: Component design documents are grouped under a dedicated `docs/designs/` folder, with the internal structure mirroring the repository's module boundaries.
   - **Map of a Project Repository:**
     ```text
     scnehaux-iam/                      # (Project Repository)
     ├── docs/                          # (Root)
     │   └── designs/                   # (TDDs - Component Architecture)
     │       └── login-module/          # (Module boundary)
     │           ├── TDD-IAM-LOG-001-oauth-flow.md
     │           └── sequence-diagram.png
     │    
     │
     └── src/                           # (Source Code matching the modules)
         └── login/
     ```

#### 2.1.2 Logical Decentralization (The Meta-Federation)
Even though all overarching policies are physically centralized in the Root Repo, they are *logically* decoupled. The governance ecosystem operates on a strict hierarchical DAG (Directed Acyclic Graph):

~~~mermaid
graph TD
    Gov000{"GDC-000 (The Constitution / Root Node)"}

    subgraph Tier1 ["Tier 1: Artifact Domain Policies"]
        GovGuide["Governance Guidelines (GDC-006)"]
        ArchGuide["Architecture Guidelines (GDC-007 to GDC-012)"]
    end

    subgraph Tier2 ["Tier 2: The Fitness Function (Base Class)"]
        FitFunc{"GDC-001 (Master Fitness Function)"}
        BaseYaml["Root Schema (linting-rules.yaml)"]
        BasePy["Root Validator (base.py)"]
    end

    subgraph Tier3 ["Tier 3: Domain-Specific Fitness Functions (Child Classes)"]
        ContextYaml["Domain-Specific Schemas (linting-rules-[type].yaml)"]
        ContextPy["Domain-Specific Validators ([type].py)"]
    end

    Gov000 ==>|Spawns| GovGuide
    Gov000 ==>|Spawns| ArchGuide
    Gov000 ==>|Spawns| FitFunc

    GovGuide -.->|Extends| FitFunc
    ArchGuide -.->|Extends| FitFunc

    FitFunc -->|Produces| BaseYaml
    FitFunc -->|Produces| BasePy

    GovGuide -->|Produces| ContextYaml
    GovGuide -->|Produces| ContextPy
    ArchGuide -->|Produces| ContextYaml
    ArchGuide -->|Produces| ContextPy

    BaseYaml -.->|Deep Merged By| ContextYaml
    BasePy -.->|Extended By| ContextPy

    style Gov000 fill:#805ad5,stroke:#553c9a,stroke-width:2px,color:#fff
    style GovGuide fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style ArchGuide fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style FitFunc fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style BaseYaml fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style BasePy fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style ContextYaml fill:#2c5282,stroke:#4299e1,stroke-width:2px,color:#fff
    style ContextPy fill:#2c5282,stroke:#4299e1,stroke-width:2px,color:#fff
~~~

**1. The Root (Constitution)**
`GDC-000` is the root anchor that establishes the philosophical pillars. It acts as the ultimate authority, directly spawning all Guidelines and the Master Fitness Function.

**2. The Master Fitness Function (The Base Interface)**
`GDC-001` (Architecture Fitness Functions) is the centralized Master Policy for all automated validation. It acts as the "Base Class" of the governance ecosystem, producing the universal Root Schema (`linting-rules.yaml`) and Root Validator (`validators/base.py`).

**3. The Guidelines (The Implementations)**
Architecture & Governance Guidelines (e.g., `GDC-006` to `GDC-012`): These documents define the domain-specific constraints (e.g., ADR schemas, SAD boundaries).

**4. The Domain-Specific Validators (Polymorphic Execution)**
By inheriting the Master Fitness Function (`GDC-001`), every Guideline is forced to produce its own decentralized, domain-specific fitness functions:
- **Domain-Specific Schemas**: Domain-specific YAML (e.g., `linting-rules-adr.yaml`) which dynamically *deep-merges* into `linting-rules.yaml`.
- **Domain-Specific Validators**: Domain-specific Python (e.g., `validators/adr.py`) which physically *extends* the `BaseValidator` class.



### 2.2 Logical Abstraction & The Traceability DAG (Directed Acyclic Graph)
Documents must strictly align with their C4-assigned boundary without leaking execution details across layers. All artifacts in the Scnehaux ecosystem must connect to form an unbroken **Directed Acyclic Graph (DAG)** of traceability, meaning every decision and design flows top-down without circular dependencies.

~~~mermaid
---
title: The C4 Traceability Chain & Exception Workflow
---
graph TD
    GDC{"GDC-000 (The Constitution / Root Node)"}

    subgraph Supreme ["Level 1: Enterprise Strategy & Policy"]
        EAD["EAD (Enterprise Architecture)"]
        STD["STD (Global Standards)"]
    end

    subgraph Domain ["Level 2: Logical Boundaries"]
        PAD["PAD (Product Architecture)"]
    end

    subgraph System ["Level 3: Physical Implementation"]
        SAD["SAD (System Architecture)"]
    end

    subgraph Execution ["Level 4: Component Design"]
        TDD["TDD (Technical Design)"]
    end
    
    ADR{{"ADR (Decision Record)"}}

    GDC ==>|Dictates Governance| EAD
    
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

    %% Escape Hatches
    STD -.->|Escape Hatch - Orphan Policy| GDC
    ADR -.->|Escape Hatch - Orphan Policy| GDC
    
    style GDC fill:#805ad5,stroke:#553c9a,stroke-width:2px,color:#fff
    style ADR fill:#dd6b20,stroke:#c05621,stroke-width:2px,color:#fff
    style EAD fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style STD fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style PAD fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style SAD fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style TDD fill:#2c5282,stroke:#4299e1,stroke-width:2px,color:#fff
~~~

#### 2.2.1 The 1-to-N Mapping Rule
A single Domain Capability (PAD) is fulfilled by multiple physical software systems (SADs). To prevent logical boundaries from being contaminated by deployment-specific execution mechanics, **every distinct deployable unit must have its own SAD**, even if they serve the same domain capability. Furthermore, every SAD **MUST** strictly trace back to a parent PAD.

~~~mermaid
graph TD
  PAD["identity.pad.md (C2 Domain Capability)"]
  PAD --> SAD1["scnehaux-iam.sad.md (Core Auth & Session)"]
  PAD --> SAD2["scnehaux-directory.sad.md (User Cache Service)"]
  PAD --> SAD3["scnehaux-kms-rotator.sad.md (Key Rotator Utility)"]

  style PAD fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
  style SAD1 fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff
  style SAD2 fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff
  style SAD3 fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff
~~~

- **Resilience to Refactoring**: Splitting a backend monolith (e.g., `scnehaux-iam` into separate microservices) requires zero changes to the PAD since the logical integration contracts, trust boundaries, and domain capabilities remain identical.
- **Leakage Prevention**: Separating these layers prevents strategic capability documents from being polluted with operational details.

#### 2.2.2 The C4 Traceability Chain

- **C1 Enterprise documents (EAD)** must focus exclusively on macro-level strategic capabilities, enterprise policies, and value streams. They must not contain container topologies, system integration schemas, or API endpoints.
- **Engineering Standards (STD)** serve as cross-cutting guardrails. They define mandatory engineering baselines, compliance rules, and paved roads that apply across all C4 levels.
- **C2 Capability and System documents (PAD/SAD)** must define logical domain capabilities and physical container structures. They must not contain C3 component-level implementation mechanics, database index names, or low-level class/function signatures.
- **C3 Component documents (TDD)** must define concrete component artifacts, API schemas, and entity relationships. They must not override platform-wide integration contracts, trust boundaries, or global protocols established in C2 documents.

Every technical decision must be traceable back to its root cause in the architecture. The **Hierarchy of Authority** (Chain of Command) operates top-down:

1. **EAD & STD (The Supreme Law)**: No downstream document may violate enterprise strategy or global engineering policies.
2. **PAD (The Domain Contract)**: Must comply with EAD/STD. Establishes the logical constraints that downstream physical systems must follow.
3. **SAD (The System Reality)**: Must comply with its parent PAD.
4. **TDD (The Execution Artifact)**: Must comply with its parent SAD.
5. **ADR (The Orthogonal Ledger)**: Serves a dual-purpose. It either *establishes* the baseline for EAD/STD, or acts as an approved *Exception Waiver* that allows a PAD/SAD to legally break the chain of command.

#### 2.2.3 The Orphan Policy & Ecosystem Escape Hatch
To maintain the unbroken DAG illustrated above, **Orphan Artifacts are strictly prohibited**. Every meta-artifact (ADR and STD) must explicitly declare its parent context (`governed_by`). However, to prevent "Chicken or Egg" friction—where global technical standards (e.g., Git branching rules) are blocked because a strategic EAD hasn't been written yet—purely technical or ecosystem-wide meta-artifacts are legally permitted to bypass EAD/PAD and attach directly to **GDC-000** as their root node.



A downstream document (e.g., a SAD) that contradicts an upstream document (e.g., an EAD or PAD) without an approved **ADR** (Architecture Decision Record) granting an explicit exception is a strict governance violation.



### 2.3 The Mutability Matrix
To prevent documentation rot while preserving decision traceability, all documents must adhere to this Mutability Matrix:

| Doc Type | C4 Level       | Mutability           | Mutability Rule                                                                                                                                                                |
| :------- | :------------- | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[EAD](GDC-007-ead-guideline.md)**  | C1 (Context)   | **Mutable (Living)** | Represents the active enterprise architecture artifact. Updated directly when strategic TOGAF domains or capabilities evolve.                                                 |
| **[STD](GDC-008-std-guideline.md)**  | Meta           | **Mutable (Living)** | Represents current active rules. Modified directly and versioned via SemVer when rules evolve. Major changes require an authorizing ADR.                                       |
| **[PAD](GDC-009-pad-guideline.md)**  | C2 (Domain)    | **Mutable (Living)** | Represents active domain capability boundaries and trust contracts. Updated directly when capabilities are added or when the `fulfilled_by` SAD list changes.                  |
| **[SAD](GDC-010-sad-guideline.md)**  | C2 (System)    | **Mutable (Living)** | Represents active physical system topologies. Updated directly when microservices, containers, or deployment infrastructures are modified.                                     |
| **[ADR](GDC-011-adr-guideline.md)**  | Meta           | **Immutable**        | Represents a point-in-time decision. Once accepted, it must never be modified (except for status updates). Changes require a new replacing ADR.                                |
| **[TDD](GDC-012-tdd-guideline.md)**  | C3 (Component) | **Hybrid**           | Component designs. Class A (strategic) is archived. Class B (feature) is folded into the SAD and deleted. Class C (spike) is deleted upon PR merge. |

### 2.4 Design-Time vs. Consumption-Time Separation

To prevent documentation rot and ensure developers have access to low-level actionable details without polluting the high-level architecture registry:

- **Design-Time (Architecture Git)**: The `scnehaux-architecture` repository serves as the authoritative _Single Source of Truth_ for the ARB and CI/CD linter. It defines the logical domain artifacts (PAD/SAD) and governance constraints before implementation.
- **Consumption-Time (Web Developer Portal)**: Concrete integration manuals, API endpoints, JSON payloads, and SDKs must be published and consumed via Web Developer Portals (e.g., Swagger, ReDoc, Backstage) generated from code annotations, rather than polluting the Git architecture registry.

### 2.5 Versioning & Change Management

The architecture baseline is strictly version-controlled to maintain a traceable history of enterprise decisions. We reject a one-size-fits-all versioning scheme.

1. **Git as the Ultimate Revision History**: We do not maintain manual "Revision History" tables inside markdown files. Git commit history is the single source of truth for who changed what, when, and why.
2. **Immutable Snapshots vs. Semantic Versioning**: Immutable documents (like ADRs) are not versioned, if a decision changes, a *new* document must supersede the old one. Living documents (like PADs and SADs) utilize Semantic Versioning tags inside their YAML frontmatter.
3. **The Version Bump Mandate**: Once a living document reaches an `approved` state, any subsequent modification to its architectural content MUST include a corresponding version bump in its YAML metadata.

> For the exact review processes, ARB escalation triggers, and Git Pull Request mechanics governing these changes, refer to **[GDC-004: Architecture Review Process](GDC-004-review-process.md)**.

### 2.6 Document Lifecycle & State Management

Architecture documents are not static; they represent the evolving truth of the enterprise. Therefore, all documents must adhere to a strict state machine lifecycle.

1. **Mandatory Lifecycle Metadata**: Every document must declare its current lifecycle state (e.g., whether it is a draft under review, an active baseline, or a retired concept) within its YAML frontmatter.
2. **Decentralized State Machines**: The exact allowable statuses (e.g., `proposed`, `approved`, `deprecated`) and the valid transition paths between them are explicitly defined by their respective Document Context Guidelines.

> The mechanical enforcement of these lifecycles—including automated CI/CD Fitness Function validations and Git-driven state transitions via the ARB—is centrally managed by **[GDC-001: Architecture Fitness Functions](GDC-001-fitness-functions.md)** and **[GDC-004: Architecture Review Process](GDC-004-review-process.md)**.

---

## 3. Enforcement Mechanism (The Ecosystem)

### 3.1 The Dual-Gate Enforcement Model

To manage governance across federated repositories without creating a human bottleneck, the ecosystem utilizes a two-stage evaluation pipeline.

1. **Gate 1: Automated CI/CD Fitness Functions**: **[GDC-001 — Architecture Fitness Functions](./GDC-001-fitness-functions.md)** functions as the first line of evaluation. It deterministically validates metadata completeness, structural layout, and technology lifecycle patterns across documents before human review.
2. **Gate 2: Qualitative Design Review**: **[GDC-003 — Documentation Quality Framework](./GDC-003-quality-rubric.md)** functions as the human evaluation stage. It equips Architecture Review Board (ARB) members with an objective scoring rubric to evaluate complex trade-offs that machines cannot parse (e.g., system blast radius, domain coupling, and business alignment).

> [!IMPORTANT]
> **The Circular Dependency of Trust (Checks & Balances)**
> The ecosystem is designed to validate itself. For example, while the Constitution (`GDC-000`) outlines the validation requirements, it is simultaneously evaluated by the automated Fitness Function (`GDC-001`), which operates based on the layout patterns defined in the GDC Guideline (`GDC-006`). This creates a closed loop where the framework continuously audits its own integrity.

> [!NOTE]
> **Scope**: The Dual-Gate model is built to evaluate structural Architecture Artifacts (SAD, PAD, EAD, ADR, GDC). Ephemeral assets (e.g., whiteboard sketches) and code-level documentation (e.g., inline comments, Swagger specs) fall outside this evaluation pipeline.

### 3.2 The Glossary of Truth & Execution Gateways

| Code              | Full Name                        | Authoritative Owner & Purpose                                                                                                                                                                                       |
| :---------------- | :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PRD**           | Product Requirements Document    | **[Owner: Product Managers]** Business "What" and "Why" (Non-technical). Not part of Scnehaux Architecture.                                                                          |
| **GDC (Vision)**  | Global Design Concept            | **[REJECTED]** High-Level Vision (C1). Integrated into the **Domain Capability** section of **PAD** and **Context** of **SAD** documents.                                                                       |
| **GDC (Gov)**     | Governance Document Contract     | **[Owner: ARB]** Automated policy definitions and deterministic fitness function enforcement. *(See [Appendix 5.1](#appendix-5-1) for acronym clarification).*                                                    |
| **EAD**           | Enterprise Architecture Document | **[Owner: ARB]** Strategic "North Star" (C1), cross-domain rules, and enterprise capability models.                                                              |
| **PAD**           | Product Architecture Document    | **[Owner: Domain Team]** Domain Capability (C2). Defines domain capabilities, integration contracts, and system positioning.                                                                              |
| **SAD**           | System Architecture Document     | **[Owner: System Team]** System Solution (C2). Defines internal structure, deployment topology, observability, and resilience mechanics.                                            |
| **ADR**           | Architecture Decision Record     | **[Owner: Inherited (ARB or Domain/System Team)]** Meta. Rationale for significant technical pivots and trade-offs (`05-decisions`).                                                                                                                               |
| **STD**           | Standard Document                | **[Owner: Inherited (ARB or Domain/System Team)]** Meta. Mandatory engineering policies and guardrails (`02-standards`).                                                                                                                                           |
| **TRD**           | Technical Requirements Document  | **[REJECTED]** Scnehaux rejects TRDs to prevent documentation fragmentation. *(See [Appendix 5.2](#appendix-5-2) for rationale).*                                         |
| **TDD (Design)**  | Technical Design Document        | **[Owner: Component Team]** Component artifacts (C3), API contracts, ERDs, Security, and Failure Handling.                                                                                             |
| **TDD (Testing)** | Test Driven Development          | **[Owner: Component Team]** Engineering Methodology. The discipline used to implement the Test Strategy.                                                                                                                                    |
| **ERD**           | Entity Relationship Diagram      | **[Owner: Component Team]** Data Schema. The structural foundation of the TDD (Design).                                                                                                                                                     |

### 3.3 The Policy Layer (The Artifact-Specific Guidelines)

At Scnehaux, **Policy resides entirely in the Guidelines**. These documents define the explicit rules, schemas, and expectations for every artifact produced by the enterprise. They act as the "mothers" of the Fitness Functions.

*   **[GDC-006 — GDC Guideline (Governance Rules)](./GDC-006-gdc-guideline.md)**: Rules for writing a GDC itself.
*   **[GDC-007 — EAD Guideline (Enterprise Strategy)](./GDC-007-ead-guideline.md)**
*   **[GDC-008 — STD Guideline (Engineering Policy)](./GDC-008-std-guideline.md)**
*   **[GDC-009 — PAD Guideline (Logical Domain)](./GDC-009-pad-guideline.md)**
*   **[GDC-010 — SAD Guideline (Physical System)](./GDC-010-sad-guideline.md)**
*   **[GDC-011 — ADR Guideline (Decision Records)](./GDC-011-adr-guideline.md)**
*   **[GDC-012 — TDD Guideline (Component Design)](./GDC-012-tdd-guideline.md)**

### 3.4 The Enforcement Layer (The GDC Pillars)

If the Guidelines are the Law, the 3 Core Pillars are the Police. They act universally across all Policies. If one component is missing, the ecosystem's identity collapses:

*   **[GDC-001 — Architecture Fitness Functions](./GDC-001-fitness-functions.md)** (The Machine Police): The CI/CD linter. It acts as the automated gatekeeper, deterministically validating structural layout, metadata, and the enterprise technology radar.
*   **[GDC-003 — Quality Rubric](./GDC-003-quality-rubric.md)** (The Human Brain): Defines the 10 deep architectural parameters used by reviewers to judge subjective trade-offs.
*   **[GDC-004 — Review Process](./GDC-004-review-process.md)** (The Supreme Court): Defines how the ARB scores PRs and grants exception waivers.

## 4. Severity & Exceptions (The Enforcement Pipeline)

To understand how the Scnehaux ecosystem operates, one must differentiate between how the governance framework is **built** (Metaprogramming) and how it is **consumed** (Execution). 

### 4.1 The Metaprogramming Flow (Authoring Governance)

This is the conceptual flow used by the Architecture Review Board (ARB) when creating or modifying the framework itself (e.g., adding a new PAD rule). It strictly follows the "Policy-as-Code" Acid Test: **A policy that cannot be translated into a Fitness Function is a failure of governance.**

1. **Policy Ideation**: The ARB debates and defines the new architectural standard (e.g., updating a GDC Guideline).
2. **The Acid Test (Fitness Function Extraction)**: The policy is immediately forced to be codified into measurable Fitness Functions (YAML rules for the Linter, or Semgrep rules for Code). 
   - *If it cannot be automated*, the policy is rejected as "hand-wavy" or vague.
3. **Engine Integration**: The automated engine (`GDC-001`) executes the new Fitness Functions.
4. **Human Qualification (`GDC-003`)**: For the qualitative nuances of the policy that machines cannot mathematically judge (e.g., the context of a trade-off), the ARB updates the Quality Rubric for human PR reviews.

~~~mermaid
graph TD
    subgraph Ideation
        ARB[ARB Defines a New Architectural Policy] --> Policy[GDC Guideline Document]
    end

    subgraph The Acid Test
        Policy --> Fitness{Can it be codified into a Fitness Function?}
        Fitness -->|No: Vague/Unmeasurable| Reject[Reject Policy: Rewrite required]
        Fitness -->|Yes: Deterministic| Codify[Extract to YAML / Semgrep]
    end

    subgraph Execution Layers
        Codify --> Engine{Automated Engine: GDC-001}
        Policy --> Rubric{GDC-003: Quality Rubric}
        Rubric -.->|Guides Human Context Audit| Human[ARB PR Review]
    end
    
    style ARB fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#fff
    style Fitness fill:#d69e2e,stroke:#b7791f,stroke-width:2px,color:#fff
    style Reject fill:#9b2c2c,stroke:#fc8181,stroke-width:2px,color:#fff
    style Engine fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff
    style Rubric fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
~~~

> **Rule Reconciliation**: Because adding a rule is fundamentally an act of modifying a Governance Document Contract, the exact 4-step execution flow for updating YAML rules and synchronizing rubrics is defined in **[GDC-006 §3 — The Reconciliation Flow](./GDC-006-gdc-guideline.md#3-the-reconciliation-flow-adding-or-modifying-rules)**.

### 4.2 The Execution Flow (Consuming Governance)

This is the CI/CD pull request lifecycle used by downstream engineers when proposing an architectural change (e.g., submitting a new SAD or TDD). Because machines are faster than humans, the execution flow is the inverse of the metaprogramming flow: **Automation runs before Qualification.**

~~~mermaid
graph TD
    subgraph Phase 1: Architecture Design
        Author[Engineer Authors PAD/SAD] --> GitPR[Opens Pull Request]
    end

    subgraph Phase 2: Design Validation
        GitPR --> Linter{Gate 1: Design Automation<br>GDC-001 Compliance Engine}
        Linter -->|Fails| Reject1[Block PR Merge]
        Linter -->|Passes| ARB{Gate 2: Design Qualification<br>GDC-003 ARB Rubric}
        ARB -->|Rejects| Reject1
        ARB -->|Exception Needed| Exception{GDC-004: Review Process}
        Exception -->|Approved via ADR| Merge
        ARB -->|Approved| Merge[Merge to Main]
    end

    subgraph Phase 3: Downstream Execution
        Merge --> Dev[Engineer Writes Source Code]
        Dev --> CodeCI{Gate 3: Execution Automation<br>GDC-001 Fitness Functions}
        CodeCI -->|Fails Semgrep/CodeQL| Reject2[Block Code Deployment]
        CodeCI -->|Passes| Prod[Deploy to Production]
    end
    
    subgraph Ecosystem Constraints
        TechRadar[GDC-001: Tech Lifecycle] -.->|Feeds Sunset Rules to| Linter
        TechRadar -.->|Feeds Constraints to| CodeCI
    end

    style Linter fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style ARB fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style CodeCI fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff
    style Reject1 fill:#9b2c2c,stroke:#fc8181,stroke-width:2px,color:#fff
    style Reject2 fill:#9b2c2c,stroke:#fc8181,stroke-width:2px,color:#fff
    style Prod fill:#276749,stroke:#68d391,stroke-width:2px,color:#fff
~~~

### 4.3 Deprecation and Exception Request Workflow

Architecture is not static. However, bypassing standards is a high-risk operation. Any deviation from the execution flow requires:
1. An ADR justifying the technical necessity for the exception.
2. Formal sign-off from the ARB.
3. Documentation of the waiver in the project's local `linting-rules.yaml`.

### 4.4 The Absolute Mandates
The architecture ecosystem operates under three absolute mandates. No system may:

1. Enter production without an approved SAD.
2. Deviate from standards without an ADR.
3. Introduce breaking architectural changes without a formal peer review and ARB approval.

### 4.5 The Three-Gate CI Rule
To maintain high developer velocity, automated validation (Gate 1 & Gate 3) only triggers a **HARD BLOCK (Exit 1)** if a violation threatens:
1. **Security & Data Isolation** (e.g., bypassing PostgreSQL RLS).
2. **Structural Integrity** (e.g., CQRS Level 1 domain-isolation breach).
3. **Operational Stability** (e.g., missing mandatory SLAs).

Stylistic, naming conventions, or formatting preferences are treated as **WARNINGS**; they flag in PR reviews but do not block the merge.

### 4.6 Non-Functional Discipline

All systems must define measurable targets for Availability, Performance, Scalability, Security, Observability, and Resilience. Vague or non-measurable requirements (e.g., "fast" or "highly scalable") are considered governance violations and are not acceptable.

### 4.7 The Fitness Function Orchestration

The execution of the automated fitness function gate is orchestrated by `linter.py`. The CI/CD engine utilizes a dynamic YAML federation where global rules (`linting-rules.yaml`) are deeply merged with domain-specific rules.
Crucially, all specifications regarding the Fitness Function Execution Flow, Modular Ruleset Configurations, and linting enforcement are strictly maintained in the global framework:
👉 **[GDC-001 - Architecture Fitness Functions](./GDC-001-fitness-functions.md)**

### 4.8 The Reconciliation Flow (Adding or Modifying Rules)

At Scnehaux, **if an architectural rule is not enforceable by the fitness function, it is merely a suggestion.** You cannot directly type a new rule (e.g., "Do not use X format") into a Markdown document. Every new rule MUST be reconciled with the automated fitness function engine.

Because the process of adding or modifying a rule is fundamentally an act of modifying a Governance Document Contract (GDC), the exact 4-step execution flow for updating YAML rules, regenerating documentation, and synchronizing qualitative rubrics is defined strictly within its authoritative guideline:
👉 **[GDC-006 §3 — The Reconciliation Flow](./GDC-006-gdc-guideline.md#3-the-reconciliation-flow-adding-or-modifying-rules)**

---

## 5. Appendix: Architectural Clarifications & Trade-Offs

<a id="appendix-5-1"></a>
### 5.1 Resolving the Acronym Overload (GDC)

To prevent acronym collision with external methodologies where "GDC" is used for "Global/General Design Concept", Scnehaux explicitly establishes that the acronym **GDC** refers **exclusively to Governance Document Contracts** (such as this `GDC-000` policy).

Standalone "Global Design Concept" or "General Design Concept" documents are not used in Scnehaux. Instead, high-level business vision and product capabilities are integrated directly into the **Domain Capability** section of PADs and the **Context** section of SADs from day one.

<a id="appendix-5-2"></a>
### 5.2 The Rejection of TRD (Technical Requirements Document)

At Scnehaux, we **do not use** a standalone TRD. We believe that technical requirements are inseparable from the architecture that addresses them.

- **Reasoning**: Separate TRDs often lead to documentation fragmentation and "stale requirements" that do not reflect the actual architectural solution.
- **The Integrated Approach**: All functional and technical translations of the PRD are integrated directly into the **PAD** and **SAD** (specifically within the **Domain Capability** and **Solution Architecture** sections). Enterprise Architecture (EAD) is driven by C-Level strategy rather than product-level PRDs.
- **Benefit**: This ensures that every technical requirement is mapped directly to an architectural decision or container structure, maintaining a single source of truth for the entire system lifecycle.

### 5.3 Framework Trade-Offs (Why Docs-as-Code?)

In accordance with the 10th parameter of the Quality Rubric (Trade-Offs), the ARB explicitly documents the rationale and technical compromises accepted when designing this custom, Markdown-based Governance Framework:

1. **Markdown + Custom Fitness Function vs. Spotify Backstage / Structurizr**
   - *Why rejected*: Commercial/Enterprise systems like Backstage or Structurizr require dedicated infrastructure, operational overhead, and steep learning curves for UI-based modeling.
   - *The Trade-Off*: We lose interactive UI graphs and out-of-the-box cataloging. In exchange, we gain absolute **Policy-as-Code execution**. Markdown lives alongside the code, gets version-controlled via Git, and can be strictly validated by our custom Python Fitness Function, making governance a blocking build step rather than an external chore.
2. **Binary Pass/Fail vs. Weighted Scoring (0-5)**
   - *Why rejected*: A 0-5 scoring system introduces subjectivity and negotiation.
   - *The Trade-Off*: We lose granular "partial credit" for semi-compliant documents. In exchange, we force absolute determinism. A document either meets the FAANG-grade threshold or it does not.
