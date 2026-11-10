---
doc_meta:
  id: ADR-PRV-006
  title: Each Platform Provisions Its Own Part of a Tenant; Provisioning Control Coordinates
  adr_type: foundational
  status: accepted
  created: 2026-11-04
  created_date: 2026-11-04
  created_by: Platform Engineering
  governed_by: [PAD-PLT-017]
---

# ADR-PRV-006: Each Platform Provisions Its Own Part of a Tenant; Provisioning Control Coordinates

## 1. Title

Every platform that stores Tenant data provisions, checks, disables and destroys its own part of a Tenant, with its own module, its own cloud roles and its own readiness check. Provisioning Control coordinates them through a registered participant contract, and reports `realized` to Organization Control only when every required participant is ready.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                             | Approver               |
| :--------- | :------- | :----------- | :-------------------------------------------------------------------- | :--------------------- |
| 2026-11-10 | accepted | foundational | Architecture, Core Platform, Platform Engineering, Identity, Security | Architecture Authority |

The owner approved this decision on 10 November 2026, with the cross-platform contract of `ADR-PRV-006` and the answers recorded in `SAD-021 §15`.

## 3. Context

`ADR-PRV-001` and `ADR-PRV-003`, as first written, made Provisioning Control the single builder: it wrote pooled configuration and ran OpenTofu for every dedicated resource. That covers one platform's view of a Tenant. Every platform that stores Tenant data has its own per-Tenant work for bridge, silo and regional Tenants: identity its realm data and, for some customers, federation settings; notification its delivery store; billing, scheduling and later platforms their own schemas or databases and keys.

With one central builder:

- Provisioning Control must know every platform's storage and hold cloud roles over all of it, a blast radius of every Tenant's data on every platform;
- every new platform changes Provisioning Control;
- `realized` can be reported while a platform is not ready for the Tenant.

## 4. Decision Drivers

- `realized` means the Tenant can be used on every platform its profile needs.
- No single workload holds write roles over every platform's data.
- A platform added later needs no change to Provisioning Control's code.
- The approver still sees one plan and one cost for a Tenant (`ADR-PRV-002`).
- A partial outcome never leaves resources nobody tracks.
- Pooled stays seconds long and fully automatic.

## 5. Decision

### 5.1 The Pattern: Coordinated Participants (Option B, with a Shared Runner)

- **Each platform is a participant.** It owns its OpenTofu module for its part, in its own repository; its cloud roles; and its readiness check. It runs its own plan, apply, disable and destroy.
- **Provisioning Control coordinates.** It reads the request from Organization Control (`ADR-PRV-001`), decides which participants the profile needs, sends each its commands in order, collects their reports, assembles one plan for approval, and reports to Organization Control.
- **A shared runner, not shared privilege.** Provisioning Control's repository publishes a versioned participant runner: a Go library and a container image that implement the contract below and run a participant's OpenTofu module. A participant deploys it with its own module and its own credentials. The code is shared; the identity and the roles are not.

### 5.2 Registering a Participant

A participant is a row in Provisioning Control's participant registry, not code. A provider holding `provider:provisioning` registers it, with a reason, and the row records:

| Field            | Meaning                                                                                       |
| :--------------- | :-------------------------------------------------------------------------------------------- |
| `participant_id` | A stable name, such as `identity`, `notification`                                             |
| `principal_id`   | The participant's workload, registered through identity-control with its own key and an owner |
| `endpoint`       | Its acceptance endpoint for commands                                                          |
| `work`           | For each profile and operation, `none` or `required`                                          |
| `rank`           | Order: applied in ascending rank, disabled, cleaned up and destroyed in descending rank       |
| `deadlines`      | Per stage: `plan`, `apply`, `disable`, `destroy`, `cleanup`                                   |

A participant with `none` for a profile receives nothing for it. A Tenant request records the participant rows in force when it was received, so a later registration does not change a Tenant already in progress.

### 5.3 Commands and Reports

- **Commands** go from Provisioning Control's outbox to the participant's endpoint, authenticated with Provisioning Control's workload token: `plan`, `apply` (with the participant's own approved plan hash), `cleanup`, `disable`, `destroy`, and `check` (drift). Each carries `tenant_id`, `provisioning_request_id`, `participation_id`, the profile and region. As in `ADR-PRV-001 §5.1`, a command is a hint: the participant reads its participation from Provisioning Control before acting, and acts idempotently.
- **Reports** go from the participant to `POST /v1/participations/{participation_id}/report`, authenticated as the participant's workload and admitted only for its own participations: `planned` (plan hash, summary, monthly cost estimate), `ready`, `cleaned`, `disabled`, `destroyed`, or `failed` with a cause from the closed list of `ADR-PRV-001 §5.4`. A repeat is answered as a replay.
- **Readiness.** `ready` means the participant's own checks for the profile passed, as `PAD-PLT-017 §3.4` defines them for that participant.

### 5.4 Outcomes Across Participants

