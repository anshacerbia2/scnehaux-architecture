---
doc_meta:
  id: STD-GLB-003
  title: Enterprise Observability Standard
  owner: Architecture Review Board
  version: 1.0.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 365
  created_date: 2026-01-01
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

### Distributed Tracing

- Services MUST propagate W3C Trace Context headers across all internal HTTP/gRPC boundaries and asynchronous message queues (Kafka, RabbitMQ).

## Exceptions

Batch jobs running for <10s may skip distributed tracing overhead.

## Enforcement Mechanism

CI code scanners to block direct vendor SDK imports.
