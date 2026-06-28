---
doc_meta:
  id: GDC-006
  title: Governance Document Contract (GDC) Guideline
  owner: Architecture Review Board (ARB)
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-06-14
---

# Governance Document Contract (GDC) Guideline

## 1. Context & Scope

In accordance with the **Eat Our Own Dog Food** maxim defined in `GDC-000`, the Governance framework must subject itself to the exact same rigorous validation criteria it imposes on downstream architectures. 

This document defines the structural, taxonomic, and qualitative rules governing **Governance Document Contracts (GDC)** themselves. Any file prefixed with `GDC-` must strictly adhere to the schemas and lifecycles defined herein.

---

## 2. Policy Framework

All meta-level governance documents (GDC) must strictly adhere to the defined metadata schema and the document body structure.

### 2.1 The Linter Ruleset (Machine-Readable)

In addition to the global structural enforcement defined in **[GDC-002](./GDC-002-compliance-engine.md)**, Governance Document Contracts (GDC) are strictly governed by the following domain-specific linter components:

> [!WARNING]
> **DO NOT EDIT THIS TABLE MANUALLY.**
> This table is automatically generated from the domain ruleset (`linting-rules-gdc.yaml`).
> If you need to update a rule, modify the YAML file and run:
> `python scripts/generate_rules_doc.py`

<!-- AUTO-GENERATED-RULES:START -->
| Rule Category | Parameter | Enforcement / Value |
| :--- | :--- | :--- |
| **Metadata** | Filename Pattern | `^GDC-\d{3}-[a-z0-9-]+\.md$` |
| **Metadata** | Required Fields | <ul><li>`id`</li><li>`title`</li><li>`governed_by`</li><li>`owner`</li><li>`version`</li><li>`status`</li><li>`classification`</li><li>`review_cycle_days`</li><li>`last_reviewed`</li></ul> |
| **Metadata** | Optional Fields | <ul><li>`tags`</li><li>`aliases`</li><li>`contributors`</li></ul> |
| **Metadata** | Version Format | `semver` |
| **Metadata** | Allowed Classifications | <ul><li>`public`</li><li>`internal`</li><li>`restricted`</li><li>`confidential`</li></ul> |
| **Metadata** | Allowed Statuses | <ul><li>`approved`</li><li>`draft`</li></ul> |
| **Structure** | Required Sections | <ul><li>`Context & Scope`</li><li>`Policy Framework`</li></ul> |
| **Structure** | Optional Sections | <ul><li>`Enforcement Mechanism`</li><li>`Enforcement Mechanism & Rule Reconciliation`</li><li>`Severity & Exceptions`</li><li>`Document Types (Glossary of Truth)`</li><li>`Document Lifecycle & State Management`</li><li>`Linter Execution Flow (CI/CD Automated Gate)`</li><li>`Compliance & Enforcement`</li><li>`The Git Workflow & Access Control`</li><li>`The Reconciliation Flow (Adding or Modifying Rules)`</li><li>`Directory Structure & Taxonomy`</li><li>`Directory Structure & Naming Conventions`</li><li>`Document Template Schema (Metadata Frontmatter)`</li><li>`Document Section Semantics`</li><li>`Metadata Schema Properties`</li><li>`Semantic Definitions`</li><li>`Allowed Lifecycle Statuses`</li><li>`Allowed Classifications`</li><li>`Semantic Versioning Classification`</li><li>`Appendix: Architectural Clarifications & Trade-Offs`</li><li>`Appendix: Architectural Trade-Offs`</li></ul> |
| **Structure** | Required Downstream Guideline Subsections | **Semantic Definitions**: <ul><li>`Naming Conventions`</li><li>`Taxonomy`</li><li>`Directory Structure`</li><li>`Metadata Schema Properties`</li><li>`Document Section`</li></ul><br>**Metadata Schema Properties**: <ul><li>`Allowed Lifecycle Statuses`</li><li>`Allowed Classifications`</li><li>`Semantic Versioning Classification`</li></ul> |
<!-- AUTO-GENERATED-RULES:END -->

| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-gdc.yaml` | Specific `review_cycle_days`, strict metadata, and policy structure. |
| **Python Engine** | `validators/gdc.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications` ensuring proper baseline governance. |

### 2.3 Semantic Definitions

The Linter Ruleset above strictly enforces the syntax and allowed values. This section defines the human-readable semantics and guidelines for those constraints.

#### 2.3.1 Naming Conventions

The filename must strictly adhere to the `gdc_pattern` regex: `^GDC-\d{3}-[a-z0-9-]+\.md$`.
If a GDC is acting as a downstream guideline, its name must end with `-guideline.md`.

#### 2.3.2 Taxonomy

All GDC documents must be placed strictly in the `00-governance/` directory. Subdirectories are allowed for supplementary rules (e.g., `00-governance/rules/`).

#### 2.3.3 Directory Structure

```text
scnehaux-architecture/
└── 00-governance/
    ├── rules/
    │   └── linting-rules-gdc.yaml
    └── GDC-002-compliance-engine.md
```

#### 2.3.4 Metadata Schema Properties

| Metadata Field | Type | Description / Purpose |
|---|---|---|
| `id` | String | Unique identifier (e.g., `GDC-000`). |
| `title` | String | Descriptive title of the document. |
| `owner` | String | Lead Owner (e.g., ARB). |
| `version` | String | Must comply with Semantic Versioning (e.g., 1.0.0). |
| `status` | Enum | The current lifecycle state (Refers to Allowed Lifecycle Statuses). |
| `classification` | Enum | The data sensitivity (Refers to Classification Semantics below). |
| `review_cycle_days` | Integer | The frequency in days for required review. |
| `last_reviewed` | Date | The date of the last formal review (YYYY-MM-DD). |

##### Allowed Lifecycle Statuses

| Status | Meaning / Lifecycle Stage |
|---|---|
| `draft` | The document is currently being written or reviewed and is not yet enforceable. Exempt from linter scoring. |
| `approved` | The document has been formally reviewed and approved by the ARB. Its policies are now active and enforceable. |

##### Allowed Classifications

While the exact string values are enforced by the CI Linter, their semantic meanings are:

| Classification | Meaning / Data Sensitivity |
|---|---|
| `public` | Available to anyone. |
| `internal` | Restricted to company employees. |
| `restricted` | Restricted to specific teams or roles. |
| `confidential` | Highly sensitive information restricted to a strict need-to-know basis. |

##### Semantic Versioning Classification

| Version | Trigger / Architectural Change |
|---|---|
| **Major (2.0.0)** | Breaking rule changes, introducing new strict policies. |
| **Minor (1.1.0)** | Adding new optional guidelines or non-breaking constraints. |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, fixing dead links. |

#### 2.3.5 Document Section

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name | Purpose / Content Requirement |
|---|---|
| **Context & Scope** | Defines the boundaries, objectives, and scope of the governance policy. |
| **Policy Framework** | Documents the core guidelines, philosophies, schemas, or models being established. |
| **Enforcement Mechanism** | (Optional) Redefine ONLY if the document has domain-specific linter rules. |
| **Severity & Exceptions** | (Optional) Redefine ONLY if the document explicitly blocks waivers or alters severity scaling. |
| **Document Types (Glossary of Truth)** | (Optional) Defines the glossary of truth. |
| **Document Lifecycle & Statuses** | (Optional) Defines the lifecycle statuses. |

### 2.4 Document Lifecycle & Statuses

#### 2.4.1 Git-Centric Audit Trail (No Backdoor Approvals)

A governance document (whether GDC, EAD, SAD, PAD, STD, TDD, or ADR) is only considered 'Approved' or 'Accepted' when it is formally reviewed and merged via a Git Pull Request. You must not manually change the document's status without a PR, nor use external tools (like Jira or Confluence) as proof of approval. The Git commit history is the only recognized proof.

### 2.5 The Downstream Guideline Interface

If a Governance Document Contract (GDC) is specifically authored to serve as a **Guideline** governing a downstream architectural document type (e.g., EAD, PAD, SAD, STD, ADR, TDD), it is legally bound to the "Downstream Guideline Interface".

To be recognized by the Linter as a Downstream Guideline, the document's filename **MUST** end with the suffix `-guideline.md` (e.g., `GDC-009-pad-guideline.md`).

Any GDC adopting this interface must explicitly define the following 4 structural pillars to completely eradicate implicit knowledge:

1. **Taxonomy & Directory Structure**: Must define exactly where the downstream documents are allowed to be physically stored (e.g., root repo vs project repos).
2. **Naming Conventions**: Must define the exact Regex pattern the downstream document filenames must adhere to.
3. **Document Section Semantics**: Must explicitly list all required and optional markdown `##` sections the downstream document must contain.
4. **Metadata Schema Properties**: Must define the precise YAML frontmatter (`doc_meta`) schema required for the downstream document.

