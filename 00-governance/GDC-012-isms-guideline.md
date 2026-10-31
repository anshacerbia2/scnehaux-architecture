---
doc_meta:
  id: GDC-012
  title: Information Security Management System (ISMS) Guideline
  owner: Architecture Authority
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  created_date: 2026-10-31
  last_reviewed: 2026-10-31
---

# Information Security Management System (ISMS) Guideline

> **Pending ratification.** This guideline is a review candidate under GDC-000 §2.6.7. It carries no authority until the Architecture Authority approves this exact commit, and no ISMS record is merged before then.

## 1. Context & Scope

The organisation is building an information security management system (ISMS) aligned with ISO/IEC 27001:2022. The ISMS needs documented information: its scope, its policy and roles, its risk method, its risk register, its risk treatment plan and Statement of Applicability (SoA), its objectives, and the operational records that close the gaps between what the standard asks for and what the organisation already does. This guideline gives those records a governed home with the same Docs-as-Code guarantees as the architecture: Git history, pull-request review, and the Fitness Function.

It defines the `ISMS` artifact type: where records live, what each record holds, the frontmatter they declare, the vocabulary for a control's status, how often each record is reviewed, and the rules that keep a public repository safe to read.

### 1.1 Why ISMS Is Its Own Type

GDC-000 §1.3 places every artifact in exactly one domain. None of the seven existing domains fits an ISMS record:

- **Not a Standard (STD).** A Standard states a rule engineers follow. A risk register states the organisation's current exposure, and changes whenever the exposure does.
- **Not a Decision (ADR).** An ADR records one decision at one point in time. An SoA is re-evaluated every cycle, and its rows move between statuses as controls are built.
- **Not a design (EAD, PAD, SAD, TDD).** Designs describe systems at one C4 level. ISMS records describe how the organisation manages risk to those systems, and cite artifacts at every level as evidence.
- **Not a governance contract (GDC).** A GDC governs how documents are written. ISMS records are the subject matter of a management system, owned by its roles, not by the Architecture Authority.

### 1.2 Scope

In scope: the documented information that clauses 4 to 10 of ISO/IEC 27001:2022 and the Statement of Applicability call for, and the gap documents the ISMS needs to show a control operating.

Out of scope:

- the text of ISO/IEC 27001 or ISO/IEC 27002 (§2.1 rule 1);
- the evidence itself. Evidence stays in the repository where the control operates, and an ISMS record links to it (§2.5);
- technical rules engineers follow. Those belong in an STD, and the ISMS record links to the STD rather than restating it;
- secrets, personal data, and exploit detail (§2.1 rule 4).

### 1.3 Position in the SoC Matrix

GDC-000 §1.3 measures every domain on nine dimensions. The ISMS row and the reason for each value:

| Dimension            | ISMS value                                      | Why                                                                                                                                                                                   |
| :------------------- | :---------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Asset Owned**      | Information security management records         | The asset is the organisation's management of information security risk: scope, risks, control applicability and status, and the index of evidence. No architecture artifact owns it. |
| **Scope**            | ISMS scope (declared by the scope record)       | Clause 4.3 sets one scope for the whole management system. Every other record inherits it.                                                                                            |
| **Abstraction**      | Management system                               | It sits outside the C4 zoom. It does not describe a system at any level; it cites artifacts at every level as evidence.                                                               |
| **Primary Owner**    | ISMS Owner (role)                               | Clause 5.3 assigns ISMS responsibilities to roles. The Architecture Authority owns this guideline, not the records.                                                                   |
| **Target Audience**  | Top Management, ISMS Owner, auditors, assessors | Internal audit (9.2) and management review (9.3) consume the records, and so do external auditors and customers' security assessors who read the public repository.                   |
| **Blast Radius**     | Enterprise assurance (Two-Way)                  | A record can be corrected in the next pull request, but a wrong scope, risk criterion, or SoA entry misstates the organisation's assurance position to every reader until it is.      |
| **Decision Horizon** | Cyclic                                          | Records live as long as the ISMS and are re-evaluated at planned intervals (clauses 6.1.2, 9.2, 9.3), unlike a point-in-time ADR or an ephemeral TDD.                                 |
| **Change Frequency** | Medium                                          | Scheduled reviews every 90 to 365 days (§2.4), plus event-driven changes after an incident, an audit finding, or a significant change.                                                |
| **NFR Focus**        | Security, Reliability, Operational Excellence   | Confidentiality, integrity and availability of information (Security); continuity under A.5.29 and A.5.30 (Reliability); audit, change control and evidence (Operational Excellence). |

