---
doc_meta:
  id: ADR-GLB-005
  title: ADR-GLB-005 Adopting Load Shedding and Resilience Invariants
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-GLB-005: Standardizing on active Load Shedding and Priority-based request classification for enterprise microservices

---

## 1. Title

Standardizing on active Load Shedding and Priority-based request classification for enterprise microservices

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

As Scnehaux microservices scale, transient traffic spikes and downstream outages threaten the availability of core platform systems. Traditional mitigation patterns like circuit breakers and bulkheads prevent cascading failures but do not protect individual service instances from resource exhaustion when total ingress volume exceeds capacity. If a service receives requests faster than it can process them, connection pools saturate, memory utilization spikes, and the service collapses. We need a deterministic mechanism to reject low-priority traffic before host resources exhaust.

## 4. Decision Drivers

Adopting load shedding guarantees that core platform services remain operational even under catastrophic traffic spikes. By prioritizing critical operations (Priority 1) over non-interactive work, we preserve user authentication and transactional database integrity. Rejection at the ingress layer preserves CPU cycles and memory that would otherwise be wasted processing requests destined to time out, ensuring predictable system degradation rather than crash collapse.

## 5. Decision

We officially adopt active **Load Shedding** and Priority-based request classification across all enterprise services.

Application middleware and ingress controllers must automatically drop incoming traffic when system thresholds are breached:

1.  **Shedding Triggers**: Load shedding activates if CPU utilization exceeds `85%`, container memory exceeds `90%`, or the pending request buffer queue length exceeds `500 requests`.
2.  **Request Priority**: Inbound requests must carry or resolve a Priority Class:
    - _Priority 1 (System-Critical)_: Auth token validations, transactional database writes, financial ledger modifications.
    - _Priority 2 (Standard Operations)_: Standard user interactions, core query endpoints.
    - _Priority 3 (Background/Non-Interactive)_: Telemetry syncing, reporting exports, analytics ingestion, administrative audits.
3.  **Cascading Shedding Execution**: Drop Priority 3 requests first. If resource pressure persists for longer than `5 seconds`, drop Priority 2 requests. Priority 1 requests must never be shed.
4.  **Error Propagation**: Shed requests must fail fast, returning HTTP `503 Service Unavailable` or `429 Too Many Requests` status, with a `Retry-After: 10` header.

## 6. Consequences

### Positive

- **Guaranteed Core Availability**: Critical path calls (Priority 1) execute successfully during traffic spikes.
- **Fail-Fast Mechanics**: Throttled requests receive immediate responses, preventing client connection timeouts.
- **Deterministic Degradation**: Services degrade gracefully by turning off analytics and background sync features first.

### Negative

- **Operational Degradation**: Background workflows (e.g. reporting exports) fail during high-load periods.
- **Header Complexity**: Middleware must classify request priority, introducing slight request routing overhead.

### Tradeoffs

- We trade background analytical processing and internal reporting availability to guarantee transactional database integrity and core user session validation.

### Operational Impact

- Simplifies operational alerts: transient spikes do not trigger system-wide pager calls, as services handle load surges autonomously.

### Security Impact

- Prevents Denial of Service (DoS) attacks from consuming core resources, maintaining authentication gate availability.

### Scalability Impact

- Increases overall system throughput capability by preventing database locks and thread pool starvation under high stress.

### Operational

- Codified in the Enterprise System Resilience Standard (`STD-GLB-005`).
- Implementation utilizes middleware parsing incoming HTTP headers (`X-Priority-Class`) and checking CPU limits from `/sys/fs/cgroup`.

## 7. Compliance Impact

### Related Standards

- Enterprise System Resilience & Fault Tolerance Standard (STD-GLB-005)
- Enterprise Observability Standard (STD-GLB-004)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Auto-Scaling Infrastructure Only

- **Pros**: Accommodates traffic surges by dynamically increasing compute instances.
- **Cons**: Scaling out has latency (often taking 2 to 5 minutes to launch containers), fails to prevent instant crash spikes, and can exhaust downstream database connection pools.
- **Why Rejected**: Fails to protect services during the scaling lag, leading to service outages before new containers boot.

### Alternative B: Direct Rate Limiting (No Priority context)

- **Pros**: Requires low configuration effort to implement globally at the API Gateway.
- **Cons**: Rejects incoming requests indiscriminately. Critical authentication check calls are dropped at the same rate as background analytical exports.
- **Why Rejected**: Drops high-priority customer transactions during spikes, causing business disruption.
