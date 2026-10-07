---
doc_meta:
  id: STD-GLB-009
  title: Enterprise Platform Engineering Standard
  owner: Principal Platform Architect
  version: 1.5.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-10-07
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

Three documents carry it, each at its own level (1.5.0):

- **This section** is the rule: the `deploy/dev` skeleton every repository follows, and why.
- **[The development server runbook](../../deploy/dev/README.md)** is the procedure across repositories: the order of the stacks, from an empty host to a wired server, updating, resetting and restoring, and the pitfalls met on the real server. Each step points to the repository README section that owns the detail.
- **[The imam-station environment page](../../deploy/dev/imam-station.md)** holds one server's facts: its network, ports, subnets, tunnel and local files. It holds no secret.

**Layout.**

| Path                                       | Contents                                                                                                                                                                        |
| :----------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Dockerfile` at the repository root        | Multi-stage, every base image pinned by digest. Target `migrate`: the schema pipeline and every one-off admin binary. Target `service`: the service alone, distroless, non-root |
| `deploy/dev/compose.yaml`                  | Project `name: scnehaux-<repository>-dev`. Services `postgres`, `migrate` and the service itself, plus one-off tasks                                                            |
| `deploy/dev/migrate.sh`                    | The schema pipeline, idempotent: databases, the pre stage, `atlas migrate apply`, the post stage, the login roles, and assertions of the privilege shape                        |
| `deploy/dev/.env.example`                  | Every setting the stack reads, with placeholders and no credential. `.env` is gitignored                                                                                        |
| `deploy/dev/compose.override.example.yaml` | What a server MAY add in its own uncommitted `compose.override.yaml`: subnet pins, a loopback database port. Rule 4 below                                                       |
| `deploy/dev/<verb>-<noun>.sh`              | The operator's one-time steps on the server, such as making a key or registering a client. Rule 2 below                                                                         |
| `deploy/dev/keys/`                         | Private keys, gitignored. Made on the server by identity-kernel's `new-client-key.sh`; only the public JWK leaves it                                                            |
| `deploy/dev/README.md`                     | The ten sections of rule 3 below, in that order                                                                                                                                 |

**The skeleton (1.5.0).** Five repositories wrote their `deploy/dev` one at a time, and each said the same things under other headings, or left them out: how to back the database up, what never to run, what to do when a step fails. An operator then had to read all five to find out. The rules below make every `deploy/dev` answer the same questions in the same place. The reusable workflow `deploy-dev-skeleton.yml` (§5, item 5) checks the parts a machine can check.

1. **Two kinds of repository.**
   - A _server-deployed service_ (identity-kernel, identity-control, organization-control) runs its own compose stack on the server. Its `deploy/dev` MUST hold `README.md`, `compose.yaml`, `.env.example` and `compose.override.example.yaml`, and `migrate.sh` when `compose.yaml` has a `migrate` service.
   - A _laptop-run application_ (identity-experience, organization-experience) runs on a developer's machine and runs no stack on the server. Its `deploy/dev` MUST hold `README.md`, plus any script the server's operator runs for it, such as identity-experience's `create-bff-client.sh`.
2. **Scripts are named `<verb>-<noun>.sh` and refuse to overwrite.** A script in `deploy/dev` runs from its own directory, reads `.env` for what it needs, and never prints a secret. A script that makes something (a key, a client, a key ring) MUST refuse when its output already exists, because replacing a key is a rotation, a step of its own. A script that sets a value MUST be idempotent and say so in its header. identity-kernel's `new-client-key.sh` and `create-apply-client.sh` refuse, and its `set-client-key.sh` and `tunnel-admin.sh` converge. Names already in use stay. A new script follows the form.
3. **`README.md` has ten sections, in this order**, each a level-2 heading with exactly this text. A section that does not apply still exists and says so in one line, with the reason. Other level-2 sections, such as a move between versions, MAY sit between them.

   | Heading                       | Holds                                                                                                                                   |
   | :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
   | `## What runs`                | Each service of the stack, its image, and what it does. Any deviation from this section, with its reason                                |
   | `## Before you start`         | The stacks that must already run, the host's tools (Docker, Compose v2, `pwsh` where a script needs it), and what is needed from others |
   | `## First start`              | From an empty `deploy/dev` to a ready service: `.env`, the one-time scripts in order, `docker compose up -d --build`, the readiness URL |
   | `## Updating`                 | `git pull`, then `docker compose up -d --build`, and the logs to read afterwards                                                        |
   | `## One-off tasks`            | Each profiled task: how to run it and when                                                                                              |
   | `## Wiring to other services` | The networks joined and created, and the procedure, as a script, that connects this service to the others                               |
   | `## Keys`                     | Each key: who makes it, where it lives, who owns the file, how it is installed and rotated                                              |
   | `## Backups`                  | Rule 9                                                                                                                                  |
   | `## Never do`                 | The commands that destroy state or break another stack, each with what it would break                                                   |
   | `## Troubleshooting`          | Each failure met on a server, by its symptom, with the cause and the fix                                                                |

