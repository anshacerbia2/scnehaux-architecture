---
doc_meta:
  id: ADR-GLB-012
  title: ADR-GLB-012 Separate Product, Knowledge, and AI Execution Authority
  adr_type: foundational
  status: accepted
  created: 2026-08-23
  created_date: 2026-08-23
  created_by: Architecture Authority
  governed_by:
    - EAD-001
    - EAD-003
    - EAD-005
    - EAD-006
---

# ADR-GLB-012: Separate Product, Knowledge, and AI Execution Authority

## 1. Title

Separate Product business authority, governed Knowledge & Retrieval, and AI model/agent execution into distinct bounded capabilities.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                                           | Approver               |
| :--------- | :------- | :----------- | :---------------------------------------------------------------------------------- | :--------------------- |
| 2026-08-23 | accepted | foundational | Architecture Authority, Product Architecture, Data/Knowledge, AI Platform, Security | Architecture Authority |

## 3. Context

Scnehaux will support vertical AI Products and Product features across Travel Operations, HCM, future ERP, knowledge capture, copilots, workflow assistance, and operational decision support.

The enterprise must preserve differentiation in proprietary knowledge, domain workflow, Product context, tools/actions, authorization, human expertise, evaluation/feedback, and Product experience while remaining able to change model/provider implementations.

A single "AI Platform" owning inference, RAG, Knowledge Graph truth, ontology, Product prompts, agent workflow, and Product business decisions would create a god-platform. It would couple knowledge lifecycle to model-provider lifecycle and make Product authority ambiguous.

Conversely, making every Product directly integrate provider SDKs, vector stores, graph stores, and model credentials would duplicate security, cost, evaluation, portability, and observability concerns.

Graph-based retrieval is strategically important for relationship-rich enterprise knowledge, but graph representation is not appropriate for every query and must not silently become the master database for Product facts.

Provider access also occurs through different authority modes. Human enterprise SSO/seat access is an interactive user capability; API/workload credentials and workload identity are unattended machine authority. Treating them as one credential type destroys attribution and lifecycle boundaries.

## 4. Decision Drivers

- Vertical AI Products must retain Product/domain authority
- Enterprise knowledge must be reusable across AI, search, humans, analytics, and rules
- Knowledge provenance and source authority must survive model/provider changes
- Graph RAG is first-class but must coexist with lexical, vector, metadata, and hybrid retrieval
- Model/provider portability must be governed by evaluation rather than assumed equivalence
- Provider credentials and access modes require centralized policy, usage, cost, and security controls
- Agents/tools must use bounded delegated authority and Product-side authorization
- HCM, Travel, future ERP, and other Products must be able to share AI/Knowledge substrate without sharing Product databases

## 5. Decision

Scnehaux SHALL maintain three distinct authority boundaries.

### 5.1 Product Authority

Business Products SHALL own:

- Product business state and invariants
- Product workflow meaning and final business outcome
- Product authorization at the protected resource
- domain prompt/skill semantics where those artifacts encode Product meaning
- Product tools and their side effects
- acceptance of AI-generated/proposed outputs into Product truth

### 5.2 Knowledge & Retrieval Authority

The Knowledge & Retrieval Platform SHALL own:

- governed Knowledge Asset lifecycle
- source/provenance/version/effective metadata
- Enterprise Core Ontology mechanics and domain extension lifecycle
- entity/relationship/claim representation
- Knowledge Graph representation
- lexical/vector/metadata/graph index lifecycle
- retrieval planning/ranking
- authorization-aware retrieval
- citation/evidence assembly

Knowledge representations SHALL preserve source authority. A graph, embedding, index, or Knowledge Claim SHALL NOT silently replace Product/external transactional authority.

Graph is a first-class retrieval representation but SHALL NOT be the only supported retrieval mode.

### 5.3 AI Execution Authority

The AI Enablement Platform SHALL own:

- Model & Provider Gateway
- Provider Access Profiles
- Model Catalog and Capability Profiles
- routing/policy
- inference runtime
- Agent Runtime
- tool registration/mediation and protocol adapters
- prompt/skill/AI-asset runtime lifecycle mechanics
- evaluation/release/canary/fallback
- runtime guardrail enforcement
- usage/quota/cost
- AI telemetry

The AI Platform SHALL NOT own enterprise Knowledge truth or Product business decisions.

### 5.4 Provider Access Profiles

Provider access SHALL distinguish at least:

- workload API credential
- cloud workload identity
- delegated user OAuth where supported
- enterprise SSO/seat-bound interactive access where supported
- local/self-hosted runtime

Human interactive SSO/session authority SHALL NOT be silently reused as unattended machine authority.

### 5.5 Governed Portability

Products SHALL consume stable AI capability profiles instead of depending on provider SDK payloads as Product contracts.

Provider/model substitution requires current evaluation evidence appropriate to the profile, including quality and safety and, where relevant, latency and cost.

### 5.6 Retrieval Security

Knowledge retrieval SHALL apply authorization before protected content is assembled into model context.

### 5.7 Agent and Tool Boundary

Agent Runtime is not Workflow. A Workflow task MAY invoke an Agent Run.

Tool protocols such as MCP MAY be supported as adapters. They do not become Product authorization authority. The tool-owning Product/Platform authorizes the requested business operation.

## 6. Consequences

### Positive

- Product authority remains explicit
- enterprise knowledge survives model/provider changes
- model/provider switching is governed rather than fictional
- graph, vector, lexical, and metadata retrieval can evolve independently
- provider credentials, AI cost, evaluation, and telemetry are reusable
- vertical AI Products can share substrate without becoming generic chat wrappers
- knowledge can be consumed by non-AI systems

### Negative

- more logical boundaries and contracts than a single AI service
- retrieval and AI latency must be managed across a platform boundary
- ontology/provenance governance requires dedicated ownership
- model fallback needs continuing evaluation investment
- tool authorization is intentionally duplicated as enforcement near each protected Product resource

### Operational

- PAD-PLT-008 is rebaselined around AI execution
- PAD-PLT-015 establishes Knowledge & Retrieval
- AI execution remains separated from Product and Knowledge authority
- ADR-GLB-015 further refines AI execution into separate Model & Inference and Agent Runtime Platform authorities; this ADR remains accepted at the macro authority boundary
- graph/vector/search technology selection remains a downstream SAD/ADR decision

## 7. Compliance Impact

- EAD-001, EAD-003, EAD-004, EAD-005, and EAD-006 are aligned to the new authority split
- PAD-PLT-008 and PAD-PLT-015 are the logical contracts
- no exception to an existing enterprise standard is required
- future provider/model/knowledge technology selection must comply with technology lifecycle governance

## 8. Alternatives Considered

### Alternative A — One AI Platform owns RAG, Knowledge Graph, agents, Product prompts, and business workflow

Rejected because it centralizes unrelated authority and makes model/provider execution the owner of enterprise knowledge.

### Alternative B — Every Product integrates providers and RAG independently

Rejected because security, credentials, routing, evaluation, cost, telemetry, and knowledge governance would be duplicated.

### Alternative C — Vector-only enterprise RAG

Rejected because relationship-rich and evidence-sensitive queries require other retrieval modes.

### Alternative D — Graph-only enterprise RAG

Rejected because many search/retrieval workloads are simpler, faster, or better served through lexical/vector/metadata paths.

### Alternative E — Model/provider switching is transparent configuration

Rejected because models differ semantically. Portability requires evaluation and controlled promotion.