---

## 2. Policy Framework

### 2.1 Publication Rules

The architecture repository is public. Four rules apply to every ISMS record without exception:

1. **ISO/IEC text is never reproduced.** ISO/IEC 27001 and ISO/IEC 27002 are copyrighted. A record cites a clause or control by number and title only, for example "6.1.2 Information security risk assessment" or "A.8.32 Change management". It never quotes requirement text, notes, annex guidance, or ISO/IEC 27002 implementation guidance. The organisation's own requirements are written in its own words with MUST and MUST NOT. Because "shall" is the verb of ISO requirement text, the linter rejects it in an ISMS record (`isms_reproduced_requirement_text`); this catches the common case of pasted text, and review catches paraphrase that stays too close to the source.
2. **Roles, never people.** The `owner` field is a role from the schema's role list, and the body names roles only. No record carries a person's name, email address, account handle, or phone number. A team handle (`@org/team`) names a group and is allowed. Who holds a role is recorded outside the public repository. The linter enforces the owner role list and rejects email addresses and personal account handles (`isms_personal_identifier`); names written in prose are caught in review (GDC-002).
3. **No certification claim.** A record says the ISMS is "aligned with ISO/IEC 27001:2022" or "prepared for ISO/IEC 27001:2022 certification". It never says the organisation is certified, accredited, or compliant. Certification is a certification body's statement, not ours; if a certificate is issued, a record links to it as evidence. The linter rejects certification wording (`isms_certification_claim`).
4. **Safe to publish.** Every record is classified `public`. A record describes a risk or a control gap at the level needed to manage it, never how to exploit it. It contains no secret, credential, internal hostname, IP address, or personal data. A weakness that cannot be described safely is entered with its risk identifier and the note "detail held by the ISMS Owner", and the detail is kept outside the repository until the weakness is treated.

### 2.2 The Schema Architecture

In addition to the global structural enforcement defined in **[GDC-001](GDC-001-fitness-functions.md)**, ISMS records are governed by the following domain-specific linter schema:

> [!WARNING]
>
> **DO NOT EDIT THIS TABLE MANUALLY.** This table is automatically generated from the JSON Schema (`schemas/isms.schema.json`). If you need to update a rule, modify the schema file and run: `python 06-fitness-function/generators/generate_rules_doc.py`

<!-- AUTO-GENERATED-SCHEMA:START -->

| Rule Category      | Parameter            | Enforcement / Value                                                                                            |
| :----------------- | :------------------- | :------------------------------------------------------------------------------------------------------------- |
| **Metadata Rules** | Metadata Rules       | <ul><li>doc_meta</li></ul>                                                                                     |
| **Section Rules**  | Required Sections    | <ul><li>Purpose & Scope</li><li>ISO/IEC 27001 Mapping</li><li>Record</li><li>Review & Change Control</li></ul> |
| **Section Rules**  | Recommended Sections | <ul><li>Open Gaps</li><li>References</li></ul>                                                                 |

<!-- AUTO-GENERATED-SCHEMA:END -->

