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

# Enterprise Application Architecture

## 1. Context & Business Drivers

Modern distributed architecture dictates that integration surfaces and security boundaries are inherently the same thing. The Enterprise Application Architecture defines how disparate systems securely communicate, authenticate, and propagate context across the Scnehaux ecosystem. 

The primary business drivers are:
1.  **Isolation at Scale**: Ensuring that multi-tenant traffic and inter-domain communications never leak across strict security boundaries.
2.  **Unified Ecosystem**: Guaranteeing that whether a user interacts with IAM, Finance, or HRIS, the application behavior, error handling, and identity validation remain absolutely consistent.
3.  **Traceability**: Every request traversing the enterprise must be observable, attributable, and auditable.

## 2. Enterprise Principles

### 2.1 Identity as the Perimeter (Zero Trust)
*   **Statement**: The network is inherently hostile.
*   **Rationale**: Hardened firewalls are insufficient; lateral movement within a compromised network must be prevented.
*   **Implication**: IP whitelisting is insufficient. Every request must carry cryptographic proof of identity (Service or User).

### 2.2 Standardized Interoperability
*   **Statement**: Integration complexity is a liability.
*   **Rationale**: Homogeneous integration patterns reduce operational overhead and simplify client/SRE onboarding.
*   **Implication**: All inter-service communication must utilize the enterprise "Paved Road" protocols (REST/JSON for synchronous, NATS/Kafka for asynchronous). Proprietary or esoteric protocols are forbidden.

### 2.3 Fail-Closed Security
*   **Statement**: In the event of an ambiguity or failure in the authorization chain, the system must deny access.
*   **Rationale**: Preserving default-deny configurations ensures security guarantees are maintained even under degradations.
*   **Implication**: Services must default to HTTP 403/401 when downstream IAM checks timeout or fail.

## 3. Strategic Architecture

### 3.1 The API Gateway Layer
All external traffic must ingress through a centralized API Gateway. The Gateway is responsible for:
*   SSL/TLS termination.
*   Initial token validation (JWKS).
*   Global Rate Limiting and WAF (Web Application Firewall) enforcement.
*   Routing to downstream domain services.

### 3.2 Service-to-Service Integration (The Mesh)
Direct internal communication between microservices must bypass the external Gateway and utilize internal routing.
*   **Protocol**: REST (HTTP/1.1 or HTTP/2).
*   **Security**: Mutual TLS (mTLS) is mandatory for all internal hops.
*   **Mesh Infrastructure**: The enterprise standardizes on a **Service Mesh Infrastructure** using **sidecar proxies** running in every application pod. The mesh is responsible for enforcing strict mTLS, traffic routing, retries, and distributed tracing injection (W3C Trace Context). Applications must not implement mTLS or tracing instrumentation inside their business logic layers; these concerns are delegated entirely to the sidecars.

### 3.3 Asynchronous Integration
*   Event-driven architectures decouple domains. Integration via events must use the **Outbox Pattern** to guarantee that database commits and event dispatches are transactionally bound.

### 3.4 Frontend & Scnehaux UI Platform Architecture

#### 3.4.1 UI Compilation & Composition Patterns
The enterprise UI architecture supports two first-class frontend patterns based on organizational and deployment requirements:
*   **Standalone Applications**: Mandated for focused, high-security, single-viewport portals (e.g., the Scnehaux IAM Dashboard). These applications are compiled as fully isolated Single Page Applications (SPAs).
*   **Federated Portal Suites**: Enforced when independent deployability and runtime dynamic composition of multiple business domains are required (e.g., the Scnehaux ERP portal integrating HRIS and Finance micro-frontends). This pattern uses **federated runtime composition engines**.

#### 3.4.2 Unified Visual Engine (Scnehaux UI Platform)
Regardless of the compilation pattern, all frontend applications must consume the unified **Scnehaux UI Platform**, which is structured as a strict **3-Layer Visual Engine**:
1.  **Layer 1: Primitive Components (Accessible Headless Core)**: Pure, style-agnostic, and polymorphic elements that manage strict accessibility (WCAG 2.2 AA), keyboard navigation, focus-trapping, and ARIA handling, serving as the logical skeleton.
2.  **Layer 2: Design Tokens (The Design API)**: A platform-agnostic multi-family token taxonomy structured as a 3-Tier engine (Tier-1 Core Primitives, Tier-2 Global Semantic Contracts across color, dimension, typography, and motion domains, Tier-3 Component overrides) compiled to CSS custom properties (`--ds-*`).
3.  **Layer 3: Styled Engine (Zero-Runtime Compiler)**: Marries the Headless Primitives (Layer 1) with the Design Tokens (Layer 2) by generating compile-time atomic utility classes (via zero-runtime styled components compilers) and static layout themes (via static stylesheets preprocessors) with zero runtime performance overhead.

