---
doc_meta:
  id: STD-GLB-003
  title: Enterprise Observability Standard
  owner: Enterprise Architect
  version: 1.0.0
  status: adopted
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# Enterprise Observability Standard (STD-GLB-003)

---

## 1. Objective & Scope

This standard establishes the non-negotiable rules for structured logging, distributed tracing, metrics emission, and performance alerts across the Scnehaux enterprise. It applies to all services, microservices, background jobs, and cloud-native infrastructure components.


## 2. Design Principles



## 3. Normative Rules

### Telemetry & Observability Standards

To guarantee deep cross-system visibility during incidents and ensure a 99.99% system availability target, all services must implement the **OpenTelemetry (OTel)** standard.

#### Structured Logging Rules
- **JSON Format**: In all non-development environments, services must emit structured logs in JSON format directly to `STDOUT`. Plaintext or legacy log patterns are prohibited.
- **Mandatory Correlation Context**: Every log entry must include, if available, the following exact keys to allow correlation queries:
  - `trace_id`: The W3C distributed trace identifier.
  - `span_id`: The active OTel span identifier.
  - `tenant_id`: The active multi-tenancy context.
  - `actor_id`: The identifier of the authenticated user/service agent.
- **PII Scrubbing**: Logs must be programmatically scrubbed of sensitive data (passwords, JWT secrets, authorization headers, credit cards, emails) before serialization.

#### Distributed Tracing Rules
- **W3C Standard Propagation**: All HTTP and gRPC services must inject and extract W3C `traceparent` headers across boundaries.
- **Context Preservation**: Asynchronous processing paths (e.g., outbox dispatchers, background workers) must preserve the `trace_id` from the originating API transaction to maintain unified trace maps.
- **Span Coverage**: Spans must wrap all significant database queries, external KMS integrations, and inter-service HTTP/gRPC calls.

#### Prometheus Metrics Rules
All active services must expose a `/metrics` scrape endpoint.
- **Naming Conventions**: Metrics must follow a strict namespaces format: `namespace_subsystem_name_unit` (e.g., `auth_session_validation_duration_seconds`).
- **RED Metrics Baseline**: Every network service must emit the following baseline metrics:
  - **Rate**: Inbound requests per second (RPS).
  - **Errors**: Number of failed requests (HTTP 5xx, gRPC error codes).
  - **Duration**: p95 and p99 request execution latency metrics.

#### SLO Tiers & Availability Targets
To establish clear availability thresholds, all enterprise services must align to one of the following Service Level Objective (SLO) tiers:
- **Tier 1 (Core Path)**: Includes Identity & Access Management (IAM), Session Validation, and Financial Ledgers.
  - *Availability Target*: `99.99%` over a rolling 30-day window.
  - *Latency Target*: p99 execution duration `< 200ms`.
- **Tier 2 (General API)**: Includes resource management, analytics ingestion, and transactional configurations.
  - *Availability Target*: `99.9%` over a rolling 30-day window.
  - *Latency Target*: p99 execution duration `< 1000ms`.
- **Tier 3 (Internal Reporting & CMS)**: Includes administrative panels, content management, and reporting systems.
  - *Availability Target*: `99.0%` over a rolling 30-day window.
  - *Latency Target*: p95 execution duration `< 3000ms`.

#### Alerting & Burn Rates
- **Burn Rate Alerts**: Critical alerts (S1/S2 pages) must trigger based on Service Level Objective (SLO) error budget burn rates rather than static resource thresholds.
- **Alert Thresholds**:
  - *Fast Burn Alert (PagerDuty)*: Triggered if `2%` of the monthly error budget is consumed in a `1-hour` window (burn rate multiplier of `14.4`).
  - *Slow Burn Alert (Slack Ticket)*: Triggered if `5%` of the monthly error budget is consumed in a `6-hour` window (burn rate multiplier of `6.0`).
- **Alert Runbook Structure**: Every alert definition must link to a structured runbook in documentation containing:
  1. *Condition Summary*: Description of the triggered metric and customer impact.
  2. *First-Response Triage*: Commands to check active traffic volume, logs, and database locks.
  3. *Mitigation Paths*: Specific steps to roll back, scale capacity, or failover.
  4. *Escalation Contacts*: Team ownership metadata.

