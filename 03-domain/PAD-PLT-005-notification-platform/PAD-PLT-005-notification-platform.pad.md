---
doc_meta:
  id: PAD-PLT-005
  title: Enterprise Notification Platform
  owner: Notification Platform Team
  version: 2.2.1
  status: approved
  classification: restricted
  governed_by:
    - GDC-008
    - ADR-GLB-017
  realizes_capability:
    - EAD-001
    - EAD-005
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-08-24
  fulfilled_by:
    - SAD-005
    - SAD-015
---

# Enterprise Notification Platform

## 1. Purpose & Scope

The Enterprise Notification Platform provides shared communication-delivery capability for Scnehaux Products and Platforms. It accepts an authorized communication intent, freezes the minimum communication-semantic snapshot required for correctness, resolves a governed template/channel variant, routes through an authorized sender/channel profile, executes provider delivery asynchronously, applies communication retry policy, and tracks normalized delivery outcomes.

Products own **why a communication is needed**, the business event or rule behind it, and business-recipient eligibility. Notification owns **how an accepted communication is rendered and delivered**.

The platform supports email, WhatsApp/messaging-provider delivery, SMS, push, and governed webhook channels through replaceable adapters.

Notification also owns **Application Notification Profile** configuration: the mapping from an authorized application/Tenant/channel context to Notification-owned sender/channel/provider/template policy. Organization remains authoritative for Tenant/Workspace facts, Application/Service Trust remains authoritative for application/workload identity and ownership, and Trust/Secret Services remain authoritative for secret custody.

### 1.1 Out Of Scope

- Product business event generation, business rules, or business recipient eligibility
- Generic durable application scheduling
- Workflow process orchestration
- Gmail/mailbox ingestion, inbound email polling, or business-message parsing
- Customer/contact system-of-record ownership
- Identity account lifecycle or authentication
- Product business authorization and irreversible Product outcomes
- Arbitrary external integration unrelated to communication delivery
- Marketing campaign/business-domain ownership unless separately chartered
- Provider credential custody outside enterprise Trust/Secret Services

## 2. Enterprise Traceability

### 2.1 Realizes

- **EAD-001** — Notification & Communication shared enabling capability
- **EAD-005** — multi-tenant reusable communication execution capability on the enterprise runtime substrate

### 2.2 Relationships

- **Products/Platforms:** publish or submit authorized Notification intents; Product business authority remains upstream
- **Scheduling Platform:** provides generic durable future wake-up when a Notification is already accepted/frozen and only delivery time remains; cross-platform registration uses an idempotent Schedule command and recoverable binding rather than a correctness-critical distributed transaction
- **Document Platform:** supplies immutable attachment/version references when attachments are used
- **Identity / Organization / Application Trust:** establish authenticated caller, application ownership, Tenant scope, and optional Principal contact resolution without requiring every recipient to be a Principal; administrative profile validation may use bounded/local projections and normal delivery does not require a per-send synchronous Organization call
- **Trust Services:** hold provider/API/SMTP credentials; Notification stores only governed provider/channel configuration and secret references
- **Event & Messaging:** carries Notification request/lifecycle contracts where asynchronous integration is selected
- **Integration Enablement:** optional reusable connector/protocol machinery when it adds value; it is not a mandatory network hop between Notification and its natural communication providers
- **Audit & Evidence:** receives privileged configuration/test-send/replay evidence

### 2.3 Consumed By

All Scnehaux Products and Platforms may consume Notification. Initial migration consumers include:

- Mailcast client workloads for outbound WhatsApp/email delivery and template/provider machinery
- ATI PH for governed public-holiday email delivery
- Workflow for human-task, escalation, and process communications
- HCM, finance operations, travel operations, approvals, and future Products requiring governed communication

Consumers do not synchronously wait for provider delivery. A control/API command may return accepted state, while actual provider interaction remains asynchronous.

## 3. Domain & Context Model

### 3.1 Bounded Context

- Notification Request
- Recipient Snapshot
- Template & Channel Variant
- Channel / Sender Profile
- Application Notification Profile
- Provider Routing
- Delivery Planning
- Delivery Execution
- Delivery Retry
- Provider Callback & Receipt Normalization
- Delivery Tracking
- Communication Preference Enforcement
- Scheduled Notification Binding
- Notification Governance

### 3.2 Ubiquitous Language

