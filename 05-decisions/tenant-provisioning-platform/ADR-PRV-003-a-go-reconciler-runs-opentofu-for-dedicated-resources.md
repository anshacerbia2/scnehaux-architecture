---
doc_meta:
  id: ADR-PRV-003
  title: A Go Reconciler Builds Pooled Tenants Directly and Runs OpenTofu for Dedicated Resources
  adr_type: foundational
  status: accepted
  created: 2026-11-04
  created_date: 2026-11-04
  created_by: Platform Engineering
  governed_by: [PAD-PLT-017]
---

# ADR-PRV-003: A Go Reconciler Builds Pooled Tenants Directly and Runs OpenTofu for Dedicated Resources

## 1. Title

The provisioning service is a Go application with its own PostgreSQL database. It runs its own reconciliation loop and keeps each request's steps in its database. It builds a pooled Tenant with direct, idempotent writes. For bridge, silo and regional Tenants each participating platform runs its own versioned OpenTofu module through a shared participant runner: plan, approval, then apply of the saved plan (`ADR-PRV-006`). The provisioning service runs no module for another platform. No workflow engine and no Kubernetes control plane are added.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                            | Approver               |
| :--------- | :------- | :----------- | :------------------------------------------------------------------- | :--------------------- |
| 2026-11-10 | accepted | foundational | Architecture, Core Platform, Platform Engineering, Security, Product | Architecture Authority |

The owner approved this decision on 10 November 2026, with the cross-platform contract of `ADR-PRV-006` and the answers recorded in `SAD-021 §15`. The development stand-ins of §5.4 were decided on 12 November 2026 (open question 5).

## 3. Context

The service must do two different kinds of work (`PAD-PLT-017 §3.4`):

- **Pooled:** write a Tenant's configuration and quota rows. Seconds, no new resource, many per day.
- **Bridge, silo, regional:** create cloud resources: a schema or database, a database instance, a per-Tenant KMS key, routing, all in a named region for regional. Minutes to tens of minutes, few per month, each approved first (`ADR-PRV-002`).

It must also be able to show a plan before it builds, apply exactly that plan, detect drift, and remove what it built (`ADR-PRV-001`, `ADR-PRV-005`).

What the estate already has: Go, PostgreSQL, Kubernetes, AWS, AWS KMS and AWS Secrets Manager are `adopt` on the tech radar. No infrastructure-as-code tool and no workflow engine is on it. `STD-GLB-009` §Internal Developer Platform (IDP) Interfaces asks that cloud resources be declared in files kept in Git and names "standard CRDs or Terraform module definitions". The development server runs Docker Compose, not Kubernetes (`STD-GLB-009` §Development Server Deployment).

## 4. Decision Drivers

- A plan an approver can read, and an apply that runs exactly that plan.
- The same path in development and production, with every difference stated.
- Few new things to operate: no new cluster or engine unless the work needs it.
- Resource declarations kept in Git and reviewed, as `STD-GLB-009` asks.
- Idempotent, resumable steps (`ADR-PRV-001 §5.3`).
- The provider can be changed later without changing the contract with Organization Control.

## 5. Decision

### 5.1 The Service

- **Go**, as Organization Control and identity-control are, with the estate's project structure (`ADR-GLB-008`).
- **Its own PostgreSQL database** holds each request's record, plan, steps, leases, approvals and audit outbox. It shares no database with Organization Control.
- **Its own loop**, as `ADR-PRV-001` describes: wake-up, resync, one leased worker per request. This is the saga orchestrator `STD-GLB-006` asks for: it keeps state, calls each step and compensates when a step fails.

### 5.2 Pooled: Direct, Idempotent Writes

A pooled request writes the Tenant's configuration record and quota limits to the service's configuration store, then runs its health checks (`PAD-PLT-017 §3.4`). Each write is an upsert keyed by `tenant_id` and the request's version. No infrastructure-as-code tool runs for a pooled Tenant, because nothing is created.

### 5.3 Bridge, Silo, Regional: OpenTofu, Plan Then Apply

