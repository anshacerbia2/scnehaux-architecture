---
doc_meta:
  id: ADR-GLB-010
  title: Application Mechanics Stay In-Process; Network Mechanics Move to Infrastructure
  adr_type: foundational
  status: proposed
  created: 2026-08-12
  created_date: 2026-08-12
  created_by: Architecture Authority
  governed_by: [GDC-000, EAD-002, EAD-004, EAD-005]
---

# ADR-GLB-010: Application Mechanics Stay In-Process; Network Mechanics Move to Infrastructure

## 1. Title

Placement of Cross-Cutting Mechanics: In-Process Application Concerns, Generated Contracts, and Infrastructure-Owned Network Concerns

## 2. Status

| Date | Status | ADR Type | Reviewers | Approver |
| :-- | :-- | :-- | :-- | :-- |
| 2026-08-12 | proposed | foundational | Architecture, Platform, Security, Engineering | Architecture Authority — pending |

## 3. Context

Cross-cutting mechanics — transactional outbox, idempotency, tenant-context propagation, retries, circuit breaking, mutual TLS, and telemetry — need a consistent home across Scnehaux systems. Two placements were proposed.

**A shared foundation library.** Every service imports one versioned package that implements the mechanics. The objections to this are real and were raised correctly:

- it binds every consumer to one language;
- a version conflict between the library's dependencies and a consumer's dependencies breaks the build;
- a defect in the library requires recompiling and redeploying every consumer, which recouples the release trains that independent deployability exists to separate.

**A sidecar runtime** such as Dapr, or a service mesh such as Envoy under Istio. The application calls `localhost` over HTTP or gRPC and the sidecar performs the mechanics. The claimed benefits are genuine polyglot support, instrumentation without application code, and central patching without touching consumers.

The choice is frequently framed as old versus modern. That framing does not survive examination: every large cloud-native organisation still ships shared libraries for protocol clients, telemetry SDKs, and database drivers, and several that adopted sidecars for application concerns later returned to in-process implementations on latency-critical paths. The useful question is not which era a mechanism belongs to. It is **which concerns can physically leave the process, and which cannot**.

Three facts about the Scnehaux estate constrain the answer:

1. **Transactional atomicity cannot cross a process boundary.** The transactional outbox pattern mandated by ADR-GLB-003 requires the event record to commit in the same database transaction as the state change it describes. An application that writes state to its own database and then calls a sidecar to publish has performed a dual write, which is the exact failure the pattern removes. A sidecar cannot enlist in the application's database transaction.

2. **Sidecar outbox support requires surrendering the data model.** Runtimes that do offer a transactional outbox achieve it by owning both the state write and the publication through their own state abstraction, which is key-value oriented. The Scnehaux control-plane authority stores depend on relational semantics that abstraction does not express: forced row-level security with a non-owner runtime role, composite foreign keys enforcing cross-entity invariants, partial unique indexes, optimistic concurrency columns, and per-module schema ownership with independent migrations.

3. **The current estate is single-language and has no orchestrator.** The control plane is two Go deployables operated by one team, and EAD-005 §6.2 requires documented evidence before adopting Kubernetes or a service mesh. Sidecar injection realistically presumes an orchestrator. Adopting it now purchases polyglot capability that has no consumer, at the cost of a cluster, a mesh, and the operational competence for both.

## 4. Decision Drivers

- Preserve atomicity between state change and event emission.
- Preserve the relational semantics the authority stores depend on.
- Prevent a shared library from coupling release trains across services.
- Keep the simplest sufficient runtime until evidence justifies more.
- Retain a credible path to polyglot without paying its infrastructure cost today.
- Keep privileged credentials confined to the process that requires them.
- Ensure business-journey observability, which network telemetry cannot supply.
- Make the future adoption of a mesh a decision with stated conditions rather than a matter of preference.

## 5. Decision

Cross-cutting mechanics are placed by **concern**, not by a single mechanism. Four placements are established and are mutually exclusive.

### 5.1 Contracts — Versioned Artifacts, Generated Per Language

Event schemas, API specifications, and the clients generated from them are versioned artifacts. They carry data shape and no behaviour.

