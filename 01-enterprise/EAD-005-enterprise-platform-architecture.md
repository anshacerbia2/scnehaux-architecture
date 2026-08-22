---
doc_meta:
  id: EAD-005
  title: Enterprise Platform Architecture
  owner: Architecture Authority
  version: 2.1.0
  status: approved
  classification: internal
  governed_by: [GDC-006]
  review_cycle_days: 180
  created_date: 2026-08-06
  last_reviewed: 2026-08-23
---

# Enterprise Platform Architecture

## 1. Purpose

Define how reusable Platform capabilities are grouped, qualified, product-managed, realized, operated, and evolved across the **Scnehaux Enterprise Cloud**.

**Decision question:** _Which reusable responsibilities belong in the Platform Plane, when should they become shared Platform Products, and what platform/runtime posture minimizes total system complexity?_

## 2. Scope

**In scope**

- Five Platform Plane concern families
- Platform qualification and Platform-as-a-Product doctrine
- Workspace Experience, Work Management, Rules, Knowledge & Retrieval, AI, Artifact, Scheduling, and Background Job capability posture
- Runtime/workload profiles
- Technology portfolio at macro level
- Reliability, observability, resilience, capacity, and FinOps direction

**Out of scope**

- Product-specific business semantics
- System/container topology
- Concrete graph/vector/model/provider technology choice
- Exact framework/library versions
- Product-specific SLO/runbook
- Detailed security policy

## 3. Enterprise Context

Platform architecture exists to reduce total enterprise complexity and repeated friction while preserving clear authority.

The enterprise deliberately avoids both extremes:

```text
top-down platform catalog without demand
and
duplicate foundational capability everywhere until extraction hurts
```

Platform discovery is dual-directional:

```text
Enterprise structural / constitutional need
              +
Product friction / repeated machinery / runtime evidence
              ↓
Capability candidate
              ↓
Authority boundary
              ↓
Platform qualification
              ↓
Platform Product
              ↓
Adoption / runtime evidence / feedback
              ↺
```

## 4. Architectural Drivers & Lessons

### 4.1 Drivers

| ID | Driver | Platform Consequence |
| :-- | :-- | :-- |
| D1 | HCM, Travel, future ERP, and vertical AI Products need shared foundations | Cross-product capabilities have stable logical contracts |
| D2 | Models/providers change faster than Product semantics | AI provider abstraction and evaluation are first-class |
| D3 | Enterprise knowledge is strategic and cross-product | Knowledge & Retrieval is separate from AI execution |
| D4 | Human operational work spans Products | Work Management and Workspace Experience are explicit capabilities |
| D5 | Durable background execution recurs everywhere | Background Job Execution receives a standard/paved road before an independent Platform Product |
| D6 | Shared services add dependency and blast radius | Platformization must lower total system complexity |

### 4.2 Lessons Incorporated

| Lesson | Platform Response |
| :-- | :-- |
| Platform root was mistaken for a Platform Product | Root, capability, Platform Product, system, deployable, and team remain distinct |
| Mechanism vs meaning was framed too absolutely | Platform owns its own bounded semantics; Product owns Product semantics/outcomes |
| Platform discovery looked waterfall/top-down | Structural need and bottom-up evidence converge |
| Cognitive load was secondary | DevEx/adoption are first-class Platform Product metrics |
| Canonical authority overlap was justified as resilience | Projections/replicas may overlap; canonical authority remains singular |
| AI gateway threatened to become a god-platform | Knowledge, AI execution, Product workflow, and Product authorization remain separate |

## 5. Architecture Model

### 5.1 Platform Topology

