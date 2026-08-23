---
doc_meta:
  id: EAD-004
  title: Enterprise Integration Architecture
  owner: Architecture Authority
  version: 1.2.0
  status: approved
  classification: internal
  governed_by: [GDC-006]
  review_cycle_days: 180
  created_date: 2026-08-06
  last_reviewed: 2026-08-23
---

# Enterprise Integration Architecture

## 1. Purpose

Define macro interaction patterns for Product, Platform, Governance, external provider, AI, knowledge, asynchronous job, workflow, and scheduled execution contracts.

**Decision question:** _Which interaction relationship is appropriate, who owns the contract and outcome, and how are failure, duplication, identity, authorization, and reconciliation preserved across boundaries?_

## 2. Scope

**In scope**

- Synchronous APIs, async commands/events, files/batches, webhooks/callbacks, projections, Workflow, Scheduling, background jobs, AI inference, retrieval, and tool invocation
- Provider/natural-owner relationships
- Contract ownership, compatibility, idempotency, ambiguity, and reconciliation
- AI provider and tool protocol boundaries including protocol-neutral MCP interoperability
- Context propagation across identity, application, tenant, purpose, classification, and correlation

**Out of scope**

- Endpoint/payload schemas
- Product-specific workflow
- Concrete brokers/gateways/connector topology
- Model/provider SDK selection
- Tool implementation detail
- Credential/token implementation

## 3. Enterprise Context

Scnehaux integrates internal Product/Platform systems and external client/industry/model providers. A protocol does not determine business authority.

Shared Integration may provide connector/protocol/transformation machinery. The natural owner remains accountable for business/provider meaning. For AI model providers, AI Enablement is the natural capability owner for provider execution semantics while Integration may provide reusable protocol/connectivity machinery.

## 4. Architectural Drivers & Lessons

### 4.1 Drivers

| ID | Driver | Integration Consequence |
| :-- | :-- | :-- |
| D1 | Multiple durable execution forms | Commands, Jobs, Workflows, and Schedules remain distinct |
| D2 | AI model and tool ecosystems change rapidly | Provider and tool contracts are capability-based and protocol-neutral |
| D3 | RAG crosses Product/data boundaries | Retrieval is an explicit authorized contract |
| D4 | External outcomes are ambiguous | Acceptance, completion, reconciliation, and evidence are distinct |
| D5 | Model/provider switching is desired | Portability requires evaluation, not assumed equivalence |
| D6 | Shared integration must not become central coupling | Natural Owner rule remains mandatory |
| D7 | Local authoritative state changes may require external event publication | Atomic publication intent remains inside the source transaction boundary; shared delivery machinery does not become a second authority |

### 4.2 Lessons Incorporated

| Lesson | Response |
| :-- | :-- |
| Async transport acknowledgement was treated as business completion | Commands and outcomes remain distinct |
| Queue was treated as work/business state | Queue remains a delivery/buffering mechanism unless a domain explicitly owns queue semantics |
| MCP/provider SDK was treated as architecture | Protocol adapters sit behind stable tool/provider contracts |
| SSO and API credentials were treated as interchangeable | Interactive and workload access profiles are distinct |
| Integration mediated every external provider | Shared Integration remains optional machinery |
| Model change was treated as configuration-only | Evaluation and release gates protect semantic compatibility |
| A central outbox service was treated as the transaction boundary | Outbox state stays local to the authoritative mutation; shared relays/CDC may transport it after commit |

## 5. Architecture Model

### 5.1 Strategic Interaction Types

| Pattern | Use |
| :-- | :-- |
| Synchronous Request/Response | Immediate authoritative response is required |
| Asynchronous Command | Bounded work is accepted without immediate completion |
| Domain Event | Accepted fact is published to independent consumers |
| Background Job | Technical bounded execution inside an owning Product/Platform |
| Durable Workflow | Persisted multi-step coordination, human/system tasks, compensation |
| Durable Schedule | Future temporal trigger independent of consumer restart |
| Bounded Projection | Local resilient reads/enforcement |
| Batch / File | High-volume or partner-driven exchange |
| Webhook / Callback | External provider asynchronous notification |
| Retrieval | Authorized knowledge/search query returning provenance/evidence |
| AI Inference | Model execution under an AI capability profile |
| Agent Run | Bounded iterative model/tool execution |
| Tool Invocation | Delegated operation against a registered Product/Platform tool contract |

### 5.2 Work/Workflow/Job/Schedule Interaction

