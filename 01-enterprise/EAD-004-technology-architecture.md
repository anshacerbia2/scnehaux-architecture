---
doc_meta:
  id: EAD-004
  title: Enterprise Technology Architecture
  owner: Chief Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-000]
  review_cycle_days: 90
  last_reviewed: 2026-05-17
---

# Enterprise Technology Architecture (EAD-004)

---

## 1. Cloud Strategy

The enterprise dictates a cloud-native approach to maximize developer velocity, guarantee operational stability, and eliminate technological fragmentation. 

### 1.1 Infrastructure as Code
All cloud resources and deployments must be strictly managed using Infrastructure as Code (IaC) via **Terraform**. Manual modifications to cloud environments (ClickOps) are prohibited.

### 1.2 Kubernetes Native
All deployments must be containerized (**Docker**) and orchestrated via **Kubernetes (K8s)**. Applications must be completely stateless and read configuration exclusively from environment variables to ensure portability.

## 2. Security Principles

### 2.1 Container Security & Image Integrity
- **Base Images**: Deployed containers must run on minimal, hardened base images. Go binaries must use `gcr.io/distroless/static-debian11` or equivalent; Node.js applications must use official Alpine (`-alpine`) or slim (`-slim`) minimal runtimes.
- **Vulnerability Scanning**: Automated vulnerability scanning must run in CI. Pipelines must fail if a `CRITICAL` vulnerability is found in any production image.
- **SBOM Attestation**: Every production container image tag must be accompanied by an automated Software Bill of Materials (SBOM) uploaded to the artifact repository to satisfy supply-chain security baselines.

## 3. Observability Principles

Strict observability is required to guarantee enterprise-grade SLAs.
- **Structured Logging**: Applications must emit structured JSON logs to `STDOUT`.
- **SLA Metrics**: The technology stack must be engineered to hit quantified enterprise targets. Marketing adjectives ("fast", "scalable") are banned.
  - **Tier-0 APIs**: `P95 Latency <= 200ms`.
  - **Tier-0 Availability**: `>= 99.95%` uptime.
  - **Database RTO**: `< 1 Hour`.

## 4. Platform Strategy

### 4.1 The Paved Road
The standardized tech stack is opinionated, fully supported, and enforceable. Standardizing technology choices maximizes developer mobility and optimizes infrastructure costs. Building within the Paved Road means you get CI/CD, Observability, and Security out-of-the-box. Deviating requires justification.

### 4.2 Exception Governance (The Escape Hatch)
The Paved Road is not a prison. Unique workloads require unique tools. An absolute paved road without an escape hatch leads to architectural fossilization. Deviations (e.g., introducing Python for an ML workload, or Rust for extreme low-latency) are explicitly permitted **IF** justified via an approved Architecture Decision Record (ADR) and sanctioned by the Architecture Review Board (ARB).

## 5. Technology Principles

> Principles set **direction**; the binding, versioned specifications live in the **Standards (STD) layer** and are referenced here rather than duplicated, to preserve a single source of truth.

- **Opinionated Paved Road**: a curated, fully-supported default stack maximizes developer mobility and optimizes infrastructure cost; deviation requires an approved ADR (see §4.2).
- **Backend direction**: a compiled, concurrency-first language for low-latency, critical-path domains (e.g. Core IAM, Ledger); a TypeScript runtime for business-logic and Backend-For-Frontend aggregation. *Binding stack: see the backend STDs.*
- **Frontend direction**: a single standardized component model, build toolchain, and state strategy across all surfaces. *Binding stack: see [`STD-GLB-FE-*`](../02-standards/_global/frontend/).*
- **Workload isolation**: critical (Tier-0) workloads receive guaranteed, predictable resourcing and explicit autoscaling targets; the concrete QoS classes and HPA thresholds are defined in the platform STD, not here.

## 6. Technology Radar

The enterprise architecture is an evolutionary trajectory: technologies and patterns move through a managed lifecycle of **Assess → Trial → Adopt → Hold**, governed by [GDC-004](../00-governance/GDC-004-tech-lifecycle.md).

The authoritative radar is maintained as machine-readable policy in [`tech-radar.yaml`](./tech-radar.yaml) — the linter enforces it directly: a document that adopts a technology on `Hold` fails CI. This section intentionally does **not** re-list the entries, to avoid drifting from that single source of truth.
