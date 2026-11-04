---
doc_meta:
  id: ADR-PRV-001
  title: Provisioning Reconciles Desired State Read from Organization Control
  adr_type: foundational
  status: proposed
  created: 2026-11-04
  created_date: 2026-11-04
  created_by: Platform Engineering
  governed_by: [PAD-PLT-017]
---

# ADR-PRV-001: Provisioning Reconciles Desired State Read from Organization Control

## 1. Title

The provisioning service reconciles: it reads each outstanding provisioning request from Organization Control, compares it with what it has built, and closes the difference with idempotent steps. An event wakes it up; a periodic resync makes sure nothing is missed.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                            | Approver                         |
| :--------- | :------- | :----------- | :------------------------------------------------------------------- | :------------------------------- |
| 2026-11-04 | proposed | foundational | Architecture, Core Platform, Platform Engineering, Security, Product | Architecture Authority (pending) |

## 3. Context

`SAD-004 §7.5` sends a provisioning request for each Tenant version and accepts a `realized` or `failed` report against the request's correlation identifier. A request with no report after `ORGANIZATION_PROVISIONING_TIMEOUT` (30 minutes) becomes `unresolved`, and nothing resolves it automatically (`TDD-organization-control-003` §Provisioning Correlation). The reporter is a registered workload, not a person's token (`ADR-ORG-001 §5.11`).

No provisioning system exists. On the development server an operator runs `scripts/dev-provisioning.ps1`, which builds nothing and reports `realized` (`STD-GLB-009` rule 13). The owner wants no person to run a script or to report `realized` in normal operation, in production or in development (`PAD-PLT-017 §1`).

Three facts about Organization Control shape how a provisioning service learns what to do:

- **The desired state is a row, not only an event.** Every request, in both directions, is a row of `tenant.provisioning_request` with its `desired_profile`, `state` and `correlation_id`. Intake writes one; a retry after `failed` writes a new one with a new correlation identifier; an offboarding's release writes a deprovisioning one; a resend writes another with the same correlation identifier (`TDD-organization-control-004` §Sending a Failed Deprovisioning Again).
- **Only some of those rows publish an event.** Intake publishes `tenant.lifecycle.requested`, which carries the desired state (`TDD-organization-control-003` §Published Events). Release and resend publish `tenant.offboarding.released`. A retry after `failed` publishes nothing: the three provisioning transitions are silent by design.
- **Neither event can be subscribed to today.** The outbox delivers to a registered consumer only the types in `projection.SubscribableEventTypes`, which holds the Membership, Tenant-authority and provider-grant types and not `tenant.lifecycle.requested` or `tenant.offboarding.*` (`TDD-organization-control-004` §Published Events).

A design that depends only on events would therefore miss retries and depend on a delivery path that does not yet exist for these types. A design that only polls would be correct but slow to start, and the owner's brief asks for event-driven work.

## 4. Decision Drivers

- No person reports an outcome in normal operation.
- A duplicate, late or out-of-order event must never cause a second build or a wrong report.
- A lost event must not leave a Tenant waiting forever.
- A pooled Tenant is realised in seconds, well inside the 30-minute timeout.
- Every step can be retried safely after a crash, because the service will crash mid-step at some point.
- The service, not a person, decides `failed`, with a cause, before Organization Control decides `unresolved`.
- The contract with Organization Control stays compatible: existing routes keep their meaning.

## 5. Decision

### 5.1 The Desired State Is Read, Never Taken from an Event

The service acts only on a provisioning request it has read from Organization Control. Organization Control serves the outstanding requests to the `provisioning` reporter through a new read route (`SAD-004 §7.5`, Phase 1):

```text
GET /v1/provisioning/requests?state=requested|unresolved&operation=provision|deprovision&after=&limit=
```

Each item carries `provisioning_request_id`, `correlation_id`, `tenant_id`, `operation`, `desired_profile`, `state` and `requested_at`. An event is a hint that something may have changed. On any hint the service reads the request it names before acting. A stale or repeated event therefore reads a request that is already closed and does nothing.

This is how a Kubernetes controller works with state held elsewhere: it reads the desired state from the authority, then acts on the external system to bring the current state closer [R1]. It is level-triggered: the service acts on the difference it observes, not on the event it received, so a missed event costs only time [R2].

### 5.2 An Event Wakes It; a Resync Catches What Events Miss

