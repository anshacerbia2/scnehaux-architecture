---
doc_meta:
  id: ADR-GLB-010
  title: Application Mechanics Stay In-Process; Network Mechanics Move to Infrastructure
  adr_type: foundational
  status: accepted
  created: 2026-08-12
  created_date: 2026-08-12
  created_by: Architecture Authority
  governed_by: [GDC-000, EAD-002, EAD-004, EAD-005]
---

# ADR-GLB-010: Application Mechanics Stay In-Process; Network Mechanics Move to Infrastructure

## 1. Title

Placement of Cross-Cutting Mechanics: In-Process Application Concerns, Generated Contracts, and Infrastructure-Owned Network Concerns

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                     | Approver                         |
| :--------- | :------- | :----------- | :-------------------------------------------- | :------------------------------- |
| 2026-08-12 | proposed | foundational | Architecture, Platform, Security, Engineering | Architecture Authority — pending |
| 2026-10-20 | accepted | foundational | Architecture, Platform, Security, Engineering | Architecture Authority           |

**Accepted 2026-10-20 with amendments,** as the owner approved that day. Before acceptance, the
proposed text was corrected: §3 fact 3 described the estate as it no longer is, and cited two
statements `EAD-005` does not make; §7 gave `ADR-GLB-016` a title it does not have; §5.3 treated a
sidecar and a mesh as the same thing; §5.5 gains the rule that a resilience policy lives at one
layer; and §5.1 admits a hand-written client only when it is contract-tested against a published
specification. The code was checked against it on 2026-10-20: §5.2, §5.3, §5.5 and §5.6 hold, and
§5.1 does not yet (§7).

## 3. Context

Cross-cutting mechanics — transactional outbox, idempotency, tenant-context propagation, retries, circuit breaking, mutual TLS, and telemetry — need a consistent home across Scnehaux systems. Two placements were proposed.

**A shared foundation library.** Every service imports one versioned package that implements the mechanics. The objections to this are real and were raised correctly:

- it binds every consumer to one language;
- a version conflict between the library's dependencies and a consumer's dependencies breaks the build;
- a defect in the library requires recompiling and redeploying every consumer, which recouples the release trains that independent deployability exists to separate.

**A sidecar runtime** such as Dapr, or a service mesh such as Envoy under Istio. The application calls `localhost` over HTTP or gRPC and the sidecar performs the mechanics. The claimed benefits are genuine polyglot support, instrumentation without application code, and central patching without touching consumers.

The choice is frequently framed as old versus modern. That framing does not survive examination: every large cloud-native organisation still ships shared libraries for protocol clients, telemetry SDKs, and database drivers, and several that adopted sidecars for application concerns later returned to in-process implementations on latency-critical paths. The useful question is not which era a mechanism belongs to. It is **which concerns can physically leave the process, and which cannot**.

Three facts about the Scnehaux estate constrain the answer:

1. **Transactional atomicity cannot cross a process boundary.** The transactional outbox pattern mandated by ADR-GLB-016 requires the event record to commit in the same database transaction as the state change it describes. An application that writes state to its own database and then calls a sidecar to publish has performed a dual write, which is the exact failure the pattern removes. A sidecar cannot enlist in the application's database transaction.

2. **Sidecar outbox support requires surrendering the data model.** Runtimes that do offer a transactional outbox achieve it by owning both the state write and the publication through their own state abstraction, which is key-value oriented. The Scnehaux control-plane authority stores depend on relational semantics that abstraction does not express: forced row-level security with a non-owner runtime role, composite foreign keys enforcing cross-entity invariants, partial unique indexes, optimistic concurrency columns, and per-module schema ownership with independent migrations.

3. **Each placement has one default language, and the estate has no orchestrator (corrected 2026-10-20).** The authority services, identity-control and organization-control, are Go deployables, and they run every mechanic of §5.2. The identity kernel is Keycloak, a JVM product the estate adopts rather than writes (`ADR-IAM-001`). The two experience BFFs, identity-experience and organization-experience, are TypeScript on Node.js (`STD-GLB-FE-001`); they hold sessions and call the authority APIs, and own no authority state. So "the current default" language is defined per placement: Go for an authority service, TypeScript for a BFF. Everything runs on Docker Compose on a development server. `EAD-005 §6.6`, Simplest Sufficient Runtime, asks that "independent distributed runtime choices carry SAD/ADR evidence". Sidecar injection realistically presumes an orchestrator. Adopting it now purchases polyglot capability that has no consumer, at the cost of a cluster, a mesh, and the operational competence for both.

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
- Language bindings SHALL be generated from the contract, or, where they are hand-written, contract-tested in CI against the published specification (amended 2026-10-20). A hand-written client tested against nothing is prohibited.
- Each served API SHALL publish its specification (OpenAPI for HTTP) as a versioned artifact. Today identity-control and organization-control publish none, and the BFFs hand-write their clients, so §5.1 is not yet met. Event contracts already meet it, in foundation-platform's `contracts/events/registry.json`.
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