---

## 3. The Reconciliation Flow (Adding or Modifying Rules)

If you need to introduce a new constraint or modify an existing rule across any of the architecture documents, you must follow this exact flow to maintain the integrity of the CI/CD linter:

1. **Codify the Rule**: Do not edit the Markdown guidelines directly. Instead, encode the rule into the machine-readable format.
   - For declarative constraints (e.g., required sections, metadata schemas, allowed formats), edit the appropriate `00-governance/rules/linting-rules-[type].yaml`.
   - For complex dynamic logic, modify the corresponding Python validator in `validators/`.
2. **Reconcile Documentation (Generate, Don't Duplicate)**: To maintain the Single Source of Truth (SSOT), the human-readable markdown tables inside the Guideline documents must be synchronized with the YAML. You **MUST** regenerate the documentation by executing:
   ```bash
   python scripts/generate_rules_doc.py
   ```
3. **Update Semantic Definitions**: The automated script only updates the machine-readable table. You **MUST** manually update the Semantic Definitions section in the corresponding Guideline document to explain the "Why" and "How" behind your new constraints for human readers.
4. **Qualitative Synchronization (Human Governance)**: If your rule modification impacts the qualitative evaluation of architecture (e.g., prohibiting new vague terms, demanding new quantitative NFR metrics, or altering risk disclosure requirements), you **MUST** also manually synchronize the human-driven governance artifacts:
   - Update `GDC-003-quality-rubric.md` (The 10-Parameter Qualitative Benchmark).
   - Update `review-score-sheet-template.md` (The ARB Peer-Review Execution Tool).

Failure to follow this reconciliation flow will result in Documentation Drift and a rejected Pull Request.

---

## 4. Enforcement Mechanism

In addition to the global structural enforcement defined in `GDC-002`, GDC documents are strictly governed by the following domain-specific linter components:

| Linter Component | File | Enforcement Logic |
| :--- | :--- | :--- |
| **Domain Ruleset** | `rules/linting-rules-gdc.yaml` | Specific `review_cycle_days`, strict metadata, and policy structure. |
| **Python Engine** | `validators/gdc.py` | **Taxonomy**: Validates `allowed_statuses` and `allowed_classifications` ensuring proper baseline governance. |

---

## 5. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the ARB explicitly documents the compromises of this GDC Guideline:

1. **Self-Referential Linter Rules vs Hardcoded Engine Logic**
   - *Why rejected*: Writing specific logic in the main engine `linter.py` to validate `GDC` files pollutes the global execution engine with domain-specific concerns.
   - *The Trade-Off*: We accept the cognitive overhead of creating a specific `validators/gdc.py` module and a `linting-rules-gdc.yaml` to validate the files that define the rules themselves. In exchange, the global linter engine remains perfectly domain-agnostic, treating `GDC` files identically to `SAD` or `PAD` files during execution.