| Linter Component  | File                                          | Enforcement Logic                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :---------------- | :-------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Domain Schema** | `schemas/isms.schema.json`                    | Validates the filename and `id` pattern, the owner role list, the lifecycle statuses, `public` classification, the record kind, and the clause and Annex A control number formats. Requires the four record sections and an edition-specific mapping. The `x-isms-rules` block holds the review cadence per record kind, the control status vocabulary, and the publication patterns the validator reads.                                                                                                                                                                                                                           |
| **Python Engine** | `engine/validators/domains/isms_validator.py` | **Mapping**: at least one clause or control is declared, and each declared number is cited in the mapping section.<br>**Cadence**: `review_cycle_days` does not exceed the record kind's maximum (`isms_review_cadence_violation`).<br>**Single home**: one active record per record kind (`structural_integrity_violation`).<br>**Publication**: certification wording, personal identifiers, and "shall" outside code blocks are rejected.<br>**Control status**: every `Control status` table uses the vocabulary of §2.3.6, links evidence for `implemented`, and justifies `not applicable` (`isms_control_status_violation`). |
| **Graph Auditor** | `engine/auditors/graph_auditor.py`            | **Attachment**: `governed_by` names only a GDC, an EAD, or another ISMS record; a record without `governed_by` is an orphan.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

### 2.3 Semantic Definitions

#### 2.3.1 Naming Conventions

- **Filename**: `^ISMS-\d{3}-[a-z0-9-]+\.md$`, for example `ISMS-NNN-risk-register.md`. The slug repeats the record kind for single-instance kinds.
- **Identifier**: `ISMS-NNN`, allocated in sequence and never reused. The filename starts with the identifier (GDC-001, `compliance_filename_match`).
- **Clause and control numbers** in frontmatter are quoted strings (`"6.1.2"`, `"A.5.9"`). An unquoted `6.2` is read by YAML as a number and fails the schema.

#### 2.3.2 Taxonomy

ISMS records live in the top-level `07-isms/` directory, flat, with no subdirectories. Each record kind other than `other` has exactly one active record. The table below defines what each record holds; a record cites each clause or control with its number and title.

| Record kind (`isms_record`) | What the record holds                                                                                                                                                                                                                 | Usually answers                           | Max review cycle (days) | Approving role |
| :-------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------- | :---------------------- | :------------- |
| `scope-and-context`         | Internal and external issues; interested parties and their requirements; the ISMS boundary, its interfaces and dependencies; anything excluded and why.                                                                               | 4.1, 4.2, 4.3, 4.4                        | 365                     | Top Management |
| `policy-and-roles`          | The information security policy; top management commitment; ISMS roles, their responsibilities and authorities; segregation of duties; the index of topic-specific policies.                                                          | 5.1, 5.2, 5.3, A.5.1, A.5.2, A.5.3, A.5.4 | 365                     | Top Management |
| `risk-methodology`          | Risk acceptance criteria and the criteria for assessing risk; likelihood and impact scales; how risks are identified, analysed and evaluated; treatment options; how repeated assessments stay consistent, valid and comparable.      | 6.1.1, 6.1.2, 6.1.3, 8.2, 8.3             | 365                     | Top Management |
| `risk-register`             | One row per risk: identifier, asset or process, threat and weakness described at a publishable level, risk owner role, likelihood, impact, risk level, evaluation result, and treatment decision with a link to its treatment action. | 6.1.2, 8.2                                | 90                      | ISMS Owner     |
| `risk-treatment-and-soa`    | The risk treatment plan (action, owner role, target date, residual risk, risk owner acceptance) and the SoA: every Annex A control with applicability, justification, control status, and evidence.                                   | 6.1.3, 8.3                                | 90                      | ISMS Owner     |
| `objectives`                | Information security objectives, how each is measured, its target, who monitors it, and the latest result.                                                                                                                            | 6.2, 9.1                                  | 180                     | Top Management |
| `asset-inventory`           | Information and associated assets: repositories, scripts, pipelines, hosts, cloud services, and credential stores (never their secret values), each with an owner role and classification.                                            | A.5.9, A.5.10, A.5.12                     | 90                      | ISMS Owner     |
| `change-management`         | How changes to the ISMS and to information processing facilities are planned, reviewed, approved and recorded, with links to the Git and pull-request workflow that carries them.                                                     | 6.3, A.8.32                               | 365                     | ISMS Owner     |
| `supplier-register`         | Suppliers and cloud services, the information each processes, the security requirements agreed with each, and when each was last reviewed.                                                                                            | A.5.19, A.5.20, A.5.21, A.5.22, A.5.23    | 180                     | ISMS Owner     |
| `incident-management`       | How events are reported and assessed, how incidents are responded to and learned from, how evidence is collected, and where the incident log is kept.                                                                                 | A.5.24 to A.5.28, A.6.8                   | 365                     | ISMS Owner     |
| `continuity`                | Information security during disruption and ICT readiness: recovery objectives, backups, redundancy, and the results of recovery tests.                                                                                                | A.5.29, A.5.30, A.8.13, A.8.14            | 365                     | ISMS Owner     |
| `internal-audit`            | The audit programme (the schedule of audits), each audit's criteria and scope, how auditor independence is kept, and the results and their reporting.                                                                                 | 9.2                                       | 365                     | Top Management |
| `management-review`         | The inputs and outputs of each management review, the decisions taken, and the actions that follow.                                                                                                                                   | 9.3                                       | 365                     | Top Management |
| `nonconformity-log`         | Each nonconformity: what happened, the immediate reaction, the root cause, the corrective action, and the review of its effectiveness.                                                                                                | 10.1, 10.2                                | 90                      | ISMS Owner     |
| `other`                     | A gap document not listed above, for example competence and awareness (7.2, 7.3, A.6.3) or control of documented information (7.5). Several `other` records may exist.                                                                | As declared                               | 365                     | ISMS Owner     |