Condition 1 counts a service in a language other than the default **of its placement** (§3 fact 3). A BFF in TypeScript does not meet it, because TypeScript is the default for a BFF and a BFF runs no §5.2 mechanic.

A mesh need not use sidecars. Istio's ambient mode: "Since workload pods no longer require proxies running in sidecars in order to participate in the mesh, ambient mode is often informally referred to as “sidecar-less mesh”" [R3]. It still runs on Kubernetes, so condition 2 holds for it unchanged. A mesh handles network concerns for any language: "Envoy works with any application language" [R1]. It does not relieve the application: "applications must handle the failure or errors and take appropriate fallback actions" [R2].

### 5.4 Observability — Split by Signal

- Business-journey signals — journey success and failure, projection freshness, reconciliation age, revocation enforcement delay, tenant impact — SHALL be instrumented in-process through an OpenTelemetry-compatible SDK.
- Network signals — request rate, connection latency, transport errors — MAY be supplied by infrastructure where it exists.

Infrastructure cannot infer business meaning from traffic. A sidecar therefore supplements in-process instrumentation and does not replace it. Claims that a sidecar removes the need for an application telemetry dependency are rejected. Even trace stitching needs the application: "Applications must propagate this information in HTTP headers, so that when proxies send spans, the backend can join them together into a single trace" [R4].

### 5.5 Prohibited Patterns

The following are prohibited by default and require a replacement ADR:

- A **mandatory shared runtime dependency upgraded in lockstep**, where one service's release is gated on another's adoption of a new version. Shared code that is independently versioned, pinned per consumer, and upgraded deliberately is permitted under §5.6.
- Delegating transactional mechanics to any out-of-process component.
- Replacing an authority store's relational access with a key-value state abstraction.
- Adopting a sidecar runtime or service mesh before the conditions in §5.3 hold.
- Treating a shared library and a sidecar as interchangeable placements for the same concern.
- **A retry or timeout policy for one call at more than one layer (amended 2026-10-20).** A resilience policy lives at exactly one layer: in the application while §5.3 is not met, in the mesh after it, never both. Istio: "if you are also setting failure recovery policies in your application code you need to keep in mind that both work independently, and therefore might conflict" [R2]. Google SRE: "avoid amplifying retries by issuing retries at multiple levels: a single request at the highest layer may produce a number of attempts as large as the product of the number of attempts at each layer to the lowest layer" [R8].

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

- ADR-GLB-016 — Separate Transactional Publication from Durable Messaging Substrate Selection, whose transactional outbox this decision protects (title corrected 2026-10-20).
- ADR-GLB-006 — Event Versioning, which governs the contract artifacts in §5.1.
- ADR-GLB-008 — Go Project Structure and Layer Enforcement, whose machine-enforced import analysis is the mechanism that verifies the placement rules in §5.5.
- EAD-002 — relationship semantics and the prohibition on universal mediation hops.
- EAD-004 — integration patterns and contract ownership.
- EAD-005 — §6.6 Simplest Sufficient Runtime, the technology portfolio, and observability requirements.
- STD-GLB-002 — database isolation controls that the §5.2 prohibition preserves.
- STD-GLB-003 — observability requirements satisfied by §5.4.

### Compliance Status

Accepted 2026-10-20. Checked against the code that day:

- **§5.2 holds.** organization-control's outbox append runs inside the state transaction (`internal/authority/publication.go`), and identity-control claims an idempotency key inside it (`internal/firstcredential`).
- **§5.3 and §5.5 hold.** No mesh and no sidecar; the stacks run on Docker Compose.
- **§5.6 holds.** foundation-platform is tagged, consumers pin different versions, and its declared import graph is asserted in CI. It holds no domain package and is not deployed.
- **§5.1 does not hold yet.** identity-control and organization-control publish no API specification, and the two BFFs hand-write their clients. Each of the four repositories carries a dated ROADMAP item: the two services publish an OpenAPI document per served API as a versioned artifact, and the two BFFs generate their clients from it or contract-test the hand-written ones against it.

### Required Waivers

None at proposal time. Adoption of a sidecar runtime or service mesh before the §5.3 conditions hold requires an exception ADR with expiry.

## 8. Alternatives Considered

### Alternative A — Enterprise Foundation Library

A single versioned package implementing outbox, idempotency, tracing, retries, and context propagation, adopted by every service.

**Benefits:** one implementation, consistent behaviour, correction applied once.

