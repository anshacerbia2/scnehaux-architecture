---
doc_meta:
  id: ISMS-007
  title: Information and Associated Asset Inventory
  owner: ISMS Owner
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-012, ISMS-001]
  review_cycle_days: 90
  created_date: 2026-11-03
  last_reviewed: 2026-11-03
  isms_record: asset-inventory
  iso_clauses: []
  annex_a_controls: ['A.5.9', 'A.5.12', 'A.8.19']
---

# Information and Associated Asset Inventory

## Purpose & Scope

This record lists the information and associated assets inside the scope of [ISMS-001](ISMS-001-scope-and-context.md): repositories, data stores, credential stores, hosts and services, CI pipelines and scripts. Each asset has an owner role and a classification. Each script also has the environments it is allowed to run in. Risk identification in [ISMS-004](ISMS-004-risk-register.md) starts from this list.

The state recorded is the state on 3 November 2026. Only the development environment runs; staging and production are designed, not built. A credential store is listed by where it is and what kind of secret it holds. Its values never appear here. Host addresses, subnets and ports stay on the [development environment page](../deploy/dev/dev-station.md), where they already are, and are not repeated.

Excluded: the account's repositories that are not part of Scnehaux, and the corporate systems ISMS-001 places outside the scope. Five repositories under the same account have no scope decision yet; they are listed in [Scope not decided](#scope-not-decided) and are a gap.

## ISO/IEC 27001 Mapping

Edition: ISO/IEC 27001:2022. This record answers:

