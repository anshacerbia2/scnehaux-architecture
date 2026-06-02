---
doc_meta:
  id: GDC-005
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

### 2.1 ADR Taxonomy & Types

Every ADR must declare its `adr_type` to clarify the intent of the decision. The allowed types are:

| ADR Type | Purpose |
|---|---|
| **Foundational** | Makes a core architectural decision for the first time when no prior decision exists. |
| **Implementation** | Selects an implementation or option that is mandated/permitted by an STD. |
| **Exception** | Approves a deviation (waiver) against an active STD. |
| **Conflict Resolution** | Resolves conflicting constraints between an STD, ADR, or business requirement. |
| **Replacement** | Replaces a pre-existing architectural decision. |

### 2.2 STD vs ADR Implementation Scenarios

To resolve confusion on when to write an ADR vs an STD, teams must follow this matrix:

| Scenario | Global STD | Global ADR | Project ADR | Notes |
|---|---|---|---|---|
| Organization establishes a new enterprise-wide rule | ✅ Create | ⚠️ Optional | ❌ | Board can create an STD without an ADR |
| Organization selects an enterprise strategic platform/tech | ✅ Update/Create | ✅ Create | ❌ | E.g., React, PostgreSQL, Kubernetes |
| Organization adopts an external regulation | ✅ Create | ❌ Usually No | ❌ | PCI-DSS, ISO27001, GDPR |
| Organization resolves a conflict between enterprise standards | ✅ Update | ✅ Create | ❌ | Enterprise-level conflict resolution |
| Organization shifts enterprise architectural direction | ✅ Update | ✅ Create | ❌ | E.g., monolith → microservices |
| STD dictates a single, exclusive solution | ✅ Existing | ❌ | ❌ | Project simply complies |
| STD provides multiple approved options | ✅ Existing | ❌ | ✅ Create | Project selects an option |
| STD mandates a capability but does not specify a product | ✅ Existing | ❌ | ✅ Create | Project selects the implementation |
| Project adopts technology not covered by an STD | ❌ | ❌ | ✅ Create | Local architecture decision |
| Project makes a local, isolated decision | ❌ | ❌ | ✅ Create | E.g., adopting an internal library |
| Project deviates from an STD (waiver) | ✅ Existing | ❌ | ✅ Create | Exception decision |
| Multiple projects request the exact same waiver | ✅ Update | ✅ Create | Existing | Indicates the STD needs revision |
| Project faces a conflict between two STDs | ✅ Existing | ❌ | ✅ Create | Local conflict resolution |
| Conflict applies across the entire enterprise | ✅ Update | ✅ Create | ❌ | Global conflict resolution |
| Internal refactoring without architectural changes | ❌ | ❌ | ❌ | ADR not required |
| Minor version upgrades that don't alter architecture | ❌ | ❌ | ❌ | ADR not required |
| Replacing a strategic library in a single project | ❌ | ❌ | ✅ Create | E.g., Redux → Zustand |
| Replacing a strategic library enterprise-wide | ✅ Update | ✅ Create | ❌ | Enterprise migration |
| Project follows the STD fully without needing a choice | ✅ Existing | ❌ | ❌ | No decision necessary |

### 2.3 ADR Lifecycle

Every architectural decision must progress through a managed, auditable lifecycle. An ADR must exist in one of five explicit states:

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

### 2.3.1 The Immutability Principle
An ADR is a strict historical record. Once an ADR reaches the **Accepted** or **Rejected** state, its core substantive content (Context, Decision Drivers, Decision, Consequences) **MUST NEVER BE MODIFIED**. 
- If a decision needs to be reversed or fundamentally changed, you must create a **new ADR** (using the `replacement` type) and update the old ADR's status to `Superseded`. 
- **Administrative Exemption (Decoupled Execution)**: Strategic decisions (ADRs) are decoupled from tactical execution (STDs). An ADR may be approved before its corresponding Standard document is finalized. Appending hyperlinks to newly drafted Standards (STDs) or cross-referencing newer ADRs in the "Related Standards" section is classified as a metadata update and is explicitly permitted.
- Other permissible edits to an existing Accepted ADR include: updating the Status table to reflect a lifecycle transition, or fixing minor typographical errors that do not alter the technical context.

