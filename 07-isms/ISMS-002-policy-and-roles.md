---
doc_meta:
  id: ISMS-002
  title: Information Security Policy and Roles
  owner: Top Management
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-012, ISMS-001]
  review_cycle_days: 365
  created_date: 2026-11-01
  last_reviewed: 2026-11-01
  isms_record: policy-and-roles
  iso_clauses: ['5.1', '5.2', '5.3']
  annex_a_controls: ['A.5.1', 'A.5.2', 'A.5.3', 'A.5.4']
---

# Information Security Policy and Roles

## Purpose & Scope

This record is Scnehaux's information security policy. It states what top management commits to, the principles every system and person in scope follows, the roles that carry the ISMS and who may hold them together, and where the detailed rules live. It applies to everything inside the scope of [ISMS-001](ISMS-001-scope-and-context.md).

Roles are named, never people. Who holds each role is recorded outside this public repository, by the ISMS Owner.

## ISO/IEC 27001 Mapping

Edition: ISO/IEC 27001:2022. This record answers:

| Clause or control | Title                                                  | Where in this record                                                     |
| :---------------- | :----------------------------------------------------- | :----------------------------------------------------------------------- |
| 5.1               | Leadership and commitment                              | [Commitment](#commitment)                                                |
| 5.2               | Policy                                                 | [The policy](#the-policy)                                                |
| 5.3               | Organizational roles, responsibilities and authorities | [Roles](#roles)                                                          |
| A.5.1             | Policies for information security                      | [The policy](#the-policy), [Topic-specific rules](#topic-specific-rules) |
| A.5.2             | Information security roles and responsibilities        | [Roles](#roles)                                                          |
| A.5.3             | Segregation of duties                                  | [Segregation of duties](#segregation-of-duties)                          |
| A.5.4             | Management responsibilities                            | [Commitment](#commitment)                                                |

No text of the standard is reproduced.

## Record

### The policy

Scnehaux protects the information it holds for tenants, their people and itself: it keeps that information confidential to those entitled to it, correct, and available when they need it. To do that:

1. **Security is designed in, and written down first.** A new system or change MUST be covered by a standard, decision or design before it is built, or the same change MUST update them ([GDC-000](../00-governance/GDC-000-governance-policy.md)). Security is a required part of each system design.
2. **Access is the least that does the job, for as long as it is needed.** Privileged access is eligible, not standing: it is activated for a reason and approved by another person ([ADR-ORG-002](../05-decisions/organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md)).
3. **No one acts alone on the keys to the platform.** A ceremony that creates or changes trust (the first Principal, a signing key, its rotation) has a second person present, and a third reviews it ([STD-IAM-001 §3.10](../02-standards/identity-access-platform/STD-IAM-001-identity-security.md#310-ceremonies-290)).
4. **Secrets never enter a repository, a ticket or a chat.** Every repository is public. A procedure that handles a secret reads it from a protected file and never prints it.
5. **A procedure step is a script, and CI runs it** ([STD-GLB-009](../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment)). What the server runs is what CI proves.
6. **Known vulnerabilities are fixed on a clock.** Images are scanned daily, and a finding with a fix is fixed within the time CISA's BOD 26-04 table gives, or carries a dated, evidenced exception ([STD-GLB-009 §Container Images](../02-standards/_global/STD-GLB-009-platform-engineering.md#container-images-140)).
7. **What we publish is safe to publish.** Records describe risks at the level needed to manage them, never how to exploit them, and name roles, never people ([GDC-012 §2.1](../00-governance/GDC-012-isms-guideline.md#21-publication-rules)).
8. **We keep evidence and learn from what goes wrong.** Changes go through pull requests; incidents, audit findings and near misses lead to a recorded corrective action.
9. **We meet our legal and contractual obligations** in every jurisdiction where we process personal data, and improve the ISMS continually.

This policy is published in this repository, which every person in scope can read. Each person who holds an ISMS or ceremony role MUST read it before taking the role, and again after each change.

### Commitment

Top Management:

- approves this policy, the scope ([ISMS-001](ISMS-001-scope-and-context.md)) and the risk method ([ISMS-003](ISMS-003-risk-methodology.md)), and accepts residual risk above the acceptance level;
- makes sure the ISMS has the people, time and tools it needs, and records when it does not, as a risk;
- sets the information security objectives and reviews them in the management review;
- makes sure each role below is held, and that no one holds two roles this record keeps apart;
- requires everyone who works on Scnehaux, including contractors and AI assistants acting under direction, to follow this policy and the rules it points to.

### Roles

**ISMS roles**

| Role                          | Responsibilities                                                                                                                                                      | Authority                                                                                                          |
| :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| Top Management                | Commitment above; approves the scope, policy, method and objectives; chairs the management review; accepts residual risk                                              | Final approval of ISMS records it owns ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)) |
| ISMS Owner                    | Runs the ISMS: keeps the records current, the risk register, the treatment plan and the SoA; reports to Top Management; keeps the off-repository list of role holders | Approves operational ISMS records; assigns risk owners                                                             |
| Information Security Officer  | Day-to-day security: vulnerability handling, incident coordination, threat intelligence, security review of changes                                                   | Can stop a release or a change on a security ground                                                                |
| Architecture Authority        | Keeps the architecture and its standards consistent with this policy; ratifies governance changes                                                                     | Approves GDCs, EADs and standards ([GDC-000 §2.12](../00-governance/GDC-000-governance-policy.md))                 |
| Enterprise Security Architect | Security architecture: identity, keys, trust boundaries ([EAD-006](../01-enterprise/EAD-006-enterprise-security-architecture.md))                                     | Approves security designs and decisions                                                                            |
| Internal Auditor              | Plans and carries out internal audits; reports findings                                                                                                               | Access to every record needed for an audit; independent of what is audited                                         |
| Risk owner                    | Owns a risk in the register; approves its treatment and accepts its residual risk within the acceptance level                                                         | Named per risk, by role                                                                                            |

**Operational roles** (already defined by the standards and decisions that use them)

| Role                 | Where defined                                                                                                     | Responsibilities                                                |
| :------------------- | :---------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| Operator             | [STD-IAM-001 §3.10](../02-standards/identity-access-platform/STD-IAM-001-identity-security.md#310-ceremonies-290) | Runs a ceremony or a state-changing procedure                   |
| Witness              | STD-IAM-001 §3.10                                                                                                 | Is present at a ceremony and confirms what was done             |
| Approver             | STD-IAM-001 §3.10; identity-kernel signing-key rotation runbook                                                   | Approves a signing-key stage, activation or retirement          |
| Reviewer             | STD-IAM-001 §3.10                                                                                                 | Reviews a ceremony's record afterwards, and records the outcome |
| Provider             | [ADR-ORG-002](../05-decisions/organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md)           | Operates Scnehaux with eligible, approved authority             |
| Tenant administrator | [ADR-ORG-003](../05-decisions/organization-tenancy-platform/ADR-ORG-003-tenant-administration-grant.md)           | Administers one tenant's people and access                      |

**Who holds the roles today.** One person holds Top Management, ISMS Owner, Information Security Officer, Architecture Authority and Enterprise Security Architect. The witness, approver and reviewer of ceremonies are held by other people. No one holds the Internal Auditor role yet (Open Gaps).

### Segregation of duties

These roles MUST be held by different people for the same act. Where code enforces the rule, the evidence is linked.

| Kept apart                                       | For                                                  | Control status | Evidence                                                                                                                                                                                                                                                                                                                     | Justification                                                                                                                                                                                           |
| :----------------------------------------------- | :--------------------------------------------------- | :------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Operator and witness                             | The bootstrap ceremony and each signing-key ceremony | `partial`      | [signing-key-ceremony.sh refuses a witness equal to the operator](https://github.com/anshacerbia2/identity-kernel/blob/main/scripts/signing-key-ceremony.sh); [bootstrap_ceremony_witness_check](https://github.com/anshacerbia2/identity-control/blob/main/migrations/20261020163355_ceremony_witness_adoption_consent.sql) | The check compares typed names, so it proves two names, not two people (Open Gaps)                                                                                                                      |
| Reviewer and the ceremony's operator and witness | The bootstrap ceremony's review                      | `implemented`  | [bootstrap_ceremony_review_independent compares the reviewer's Principal with the ceremony's](https://github.com/anshacerbia2/identity-control/blob/main/migrations/20261020163355_ceremony_witness_adoption_consent.sql)                                                                                                    | The reviewer signs in, so the check is on authenticated identities                                                                                                                                      |
| Requester and approver of a provider activation  | Eligible provider authority                          | `implemented`  | [ErrSelfApproval in organization-control's activation](https://github.com/anshacerbia2/organization-control/blob/main/internal/authority/activation.go)                                                                                                                                                                      | Self-approval is refused by the service                                                                                                                                                                 |
| Operator and approver                            | Signing-key stage, activation and retirement         | `partial`      | [signing_key_witness_check](https://github.com/anshacerbia2/identity-control/blob/main/migrations/20261025100000_signing_key_registry.sql); [rotation runbook](https://github.com/anshacerbia2/identity-kernel/blob/main/docs/runbooks/signing-key-rotation.md)                                                              | The approver is a typed name, not a sign-in                                                                                                                                                             |
| Author and approver of a change                  | Pull requests                                        | `planned`      |                                                                                                                                                                                                                                                                                                                              | With one maintainer, pull requests need no second approval today ([STD-GLB-009 §Security & Access Governance](../02-standards/_global/STD-GLB-009-platform-engineering.md#security--access-governance)) |
| Auditor and the work audited                     | Internal audits                                      | `planned`      |                                                                                                                                                                                                                                                                                                                              | No Internal Auditor yet                                                                                                                                                                                 |

### Topic-specific rules

The policy's detail lives in these standards and decisions. Each has its own owner, version and review cycle.

| Topic                                                  | Rules                                                                                                                                                                                                            |
| :----------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Identity, authentication, ceremonies                   | [STD-IAM-001](../02-standards/identity-access-platform/STD-IAM-001-identity-security.md), [ADR-IAM-004](../05-decisions/identity-access-platform/ADR-IAM-004-authentication-assurance-and-step-up.md)            |
| Token signing and key custody                          | [ADR-IAM-002](../05-decisions/identity-access-platform/ADR-IAM-002-token-signing.md)                                                                                                                             |
| Privileged and tenant administration                   | [ADR-ORG-002](../05-decisions/organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md), [ADR-ORG-003](../05-decisions/organization-tenancy-platform/ADR-ORG-003-tenant-administration-grant.md) |
| Platform engineering, environments, images, procedures | [STD-GLB-009](../02-standards/_global/STD-GLB-009-platform-engineering.md)                                                                                                                                       |
| Data classification and retention                      | [STD-GLB-007](../02-standards/_global/STD-GLB-007-data-governance.md)                                                                                                                                            |
| Databases, backups and restore evidence                | [STD-GLB-002](../02-standards/_global/STD-GLB-002-database.md)                                                                                                                                                   |
| Logging and monitoring                                 | [STD-GLB-003](../02-standards/_global/STD-GLB-003-observability.md)                                                                                                                                              |
| Frontend security                                      | [STD-GLB-FE-003](../02-standards/_global/STD-GLB-FE-003-security.md)                                                                                                                                             |
| Security architecture                                  | [EAD-006](../01-enterprise/EAD-006-enterprise-security-architecture.md)                                                                                                                                          |

## Review & Change Control

- **Reviewer and approver:** the ISMS Owner reviews; Top Management approves.
- **Cadence:** every 365 days at most.
- **Early review when:** a role holder changes; a second maintainer joins (segregation of pull requests becomes possible); production is built; an incident or audit finding concerns a role or a duty; a topic-specific rule above is replaced.

## Open Gaps

| Gap                                                                                                          | Treatment                                                                                                  |
| :----------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| Witness and approver are typed names, not authenticated identities, so code proves two names, not two people | Decision on whether ceremony roles sign in, before production                                              |
| Pull requests have no second approver                                                                        | Required once a second maintainer exists; until then each merge is a recorded risk                         |
| No Internal Auditor                                                                                          | Appoint someone independent of the work, or commission an external review, before the first internal audit |
| No record that role holders have read this policy                                                            | An acknowledgement entry per role holder, kept with the off-repository list                                |
| Ceremony role holders and the review deadline are still open in STD-IAM-001 §3.10                            | Owner decision                                                                                             |

## References

- **[R1]** ISO/IEC 27001:2022. Cited by clause and control number and title only.
- **[R2]** [GDC-012 ISMS Guideline](../00-governance/GDC-012-isms-guideline.md).
- **[R3]** [ISMS-001 Scope and Context](ISMS-001-scope-and-context.md).