**Why `07-isms/` and not an existing folder.** The top-level folders of the root repository are separated by abstraction level or cross-cutting concern (GDC-000 §2.3.1), and the linter binds each type to one macro-directory. ISMS records are a concern of their own, so they take the next free top-level number:

- `00-governance/` is rejected: GDC-005 §2.3.2 reserves its root for GDCs, and its reviewers are the Architecture Authority, not the ISMS roles.
- `02-standards/` and `05-decisions/` are rejected: a record kept there would read as a guardrail or a decision, which §1.1 shows it is not, and its ownership would blur with the STD and ADR owners in CODEOWNERS.
- A separate folder gives the ISMS its own CODEOWNERS line, its own review path, and a macro-directory the linter checks (`compliance_macro_directory`).

The folder is flat because the full set is about fifteen records; subfolders would add depth without adding meaning.

#### 2.3.3 Directory Structure

**Centralised Repository (Root Repo)**

```text
scnehaux-architecture/
└── 07-isms/                                  # (ISMS records - flat)
    ├── ISMS-001-scope-and-context.md         # (illustrative numbering)
    ├── ISMS-002-policy-and-roles.md
    ├── ISMS-003-risk-methodology.md
    ├── ISMS-004-risk-register.md
    ├── ISMS-005-risk-treatment-and-soa.md
    └── ISMS-010-asset-inventory.md
```

ISMS records are never authored in project repositories. A project repository holds the evidence an ISMS record links to.

#### 2.3.4 Metadata Schema Properties

```yaml
doc_meta:
  id: ISMS-[Seq] # e.g., ISMS-004
  title: Short Descriptive Title
  owner: ISMS Owner # A role from the schema role list, never a person
  version: Y.Y.Y
  status: draft | proposed | approved | deprecated
  classification: public
  governed_by: [GDC-012] # GDC-012, an EAD, or another ISMS record
  review_cycle_days: 90 # At most the record kind's maximum (§2.3.2)
  created_date: YYYY-MM-DD
  last_reviewed: YYYY-MM-DD
  isms_record: risk-register # Record kind (§2.3.2)
  iso_clauses: ['6.1.2', '8.2'] # ISO/IEC 27001:2022 clause numbers, quoted
  annex_a_controls: [] # ISO/IEC 27001:2022 Annex A control numbers, quoted
```

