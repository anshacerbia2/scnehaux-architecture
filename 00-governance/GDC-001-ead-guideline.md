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

EADs represent the "North Star" directives, cross-domain standardization principles, and strategic alignment boundaries that govern all downstream platform capability designs and software applications.

---

## 2. Policy Framework

### 2.1 Document Template Schema

All EAD files must use the prefix `EAD-` (e.g. `EAD-001-Business-Architecture.md`) and must contain the following structural sections in the exact order shown:

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
- **Requirement**: Must explicitly link technical strategy to business capabilities.

#### 2.1.3 Section 2: Enterprise Principles
- **Objective**: Establish the non-negotiable, immutable rules that guide all downstream architectural designs.
- **Requirement**: Principles must be stated as rules (e.g. "Single Source of Truth", "Secure by Default") accompanied by brief rationales.

#### 2.1.4 Section 3: Strategic Architecture
- **Objective**: Provide macro-level capability models, long-term evolutionary trajectories, and high-level structural diagrams.
- **Requirement**: Must outline the target state architecture and transition horizons.

#### 2.1.5 Section 4: Cross-Cutting Standards
- **Objective**: Mandate rules applicable to all domains and platforms (e.g., universal API error formats, central logging specifications, data retention baselines).
- **Requirement**: Rules must be actionable, prescriptive, and testable by automated fitness functions.

#### 2.1.6 Section 5: Decision Log
- **Objective**: Record major strategic pivots, accepted trade-offs, and their enterprise-wide ramifications.
- **Requirement**: Each log entry must list the date, decision maker, and a reference to the related ADR.

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Structural Audit**: The automated pipeline will verify that all EAD files contain the metadata header and the five mandatory sections. Missing sections or incorrect YAML format will fail the build.
2. **Quality Checklist**:
   - Technical statements must be quantified.
   - Ambiguous marketing terms (e.g., highly-scalable or blazing-fast) are prohibited.

## 4. Severity & Exceptions

### 4.1 Exception Waiver Protocol
- Deviations from EAD structures or principles require an approved project Exception ADR and ARB waiver sign-off.
- Approved waivers have a maximum validity of 365 days.