4. **A local override is an example, never a commit.** Compose reads "two files, a compose.yaml and an optional compose.override.yaml file" by default [R23]. A server's own changes, such as subnet pins where Docker's default ranges overlap the host's networks or a loopback port for its database, go in an uncommitted `compose.override.yaml`. `compose.override.example.yaml` shows them, commented, so the next server copies rather than rediscovers them. A stack whose `.env` sets `COMPOSE_FILE` (identity-kernel in tunnel mode) lists its local file there [R23], and is then run with plain `docker compose`. A `-f` on the command line replaces that list, local file included.
5. **Names.** The project is `name: scnehaux-<repository>-dev`. "Compose uses a project name to isolate environments from each other" [R16], so two stacks never share a container or a volume. The network other stacks join is `scnehaux-<repository>-api`, created by its own stack and carrying its service alone. A network's `name` "is used as is and is not scoped with the project name" [R22], which is what lets another stack declare it `external`. identity-kernel keeps `scnehaux-identity-dev` and `scnehaux-identity-api`, both named before this rule: its volumes belong to the project, so a renamed project starts with an empty database, and two stacks join the network by its name. Its README states both.
6. **Host ports bind to `127.0.0.1` only.** "Publishing container ports is insecure by default" [R21]: a port published without an address is published "to all host addresses (0.0.0.0 and [::])" [R21]. With `127.0.0.1`, "only the Docker host can access the published container port" [R21]. What leaves the host goes through the dev tunnel, port by port (rule 10). The one exception is identity-kernel's DNS-name mode, whose proxy is the public listener on 80 and 443. The tunnel mode, which the development server runs, binds that proxy to loopback as well.
7. **Go modules come through `GOPROXY`, a build argument filled from `.env`.** Every `build:` whose Dockerfile declares `ARG GOPROXY` passes `GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}`. "args define build arguments, that is Dockerfile ARG values" [R24]. The default is Go's own default [R25]. A server whose network intercepts the module proxy sets `GOPROXY=direct` in `.env`, which "instructs the go command to download modules from version control repositories where they’re developed instead of using a proxy" [R25]. Integrity does not depend on the proxy either way: `go.sum` and the checksum database verify every module, which "makes untrusted proxies possible since they can’t serve the wrong code without it going unnoticed" [R25]. A build argument in `.env`, rather than a local override, means the setting survives every `git pull` and is set once per server.
8. **Every setting `.env` holds is passed by name.** "A container's environment is not set until there's an explicit entry in the service configuration to make this happen" [R17]. `.env` holds "variables that should be made available for interpolation" [R18]. Its values "don't result in a variable in the container by itself, but in conjunction with either the environment or env_file attribute" [R19]. So a setting the README tells an operator to put in `.env` is listed under the service's `environment:` in `compose.yaml`, with its default. If it is missing there, `.env` changes nothing and nothing says so. Every variable `.env.example` names MUST be read by a compose file or by a script.
9. **Backups.** A stack that owns a database MUST state in `## Backups` a daily backup to storage outside the Docker volume, made by `pg_dump` in the custom format, and how it is restored:
   - Each database is dumped with `pg_dump -Fc`. It "makes consistent backups even if the database is being used concurrently" [R26]. A custom-format dump "must be restored with pg_restore" [R27].
   - The cluster's roles are dumped with `pg_dumpall --globals-only`, because `pg_dump` "does not dump information about roles or tablespaces" [R27], and "Before restoring an SQL dump, all the users who own objects or were granted permissions on objects in the dumped database must already exist" [R27].
   - `.env` and `keys/` are copied beside the dumps. The dumps hold role password hashes and the copies hold keys, so the backup is kept like `.env`: readable by the operator alone.
   - The README says, in `## Backups` and `## Never do`, that `docker compose down -v` deletes the database. The flag removes "named volumes declared in the "volumes" section of the Compose file" [R20]. A volume is a store whose "contents exist outside the lifecycle of a given container" [R28]. It is not outside the project's lifecycle, so a backup made into the volume is deleted with it.