- **Modules in Git, owned by each platform.** One OpenTofu module per participant and profile, in that participant's repository, versioned and released with it and changed only through a pull request. The provisioning service's repository publishes the participant runner, a Go library and image that runs a module under the contract of `ADR-PRV-006`. The module is the declaration `STD-GLB-009` asks for; the per-Tenant inputs (`tenant_id`, profile, region) come from Organization Control's request.
- **One state per Tenant per participant.** Each participant's resources for a Tenant have their own OpenTofu state, in an encrypted bucket with state locking [R1]. One Tenant's failed apply cannot touch another's state.
- **Plan saved, then applied.** The participant runs `tofu plan` with an output file in an isolated working directory and stores the saved plan and its hash. After approval it runs `tofu apply` on that saved file, which takes the actions in the saved plan and no others [R2]. If that apply fails because the infrastructure changed after planning, the participant plans again and the set is approved again (`ADR-PRV-002 §5.2`).
- **Drift.** Once a day the service sends each participant a `check` for each non-pooled Tenant, and the participant runs a plan with `-detailed-exitcode`. A non-empty plan is drift, and it raises an alert. Correcting drift is a new approved plan, never an automatic apply [R3].
- **Pinned tool.** The OpenTofu binary and each provider are pinned by version and checksum in the service image, and scanned with it (`STD-GLB-009` §Container Images).
- **Radar.** OpenTofu, an open-source tool under the Mozilla Public License v2.0 and the Linux Foundation's stewardship [R8], is on the tech radar at `trial` from 4 November 2026, owner Platform Engineering, with a trial end date of 4 May 2027.

### 5.4 Development

| Concern                  | Production                       | Development                                                                                              | Why it differs                                                        |
| :----------------------- | :------------------------------- | :------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| Pooled path              | The service, direct writes       | The same service and code, in the development stack                                                      | Does not differ                                                       |
| Contract and credentials | Registered workload, its own key | A development workload registered the same way, its own key                                              | Does not differ (`ADR-ORG-001 §5.11`)                                 |
| Bridge databases         | Managed PostgreSQL instances     | One shared PostgreSQL container, a database per bridge Tenant, made by the same modules                  | No managed database service on the development server                 |
| Silo databases           | One managed instance per Tenant  | A fixed pool of 2 PostgreSQL containers; the modules create and drop a database and its roles inside one | Same reason; and the runner never holds the Docker socket (see below) |
| Per-Tenant key           | AWS KMS key                      | An OpenBao Transit key, one per Tenant per participant (see below)                                       | No cloud account in development                                       |
| State bucket             | Encrypted cloud bucket, locked   | A local bucket stand-in or the local backend, locked                                                     | Same reason                                                           |

Phase 1 builds only the pooled path, so it needs no OpenTofu and has no stand-in.

**The stand-ins are open source; LocalStack is not used.** The owner decided on 12 November 2026 (`SAD-021 §15`, open question 5). LocalStack needs an auth token for every run since its 2026.03.0 release, its free plan is for non-commercial use, and its RDS service is in paid plans only [R6][R7]. A company development server would need a paid plan and an account outside the estate's control, and its KMS emulation would prove nothing about deletion that an open-source stand-in cannot.

- **Keys: OpenBao Transit**, an open-source secrets manager under the Mozilla Public License v2.0 [R9], whose Transit engine "handles cryptographic functions on data in-transit" [R10]. It runs pinned by digest and never in dev mode, where "All data is stored (encrypted) in-memory" and the server "will lose data on every restart" [R11]. It uses file storage and the `file` audit device, which "writes audit logs to a file" [R12], and it is reachable only on the stack's internal network, never through the tunnel.
- **One mount, one policy and one AppRole per participant.** Each participant has its own Transit mount and a policy limited to that mount. It authenticates with AppRole, the method that "allows machines or apps to authenticate with OpenBao-defined roles" [R13], and receives short-lived tokens. The root token is used for setup only and revoked after it. A participant's module deletes a key through the OpenTofu Vault provider, whose key resource needs `deletion_allowed`, which "Must be set to 'true' before terraform will be able to destroy keys" [R14]; the module sets it only at stage 3 of `ADR-PRV-005`.
- **Databases: no superuser and no Docker socket.** In each silo container the modules connect as a role with `CREATEDB` and `CREATEROLE` only. The provisioning runner never holds the Docker socket, because on the development server that is root on a host that also runs the identity stacks. That is why the silo containers are a fixed pool, defined in provisioning-control's development compose file, rather than created per Tenant; development holds at most 2 dedicated Tenants at a time.
- **What development does not show.** OpenBao has no pending-deletion window like a KMS key's 7 to 30 days, so the 30-day window of `ADR-PRV-005` is kept by provisioning-control's schedule alone, and tests shorten it by configuration. The keys are software keys, not held in hardware security modules. The local disks are not encrypted per Tenant, so deleting a development key destroys only data a participant encrypted with that key itself (`SAD-021 §10.4`).