- **Wake-up.** Organization Control publishes a command event, `com.scnehaux.organization.tenant.provisioning.requested`, in the same transaction as each `tenant.provisioning_request` row it writes: intake, retry, release and resend. It carries identifiers only: `tenant_id`, `provisioning_request_id`, `correlation_id` and `operation`. It is delivered by the per-consumer outbox dispatch of `ADR-GLB-018 §5.4` to the service's acceptance endpoint, authenticated with Organization Control's workload token. The service is registered there as a **provisioning target**, a kind distinct from a projection consumer: it subscribes to this one type, holds no projection, takes no snapshot and adds no authority debt.
- **Resync.** Every `PROVISIONING_RESYNC_INTERVAL` (default 60 seconds) the service lists the outstanding requests through §5.1 and treats each as a hint. A request whose event was lost, delayed or never published is picked up within one interval.
- **Its own drift check.** Every `PROVISIONING_DRIFT_INTERVAL` (default 24 hours) the service compares each realised Tenant's resources with the desired profile it built them from, and raises a drift alert. It does not change a realised Tenant without a new request: Organization Control is the only source of a change in desired state.

### 5.3 Each Request Is a Plan of Idempotent Steps

- **One record per request.** The service keeps its own record of each request, keyed by `provisioning_request_id`, with the plan of steps for its profile (`ADR-PRV-003`) and each step's state. A unique key on `provisioning_request_id` makes a second hint for the same request find the existing record.
- **Each step is idempotent.** A step names the resource it creates by a deterministic name derived from `tenant_id`, reads before it writes, and treats "already exists with the desired settings" as done. Retrying a step with the same input yields the same result [R3].
- **One worker per request.** A worker claims a request with a lease in the service's database. A second replica that sees the same request waits for the lease.
- **A report is sent once and repeated safely.** The report to Organization Control carries the request's `correlation_id`. Organization Control answers a repeat as a replay (`TDD-organization-control-003` §API / Interface), so the service resends a report whose answer it did not receive.

### 5.4 Retry, Deadline and Cause

- **Transient errors retry with backoff.** A step that fails with a transient error, such as a timeout, throttling or a `5xx`, retries with exponential backoff and full jitter: base 1 second, cap 60 seconds [R4].
- **A permanent error fails the request at once.** A step that fails with a permanent error, such as an invalid profile, an exceeded quota or a refused permission, stops retrying.
- **The service has its own deadline, ahead of `unresolved`.** For a pooled request it is 10 minutes from `requested_at`, a third of Organization Control's 30-minute timeout. A request still unfinished at its deadline stops retrying.
- **Failing compensates, then reports.** On a permanent error or a passed deadline, the service removes what it created for that request, in reverse order, then reports `POST /v1/provisioning/failed` with a cause from a closed list: `invalid_profile`, `quota_exceeded`, `permission_denied`, `dependency_unavailable`, `deadline_exceeded`, `health_check_failed`, `approval_rejected`, `approval_expired`, `profile_not_supported`. A cause is never free text from a cloud error, which could carry an account identifier.
- **Longer work tells Organization Control when to expect it.** A bridge, silo or regional request waits for approval and builds for longer than 30 minutes. From Phase 2 the service reports progress, `POST /v1/provisioning/progress` with a stage and an `expected_by`, and Organization Control ages the request against `expected_by` instead of the fixed timeout (`SAD-004 §7.5`, Phase 2). Until Phase 2 is built, the service builds pooled requests only and reports any other `failed` with `profile_not_supported` (`ADR-PRV-002 §5.5`).

### 5.5 The Service Resolves `unresolved` with What It Knows

An `unresolved` request is one whose outcome Organization Control does not know. The service does know it: it holds the request's record and can inspect the resources. During resync it reports the outcome of every `unresolved` request it holds a record for. A request it holds no record for was never seen, so it starts work on it, as Organization Control already allows a dispatch against an `unresolved` request (`TDD-organization-control-003` §Resolving an `unresolved` Request).

This keeps `SAD-004 §7.5`'s rule that success is never inferred: the party that built the resources reports what it built, after its health checks (`PAD-PLT-017 §3.4`).

## 6. Consequences

### Positive