#### 3.4.3 Frontend Platform Governance
*   **Technology Stack & Layered Architecture Standard**: Frontend application repositories must organize their internal source code directories, boundary abstractions, and network data layers to satisfy the [Enterprise Frontend Technology Stack & Layered Architecture Standard (STD-E005)](../05-standards/STD-E005-frontend-technology-stack-layered-architecture-standard.md).
*   **React Development Standard**: Component lifecycles, hook structures, and rendering optimizations must comply with the [Enterprise React Development Standard (STD-E010)](../05-standards/STD-E010-react-development-standard.md).
*   **Runtime, Security & Observability Standard**: Build-time budgets, supply chain dependency checks, environment variable separation, and telemetry tracing must comply with the [Enterprise Frontend Runtime, Security & Observability Standard (STD-E008)](../05-standards/STD-E008-frontend-runtime-observability-standard.md).
*   **Micro Frontend Federation Standard**: Integration contracts, shared dependency versions, and EventBus communications must comply with the [Enterprise Micro Frontend Federation Standard (STD-E011)](../05-standards/STD-E011-micro-frontend-federation-standard.md).
*   **Frontend Styling Standard**: Interface styling conventions, responsive layouts, and z-index context scales must adhere to the [Enterprise Frontend Styling Standard (STD-E009)](../05-standards/STD-E009-frontend-styling-standard.md).
*   **UI Platform Primitive Components Standard**: Headless component foundations, accessibility hooks, and slot composition APIs must comply with the [Enterprise UI Platform Primitive Components Standard (STD-E012)](../05-standards/STD-E012-ui-platform-primitive-components-standard.md).
*   **UI Platform Design Tokens Standard**: Design token hierarchies, custom properties pipelines, and themes mapping must comply with the [Enterprise UI Platform Design Tokens Standard (STD-E013)](../05-standards/STD-E013-ui-platform-design-tokens-standard.md).
*   **UI Platform Styled Components & Compilation Standard**: Zero-runtime styling engines, compilation configurations, and class prefixing parameters must comply with the [Enterprise UI Platform Styled Components & Compilation Standard (STD-E014)](../05-standards/STD-E014-ui-platform-styled-components-standard.md).
*   **Encapsulation Constraint**: For federated environments to prevent visual style collisions on shared DOM environments, micro-frontends must not use global CSS selectors. Style boundaries must use unique CSS Modules or unique domain-specific class prefixes (e.g., `scnx-hris-`, `scnx-fin-`), ensuring they do not collide with each other or with the core platform prefix (`scnx-`).

### 3.5 API Versioning & Lifecycle Protocol
To manage API changes without breaking client integrations:
*   **Major Versioning**: Major breaking API releases must utilize path-based versioning (e.g., `/api/v1/resource`, `/api/v2/resource`).
*   **Minor Versioning**: Non-breaking updates or minor feature variations must use header-based media type content negotiation (e.g., `Accept: application/vnd.scnehaux.v1.1+json`).
*   **Deprecation Policy**: Deprecated endpoints must return the standard `Sunset: <date>` header and `Link: <url>; rel="successor-version"` header to alert consumer developers. The deprecation window is strictly capped at **6 months** before termination.

## 4. Cross-Cutting Standards

1.  **Tenant Context Propagation**: All requests associated with a tenant must explicitly pass the `Scnehaux-Account` header. Services must validate this header against the authenticated token claims.
2.  **Distributed Tracing**: Every request must generate or propagate a `X-Trace-Id` header. This ID must be injected into all application logs.
3.  **Standardized Error Responses**: All HTTP APIs must return errors following the RFC 7807 (Problem Details for HTTP APIs) standard or the exact proprietary Scnehaux Error Domain structure. Silent failures are prohibited.

## 5. Decision Log

| ID | Decision | Status | Rationale |
| :--- | :--- | :--- | :--- |
| **APP-01** | Mandatory mTLS | Approved | Enforces Zero Trust internally; perimeter defense is obsolete. |
| **APP-02** | Scnehaux-Account Header | Approved | Standardizes multi-tenant context propagation across all polyglot microservices without relying on payload inspection. |
| **APP-03** | Unified UI & Presentation Platform | Approved | Mandates a unified 3-layer visual engine (Design Tokens, Styled Engine, and Accessible Primitives) under federated micro-frontend composition runtimes to prevent visual collision and ensure strict WCAG 2.2 AA accessibility. |