| Metadata Field      | Type         | Description / Purpose                                                                                                                                                                                                                                                            |
| ------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | String       | `ISMS-NNN`, unique and never reused.                                                                                                                                                                                                                                             |
| `title`             | String       | Descriptive title of the record.                                                                                                                                                                                                                                                 |
| `owner`             | Enum         | One role: `Top Management`, `ISMS Owner`, `Information Security Officer`, `Architecture Authority`, `Enterprise Security Architect`, or `Internal Auditor`. A new role is added to `isms.schema.json` in the same pull request that defines it in the `policy-and-roles` record. |
| `version`           | String       | Semantic Versioning (GDC-000 §2.6).                                                                                                                                                                                                                                              |
| `status`            | Enum         | Document lifecycle state (Allowed Lifecycle Statuses below). It is not a control status (§2.3.6).                                                                                                                                                                                |
| `classification`    | Enum         | Always `public` (§2.1 rule 4).                                                                                                                                                                                                                                                   |
| `governed_by`       | List[String] | **Required**: GDC-012, an EAD (for example EAD-006 or EAD-007), or another ISMS record (§2.5).                                                                                                                                                                                   |
| `review_cycle_days` | Integer      | **Required**: review interval, at most the maximum for the record kind (§2.3.2).                                                                                                                                                                                                 |
| `created_date`      | Date         | Creation date (YYYY-MM-DD).                                                                                                                                                                                                                                                      |
| `last_reviewed`     | Date         | **Required**: date of the last completed review (YYYY-MM-DD).                                                                                                                                                                                                                    |
| `isms_record`       | Enum         | **Required**: the record kind (§2.3.2). It sets the review maximum and the single-home rule.                                                                                                                                                                                     |
| `iso_clauses`       | List[String] | **Required** (may be empty): the ISO/IEC 27001:2022 clauses the record answers, for example `"4.3"` or `"9.2.2"`.                                                                                                                                                                |
| `annex_a_controls`  | List[String] | **Required** (may be empty): the Annex A controls the record answers, `"A.5.1"` to `"A.8.34"`. At least one of `iso_clauses` and `annex_a_controls` is non-empty.                                                                                                                |

##### Allowed Lifecycle Statuses

| Status       | Meaning / Lifecycle Stage                                                                                                               |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `draft`      | Being written. Exempt from full validation for 30 days (GDC-001).                                                                       |
| `proposed`   | Complete and under review; fully validated; carries no authority.                                                                       |
| `approved`   | Approved by the approving role (§2.3.2) through a merged pull request. The current record of the ISMS.                                  |
| `deprecated` | Being retired, for example when its content moves to another record. Exempt from single-home checks; deleted within 180 days (GDC-001). |

##### Allowed Classifications

| Classification | Meaning / Data Sensitivity                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------------------------------- |
| `public`       | The only allowed value. The repository is public, so a record that cannot be public does not belong here (§2.1). |

##### Semantic Versioning Classification

| Version           | Trigger / Change                                                                                               |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| **Major (2.0.0)** | The scope changes, the risk criteria change, or a control moves out of `implemented` or into `not applicable`. |
| **Minor (1.1.0)** | A risk, control, supplier, asset, or evidence link is added, or a control moves towards `implemented`.         |
| **Patch (1.0.1)** | Editorial updates, typo fixes, formatting, and fixing dead links.                                              |

Before the first production deployment, records are edited in place and the version-bump audit is off (GDC-000 §2.6 item 5).

#### 2.3.5 Artifact Section

The linter enforces the presence of these sections. Their semantic purposes are:

