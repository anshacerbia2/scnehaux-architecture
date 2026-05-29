---
doc_meta:
  id: STD-GLB-001
  title: Enterprise API Design Standard
  owner: Enterprise Architect
  version: 1.0.0
  status: adopted
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# Enterprise API Design Standard (STD-GLB-001)

---

## 1. Objective & Scope

This standard establishes the non-negotiable rules for designing, versioning, and implementing network APIs across the Scnehaux enterprise. It applies to all external client-facing REST endpoints and all internal service-to-service gRPC APIs.


## 2. Design Principles

*(TBD - Architectural philosophy guiding these rules)*

## 3. Normative Rules

### Public REST API Standards (Client-Facing)

All public APIs exposed at the enterprise perimeter must be RESTful and conform strictly to the **OpenAPI 3.1** specification.

#### Protocol & Versioning
- **Format**: JSON payloads strictly. Plaintext or XML is prohibited.
- **URL Versioning**: Mandatory path-based versioning (`/v1/resource`). Custom version headers are prohibited.
- **UTF-8 Enforcement**: All JSON payloads must be encoded in UTF-8. The `Content-Type` header must be `application/json; charset=utf-8`.

#### Standard Response Wrapper
To ensure client parsing predictability, every API response must follow this deterministic JSON schema:

#### Success Response (HTTP 200/201)
```json
{
  "success": true,
  "data": {
    "user_id": "usr_92f3a8",
    "email": "user@scnehaux.com"
  },
  "metadata": {
    "request_id": "req_01h6w821j",
    "timestamp": "2026-05-18T01:15:00Z",
    "path": "/api/v1/users",
    "version": "v1"
  }
}
```

#### Error Response (HTTP 4xx/5xx)
Must conform strictly to **RFC 7807 (Problem Details)** to prevent raw stack-trace leakage:
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "The provided credentials are invalid or expired.",
    "details": {
      "ip_address": "192.168.1.1"
    },
    "reference": "https://docs.scnehaux.com/errors/AUTHENTICATION_FAILED"
  },
  "metadata": {
    "request_id": "req_01h6w821j",
    "timestamp": "2026-05-18T01:15:05Z",
    "path": "/api/v1/auth/login",
    "version": "v1"
  }
}
```

#### Context & Tenant Propagation
To support absolute B2B multi-tenancy, all client requests crossing the gateway must propagate tenant context:
- **Mandatory Header Key**: `Scnehaux-Account`
- **Header Value**: A cryptographically valid, non-null Tenant UUID (v4 or v7).
- **Validation**: Gateway and application middleware must validate the presence of this header. Requests lacking it must fail-closed with an HTTP 400 Bad Request.

#### Pagination & Rate Limiting
- **Pagination**: Large collections must implement cursor-based pagination using `limit` and `starting_after` query params. Page-offset pagination is prohibited due to database execution overhead on large datasets. Keyset or offset-based pagination is permitted solely under an approved ADR waiver for complex reporting/admin interfaces requiring random page access.
- **Rate Limit Headers & Tiers**: APIs must enforce tiered rate limiting and return standard headers:
  - `X-RateLimit-Limit`: Maximum requests allowed per window.
  - `X-RateLimit-Remaining`: Remaining requests in current window.
  - `Retry-After`: Delay time in seconds when rate limits are exceeded.
  - *Standard Rate Limit Tiers*:
    - Authenticated Enterprise Tier: `100` requests per second (RPS) sustained, `150` RPS burst.
    - Standard Authenticated Tier: `20` RPS sustained, `50` RPS burst.
    - Public/Unauthenticated Tier: `5` RPS sustained, `10` burst.

#### Idempotency & Mutations
- **Idempotency Header**: Non-idempotent mutations (POST/PATCH operations on financial transactions or core identity mutations) must require the client to send an `Idempotency-Key` header holding a unique UUID v4.
- **Idempotency Cache**: The server must cache the response of successful requests associated with the `Idempotency-Key` in Redis for `86400s` (24 hours). Replayed requests with the same key within this window must return the cached response without re-executing the operation.

#### Webhook Standards
- **Payload Format**: Outgoing webhooks must deliver CloudEvents payload structures in JSON format.
- **Security Signatures**: All webhook POST requests must include a cryptographic signature header `X-Scnehaux-Signature` generated using HMAC-SHA256 with a tenant-specific shared secret key.
- **Replay Protection**: The payload must contain an `X-Scnehaux-Timestamp` header. Receivers must reject webhooks if the timestamp differs from current system time by more than `300s` (5 minutes).
- **Retry Policy**: Failed webhook deliveries (network errors or HTTP status non-2xx) must trigger retries using exponential backoff with jitter over `72 hours` before routing to the dead letter log.

#### Sunset & Deprecation Policy
- **Notice Period**: Deprecated API versions must remain supported for a minimum transition period of `12 months` after formal deprecation notification.
- **Deprecation Headers**: Deprecated endpoints must return the standard HTTP headers:
  - `Deprecation: true` (or date-anchored timestamp).
  - `Sunset`: Date indicating when the endpoint will be turned off (conforming to RFC 8594).

---

### Internal RPC API Standards (Service-to-Service)

All internal inter-service communication must run over gRPC using **Protocol Buffers v3 (Protobuf)**.

- **Encapsulation & Security**: All internal gRPC calls must run strictly within the mTLS service mesh.
- **Deadline Propagation**: Context deadlines must be propagated across all RPC hops. If a downstream RPC exceeds `2000ms`, it must abort to prevent connection starvation.
- **Rich Error Handling**: Use the standard `google.rpc.Status` proto to return detailed error codes and details payloads rather than plain string messages.

---


## 4. Exceptions & Alternatives

Deviations from these normative rules require an approved exception waiver from the Architecture Review Board (ARB).

## 5. Enforcement Mechanism

1.  **API Schema Linting**: All OpenAPI specifications and Protobuf schemas are audited in the CI/CD pipeline using automated linters (e.g., `buf lint`).
2.  **Telemetry Correlation**: Every request must carry an OpenTelemetry W3C `traceparent` context header.
3.  **Deviation Waiver**: Any deviation from this API design standard requires an approved Architectural Decision Record (ADR) and Architecture Review Board (ARB) waiver.