| Term                             | Meaning                                                                                                                                                                              |
| :------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Notification                     | Accepted communication intent tracked by the platform                                                                                                                                |
| Recipient Snapshot               | Immutable destination endpoint and bounded recipient metadata used for one Notification                                                                                              |
| Template Family                  | Stable semantic communication type managed through platform lifecycle                                                                                                                |
| Template Version                 | Immutable governed version of template content and data contract                                                                                                                     |
| Channel Variant                  | Email, WhatsApp, SMS, Push, Webhook, or other realization of one Template Version                                                                                                    |
| Channel Profile                  | Sender identity, provider binding, routing policy, and secret references for one channel context                                                                                     |
| Application Notification Profile | Notification-owned configuration that binds authorized application/Tenant/channel context to sender/channel/provider/template policy without owning the application or Tenant itself |
| Deferred Notification Command    | Bounded registered command delivered by Scheduling that causes Notification creation at due time rather than at schedule-registration time                                           |
| Provider Binding                 | Notification-owned provider configuration that references secrets held by Trust Services                                                                                             |
| Delivery                         | One recipient/channel delivery lifecycle                                                                                                                                             |
| Delivery Attempt                 | One provider interaction attempt within a Delivery lifecycle                                                                                                                         |
| Provider Acceptance              | Provider accepted a send request; not necessarily final channel delivery                                                                                                             |
| Delivery Receipt                 | Provider/channel evidence of final or intermediate delivery where available                                                                                                          |
| Delivery Status                  | Provider-independent normalized state owned by Notification                                                                                                                          |
| Scheduled Notification           | Accepted Notification whose communication semantics are frozen and which awaits a durable future wake-up from Scheduling                                                             |
| Scheduling Binding               | Recoverable association between one Notification scheduling intent and the Scheduler Schedule identity created idempotently for it                                                   |

### 3.3 Domain Policies

- Product domains own Notification intent and business recipient eligibility
- Notification owns accepted communication snapshots, template/version lifecycle, provider routing, delivery attempts, retry, and normalized delivery state
- Provider acceptance and final delivery are distinct states
- Every non-idempotent provider send is protected by a platform delivery identity/idempotency strategy
- Template versions and recipient snapshots used for an accepted Notification are immutable
- Template data contracts are machine-validatable; a UI-only variable registry is not sufficient authority
- Template rendering cannot execute arbitrary Product code
- Product business aggregates are not copied into Notification; only bounded values required to render/deliver the accepted communication are snapshotted
- External recipients may be email addresses, phone/WhatsApp endpoints, device endpoints, or registered webhook endpoints without being enterprise Principals
- Product/Legal authority retains business-specific consent meaning; Notification enforces communication preferences/policy facts within its declared scope
- Generic future scheduling is delegated to the Scheduling Platform
- Pure scheduled communication SHOULD use a frozen Notification registered with Scheduling when recipient/content/version semantics must be preserved from creation time
- Frozen Notification preserves communication meaning at acceptance time, including recipient snapshot, immutable template/content version and data, selected channel, logical sender identity where required, immutable attachment/version references, and business correlation needed for the accepted communication
- Provider route, current provider credential/secret version, provider endpoint, failover route, rate-limit state, and comparable operational delivery machinery SHOULD be resolved at delivery time from the current valid Notification-owned configuration unless an explicit governed contract requires a pinned configuration version
- Frozen Notification registration SHALL NOT depend on an atomic cross-service transaction between Notification and Scheduling; Notification SHALL durably record its local scheduling intent, register the Schedule with a stable idempotency identity, persist/recover the returned binding, and reconcile missing or ambiguous bindings
- Notification cancellation is authoritative for whether a not-yet-started Notification Delivery may proceed; cancellation of the corresponding Scheduler Schedule is asynchronous cleanup/optimization and a late or already-dispatched Scheduling Occurrence SHALL NOT resurrect a terminally cancelled Notification
- A Product MAY schedule a bounded Deferred Notification Command directly to Notification when no Notification must exist before due time and Scheduler does not become a communication-data store
- If business eligibility, recipient, or content must be revalidated at due time, Scheduling targets the owning Product/Platform Worker before Notification is requested
- Application Notification Profile resolution is Notification authority; Organization/Application Trust supply canonical context/ownership and are not replaced by Notification-local configuration
- Notification retries only delivery operations it owns; Product business retry remains Product/Workflow responsibility

## 4. Integration Contracts

### 4.1 Integration Provided

The Notification Platform provides:

