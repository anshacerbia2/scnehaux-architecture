---
doc_meta:
  id: STD-GLB-003
  title: Enterprise Observability Standard
  owner: Architecture Review Board
  version: 1.2.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 365
  created_date: 2026-01-01
  last_reviewed: 2026-10-09
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
3. **Attributes come from a closed set.** A severity or an operation type is an attribute. A client, Principal, Tenant, source address or any other identifier is never one: "Each labelset is an additional time series", and "The vast majority of your metrics should have no labels" [R2]. Prometheus names the same limit: "Do not use labels to store dimensions with high cardinality (many different label values), such as user IDs, email addresses, or other unbounded sets of values" [R3]. The gauge says how many. The service's log and its API say which, as each repository's design states.
4. **Every value of the set is observed, zero included.** "Time series that are not present until something happens are difficult to deal with ... export a default value such as `0` for any time series you know may exist in advance" [R2]. Zero then means none, and absence means the read failed.
5. **A refusal that leaves no row is a counter in the process (1.2.0).** A statement an isolation control refused rolls back, so no store holds the condition for a gauge to read. The service counts it where it classifies the error, with the same closed attributes, and logs the cause: a `Counter` "supports non-negative increments", and OpenTelemetry's own examples include "count the number of HTTP 5xx errors" [R1]. An alert on it reads the increase over a window.

### Distributed Tracing

- Services MUST propagate W3C Trace Context headers across all internal HTTP/gRPC boundaries and asynchronous message queues (Kafka, RabbitMQ).

### Correlation Across a Delivery (1.2.0)

`STD-GLB-006` has the gateway inject `X-Correlation-ID` and every service propagate it. A delivery the outbox dispatcher makes is a request no inbound request carried, so its value comes from the event.

1. **The event carries the correlation identifier, and the consumer reads it there.** The envelope's `data.correlation_id` is the identifier of the request that produced the event. OpenTelemetry's messaging conventions put the same context in the message rather than the transport: a creation context "allows correlating producers with consumers of a message and model the dependencies between them, regardless of the underlying messaging transport mechanism and its instrumentation", and "A producer SHOULD attach a message creation context to each message" [R4]. An HTTP header does not cross a broker, so the payload is the one place that holds it on every delivery profile of `STD-GLB-004`.
2. **A direct delivery also sends it as `X-Correlation-Id`,** so the producer's log, the delivery and the consumer's refusal join on one value. The value is the publishing context's correlation identifier when it has one, such as a replay run under an operator's incident correlation, otherwise the envelope's when it is a valid identifier, otherwise none.
3. **A missing or malformed value never fails a delivery.** The event is not at fault, and correlation is telemetry. OpenTelemetry states the priority: "We assume that users would prefer to lose telemetry data rather than have the library significantly change the behavior of the instrumented application" [R5].

## Exceptions

Batch jobs running for <10s may skip distributed tracing overhead.

## Enforcement Mechanism

CI code scanners to block direct vendor SDK imports.

## References

- **[R1]** OpenTelemetry, _Metrics API_ specification, "Asynchronous Gauge" and "Asynchronous instrument API", accessed 2026-10-07. <https://opentelemetry.io/docs/specs/otel/metrics/api/>. "Asynchronous Gauge is an asynchronous Instrument which reports non-additive value(s) (e.g. the room temperature - it makes no sense to report the temperature value from multiple rooms and sum them up) when the instrument is being observed"; "Callback functions will be called only when the Meter is being observed"; "Callback functions SHOULD NOT take an indefinite amount of time"; "`Counter` is a synchronous Instrument which supports non-negative increments", with the example uses "count the number of HTTP 5xx errors".
- **[R2]** Prometheus, _Instrumentation_ best practices, "Do not overuse labels" and "Avoid missing metrics", accessed 2026-10-07. <https://prometheus.io/docs/practices/instrumentation/>. "Each labelset is an additional time series that has RAM, CPU, disk, and network costs"; "The vast majority of your metrics should have no labels"; "Time series that are not present until something happens are difficult to deal with, as the usual simple operations are no longer sufficient to correctly handle them. To avoid this, export a default value such as `0` for any time series you know may exist in advance."
- **[R3]** Prometheus, _Metric and label naming_, accessed 2026-10-09. <https://prometheus.io/docs/practices/naming/>. "Remember that every unique combination of key-value label pairs represents a new time series, which can dramatically increase the amount of data stored. Do not use labels to store dimensions with high cardinality (many different label values), such as user IDs, email addresses, or other unbounded sets of values."
- **[R4]** OpenTelemetry, _Semantic conventions for messaging spans_, "Context propagation", status Development, accessed 2026-10-09. <https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/>. "To be able to directly correlate producers with consumers, another context that is propagated with the message is required"; "A message _creation context_ allows correlating producers with consumers of a message and model the dependencies between them, regardless of the underlying messaging transport mechanism and its instrumentation"; "A producer SHOULD attach a message creation context to each message."
- **[R5]** OpenTelemetry, _Error handling in OpenTelemetry_, accessed 2026-10-09. <https://opentelemetry.io/docs/specs/otel/error-handling/>. "We assume that users would prefer to lose telemetry data rather than have the library significantly change the behavior of the instrumented application"; "OpenTelemetry implementations MUST NOT throw unhandled exceptions at runtime."