10. **The tunnel is persistent, opened port by port, and watched.** The server is reached through one persistent Microsoft dev tunnel. `devtunnel host` without a tunnel ID creates "a new temporary dev tunnel ... that is deleted once the connection is closed" [R29], and with it the issuer. Anonymous access is granted per port, and only on the public issuer's port. "Allowing anonymous access to a dev tunnel means anyone on the internet is able to connect to your local server" [R29]. The host process runs as a systemd user service with lingering enabled, so that "a user manager is spawned for the user at boot and kept around after logouts" [R30]. A timer runs a watchdog that requests the public discovery URL and restarts the host when it stops answering. `Restart=on-failure` restarts a process that "exits with a non-zero exit code" [R30]. The tunnel host has been seen to lose its relay while its process stays alive, which no exit status reports.
11. **Request header values are plain ASCII**, as STD-GLB-001 §Request Header Values requires. Every `X-Administrative-Reason` a README or script sends is ASCII.
12. **`deploy/` holds environments and nothing else.** A repository's `deploy/` MUST contain one directory per environment, named `dev`, `staging` or `prod`, and no other entry. `dev` is the only one today, and the others are added when those environments exist. An artifact that every environment uses is not specific to an environment, so it lives outside `deploy/`. Prometheus alert rules, for example, live in `observability/alerts/`, so `deploy/alerts/` (organization-control, foundation-reference) moves there. An operator then finds everything one environment needs under its own directory, and nothing that belongs to another. This repository's own `deploy/dev/` holds the cross-repository runbook and the pages of each development server, and no stack.

**Compose.**

- Configuration comes from the environment, through `.env` [R1]. A required setting is `${NAME:?…}`, so a missing one stops `up` with its name: compose resolves it to the "value of VAR if set and non-empty, otherwise exit with error" [R5]. A setting that only a profiled task reads is `${NAME:-}`, and the task refuses it empty. Compose interpolates every service, profiled or not, so a required one would stop every `up`.
- Each service owns its database: its own `postgres`, on a network named `internal` that no other stack joins (EAD-003). Its data lives in a named volume. `docker compose down -v` destroys a service's authority data and is never part of a procedure, except the deliberate reset from zero the runbook describes, which starts with a backup (rule 9).
- `migrate` is a one-shot service (`restart: "no"`) that waits for `postgres` with `condition: service_healthy`. The service waits for it with `condition: service_completed_successfully`, which compose defines as "a dependency is expected to run to successful completion before starting a dependent service" [R3].
- **One-off admin tasks are services behind a profile named after the task** (a ceremony, a first grant, a projection bootstrap). Compose enables a profiled service only on request: "Services without a `profiles` attribute are always enabled" [R2]. They "run against a release, using the same codebase and config as any process run against that release" [R4]. So a task declares no build of its own and uses the `migrate` service's image by name, and `docker compose up -d --build` rebuilds every task with the release. A task with its own build is rebuilt only when someone remembers to.
- A service other stacks call is on a network named `scnehaux-<repository>-api` that carries it alone, created by its own stack. A stack that calls it joins that network as `external`. Stacks start in dependency order: identity-kernel, identity-control, organization-control.
- A service publishes its port on `127.0.0.1` only (rule 6 above). Public exposure goes through identity-kernel's proxy or tunnel.