- Notification intent acceptance
- Email delivery
- WhatsApp / messaging-platform delivery
- SMS delivery
- Push delivery
- Governed webhook delivery
- Template family/version/channel-variant management
- Template data-schema validation and preview
- Recipient snapshot and optional recipient-resolution contracts
- Channel/sender/provider profile management
- Application Notification Profile management by authorized application/Tenant/channel scope
- deferred Notification command acceptance from registered Scheduling targets
- Frozen scheduled-notification registration with idempotent/reconcilable Scheduling binding
- Delivery retry and cancellation
- Provider callback/receipt normalization
- Delivery status query
- Notification lifecycle events
- Test-send and administrative validation under privileged policy

### 4.2 Integration Consumed

The Notification Platform consumes:

- Scheduling Platform for durable future wake-up of frozen Notifications using stable idempotent registration and reconciliation semantics
- Document Platform for immutable attachment versions
- Identity / Organization / Application Trust for caller, ownership, Tenant scope, and optional Principal contact resolution
- Trust Services for provider/SMTP/API credential material through secret references
- bounded locally usable Organization/Application Trust context for profile ownership validation without a required per-delivery synchronous control-plane call
- Event & Messaging for asynchronous intent and lifecycle propagation
- Audit & Evidence for privileged-operation evidence
- optional reusable Integration connectors where justified by the specific provider relationship

SMTP host/port/TLS mode, sender identity, provider selection, messaging-provider endpoint metadata, and comparable delivery configuration remain Notification-owned because they directly control Notification behavior. Passwords, OAuth refresh tokens, private keys, and API secrets remain Trust-owned. For a Frozen Notification, communication semantics are immutable while operational provider realization is late-bound by default unless an explicit version-pinning contract says otherwise.

## 5. Trust & Data Boundaries

### 5.1 Trust Boundary

Notification is authoritative for its Notification aggregate, communication template/version lifecycle, channel/provider routing configuration, Delivery state, and provider-normalized outcomes.

Notification is not authoritative for Product state that motivated the communication, canonical customer/employee/contact truth, or provider credential custody.

### 5.2 Identity Access

- Human/workload callers authenticate through enterprise Identity and are authorized within application/Tenant scope
- External recipients need not be Identity Principals
- direct recipient endpoints are accepted only through authorized bounded contracts and are snapshotted with purpose/correlation
- provider callbacks are authenticated using provider-specific signature/credential contracts
- privileged template publication, channel-profile mutation, test-send, replay, and cross-Tenant operations require evidence

### 5.3 Data Classification

Notification manages:

- communication metadata and correlation
- Template Families, immutable versions, channel variants, and template data schemas
- Recipient Snapshots and delivery endpoints
- Channel Profiles and Provider Bindings excluding raw secrets
- Application Notification Profiles keyed by authorized application/Tenant/channel scope
- Delivery and Delivery Attempt state
- provider identifiers, callbacks, and normalized receipts
- communication preference metadata within the platform scope
- scheduled-notification registration intent, reconciliation metadata, and binding to a Scheduling identifier

Recipient endpoints are treated as PII where applicable.

Notification does not own Product business records, HR/finance/travel transactions, provider secrets, or source mailbox contents.

## 6. Capability NFR

### 6.1 Availability, RTO, and RPO

- Reliability class: **C1 Mission-Critical Operations**
- Target mature service availability: **>= 99.95% monthly** for Notification acceptance and internal delivery processing
- Target RTO: **<= 1 hour**
- Target RPO: **<= 15 minutes**
- accepted Notifications are delayed rather than silently lost during platform/provider outage
- accepted frozen Notifications with incomplete or ambiguous Schedule binding remain recoverable through idempotent registration and reconciliation rather than becoming silently unscheduled

### 6.2 Delivery SLO and Scalability

- internal accepted-to-ready processing target: **99.9% within 30 seconds** for immediate Notifications, excluding provider latency and intentionally scheduled delivery
- production capacity certification demonstrates **10x forecast peak accepted-notification rate** without breaching internal processing SLO
- provider/channel/Tenant bulkheads prevent one provider or Tenant from exhausting unrelated delivery capacity
- large fan-out is expanded through bounded asynchronous work rather than one unbounded transaction
- provider rate limits and Tenant/application quotas are explicit

Final provider delivery time is not used as a universal platform SLO because provider/channel capabilities differ. Provider-specific SLOs are declared by Channel Profile where evidence exists.

### 6.3 Security, Compliance, Data Privacy, and Residency

