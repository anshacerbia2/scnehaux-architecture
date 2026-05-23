---
doc_meta:
  id: ADR-E000
  title: ADR-E000 Architectural Governance Taxonomy & Methodology
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# ADR-E000: Architectural Governance Taxonomy & Methodology

---

## 1. Title
Enterprise-wide Adoption of the Context-Aware Documentation Governance Standard (GDC/EAD/PAD/SAD/TDD)

## 2. Status
Accepted

## 3. Context
The Scnehaux Foundation requires a unified documentation and governance standard to ensure architectural artifacts are consistent, auditable, and scalable across multiple projects. Historically, lacking a formal taxonomy led to documentation fragmentation, where strategic vision was lost in implementation details, different teams used inconsistent templates, and architectural drift went unchecked.

## 4. Decision
We officially establish the **Context-Aware Documentation Governance Standard (GDC/EAD/PAD/SAD/TDD)** as the mandatory architecture definition framework. 

This model integrates structural boundaries and semantic compliance into a unified multi-layer hierarchy:
1.  **Layer 1 (00-governance / GDC)**: Automated policy definitions and compliance gates.
2.  **Layer 2 (01-enterprise / EAD)**: The Strategic Layer mapping to the **4 Core TOGAF Domains** (Business, Data, Application, Technology).
3.  **Layer 3 (02-platform / PAD)**: Cohesive platform-level horizontal architecture documents (`*.pad.md`).
4.  **Layer 4 (03-applications / SAD)**: Cohesive application-level vertical software architecture blueprints (`*.sad.md`).
5.  **Layer 5 (04-decisions & 05-standards / ADR & STD)**: Architectural decisions and granular paved road standards.
6.  **Project Level (TDD)**: Concrete Technical Design Documents residing close to codebase repositories.

## 5. Rationale
Adopting this cohesive metamodel eliminates "magic decisions" and guarantees that every technical implementation can be traced back to strategic business capabilities and enterprise principles. By rejecting the bloated, generic *arc42 Standard-16* template for all layers and replacing it with specialized, high-density, context-aware templates, we reduce writer fatigue while ensuring maximum relevance for the target audience.

## 6. Alternatives Considered

### Alternative A: Wiki-Only Documentation (Confluence/Notion)
*   **Pros**: Low barrier to entry, easily editable.
*   **Cons**: Lack of structured version control, impossible to automate compliance checks via CI/CD, high risk of stale data and structural fragmentation.
*   **Why Rejected**: Fails to meet the grade 10/10 automated audit and traceability requirements.

### Alternative B: Strict arc42 "Standard-16" Globally
*   **Pros**: Standardized industry template.
*   **Cons**: Introduces massive redundancy (e.g., repeating Context, Problem Statement, and Scope across every microservice and strategy).
*   **Why Rejected**: Deprecated due to high documentation bloat and lack of specific context adaptation.

## 7. Consequences

### Positive
- **Automated Validation**: High-performance automated audits via the CI/CD pipeline using the custom python `linter.py` and `linting-rules.yaml`.
- **Zero Drift**: Mandating single cohesive files for PAD and SAD (rather than folder-based file fragmentation) eliminates internal context synchronization drift.
- **Traceability**: All downstream technical documents must trace back to explicit strategic decisions.

### Negative
- **Onboarding Friction**: New team members must learn the specific document metadata and section boundaries.

### Tradeoffs
- We sacrifice generic "wiki-style" flexibility in exchange for strict, lint-enforced structural consistency.

### Operational Impact
- Automated CI pipeline runs linting on every Pull Request, blocking merges if metadata is missing or if prohibited words (e.g., `TBD`, `should consider`) are present.

### Security Impact
- Ensures that sensitive structural data is classified correctly (`classification: restricted` or `public`) at the document metadata level.

### Scalability Impact
- As the engineering organization grows, the boundary between platform (Layer 3) and application (Layer 4) remains clear, avoiding boundary contamination.

## 8. Risks
- **Documentation Overhead**: Developers might view documentation as a bottleneck. 
  - *Mitigation*: Solved by providing auto-scaffolded templates, a local dry-run linter, and pre-configured HSL tokens.

## 9. Implementation Notes
- The DGS and linter rules are set to `version: 1.0.0` as the authoritative baseline.
- `linter.py` must run as a pre-commit hook and as an automated GitHub Action gate.

## 10. Related Documents
- [Documentation Governance Standard (GDC-000)](file:///d:/Ansha/architecture-description/scnehaux-architecture/00-governance/documentation-governance-standard.md)
- [Documentation Quality Framework (GDC-001)](file:///d:/Ansha/architecture-description/scnehaux-architecture/00-governance/documentation-quality-framework.md)
- [Enterprise Architecture Governance Root README](file:///d:/Ansha/architecture-description/scnehaux-architecture/README.md)
