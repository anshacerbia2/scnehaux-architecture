---
doc_meta:
  id: ADR-GLB-FE-008
  title: ADR-GLB-FE-008 Standardization on GraphQL as Primary Data Protocol
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-008: Standardization on GraphQL as Primary Data Protocol

---

## 1. Title

Standardization on GraphQL as Primary Data Protocol

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                              | Approver                  |
| ---------- | -------- | ------------ | -------------------------------------- | ------------------------- |
| 2026-06-01 | proposed | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |

## 3. Context

As enterprise UI complexity grows, frontend applications are increasingly forced to orchestrate multiple REST API calls to render a single view. This leads to massive over-fetching (downloading unneeded payload data) and under-fetching (requiring waterfall requests to fetch relational data). Furthermore, the lack of a strictly typed contract between Frontend and Backend results in frequent runtime errors and fragile integration layers.

## 4. Decision Drivers

- **Payload Optimization**: Mobile and low-bandwidth users require exact data payloads without bloated JSON responses.
- **Developer Velocity**: Frontend engineers need auto-generated TypeScript types directly from the API schema to ensure compile-time safety.
- **Client-Side Caching**: A robust, normalized caching mechanism is required to prevent redundant network requests when navigating between UI components.
- **Backend-For-Frontend (BFF)**: The enterprise requires an API Gateway that aggregates microservices into a single, cohesive schema for UI consumption.

## 5. Decision

We will standardize **GraphQL** as the primary synchronous data-fetching protocol for all enterprise frontend applications. REST APIs are officially deprecated for new complex data aggregations and must only be used for binary uploads/downloads or legacy system integrations.

- **Client Library**: We mandate the use of **Apollo Client** (or **URQL**) as the standard GraphQL client to handle normalized caching, optimistic UI updates, and query batching.
- **Schema Validation**: All GraphQL queries must be statically analyzed and compiled into TypeScript types during the CI/CD build phase using GraphQL Code Generator.

## 6. Consequences

### Positive

- **Exact Data Fetching**: UIs only request the specific fields they need, drastically reducing network payload size and parsing time.
- **End-to-End Type Safety**: The GraphQL schema acts as the ultimate source of truth, enabling automated contract testing and TypeScript interface generation.
- **Normalized Caching**: Apollo/URQL automatically normalizes entities by `__typename` and `id`, ensuring the UI is consistently updated across multiple components without manual state management.

### Negative & Risks

- **Caching Complexity**: HTTP-level caching (CDN) becomes ineffective because all GraphQL requests hit a single `/graphql` endpoint via POST. Caching must be managed via Persisted Queries or at the Application/Gateway layer.
- **Learning Curve**: Frontend engineers must master the declarative mental model of GraphQL fragments, cache invalidation, and pagination (Relay Cursor Connections).

### Operational

- The Platform Team must maintain a unified GraphQL Gateway (Federation) that aggregates all backend microservices.
- Raw `fetch()` calls to REST endpoints are strictly prohibited for domain data retrieval unless authorized via architectural waiver.

## 7. Compliance Impact

### Related Standards

- [STD-GLB-FE-010 (Data Access)](../../02-standards/_global/STD-GLB-FE-010-data-access.md) - Tactical implementation rules for Apollo/URQL and cache management.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **REST APIs (OpenAPI/Swagger)**: Rejected. Prone to over-fetching and requires the frontend to write complex orchestration logic to join data from multiple microservices.
- **gRPC-Web**: Rejected. While highly optimized for low latency (< 10ms serialization) via Protobuf, the ecosystem for frontend debugging and normalized caching is far less mature than GraphQL.