- Contracts SHALL be versioned independently of any consumer.
- Language bindings SHALL be generated from the contract, not hand-written per service.
- A contract change SHALL follow the compatibility rules in ADR-GLB-006.

This is the placement that delivers genuine polyglot capability: a new language consumes the contract by generating a client, with no additional runtime.

### 5.2 Transactional Mechanics — In-Process

The transactional outbox write, idempotency-key claim, optimistic concurrency, and tenant-context binding for row-level security SHALL execute in the application process, inside the same database transaction as the state change.

- These mechanics SHALL NOT be delegated to a sidecar, an out-of-process runtime, or any component that cannot participate in the application's database transaction.
- Authority stores SHALL NOT be placed behind a state abstraction that removes the relational semantics declared by their SAD.
- Duplication of this logic across services is accepted where divergence would cost only maintenance. It is prohibited where divergence would alter a declared security or correctness invariant; §5.6 governs that case.

### 5.3 Network Mechanics — Infrastructure, When Triggered

Mutual TLS, connection-level retry, circuit breaking, L7 routing, and network-level telemetry are infrastructure concerns and are the legitimate domain of a service mesh or gateway.

Adoption of a service mesh or sidecar runtime for these concerns requires **all three** of the following to be true, evidenced rather than projected:

1. A production service exists in a language other than the current default, in operation rather than planned.
2. The estate already runs on an orchestrator, adopted for a reason independent of this decision.
3. Service count has reached a point where per-service network policy and certificate lifecycle cannot be managed by explicit configuration.

Until all three hold, these concerns are handled by explicit configuration at the ingress and by the platform substrate. Adoption when the conditions are met requires a replacement ADR recording the evidence.

### 5.4 Observability — Split by Signal

- Business-journey signals — journey success and failure, projection freshness, reconciliation age, revocation enforcement delay, tenant impact — SHALL be instrumented in-process through an OpenTelemetry-compatible SDK.
- Network signals — request rate, connection latency, transport errors — MAY be supplied by infrastructure where it exists.

Infrastructure cannot infer business meaning from traffic. A sidecar therefore supplements in-process instrumentation and does not replace it. Claims that a sidecar removes the need for an application telemetry dependency are rejected.

### 5.5 Prohibited Patterns

The following are prohibited by default and require a replacement ADR:

- A **mandatory shared runtime dependency upgraded in lockstep**, where one service's release is gated on another's adoption of a new version. Shared code that is independently versioned, pinned per consumer, and upgraded deliberately is permitted under §5.6.
- Delegating transactional mechanics to any out-of-process component.
- Replacing an authority store's relational access with a key-value state abstraction.
- Adopting a sidecar runtime or service mesh before the conditions in §5.3 hold.
- Treating a shared library and a sidecar as interchangeable placements for the same concern.

### 5.6 Extraction Threshold

A mechanic is extracted from duplicated in-process code into a shared, independently versioned package when **either** condition holds:

1. **Three independent consumers and a stable interface.** This is the default threshold, and it exists to prevent abstraction before the shape of the concern is known.
2. **Divergence between copies would alter a declared security or correctness invariant.** Where a duplicated mechanic carries a term in an invariant that another artifact declares, extraction is justified at the first pair of consumers, because duplication no longer costs maintenance — it costs the invariant.

The second condition is the operative one for propagation machinery. The outbox dispatcher's poll interval and claim behaviour are terms in the revocation enforcement delay that STD-IAM-001 §3.4 defines as `propagation_time + remaining_access_token_lifetime`. Two copies polling at different intervals produce two different enforcement intervals while both services report compliance, and no test inside either service detects the difference.

A shared package created under either condition MUST satisfy all of the following, or it becomes the coupling vector §5.5 prohibits:

- **No package contains a domain concept** — not as a type, a constant, or a field name. A domain type in a shared package is a back channel between authorities that communicate only through versioned contracts.
- **The internal dependency graph is declared and machine-asserted** against the package graph rather than against text, and an undeclared edge fails the build.
- **Consumers depend on a tagged version, never a branch**, and upgrade deliberately rather than by rebuild.
- **The package holds no state and is not deployed**, so it carries no SAD and introduces no runtime failure domain.

## 6. Consequences