### 2.4 Mandatory ADR Schema

Every ADR must utilize the standard Markdown template and include the following metadata and sections:

#### 2.4.1 Metadata Frontmatter

##### 2.4.1.1 Enterprise Level (Root Repo)
```yaml
doc_meta:
  id: ADR-GLB-[Seq] | ADR-[DOM]-[CAP]-[Seq]  # e.g. ADR-GLB-001 or ADR-UIP-TKN-001
  title: Short Descriptive Title
  adr_type: foundational | implementation | exception | conflict_resolution | replacement
  status: proposed | accepted | rejected | superseded | deprecated
  created: YYYY-MM-DD
  created_by: Creator Name | [Name1, Name2]
```

##### 2.4.1.2 Project/Local Level (Project Repo)
```yaml
doc_meta:
  id: ADR-[REPO]-[COMPONENT]-[Seq]  # e.g. ADR-SCNX-IAM-GO-001 or ADR-UIP-AUTH-001
  title: Short Descriptive Title
  adr_type: foundational | implementation | exception | conflict_resolution | replacement
  status: proposed | accepted | rejected | superseded | deprecated
  created: YYYY-MM-DD
  created_by: Creator Name | [Name1, Name2]
  parent_sad: [Parent SAD ID]       # Optional: Mapped parent Software Architecture Document

  # Required ONLY if adr_type is "exception" (Waiver Approval)
  approved_by: [Sponsor/Approver Name or ARB]
  expiry_date: YYYY-MM-DD           # Waiver validity cap (max 365 days)
  risk_classification: low | medium | high
  exception_reason: Brief rationale explaining standard deviation
```

#### 2.4.2 Required Document Sections
1. **Title**: The ADR ID and a descriptive title header.
2. **Status**: Chronological table tracking state transitions (`Date`, `Status`), the `ADR Type`, the `Reviewers` (or SMEs) consulted, and the final `Approver`.
3. **Context**: The technical problem, constraints, and business requirements driving the decision.
4. **Decision Drivers**: The core technical and business factors forcing the decision.
5. **Decision**: The chosen course of action with concrete, binding statements.
6. **Consequences**: The results (Positive, Negative, Operational) of the decision.
7. **Compliance Impact**: Defines related standards, compliance status, and required waivers.
8. **Alternatives Considered**: Analysis of alternate paths rejected during review.

### 2.5 Repository Management & Indexing Invariants

- **Location**: Enterprise ADRs must reside in the `/05-decisions` directory of the architecture-description repository, grouped by Bounded Context (e.g., `/05-decisions/_global/` or `/05-decisions/ui-platform/`). Local project ADRs remain in `packages/docs/04-decisions` of local workspaces.
- **Naming Conventions**: Files must be named sequentially within their context: `ADR-GLB-[Sequence]-[slug].md` for global decisions and `ADR-[DOMAIN]-[CAPABILITY]-[Sequence]-[slug].md` for domain-level enterprise decisions. Local project decisions use `ADR-[SYSTEM]-[DOMAIN]-[NUMBER]-[slug].md`.
- **Unified Index**: Every repository must maintain a root-level index catalog linking to every ADR with its current status. The index must be updated prior to merging any new ADR.

---

## 3. Enforcement Mechanism

### 3.1 Compliance & Enforcement

1. **Commit Hook Checks**: Pre-commit hooks must scan new ADR files to verify that the YAML frontmatter contains valid fields and matches the schema defined in Section 2.2.1.
2. **Waiver Expiration Tracking**: The CI pipeline must compile a report of all active waiver ADRs, raising critical warnings for any waiver within `30 days` of expiration.
3. **Audit Trail**: Every merged ADR must be signed using Git commits. Manual database or document overrides of approval states are prohibited.

### 3.2 Rule Conflict Resolution Matrix

When multiple mandatory standards collide during implementation, the resolution priority tree defined in **[GDC-008 §3.1 — Rule Conflict Resolution Matrix](./GDC-008-architecture-lifecycle.md)** governs the outcome.

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
