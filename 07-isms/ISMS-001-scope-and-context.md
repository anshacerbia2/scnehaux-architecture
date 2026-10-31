---
doc_meta:
  id: ISMS-001
  title: ISMS Scope and Context
  owner: ISMS Owner
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-012, EAD-007]
  review_cycle_days: 365
  created_date: 2026-11-01
  last_reviewed: 2026-11-01
  isms_record: scope-and-context
  iso_clauses: ['4.1', '4.2', '4.3', '4.4']
  annex_a_controls: []
---

# ISMS Scope and Context

## Purpose & Scope

This record sets the boundary of the Scnehaux information security management system (ISMS). It states the issues that shape it, the parties who need something from it, what is inside and outside its scope, and the processes that make it up. Every other ISMS record (`07-isms/`) works inside this boundary.

The ISMS is aligned with ISO/IEC 27001:2022. It is not certified, and nothing in this repository claims that it is. An external audit would still need records of the ISMS operating over time: completed risk treatments, internal audits, management reviews and incident records.

The state described here is the state on 1 November 2026. **Production does not exist yet.** The only running environment is one development server and the developers' laptops. Staging and production are designed and not built. Where a control depends on production or on a role that is not yet staffed, the record says so.

## ISO/IEC 27001 Mapping

Edition: ISO/IEC 27001:2022. This record answers:

