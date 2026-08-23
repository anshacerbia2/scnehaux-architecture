#!/usr/bin/env python3
"""
Apply Notification + Scheduling runtime-contract hardening to scnehaux-architecture.

Run from the repository root:
    python apply_notification_scheduling_hardening.py

The script is intentionally fail-closed:
- every replacement must match the expected current main-branch text
- already-applied replacements are skipped
- unexpected drift aborts instead of guessing
"""

from pathlib import Path
import sys

ROOT = Path.cwd()

def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f"Missing file: {path}")

    text = p.read_text(encoding="utf-8")

    if new in text and old not in text:
        print(f"SKIP already applied: {path}")
        return

    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"Refusing to edit {path}: expected old text exactly once, found {count}\n"
            f"OLD:\n{old}"
        )

    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"UPDATED: {path}")

def apply_all() -> None:
    # ------------------------------------------------------------------
    # PAD-PLT-005 Notification
    # ------------------------------------------------------------------
    f = "03-domain/PAD-PLT-005-notification-platform/PAD-PLT-005-notification-platform.pad.md"

    replace_once(f, "  version: 2.1.0", "  version: 2.2.0")
    replace_once(f, "  last_reviewed: 2026-08-22", "  last_reviewed: 2026-08-24")
    replace_once(
        f,
        "The Enterprise Notification Platform provides shared communication-delivery capability for Scnehaux Products and Platforms. It accepts an authorized communication intent, freezes the minimum delivery snapshot required for correctness, resolves a governed template/channel variant, routes through an authorized sender/channel profile, executes provider delivery asynchronously, applies communication retry policy, and tracks normalized delivery outcomes.",
        "The Enterprise Notification Platform provides shared communication-delivery capability for Scnehaux Products and Platforms. It accepts an authorized communication intent, freezes the minimum communication-semantic snapshot required for correctness, resolves a governed template/channel variant, routes through an authorized sender/channel profile, executes provider delivery asynchronously, applies communication retry policy, and tracks normalized delivery outcomes.",
    )
    replace_once(
        f,
        "- **Scheduling Platform:** provides generic durable future wake-up when a Notification is already frozen and only delivery time remains",
        "- **Scheduling Platform:** provides generic durable future wake-up when a Notification is already accepted/frozen and only delivery time remains; cross-platform registration uses an idempotent Schedule command and recoverable binding rather than a correctness-critical distributed transaction",
    )
    replace_once(
        f,
        "| Scheduled Notification | Frozen Notification awaiting a durable future wake-up from Scheduling |",
        "| Scheduled Notification | Accepted Notification whose communication semantics are frozen and which awaits a durable future wake-up from Scheduling |\n"
        "| Scheduling Binding | Recoverable association between one Notification scheduling intent and the Scheduler Schedule identity created idempotently for it |",
    )
    replace_once(
        f,
        "- Generic future scheduling is delegated to the Scheduling Platform\n"
        "- Pure scheduled communication SHOULD use a frozen Notification registered with Scheduling when recipient/content/version semantics must be preserved from creation time\n"
        "- A Product MAY schedule a bounded Deferred Notification Command directly to Notification when no Notification must exist before due time and Scheduler does not become a communication-data store",
        "- Generic future scheduling is delegated to the Scheduling Platform\n"
        "- Pure scheduled communication SHOULD use a frozen Notification registered with Scheduling when recipient/content/version semantics must be preserved from creation time\n"
        "- Frozen Notification preserves communication meaning at acceptance time, including recipient snapshot, immutable template/content version and data, selected channel, logical sender identity where required, immutable attachment/version references, and business correlation needed for the accepted communication\n"
        "- Provider route, current provider credential/secret version, provider endpoint, failover route, rate-limit state, and comparable operational delivery machinery SHOULD be resolved at delivery time from the current valid Notification-owned configuration unless an explicit governed contract requires a pinned configuration version\n"
        "- Frozen Notification registration SHALL NOT depend on an atomic cross-service transaction between Notification and Scheduling; Notification SHALL durably record its local scheduling intent, register the Schedule with a stable idempotency identity, persist/recover the returned binding, and reconcile missing or ambiguous bindings\n"
        "- Notification cancellation is authoritative for whether a not-yet-started Notification Delivery may proceed; cancellation of the corresponding Scheduler Schedule is asynchronous cleanup/optimization and a late or already-dispatched Scheduling Occurrence SHALL NOT resurrect a terminally cancelled Notification\n"
        "- A Product MAY schedule a bounded Deferred Notification Command directly to Notification when no Notification must exist before due time and Scheduler does not become a communication-data store",
    )
    replace_once(
        f,
        "- Frozen scheduled-notification registration",
        "- Frozen scheduled-notification registration with idempotent/reconcilable Scheduling binding",
    )
    replace_once(
        f,
        "- Scheduling Platform for durable future wake-up of frozen Notifications",
        "- Scheduling Platform for durable future wake-up of frozen Notifications using stable idempotent registration and reconciliation semantics",
    )
    replace_once(
        f,
        "SMTP host/port/TLS mode, sender identity, provider selection, messaging-provider endpoint metadata, and comparable delivery configuration remain Notification-owned because they directly control Notification behavior. Passwords, OAuth refresh tokens, private keys, and API secrets remain Trust-owned.",
        "SMTP host/port/TLS mode, sender identity, provider selection, messaging-provider endpoint metadata, and comparable delivery configuration remain Notification-owned because they directly control Notification behavior. Passwords, OAuth refresh tokens, private keys, and API secrets remain Trust-owned. For a Frozen Notification, communication semantics are immutable while operational provider realization is late-bound by default unless an explicit version-pinning contract says otherwise.",
    )
    replace_once(
        f,
        "- scheduled-notification binding to a Scheduling identifier",
        "- scheduled-notification registration intent, reconciliation metadata, and binding to a Scheduling identifier",
    )
    replace_once(
        f,
        "- Target RPO: **<= 15 minutes**\n"
        "- accepted Notifications are delayed rather than silently lost during platform/provider outage",
        "- Target RPO: **<= 15 minutes**\n"
        "- accepted Notifications are delayed rather than silently lost during platform/provider outage\n"
        "- accepted frozen Notifications with incomplete or ambiguous Schedule binding remain recoverable through idempotent registration and reconciliation rather than becoming silently unscheduled",
    )
    replace_once(
        f,
        "Traceable lifecycle includes request acceptance, snapshot creation, template/version selection, future schedule binding, provider attempt, provider acceptance, receipt, retry, permanent failure, cancellation, replay, and privileged configuration change.",
        "Traceable lifecycle includes request acceptance, snapshot creation, template/version selection, schedule-registration intent, Schedule binding/reconciliation, provider attempt, provider acceptance, receipt, retry, permanent failure, cancellation, replay, and privileged configuration change.",
    )
    replace_once(
        f,
        "- Notification SHALL NOT require every recipient to be an Identity Principal\n"
        "- generic durable scheduling SHALL NOT be reimplemented inside Notification\n"
        "- Notification SHALL own application/Tenant/channel-to-provider/template mapping but SHALL NOT become authoritative for Organization/Tenant/Workspace or application ownership",
        "- Notification SHALL NOT require every recipient to be an Identity Principal\n"
        "- generic durable scheduling SHALL NOT be reimplemented inside Notification\n"
        "- Frozen Notification SHALL durably persist its local scheduling intent before depending on Scheduling and SHALL reconcile incomplete or ambiguous Schedule bindings using a stable idempotency identity\n"
        "- Notification terminal cancellation SHALL gate delivery even if Scheduling cancellation races with or follows durable occurrence dispatch\n"
        "- frozen communication semantics SHALL remain immutable, while operational provider routing/credentials SHOULD remain late-bound unless an explicit governed pinning contract requires otherwise\n"
        "- Notification SHALL own application/Tenant/channel-to-provider/template mapping but SHALL NOT become authoritative for Organization/Tenant/Workspace or application ownership",
    )

    # ------------------------------------------------------------------
    # PAD-PLT-011 Scheduling
    # ------------------------------------------------------------------
    f = "03-domain/PAD-PLT-011-scheduling-platform/PAD-PLT-011-scheduling-platform.pad.md"

    replace_once(f, "  version: 1.1.0", "  version: 1.2.0")
    replace_once(f, "  last_reviewed: 2026-08-22", "  last_reviewed: 2026-08-24")
    replace_once(
        f,
        "- Every Schedule has one owning application and, when Tenant-scoped, one canonical Tenant\n"
        "- Every due Occurrence has a stable identity reused across dispatch retries and replay",
        "- Every Schedule has one owning application and, when Tenant-scoped, one canonical Tenant\n"
        "- Schedule registration is idempotent under a stable consumer command identity; a retry after timeout or ambiguous response MUST resolve to the same logical Schedule when the semantic request is unchanged, and conflicting reuse of the same identity MUST be rejected\n"
        "- Consumers and operators can reconcile a Schedule registration through owned identifiers/correlation without direct database access\n"
        "- Every due Occurrence has a stable identity reused across dispatch retries and replay",
    )
    replace_once(
        f,
        "- One-Time Schedule Registration\n"
        "- Recurring Schedule Registration\n"
        "- Schedule Query and Ownership Discovery",
        "- One-Time Schedule Registration\n"
        "- Recurring Schedule Registration\n"
        "- Idempotent Schedule Registration Recovery and Reconciliation\n"
        "- Schedule Query and Ownership Discovery",
    )
    replace_once(
        f,
        "- Consumers SHALL implement occurrence-level idempotency\n"
        "- Durable recurrence SHALL declare time-zone and misfire semantics",
        "- Consumers SHALL implement occurrence-level idempotency\n"
        "- Consumers SHALL use a stable registration idempotency identity for retryable create operations and SHALL NOT manufacture a second Schedule solely because the original create response was lost\n"
        "- Durable recurrence SHALL declare time-zone and misfire semantics",
    )

    # ------------------------------------------------------------------
    # STD-GLB-010 Durable Scheduled Work
    # ------------------------------------------------------------------
    f = "02-standards/_global/STD-GLB-010-durable-scheduled-work.md"

    replace_once(f, "  version: 1.1.0", "  version: 1.2.0")
    replace_once(f, "  last_reviewed: 2026-08-23", "  last_reviewed: 2026-08-24")
    replace_once(
        f,
        "- Notification **MAY** register its own future delivery after communication intent, recipient snapshot, governed content/template version, and required delivery semantics are frozen\n"
        "- This mode **SHOULD** be the default for pure scheduled communication because it keeps Scheduler payload minimal and establishes Notification lifecycle/status/cancellation at creation time",
        "- Notification **MAY** register its own future delivery after communication intent, recipient snapshot, governed content/template version, and required delivery semantics are frozen\n"
        "- This mode **SHOULD** be the default for pure scheduled communication because it keeps Scheduler payload minimal and establishes Notification lifecycle/status/cancellation at creation time\n"
        "- Notification **MUST** durably record its local scheduling intent before treating the cross-platform Schedule binding as complete\n"
        "- Schedule creation for a Frozen Notification **MUST** use a stable idempotency identity so retry after timeout, process loss, or an ambiguous response cannot create a second logical Schedule for the same registration generation\n"
        "- Notification **MUST** be able to reconcile incomplete or ambiguous Schedule bindings without relying on an atomic transaction spanning Notification and Scheduling\n"
        "- Frozen communication semantics **MUST** remain immutable after acceptance; operational provider route, active credential/secret version, provider endpoint, failover route, and rate-limit state **SHOULD** be resolved at delivery time unless an explicit governed contract pins a configuration version\n"
        "- Notification cancellation **MUST** remain the final delivery gate for a Frozen Notification. Scheduler cancellation reduces future dispatch but **MUST NOT** be relied on to retract an Occurrence already durably dispatched\n"
        "- A late/duplicate `occurrence.due` for a terminally cancelled Notification **MUST** be consumed idempotently as a no-op and **MUST NOT** resurrect delivery",
    )
    replace_once(
        f,
        "- Every Schedule **MUST** have a globally unique, non-enumerable `schedule_id`\n"
        "- Every Schedule **MUST** have one owning `application_id`",
        "- Every Schedule **MUST** have a globally unique, non-enumerable `schedule_id`\n"
        "- Every retryable Schedule-create command **MUST** carry a stable idempotency identity scoped to the authenticated owning application/Tenant context\n"
        "- Reuse of that identity with an equivalent semantic request **MUST** resolve to the same logical Schedule; reuse with conflicting semantic content **MUST** be rejected\n"
        "- Every Schedule **MUST** have one owning `application_id`",
    )
    replace_once(
        f,
        "- Cancellation **MUST NOT** claim to retract an Occurrence whose Trigger was already durably dispatched\n"
        "- Near-due update/cancel races **MUST** have deterministic tested semantics",
        "- Cancellation **MUST NOT** claim to retract an Occurrence whose Trigger was already durably dispatched\n"
        "- A consumer-owned terminal state **MUST** remain authoritative for whether the consumer effect may proceed after dispatch; Scheduler cancellation is not a substitute for consumer-side terminal-state/idempotency checks\n"
        "- Near-due update/cancel races **MUST** have deterministic tested semantics",
    )
    replace_once(
        f,
        "- Contract tests verify one-time, recurring, pause, resume, update, cancel, replay, and optimistic-concurrency semantics\n"
        "- A time-zone golden corpus verifies DST gaps, repeated local times, leap-calendar boundaries, and time-zone-data upgrades",
        "- Contract tests verify one-time, recurring, pause, resume, update, cancel, replay, and optimistic-concurrency semantics\n"
        "- Contract tests verify lost-response Schedule creation retries return the same logical Schedule and conflicting idempotency-key reuse is rejected\n"
        "- Notification/Scheduling composition tests inject process loss between local Notification acceptance, Schedule creation, and binding persistence and prove reconciliation without duplicate Schedule creation\n"
        "- Cancellation-race tests prove a late/duplicate due Occurrence cannot resurrect a terminally cancelled Notification\n"
        "- Frozen-notification tests prove communication-semantic fields remain immutable while non-pinned operational provider configuration/credentials can rotate before delivery\n"
        "- A time-zone golden corpus verifies DST gaps, repeated local times, leap-calendar boundaries, and time-zone-data upgrades",
    )

    # ------------------------------------------------------------------
    # ADR-GLB-011 Scheduling Boundary
    # ------------------------------------------------------------------
    f = "05-decisions/_global/ADR-GLB-011-durable-scheduling-boundary.md"

    replace_once(
        f,
        "**Efficiency:** one additional upfront call, but smallest Scheduler payload, earliest validation, immediate Notification status/cancel/audit identity, and stable recipient/content/version semantics.\n\n"
        "#### Mode B — Deferred Notification Command",
        "**Efficiency:** one additional upfront call, but smallest Scheduler payload, earliest validation, immediate Notification status/cancel/audit identity, and stable recipient/content/version semantics.\n\n"
        "**Consistency:** Notification does not perform a distributed transaction with Scheduling. It durably records a local scheduling intent, creates/retries the Schedule with a stable idempotency identity, persists the resulting binding, and reconciles any ambiguous create response or process-loss window. A Schedule that was created while the Notification process lost the response must be rediscovered/rebound rather than recreated.\n\n"
        "**Cancellation:** Notification terminal state is the final authority over whether delivery may proceed. Scheduler cancellation is attempted asynchronously to avoid unnecessary future dispatch, but a late or already-dispatched Occurrence cannot resurrect a cancelled Notification.\n\n"
        "**Freeze boundary:** communication meaning is frozen, including recipient snapshot, immutable content/template version and data, selected channel, required logical sender identity, immutable attachments, and business correlation. Operational delivery machinery such as current provider route, credential/secret version, endpoint, failover route, and rate-limit state is late-bound by default unless an explicit governed contract pins a configuration version.\n\n"
        "#### Mode B — Deferred Notification Command",
    )
    replace_once(
        f,
        "- Products using enterprise durable scheduling gain a shared asynchronous dependency\n"
        "- Consumers must implement occurrence-level idempotency\n"
        "- Schedule lifecycle and Product business policy can drift and therefore require reconciliation",
        "- Products using enterprise durable scheduling gain a shared asynchronous dependency\n"
        "- Consumers must implement occurrence-level idempotency\n"
        "- Cross-platform callers such as Notification must implement idempotent registration reconciliation because Scheduler creation and caller binding cannot share one local transaction\n"
        "- Schedule lifecycle and Product business policy can drift and therefore require reconciliation",
    )

    # ------------------------------------------------------------------
    # SAD-005 Notification Runtime
    # ------------------------------------------------------------------
    f = "04-system/scnehaux-notification-platform/scnehaux-notification-platform.sad.md"

    replace_once(f, "  version: 1.1.0", "  version: 1.2.0")
    replace_once(f, "  last_reviewed: 2026-08-22", "  last_reviewed: 2026-08-24")
    replace_once(
        f,
        "- Scheduling adapter for frozen future delivery",
        "- Scheduling adapter with durable registration intent, idempotent Schedule creation, binding reconciliation, and asynchronous cancellation for frozen future delivery",
    )
    replace_once(
        f,
        "The runtime must remain correct under duplicate Notification commands, process restart, provider timeout with unknown outcome, duplicate provider callback, provider outage, future-trigger duplicates, template version changes, cancellation races, and noisy-neighbor Tenant/provider load.",
        "The runtime must remain correct under duplicate Notification commands, process restart, provider timeout with unknown outcome, duplicate provider callback, provider outage, future-trigger duplicates, process loss or timeout during cross-platform Schedule registration, template/provider configuration rotation before a frozen delivery becomes due, cancellation races, and noisy-neighbor Tenant/provider load.",
    )
    replace_once(f, "8. Scheduling Adapter", "8. Scheduling Registration, Binding & Reconciliation")
    replace_once(
        f,
        """### 4.4 Runtime Flow — Frozen Scheduled Notification

```mermaid
sequenceDiagram
    participant P as Product
    participant N as Notification
    participant S as Scheduling
    participant K as Kafka

    P->>N: Notification intent + scheduled_at
    N->>N: freeze recipient + template/version + channel profile
    N->>S: register one-time future wake-up
    S-->>N: schedule_id
    N->>N: persist schedule binding
    S-->>K: occurrence.due
    K-->>N: occurrence.due
    N->>N: dedupe occurrence_id and transition delivery to ready
```

This path is prohibited when Product business eligibility must be revalidated at due time. In that case Scheduling wakes the Product worker, which requests Notification after revalidation.
""",
        """### 4.4 Runtime Flow — Frozen Scheduled Notification

```mermaid
sequenceDiagram
    participant P as Product
    participant N as Notification
    participant D as Notification PostgreSQL
    participant R as Schedule Registration Worker
    participant S as Scheduling
    participant K as Kafka

    P->>N: Notification intent + scheduled_at
    N->>D: atomic Notification + frozen communication snapshot + schedule-registration intent
    D-->>N: commit
    N-->>P: accepted notification_id
    R->>D: claim pending registration
    R->>S: create one-time Schedule + stable idempotency identity
    S-->>R: same schedule_id on equivalent retry
    R->>D: persist/reconcile Schedule binding
    S-->>K: occurrence.due
    K-->>N: occurrence.due
    N->>D: dedupe occurrence_id + verify Notification terminal state
    N->>D: transition eligible delivery to ready
```

No correctness-critical transaction spans Notification and Scheduling. If Schedule creation succeeds but the response/binding persistence is lost, retry/reconciliation reuses the stable registration identity and recovers the same logical `schedule_id`.

The frozen snapshot preserves communication semantics: recipient snapshot, immutable template/content version and data, selected channel, required logical sender identity, immutable attachment versions, and business correlation. Active provider route, credential/secret version, endpoint, failover route, and rate-limit state are resolved from current valid Notification-owned configuration at delivery time unless an explicit governed contract pins a configuration version.

This path is prohibited when Product business eligibility must be revalidated at due time. In that case Scheduling wakes the Product worker, which requests Notification after revalidation.

#### 4.4.1 Cancellation Race

Notification cancellation commits the terminal Notification/Delivery state first and emits the required evidence/outbox facts. Cancellation of the bound Schedule is then retried asynchronously using the stored `schedule_id`. If Scheduling has already durably dispatched the Occurrence, Notification consumes/deduplicates it but treats it as a no-op when the Notification is terminally cancelled. A due Occurrence never resurrects a cancelled Notification.
""",
    )
    replace_once(
        f,
        "- communication preference metadata within Notification scope\n"
        "- Scheduling binding\n"
        "- outbox publication state",
        "- communication preference metadata within Notification scope\n"
        "- Scheduling registration intent, registration generation/idempotency identity, binding, and reconciliation metadata\n"
        "- outbox publication state",
    )
    replace_once(
        f,
        "- PII columns are classified and excluded/redacted from telemetry\n"
        "- immutable Template Version and Recipient Snapshot records are enforced by application/schema invariants",
        "- PII columns are classified and excluded/redacted from telemetry\n"
        "- immutable Template Version and Recipient Snapshot records are enforced by application/schema invariants\n"
        "- Schedule registration state supports crash-safe retry/reconciliation and prevents one Notification registration generation from being rebound to multiple logical Schedules",
    )
    replace_once(
        f,
        "- Notification acceptance/query/cancel\n"
        "- Template Family/Version/Channel Variant/schema administration",
        "- Notification acceptance/query/cancel\n"
        "- scheduled-Notification registration/binding status and reconciliation query\n"
        "- Template Family/Version/Channel Variant/schema administration",
    )
    replace_once(
        f,
        "- Scheduling `occurrence.due` for frozen future delivery",
        "- Scheduling idempotent Schedule create/cancel/query semantics and `occurrence.due` for frozen future delivery",
    )
    replace_once(
        f,
        "- callback verification/deduplication state\n"
        "- Tenant/application/channel/provider quota pressure",
        "- callback verification/deduplication state\n"
        "- pending/failed Schedule-registration age and binding-reconciliation backlog\n"
        "- cancelled-Notification late-occurrence no-op count\n"
        "- Tenant/application/channel/provider quota pressure",
    )
    replace_once(
        f,
        "- circuit breakers isolate a failing provider from other providers/channels\n"
        "- consumer/event processing follows the enterprise idempotency and DLQ standard",
        "- circuit breakers isolate a failing provider from other providers/channels\n"
        "- consumer/event processing follows the enterprise idempotency and DLQ standard\n"
        "- Schedule registration and cancellation calls are retried with stable idempotency identities; an ambiguous create response is reconciled before any new logical Schedule may be created",
    )
    replace_once(
        f,
        "Runbooks cover provider outage, sender credential rotation, provider rate-limit exhaustion, stuck backlog, duplicate callback, unknown delivery outcome, Scheduling outage, callback outage, replay/reconciliation, and rollback.",
        "Runbooks cover provider outage, sender credential rotation, provider rate-limit exhaustion, stuck backlog, duplicate callback, unknown delivery outcome, Scheduling outage, pending/ambiguous Schedule binding reconciliation, cancellation race/late occurrence, callback outage, replay/reconciliation, and rollback.",
    )
    replace_once(
        f,
        "- Notification and Delivery idempotency tests\n"
        "- duplicate-send fault-injection tests\n"
        "- retry/error-classification tests",
        "- Notification and Delivery idempotency tests\n"
        "- duplicate-send fault-injection tests\n"
        "- crash/fault tests across Notification acceptance, Schedule creation, lost response, and binding persistence\n"
        "- Schedule-registration idempotency and orphan/missing-binding reconciliation tests\n"
        "- cancellation-race tests proving late/duplicate `occurrence.due` cannot resurrect a terminal Notification\n"
        "- frozen-semantics tests proving immutable communication fields remain fixed while non-pinned provider credentials/routes may rotate before due time\n"
        "- retry/error-classification tests",
    )
    replace_once(
        f,
        "- Frozen Notification is the default scheduled-communication mode; bounded Deferred Notification Command is also supported when Scheduler does not become a communication-data authority\n"
        "- Application Notification Profile is Notification-owned configuration; Organization/Application Trust remain canonical for Tenant/application identity and ownership",
        "- Frozen Notification is the default scheduled-communication mode; bounded Deferred Notification Command is also supported when Scheduler does not become a communication-data authority\n"
        "- Frozen Notification uses local durable registration intent plus idempotent/reconcilable Schedule binding; no distributed transaction is assumed across Notification and Scheduling\n"
        "- Notification terminal cancellation remains the final delivery gate when Scheduler cancellation races with durable occurrence dispatch\n"
        "- Frozen communication meaning is immutable while operational provider realization is late-bound by default unless an explicit governed version pin is required\n"
        "- Application Notification Profile is Notification-owned configuration; Organization/Application Trust remain canonical for Tenant/application identity and ownership",
    )

    # ------------------------------------------------------------------
    # SAD-013 Scheduling Runtime
    # ------------------------------------------------------------------
    f = "04-system/scnehaux-scheduling-platform/scnehaux-scheduling-runtime.sad.md"

    replace_once(f, "  version: 1.1.0", "  version: 1.2.0")
    replace_once(f, "  status: draft", "  status: approved")
    replace_once(f, "  last_reviewed: 2026-08-22", "  last_reviewed: 2026-08-24")
    replace_once(
        f,
        "The runtime must remain correct under duplicate commands, concurrent replicas, process termination during due processing, broker outage, time-zone/DST transitions, near-due update/cancel races, and prolonged outage followed by recovery.",
        "The runtime must remain correct under duplicate commands, lost/ambiguous create responses, concurrent replicas, process termination during due processing, broker outage, time-zone/DST transitions, near-due update/cancel races, and prolonged outage followed by recovery.",
    )
    replace_once(
        f,
        """    C->>S: Create Schedule + idempotency key
    S->>S: authenticate, authorize, validate target and time policy
    S->>D: atomic Schedule/idempotency/lifecycle-outbox transaction
    D-->>S: commit
    S-->>C: schedule_id, version, next occurrence
```
""",
        """    C->>S: Create Schedule + stable idempotency key
    S->>S: authenticate, authorize, validate target and time policy
    S->>D: atomic Schedule/idempotency/lifecycle-outbox transaction
    D-->>S: commit
    S-->>C: schedule_id, version, next occurrence
```

The idempotency record is scoped to authenticated application/Tenant ownership. An equivalent retry with the same identity returns the same logical `schedule_id` even when the original response was lost. Reuse of the identity with conflicting semantic Schedule content is rejected. The Control API exposes owned query/reconciliation semantics sufficient for a caller to recover the binding without direct database access.
""",
    )
    replace_once(
        f,
        "- command idempotency state\n"
        "- registered-target projection",
        "- command idempotency state\n"
        "- create-command semantic fingerprint and stable idempotency-to-`schedule_id` mapping required for lost-response recovery\n"
        "- registered-target projection",
    )
    replace_once(
        f,
        "The Control API is versioned under the enterprise API standard and provides command/query capabilities for create, read/list, update, pause, resume, cancel, preview, occurrence query, replay, target discovery, and reconciliation.",
        "The Control API is versioned under the enterprise API standard and provides command/query capabilities for idempotent create, create-result recovery/reconciliation, read/list, update, pause, resume, cancel, preview, occurrence query, replay, target discovery, and reconciliation.",
    )
    replace_once(
        f,
        "- idempotency key\n"
        "- expected Schedule version where mutation races are possible",
        "- idempotency key\n"
        "- semantic consistency with any prior command using the same scoped idempotency identity\n"
        "- expected Schedule version where mutation races are possible",
    )
    replace_once(
        f,
        "- Kafka schema compatibility and duplicate-delivery tests\n"
        "- Tenant isolation, quota, and saturation tests",
        "- Kafka schema compatibility and duplicate-delivery tests\n"
        "- lost-create-response retry tests proving the same logical `schedule_id` is returned\n"
        "- conflicting idempotency-key reuse tests\n"
        "- Notification binding-reconciliation contract tests covering Schedule creation followed by caller process loss before local binding persistence\n"
        "- Tenant isolation, quota, and saturation tests",
    )
    replace_once(
        f,
        "- ADR-SCH-001 selects PostgreSQL temporal authority and Kafka dispatch\n"
        "- global outbox, database, event, resilience, and observability standards are inherited rather than redefined\n"
        "- custom Scnehaux Scheduler Experience is a separate deployable under SAD-014",
        "- ADR-SCH-001 selects PostgreSQL temporal authority and Kafka dispatch\n"
        "- global outbox, database, event, resilience, and observability standards are inherited rather than redefined\n"
        "- Schedule creation is idempotent and recoverable after ambiguous responses; Scheduler never requires a caller to create a second logical Schedule merely because a response or caller-local binding write was lost\n"
        "- custom Scnehaux Scheduler Experience is a separate deployable under SAD-014",
    )

    # ------------------------------------------------------------------
    # Generated SAD index
    # ------------------------------------------------------------------
    f = "04-system/INDEX.md"
    replace_once(
        f,
        "| [SAD-013](scnehaux-scheduling-platform/scnehaux-scheduling-runtime.sad.md) | Scnehaux Scheduling Runtime | PAD-PLT-011 | Scheduling Platform Team | draft |",
        "| [SAD-013](scnehaux-scheduling-platform/scnehaux-scheduling-runtime.sad.md) | Scnehaux Scheduling Runtime | PAD-PLT-011 | Scheduling Platform Team | approved |",
    )

if __name__ == "__main__":
    try:
        apply_all()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print("\nHardening applied.")
    print("Next:")
    print("  make generate-docs")
    print("  python -m pytest 06-fitness-function/tests -q")
    print("  git diff --check")
    print("  git diff")