**Why these two rules, and what was rejected.**

- _A task's own settings._ The application validates its configuration and refuses a missing value by name, so compose passes `${NAME:-}` and does not duplicate the check. Two alternatives were rejected. A per-task `env_file` with `required: false` keeps the setting out of interpolation ("When `required` is set to `false` and the `.env` file is missing, Compose silently ignores the entry" [R6]), but every task gains a file of its own. A separate compose file for tasks changes the command per task, which is what this road exists to prevent.
- _One artifact per release._ Build and run are separate stages, and "every release should always have a unique release ID" [R7]. Every process of a release, the service, the migration and each task, runs the artifact built for it. On the development server that artifact is the image `docker compose up -d --build` builds from the checkout, tagged by name, and the tasks reuse it. This is a development shortcut. The production path builds each image once in CI, tags it with the commit that produced it, and every process and job of the release pulls that tag. A task can then never run an image older than its release, which a locally built image cannot guarantee if someone runs a task before `up`.

**Commands.** The same in every repository, run in `deploy/dev`:

| Purpose                      | Command                                         |
| :--------------------------- | :---------------------------------------------- |
| First start and every update | `git pull`, then `docker compose up -d --build` |
| A one-off task               | `docker compose run --rm <task> <flags>`        |
| Logs                         | `docker compose logs -f <service>`              |

A service whose browser half runs on a developer's machine (identity-experience's BFF) registers its client on the server with a script in `deploy/dev` and runs no stack there.

**A procedure step is a script, and CI runs it (1.3.0).** A step that changes a server's state, such as an adoption, a registration, a ceremony or a move between versions, MUST be a script in the repository, and the repository's `deploy-dev` job MUST run it against the stack it stands up. `deploy/dev/README.md` names the script and what it checks. It does not carry a request body for an operator to retype.

- _Why._ A step done by hand is not done the same way twice: "any action performed by a human or humans hundreds of times won't be performed the same way each time", and "This inevitable lack of consistency leads to mistakes, oversights, issues with data quality, and, yes, reliability problems" [R8]. A step that only a reader runs also goes stale unseen. Go keeps its documentation true by running it: examples "are compiled (and optionally executed) as part of a package's test suite", and "Having executable documentation for a package guarantees that the information will not go out of date as the API changes" [R9].
- _What it found._ identity-control's README declared the BFF's adoption with the wrong audience class. Nothing ran it, so the error stayed until the declaration was turned into a script (2026-10-05).
- _Tradeoff._ A script needs a stack in CI that can stand in for the server, and some state, such as a person's second factor, is only on the server. A step CI cannot reach is stated as such in the README, with the reason.

### Container Images (1.4.0)

Every Scnehaux service ships as an OCI image, and an image carries every vulnerability of every layer in it. These rules apply to each image a repository builds (each `Dockerfile` target), and to each image it runs without building, such as an upstream image it pins or a database a `deploy/dev/compose.yaml` names.

**Rules.**