- Tenant-isolated communication configuration and delivery state
- raw provider credentials never persist in Notification operational tables or browser clients
- recipient PII is minimized, redacted in telemetry, and retained according to communication/evidence policy
- sender domain/number/profile ownership is verified before production enablement
- provider callbacks are authenticated
- regional/silo deployment profiles remain available for contractual residency requirements

### 6.4 Audit and Interoperability

Traceable lifecycle includes request acceptance, snapshot creation, template/version selection, schedule-registration intent, Schedule binding/reconciliation, provider attempt, provider acceptance, receipt, retry, permanent failure, cancellation, replay, and privileged configuration change.

Provider-specific vocabulary stays behind adapters; Products consume stable Notification contract semantics.

### 6.5 Cost Target

Cost is measured by channel/provider usage and accepted/delivered units per Tenant/application. Quotas and provider routing prevent unbounded shared cost.

## 7. Ownership & Governance

### 7.1 Team Ownership

Notification Platform Team owns:

- Notification contract and aggregate
- template/version/channel-variant machinery
- recipient snapshot and delivery planning
- Channel Profiles and Provider Bindings excluding secret custody
- Application Notification Profile lifecycle and application/Tenant/channel routing policy
- provider/channel adapters
- delivery retry and status normalization
- provider callbacks and reconciliation
- communication reliability, observability, operations, and support

Product teams own business intent, business timing semantics, recipient eligibility, and business follow-up.

Scheduling Team owns generic durable future trigger mechanics. Trust Services own credential/key custody.

### 7.2 Realizing Systems

- **SAD-005** Scnehaux Notification Runtime
- **SAD-015** Scnehaux Notification Experience

### 7.3 Governance Rules

- Products SHALL use Notification for enterprise communication delivery when the platform contract satisfies the channel requirement
- Notification SHALL NOT own Product business timing or eligibility
- Notification SHALL NOT require every recipient to be an Identity Principal
- generic durable scheduling SHALL NOT be reimplemented inside Notification
- Frozen Notification SHALL durably persist its local scheduling intent before depending on Scheduling and SHALL reconcile incomplete or ambiguous Schedule bindings using a stable idempotency identity
- Notification terminal cancellation SHALL gate delivery even if Scheduling cancellation races with or follows durable occurrence dispatch
- frozen communication semantics SHALL remain immutable, while operational provider routing/credentials SHOULD remain late-bound unless an explicit governed pinning contract requires otherwise
- Notification SHALL own application/Tenant/channel-to-provider/template mapping but SHALL NOT become authoritative for Organization/Tenant/Workspace or application ownership
- normal Notification delivery SHALL NOT require a synchronous Organization lookup when validated local context/projection is sufficient
- Workspace Experience, Workflow, and Work Management SHALL NOT be introduced solely to resolve Notification provider/profile configuration
- provider models SHALL terminate at Notification adapters and never leak into Product contracts
- provider transport acceptance SHALL NOT be represented as final delivery unless the channel/provider contract proves it
- browser clients SHALL NOT receive decrypted provider credentials after registration

## 8. Assumptions & Constraints

- Email and WhatsApp are initial migration channels because Mailcast and ATI PH provide immediate consumers
- Additional channels are introduced behind the same logical Delivery contract
- Provider capability differences are normalized without inventing delivery guarantees a provider cannot prove
- Scheduling, Trust, Event & Messaging, Identity/Organization context, and Document capabilities are adopted according to migration sequencing

## 9. Architectural Decisions

- ADR-GLB-011 removes generic temporal scheduling authority from Notification
- global event/outbox/resilience/database standards govern asynchronous delivery mechanics
- provider/channel implementation decisions belong in SAD/TDD or future domain decisions when they create a durable trade-off

## 10. Evolution

Notification begins with the channels required by real consumers and expands through provider/channel adapters. Communication-domain contracts remain stable if provider SDKs, SMTP implementation, messaging vendor, or internal worker topology changes.

## 11. References

- EAD-001 Enterprise Capability & Domain Map
- EAD-002 Enterprise System Landscape
- EAD-004 Enterprise Integration Architecture
- EAD-005 Enterprise Platform Architecture
- EAD-006 Enterprise Security Architecture
- ADR-GLB-011 Enterprise Durable Scheduling Boundary
- STD-GLB-004 Event-Driven Architecture & Messaging
- STD-GLB-010 Durable Scheduled Work
- ADR-GLB-014 Background Worker Network Boundary
- STD-GLB-012 Background Worker Network Exposure