```text
Product owns business intent
    ├─ Work Item → Work Management
    ├─ Multi-step process → Workflow
    ├─ Future trigger → Scheduling
    └─ Bounded technical execution → Job / Worker runtime
```

A Queue may support any of these but does not redefine their authority.

### 5.2.1 Scheduled Communication Composition

Scheduled communication supports three compositions with different authority and efficiency characteristics.

| Mode | Flow | Best fit | Main trade-off |
| :-- | :-- | :-- | :-- |
| Frozen Notification | `Product -> Notification -> Scheduling -> Notification` | Communication already accepted and recipient/content/version semantics must be preserved from creation time | One additional upfront call, but smallest Scheduler payload, earliest validation, stable Notification lifecycle, and clean cancellation/status |
| Deferred Notification Command | `Product -> Scheduling -> Notification` | A lightweight communication command may be created only when due and bounded trigger data is sufficient | Fewer upfront calls, but validation is delayed and Scheduler is coupled to a registered Notification command contract |
| Revalidated Business Action | `Product -> Scheduling -> Product Worker -> Notification` | Eligibility, recipient, content, or business state may change before due time | Extra execution hop, but preserves Product authority and current-state correctness |

**Default:** use Frozen Notification for pure scheduled communication.

Deferred Notification Command is permitted only when it does not turn Scheduling into a communication-data store. Scheduler carries a registered target plus bounded identifiers or immutable trigger input. Provider credentials, SMTP configuration, provider secrets, unbounded content, and arbitrary recipient/contact datasets remain outside Scheduling.

If current Product state must be revalidated, the due occurrence targets the owning Product/Platform Worker before Notification is requested.
### 5.3 AI Provider Contract

AI consumers request a stable capability/profile. Provider selection is performed by AI Enablement policy and evaluation.

```text
Product
  → AI Contract
      → capability/profile
      → routing/evaluation policy
          → provider/model endpoint
```

Provider switching SHALL NOT imply semantic equivalence without evaluation evidence.

### 5.4 Provider Access Modes

Interaction contracts distinguish:

- workload API credentials
- cloud workload identity
- delegated user authorization/OAuth where supported
- enterprise SSO/seat-bound interactive access where supported
- local/self-hosted runtime identity

An interactive SSO/seat session SHALL NOT be silently repurposed as shared machine authority.

### 5.5 Tool Interoperability

The stable enterprise abstraction is an **AI Tool Contract** containing:

- tool identifier and owner
- input/output schema
- required authorization/scope
- side-effect/risk class
- idempotency semantics
- approval/human-confirmation requirement
- evidence/correlation

MCP, native APIs, gRPC, or SDK bindings are transport/adapters. Product authorization remains enforced near the protected resource.

### 5.6 Retrieval Contract

Retrieval contracts contain:

- query and retrieval profile
- authorized knowledge scope
- identity/application/tenant/purpose context
- requested evidence/provenance
- result quality/freshness metadata

Consumers SHALL NOT bind to graph/vector/search-engine implementation details.

### 5.7 Natural Ownership Rule

- Product/control domain owns business intent and outcome
- Provider domain owns its published contract
- AI Platform owns AI provider execution semantics
- Knowledge & Retrieval owns retrieval contract
- Integration owns reusable connector/protocol machinery when justified
- External authority remains as defined by EAD-003

### 5.8 Enterprise Context Map

```text
Control / Platform Authorities
        ↕ governed contracts
Business Products
        ↕ natural-owner contracts
External / Client / Industry / AI Providers

Shared Integration may supply connector machinery on selected edges.
Engineering & Runtime supplies API/connectivity/messaging substrate.
```

### 5.9 Communication Strategy

Pattern selection follows responsibility and timing: synchronous query/command, asynchronous command/event, Job, Workflow, Schedule, projection, file/batch, webhook, retrieval, inference, agent run, and tool invocation are distinct contracts.

### 5.10 Contract Governance

Every critical contract declares provider owner, consumer class, authority boundary, version/compatibility, identity/Tenant/purpose/classification context, idempotency where relevant, failure/outcome semantics, observability, and lifecycle/deprecation.

### 5.11 Gateway & Broker Topology

Gateway, broker, connector, AI gateway, and tool gateway are technical roles rather than Product authorities.

- gateway does not replace Product authorization
- broker delivery does not prove business completion
- connector does not own Product intent
- AI gateway does not own Product/Knowledge truth
- no gateway/broker is a universal mandatory hop without justified capability

### 5.12 Transactional Publication Boundary

When a local authoritative state mutation and its external event publication must succeed or fail as one logical operation, the publication intent is persisted **inside the same local transactional authority** as the state mutation.

