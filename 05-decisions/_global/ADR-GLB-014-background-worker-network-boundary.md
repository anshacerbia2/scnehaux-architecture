---
doc_meta:
  id: ADR-GLB-014
  title: ADR-GLB-014 Minimize Inbound Network Surface for Background Workers
  adr_type: foundational
  status: accepted
  created: 2026-08-23
  created_date: 2026-08-23
  created_by: Architecture Authority
  governed_by:
    - EAD-005
    - EAD-006
---

# ADR-GLB-014: Minimize Inbound Network Surface for Background Workers

## 1. Title

Minimize inbound network surface for background Worker runtimes without confusing execution topology with application ingress.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                                   | Approver               |
| :--------- | :------- | :----------- | :-------------------------------------------------------------------------- | :--------------------- |
| 2026-08-23 | accepted | foundational | Architecture Authority, Security, Platform Engineering, Product Engineering | Architecture Authority |

## 3. Context

Workers exist throughout Products and Platforms: Kafka consumers, outbox relays, Scheduler due claimers, Notification delivery workers, reconciliation processors, indexing workers, and Product-owned background execution.

A pure Worker normally receives business work from an asynchronous or durable source rather than from an inbound business API. Exposing a public or business HTTP listener on such a process creates additional attack surface, routing, authorization, rate-limiting, patching, observability, and operational obligations unrelated to its execution contract.

The opposite extreme is also incorrect: operational runtimes may legitimately need liveness, readiness, startup, metrics, or tightly controlled diagnostic endpoints. A deployable may also intentionally contain both API and Worker roles.

## 4. Decision Drivers

- Zero Trust and least-exposed network surface
- Workers are often unattended and run with privileged workload authority
- Background execution is normally initiated from broker/database/schedule state rather than user requests
- Health and telemetry must remain operationally viable
- API and Worker components may coexist in one deployable when decomposition is not justified
- Provider callbacks require authenticated ingress but should terminate at an ingress/API adapter rather than at the execution Worker
- Security rules must not force microservice decomposition for topology purity

## 5. Decision

Scnehaux adopts **no business ingress by default** for pure background Worker runtimes.

A pure Worker:

- MUST NOT expose a public or Product-facing business API
- MUST NOT require inbound network reachability merely to receive its normal work when the work source is a broker, queue, database claim, schedule occurrence, or equivalent pull/subscription mechanism
- MUST execute under attributable workload identity
- MUST use outbound access only to explicitly required dependencies under least privilege

Operational listeners MAY exist for liveness/readiness/startup probes, metrics, and authenticated internal diagnostics/administration when required. They are not business contracts and must remain internal, access controlled, network-policy restricted, observable, and excluded from public ingress.

A system MAY deploy API and Worker components together. The API role may expose governed business ingress; that does not make the Worker role an ingress surface and does not require splitting them into separate deployables.

External callbacks/webhooks terminate at a dedicated authenticated ingress/API adapter. That adapter may persist/enqueue work for a Worker.

## 6. Consequences

### Positive

- lower avoidable attack surface
- clearer distinction between business API contracts and background execution
- simpler network policy for pure Workers
- fewer unnecessary authentication/rate-limit/routing surfaces
- API + Worker modular monoliths remain valid when operationally simpler

### Negative

- direct ad-hoc HTTP triggering of Workers is prohibited
- support tooling may need a control API, broker command, database operation, or authenticated internal admin path
- mixed-role deployables require documentation that distinguishes API ingress from Worker execution

### Operational

- Kubernetes probes/metrics remain allowed but internal
- service mesh/network policy should default-deny Worker inbound traffic except explicitly declared operational ports
- observability inventories distinguish business ingress from operational listeners

## 7. Compliance Impact

- Governed by EAD-005 Enterprise Platform Architecture and EAD-006 Enterprise Security Architecture
- Operationalized by STD-GLB-012 Background Worker Network Exposure
- Background Job implementations also conform to STD-GLB-011
- System SADs document any inbound listener on a Worker-bearing deployable and classify it as business or operational

## 8. Alternatives Considered

### Alternative A — Workers may expose business HTTP APIs by default

Rejected because it creates unnecessary attack surface and duplicate application ingress semantics.

### Alternative B — Workers must literally open zero ports

Rejected because health, readiness, metrics, and controlled diagnostics are legitimate operational needs, and some deployables intentionally contain both API and Worker roles.

### Alternative C — Every API and Worker role must be a separate deployable

Rejected because it forces microservice decomposition without evidence and increases deployment/operational complexity.

### Alternative D — Provider callbacks terminate directly on delivery Workers

Rejected because callback authentication, rate limiting, parsing, and ingress hardening are explicit adapter concerns and should not widen the Worker execution surface.