- **All ready.** Provisioning Control runs its own checks, then reports `realized`.
- **One fails, others succeed.** A participant retries transient errors itself within its deadline. Once it reports `failed`, Provisioning Control cleans up every participant that did work for the request, in descending rank, waits for each `cleaned`, then reports `failed` to Organization Control with the cause `participant_failed` and the participant's identifier in the detail. It does not hold partial resources waiting for a person, because they cost money and nobody owns the decision. A new attempt is a retry in Organization Control.
- **One is silent past its deadline.** Its participation becomes `unresolved` in Provisioning Control, and the others are not cleaned up yet, because the silent one may still finish. Provisioning Control reports progress to Organization Control (`ADR-PRV-001 §5.4`) and alerts. If it is still silent at the end of its last deadline, Provisioning Control cleans up the others, reports `failed` with the cause `participant_unresolved`, and keeps a cleanup obligation open for the silent participant, resent until it reports `cleaned`. Success is never inferred from silence.
- **Pooled before Phase 2.** Organization Control's progress report does not exist yet, so a pooled request with a silent participant is failed at the pooled deadline of 10 minutes. No participant has pooled work in Phase 1 (§5.6), so this does not arise there.

### 5.5 Deprovisioning Across Participants

The contract runs in reverse, in descending rank, with the stages of `ADR-PRV-005`:

- **Disable.** Every participant with work for the profile disables its part and reports `disabled`. Provisioning Control reports the deprovisioning `realized` to Organization Control only when all have, so the Tenant is not retired while any platform still serves it.
- **Destroy.** At the end of the 30-day window, unless held, every participant destroys its part, including its own key for the Tenant, and reports `destroyed` with its destruction record (`ADR-PRV-005 §5.5`). Provisioning Control records the Tenant destroyed only when every participant has. Retirement in Organization Control does not wait for this: the Tenant can no longer be reached once every participant has disabled its part. A destruction overdue by 3 days is a security incident, not only an alert.

### 5.6 Pooled

A pooled Tenant needs no participant work from most platforms: their pooled data lives in shared stores under Row-Level Security, keyed by `tenant_id`, created on first use. The only pooled work is Provisioning Control's own configuration record and quota limits. Phase 1 registers no participant with pooled work, so the pooled path stays seconds long and fully automatic. A platform that later needs pooled work (for example identity federation set up at onboarding) registers it, with a deadline under the pooled deadline.

### 5.7 Privilege

- Each participant's cloud roles belong to its platform: plan, apply and destroy roles as `ADR-PRV-004 §5.2` defines them, limited to resources tagged with its own `participant_id`.
- Provisioning Control holds no cloud role that writes another platform's data. It holds roles only for its own configuration store.
- Each participant keeps its own key per Tenant for dedicated profiles, so destroying a Tenant on one platform does not need a role on another (`ADR-PRV-005`).

### 5.8 Identity Is a Participant for Regional Tenants, Through a Regional Deployment

The owner decided the direction on 10 November 2026. A `regional` Tenant's identity data stays in its region:

- **One identity deployment per region**, shared by every Tenant in that region. It is not a Realm per Tenant: `ADR-ORG-001 §5.5` still holds, and the regional deployment serves its Tenants inside its own realms the same way the main deployment does.
- **Identity is a participant for `regional`**, with no work for `pooled`, `bridge` or `silo`. Its part for a regional Tenant is to place the Tenant's identity data in the regional deployment and to report it ready.
- **The design is a separate ADR**, written when the first regional customer is known: how a regional deployment is created, how Principals and tokens work across regions, and how the regional deployment is registered as a participant.
- **Until that ADR is accepted, `regional` is refused**, even after Phase 2 is complete (`ADR-PRV-002 §5.6`).

### 5.9 Every Platform Declares Its Part

Every SAD of a system that stores Tenant data states its participation: the profiles and operations it has work for, its readiness check, and its rank; or "no per-Tenant work", with the reason. A chartered SAD states it when it leaves `chartered`.

## 6. Consequences

### Positive

- `realized` means ready everywhere the profile needs.
- A stolen credential reaches one platform's resources, not all.
- A new platform is a registry row and its own deployment.
- Each platform knows its own storage and owns its readiness check.

### Negative

- Every participating platform deploys the runner, holds its own roles and passes its own tests.
- More messages and more states to trace across services.
- A silent participant can hold a dedicated Tenant until its last deadline.

### Operational

- The panel shows each participant's state per Tenant (`SAD-021 §5.5`).
- Alerts on a participant past its deadline and on an open cleanup obligation.

## 7. Compliance Impact

### Related Standards and Artifacts

- `ADR-PRV-001` to `ADR-PRV-005`, amended to match.
- `STD-GLB-006` — orchestration: a coordinator keeps state and compensates.
- `ADR-GLB-009` — repository boundaries follow ownership: each platform's module stays in its repository.

### Compliance Status

Accepted.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — One Central Builder

**Benefits:** one place runs everything; one set of modules; simplest to start.

**Rejected because:** it holds write roles over every platform's data, changes with every new platform, and can report `realized` without asking the platform that must serve the Tenant.

### Alternative B1 — Pure Choreography, No Coordinator

**Benefits:** each platform reacts to Tenant events and reports to Organization Control directly.

**Rejected because:** Organization Control would have to count readiness across platforms and assemble one plan for approval, work outside its boundary (`PAD-PLT-002 §1.2`); and cleanup after a partial failure would have no owner.

### Alternative B2 — Central Runner, One Role per Platform

**Benefits:** platforms own modules, but only Provisioning Control runs OpenTofu.

**Rejected because:** the one workload that can assume every platform's role is the central builder's blast radius again, behind one more step.
