---
doc_meta:
  id: EAD-004
  title: Enterprise Technology Architecture
  owner: Chief Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 90
  last_reviewed: 2026-05-17
---

# Enterprise Technology Architecture

## 1. Context & Business Drivers

The Enterprise Technology Architecture defines the absolute "Paved Road" for the Scnehaux Foundation. The goal is to maximize developer velocity, guarantee operational stability, and eliminate technological fragmentation. 

The primary business drivers are:
1.  **Operational Predictability**: Standardized technology stacks allow SRE and DevOps teams to maintain global observability and deterministic deployments.
2.  **Engineering Mobility**: A unified tech stack allows engineers to move fluidly between domains (e.g., HRIS to Finance) without learning entirely new ecosystems.
3.  **Strict Performance Baselines**: To guarantee enterprise-grade SLAs, the underlying technology choices must be highly performant, type-safe, and capable of extreme concurrency.

## 2. Enterprise Principles

### 2.1 The Paved Road
*   **Statement**: The standardized tech stack is opinionated, fully supported, and enforceable.
*   **Rationale**: Standardizing technology choices maximizes developer mobility and optimizes infrastructure costs.
*   **Implication**: Building within the Paved Road means you get CI/CD, Observability, and Security out-of-the-box. Deviating requires justification.

### 2.2 Exception Governance (The Escape Hatch)
*   **Statement**: The Paved Road is not a prison. Unique workloads require unique tools.
*   **Rationale**: Strict uniformity without flexibility causes shadow IT and hinders innovation for specialized workloads.
*   **Implication**: An absolute paved road without an escape hatch leads to architectural fossilization. Deviations (e.g., introducing Python for an ML workload, or Rust for extreme low-latency) are explicitly permitted **IF** justified via an approved Architecture Decision Record (ADR) and sanctioned by the Architecture Review Board (ARB).

### 2.3 Evolution Strategy
*   **Statement**: Enterprise architecture is an evolutionary trajectory, not a static monument.
*   **Rationale**: Over-indexing on past technology decisions blocks adoption of modernized patterns that reduce complexity.
*   **Implication**: Technologies and patterns will intentionally shift over time. 
    *   *Current trajectory*: Sync REST APIs -> Asynchronous Event-Driven Architectures.
    *   *Current trajectory*: Monolithic codebases -> Strict Modular Monoliths (Domain Isolation).

## 3. Strategic Architecture

The current Paved Road for the enterprise is defined as follows:

### 3.1 Backend Engineering
*   **Core Languages**: **Golang** and **Node.js (TypeScript)**.
    *   **Golang**: Standardized for high-performance, low-latency microservices, concurrent event processors, and critical path domains (e.g., Core IAM, Ledger).
    *   **Node.js (TypeScript)**: Standardized for business logic layers, high-velocity API services, and Backend-For-Frontend (BFF) aggregation.

### 3.2 Frontend Engineering
*   **Core Framework**: **React (TypeScript)**.
*   **Frameworks & Bundlers**:
    *   **Vite**: The standardized paved road for standalone Single Page Applications (SPAs) (e.g., Scnehaux IAM Dashboard).
    *   **Rspack / Rsbuild (Module Federation v1.5)**: The mandatory paved road for micro-frontend portal suites requiring dynamic composition at runtime (e.g., Scnehaux ERP Portals).
*   **State Management**: **TanStack Query** (Server State) and **Zustand** (Client State).
*   **Scnehaux UI Platform**: Consists of a strict unified **3-Layer Visual Engine**:
    *   **Layer 1: Primitive Components (Accessible Headless Core)**: Style-agnostic polymorphic elements managing semantic HTML, strict keyboard interactions, focus-trapping, and ARIA attributes to guarantee built-in WCAG 2.2 AA compliance.
    *   **Layer 2: Design Tokens (The Design API)**: A platform-agnostic multi-family token taxonomy structured as a 3-Tier engine (Tier-1 Core Primitives, Tier-2 Global Semantic Contracts across color, dimension, typography, and motion domains, Tier-3 Component overrides) to govern the visual vocabulary of the enterprise.
    *   **Layer 3: Styled Engine (Zero-Runtime CSS Compiler)**: A dual-compiler system marrying Headless Primitives (Layer 1) with Design Tokens (Layer 2) using **Panda CSS** (for build-time type-safe utility styling) and **Sass** (for static layout structures) with zero runtime performance overhead.

### 3.3 Infrastructure & Cloud Native
*   **Containerization**: **Docker**.
*   **Orchestration**: **Kubernetes (K8s)**.
*   **Infrastructure as Code (IaC)**: **Terraform**.
*   **Container Security & Image Integrity**:
    *   **Base Images**: Deployed containers must run on minimal, hardened base images. Go binaries must use `gcr.io/distroless/static-debian11` or equivalent; Node.js applications must use official Alpine (`-alpine`) or slim (`-slim`) minimal runtimes.
    *   **Vulnerability Scanning**: Automated vulnerability scanning (`Trivy` or `Snyk`) must run in CI. Pipelines must fail if a `CRITICAL` vulnerability is found in any production image.
    *   **SBOM Attestation**: Every production container image tag must be accompanied by an automated Software Bill of Materials (SBOM) generated via `Syft` or `CycloneDX` and uploaded to the artifact repository to satisfy supply-chain security baselines.

## 4. Cross-Cutting Standards

1.  **Strict SLA Enforcement**: Marketing adjectives ("fast", "scalable") are banned. The technology stack must be engineered to hit quantified enterprise targets:
    *   **Tier-0 APIs**: `P95 Latency <= 200ms`.
    *   **Tier-0 Availability**: `>= 99.95%` uptime.
    *   **Database RTO**: `< 1 Hour`.
2.  **Container Standards**: All deployed applications must be completely stateless, read configuration exclusively from environment variables, and emit structured JSON logs to `STDOUT`.
3.  **Deprecation Lifecycles**: Technologies removed from the Paved Road must be actively migrated out of production within 12 months of deprecation notice.
4.  **Kubernetes Resource Allocation Policy**:
    *   **QoS Class Enforcement**: To prevent CPU throttling and ensure high latency predictability, all Tier-0 deployments must use the **Guaranteed Quality of Service (QoS) Class** (CPU and Memory `requests` must be mathematically equal to their `limits`).
    *   **Autoscaling Thresholds**: Horizontal Pod Autoscaling (HPA) must be configured to trigger scaling events once average CPU utilization exceeds **70%** or when ingress request latency breaches target SLAs.

## 5. Decision Log

| ID | Decision | Status | Rationale |
| :--- | :--- | :--- | :--- |
| **TEC-01** | Go & Node.js Cores | Approved | Establishes Golang and Node.js (TypeScript) as the dual core pillars of Scnehaux, balancing high performance with developer velocity and API agility. |
| **TEC-02** | Explicit Exception Policy | Approved | Prevents shadow IT by providing a formal ARB pathway for necessary deviations (e.g., specialized data science workloads). |
| **TEC-03** | React + Vite for Standalone SPAs | Approved | Standardizes Vite for standalone SPAs (like IAM Dashboard) to ensure zero build overhead, seamless repo portability out of monorepos, and high-velocity developer feedback loop. |
| **TEC-04** | Federated Frontend & UI Platform | Approved | Mandates Rspack Module Federation v1.5 for federated portals, and a unified 3-layer Enterprise UI Platform (Tokens, Panda/Sass Dual-Engine, and Headless Primitives) to guarantee zero-overhead styled components, theme scalability, and unified accessibility. |