## 6. Consequences

### Positive

- An approver sees a real plan, and what runs is what was approved.
- No new cluster or engine to operate. The service's own database holds its state.
- The modules are the reviewed declaration of every dedicated resource.
- Pooled Tenants stay fast and cheap, with no tool run.

### Negative

- The service runs a command-line tool and must manage its working directories, its output and its exit codes. A crash during `tofu apply` leaves the state locked until the lock is released (`SAD-021 §9.1`).
- One state per Tenant per participant means many state files; each participant lists and audits its own, and the service holds the index of participations.
- OpenTofu is new to the estate and needs a radar decision and a supplier entry (`ISMS-005` T26).

### Operational

- Module changes follow the service's release; a module change that affects existing Tenants is applied Tenant by Tenant, each through an approved plan.
- The daily drift run is alerted on its last success, as other scheduled jobs are.

## 7. Compliance Impact

### Related Standards and Artifacts

- `STD-GLB-009` §Internal Developer Platform (IDP) Interfaces and §Container Images.
- `STD-GLB-006` — orchestration for multi-step work.
- `ADR-GLB-008` — Go project structure.
- Tech radar: OpenTofu to `trial`; OpenBao to `trial`, development only.

### Compliance Status

Accepted. `STD-GLB-009` asks for resources declared in Git files "parsed by the IDP". This decision keeps the declarations in Git (the modules) and takes each Tenant's inputs from Organization Control at run time, because a Tenant is created by a customer journey, not by a team's change. Accepting this ADR confirms that reading. A later reading of the rule as one Git file per Tenant would need an exception ADR.

### Required Waivers

None, under the reading above.

## 8. Alternatives Considered

### Alternative A — Crossplane

**Benefits:** Kubernetes is adopted; resources are CRDs, which `STD-GLB-009` names; Crossplane reconciles continuously [R4].

**Rejected because:** it needs a Kubernetes control plane in every environment, including the development server, which has none. It applies continuously, so there is no saved plan for a person to approve before anything is created. It would also be a second reconciler of the same resources beside this service.

### Alternative B — A Workflow Engine (Temporal)

**Benefits:** durable execution: a workflow resumes after a crash, with retries and timers built in [R5].

**Rejected because:** it is a cluster with its own database to run and secure, or a hosted service [R5]. The service gets the same resumption from its own request record and idempotent steps, for a handful of steps per request. Reconsider if provisioning grows into long multi-party workflows.

### Alternative C — Cloud SDK Calls from Go for Every Profile

**Benefits:** one language, no external tool.

**Rejected because:** there is no plan to approve, and creation order, deletion and drift detection would be written by hand for every resource type.

### Alternative D — AWS CloudFormation or CDK

**Benefits:** native to the adopted cloud; change sets can be reviewed before they run.

**Rejected because:** no local equivalent for development, and routing or other resources outside AWS would need a second tool. `STD-GLB-009` already names Terraform-style modules.

### Alternative E — OpenTofu Run from CI per Tenant

**Benefits:** the usual way teams run infrastructure-as-code.

**Rejected because:** a customer journey would wait on a CI pipeline, and CI would hold the cloud credentials for every Tenant. The service holds narrower credentials (`ADR-PRV-004`).

## 9. References

### Informative