```mermaid
graph TB
    CONSUMERS[Business Products / Platform Consumers / Engineering Teams]

    subgraph FC[Foundation & Control]
        IAM[Identity & Access]
        ORG[Organization & Tenancy]
        TRUST[Application & Service Trust]
        POLICY[Security Policy & Authorization]
        ENT[Subscription & Entitlement]
        BILL[Usage Metering & Billing]
        CONFIG[Configuration & Variation]
        AUDIT[Audit & Evidence]
        SECRETS[Trust Services]
    end

    subgraph BEE[Business Execution & Enablement]
        WORK[Work Management]
        FLOW[Workflow & Orchestration]
        RULES[Rules & Decisioning]
        APPROVAL[Approval & Review capability]
        SLA[SLA & Escalation capability]
        ART[Artifact & Document]
        NOTIF[Notification]
        INT[Integration Enablement]
    end

    subgraph DKI[Data Knowledge & Intelligence]
        DATA[Data Foundation]
        KNOW[Knowledge & Retrieval]
        AI[AI Enablement]
        ANALYTICS[Analytics]
        OI[Operational Intelligence]
    end

    subgraph EI[Experience & Interaction]
        UI[UI Platform]
        WX[Workspace Experience]
        CHANNEL[Channel Foundations]
        ACCESS[Accessibility & Localization]
    end

    subgraph ER[Engineering & Runtime]
        DEV[Developer Platform]
        CATALOG[Software Catalog]
        DELIVERY[Source Build Delivery]
        INFRA[Infrastructure Automation]
        RUNTIME[Application Runtime]
        JOB[Background Job & Task Execution]
        SCHED[Temporal Scheduling & Trigger Dispatch]
        CONNECT[API & Service Connectivity]
        MSG[Event & Messaging]
        OBS[Observability]
        REL[Reliability & Resilience]
        TEST[Testing & Quality]
    end

    CONSUMERS --> FC
    CONSUMERS --> BEE
    CONSUMERS --> DKI
    CONSUMERS --> EI
    CONSUMERS --> ER
```

The five roots are stable concern families, not mandatory deployables.

### 5.2 Platform Doctrine

```text
Platform Plane Root
!= Capability
!= Shared Platform Product
!= System
!= Deployable
!= Team
```

A Platform owns meaningful semantics within its own bounded capability. Consuming Products retain their authoritative business semantics and outcomes.

### 5.3 Three Paths to Platformization

1. **Constitutional / Authority Driven**
   - Identity
   - Organization
   - Trust
   - Audit/Evidence

2. **Friction / Reuse Driven**
   - Work Management
   - Workflow
   - Rules
   - Artifact
   - Notification
   - Integration
   - Knowledge & Retrieval

3. **Runtime Economics Driven**
   - Event & Messaging
   - Observability
   - CI/CD
   - Runtime
   - Scheduling
   - Background Job execution patterns

A capability may have multiple drivers.

### 5.4 Platform Qualification

```text
Shared Platform Justification
=
Enterprise Responsibility
+ Authority Need
+ Consumer Friction
+ Reuse Evidence
+ Lifecycle Independence
+ Operational Economics
+ Risk Reduction

-

Shared Dependency Cost
- Cognitive Load Introduced
- Platform Operating Cost
- Blast Radius
- Migration Cost
```

A capability becomes shared only when the total system becomes simpler/safer to operate.

### 5.5 Workspace Experience

Workspace Experience is a reusable **human digital work environment**, not the Organization-owned Workspace operating context.

It may provide:

- application shell and navigation
- Product composition and deep-linking
- active context presentation/switching through Organization contracts
- My Work and work surfaces through Work Management contracts
- notification/search/knowledge/copilot composition slots
- shared chrome and experience policies

It does not own Organization/Tenant/Workspace/Membership facts.

### 5.6 Work Management

Work Management owns reusable work-management semantics such as Work Item, Case, Queue, Assignment, Claim, Priority, generic review state, and work history.

Workflow owns durable multi-step process position/coordination. Product owns what the work means and the final business outcome.

### 5.7 Rules & Decisioning

Rules & Decisioning owns reusable rule-definition/evaluation/version/testing/explanation lifecycle. Product domains own domain rule meaning and resulting business decision.

### 5.8 Knowledge & Retrieval

Knowledge & Retrieval owns governed Knowledge Asset lifecycle, provenance, ontology mechanics, graph/vector/lexical/metadata index lifecycle, authorized retrieval, and evidence/citation assembly.