1. **Pinned by digest.** An image a repository builds from or runs MUST be referenced by digest, with the tag it was resolved from beside it as a comment. A tag can be moved to other bytes. A digest names the bytes.
2. **Minimal and unprivileged.** A service image MUST run as a non-root user and SHOULD be distroless. NIST: "images should be configured to run as non-privileged users", and base layers should come "from minimalistic technologies ... to reduce attack surface areas" [R11].
3. **Scanned in CI, on every change and every day.** Every image in scope MUST be scanned for known vulnerabilities in the repository's CI on every pull request and push to `main`, and on a daily schedule. NIST asks for scanning "from the beginning of the build process, to whatever registries the organization is using, to runtime", covering "all layers of the image, not just the base layer" [R10]. The daily run exists because a new advisory changes an unchanged image's findings.
4. **A gate on what can be fixed.** The scan MUST fail the build on any vulnerability of severity High or Critical that has a fixed version. This is NIST's quality gate: "a rule in the build process to prevent the progression of images that include vulnerabilities with Common Vulnerability Scoring System (CVSS) [18] ratings above a selected threshold" [R10]. The scan reports every other finding without failing, because nothing in the repository can act on a vulnerability that has no fix. A finding in an upstream image, such as the identity kernel's Keycloak, is fixed by moving the pin to a release that fixes it.
5. **Exceptions are written down and expire.** A finding the gate fails on, and that cannot be fixed now, MAY be ignored by a rule in the repository's `.grype.yaml`. The rule MUST name the vulnerability and the package. Its `reason` MUST begin with `review-by YYYY-MM-DD:`, at most 90 days ahead, and say why the finding does not apply or what it waits for. CI MUST fail when a rule's review date has passed. An ignored finding is then either fixed or decided again.
6. **The scanner is pinned too.** The scanner MUST run from an image pinned by digest, or from an action pinned by its full commit SHA. Never from a tag, and never from a script fetched at run time. GitHub: "Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release" [R12]. On 2026-03-19, an attacker "force-pushed 76 of 77 version tags in aquasecurity/trivy-action and all 7 tags in aquasecurity/setup-trivy", and later published malicious images of the scanner itself (CVE-2026-33634). A pipeline that named a tag ran the attacker's code with its CI secrets. The advisory's own mitigation is to "Pin GitHub Actions to full, immutable commit SHA hashes, don't use mutable version tags" [R13].

**The scanner.** Grype, run from `anchore/grype` pinned by digest:

- `--fail-on high` exits non-zero "if it found vulnerabilities at or above the specified severity" [R14].
- `--only-fixed` "filters out vulnerabilities with these fix states: `not-fixed`, `wont-fix`, `unknown`" [R14]. The gate runs with it, and a second, report-only pass runs without it.
- Ignore rules live in `.grype.yaml` and carry a `reason` field [R14] [R15].

Trivy meets the same rules. One scanner is chosen so every repository has one ignore format and one gate. Trivy's distribution was the one compromised in March 2026 [R13], but what protects a pipeline is rule 6, pinning, not the choice of vendor. A Go repository keeps `govulncheck` as well. It reads the source, and reports only vulnerable code the program can reach, which an image scan cannot.

**Why not a gate on Medium, or on unfixed findings.** A gate that fails on what nobody can fix gets ignored as a whole, and the 90-day exceptions would become permanent. NIST leaves the threshold to the organization ("a selected threshold") [R10]. High with a fix is the line every repository here can always meet, by upgrading.

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
4. **Image scanning (1.4.0)**: Each repository's CI runs the §Container Images scan on every change and daily, fails on a fixable High or Critical vulnerability, and fails on an expired ignore rule.
5. **The `deploy/dev` skeleton (1.5.0)**: Each service and application repository's CI calls this repository's reusable workflow `.github/workflows/deploy-dev-skeleton.yml` with its kind, `service` or `application`. It runs `06-fitness-function/scripts/deploy-dev-skeleton-check.py`, whose header lists every check. For both kinds: every entry directly under `deploy/` is `dev`, `staging` or `prod` (rule 12); `README.md` exists and carries the ten headings of rule 3 in order, none empty. For a service, also: the files of rule 1; the project name and api network of rule 5; every host port of every committed compose file bound to loopback (rule 6); `migrate` gating the service with `service_completed_successfully`; no profiled task with a build of its own; the `GOPROXY` build argument of rule 7; every `.env.example` variable read by a compose file or a script (rule 8); and `.env` and `keys/` ignored by git. A name that differs from rule 5's, or a public port, is passed as an input, and the README MUST state the name. Script naming, refusals, and the content of each section are left to review.