### Positive

- Atomicity between state change and event emission is preserved by construction rather than by discipline.
- Authority stores retain the relational controls their security and correctness depend on.
- Release trains remain independent because no consumer is required to upgrade a shared dependency.
- Polyglot capability is available through generated contracts without an orchestrator, a mesh, or a second runtime per workload.
- Privileged credentials remain confined to the process that requires them, which a shared sidecar would widen.
- The mesh question has stated conditions and stops being re-argued each quarter.

### Negative

- Transactional mechanics are duplicated across services until the extraction threshold is met, and a defect found in one copy must be corrected in each.
- Retry, timeout, and circuit-breaking policy is expressed per service rather than centrally, and consistency depends on review.
- A future move to a mesh will require migrating network policy that currently lives in configuration.
- Teams must reason about where a concern belongs rather than applying one mechanism to everything.

### Operational

- Each service owns its own outbox table, dispatcher, and telemetry configuration.
- Contract generation is a build-pipeline responsibility and requires a published schema registry or repository location.
- Network policy and certificate lifecycle are managed explicitly until §5.3 is satisfied.
- Architecture review verifies placement of any new cross-cutting mechanic against this decision.

## 7. Compliance Impact

### Related Standards and Artifacts

- ADR-GLB-003 — Transactional Outbox, whose atomicity requirement this decision protects.
- ADR-GLB-006 — Event Versioning, which governs the contract artifacts in §5.1.
- ADR-GLB-008 — Go Project Structure and Layer Enforcement, whose machine-enforced import analysis is the mechanism that verifies the placement rules in §5.5.
- EAD-002 — relationship semantics and the prohibition on universal mediation hops.
- EAD-004 — integration patterns and contract ownership.
- EAD-005 — simplest sufficient runtime, technology portfolio, and observability requirements.
- STD-GLB-002 — database isolation controls that the §5.2 prohibition preserves.
- STD-GLB-003 — observability requirements satisfied by §5.4.

### Compliance Status

Proposed and not yet authoritative. On acceptance, no existing system requires modification: the current control-plane design already places transactional mechanics in-process and holds no service mesh.

### Required Waivers

None at proposal time. Adoption of a sidecar runtime or service mesh before the §5.3 conditions hold requires an exception ADR with expiry.

## 8. Alternatives Considered

### Alternative A — Enterprise Foundation Library

A single versioned package implementing outbox, idempotency, tracing, retries, and context propagation, adopted by every service.

**Benefits:** one implementation, consistent behaviour, correction applied once.

**Rejected because:** it binds consumers to one language, creates dependency conflicts between the library's requirements and the consumer's, and forces lockstep upgrades that recouple release trains. The concern raised against it was correct. Section 5.5 prohibits it explicitly and §5.6 defines the narrow conditions under which shared code is permitted instead.

### Alternative B — Sidecar Runtime for Application Mechanics

A per-workload runtime such as Dapr performing outbox, idempotency, state access, and publication on behalf of the application.

**Benefits:** language independence, central patching, uniform behaviour without application code.

**Rejected because:** the transactional outbox cannot be delegated across a process boundary without reintroducing the dual write it exists to prevent, and the sidecar implementations that do provide it require the application's state to be written through a key-value abstraction. The control-plane authority stores depend on forced row-level security, composite foreign keys, partial unique indexes, and optimistic concurrency, none of which survive that abstraction. Adoption would also require an orchestrator that EAD-005 §6.2 permits only on evidence, in exchange for polyglot capability that currently has no consumer.

### Alternative C — Service Mesh Immediately

Adopt Kubernetes and a mesh now so that network mechanics are centralised from the beginning.

**Rejected for the current phase because:** it inverts the driver. The estate is two deployables in one language operated by one team without an orchestrator, and EAD-005 records prior failure from treating orchestration as a maturity goal. The capability is retained as a conditional future decision in §5.3 rather than abandoned.

### Alternative D — No Enterprise Guidance

Allow each system to place cross-cutting mechanics as its team prefers.

**Rejected because:** placement of the outbox is a correctness property, not a preference. Without a stated rule, a service that publishes through an out-of-process component after committing state produces silent event loss that no test in that service detects.