**Rejected because:** it binds consumers to one language, creates dependency conflicts between the library's requirements and the consumer's, and forces lockstep upgrades that recouple release trains. Netflix's experience is a move away from one mandated runtime, not toward a mesh: Hystrix "is no longer in active development", and "our focus has shifted towards more adaptive implementations that react to an application’s real time performance rather than pre-configured settings … and to leverage open and active projects like resilience4j for new internal projects" [R7]. The concern raised against it was correct. Section 5.5 prohibits it explicitly and §5.6 defines the narrow conditions under which shared code is permitted instead.

### Alternative B — Sidecar Runtime for Application Mechanics

A per-workload runtime such as Dapr performing outbox, idempotency, state access, and publication on behalf of the application.

**Benefits:** language independence, central patching, uniform behaviour without application code.

**Rejected because:** the transactional outbox cannot be delegated across a process boundary without reintroducing the dual write it exists to prevent: "The command must atomically update the database and send messages in order to avoid data inconsistencies and bugs" [R6]. The sidecar implementations that do provide it require the application's state to be written through their abstraction: Dapr's "outbox feature requires a transactional state store supported by Dapr" [R5]. The control-plane authority stores depend on forced row-level security, composite foreign keys, partial unique indexes, and optimistic concurrency, none of which survive that abstraction. Adoption would also require an orchestrator, an independent distributed runtime choice that `EAD-005 §6.6` asks to carry SAD/ADR evidence, in exchange for polyglot capability that currently has no consumer.

### Alternative C — Service Mesh Immediately

Adopt Kubernetes and a mesh now so that network mechanics are centralised from the beginning.

**Rejected for the current phase because:** it inverts the driver. The estate has no orchestrator, its authority services are in one language, and `EAD-005 §6.6` asks that a distributed runtime choice carry evidence (§3 fact 3, corrected 2026-10-20). A mesh would also not remove the application's own failure handling [R2]. The capability is retained as a conditional future decision in §5.3 rather than abandoned.

### Alternative D — No Enterprise Guidance

Allow each system to place cross-cutting mechanics as its team prefers.

**Rejected because:** placement of the outbox is a correctness property, not a preference. Without a stated rule, a service that publishes through an out-of-process component after committing state produces silent event loss that no test in that service detects.

## 9. References

The external sources the decision rests on, cited as `[Rn]`, all accessed 2026-10-20.

### Informative

- **[R1]** Envoy, _What is Envoy_. <https://www.envoyproxy.io/docs/envoy/latest/intro/what_is_envoy>. "Out of process architecture: Envoy is a self contained process that is designed to run alongside every application server"; "The out of process architecture has two substantial benefits over the traditional library approach to service to service communication: Envoy works with any application language."
- **[R2]** Istio, _Traffic Management_, §Working with your applications. <https://istio.io/latest/docs/concepts/traffic-management/>. "Istio failure recovery features are completely transparent to the application"; "This means that if you are also setting failure recovery policies in your application code you need to keep in mind that both work independently, and therefore might conflict"; "While Istio failure recovery features improve the reliability and availability of services in the mesh, applications must handle the failure or errors and take appropriate fallback actions."
- **[R3]** Istio, _Ambient mode overview_. <https://istio.io/latest/docs/ambient/overview/>. "Since workload pods no longer require proxies running in sidecars in order to participate in the mesh, ambient mode is often informally referred to as “sidecar-less mesh”."
- **[R4]** Istio, _Distributed Tracing overview_. <https://istio.io/latest/docs/tasks/observability/distributed-tracing/overview/>. "Applications must propagate this information in HTTP headers, so that when proxies send spans, the backend can join them together into a single trace."
- **[R5]** Dapr, _How-To: Enable the transactional outbox pattern_. <https://docs.dapr.io/developing-applications/building-blocks/state-management/howto-outbox/>. "The transactional outbox pattern uses a single transaction that spans across the database and the message broker delivering the notification"; "The outbox feature requires a transactional state store supported by Dapr."
- **[R6]** C. Richardson, _Pattern: Transactional outbox_, microservices.io. <https://microservices.io/patterns/data/transactional-outbox.html>. "The command must atomically update the database and send messages in order to avoid data inconsistencies and bugs"; "But without using 2PC, sending a message in the middle of a transaction is not reliable."
- **[R7]** Netflix, _Hystrix_ README. <https://github.com/Netflix/Hystrix>. "Hystrix is no longer in active development, and is currently in maintenance mode"; "Meanwhile, our focus has shifted towards more adaptive implementations that react to an application’s real time performance rather than pre-configured settings … and to leverage open and active projects like resilience4j for new internal projects." Netflix makes no claim about meshes.
- **[R8]** Google, _Site Reliability Engineering_, ch. 22, "Addressing Cascading Failures". <https://sre.google/sre-book/addressing-cascading-failures/>. "Limit retries per request"; "Consider having a server-wide retry budget"; "In particular, avoid amplifying retries by issuing retries at multiple levels: a single request at the highest layer may produce a number of attempts as large as the product of the number of attempts at each layer to the lowest layer."