## 6. References

- **[R1]** The Twelve-Factor App, _III. Config_, accessed 2026-10-03. <https://12factor.net/config>. "Store config in the environment"; "The twelve-factor app stores config in environment variables."
- **[R2]** Docker, _Using profiles with Compose_, accessed 2026-10-03. <https://docs.docker.com/compose/how-tos/profiles/>. "Services without a `profiles` attribute are always enabled."
- **[R3]** Docker, _Control startup order_, accessed 2026-10-03. <https://docs.docker.com/compose/how-tos/startup-order/>. `service_healthy`: "a dependency is expected to be "healthy", which is defined with `healthcheck`, before starting a dependent service"; `service_completed_successfully`: "a dependency is expected to run to successful completion before starting a dependent service."
- **[R4]** The Twelve-Factor App, _XII. Admin processes_, accessed 2026-10-03. <https://12factor.net/admin-processes>. "Run admin/management tasks as one-off processes"; "One-off admin processes should be run in an identical environment as the regular long-running processes of the app. They run against a release, using the same codebase and config as any process run against that release."
- **[R5]** Docker, _Interpolation_, accessed 2026-10-03. <https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/>. "${VAR:?error} -> value of VAR if set and non-empty, otherwise exit with error"; "${VAR:-default} -> value of VAR if set and non-empty, otherwise default."
- **[R6]** Docker, _Set environment variables within your container's environment_, accessed 2026-10-03. <https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/>. "As of Docker Compose version 2.24.0, you can set your `.env` file, defined by the `env_file` attribute, to be optional by using the `required` field. When `required` is set to `false` and the `.env` file is missing, Compose silently ignores the entry."
- **[R7]** The Twelve-Factor App, _V. Build, release, run_, accessed 2026-10-03. <https://12factor.net/build-release-run>. "Strictly separate build and run stages"; "Every release should always have a unique release ID, such as a timestamp of the release (such as `2011-04-06-20:32:17`) or an incrementing number (such as `v100`)."
- **[R8]** Google, _Site Reliability Engineering_, ch. 7, "The Evolution of Automation at Google", accessed 2026-10-05. <https://sre.google/sre-book/automation-at-google/>. "any action performed by a human or humans hundreds of times won't be performed the same way each time"; "This inevitable lack of consistency leads to mistakes, oversights, issues with data quality, and, yes, reliability problems."
- **[R9]** The Go Blog, _Testable Examples in Go_, accessed 2026-10-05. <https://go.dev/blog/examples>. "Examples are compiled (and optionally executed) as part of a package's test suite"; "Having executable documentation for a package guarantees that the information will not go out of date as the API changes."
- **[R10]** NIST, _SP 800-190, Application Container Security Guide_, §4.1.1 "Image vulnerabilities", 2017, accessed 2026-10-07. <https://doi.org/10.6028/NIST.SP.800-190>. "Integration with the entire lifecycle of images, from the beginning of the build process, to whatever registries the organization is using, to runtime"; "Visibility into vulnerabilities at all layers of the image, not just the base layer of the image but also application frameworks and custom software"; "organizations should be able to configure a rule in the build process to prevent the progression of images that include vulnerabilities with Common Vulnerability Scoring System (CVSS) [18] ratings above a selected threshold."
- **[R11]** NIST, _SP 800-190_, §4.1.2 "Image configuration defects", accessed 2026-10-07. <https://doi.org/10.6028/NIST.SP.800-190>. "For example, images should be configured to run as non-privileged users"; "Use of base layers from trusted sources only, frequent updates of base layers, and selection of base layers from minimalistic technologies like Alpine Linux and Windows Nano Server to reduce attack surface areas."
- **[R12]** GitHub, _Secure use reference_, accessed 2026-10-07. <https://docs.github.com/en/actions/reference/security/secure-use>. "Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release. Pinning to a particular SHA helps mitigate the risk of a bad actor adding a backdoor to the action's repository, as they would need to generate a SHA-1 collision for a valid Git object payload."
- **[R13]** Aqua Security, _Trivy ecosystem supply chain temporarily compromised_, GHSA-69fq-xp46-6x23 / CVE-2026-33634, accessed 2026-10-07. <https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23>. Compromised: "trivy-action" "Any tags prior except 0.35.0 (0.0.1 – 0.34.2)", "setup-trivy" "All 7 existing tags (v0.2.0 – v0.2.6)", and "trivy container images v0.69.5 and v0.69.6 distributed via Docker Hub"; mitigation: "Pin GitHub Actions to full, immutable commit SHA hashes, don't use mutable version tags." Microsoft, _Guidance for detecting, investigating, and defending against the Trivy supply chain compromise_, 2026-03-24. <https://www.microsoft.com/en-us/security/blog/2026/03/24/detecting-investigating-defending-against-trivy-supply-chain-compromise/>. "the attacker force-pushed 76 of 77 version tags in aquasecurity/trivy-action and all 7 tags in aquasecurity/setup-trivy"; "Pin GitHub Actions to commit SHA rather than version tags (e.g., @v1), as tags can be force-modified by attackers."
- **[R14]** Anchore, _Grype: Filter results_, accessed 2026-10-07. <https://oss.anchore.com/docs/guides/vulnerability/filter-results/>. "When scanning completes, Grype exits with code 2 if it found vulnerabilities at or above the specified severity"; `--only-fixed` "filters out vulnerabilities with these fix states: `not-fixed`, `wont-fix`, `unknown`"; ignore rules in `.grype.yaml` match on `vulnerability`, `package` and `fix-state`, and "When you combine multiple criteria in a rule, all criteria must match for the rule to apply."
- **[R15]** Anchore, Grype v0.120.1 source, `grype/match/ignore.go`, accessed 2026-10-07. <https://github.com/anchore/grype/blob/v0.120.1/grype/match/ignore.go>. The `IgnoreRule` struct carries a `Reason` field, read from the key `reason`.
- **[R16]** Docker, _Specify a project name_, accessed 2026-10-07. <https://docs.docker.com/compose/how-tos/project-name/>. "Compose uses a project name to isolate environments from each other"; precedence, highest first: "The -p command line flag", "The COMPOSE_PROJECT_NAME environment variable", "The top-level name: attribute in your Compose file."
- **[R17]** Docker, _Set environment variables within your container's environment_, accessed 2026-10-07. <https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/>. "A container's environment is not set until there's an explicit entry in the service configuration to make this happen."
- **[R18]** Docker, _Set, use, and manage variables in a Compose file with interpolation_, accessed 2026-10-07. <https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/>. "An .env file in Docker Compose is a text file used to define variables that should be made available for interpolation when running docker compose up."
- **[R19]** Docker, _Environment variables precedence_, accessed 2026-10-07. <https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/>. "The columns Host OS environment and .env file is listed only for illustration purposes. In reality, they don't result in a variable in the container by itself, but in conjunction with either the environment or env_file attribute."
- **[R20]** Docker, _docker compose down_, accessed 2026-10-07. <https://docs.docker.com/reference/cli/docker/compose/down/>. "-v, --volumes: Remove named volumes declared in the "volumes" section of the Compose file and anonymous volumes attached to containers"; "Networks and volumes defined as external are never removed."
- **[R21]** Docker, _Port publishing and mapping_, accessed 2026-10-07. <https://docs.docker.com/engine/network/port-publishing/>. "Publishing container ports is insecure by default. Meaning, when you publish a container's ports it becomes available not only to the Docker host, but to the outside world as well"; "If you include the localhost IP address (127.0.0.1, or ::1) with the publish flag, only the Docker host can access the published container port"; "By default, when a container's ports are mapped without any specific host address, the Docker daemon publishes ports to all host addresses (0.0.0.0 and [::])."
- **[R22]** Docker, _Compose file reference: Define and manage networks_, accessed 2026-10-07. <https://docs.docker.com/reference/compose-file/networks/>. "name sets a custom name for the network"; "The name is used as is and is not scoped with the project name"; "external specifies that this network’s lifecycle is maintained outside of that of the application."
- **[R23]** Docker, _Merge Compose files_, accessed 2026-10-07. <https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/>. "By default, Compose reads two files, a compose.yaml and an optional compose.override.yaml file"; "To use multiple override files, or an override file with a different name, you can either use the pre-defined COMPOSE_FILE environment variable, or use the -f option to specify the list of files." Docker, _Configure pre-defined environment variables in Docker Compose_, <https://docs.docker.com/compose/how-tos/environment-variables/envvars/>. `COMPOSE_FILE`: "Specifies the path to a Compose file. Specifying multiple Compose files is supported."
- **[R24]** Docker, _Compose Build Specification_, accessed 2026-10-07. <https://docs.docker.com/reference/compose-file/build/>. "args define build arguments, that is Dockerfile ARG values."
- **[R25]** The Go Programming Language, _Go Modules Reference_, accessed 2026-10-07. <https://go.dev/ref/mod>. "The default value of GOPROXY is: https://proxy.golang.org,direct"; "The keyword direct instructs the go command to download modules from version control repositories where they’re developed instead of using a proxy"; the checksum database "makes untrusted proxies possible since they can’t serve the wrong code without it going unnoticed."
- **[R26]** PostgreSQL 17 Documentation, _pg_dump_, accessed 2026-10-07. <https://www.postgresql.org/docs/17/app-pgdump.html>. "pg_dump is a utility for backing up a PostgreSQL database. It makes consistent backups even if the database is being used concurrently. pg_dump does not block other users accessing the database (readers or writers)"; `-Fc`: "Output a custom-format archive suitable for input into pg_restore."
- **[R27]** PostgreSQL 17 Documentation, _25.1. SQL Dump_, accessed 2026-10-07. <https://www.postgresql.org/docs/17/backup-dump.html>. "Before restoring an SQL dump, all the users who own objects or were granted permissions on objects in the dumped database must already exist"; "pg_dump dumps only a single database at a time, and it does not dump information about roles or tablespaces (because those are cluster-wide rather than per-database)"; "Cluster-wide data can be dumped alone using the pg_dumpall --globals-only option"; "A custom-format dump is not a script for psql, but instead must be restored with pg_restore."
- **[R28]** Docker, _Volumes_, accessed 2026-10-07. <https://docs.docker.com/engine/storage/volumes/>. "A volume's contents exist outside the lifecycle of a given container."
- **[R29]** Microsoft, _Dev tunnels command-line commands_, accessed 2026-10-07. <https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/cli-commands>. `devtunnel host`: "If a dev tunnel ID isn't specified, a new temporary dev tunnel is created that is deleted once the connection is closed"; `devtunnel create`: "Create a persistent dev tunnel"; "Allowing anonymous access to a dev tunnel means anyone on the internet is able to connect to your local server, if they can guess the dev tunnel ID"; `devtunnel access create TUNNELID --port 3000 --anonymous`: "Enable anonymous client access on port 3000."
- **[R30]** systemd, _loginctl_, accessed 2026-10-07. <https://www.freedesktop.org/software/systemd/man/latest/loginctl.html>. `enable-linger`: "If enabled for a specific user, a user manager is spawned for the user at boot and kept around after logouts. This allows users who are not logged in to run long-running services." systemd, _systemd.service_, <https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html>. "If set to on-failure, the service will be restarted when the process exits with a non-zero exit code, is terminated by a signal". systemd, _systemd.timer_, <https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html>. `OnUnitActiveSec=`: "Defines a timer relative to when the unit the timer unit is activating was last activated."
