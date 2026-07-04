---
doc_meta:
  id: EAD-003
  title: Enterprise Application Architecture
  owner: Chief Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 180
  last_reviewed: 2026-05-17
---

# Enterprise Application Architecture (EAD-003)

---

## 1. Application Portfolio

The Scnehaux Foundation enterprise application landscape is organized around autonomous, loosely coupled capability domains. The portfolio is divided into foundational platforms and business capability applications.

- **Foundational Platforms**: IAM, Scnehaux UI Platform (Unified Visual Engine).
- **Core Business Applications**: Workforce Management, Compensation Processing, Operational Velocity, Talent & Growth.

### 1.1 Frontend Platform Portfolio
The UI portfolio supports two primary composition patterns based on deployment requirements:
*   **Standalone Applications**: Mandated for focused, high-security, single-viewport portals (e.g., the Scnehaux IAM Dashboard). Compiled as isolated SPAs.
*   **Federated Portal Suites**: Enforced when independent deployability and runtime dynamic composition of multiple business domains are required.

## 2. Application Interaction

Modern distributed architecture dictates that integration surfaces and security boundaries are inherently the same thing. The interaction between applications relies on Zero Trust principles.

### 2.1 Identity as the Perimeter
The network is inherently hostile. IP whitelisting is insufficient. Every request must carry cryptographic proof of identity (Service or User). In the event of an ambiguity or failure in the authorization chain, the system must deny access (Fail-Closed Security).

### 2.2 The API Gateway Layer
All external traffic must ingress through a centralized API Gateway responsible for:
*   SSL/TLS termination.
*   Initial token validation (JWKS).
*   Global Rate Limiting and WAF enforcement.
*   Routing to downstream domain services.

### 2.3 Service-to-Service Integration (The Mesh)
Direct internal communication between microservices bypasses the external Gateway and utilizes internal routing.
*   **Protocol**: REST (HTTP/1.1 or HTTP/2).
*   **Security**: Mutual TLS (mTLS) is mandatory for all internal hops.
*   **Mesh Infrastructure**: The enterprise standardizes on a Service Mesh using sidecar proxies running in every application pod to enforce strict mTLS, traffic routing, retries, and distributed tracing injection (W3C Trace Context).

## 3. Application Classification

Applications within the portfolio are classified by their integration and security profiles to dictate their behavior and failure handling. All tier-0 capability endpoints must achieve >=99.95% availability.

## 4. Build vs Buy

The enterprise dictates a strict Build vs Buy strategy to maximize competitive advantage while minimizing undifferentiated heavy lifting.
- **Buy/SaaS**: Commodity services such as email delivery, external identity brokering (IdPs), and basic infrastructural logging/monitoring.
- **Build**: Core domain logic including Workforce Management, unique Payroll engines, and the unified Scnehaux UI Platform.

## 5. Enterprise Integration Strategy

Integration complexity is a liability. Homogeneous integration patterns reduce operational overhead and simplify client/SRE onboarding.

### 5.1 Standardized Interoperability
All inter-service communication must utilize the enterprise "Paved Road" protocols (REST/JSON for synchronous, NATS/Kafka for asynchronous). Proprietary or esoteric protocols are forbidden.

### 5.2 Asynchronous Integration
Event-driven architectures decouple domains. Integration via events must use the **Outbox Pattern** to guarantee that database commits and event dispatches are transactionally bound.

### 5.3 API Versioning & Lifecycle Protocol
To manage API changes without breaking client integrations:
*   **Major Versioning**: Major breaking API releases must utilize path-based versioning (e.g., `/api/v1/resource`, `/api/v2/resource`).
*   **Minor Versioning**: Non-breaking updates or minor feature variations must use header-based media type content negotiation.
*   **Deprecation Policy**: Deprecated endpoints must return the standard `Sunset: <date>` header and `Link: <url>; rel="successor-version"` header to alert consumer developers. The deprecation window is strictly capped at **6 months** before termination.

### 5.4 Design-Time vs. Consumption-Time Separation
To prevent documentation rot and ensure developers have access to low-level actionable details without polluting the high-level architecture registry, the enterprise mandates a strict separation of concerns for integration contracts:
- **Design-Time (Architecture Git)**: The architecture repository serves as the authoritative Single Source of Truth for the ARB and CI/CD linter. It defines logical domain boundaries and governance constraints, but must not contain low-level API payloads or execution schemas.
- **Consumption-Time (Web Developer Portal)**: Concrete integration manuals, API endpoints, JSON payloads, and SDKs must be published and consumed via automated Web Developer Portals (e.g., Swagger, ReDoc, Backstage) generated directly from code annotations.

### 5.5 Unified Visual Engine Strategy
All frontend applications must consume the unified **Scnehaux UI Platform**, structured as a strict 3-Layer Visual Engine:
1.  **Layer 1: Primitive Components (Accessible Headless Core)**
2.  **Layer 2: Design Tokens (The Design API)**
3.  **Layer 3: Styled Engine (Zero-Runtime Compiler)**