```text
Source Product / Platform DB transaction
├─ authoritative mutation
└─ outbox publication intent
        ↓ COMMIT
local relay / shared relay / CDC
        ↓
enterprise messaging
```

A separate central Outbox database/service is not an atomic substitute for the source transaction because it recreates a distributed dual-write boundary.

The following may be shared without moving authority:

- outbox library/schema conventions
- relay implementation
- CDC infrastructure
- event envelope and schema tooling
- telemetry and operational dashboards

Outbox state itself remains owned by the source Product/Platform transaction.
## 6. Principles & Rules

### 6.1 Contract First
- **Fitness function:** every production integration resolves to a registered owner and contract

### 6.2 Pattern Follows Responsibility
- **Fitness function:** critical relationships identify whether they are query, command, event, Job, Workflow, Schedule, retrieval, inference, or tool invocation

### 6.3 Natural Owner Retains Meaning
- **Fitness function:** shared Integration PADs contain zero Product-specific outcomes

### 6.4 Provider Portability Is Evaluated
- **Fitness function:** provider/model promotion has quality/safety/cost/latency evidence appropriate to the Product profile

### 6.5 Interactive and Machine Credentials Are Distinct
- **Fitness function:** credential inventory classifies human interactive versus workload authority

### 6.6 Tool Calls Preserve Product Authorization
- **Fitness function:** high-risk AI tool paths enforce Product authorization and required approval at the resource boundary

### 6.7 Retrieval Is Authorized Before Disclosure
- **Fitness function:** cross-tenant/unauthorized retrieval negative tests run before model context assembly

### 6.8 No Universal Integration Hop
- **Fitness function:** architecture review reports zero mandatory hops justified solely by uniformity

### 6.9 Critical External Outcomes Reconcile
- **Fitness function:** critical provider contracts declare unresolved-state and reconciliation ownership

### 6.10 Atomic Publication Stays With Source Authority
- **Fitness function:** transactional publishers have zero network write to a separate outbox authority inside the source commit path; publication intent is atomically persisted with the authoritative mutation or an equivalent atomic mechanism is proven
## 7. Alternatives Considered

| Alternative | Why Rejected |
| :-- | :-- |
| REST everywhere | Misfits long-running and asynchronous work |
| Event-driven everything | Confuses commands, current queries, and outcomes |
| Queue means workflow/job | Hides ownership and lifecycle distinctions |
| Universal ESB / Integration hop | Centralizes coupling and obscures ownership |
| MCP as mandatory tool architecture | Couples enterprise contract to one transport |
| Provider SDKs directly in Products | Leaks provider semantics and prevents governed portability |
| Reuse human SSO session for workers | Destroys attribution, lifecycle, and workload identity boundaries |

## 8. Single Points of Failure & Graceful Degradation

| Dependency | Blast Radius | Required Posture |
| :-- | :-- | :-- |
| Messaging | Delayed commands/events | Durable accepted work and replay |
| Integration connector | Provider-specific | Isolate by provider/tenant and reconcile |
| AI provider | AI profile | Evaluated fallback or explicit degradation |
| Knowledge retrieval | Grounded AI/search | Explicit degraded mode; no fabricated evidence |
| Tool provider/Product API | Agent task | Tool failure does not grant alternate authority |
| Scheduling | Future triggers | Durable recovery/misfire |
| Workflow | Stateful process | Durable resumability |

## 9. Ownership

| Responsibility | Accountable |
| :-- | :-- |
| Enterprise interaction principles | Architecture Authority |
| Business contract | Provider/Natural Owner |
| Shared integration machinery | Integration Platform |
| AI provider execution contract | AI Platform |
| Retrieval contract | Knowledge & Retrieval Platform |
| Tool business operation | Owning Product/Platform |

## 10. Dependencies

- This C1 architecture artifact has no synchronous runtime dependency on another architecture artifact
- Its inputs are enterprise strategy, accountable domain ownership, legal or contractual obligations, and validated operational evidence appropriate to its subject
- Cross-artifact architectural lineage is recorded in the Traceability section and MUST NOT be interpreted as a runtime dependency graph

## 11. Traceability

- ADR-GLB-012 AI/Knowledge/Product separation
- ADR-GLB-013 Work/Workflow/Job/Schedule boundaries
- PAD-PLT-006 Integration
- PAD-PLT-008 AI
- PAD-PLT-015 Knowledge & Retrieval
- STD-GLB-011 Background Job Execution
- ADR-GLB-003 Transactional Outbox
- STD-GLB-004 Event-Driven Architecture & Messaging
