---
doc_meta:
  id: GDC-006
  title: Technical Design Document (TDD) Guideline
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-06-01
---

# Technical Design Document (TDD) Guideline

## 1. Context & Scope

This guideline defines the mandatory structure, metadata schema, and section requirements for **Technical Design Documents (TDD)** within the Scnehaux architecture registry. 

TDDs represent the component-level (C3) blueprints, API contracts, ERDs, security boundaries, and failure handling mechanisms for specific implementations before code is written.

---

## 2. Policy Framework

### 2.1 Document Template Schema

All TDD files must use the prefix `TDD-` (e.g. `TDD-SCNX-IAM-GO-SECURITY-003.md`) and must contain the following structural sections in the exact order shown:

#### 2.1.1 YAML Metadata Header
Every TDD must begin with a YAML frontmatter block containing these fields:
```yaml
---
doc_meta:
  id: TDD-[REPO]-[COMPONENT]-[Seq]    # Unique system ID
  title: [Component Title]            # Descriptive title of the component
  owner: [Engineer/Role]              # Authoritative owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: internal            # public | internal | restricted
  parent_sad: DOC-S-XXX               # Referencing the Parent SAD ID
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
---
```

#### 2.1.2 Section 1: Context & Requirements
- **Objective**: Define the upstream and downstream context, what the feature accomplishes, and the specific functional requirements.
- **Requirement**: Must link to the Parent SAD to provide high-level traceability.

#### 2.1.3 Section 2: Design Details
- **Objective**: Provide the C3 component blueprints. Include sequence diagrams, internal interactions, and structural class/module design.
- **Requirement**: Must be technology-specific and concrete.

#### 2.1.4 Section 3: API / Schema Contracts
- **Objective**: Outline the exact payloads, database schemas (ERD), API endpoints, or event formats.
- **Requirement**: Must explicitly define data models, constraints, and validation rules.

#### 2.1.5 Section 4: Security & Privacy
- **Objective**: Detail how PII is handled, what specific RBAC or RLS policies apply, and encryption requirements.
- **Requirement**: Must align with global and domain-specific security standards.

#### 2.1.6 Section 5: Failure Handling
- **Objective**: Describe component-level retries, circuit breakers, degradation, and edge case mitigation.
- **Requirement**: Must be mapped to the SAD Blast Radius.

#### 2.1.7 Section 6: Observability
- **Objective**: Document exact metric names, log formats, and distributed tracing spans that will be emitted.
- **Requirement**: Must adhere to global observability guidelines.

#### 2.1.8 Section 7: Testing Strategy
- **Objective**: Outline unit, integration, and E2E testing approaches.
- **Requirement**: Must mention edge cases and security testing.

#### 2.1.9 Section 8: Rollout Strategy
- **Objective**: Document feature flags, rollout phases, schema migration steps, and backward compatibility.
- **Requirement**: Must detail rollback procedures.

#### 2.1.10 Conditional Sections (As Required)
- **Alternatives Considered**: Analysis of alternate paths rejected during review.
- **Compatibility Strategy**: Detailed backward compatibility plans for API changes.

### 2.2 TDD Fate Matrix

TDDs are ephemeral. Their lifecycle must follow the **Ephemeral TDD Matrix**:

- **Class A (Strategic Transition)**: Designs governing core architectural shifts, major security FSMs, or schema migrations. Preserved permanently under `docs/06-designs/historical/` for forensic and audit value.
- **Class B (Component & Feature Detail)**: Standard feature implementation layouts. Folded into the parent SAD and the physical TDD file is deleted once verified in production.
- **Class C (Exploratory & Spike)**: Prototype or exploratory designs. Deleted immediately after the Pull Request merges.

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Structural Audit**: The automated pipeline will verify that all TDD files contain the metadata header and the mandatory sections. Missing sections or incorrect YAML format will fail the build.
2. **Traceability**: The linter ensures that a `parent_sad` attribute exists in the TDD metadata, preventing isolated or "orphan" components.

## 4. Severity & Exceptions

### 4.1 Exception Waiver Protocol
- Deviations from TDD structures or the TDD Fate Matrix require an approved Exception ADR.