Graph is first-class but not mandatory for every query. The Platform supports lexical, vector, metadata, graph, and hybrid retrieval selected by profile and evidence.

### 5.9 AI Enablement

AI Enablement provides:

- Model & Provider Gateway
- Provider Access Profiles
- Model Catalog and Capability Profiles
- routing and policy
- inference runtime
- agent runtime
- tool/MCP interoperability
- prompt/skill/AI-asset runtime lifecycle
- evaluation and release
- guardrail enforcement
- usage/quota/cost
- AI telemetry

AI Enablement does not own Product workflow, Product business authorization, Product prompt semantics, or enterprise Knowledge authority.

#### Provider Access Profiles

Supported conceptual modes include:

- workload API credential
- cloud workload identity
- delegated user OAuth where supported
- enterprise SSO/seat-bound interactive access where supported
- local/self-hosted runtime

Interactive human access and machine workload access are different authority classes.

#### Governed Portability

Provider/model switching is based on capability compatibility plus evaluation evidence. Semantic equivalence is never assumed.

### 5.10 Artifact & Document

Artifact is the broader reusable abstraction covering file/document/image/video/audio/spreadsheet/generated outputs.

Artifact Platform owns content/version/checksum/provenance/lifecycle/conversion/rendering/scan/archive mechanics. Product owns business meaning.

### 5.11 Background Job & Task Execution

Background Job Execution is an **Engineering & Runtime capability**, not yet an independent Platform Product.

The enterprise first standardizes:

- Job identity
- durable acceptance when required
- attempt/lease/claim
- retry/backoff
- timeout/cancellation
- progress
- dead-letter/replay
- bounded concurrency
- tenant/workload context
- telemetry

Product/Platform handler code remains with the owner. Scheduling owns future time. Workflow owns multi-step process state.

### 5.12 Runtime Strategy

Enterprise workload profiles include:

- request/response
- background job/worker
- scheduled/batch
- durable workflow
- integration connector
- event/stream processing
- data/knowledge indexing
- retrieval
- AI inference
- agent execution
- evaluation batch
- sandboxed tool execution
- frontend/static
- build-time library/package

### 5.13 Technology Portfolio

| Concern | Direction |
| :-- | :-- |
| Transactional/control server | Go as primary default where fit |
| Web/BFF | TypeScript |
| Data/AI/scientific workloads | Python where ecosystem leverage justifies |
| Adopted vendor kernels | Vendor runtime scoped to adopted product |
| Transactional persistence | Managed relational, PostgreSQL-compatible preferred |
| Object/artifact storage | Managed object storage |
| Messaging | Managed broker/stream |
| Cryptographic custody | Managed KMS/HSM and secret management |
| Telemetry | OpenTelemetry-compatible |
| Infrastructure | Declarative/version-controlled |
| Graph/vector/search/model provider | **Not selected at EAD level; selected downstream based on PAD/SAD evidence** |

### 5.14 Reliability Classes

| Class | Meaning | Target Availability Direction | Default RTO | Default RPO |
| :-- | :-- | :-- | :-- | :-- |
| C0 | Trust / safety critical | >=99.99% | <=15m | <=1m |
| C1 | Mission-critical operations | >=99.95% | <=1h | <=15m |
| C2 | Business important | >=99.9% | <=4h | <=1h |
| C3 | Assistive / best effort | Consumer-journey defined | <=24h | By data class |

AI Products may require a higher reliability profile than an assistive copilot. Criticality is declared by consumer journey, not “AI” as a blanket label.

### 5.15 Internal Developer Platform Strategy

The Internal Developer Platform is a Platform Product for engineering teams. It provides discoverable, measured paved roads for:

- software/catalog ownership
- project/service templates
- build/test/security/delivery
- environment/configuration provisioning
- API/event/data/AI contract discovery
- observability/readiness metadata
- background Job reference patterns
- documentation/support

Teams may leave paved roads through governed decisions. Platform success is measured through adoption, lead time, failure rate, support burden, cognitive load, and consumer satisfaction.

### 5.16 Operational Model

Every active Platform Product declares:

- accountable owner and consumers
- reliability/service profile and current SLO
- capacity/backpressure and Tenant isolation
- incident/on-call/support model appropriate to criticality
- adoption and consumer-friction metrics
- unit cost/FinOps attribution where meaningful
- recovery/reconciliation evidence
- lifecycle/deprecation/exit conditions

A shared Platform that persistently increases total-system complexity more than the value it creates is refined, split, merged, retired, or returned local.

## 6. Principles & Rules

### 6.1 Platform Is a Product
- **Fitness function:** every approved shared Platform PAD identifies owner, consumers, NFR, support/lifecycle, and adoption outcome

### 6.2 Shared Capability Must Lower Total System Complexity
- **Fitness function:** new independent Platform PAD includes reuse/authority/economics justification and negative externalities

### 6.3 Platform Owns Platform Semantics, Product Owns Product Semantics
- **Fitness function:** platform PAD review finds zero Product-specific authoritative outcome ownership

### 6.4 Distinct Primary Concerns
- **Fitness function:** every critical fact and primary responsibility has one accountable authority

### 6.5 Platform Discovery Is Evolutionary
- **Fitness function:** Platform roadmap includes consumer/runtime feedback and explicit refine/retire path

### 6.6 Simplest Sufficient Runtime
- **Fitness function:** independent distributed runtime choices carry SAD/ADR evidence

### 6.7 Background Job Is Not a Universal Worker Platform
- **Fitness function:** background-job standard prohibits arbitrary central Product code ownership

### 6.8 AI and Knowledge Remain Separate Authorities
- **Fitness function:** AI PAD does not own Knowledge Asset/Graph truth; Knowledge PAD does not own model execution

### 6.9 Human SSO Is Not Machine Authority
- **Fitness function:** provider access profile inventory distinguishes interactive and workload identities

### 6.10 Model Portability Is Evaluated
- **Fitness function:** model/provider promotions resolve to evaluation/release evidence

## 7. Alternatives Considered

| Alternative | Why Rejected |
| :-- | :-- |
| Platformize every reusable idea | Creates support and dependency cost without leverage |
| Keep every repeated mechanism Product-local | Multiplies correctness/operational burden |
| Central Worker Platform now | Prematurely centralizes arbitrary Product execution |
| AI Platform owns graph/RAG truth | Conflates knowledge authority with execution |
| Graph-only retrieval | Makes one representation mandatory |
| Provider-specific Product integration | Prevents governed portability and multiplies security/cost controls |

## 8. Single Points of Failure & Graceful Degradation

| Capability | Blast Radius | Posture |
| :-- | :-- | :-- |
| Identity / Organization | Trust/context changes | Local artifacts/projections where permitted |
| Event & Messaging | Async ecosystem | Durable producers/replay |
| Scheduling | Future work | Durable state/misfire |
| Workspace Experience | Shared work surface | Direct Product entry where required |
| Knowledge & Retrieval | Search/RAG | Explicit degraded mode |
| AI Enablement | AI features | Evaluated provider fallback/non-AI fallback according to Product profile |
| Shared Work/Workflow | Operational coordination | Durable state and bounded isolation |

## 9. Ownership

- Architecture Authority owns Platform Plane taxonomy and qualification doctrine
- Platform Product owners own approved PAD capability outcomes
- Product teams own Product business semantics
- Engineering Platform owns common runtime/paved-road capabilities
- Governance authorities define non-negotiable controls and evidence requirements

## 10. Dependencies

- EAD-001 capability map
- EAD-002 landscape
- EAD-003 data/knowledge authority
- EAD-004 integration
- EAD-006 security
- EAD-007 governance/assurance

## 11. Traceability

- PAD-PLT-012 Workspace Experience
- PAD-PLT-013 Work Management
- PAD-PLT-014 Rules & Decisioning
- PAD-PLT-015 Knowledge & Retrieval
- PAD-PLT-008 AI rebaseline
- PAD-PLT-009 Artifact & Document rebaseline
- ADR-GLB-012 and ADR-GLB-013
- STD-GLB-011 Background Job Execution
