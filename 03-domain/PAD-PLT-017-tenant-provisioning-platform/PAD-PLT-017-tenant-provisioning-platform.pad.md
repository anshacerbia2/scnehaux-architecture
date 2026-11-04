---
doc_meta:
  id: PAD-PLT-017
  title: Tenant Provisioning & Configuration Platform
  owner: Platform Engineering
  version: 1.1.0
  status: approved
  classification: public
  governed_by:
    - GDC-008
  realizes_capability:
    - EAD-002
    - EAD-005
    - EAD-006
  review_cycle_days: 180
  created_date: 2026-11-04
  last_reviewed: 2026-11-04
  fulfilled_by:
    - SAD-021
---

# Tenant Provisioning & Configuration Platform

## 1. Purpose & Scope

The **Tenant Provisioning & Configuration Platform** turns a Tenant's desired state, decided by the Organization & Tenancy Platform, into realised infrastructure and configuration, and reports the outcome back. It is the capability `PAD-PLT-002 §2.2` names "Tenant Provisioning & Configuration" and keeps outside the Organization boundary.

Its promise is that **no person builds a Tenant or reports a Tenant built in normal operation**, in production or in development. One automated path serves every isolation profile; only the work done differs by profile.

**Approval driver (`GDC-008 §2.3.6`): mandatory dependency.** `PAD-PLT-002` is approved, and its Tenant cannot become `active` until a provisioning system reports it realised (`SAD-004 §5.1`). Without this capability, that report is made by a person on the development server (`STD-GLB-009` rule 13) and by nobody in production.

### 1.1 Capability

The platform owns:

- coordination of every platform that stores Tenant data, each a registered participant that provisions its own part (`ADR-PRV-006`);
- the plan of work for each isolation profile, and its execution;
- health checks that decide when a Tenant is realised;
- approval of dedicated resources before they are created;
- per-Tenant encryption keys for dedicated profiles, and their destruction;
- Tenant configuration records and quota limits;
- deprovisioning: disabling, the recoverable window and destruction;
- drift detection between what was built and what exists;
- the provisioning exceptions panel for failed, stuck and waiting requests.

### 1.2 Out of Scope

The platform does not own:

- Tenant identity, lifecycle, isolation-profile choice or residency choice (Organization & Tenancy, `PAD-PLT-002`);
- Tenant activation, suspension, offboarding obligations, legal hold or retirement (Organization & Tenancy);
- Principal, workload identity or authentication (Identity & Access, `PAD-PLT-001`);
- Product data, its export, retention or deletion inside shared stores (each Product domain, through offboarding obligations);
- Subscription, Entitlement, plan, price or contract (Subscription & Entitlement);
- the shared platform's own infrastructure: clusters, shared databases, networks (Platform Engineering's estate, declared under `STD-GLB-009`);
- Product feature flags and Product configuration values;

## 2. Enterprise Traceability

### 2.1 Realizes

- **EAD-005:** control-plane and application-plane separation, governed tenant-deployment profiles, and environment and configuration provisioning as a platform product (§5.15).
- **EAD-002:** the provisioning system in the enterprise system landscape, correlated with but separate from Tenancy.
- **EAD-006:** tenant-isolation defence in depth for dedicated profiles, least-privilege workload identity.

### 2.2 Relationships

It depends on:

- **Organization & Tenancy (`PAD-PLT-002`)** for desired Tenant state, the provisioning request and its correlation identifier, provider grants for `provider:provisioning`, and the legal-hold flag.
- **Identity & Access (`PAD-PLT-001`)** for the workload identity it reports with, and for the people who approve and act in the panel.
- **Every platform that stores Tenant data**, as a participant that provisions, checks, disables and destroys its own part (`ADR-PRV-006`). shared databases, key service and secret store it builds within.
- **Audit & Evidence (`PAD-PLT-007`)** for evidence retention, when built.

### 2.3 Consumed By

- `PAD-PLT-002 §2.2`, which sends desired Tenant lifecycle and profile here and receives realised state.
- `SAD-004 §7.5`, which defines the request and report contract.
- Product domains and runtime systems that read Tenant configuration and the location of a dedicated Tenant's resources.

## 3. Domain & Context Model

### 3.1 Bounded Context

