---
doc_meta:
  id: ADR-GLB-FE-009
  title: ADR-GLB-FE-009 Real-Time Communication and Push Strategy
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-009: Real-Time Communication and Push Strategy

---

## 1. Title

Real-Time Communication and Push Strategy (WebSocket, SSE, WebPush)

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                              | Approver                  |
| ---------- | -------- | ------------ | -------------------------------------- | ------------------------- |
| 2026-06-01 | proposed | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |

## 3. Context

Enterprise applications increasingly require live data updates (e.g., live dashboards, chat systems, collaborative editing, and push notifications). Historically, teams have relied on short-polling (HTTP requests every X seconds), which severely degrades backend API performance, drains client battery, and inflates cloud costs due to massive redundant network overhead. A standardized protocol strategy for real-time state synchronization is urgently needed.

## 4. Decision Drivers

- **Network Efficiency**: We must eliminate HTTP polling overhead (headers, handshakes) for highly volatile data.
- **Connection Management**: Persistent connections (stateful) require complex load balancer configurations and Redis Pub/Sub scaling strategies on the backend.
- **Directionality**: Not all live data requires bi-directional communication. Some use cases only require server-to-client streaming.
- **Background Notifications**: Users must be able to receive critical alerts even when the browser tab is closed.

## 5. Decision

We standardize the real-time communication stack into three distinct protocols, strictly segmented by use case:

1. **Server-Sent Events (SSE)**: Must be the default choice for one-way, server-to-client streaming (e.g., live stock tickers, system status updates). SSE operates over standard HTTP/2, automatically handles reconnections, and requires zero stateful Load Balancer gymnastics.
2. **WebSockets (GraphQL Subscriptions / Socket.io)**: Exclusively reserved for high-frequency, bi-directional communication (e.g., chat applications, multiplayer collaborative editing). WebSockets must not be used if the client only needs to _listen_ to data.
3. **WebPush Protocol (Service Workers)**: Mandated for asynchronous, offline notifications. Must be integrated natively via standard browser Service Workers to deliver OS-level push notifications even when the application is closed.

## 6. Consequences

### Positive

- **Architectural Precision**: Teams stop defaulting to heavy WebSockets for straightforward one-way data feeds, utilizing lightweight SSE instead.
- **Backend Relief**: Eliminating HTTP polling drastically reduces the compute load and database queries on the backend API Gateway.
- **User Engagement**: Native WebPush integration ensures critical alerts reach users reliably, mirroring native mobile app experiences.

### Negative & Risks

- **Stateful Scaling**: WebSockets require the backend to maintain state. Load balancers must support sticky sessions or the backend must utilize a centralized Pub/Sub (e.g., Redis) to sync messages across horizontal server nodes.
- **Firewall Interference**: Certain enterprise firewalls arbitrarily block WebSocket upgrades or drop persistent connections, requiring the frontend to write robust fallback mechanisms (e.g., long-polling fallback).

### Operational

- Frontend applications must implement exponential backoff logic for all persistent connection reconnections to prevent DDoSing our own servers after a network partition.
- `HTTP Short Polling` (`setInterval` fetch) is officially prohibited unless granted a specific architectural waiver.

## 7. Compliance Impact

### Related Standards

- [ADR-GLB-FE-008 (GraphQL Protocol)](ADR-GLB-FE-008-graphql-protocol.md) - Outlines how GraphQL Subscriptions will utilize the WebSocket transport layer.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **HTTP Long-Polling**: Rejected. While easier to scale on legacy load balancers than WebSockets, it still incurs massive HTTP header overhead and connection churn compared to SSE or true WebSockets.
- **WebRTC**: Rejected for general data transfer. While perfect for peer-to-peer audio/video streaming, it is vastly over-engineered and difficult to traverse via NAT/TURN servers for straightforward JSON data synchronization.
