---
doc_meta:
  id: STD-GLB-009
  title: Enterprise Platform Engineering Standard
  owner: Principal Platform Architect
  version: 1.1.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-03
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

### Development Server Deployment

The shared development server runs every Scnehaux service the same way, so an operator who has deployed one has deployed them all. This is the paved road. A repository whose service runs on the server SHOULD follow it, and a deviation is stated in that repository's `deploy/dev/README.md`.

**Layout.**

| Path                                | Contents                                                                                                                                                                        |
| :---------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Dockerfile` at the repository root | Multi-stage, every base image pinned by digest. Target `migrate`: the schema pipeline and every one-off admin binary. Target `service`: the service alone, distroless, non-root |
| `deploy/dev/compose.yaml`           | Project `name: scnehaux-<repository>-dev`. Services `postgres`, `migrate` and the service itself, plus one-off tasks                                                            |
| `deploy/dev/migrate.sh`             | The schema pipeline, idempotent: databases, the pre stage, `atlas migrate apply`, the post stage, the login roles, and assertions of the privilege shape                        |
| `deploy/dev/.env.example`           | Every setting the stack reads, with placeholders and no credential. `.env` is gitignored                                                                                        |
| `deploy/dev/keys/`                  | Private keys, gitignored. Made on the server by identity-kernel's `new-client-key.sh`; only the public JWK leaves it                                                            |
| `deploy/dev/README.md`              | In this order: what the stack is, before you start, first start, updating, one-off tasks, wiring to other services, and moves between versions                                  |

**Compose.**

- Configuration comes from the environment, through `.env` [R1]. A required setting is `${NAME:?…}`, so a missing one stops `up` with its name.
- Each service owns its database: its own `postgres`, on a network named `internal` that no other stack joins (EAD-003). Its data lives in a named volume. `docker compose down -v` destroys a service's authority data and is never part of a procedure.
- `migrate` is a one-shot service (`restart: "no"`) that waits for `postgres` with `condition: service_healthy`. The service waits for it with `condition: service_completed_successfully`, which compose defines as "a dependency is expected to run to successful completion before starting a dependent service" [R3].
- **One-off admin tasks are services behind a profile named after the task** (a ceremony, a first grant, a projection bootstrap). Compose enables a profiled service only on request: "Services without a `profiles` attribute are always enabled" [R2]. They "run against a release, using the same codebase and config as any process run against that release" [R4]. So a task declares no build of its own and uses the `migrate` service's image by name, and `docker compose up -d --build` rebuilds every task with the release. A task with its own build is rebuilt only when someone remembers to.
- A service other stacks call is on a network named `scnehaux-<repository>-api` that carries it alone, created by its own stack. A stack that calls it joins that network as `external`. Stacks start in dependency order: identity-kernel, identity-control, organization-control.
- A service publishes its port on `127.0.0.1` only. Public exposure goes through identity-kernel's proxy or tunnel.

**Commands.** The same in every repository, run in `deploy/dev`:

| Purpose                      | Command                                         |
| :--------------------------- | :---------------------------------------------- |
| First start and every update | `git pull`, then `docker compose up -d --build` |
| A one-off task               | `docker compose run --rm <task> <flags>`        |
| Logs                         | `docker compose logs -f <service>`              |

A service whose browser half runs on a developer's machine (identity-experience's BFF) registers its client on the server with a script in `deploy/dev` and runs no stack there.

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

## 6. References

- **[R1]** The Twelve-Factor App, _III. Config_, accessed 2026-10-03. <https://12factor.net/config>. "Store config in the environment"; "The twelve-factor app stores config in environment variables."
- **[R2]** Docker, _Using profiles with Compose_, accessed 2026-10-03. <https://docs.docker.com/compose/how-tos/profiles/>. "Services without a `profiles` attribute are always enabled."
- **[R3]** Docker, _Control startup order_, accessed 2026-10-03. <https://docs.docker.com/compose/how-tos/startup-order/>. `service_healthy`: "a dependency is expected to be "healthy", which is defined with `healthcheck`, before starting a dependent service"; `service_completed_successfully`: "a dependency is expected to run to successful completion before starting a dependent service."
- **[R4]** The Twelve-Factor App, _XII. Admin processes_, accessed 2026-10-03. <https://12factor.net/admin-processes>. "Run admin/management tasks as one-off processes"; "One-off admin processes should be run in an identical environment as the regular long-running processes of the app. They run against a release, using the same codebase and config as any process run against that release."