| Bounded Context        | Owns                                                                                            | Does Not Own                                     |
| :--------------------- | :---------------------------------------------------------------------------------------------- | :----------------------------------------------- |
| Request Reconciliation | the service's record of each request, its plan, steps, leases and outcome                       | the request itself, which is Organization's      |
| Participation          | the participant registry, each participation's state, commands and reports, cleanup obligations | a participant's own resources, module and roles  |
| Profile Execution      | the work per profile and its health checks                                                      | the choice of profile                            |
| Approval               | plans awaiting approval, decisions, reasons, contract references                                | provider grants, which are Organization's        |
| Tenant Configuration   | configuration records and quota limits per Tenant                                               | Product configuration values                     |
| Tenant Keys            | per-Tenant keys for dedicated profiles, their state and scheduled deletion                      | the key service itself                           |
| Deprovisioning         | disabling, the recoverable window, holds and destruction                                        | release and retirement, which are Organization's |
| Drift                  | comparison of built resources with the plan they came from                                      | the shared platform's own drift                  |

### 3.2 Ubiquitous Language

| Term                 | Meaning                                                                                                                                 |
| :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| Provisioning request | One row of Organization Control's `tenant.provisioning_request`: a Tenant, a desired profile, an operation and a correlation identifier |
| Operation            | `provision` or `deprovision`                                                                                                            |
| Participant          | A platform that stores Tenant data and does its own part of provisioning, registered with the work each profile needs from it           |
| Isolation profile    | `pooled`, `bridge`, `silo` or `regional` (§3.4)                                                                                         |
| Plan                 | The list of steps, and for dedicated profiles the saved infrastructure plan, the service will run for a request                         |
| Realised             | Every step done and every health check of the profile passed (§3.4)                                                                     |
| Cause                | One of a closed list of reasons a request failed, reported with `failed`                                                                |
| Approval             | A recorded decision by a second person, bound to one plan by its hash                                                                   |
| Recoverable window   | The 30 days after release during which a deprovisioned Tenant's resources can still be recovered                                        |
| Hold                 | A recorded stop on destruction, by a provider or by a legal hold                                                                        |
| Drift                | A difference between a realised Tenant's resources and the plan they were built from                                                    |

### 3.3 Domain Invariants

1. The platform acts only on a request it has read from Organization Control; an event is a hint, never the desired state.
2. Every step is idempotent and resumable.
3. A Tenant is reported realised only after every health check of its profile passes. Success is never inferred.
4. No dedicated resource is created without an approval bound to its plan.
5. The approver is not the person who requested the Tenant.
6. A failure is reported with a cause from a closed list, never with a raw cloud error.
7. A held or legally held Tenant is never destroyed.
8. No person reports `realized` in normal operation. The only manual report is the emergency break-glass of `SAD-021 §5.5`, under an emergency grant.
9. The platform holds no person's token and Organization Control holds none of its cloud credentials.
10. Records of requests, approvals and destruction outlive the Tenant by 7 years.

### 3.4 Isolation Profiles and What Realised Means

These definitions follow the industry's silo, pool and bridge models [R1]. `regional` is a silo placed in a named region. The work and the checks below are done by each participant for its own part; pooled needs no participant work in Phase 1 (`ADR-PRV-006 §5.6`).

| Profile    | Work                                                                                     | Realised when every check passes                                                                                                                                                                  | Approval |
| :--------- | :--------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- |
| `pooled`   | Configuration record and quota limits in shared infrastructure. Seconds. No new resource | The record reads back with the request's version; quotas read back as desired; the Tenant's configuration is served to readers                                                                    | No       |
| `bridge`   | A schema or database for the Tenant in a shared cluster, with its own database role      | The schema exists at the Product's migration version; the Tenant's role connects and can read its own schema; the role cannot read another Tenant's schema; the configuration record points to it | Yes      |
| `silo`     | A dedicated database instance encrypted with a per-Tenant key, and routing to it         | The instance is available; its encryption key is the Tenant's key; the route resolves to it; the migration version is current; backups are on; another Tenant's route does not resolve to it      | Yes      |
| `regional` | As silo, in the region the Tenant's residency names                                      | As silo, and every resource for the Tenant, including backups and replicas, is in that region                                                                                                     | Yes      |

## 4. Integration Contracts

### 4.1 Integration Provided

- reports of `realized`, `failed` (with cause) and, from Phase 2, progress, to Organization Control;
- Tenant configuration records and quota limits, read by Product and runtime systems;
- the location of a dedicated Tenant's resources, read by the runtime that routes to them;
- the provisioning panel's operations: retry, fail with a cause, clean up a failed build, approve or reject a plan, hold destruction;
- provisioning security and audit events.

### 4.2 Integration Consumed

- the outstanding provisioning requests and the command event from Organization Control;
- provider grants for `provider:provisioning`, projected from Organization Control;
- the offboarding's legal-hold flag;
- workload identity from Identity & Access;
- the shared platform's key service, secret store, databases and clusters.

