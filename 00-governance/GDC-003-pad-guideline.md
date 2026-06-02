---
doc_meta:
  id: GDC-003
  title: Platform Architecture Document (PAD) Guideline
  owner: Principal Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Platform Architecture Document (PAD) Guideline

## 1. Context & Scope

This guideline defines the mandatory structure, metadata schema, and section requirements for **Platform Architecture Documents (PAD)** within the Scnehaux architecture registry. 

PADs represent the logical capability definitions, domain boundaries, and conceptual integration rules for all business domains and applications. They serve as the design-time single source of truth (SSOT) for domain-level contracts before physical container systems (SADs) are built, while concrete API integration documents are generated and consumed downstream via Web Developer Portals.

---

## 2. Policy Framework

### 2.1 Document Template Schema

All PAD files must use the suffix `.pad.md` (e.g. `identity-platform.pad.md`) and must contain the following structural sections in the exact order shown:

#### 2.1.1 YAML Metadata Header
Every PAD must begin with a YAML frontmatter block containing these fields:
```yaml
---
doc_meta:
  id: DOC-P-XXX                       # Application capability ID
  title: [Application Title]          # Descriptive title of the Application
  owner: [Domain Team/Role]           # Authoritative team owner
  version: 1.0.0                      # Semantic versioning format
  status: approved                    # proposed | approved | deprecated
  classification: public              # public | internal | restricted
  fulfilled_by:                       # List of physical SAD IDs fulfilling this application capability
    - DOC-S-XXX
  review_cycle_days: 180              # Review cycle period
  last_reviewed: YYYY-MM-DD           # Last audit date
---
```

#### 2.1.2 Section 1: Application Capability
- **Objective**: Define the business value, bounded context, and macro-level features that define this application capability.
- **Requirement**: Must remain technology-agnostic. Focus on logical boundaries rather than libraries or infrastructure.

#### 2.1.3 Section 2: Trust Boundary & Security
- **Objective**: Map the isolation levels, identity propagation (e.g., Zero Trust), data encryption, and tenant separation models.
- **Requirement**: Detail how user contexts and application credentials traverse system boundaries.

#### 2.1.4 Section 3: Integration Contract
- **Objective**: Specify strict API contracts, required proprietary headers (e.g., `Scnehaux-Account`), and authentication handshakes.
- **Requirement**: Must define retry envelopes and payload validation standards for external clients.

#### 2.1.5 Section 4: Strategic Architecture
- **Objective**: Illustrate the C1/C2 macro-topology and its relationship with other enterprise systems.
- **Requirement**: Must contain a clean structural diagram (such as Mermaid or similar) mapping domains.

#### 2.1.6 Section 5: Quality Attributes
- **Objective**: Explicit, quantifiable Non-Functional Requirements (NFR) targets.
- **Requirement**: Must quantify metrics (e.g., "99.99% Availability", "P95 Latency < 200ms", "Maximum throughput of 5000 req/s").

#### 2.1.7 Conditional Sections (As Required)
- **Assumptions**: Document any external dependencies or business assumptions.
- **Alternatives Considered**: Document technical alternatives evaluated and the trade-offs that led to the selected pattern.
- **Data Classification**: Detail sensitivity levels of data processed by the platform.

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Logical Boundary Isolation**: The linter will flag any PAD that hardcodes physical server names, specific deployment ports, database index structures, or specific library versions.
2. **Quantification Rule**: Any metric listed in the Quality Attributes section must be expressed with units (e.g., ms, req/s, %). Generic terms are prohibited.

## 4. Severity & Exceptions

### 4.1 Exception Waiver Protocol
- Deviations from Platform Architecture requirements or schemas require an approved project Exception ADR and ARB waiver sign-off.
- Approved waivers have a maximum validity of 365 days.