- No person reports an outcome in normal operation. An `unresolved` request is resolved by the party that knows the answer.
- Duplicate, late and reordered events are harmless, because they are only hints.
- Retries after `failed`, which publish no Tenant event today, are found by the command event and by resync.
- A crash at any step resumes at that step.

### Negative

- Organization Control gains a read route, a command event type and a new kind of delivery target. These are code changes in organization-control, made in Phase 1.
- A lost event delays a Tenant by up to one resync interval.
- The service holds a record of every request, which must be kept consistent with Organization Control's.

### Operational

- The service's metrics expose requests by state and age, and the age of the last successful resync. The alerts are in `SAD-021 §9.3`.
- Organization Control's existing alerts on stuck and `unresolved` requests stay, and catch a silent service (`TDD-organization-control-003` §Alerts).

## 7. Compliance Impact

### Related Standards and Artifacts

- `PAD-PLT-017` — Tenant Provisioning & Configuration Platform.
- `SAD-021` — Scnehaux Provisioning Control.
- `SAD-004 §7.5` and `ADR-ORG-001 §5.11`, which this decision extends in a compatible way.
- `ADR-GLB-016` and `ADR-GLB-018`, transactional outbox and per-consumer delivery.
- `STD-GLB-006`, which asks for an orchestrator that keeps state and compensates when a step fails.

### Compliance Status

Proposed. Compatible with `SAD-004` as it stands: the report routes and their meaning do not change. The additions are listed in `SAD-004 §7.5`.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Act on the Event Payload Alone

**Benefits:** no read route; the event already carries the profile.

**Rejected because:** a retry after `failed` publishes no event, an event can arrive late or twice, and a payload acted on without a read would rebuild a Tenant whose request is already closed.

### Alternative B — Poll Only

**Benefits:** one mechanism, correct by itself, and no new delivery kind in Organization Control.

**Rejected as the only mechanism because:** a pooled Tenant would wait up to one poll interval for no reason, and the owner's brief asks for event-driven work. It is kept as the resync of §5.2, so correctness never depends on the event.

### Alternative C — Subscribe as an Ordinary Projection Consumer

**Benefits:** reuses registration and delivery as they are.

**Rejected because:** a projection consumer carries a snapshot, a reconciliation interval and authority debt, none of which apply to a command. Adding `tenant.lifecycle.requested` to `SubscribableEventTypes` would also offer it to every projection consumer.

### Alternative D — Organization Control Calls the Service Synchronously

**Benefits:** immediate, with no outbox delivery.

**Rejected because:** the call would sit inside or after the intake transaction. Inside, it blocks intake on the service; after, a crash between them loses the call. The transactional outbox exists to avoid both (`ADR-GLB-016`).

### Alternative E — Treat a Passed Deadline as Retry Forever

**Benefits:** a slow cloud API eventually succeeds.

**Rejected because:** the Tenant would age to `unresolved` in Organization Control with no cause recorded. A deadline with a reported cause tells the operator what happened, and a retry after `failed` is a deliberate act.

## 9. References

### Informative

- **[R1]** Kubernetes, _Controllers_, accessed 2026-11-04. <https://kubernetes.io/docs/concepts/architecture/controller/>. "In Kubernetes, controllers are control loops that watch the state of your cluster, then make or request changes where needed. Each controller tries to move the current cluster state closer to the desired state." Supports §5.1.
- **[R2]** Kubernetes community, _Writing Controllers_, accessed 2026-11-04. <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/controllers.md>. "Level driven, not edge driven. Just like having a shell script that isn't running all the time, your controller may be off for an indeterminate amount of time before running again." Supports acting on observed state, not on events.
- **[R3]** M. Featonby, _Making retries safe with idempotent APIs_, Amazon Builders' Library, 15 January 2021, accessed 2026-11-04. <https://builder.aws.com/content/3Ev0BENTyBr0XxzRk5FDZzgNYos/making-retries-safe-with-idempotent-apis>. "An idempotent operation is one where a request can be retransmitted or retried with no additional side effects, a property that is very beneficial in distributed systems." Supports §5.3.
- **[R4]** M. Brooker, _Timeouts, retries, and backoff with jitter_, Amazon Builders' Library, 5 December 2019, accessed 2026-11-04. <https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter>. "If all the failed calls back off to the same time, they cause contention or overload again when they are retried"; "Jitter adds some amount of randomness to the backoff to spread the retries around in time." Supports §5.4.