### 4.3 Contract Principles

- Organization Control is the only source of desired state. The platform never changes a Tenant's profile on its own.
- Every report carries the request's correlation identifier and is safe to repeat.
- The platform tells Organization Control when to expect a long request, so a slow build is not mistaken for a lost one.
- A change to the request or report contract is made in `SAD-004` and `ADR-ORG-001 §5.11` first, and kept compatible or migrated.

## 5. Trust & Data Boundaries

### 5.1 Trust Boundary

The platform establishes boundaries between:

- the authority that decides a Tenant's desired state and the system that builds it;
- planning, which cannot change anything, and applying, which can;
- one Tenant's dedicated resources and another's;
- the platform's ability to create and delete resources and its inability to read Tenant data;
- a person's approval and the machine's execution.

### 5.2 Identity Access

- The platform is one registered workload toward Organization Control (`ADR-ORG-001 §5.11`, `ADR-PRV-004`).
- People act in the panel through a provider grant for `provider:provisioning`, eligible and activated, as `ADR-ORG-002` defines.
- Toward the cloud it uses short-lived roles split by task, under a permission boundary (`ADR-PRV-004 §5.2`).

### 5.3 Data Classification

Tiers are those of `STD-GLB-007`.

| Data                                   | Examples                                                | Tier                 |
| :------------------------------------- | :------------------------------------------------------ | :------------------- |
| Request records and plans              | Tenant identifier, profile, region, steps, plan summary | Tier 3 Internal      |
| Approvals and audit                    | approver `principal_id`, reason, contract reference     | Tier 2 Identifiable  |
| Resource locations and key identifiers | database endpoint, key identifier                       | Tier 3 Internal      |
| Credentials                            | the workload's private key, database role passwords     | Tier 1 Restricted    |
| Tenant data                            | inside the databases it builds                          | Not held; never read |

## 6. Capability NFR

### 6.1 Service Levels

- **Pooled:** realised and reported within 60 seconds of the request at the 95th percentile, and within 10 minutes at most, after which the request fails with a cause.
- **Dedicated:** planned within 15 minutes of the request; applied and reported within 60 minutes of approval.
- **No outcome lost:** every request reaches `realized` or `failed` without a person reporting it, unless a person deliberately fails it.
- No external SLA is declared until production evidence exists.

### 6.2 RTO and RPO

- RTO for the service: 1 hour. While it is down, no Tenant is built; active Tenants are unaffected.
- RPO for its records: the same as Organization Control's, 1 minute, because an approval or a destruction record must not be lost.
- After a restore to an older point, the service rereads outstanding requests and rechecks every request it holds against the resources that exist before acting.

### 6.3 Scalability

- Requests are processed in parallel, one worker per request, with a bound on concurrent applies per account and region.
- One Tenant's failure or slow build never blocks another's.

### 6.4 Compliance and Residency

- A regional Tenant's resources, backups and replicas stay in its region; the health check proves it.
- Destruction of silo and regional data uses key deletion (`ADR-PRV-005`).

### 6.5 Audit

Every request, step, report, approval, hold and destruction records the actor (workload or person), the Tenant, the request and correlation identifiers, the reason where a person acted, and the result. Records are kept 7 years.

## 7. Ownership & Governance

### 7.1 Team Ownership

**Platform Engineering** is the accountable owner. It owns the service, its modules, its cloud roles and the provisioning panel's back end.

### 7.2 Realizing Systems

- **SAD-021 — Scnehaux Provisioning Control**

### 7.3 Governance Rules

1. No other system creates or deletes a Tenant's dedicated resources.
2. Organization Control never holds a cloud credential that can.
3. A new isolation profile, or a change to what realised means, changes this PAD first.
4. A module change that affects existing Tenants is applied Tenant by Tenant through approved plans.
5. Decisions: `ADR-PRV-001` to `ADR-PRV-005`.

## 8. Assumptions & Constraints

- Production runs on the adopted cloud and Kubernetes; the development server runs Docker Compose (`STD-GLB-009`).
- Before Phase 2 is complete, no non-pooled Tenant is created.
- Product domains settle their data obligations before release, through Organization Control.

## 9. References

- **[R1]** AWS, _Silo, Pool, and Bridge Models_, AWS Well-Architected SaaS Lens, accessed 2026-11-04. <https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/silo-pool-and-bridge-models.html>. "The silo model refers to an architecture where tenants are provided dedicated resources"; "the pool model of SaaS refers to a scenario where tenants share resources"; "many systems have a mixed mode where some of the system is implemented in a silo model and some is in a pooled model."