#### Distributed Trace Sampling
- **Sampling Rates**: To manage storage overhead, the distributed tracing collector must implement adaptive tail-based sampling rules:
  - *Success Paths (HTTP 2xx)*: Sampled at `10%` of overall traffic.
  - *Error Paths (HTTP 5xx / gRPC errors)*: Sampled at `100%` of traffic.
  - *Slow Transactions (latency > p95 target)*: Sampled at `100%` of traffic.
- **Span Limit**: Individual traces are capped at `1000` child spans to prevent trace buffer memory exhaustion.

#### Uptime and Synthetic Probes
- **External Synthetic Checks**: To monitor client-facing availability, independent synthetic probe runners must hit core endpoints (e.g. `/healthz`, `/api/v1/auth/jwks`) from multiple public geographic regions once every `60s`.
- **Latency Alarms**: If a synthetic check fails or exceeds a latency of `5000ms` for `3` consecutive probes, an S1 incident ticket must trigger automatically.

#### Business-Centric Observability (Business SLIs & KPIs)
To measure system performance relative to actual business value and user outcomes, services must track domain-specific business transactions alongside system resources:
- **Telemetry Propagation**: Key business processes must propagate trace contexts containing explicit metadata descriptors (e.g. `business.operation_id`, `business.domain`, `business.record_count`) using custom OpenTelemetry span attributes.
- **HRIS Core Business SLIs**: All HRIS deployments must export the following high-level business indicators:
  - *Payroll Processing Success Rate*: Calculated as `(Successful Payroll Cycles / Total Triggered Payroll Cycles) * 100`. The target KPI is $\ge 99.9\%$ over a rolling 30-day window.
  - *Leave Approval Latency*: The p95 time elapsed between a leave request submission and its final workflow resolution. The target KPI is $\le 2$ hours.
  - *User Provisioning Completion Duration*: The p99 duration required to fully provision access across all integrated downstream systems following user onboarding. The target KPI is $\le 5$ minutes.
- **Reporting Interfaces**: Business metrics must be exported to Prometheus and visualized on domain dashboards dedicated to service delivery managers.

#### Observability Cost Governance & Telemetry Economics

To manage storage bills and network bandwidth overhead under high-volume operations:

1.  **Adaptive Trace Sampling Rules**:
    - **Standard Load (< 1000 TPS)**: Success traces (HTTP 2xx) must be sampled at a `10%` rate.
    - **Extreme Ingress Load (>= 1000 TPS)**: Success traces must be throttled dynamically to a `1%` sampling rate or less using tail-based collector sampling filters.
    - **Invariants**: Error responses (HTTP 5xx / gRPC error codes) and slow requests (latency > p95 target) must be captured at a `100%` rate under all load conditions.
2.  **Telemetry Data Retention Tiers**:
    - **Tier A (Debug Logs & Traces)**: Maximum retention of `7 days`. Data must undergo automatic deletion after 7 days to clear storage volumes.
    - **Tier B (Info/Warning Operational Logs)**: Retained for `30 days` on standard block storage.
    - **Tier C (Audit Ledger & Security Logs)**: Retained for `7 years` (84 months) in compressed object storage formats (e.g., Apache Parquet on AWS S3 Glacier) to satisfy compliance audits while minimizing operational storage costs.
3.  **Log Volume Allocation Budgets**:
    - Services must budget log output to not exceed `20 KB per 100 requests` under normal operation. Excessive debug log patterns in production build files are prohibited.

---


## 4. Exceptions



## 5. Enforcement Mechanism

1.  **Automated Audits**: Telemetry libraries are validated during CI/CD compilation. Services failing to expose the mandatory `/metrics` endpoint or log in JSON are blocked from deployment.
2.  **Trace Correlation Audits**: Staging trace maps are regularly audited to ensure trace IDs propagate from the API gateway down to the persistent database transaction layer without breaks.
3.  **Waiver Protocol**: Custom logging or metric configurations require an approved ADR and Architecture Review Board (ARB) exemption sign-off.
