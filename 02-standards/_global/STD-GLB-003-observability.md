---
doc_meta:
  id: STD-GLB-003
  title: Enterprise Observability Standard
  owner: Architecture Review Board
  version: 1.1.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 365
  created_date: 2026-01-01
  last_reviewed: 2026-10-07
---

# STD-GLB-003: Enterprise Observability Standard

## Objective & Scope

Distributed systems fail in complex ways. This standard defines the telemetry requirements to ensure all services are monitorable, traceable, and debuggable in production.

## Design Principles

- Observability is a first-class feature, not an afterthought.
- All telemetry must be vendor-agnostic at the application level.

## Normative Rules

### OpenTelemetry Mandate

- **OpenTelemetry (OTel)** is the mandatory instrumentation framework for all services.
- Vendor-specific agents (e.g., Datadog Agent, New Relic Agent) MUST NOT be directly coupled into application code. All telemetry MUST flow through an OTel Collector.

### Logging Requirements

- Logs MUST be written to `stdout/stderr` in **structured JSON format**.
- The following context fields are MANDATORY in every log entry:
  - `timestamp` (ISO 8601)
  - `level` (INFO, WARN, ERROR, DEBUG)
  - `trace_id` and `span_id`
  - `tenant_id` (if applicable)

### Metrics (The RED Method)

All services MUST expose the RED metrics for every API endpoint and background job:

- **Rate**: Requests per second.
- **Errors**: Number of failing requests (HTTP 5xx).
- **Duration**: Request latency distributions (P50, P90, P95, P99).

### State Metrics (1.1.0)

RED measures traffic. Some failures arrive with no traffic at all: a client credential that expires next week, or a job parked for an operator. Each is a state held in a service's database, and an alert on it needs a metric that reads that state.

1. **A condition an operator is alerted on is an asynchronous gauge, read from the store that holds it.** OpenTelemetry's asynchronous gauge "reports non-additive value(s) ... when the instrument is being observed", and its "Callback functions will be called only when the Meter is being observed" [R1]. The callback reads the database when the reader collects. Every replica then reports the database's value, never its own memory, and the service keeps no extra state for the metric.
2. **The read is bounded.** "Callback functions SHOULD NOT take an indefinite amount of time" [R1]. The callback reads under its own timeout. A read that fails observes nothing and is logged. An alert on the metric therefore also fires when the metric is absent.
3. **Attributes come from a closed set.** A severity or an operation type is an attribute. A client, Principal, Tenant or any other identifier is never one: "Each labelset is an additional time series", and "The vast majority of your metrics should have no labels" [R2]. The gauge says how many. The service's log and its API say which, as each repository's design states.
4. **Every value of the set is observed, zero included.** "Time series that are not present until something happens are difficult to deal with ... export a default value such as `0` for any time series you know may exist in advance" [R2]. Zero then means none, and absence means the read failed.

### Distributed Tracing

- Services MUST propagate W3C Trace Context headers across all internal HTTP/gRPC boundaries and asynchronous message queues (Kafka, RabbitMQ).

## Exceptions

Batch jobs running for <10s may skip distributed tracing overhead.

## Enforcement Mechanism

CI code scanners to block direct vendor SDK imports.

## References

- **[R1]** OpenTelemetry, _Metrics API_ specification, "Asynchronous Gauge" and "Asynchronous instrument API", accessed 2026-10-07. <https://opentelemetry.io/docs/specs/otel/metrics/api/>. "Asynchronous Gauge is an asynchronous Instrument which reports non-additive value(s) (e.g. the room temperature - it makes no sense to report the temperature value from multiple rooms and sum them up) when the instrument is being observed"; "Callback functions will be called only when the Meter is being observed"; "Callback functions SHOULD NOT take an indefinite amount of time."
- **[R2]** Prometheus, _Instrumentation_ best practices, "Do not overuse labels" and "Avoid missing metrics", accessed 2026-10-07. <https://prometheus.io/docs/practices/instrumentation/>. "Each labelset is an additional time series that has RAM, CPU, disk, and network costs"; "The vast majority of your metrics should have no labels"; "Time series that are not present until something happens are difficult to deal with, as the usual simple operations are no longer sufficient to correctly handle them. To avoid this, export a default value such as `0` for any time series you know may exist in advance."