- **[R1]** OpenTofu, _Backend Type: s3_, accessed 2026-11-04. <https://opentofu.org/docs/language/settings/backends/s3/>. "The preferred one is a native S3 locking via conditional writes with `If-None-Match` header. This can be enabled by setting `use_lockfile=true`." Supports §5.3, one locked state per Tenant.
- **[R2]** OpenTofu, _Command: plan_ and _Command: apply_, accessed 2026-11-04. <https://opentofu.org/docs/cli/commands/plan/>, <https://opentofu.org/docs/cli/commands/apply/>. "The `tofu plan` command creates an execution plan, which lets you preview the changes that OpenTofu plans to make to your infrastructure"; "When you pass a saved plan file to `tofu apply`, OpenTofu takes the actions in the saved plan without prompting you for confirmation." Supports §5.3.
- **[R3]** OpenTofu, _Command: plan_, `-detailed-exitcode`, accessed 2026-11-04. <https://opentofu.org/docs/cli/commands/plan/>. "Returns a detailed exit code when the command exits"; "2 = Succeeded with non-empty diff (changes present)". Supports the drift check.
- **[R4]** Crossplane, _What's Crossplane?_ and _Install Crossplane_ (v2.4), accessed 2026-11-04. <https://docs.crossplane.io/latest/whats-crossplane/>, <https://docs.crossplane.io/latest/get-started/install/>. "Crossplane extends Kubernetes"; "Crossplane installs into an existing Kubernetes cluster, creating the Crossplane pod." Supports Alternative A.
- **[R5]** Temporal, _Understanding Temporal_, accessed 2026-11-04. <https://docs.temporal.io/evaluate/understanding-temporal>. "Temporal runs your application code as a Durable Execution"; "Run the Temporal Service yourself, or use Temporal Cloud and skip operating the database, the shards, and multi-region failover." Supports Alternative B.
- **[R6]** LocalStack, _Announcing the LocalStack for AWS 2026.03.0 Release_, 23 March 2026, accessed 2026-11-04. <https://blog.localstack.cloud/localstack-for-aws-release-2026-03-0/>. "As of version 2026.03.0, an auth token or CI auth token is required to start LocalStack for AWS." Supports §5.4.
- **[R7]** LocalStack, _Key Management Service (KMS)_ and _Relational Database Service (RDS)_, accessed 2026-11-04. <https://docs.localstack.cloud/aws/services/kms/>, <https://docs.localstack.cloud/aws/services/rds/>. KMS: "Available from the Hobby plan"; RDS: "Available from the Base plan." The Hobby plan is for non-commercial use (<https://docs.localstack.cloud/aws/licensing/>). Supports §5.4.
- **[R8]** OpenTofu, home page and repository, accessed 2026-11-04. <https://opentofu.org/>, <https://github.com/opentofu/opentofu>. "OpenTofu is a reliable, flexible, community-driven infrastructure as code tool under the Linux Foundation's stewardship"; the repository is licensed under the Mozilla Public License v2.0. Supports the radar entry.
- **[R9]** OpenBao, repository, accessed 2026-11-12. <https://github.com/openbao/openbao>. "OpenBao is a software solution to manage, store, and distribute sensitive data including secrets, certificates, and keys"; licensed MPL-2.0. Supports §5.4 and the radar entry.
- **[R10]** OpenBao, _Transit secrets engine_, accessed 2026-11-12. <https://openbao.org/docs/secrets/transit/>. "The transit secrets engine handles cryptographic functions on data in-transit." Supports §5.4.
- **[R11]** OpenBao, _Dev server_, accessed 2026-11-12. <https://openbao.org/docs/concepts/dev-server/>. "All data is stored (encrypted) in-memory"; "It is insecure and will lose data on every restart (since it stores data in-memory)"; "Never, ever, ever run a "dev" mode server in production." Supports §5.4, no dev mode.
- **[R12]** OpenBao, _File audit device_, accessed 2026-11-12. <https://openbao.org/docs/audit/file/>. "The `file` audit device writes audit logs to a file." Supports §5.4 and the destruction evidence of `SAD-021 §10.4`.
- **[R13]** OpenBao, _AppRole auth method_, accessed 2026-11-12. <https://openbao.org/docs/auth/approle/>. "The approle auth method allows machines or apps to authenticate with OpenBao-defined roles"; "This auth method is oriented to automated workflows (machines and services)". Supports §5.4.
- **[R14]** Vault provider, _vault_transit_secret_backend_key_, accessed 2026-11-12. <https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/transit_secret_backend_key>. `deletion_allowed`: "Specifies if the keyring is allowed to be deleted. Must be set to 'true' before terraform will be able to destroy keys." Supports §5.4.
- **[R15]** OpenBao, _Static key seal_, accessed 2026-11-12. <https://openbao.org/docs/configuration/seal/static/>. "Static key seal configures OpenBao to use static keys provided alongside the configuration file"; "Carefully evaluate use of Static Key Auto Unseal to see if its use meets the desired security properties." Supports SAD-021 §10.4.
- **[R16]** OpenBao, _status command_, accessed 2026-11-12. <https://openbao.org/docs/commands/status/>. "The exit code reflects the seal status": "0 - unsealed", "1 - error", "2 - sealed". Supports SAD-021 §10.4.
