---
doc_meta:
  id: GDC-001
  title: Enterprise Architecture Document (EAD) Guideline
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Enterprise Architecture Document (EAD) Guideline

## 1. Context & Scope

This guideline defines the mandatory structure, metadata schema, and section requirements for **Enterprise Architecture Documents (EAD)** within the Scnehaux architecture registry. 

EADs represent the C1 global context layer of the C4 metamodel. They establish the "North Star" directives, cross-domain standardization principles, and strategic alignment boundaries that govern all downstream Platform Architecture Documents (PADs) and System Architecture Documents (SADs). EADs are structured strictly around the four core TOGAF architecture domains:
- **Business Architecture (EAD-001)**: Establishes capability-centric blueprints, mapping domain boundaries strictly to business capabilities.
- **Data Architecture (EAD-002)**: Governs system-of-record boundaries, data sovereignty, sharing constraints, and storage paths.
- **Application Architecture (EAD-003)**: Establishes integration patterns, security boundaries, and the UI platform composition patterns.
- **Technology Architecture (EAD-004)**: Defines the paved road for languages, bundlers, compilers, and cloud-native execution runtimes.

---

## 2. Policy Framework

### 2.1 Document Template Schema

All EAD files must use the prefix `EAD-` (e.g. `EAD-001-business-architecture.md`) and must contain the following structural sections in the exact order shown:

#### 2.1.1 YAML Metadata Header
Every EAD must begin with a YAML frontmatter block containing these fields:
```yaml
---
doc_meta:
  id: EAD-XXX                         # Unique sequential ID (e.g. EAD-001)
  title: [Document Title]             # Descriptive title of the EAD
  owner: [Principal Architect/Role]   # Authoritative owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: public              # public | internal | restricted
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
---
```

#### 2.1.2 Section 1: Context & Business Drivers
- **Objective**: Explain the organizational "Why" behind the enterprise standard, mapping it to concrete business outcomes, constraints, and strategic goals.
- **Requirement**: Must explicitly link technical strategy to business capabilities. Detailed sections must trace constraints to external regulatory compliance (e.g., GDPR, SOC2) and internal business outcomes.

#### 2.1.3 Section 2: Enterprise Principles
- **Objective**: Establish the non-negotiable, immutable rules that guide all downstream architectural designs.
- **Requirement**: Principles must be stated as rules and must adhere to a strict three-part schema:
  - **Statement**: A clear, unambiguous description of the rule.
  - **Rationale**: The business or engineering reason for the principle.
  - **Implication**: The direct downstream development and operational requirements.

#### 2.1.4 Section 3: Strategic Architecture
- **Objective**: Provide macro-level capability models, long-term evolutionary trajectories, and high-level structural diagrams.
- **Requirement**: Must outline target state boundaries and define the transition horizons:
  - **Horizon 1 (Current State/Tactical)**: The currently active and supported architecture.
  - **Horizon 2 (Transition/Medium-Term)**: Planned intermediate states, migrations, and structural evolution pathways.
  - **Horizon 3 (Target State/Strategic North Star)**: The final optimized target architecture.
  Visual C1/C2 diagrams mapping domain/capability boundaries are mandatory.

#### 2.1.5 Section 4: Cross-Cutting Standards
- **Objective**: Mandate rules applicable to all domains and platforms (e.g., universal API error formats, central logging specifications, data retention baselines).
- **Requirement**: Rules must be actionable, prescriptive, and testable by automated fitness functions. All SLA and NFR baselines must be quantified (e.g., latency targets, availability, database recovery bounds).

#### 2.1.6 Section 5: Decision Log
- **Objective**: Record major strategic pivots, accepted trade-offs, and their enterprise-wide ramifications.
- **Requirement**: Each log entry must list the date, decision maker, and a reference to the related global or domain ADR (e.g. `ADR-GLB-001`, `ADR-UIP-TKN-001`).

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

#### 3.1.1 Structural Audit
The automated pipeline will verify that all EAD files contain the metadata header and the five mandatory sections. Missing sections or incorrect YAML format will fail the build.

#### 3.1.2 Quality Checklist
- Technical statements must be quantified.
- Ambiguous marketing terms (e.g., highly-scalable or blazing-fast) are prohibited.
- All enterprise principles must conform to the 3-part schema (Statement, Rationale, Implication).

## 4. Severity & Exceptions

### 4.1 Exception Waiver Protocol

#### 4.1.1 Waiver Approval
Deviations from EAD structures or principles require an approved project Exception ADR and ARB waiver sign-off.

#### 4.1.2 Waiver Life-Cycle
Approved waivers have a maximum validity of 365 days, after which they must be re-evaluated or remediated.

