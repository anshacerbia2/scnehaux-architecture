---
doc_meta:
  id: ADR-GLB-015
  title: ADR-GLB-015 Separate Model & Inference from Agent Runtime
  adr_type: foundational
  status: accepted
  created: 2026-08-23
  created_date: 2026-08-23
  created_by: Architecture Authority
  governed_by: [EAD-001, EAD-003, EAD-005, EAD-006]
---

# ADR-GLB-015: Separate Model & Inference from Agent Runtime

## 1. Title

Separate bounded model/provider inference execution from durable stateful Agent Runtime execution.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                                               | Approver               |
| :--------- | :------- | :----------- | :-------------------------------------------------------------------------------------- | :--------------------- |
| 2026-08-23 | accepted | foundational | Architecture Authority, AI Platform, Knowledge Platform, Product Architecture, Security | Architecture Authority |

This ADR **refines ADR-GLB-012**. ADR-GLB-012 remains accepted for Product/Knowledge/AI macro separation; this ADR decomposes AI execution into two Platform authorities.

## 3. Context

The prior AI Enablement boundary centralized provider access, model abstraction, Agent execution, Tool mediation, evaluation, cost, and telemetry while correctly excluding Product and Knowledge authority.

Zero-based review found two different computational/runtime models inside that boundary:

- **bounded inference**: provider/model/profile/routing/latency/quality/cost
- **durable Agent execution**: Agent Definition/Run/Turn, Context, Memory, Tool side effects, waits, budgets, delegation, recovery

Combining them couples latency-oriented provider routing to stateful long-running execution and makes simple inference appear to require Agent machinery.

## 4. Decision Drivers

- distinct primary semantics and state models
- different durability/failure/security/scaling economics
- Tool-side-effect and delegated-authority concerns belong to Agent Runtime
- simple inference must remain possible without Agent Runtime
- providers/frameworks remain replaceable
- Product/Workflow/Knowledge/Tool/human-decision authority remains outside both

## 5. Decision

Scnehaux SHALL treat **AI Enablement as a capability family**, realized by two separate Platform Products.

### 5.1 Model & Inference Platform

PAD-PLT-008 owns provider/model registry/access, Capability Profiles, bounded inference, routing, model evaluation/release, fallback, model guardrails, usage/quota/cost, provider health, inference telemetry.

It SHALL NOT own durable Agent Run/Memory/Tool Binding/delegation/control-loop authority.

Products MAY consume it directly.

### 5.2 Agent Runtime Platform

PAD-PLT-016 owns Agent Definition runtime lifecycle, Agent Run/Turn, Harness, Context Assembly/Snapshot, Run/Session Memory mechanics, Tool Binding/mediation, Skill Runtime, budgets/stops, parent/child/delegation/handoff/agent-as-tool, waits/resume, runtime evaluation, trace/telemetry.

It consumes Model & Inference and Knowledge & Retrieval.

### 5.3 Agent Runtime Is Not Product or Workflow

A Vertical AI Product may use zero, one, or many Agents. Product owns domain workflow/meaning/Tools/authorization/acceptance/outcome. Workflow may invoke Agent Runs but retains business-process authority.

### 5.4 Harness Is Not a Separate Platform

Harness is internal Agent Runtime machinery.

### 5.5 Context Assembly Does Not Own Sources

Agent Runtime composes context but Identity/Organization/Product/Knowledge/Tool sources retain authority.

### 5.6 Agent Memory Is Not Knowledge Authority

Run/Session Memory is execution state. Reusable factual knowledge requires governed Knowledge publication. Product preferences/master data remain Product authority.

### 5.7 Tool Binding Is Not Tool Authority

Agent Runtime owns Agent-side Binding/mediation/correlation. Tool owner owns semantics/final authorization/invariants/idempotency/reconciliation/side effects. Unknown side-effect outcome must be reconciled before unsafe retry.

MCP/native Tool protocols remain adapters, not authorization authority.

### 5.8 Multi-Agent Is Composition

Parent/child, delegation, handoff, agent-as-tool are Agent Runtime composition semantics, not a separate Multi-Agent Platform.

### 5.9 Human Wait State Is Not Approval Authority

Agent Runtime may wait/suspend/resume, but Product/Workflow/Work Management owns the human business decision.

### 5.10 Isolated Execution Remains Separately Qualifiable

Code/browser/computer/shell/filesystem execution may require a separate Engineering & Runtime capability. Agent Runtime consumes it through Tool contracts rather than automatically owning sandbox authority.

## 6. Consequences

### Positive

- simple inference avoids Agent dependency
- provider routing and durable Agent lifecycle evolve independently
- Agent recovery/side-effect/delegation controls become explicit
- provider and agent-framework replacement boundaries improve
- Product/Workflow/Knowledge/Tool authority stays clear

### Negative

- one additional Platform boundary/contract
- agentic flows add one platform hop
- tracing spans Product/Agent/Knowledge/Inference/Tools
- separate capacity/reliability models may be required
- evaluation becomes layered: model, Agent runtime, Product domain

### Operational

- PAD-PLT-008 rebaselined as Model & Inference
- PAD-PLT-016 establishes Agent Runtime
- SAD-011 remains chartered for Model & Inference
- SAD-020 chartered for Agent Runtime
- no provider/framework/state-engine/memory-store/sandbox selected

## 7. Compliance Impact

- EAD-001 splits authority without changing five roots
- EAD-002 splits system roles
- EAD-003 splits Inference Run from Agent Run/context/memory state
- EAD-005 recognizes independent runtime economics
- EAD-006 existing Agent/Tool security controls apply
- ADR-GLB-012 remains accepted and is refined here

## 8. Alternatives Considered

### Alternative A — Keep one AI Enablement Platform

Rejected because distinct runtime/state/security/scaling/failure models remain coupled.

### Alternative B — Product-local Agent harness everywhere

Rejected because durable execution, Tool mediation, context/memory, delegation, evaluation, tracing, recovery would repeat.

### Alternative C — Agent Runtime mandatory for every AI call

Rejected because bounded inference does not require Agent semantics and a universal hop adds latency/blast radius/cognitive load.

### Alternative D — Separate Harness/Memory/Skill/MCP/Multi-Agent Platforms now

Rejected because they are cohesive Agent Runtime capabilities/protocols without independent authority/economics sufficient today.

### Alternative E — Agent Runtime owns Tool/Product effects

Rejected because protected-resource authority remains with Tool/Product owner.

### Alternative F — Agent Runtime owns enterprise long-term memory truth

Rejected because reusable factual knowledge requires Knowledge governance.