| Section Name                | Objective                                                                                    | Requirement                                                                                                                                                 |
| --------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Purpose & Scope**         | What the record covers and which part of the ISMS scope it applies to.                       | Must state the boundary of the record and any exclusion.                                                                                                    |
| **ISO/IEC 27001 Mapping**   | The clauses and Annex A controls the record answers.                                         | Must name the edition `ISO/IEC 27001:2022` and cite every number in `iso_clauses` and `annex_a_controls` with its title. No requirement text (§2.1 rule 1). |
| **Record**                  | The record itself: the policy statements, the method, the register or SoA table, or the log. | Registers and the SoA are Markdown tables. A table that reports control status follows §2.3.6.                                                              |
| **Review & Change Control** | Who reviews the record, how often, and which events trigger an early review.                 | Must name the reviewing role, the cadence, and the event triggers of §2.4.                                                                                  |
| **Open Gaps** _(Optional)_  | What is not yet in place, with the treatment action that closes it.                          | Recommended for every record with a `partial` or `planned` control.                                                                                         |
| **References** _(Optional)_ | Standards and sources cited by number and title, and the repositories that hold evidence.    | Recommended. Each entry carries an identifier (`[R1]`) the text cites, a title, a URL where one exists, and the edition or access date.                     |

#### 2.3.6 Control Status Vocabulary

A control's status is separate from the document's lifecycle status. Any Markdown table with a column headed `Control status` uses exactly these values:

| Control status   | Meaning                               | Rule                                                                                                                                                                             |
| ---------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implemented`    | The control operates as described.    | The `Evidence` cell MUST link evidence in a repository: an `https://` link to a file, commit, pull request, workflow run, or release, or a relative path inside this repository. |
| `partial`        | Part of the control operates.         | The record states what is missing in `Open Gaps` and links the treatment action. Evidence for the operating part is linked where it exists.                                      |
| `planned`        | The control does not operate yet.     | The treatment plan carries an action with an owner role and a target date.                                                                                                       |
| `not applicable` | The control is excluded from the SoA. | The `Justification` cell MUST state why (clause 6.1.3 d). An empty cell, `-`, `n/a`, or `none` is not a justification.                                                           |

A table with a `Control status` column MUST also have an `Evidence` column. Prose such as "see the repository" is not evidence; neither is a link to a wiki page, a chat message, an email, or an `http://` address.

```markdown
| Control                                                    | Control status   | Evidence                                    | Justification                                         |
| :--------------------------------------------------------- | :--------------- | :------------------------------------------ | :---------------------------------------------------- |
| A.5.9 Inventory of information and other associated assets | `implemented`    | [asset list](https://github.com/org/repo/…) | Repositories and scripts are in scope.                |
| A.7.1 Physical security perimeters                         | `not applicable` |                                             | No premises are in scope; processing is cloud-hosted. |
```

### 2.4 Lifecycle & Review Cadence

1. **Scheduled review.** Each record declares `review_cycle_days` no greater than its kind's maximum (§2.3.2). The global review-age rule warns when `last_reviewed` is older than `review_cycle_days`.
2. **Event-driven review.** A record is reviewed before its scheduled date when any of these happen: a significant change to the scope, a system, or a supplier (clauses 6.3 and 8.2); an information security incident; an internal audit finding or nonconformity; a management review decision. The `Review & Change Control` section names the triggers that apply to the record.
3. **What a review is.** A review is a pull request that updates `last_reviewed` and any content that changed. A review that changes nothing still updates `last_reviewed`, so Git history shows the review happened.
4. **Approval.** A record is approved when the approving role (§2.3.2) approves the pull request that sets `approved`. Residual-risk acceptance in the `risk-treatment-and-soa` record is given by each risk owner role named in that record.

### 2.5 Attachment & Evidence

