---
doc_meta:
  id: GDC-004
  title: Architecture Decision Record (ADR) Guideline
  owner: Principal Software Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Architecture Decision Record (ADR) Guideline

## 1. Context & Scope

This guideline establishes the mandatory lifecycles, metadata structures, repository locations, index requirements, and exception waiver workflows for all Architectural Decision Records (ADRs) within the Scnehaux enterprise.

It applies to all engineers, product leads, and architects documenting system decisions across global and local repository contexts.

---

## 2. Policy Framework

### 2.1 ADR & Standard Lifecycles (Maturity Model)

Every architectural decision and standard must progress through a managed, auditable lifecycle.

#### 2.1.1 ADR Lifecycle
An ADR must exist in one of five explicit states:

```
    [Proposed] ──► [Accepted] ──► [Superseded]
         │              │
         ▼              ▼
    [Rejected]     [Deprecated]
```

- **Proposed**: The decision is drafted and undergoing active peer review. It carries no authority.
- **Accepted**: The decision has been reviewed, approved by the designated authority, and is active.
- **Rejected**: The decision has been evaluated and declined. The record remains as historical context.
- **Superseded**: The decision has been replaced by a newer ADR. The newer ADR must explicitly reference the superseded record by ID.
- **Deprecated**: The decision is no longer recommended or valid, but has not been directly replaced.

#### 2.1.2 Standard Maturity Model
To prevent rigid compliance grids, every enterprise standard must declare one of four maturity phases:
- **Assessed (Evaluation)**: The standard is experimental or undergoing evaluation. Teams are encouraged to run pilots, but adoption is optional. No waivers are required to deviate.
- **Trial (Limited Adoption)**: The standard is verified in pilot programs. It is recommended for new services, but existing services are exempt.
- **Adopted (Default Mandate)**: The standard is the default mandatory baseline. Deviations require an approved exception waiver.
- **Hold (Retirement)**: The standard is deprecated. New implementations are prohibited from adopting it. Existing implementations must schedule a migration path to replacement systems within `180 days`.

#### 2.1.3 Standard Sunset & Deprecation Strategy
When a standard technology or library decays (e.g. library obsolescence or deprecation by vendors):
1. **Sunset Recommendation**: The Architecture Review Board (ARB) initiates a review and transitions the standard state to `Hold`.
2. **Migration Path Mapping**: The ARB must publish a companion Migration Guide or a successor standard (`Adopted` or `Trial`) within `30 days` of the transition.
3. **Grace Window**: Active projects have a maximum of `180 days` to sunset the legacy standard, after which compliance check warnings escalate to CI blocks.

### 2.2 Mandatory ADR Schema

Every ADR must utilize the standard Markdown template and include the following metadata and sections:

#### 2.2.1 Metadata Frontmatter
```yaml
doc_meta:
  id: ADR-GLB-[Seq] | ADR-[DOM]-[CAP]-[Seq]  # e.g. ADR-GLB-001 or ADR-UIP-TKN-001
  title: Short Descriptive Title
  status: proposed | accepted | rejected | superseded | deprecated
  created: YYYY-MM-DD
  approved_by: Lead Architect Name
  deciders: [Name1, Name2]
```

#### 2.2.2 Required Document Sections
1. **Title**: The ADR ID and a descriptive title header.
2. **Status Table**: Chronological table tracking state transitions, deciders, and approval timestamps.
3. **Context & Problem Statement**: The technical problem, constraints, and business requirements driving the decision.
4. **Decision**: The chosen course of action with concrete, binding statements.
5. **Consequences**: The positive, negative, and operational tradeoffs resulting from the decision.
6. **Alternatives Considered**: A brief analysis of alternate paths rejected during review.

### 2.3 Repository Management & Indexing Invariants

- **Location**: Enterprise ADRs must reside in the `/05-adr` directory of the architecture-description repository, grouped by Bounded Context (e.g., `/05-adr/_global/` or `/05-adr/ui-platform/`). Local project ADRs remain in `packages/docs/04-decisions` of local workspaces.
- **Naming Conventions**: Files must be named sequentially within their context: `ADR-GLB-[Sequence]-[slug].md` for global decisions and `ADR-[DOMAIN]-[CAPABILITY]-[Sequence]-[slug].md` for domain-level enterprise decisions. Local project decisions use `ADR-[SYSTEM]-[DOMAIN]-[NUMBER]-[slug].md`.
- **Unified Index**: Every repository must maintain a root-level index catalog linking to every ADR with its current status. The index must be updated prior to merging any new ADR.

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Commit Hook Checks**: Pre-commit hooks must scan new ADR files to verify that the YAML frontmatter contains valid fields and matches the schema defined in Section 2.2.1.
2. **Waiver Expiration Tracking**: The CI pipeline must compile a report of all active waiver ADRs, raising critical warnings for any waiver within `30 days` of expiration.
3. **Audit Trail**: Every merged ADR must be signed using Git commits. Manual database or document overrides of approval states are prohibited.

### 3.2 Rule Conflict Resolution Matrix

When multiple mandatory standards collide during implementation, the following priority tree governs the outcome (highest priority wins):

1. **Security & Data Compliance** (e.g., Encryption-at-rest, PII isolation, RLS rules).
2. **System Resilience & Stability** (e.g., Circuit breakers, load shedding limits).
3. **Observability & Auditability** (e.g., Audit trail logs, telemetry trace injection).
4. **Operational Performance** (e.g., Frame rate rendering target, latency budgets).
5. **Developer Experience & Scaffolding** (e.g., Directory styles, compiler version selection).

*Exception Rule*: Performance must not override Security on public network boundaries. Performance is permitted to override Audit tracing only for isolated, local high-frequency loop executions (e.g., local state evaluation).

---

## 4. Severity & Exceptions

### 4.1 Exception Waiver & Governance Framework

To resolve conflicts and handle deviations, teams utilize waivers, conflict resolution matrices, and applicability rules.

### 4.2 Applicability Criteria Framework

To prevent excessive exception waivers, standards must not apply absolute mandates unconditionally. Standards must declare an **Applicability Criteria Matrix**:
- **Team Size Metric**: Tooling frameworks (e.g., Module Federation) are `Adopted` only if the team count is greater than `3` and independent deployments are required. Otherwise, standalone deployments are `Recommended`.
- **System Scale Metric**: Advanced scaling patterns (e.g., read replicas, microservices partition keys) are `Trial` or `Hold` by default and become `Adopted` only when query throughput exceeds defined performance metrics (e.g., >5000 read QPS).

### 4.3 Exception Waiver Procedure

When a team must deviate from a mandatory engineering standard (e.g. using an uncertified database engine or violating a frontend layer constraint):
- **Waiver Request Initiation**: The requesting team must draft a dedicated local project ADR detailing the deviation, the specific standard rule being bypassed, and the mitigation strategies implemented.
- **Approval Authority Matrix**:
  - *Tier 1 Deviation (High Impact - Database, Core Security)*: Requires unanimous sign-off from the Architecture Review Board (ARB).
  - *Tier 2 Deviation (Medium Impact - Frontend Stack, Observability)*: Requires approval from the Principal Architect of the domain.
  - *Tier 3 Deviation (Low Impact - Custom Helpers, Internal Tooling)*: Requires approval from the Lead System Engineer.
- **Time-Bound Review Commitments**: The reviewing authority must issue an official decision (Approved, Rejected, or Request Info) within `5 business days` of the waiver ADR submission.
- **Auditing and Expiration**: Approved waivers must carry an expiration date not exceeding `365 days` from approval. The team must re-submit the waiver for review annually or execute the migration path back to standard compliance.