| Control | Title                                                | Where in this record                                                                                                                         |
| :------ | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| A.5.9   | Inventory of information and other associated assets | Every table under [Record](#record), each with an owner role                                                                                 |
| A.5.12  | Classification of information                        | The `Classification` column, on the tiers of [STD-GLB-007](../02-standards/_global/STD-GLB-007-data-governance.md#data-classification-tiers) |
| A.8.19  | Installation of software on operational systems      | [Scripts](#scripts): where each script is allowed to run, and whether it changes state                                                       |

No text of the standard is reproduced.

## Record

### How to read this record

- **Owner role:** a role from [ISMS-002 §Roles](ISMS-002-policy-and-roles.md#roles). Where a risk in ISMS-004 covers the asset, the owner is that risk's owner.
- **Classification:** the four tiers of STD-GLB-007: **Tier 1** Restricted (credentials, private keys, session tokens), **Tier 2** Identifiable (data about a person), **Tier 3** Internal, **Tier 4** Public. A store takes the highest tier of anything it holds. On the development environment the people are the team's own development accounts, not customers; the tier is set by the kind of data, so the same store in production keeps its tier.
- **Environments:** `dev server` (the one development server), `laptop` (a developer's laptop), `CI` (a throwaway stack on a GitHub-hosted runner). `staging` and `prod` do not exist; no asset here is allowed in them until a row says so.

### Repositories

All are public on GitHub, under one account. The code and documents in them are Tier 4: anything that cannot be public does not belong in them ([GDC-012 §2.1](../00-governance/GDC-012-isms-guideline.md#21-publication-rules)).

| Repository                                                                         | Holds                                                                                                                       | Classification | Owner role                    |
| :--------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- | :------------- | :---------------------------- |
| [scnehaux-architecture](https://github.com/anshacerbia2/scnehaux-architecture)     | Standards, decisions, designs, ISMS records, the shared CI workflows, the development runbook                               | Tier 4         | Architecture Authority        |
| [identity-kernel](https://github.com/anshacerbia2/identity-kernel)                 | The Keycloak image, the realm, the signing-key tooling, the kernel's development deployment                                 | Tier 4         | Enterprise Security Architect |
| [identity-control](https://github.com/anshacerbia2/identity-control)               | The identity control service and the Control Database schema                                                                | Tier 4         | Enterprise Security Architect |
| [identity-experience](https://github.com/anshacerbia2/identity-experience)         | The identity administration console and its BFF                                                                             | Tier 4         | Enterprise Security Architect |
| [organization-control](https://github.com/anshacerbia2/organization-control)       | The organisation and tenancy service and the Organization Database schema                                                   | Tier 4         | Enterprise Security Architect |
| [organization-experience](https://github.com/anshacerbia2/organization-experience) | The organisation console and its BFF                                                                                        | Tier 4         | Enterprise Security Architect |
| [foundation-platform](https://github.com/anshacerbia2/foundation-platform)         | Shared libraries                                                                                                            | Tier 4         | Architecture Authority        |
| [foundation-reference](https://github.com/anshacerbia2/foundation-reference)       | The reference service built on the shared libraries                                                                         | Tier 4         | Architecture Authority        |
| [ui-platform](https://github.com/anshacerbia2/ui-platform)                         | The UI packages, their release process and release evidence                                                                 | Tier 4         | Architecture Authority        |
| [ui-platform-docs](https://github.com/anshacerbia2/ui-platform-docs)               | The UI platform's documentation site                                                                                        | Tier 4         | Architecture Authority        |
| [scnehaux-design](https://github.com/anshacerbia2/scnehaux-design)                 | The visual design reference ([ADR-UIP-VIS-002](../05-decisions/ui-platform/ADR-UIP-VIS-002-design-reference-repository.md)) | Tier 4         | Architecture Authority        |
| [notification-platform](https://github.com/anshacerbia2/notification-platform)     | Designs only; the platform is not built                                                                                     | Tier 4         | Architecture Authority        |

#### Scope not decided

| Repository                                         | Visibility | Why it is listed                                                    |
| :------------------------------------------------- | :--------- | :------------------------------------------------------------------ |
| scheduling-platform                                | Public     | Named like a Scnehaux platform; not in ISMS-001's scope table       |
| ai-runtime-platform                                | Public     | Named like a Scnehaux platform; not in ISMS-001's scope table       |
| scnx                                               | Public     | Shares the `scnx` prefix of the UI packages; not in the scope table |
| architecture-knowledge, architecture-knowledge-app | Public     | Architecture material; not in the scope table                       |
| scnehaux-iam                                       | Private    | An earlier identity repository; not in the scope table              |

Top Management decides for each one whether it is inside the ISMS scope (T44). Until then none of them is used by a running Scnehaux service.

### Data stores

| Asset                                   | Where                                     | Holds                                                                                             | Classification | Owner role                          | Backup                                  |
| :-------------------------------------- | :---------------------------------------- | :------------------------------------------------------------------------------------------------ | :------------- | :---------------------------------- | :-------------------------------------- |
| Kernel database (Keycloak)              | dev server, identity-kernel stack         | Development accounts, their hashed credentials and second factors, sessions, the realm's settings | Tier 1         | Enterprise Security Architect       | Daily, to a disk in the same host (R4)  |
| Control Database                        | dev server, identity-control stack        | Registrations, Principals, ceremony records, the kernel event record                              | Tier 2         | Enterprise Security Architect       | Daily, to a disk in the same host (R4)  |
| Organization Database                   | dev server, organization-control stack    | Organizations, Tenants, grants, offboardings, the privileged-access record                        | Tier 2         | Enterprise Security Architect       | Daily, to a disk in the same host (R4)  |
| Backups of the three databases          | dev server, the shared backup disk        | Copies of the above, 14 sets each                                                                 | Tier 1         | ISMS Owner                          | None off the host (R4, T11)             |
| Local Control Database                  | laptop                                    | A copy built by `dev-database.ps1` for local work                                                 | Tier 2         | Information Security Officer        | None                                    |
| BFF session stores                      | laptop                                    | Tokens of the sessions signed in through a laptop BFF                                             | Tier 1         | Information Security Officer        | None, by design                         |
| CI logs and artefacts                   | GitHub Actions                            | Build and test logs, scan reports, drill output; kept 90 days                                     | Tier 3         | Information Security Officer        | None (R5)                               |
| UI release evidence                     | ui-platform releases and evidence packets | Attestations, SBOMs, the evidence of each release                                                 | Tier 4         | Architecture Authority              | Held by GitHub                          |
| Source code, documents and ISMS records | the repositories above                    | Everything published in them                                                                      | Tier 4         | As in [Repositories](#repositories) | Git history on GitHub and on each clone |

### Credential stores

Listed by place and kind. No value is ever written here, in any repository, or in a chat.

| Store                                           | Where                           | Kind of secret                                                                                  | Classification | Owner role                    | Risk    |
| :---------------------------------------------- | :------------------------------ | :---------------------------------------------------------------------------------------------- | :------------- | :---------------------------- | :------ |
| identity-kernel `deploy/dev/.env`               | dev server                      | Master realm administrator password, database password, the realm-apply client's identifier     | Tier 1         | Information Security Officer  | R7, R12 |
| identity-kernel client keys                     | dev server                      | Private keys of the kernel's service clients                                                    | Tier 1         | Enterprise Security Architect | R7      |
| Realm signing keystore and its vault file       | dev server                      | The realm's token signing keys                                                                  | Tier 1         | Enterprise Security Architect | R1      |
| identity-control `deploy/dev/.env`              | dev server                      | A copy of the kernel administrator password, database passwords, the operator's sign-in factors | Tier 1         | Information Security Officer  | R7, R11 |
| identity-control keys                           | dev server                      | Private keys of identity-control's clients; the key ring that seals security references         | Tier 1         | Enterprise Security Architect | R7      |
| organization-control `deploy/dev/.env` and keys | dev server                      | Database password; the caller's password and private key                                        | Tier 1         | Information Security Officer  | R7      |
| BFF `.env` and `keys/`                          | each laptop                     | The device's BFF client private key and session secret                                          | Tier 1         | Information Security Officer  | R20     |
| GitHub Actions secret `CHROMATIC_PROJECT_TOKEN` | ui-platform repository settings | The visual-testing service's project token                                                      | Tier 1         | Architecture Authority        | R14     |
| The tunnel owner's GitHub sign-in               | GitHub                          | The account that owns every repository and signs in to the development tunnel                   | Tier 1         | Information Security Officer  | R3, R23 |

### Hosts, networks and services

| Asset                                               | What it does for Scnehaux                                                                            | Run by         | Owner role                    | Risk     |
| :-------------------------------------------------- | :--------------------------------------------------------------------------------------------------- | :------------- | :---------------------------- | :------- |
| Shared development host                             | Runs the three development stacks and holds their backups                                            | A third party  | Top Management                | R10      |
| Microsoft dev tunnel                                | Carries all access to the development server from outside its network                                | Supplier       | Information Security Officer  | R3       |
| Developer laptops                                   | Run the experience BFFs and consoles; hold their keys                                                | Each developer | Information Security Officer  | R20      |
| GitHub (repositories, Actions runners)              | Holds the code and records; runs CI                                                                  | Supplier       | Information Security Officer  | R14, R23 |
| Chromatic                                           | Visual tests of ui-platform's components                                                             | Supplier       | Architecture Authority        | R14      |
| Container registries (quay.io, Docker Hub, Red Hat) | Base images                                                                                          | Suppliers      | Information Security Officer  | R8, R22  |
| Package registries (npm, Go module origins)         | Libraries                                                                                            | Suppliers      | Information Security Officer  | R14      |
| AI assistants                                       | Write code through pull requests; run commands on the development server under the owner's direction | Suppliers      | ISMS Owner                    | R24      |
| AWS                                                 | Designed for production key custody, secrets and Kubernetes; not used today                          | Supplier       | Enterprise Security Architect | R15      |

Each supplier's terms and review belong to the supplier register (T26).

### CI pipelines

Every workflow runs on a GitHub-hosted runner. `deploy-dev` brings a stack up on the runner and runs its proofs and restore drills there; it does not deploy to the development server. A scheduled workflow is marked _(daily)_.

| Repository              | Workflows                                                                                                                | Owner role                   |
| :---------------------- | :----------------------------------------------------------------------------------------------------------------------- | :--------------------------- |
| scnehaux-architecture   | `ci`; `linter` and `deploy-dev-skeleton`, which the other repositories call                                              | Architecture Authority       |
| identity-kernel         | `architecture`, `compat` _(daily)_, `deploy-dev` _(daily)_, `deploy-dev-skeleton`, `image-build`, `image-scan` _(daily)_ | Information Security Officer |
| identity-control        | `architecture`, `ci` _(daily)_, `deploy-dev` _(daily)_, `deploy-dev-skeleton`, `image-scan` _(daily)_                    | Information Security Officer |
| organization-control    | `architecture`, `ci` _(daily)_, `deploy-dev` _(daily)_, `image-scan` _(daily)_                                           | Information Security Officer |
| identity-experience     | `architecture`, `ci`, `deploy-dev-skeleton`, `identity-control-commands` _(daily)_                                       | Information Security Officer |
| organization-experience | `architecture`, `ci`, `deploy-dev-skeleton`, `stack-proof` _(daily)_                                                     | Information Security Officer |
| foundation-platform     | `architecture`, `ci` _(daily)_                                                                                           | Architecture Authority       |
| foundation-reference    | `architecture`, `ci` _(daily)_                                                                                           | Architecture Authority       |
| ui-platform             | `ci` _(daily)_, `chromatic`, `evidence`, `release`                                                                       | Architecture Authority       |
| ui-platform-docs        | `ci`                                                                                                                     | Architecture Authority       |

scnehaux-design and notification-platform have no workflow.

### Scripts

Every script in the in-scope repositories on 3 November 2026, grouped by what it may change. All are public code (Tier 4). Repository abbreviations: IK identity-kernel, IC identity-control, OC organization-control, IX identity-experience, OX organization-experience, UIP ui-platform, UIPD ui-platform-docs, SD scnehaux-design, ARCH this repository. foundation-platform, foundation-reference and notification-platform have no scripts.

| Group                                       | Scripts                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Allowed environments                      | Changes state                                                                    | Owner role                    |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------- | :------------------------------------------------------------------------------- | :---------------------------- |
| S1 Server operation                         | IK `deploy/dev/`: `backup.sh`, `restore.sh`, `create-apply-client.sh`, `new-client-key.sh`, `set-client-key.sh`, `tunnel-admin.sh`. IC `deploy/dev/`: `add-organization-roles.sh`, `backup.sh`, `bootstrap.sh`, `create-kernel-clients.sh`, `create-registration-client.sh`, `create-security-ref-key.sh`, `migrate.sh`, `restore.sh`, `rotate-client-key.sh`. OC `deploy/dev/`: `backup.sh`, `migrate.sh`, `restore.sh`. IX `deploy/dev/create-bff-client.sh`                                                                                                                                                                                          | dev server                                | Yes: databases, clients, keys, the realm                                         | Information Security Officer  |
| S2 Signing keys                             | IK `scripts/`: `signing-key-ceremony.sh`, `signing-key-generate.sh`, `signing-keystore.sh`, `signing-key-rotation.sh`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | dev server; CI                            | Yes: the realm's signing keys                                                    | Enterprise Security Architect |
| S3 Registration and wiring through the APIs | IC `scripts/`: `dev-adopt-bff.ps1`, `dev-adopt-caller.ps1`, `dev-bootstrap.ps1`, `dev-keycloak.ps1`, `dev-database.ps1`. OC `scripts/`: `dev-wire.ps1`, `dev-provisioning.ps1`, `dev-obligation.ps1`, `dev-deprovisioning.ps1`. IX `scripts/`: `dev-register-bff.ps1`, `dev-wire-enrolment.ps1`. OX `scripts/dev-register-bff.ps1`                                                                                                                                                                                                                                                                                                                      | dev server; laptop; CI                    | Yes: registrations, grants, Tenants, local databases                             | Enterprise Security Architect |
| S4 Proofs and restore drills                | IK `scripts/dev-restore-drill.sh`. IC `scripts/`: `dev-back-channel-logout-proof.ps1`, `dev-bff-adoption-proof.ps1`, `dev-enrolment-proof.ps1`, `dev-first-credential-proof.ps1`, `dev-kernel-events-proof.ps1`, `dev-key-rotation-proof.ps1`, `dev-notifications-proof.ps1`, `dev-session-removal-proof.ps1`, `dev-tenant-proof.ps1`, `dev-proof-b.ps1`, `dev-smoke.ps1`, `dev-credential-split.ps1`, `dev-production-switches.ps1`, `dev-restore-drill.sh`, `dev-restore-older-point.ps1`, `dev-restore-read.ps1`, `dev-logout-receiver.py`. OC `scripts/`: `dev-restore-drill.sh`, `dev-restore-read.ps1`, `dev-wiring-proof.ps1`. OX `e2e/seed.ps1` | CI; dev server                            | Test data on the stack they run against; a drill restores into a throwaway stack | Information Security Officer  |
| S5 Helpers loaded by other scripts          | IC `scripts/`: `client-assertion.ps1`, `dev-env.ps1`, `dev-token.ps1`. OC `scripts/dev-reporter.ps1`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Where the calling script may run          | No, on their own                                                                 | Enterprise Security Architect |
| S6 Laptop tools                             | IX and OX `scripts/`: `dev-local.ps1`, `new-client-key.mjs`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | laptop                                    | Local files only: a key pair; local processes                                    | Information Security Officer  |
| S7 Image entrypoint                         | IK `image/start.sh`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Inside the kernel image, wherever it runs | No: refuses to start Keycloak on a bad keystore                                  | Enterprise Security Architect |
| S8 Security checks in CI                    | IK: `.github/scripts/admin-login.py`, `.github/scripts/built-here.sh`, `.github/scripts/pull-policy.py`, `scripts/check-dockerignore.sh`, `scripts/image-build-check.sh`, `scripts/image-build-compare.py`, `scripts/image-scan.sh`, `scripts/image-scan-rules.py`. IC and OC `scripts/`: `atlas-execute-path.sh`, `check-dockerignore.sh`, `image-scan.sh`, `image-scan-rules.py`                                                                                                                                                                                                                                                                      | CI; laptop                                | No                                                                               | Information Security Officer  |
| S9 Contract, build and document checks      | IX `scripts/`: `check-dist.mjs`, `check-identity-control-commands.mjs`, `check-identity-control-openapi.mjs`, `ui-platform.mjs`. OX `scripts/`: `check-api-contract.mjs`, `check-bff-conformance.mjs`, `check-dist.mjs`, `ui-platform.mjs`. UIP: the 51 build, test and evidence scripts under `scripts/` and `packages/*/scripts/` other than S10. UIPD: the 7 scripts under `scripts/`. SD `scripts/`: `render-cards.mjs`, `sync-tokens.mjs`. ARCH: `06-fitness-function/scripts/` (4), `06-fitness-function/generators/` (7), `align_repository_topology_governance.py`, `scratch/fix_links.py`                                                      | CI; laptop                                | Files in the working copy only                                                   | Architecture Authority        |
| S10 Release                                 | UIP `scripts/release.mjs`, `scripts/release-line.mjs`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | CI, in the `release` workflow only        | Yes: publishes a UI release                                                      | Architecture Authority        |

**Rules that follow from this table:**

- A script in S1 to S3 runs only in the environments its row allows. Staging and production are not among them; a script is allowed there only after its row here says so, in a reviewed pull request.
- On the development server, the owner runs every state-changing script; an AI agent runs read-only checks only ([ISMS-004](ISMS-004-risk-register.md) R24).
- A new script, or a script moved to another group, is added here in the same pull request that adds it to its repository, or within the next review if the repository is not this one.

## Review & Change Control

- **Reviewer and approver:** the Information Security Officer reviews; the ISMS Owner approves ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)).
- **Cadence:** every 90 days at most, before the review of the risk register. The next review is due by 1 February 2027.
- **Early review when:** a repository, data store, host, supplier or environment is added or removed; a script is added, removed or changes group; a secret moves to another store; staging or production is built; after an incident, a nonconformity or an audit finding.

## Open Gaps

| Gap                                                                                         | Treatment                         |
| :------------------------------------------------------------------------------------------ | :-------------------------------- |
| Five repositories under the same account have no scope decision                             | T44                               |
| Nothing checks that a new script, workflow or data store reaches this record                | T45                               |
| Data stores and fields do not carry their tier in the designs; documents carry other labels | T34, T18                          |
| The production assets (managed databases, key custody, secret store, ingress) are not built | Added here as each is built (T17) |

## References

- **[R1]** ISO/IEC 27001:2022. Cited by control number and title only.
- **[R2]** [STD-GLB-007 Data Governance](../02-standards/_global/STD-GLB-007-data-governance.md), §Data Classification Tiers.
- **[R3]** [Development environment page](../deploy/dev/dev-station.md) and [runbook](../deploy/dev/README.md).
- **[R4]** The repositories listed, at their `main` branch on 3 November 2026.
