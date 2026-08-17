---
doc_meta:
  id: STD-GLB-006
  title: Enterprise Integration Architecture Standard
  owner: Principal Software Architect
  version: 1.1.0
  status: adopted
  classification: restricted
  governed_by: [EAD-004]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_updated: 2026-08-18
  last_reviewed: 2026-08-18
---

# Enterprise Integration Architecture Standard (STD-GLB-006)

---

## 1. Objective & Scope

This standard defines the mandatory integration communication patterns, API Gateway routing policies, egress network filters, third-party webhook verifications, and event ingestion boundaries across the Scnehaux enterprise.

It applies to all synchronous service-to-service REST/gRPC APIs, asynchronous event brokers, ingress controllers, and external gateway interfaces.

---

## 2. Design Principles

Inter-service integration must enforce strict contract boundaries. Services communicate through well-defined interfaces with explicit versioning, timeout propagation, and failure isolation at every boundary.

## 3. Normative Rules

### Integration Communication Patterns

To prevent cascading service failures and tightly coupled dependencies:

- **Orchestration vs. Choreography Boundaries**:
  - _Choreography (Default Event-Driven)_: Cross-domain coordination must utilize event-driven choreography. Services publish events to the broker, and downstream services react independently (e.g. `payroll-service` consuming `EmploymentTerminatedEvent`).
  - _Orchestration (Saga Pattern)_: Complex multi-step transactions requiring synchronous control loops (e.g., identity provisioning across active systems) must use a centralized orchestrator service. The orchestrator must manage state, call downstream APIs, and execute compensating transactions if a step fails.
- **Service-to-Service Invariants**:
  - _No Circular Dependencies_: Service-to-service call graphs must be acyclic. Circular call patterns (Service A calling Service B, which calls Service A) are strictly prohibited.
  - _Transport Standard_: The synchronous transport is selected by traffic class rather than by network position, and the class MUST be declared in the providing system's design.
    - **gRPC over HTTP/2 is REQUIRED** for internal service-to-service calls on a request hot path: per-request authorization checks, per-request context reads, inference calls, and any interface whose expected volume is proportional to end-user traffic. Type safety and framing matter most exactly where call volume is highest.
    - **REST/JSON is PERMITTED** for public client-to-service ingress, and for control-plane and administrative interfaces whose volume is proportional to operator actions rather than to end-user traffic.
    - A control-plane interface MUST NOT be exposed over both transports. Two surfaces over one authority produce two authorization paths, and the weaker one is the one an attacker uses.

    The exemption for control-plane interfaces is not a convenience. `EAD-004 §5.3` mandates RFC 9457 Problem Details for the error model, and the control-plane contracts across this estate depend on `Idempotency-Key`, optimistic-concurrency preconditions, and `202 Accepted` with a polled operation resource. Those are HTTP semantics with registered meanings; carrying them over gRPC means re-encoding each one in metadata and status details, which replaces a standard every client already implements with a convention each client must be told about.

---

### API Gateway Ingress Routing & Invariants

All external traffic must traverse the enterprise API Gateway (e.g., Kong, Envoy). Direct client routing to internal microservice instances is prohibited.

- **TLS Termination**: The gateway must terminate incoming TLS traffic using secure certificates (TLS 1.3 minimum). Communication from the gateway to internal services must run over encrypted private VPC channels.
- **Cross-Origin Resource Sharing (CORS)**: The gateway must enforce strict CORS policies. Wildcard origins (`*`) are prohibited; allowed origins must explicitly match designated corporate sub-domains.
- **Rate-Limiting Policy**: The gateway must enforce rate-limiting tiers based on client tier configurations:
  - _Enterprise Clients_: Maximum 100 requests per second (RPS) per IP.
  - _Standard Clients_: Maximum 20 requests per second (RPS) per IP.
  - _Unauthenticated Public Endpoints_: Maximum 5 requests per second (RPS) per IP.
- **Header Injection**: The gateway must inject correlation metadata into every ingress request, including `X-Request-ID` and `X-Correlation-ID`. These headers must propagate throughout the downstream service chain.

---

### Third-Party Webhook & Web Service Security

Integrating with external vendors (e.g. Stripe, external HR software, email providers):

- **Egress Proxy Routing**: Outbound calls to external third-party APIs must route through a designated egress proxy. The proxy must enforce domain whitelisting, audit log request metadata, and decrypt outbound payloads using system keys.
- **Incoming Webhook Verification**: Services accepting incoming webhooks must validate the sender identity:
  - _Signature Verification_: Webhooks must verify cryptographic signatures (e.g., HMAC-SHA256) using shared signing keys. Payloads lacking valid signatures must be rejected.
  - _Replay Attack Prevention_: Webhook handlers must validate the request timestamp. Requests older than `300 seconds` (5 minutes) must be discarded.

---

### Event Ingestion Boundaries

- **Gateway-Level Schema Validation**: Inbound events arriving from external webhooks must undergo schema validation at the API Gateway or edge validation middleware before being published to the internal message broker.
- **Ingestion Queue Sizing**: Ingestion endpoints must throttle input traffic using buffering queues to prevent publisher spikes from degrading downstream consumer databases.

---

## 4. Exceptions

None. All integration pattern rules apply unconditionally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

1. **Gateway configuration Audits**: CI pipelines must audit API Gateway routing specifications (`gateway.yaml` or equivalent declarations) to verify that no internal service endpoints bypass rate-limiting policies or authentication checks.
2. **Egress Firewall Rules**: Automated infrastructure scanners must verify that private subnet egress firewall rules permit outbound network access only to white-listed domains.
3. **Exception Waivers**: Deviations from these integration patterns require an approved ADR signed by the Enterprise Security Board and the Principal Software Architect.
