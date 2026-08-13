---
doc_meta:
  id: STD-GLB-009
  title: Enterprise Platform Engineering Standard
  owner: Principal Platform Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-05-22
---

# Enterprise Platform Engineering Standard (STD-GLB-009)

---

## 1. Objective & Scope

This standard defines the mandatory architectures, self-service interfaces, Golden Path templates, and integration contracts for the Internal Developer Platform (IDP) within the Scnehaux enterprise.

It covers Developer Portals, resource provisioning mechanisms, service catalogs, and infrastructure orchestration APIs. These rules ensure consistency, eliminate setup toil, and enforce security policies at the platform layer.

---

## 2. Design Principles

Platform engineering enforces self-service infrastructure with guardrails. Developer platforms must provide golden paths that reduce cognitive overhead while maintaining security, compliance, and operational baseline requirements.

## 3. Normative Rules

### Developer Self-Service Interface (Backstage Portal)

To coordinate software discovery and developer onboarding:

- **Centralized Software Catalog**: Every production service, micro-frontend, library, and data pipeline must register a `catalog-info.yaml` file in its root directory. Services that are not cataloged are blocked from deployment.
- **Service Catalog Metadata**: The registration metadata must declare:
  - _Identity_: Service name, description, and unique system namespace.
  - _Ownership_: The designated engineering group and primary domain (e.g. `payroll-team`).
  - _Context_: API definitions (OpenAPI/AsyncAPI) and runtime dependencies.
- **Lifecycle Indicators**: Services must list their operational lifecycle state (Experimental, Production, or Deprecated) within the catalog.

---

### Golden Path Provisioning Templates

Platform engineering must provide standardized software templates ("Golden Paths") to automate project initialization:

- **Unified Template Registries**: Teams creating new services must use the platform portal's software templates. Creating services from scratch or manual copy-pasting is prohibited.
- **Service Boilerplate Standards**:
  - _Directory Layout_: Repository structures must follow the standardized structure (e.g. `/cmd`, `/internal`, `/pkg` for Go services).
  - _Baseline Integrations_: Templates must include pre-configured OpenTelemetry libraries, Prometheus `/metrics` endpoints, and JSON logger middlewares.
  - _CI/CD Configuration_: Service initializations must generate standard GitHub Actions or GitLab CI files containing active linter checks, test stages, and dependency-auditing steps.

---

### Internal Developer Platform (IDP) Interfaces

To decouple infrastructure requests from manual operations support tickets:

- **Infrastructure Provisioning**: Cloud resources (databases, queues, caches, storage buckets) must be provisioned via GitOps declarative files parsed by the IDP. Direct resource creation through cloud consoles is prohibited.
- **Self-Service Custom Resource Definitions (CRDs)**: Teams must request infrastructure using standard CRDs or Terraform module definitions registered in the repository.
- **Compute Namespace Boundaries**:
  - Services must deploy into isolated Kubernetes namespaces.
  - Namespaces must carry annotations denoting the service tier (Tier 1, Tier 2, or Tier 3) and data classification tier (Tier 1 to Tier 4) to apply correct network and scheduling constraints automatically.

---

### Security & Access Governance

- **Least Privilege Access**: Developer access to infrastructure environments must use temporary credentials (e.g. via AWS IAM Identity Center or HashiCorp Vault). Permanent credentials (IAM user access keys) are prohibited in developer environments.
- **Environment Isolation**: Production environments must operate under distinct network partitions and credentials. Local developer tools are prohibited from binding to production datastores or queues.
- **Audit Logging**: Every platform engineering provision, catalog modification, or state change must emit a structured audit log stored in the immutable security archive.

---

## 4. Exceptions

None. All platform engineering standards apply universally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

1. **Catalog Verification checks**: CI pipelines must run validation checks against the service's `catalog-info.yaml` file on every branch merge. Builds without valid ownership or lifecycle indicators must be blocked.
2. **Infrastructure Audits**: Automated monitors must continuously verify active cloud resources against the GitOps declaration repository. Undeclared resources must be flagged, quarantined, and terminated within `48 hours`.
3. **Exception Waivers**: Deviations from the platform architecture or deployment paths require an approved ADR signed by both the Platform Architect and the Enterprise Security Board.