1. **Outside the C4 lineage.** ISMS records do not sit in the EAD → PAD → SAD → TDD hierarchy (GDC-000 §2.4.1). A record attaches through `governed_by` to GDC-012, to an EAD such as EAD-006 (Enterprise Security Architecture) or EAD-007 (Enterprise Governance & Assurance Architecture), or to another ISMS record, normally the `scope-and-context` record. It never attaches to a PAD, SAD, TDD, STD, or ADR, and no architecture artifact attaches to an ISMS record.
2. **Citing architecture.** A record cites an architecture artifact by its ID in prose or by a link. The linter resolves cited IDs, so a renamed or deleted artifact is reported.
3. **Evidence stays where the control operates.** Configuration, workflow runs, tests, and decision records live in their own repositories. An ISMS record links to them and never copies them.

---

## 3. Enforcement Mechanism

In addition to the global rules of GDC-001 (placement in `07-isms/`, filename identity, review age, section length, broken links, inline ID references), ISMS records are checked by the components in §2.2. The domain-specific findings are:

| Error Code                         | Severity  | Fires when                                                                                            |
| :--------------------------------- | :-------- | :---------------------------------------------------------------------------------------------------- |
| `isms_control_status_violation`    | **ERROR** | A control status table breaks §2.3.6.                                                                 |
| `isms_certification_claim`         | **ERROR** | The body claims certification, accreditation, or compliance (§2.1 rule 3).                            |
| `isms_personal_identifier`         | **ERROR** | The body carries an email address or a personal account handle (§2.1 rule 2).                         |
| `isms_reproduced_requirement_text` | **ERROR** | The body uses "shall" outside a code block (§2.1 rule 1).                                             |
| `isms_review_cadence_violation`    | **ERROR** | `review_cycle_days` exceeds the maximum for the record kind (§2.3.2).                                 |
| `structural_integrity_violation`   | CRITICAL  | Two active records share a single-instance record kind, or `governed_by` names a disallowed artifact. |
| `missing_metadata`                 | **ERROR** | A required field is absent or out of its enumeration, or neither clauses nor controls are declared.   |
| `missing_section_keyword`          | **ERROR** | A declared clause or control is not cited in the mapping section, or the mapping omits the edition.   |

The human gate (GDC-002, GDC-003) covers what a pattern cannot: names written in prose, paraphrase that stays too close to the ISO text, risk descriptions that reveal exploit detail, and whether the approving role approved the pull request.

The CODEOWNERS entry for `/07-isms/` is added in the pull request that adds the first ISMS record, because the CODEOWNERS validator rejects a path that does not exist yet. Until then the global fallback rule applies.

---

## 4. Appendix: Architectural Trade-Offs

In accordance with the Quality Rubric (Trade-Offs), the Architecture Authority documents the compromises of this guideline:

1. **A new type and folder vs. reusing STD or ADR**
   - _Why rejected_: Filing the risk register as an STD would give it a guardrail's lifecycle and owners; filing the SoA as ADRs would force a superseding record every time a control's status changes.
   - _The Trade-Off_: We accept one more triad (guideline, schema, validator) and one more top-level folder. In exchange, each ISMS record has one home, its own reviewers, and rules that fit a living record.
2. **Control status in Markdown tables vs. YAML frontmatter**
   - _Why rejected_: Holding the 93-row SoA in frontmatter makes the record hard to read and review, and the frontmatter becomes the document.
   - _The Trade-Off_: The validator parses tables, which ties the rule to a column heading (`Control status`). In exchange, auditors and reviewers read the SoA as an ordinary table.
3. **"Shall" as a proxy for copied ISO text vs. no automated check**
   - _Why rejected_: Leaving the copyright rule to review alone would break GDC-000 §2.7 (the Acid Test).
   - _The Trade-Off_: The proxy rejects every "shall", including the organisation's own wording, and does not catch close paraphrase. Authors write MUST instead, and review covers paraphrase.
4. **An owner role list vs. free text**
   - _Why rejected_: Free text cannot be checked for a person's name.
   - _The Trade-Off_: Adding a role means editing `isms.schema.json`. In exchange, no record can be owned by a named person.
