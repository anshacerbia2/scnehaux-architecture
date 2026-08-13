---
doc_meta:
  id: STD-GLB-005
  title: Enterprise System Resilience & Fault Tolerance Standard
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-05-22
---

# Enterprise System Resilience & Fault Tolerance Standard (STD-GLB-005)

---

## 1. Objective & Scope

This standard establishes the mandatory patterns and thresholds for enforcing resilience and handling cascading failures across all backend microservices, data layers, and network interfaces within the Scnehaux enterprise.

It covers circuit breaking, service timeouts, bulkhead isolation, and retry execution strategies, ensuring service availability remains within SLA commitments.

---

## 2. Design Principles

Systems must be designed to fail gracefully under partial outages. Resilience patterns (circuit breakers, bulkheads, load shedding) are mandatory infrastructure concerns, not optional application-level add-ons.

## 3. Normative Rules

### Circuit Breaker Specification

To prevent resource exhaustion under distributed failures, all service-to-service communication paths must operate under a stateful circuit breaker.

- **Failure Rate Threshold**: The circuit must transition to an `OPEN` state if the error rate exceeds `5%` over a rolling window of `100` consecutive executions.
- **Consecutive Failures**: The circuit must open instantly if `5` consecutive executions fail.
- **Cooldown (Sleep Window)**: An open circuit must wait `10000ms` before entering the `HALF-OPEN` state.
- **Half-Open Verification**: The circuit breaker must route up to `5` test requests. If any of these test requests fail, the circuit must immediately revert to `OPEN`. If all succeed, the circuit returns to `CLOSED`.
- **Degraded Fallback Execution**: Callers must register a local fallback handler. If the circuit is `OPEN`, it must immediately execute the fallback (e.g., returning stale cached data or a structured failure payload) without contacting the downstream service.

---

### Timeout Hierarchy & Deadlines

To prevent connection pools and thread stacks from starving, all request lifecycles must enforce a strict, cascaded timeout hierarchy.

- **Edge Ingress Gateway**: Maximum deadline is `30000ms` (30s).
- **Service-to-Service REST/gRPC Requests**: Maximum deadline is `2000ms` (2s).
- **Database Query Executions**: Default timeout must be set to `5000ms` (5s). Heavy report queries can extend this up to `15000ms` (15s) with a dedicated query context.
- **External Third-Party Integrations**: Maximum timeout is `10000ms` (10s).
- **Cascaded Cancellation**: Service handlers must actively monitor connection contexts (`context.Context` in Go or `AbortSignal` in JavaScript) to terminate processing if a parent request times out or is cancelled by the caller.

---

### Bulkhead & Concurrency Isolation

Services must segment resources to isolate failures to a single downstream dependencies context.

- **Thread Pool Segmenting**: Thread/connection pools must be isolated per downstream dependency. A failure in one external service must not starve thread pools dedicated to other services.
- **Concurrency Caps**: Concurrency limits must be enforced on external calls. No single downstream integration can consume more than `25%` of a service's overall thread or connection pool capacity.
- **Rate-Limiting Headers**: Rate limiting must return standardized HTTP headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After`) to enforce downstream backpressure.

---

### Retry and Exponential Backoff Policy

Retrying failed operations must implement random delays to prevent retry storms (thundering herd problem).

- **Retry Applicability**: Retries are permitted only for transient failures (HTTP 502, 503, 504, or network socket timeouts). Retries are prohibited for validation errors (HTTP 4xx) or authentication failures.
- **Delays (Backoff)**: Retries must use exponential backoff: $$T_i = \min(T_{\max}, T_{\text{initial}} \times 2^i) + \text{random\_jitter}$$
  - $T_{\text{initial}}$ must be at least `100ms`.
  - $T_{\max}$ must be capped at `3000ms`.
  - Jitter must add a random variance of `0` to `50%` of the delay step.
- **Maximum Attempt Count**: Retries must be capped at `3` attempts. If the third retry fails, the error must be propagated to the caller.

---

### Load Shedding & Ingress Mitigation

To prevent service collapse under load spike conditions, services must implement active load shedding by rejecting low-priority requests when host resource limits are breached:

- **Shedding Thresholds**: Load shedding must activate automatically if any of the following host metrics are breached:
  - _CPU Utilization_: Host CPU utilization exceeds `85%` for longer than `10 consecutive seconds`.
  - _Memory Pressure_: Container memory utilization exceeds `90%` of its allocated cgroup limit.
  - _Request Queue Length_: The pending request buffer queue length exceeds `500 requests`.
- **Request Priority Classification**: Ingress requests must carry or resolve a priority header class:
  - **Priority 1 (System-Critical)**: Token verification, session authentication, transactional writes, database ledger entries.
  - **Priority 2 (Standard Operations)**: Core user interactions, read queries, configuration checks.
  - **Priority 3 (Background / Non-Interactive)**: Telemetry exports, analytical reports, background syncs, administrative audits.
- **Shedding Execution Order**:
  - When a shedding threshold is breached, the ingress gateway or application middleware must drop Priority 3 requests immediately.
  - If resource pressure persists for an additional `5 seconds`, Priority 2 requests must be shed.
  - Priority 1 requests must never be shed.
- **Rejection Behavior**: Shed requests must return an HTTP `503 Service Unavailable` or `429 Too Many Requests` status, accompanied by a `Retry-After` header indicating a cooldown window of `10 seconds`.

---

## 4. Exceptions

None. All resilience and fault tolerance rules apply universally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

1. **Chaos Testing Audits**: Build verification pipelines must execute automated network failure injections (e.g. using Chaos Mesh or equivalent tools) to verify that circuit breakers and load shedding trigger under the designated thresholds.
2. **CI Validation**: Architecture compliance validation requires all backend services to declare their timeout configurations, circuit breaker registrations, and priority headers in their deployment schemas, audited during build compilation.
3. **Exception Waivers**: Deviations from these resilience parameters require an approved Architectural Decision Record (ADR) and approval by the Architecture Review Board.