| Clause | Title                                                               | Where in this record                                          |
| :----- | :------------------------------------------------------------------ | :------------------------------------------------------------ |
| 4.1    | Understanding the organization and its context                      | [Internal and external issues](#internal-and-external-issues) |
| 4.2    | Understanding the needs and expectations of interested parties      | [Interested parties](#interested-parties)                     |
| 4.3    | Determining the scope of the information security management system | [The scope](#the-scope)                                       |
| 4.4    | Information security management system                              | [The ISMS and its processes](#the-isms-and-its-processes)     |

No text of the standard is reproduced. Requirements below are the organisation's own, written with MUST and MUST NOT.

## Record

### Internal and external issues

**Internal issues**

| Issue                                                                                                                                                                                                                                                               | Effect on information security                                                                                                                                                                                 |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scnehaux is a platform built before its first customer: identity and access, organisation and tenancy, and a shared UI platform, with notification and audit platforms designed and not built ([EAD-002](../01-enterprise/EAD-002-enterprise-system-landscape.md)). | Controls are designed into the systems now, but most can only be shown to operate once production exists. The Statement of Applicability (SoA) records this as `partial` or `planned`, never as `implemented`. |
| A very small team. One person holds the top management, ISMS owner and operator roles. The ceremony roles (witness, approver, reviewer) are held by other people.                                                                                                   | Segregation of duties is possible for ceremonies and must be kept. Absence of the one person stalls approvals and recovery (risk R19 in the risk register).                                                    |
| Architecture is governed as code: every decision, standard and design is a reviewed file with a linter ([GDC-000](../00-governance/GDC-000-governance-policy.md)).                                                                                                  | ISMS records use the same discipline ([GDC-012](../00-governance/GDC-012-isms-guideline.md)), so their history and review are in Git.                                                                          |
| AI assistants write code and operate the development server under the owner's direction.                                                                                                                                                                            | Their access is a privileged-access and supplier question, recorded in the policy (ISMS-002) and the supplier register.                                                                                        |

**External issues**

| Issue                                                                                                                              | Effect on information security                                                                                                                                                        |
| :--------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| All repositories are public on GitHub.                                                                                             | Records and code are written to be safe to publish: no secret, no person's name, no exploit detail ([GDC-012 §2.1](../00-governance/GDC-012-isms-guideline.md#21-publication-rules)). |
| The development server is reached through a Microsoft dev tunnel, on a shared host run by others.                                  | Availability and host-level access depend on parties outside the ISMS. They are suppliers, and their risks are in the register.                                                       |
| The platform depends on open-source upstreams (Keycloak, Go and npm modules, container base images) whose advisories arrive daily. | Vulnerability handling is a continuous process, gated in CI ([STD-GLB-009 §Container Images](../02-standards/_global/STD-GLB-009-platform-engineering.md#container-images-140)).      |
| Customers are expected in Australia, Singapore, the United Kingdom, Europe and the United States.                                  | Privacy and records laws of several jurisdictions apply once personal data of real people is processed. The legal register is an open gap.                                            |

### Interested parties

| Interested party                                                  | What they need from Scnehaux's information security                                                                         | How the ISMS addresses it                                                                                                                                                                      |
| :---------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tenants (customer organisations)                                  | Isolation of their data from other tenants; control of who administers them; evidence of how access is granted and removed. | Tenant isolation and administration grants ([ADR-ORG-003](../05-decisions/organization-tenancy-platform/ADR-ORG-003-tenant-administration-grant.md)); SoA controls A.5.15 to A.5.18 and A.8.3. |
| End users (people who sign in)                                    | Accounts that cannot be taken over; to be told when their account security changes; their personal data handled lawfully.   | Authentication assurance ([ADR-IAM-004](../05-decisions/identity-access-platform/ADR-IAM-004-authentication-assurance-and-step-up.md)); notifications are a production gate (risk R6).         |
| Providers (people who operate Scnehaux)                           | Privileged access that is granted for a reason, approved by another person, and reviewed.                                   | Eligible provider authority ([ADR-ORG-002](../05-decisions/organization-tenancy-platform/ADR-ORG-002-eligible-provider-authority.md)).                                                         |
| Ceremony role holders (witness, approver, reviewer)               | A clear role, the record they sign, and the right to refuse.                                                                | Ceremonies ([STD-IAM-001 §3.10](../02-standards/identity-access-platform/STD-IAM-001-identity-security.md#310-ceremonies-290)).                                                                |
| Suppliers (GitHub, Microsoft, AWS, registries, upstream projects) | Use of their service within its terms.                                                                                      | Supplier register (planned).                                                                                                                                                                   |
| Regulators and authorities                                        | Lawful processing and reporting of breaches where required.                                                                 | Legal register and contacts with authorities (open gaps).                                                                                                                                      |
| Auditors (future)                                                 | Records that show the ISMS operating over time.                                                                             | This repository's history and the records in `07-isms/`.                                                                                                                                       |

### The scope

**In scope.** The ISMS covers the information, systems, processes and people that build and operate the Scnehaux platform:

| Area                                      | What it includes                                                           | State on 1 November 2026                                |
| :---------------------------------------- | :------------------------------------------------------------------------- | :------------------------------------------------------ |
| Identity and access platform              | identity-kernel (Keycloak), identity-control, identity-experience          | Running on the development server and laptops           |
| Organisation and tenancy platform         | organization-control, organization-experience                              | Running on the development server and laptops           |
| UI platform                               | ui-platform and its published packages                                     | Built and published                                     |
| Shared foundations                        | foundation-platform, foundation-reference                                  | Built; used as libraries                                |
| Notification platform, audit and evidence | notification-platform and the audit service                                | Designed, not built                                     |
| Architecture and governance               | this repository: standards, decisions, designs, ISMS records               | In use                                                  |
| Environments                              | `dev` (one development server and developer laptops); `staging` and `prod` | `dev` running; `staging` and `prod` designed, not built |
| Delivery                                  | source repositories, CI pipelines, container images, package publishing    | In use                                                  |

**Out of scope.** These are excluded, with the reason:

| Excluded                                                    | Reason                                                                                                                                                                                                                               |
| :---------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The organisation's other business, offices and corporate IT | Scnehaux has no premises or corporate systems of its own in this ISMS. The corporate network and the shared host are interfaces, handled as suppliers.                                                                               |
| Physical security of the hosting sites                      | The development host belongs to a third party, and production is designed for a cloud provider. Physical controls are recorded in the SoA as `not applicable` with this reason, and revisited if Scnehaux operates its own premises. |
| Customers' own systems and identity providers               | Owned by the customer. The interface (federation, APIs) is in scope; their side is not.                                                                                                                                              |

**Interfaces and dependencies.** The scope meets these parties at the points listed. Each is a supplier or an interface, not part of the ISMS:

| Party                                               | What crosses the boundary                                                                                                                                                |
| :-------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub                                              | Source code, CI runs, the release process, the identity that signs in to the dev tunnel                                                                                  |
| Microsoft dev tunnels                               | All access to the development server from outside its network                                                                                                            |
| The operator of the shared development host         | Host operating system, root access, disk, network                                                                                                                        |
| AWS (designed for production)                       | Key management, secrets, Kubernetes ([ADR-IAM-002](../05-decisions/identity-access-platform/ADR-IAM-002-token-signing.md))                                               |
| Container registries (quay.io, Docker Hub, Red Hat) | Base images the platform runs                                                                                                                                            |
| Package registries (npm, Go module origins)         | Libraries the platform is built from                                                                                                                                     |
| Developer laptops                                   | The experience BFFs, each with its own client and key ([STD-GLB-009 rule 15](../02-standards/_global/STD-GLB-009-platform-engineering.md#development-server-deployment)) |
| AI assistants                                       | Code changes through pull requests; commands on the development server under the owner's direction                                                                       |

### The ISMS and its processes

The ISMS is the set of records in `07-isms/` and the processes they describe. It is kept as code: each record is a reviewed file, checked by the linter of [GDC-012](../00-governance/GDC-012-isms-guideline.md), and approved through a pull request by the role [GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy) names.

| Process                                                                                           | Record                  | State                         |
| :------------------------------------------------------------------------------------------------ | :---------------------- | :---------------------------- |
| Scope and context                                                                                 | ISMS-001 (this record)  | Approved                      |
| Policy, roles and responsibilities                                                                | ISMS-002                | Approved                      |
| Risk assessment and treatment method                                                              | ISMS-003                | Approved                      |
| Risk register, treatment plan and SoA                                                             | ISMS-004, ISMS-005      | Approved                      |
| Objectives and measurement                                                                        | `objectives`            | Planned (ISMS-005 T30)        |
| Asset and script inventory, change management, supplier register, incident management, continuity | one record of each kind | Planned (ISMS-005 T25 to T29) |
| Internal audit, management review, nonconformity and corrective action                            | Their own records       | Planned (ISMS-005 T31, T36)   |

The ISMS MUST be improved through the same loop: a risk, an audit finding or an incident leads to a pull request that changes a record and, where needed, a standard, a decision or code in the repository that owns it.

## Review & Change Control

- **Reviewer and approver:** the ISMS Owner reviews; Top Management approves ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)).
- **Cadence:** every 365 days at most.
- **Early review when:** a staging or production environment is built; a new platform enters operation (notification, audit and evidence); the hosting model or a major supplier changes; the first real customer data is processed; an incident, audit finding or management review requires it.

## Open Gaps

| Gap                                                                                      | Treatment                                                                 |
| :--------------------------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| No legal and regulatory register (which privacy and records laws apply, by jurisdiction) | An `other` record for legal requirements; owner decision on jurisdictions |
| No list of authorities to contact                                                        | Part of the incident management record                                    |
| Records of the ISMS operating over time do not exist yet                                 | Built up by operating the ISMS: reviews, drills, audits                   |

## References

- **[R1]** ISO/IEC 27001:2022, _Information security, cybersecurity and privacy protection — Information security management systems — Requirements_. Cited by clause number and title only.
- **[R2]** [GDC-012 ISMS Guideline](../00-governance/GDC-012-isms-guideline.md).
- **[R3]** [EAD-007 Enterprise Governance and Assurance Architecture](../01-enterprise/EAD-007-enterprise-governance-and-assurance-architecture.md).
- **[R4]** [Development server runbook](../deploy/dev/README.md) and [environment page](../deploy/dev/dev-station.md).
