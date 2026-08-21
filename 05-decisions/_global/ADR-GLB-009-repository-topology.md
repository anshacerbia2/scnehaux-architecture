---
doc_meta:
  id: ADR-GLB-009
  title: One Repository per Deployable Unit for the Identity and Organization Foundation
  adr_type: foundational
  status: proposed
  created: 2026-08-12
  created_date: 2026-08-12
  created_by: Architecture Authority
  governed_by: [GDC-000, EAD-002, EAD-005]
---

# ADR-GLB-009: One Repository per Deployable Unit for the Identity and Organization Foundation

## 1. Title

Repository Topology for the Identity and Organization Foundation: One Repository per Deployable Unit, Plus One for Shared Substrate

## 2. Status

| Date | Status | ADR Type | Reviewers | Approver |
| :-- | :-- | :-- | :-- | :-- |
| 2026-08-12 | proposed | foundational | Architecture, Core Platform, Identity | Architecture Authority — pending |

This decision **ratifies a topology already implemented**. Six repositories exist and carry designs and code. The drivers recorded in Section 4 are derived from the statements in those repositories' own README files rather than from a prior written decision, which is the gap this ADR closes. The decision owner confirms or corrects Section 4 at ratification.

## 3. Context

The identity and organization foundation is realized by six repositories. Their responsibilities and the systems they belong to are:

| Repository | Role | System |
| :-- | :-- | :-- |
| `identity-kernel` | Keycloak extensions, realm configuration, login theme, image build | SAD-001 |
| `identity-control` | Identity Control Service; holds the Keycloak Admin credential | SAD-001 |
| `organization-control` | Organization, Tenant, Workspace, and Membership authority | SAD-004 |
| `foundation-platform` | Shared Go substrate: outbox, event envelope, idempotency, problem details | library, no system |
| `identity-experience` | Account security and identity administration interface with its BFF | SAD-002 |
| `organization-experience` | Organization administration interface with its BFF | SAD-012 |

Three properties of this set make repository boundaries a governance concern rather than a matter of convenience.

**Three toolchains, not one.** `identity-kernel` builds a container image and Java extensions against the Keycloak SPI. The two control services and the shared library are Go. The two experiences are TypeScript. A single repository would carry three build systems, three dependency graphs, three vulnerability-scanning configurations, and three release conventions in one pipeline.

**Three release cadences, not one.** The kernel follows the vendor's release and security cadence, and each upgrade carries a database migration with restore-based rollback. The control services follow feature delivery. The experiences follow interface delivery. Coupling them to one repository couples them to one release decision.

**A library consumed by tag cannot live inside a consumer.** `foundation-platform` is depended upon by two systems that must upgrade deliberately rather than by rebuild, which ADR-GLB-010 §5.6 requires of any shared package. A module inside one consumer's repository cannot be versioned independently of that consumer.

A fourth property is specific to this estate. `identity-control` holds the Keycloak Admin credential, which is the most privileged secret in the estate. Its separation from `organization-control` is a process boundary decided on security grounds, and a repository boundary allows contributor access and deployment credentials to be scoped to match.

## 4. Decision Drivers

- Match each pipeline to one toolchain rather than three.
- Allow each deployable to release on its own cadence, particularly the vendor-driven kernel.
- Permit the shared library to be versioned and consumed by tag, as ADR-GLB-010 §5.6 requires.
- Allow contributor access and deployment credentials to be scoped per deployable, reinforcing the credential separation that SAD-001 and SAD-004 rely on.
- Keep vulnerability scanning, dependency updates, and supply-chain provenance attributable to one artifact.
- Avoid a repository whose test suite duration is set by the slowest unrelated component.

## 5. Decision

### 5.1 Topology

The identity and organization foundation uses **one repository per deployable unit, plus one repository for the shared Go substrate**. The six repositories in Section 3 are the complete set. Adding a repository requires a decision recorded under §5.5.

### 5.2 Repository Is Not System

A repository boundary does not create a system boundary. System boundaries come from SADs, and the mapping is not one-to-one:

```text
SAD-001 Identity Runtime      → identity-kernel + identity-control
SAD-004 Organization Control  → organization-control
SAD-002 Identity Experience   → identity-experience
SAD-012 Organization Experience → organization-experience
foundation-platform           → no SAD; not deployed, holds no state
```

A design document names its parent system in `parent_sad`, never its repository. `foundation-platform` carries no SAD because EAD-002 §6.1 requires one for deployed systems and it is not deployed.

### 5.3 Cross-Repository Interaction

- Cross-system state moves only through **versioned domain events** on the broker.
- Where a consumer requires an authoritative answer a projection cannot supply, it calls the provider's **published HTTP contract** — the same contract available to every other consumer. No repository receives a privileged interface.
- `foundation-platform` is consumed by **tagged version**. A branch dependency, a local path replacement outside development, or a commit-pinned dependency in a released artifact is prohibited.
- No repository imports another repository's internal packages.

### 5.4 Contract Change Sequence

A change to an event schema or to the shared substrate crosses repositories and cannot be one atomic commit. The ordered sequence is:

1. Change and release `foundation-platform` at a new version, retaining compatibility with the current consumers.
2. Upgrade each consumer independently and deliberately.
3. Remove the compatibility shim only after every consumer reports the new version.

A change that requires all consumers to upgrade simultaneously is a design defect, not a coordination problem, because it makes one repository's release gate another's.

### 5.5 Consolidation and Further Split

Two repositories are consolidated when **all** of the following hold: they share a toolchain, they share a release cadence, neither holds a credential the other must not reach, and their combined test duration does not delay either.

A repository is split further when its deployables acquire different accountable owners, different release cadences that block each other, or a credential boundary between them.

Neither move is taken on preference. Both are recorded as an amendment to this decision.

## 6. Consequences

### Positive

- Each pipeline serves one language, so build, test, lint, and vulnerability scanning are matched to the artifact rather than to the largest common set.
- The kernel upgrades on the vendor's cadence without holding back feature delivery in the control services.
- The shared library is versioned independently, which is what allows deliberate upgrade instead of upgrade by rebuild.
- Contributor access and deployment credentials are scoped per repository, so the Keycloak Admin credential is reachable from one repository's pipeline.
- Supply-chain provenance and dependency history are attributable to one deployable.

### Negative

- Six pipelines, six dependency-update streams, and six sets of repository configuration for one team.
- No atomic change across repositories. A contract change is a sequence, and the sequence can be executed incorrectly.
- A developer working across the boundary works across checkouts.
- Duplication of repository-level configuration, which drifts unless templated.

### Operational

- Each repository carries its own CODEOWNERS, branch protection, and deployment credentials.
- Event schemas live in `foundation-platform/contracts/events` until the enterprise Schema Registry required by STD-GLB-004 is operational, after which the location changes and this rule does not.
- Repository-level configuration is templated so that a change to a shared convention is applied deliberately rather than copied.

## 7. Compliance Impact

### Related Standards and Artifacts

- EAD-002 — logical domain, software system, and deployable are distinct concepts; §6.1 requires a SAD for deployed systems.
- EAD-005 — simplest sufficient runtime and delivery principles.
- ADR-GLB-008 — Go project structure and layer enforcement, applied within each Go repository.
- ADR-GLB-010 — placement of cross-cutting mechanics; §5.6 requires the shared package to be independently versioned, which §5.3 here realizes.
- STD-GLB-004 — event-driven standard and the Schema Registry that will later own event schemas.
- SAD-001, SAD-002, SAD-004, SAD-012 — the systems these repositories realize.

### Compliance Status

Proposed, and describes the implemented state. No repository requires modification on ratification.

### Required Waivers

None. A seventh repository, a consolidation, or a branch-based dependency on the shared library requires an amendment to this decision.

## 8. Alternatives Considered

### Alternative A — Single Monorepo for the Whole Foundation

One repository holding the kernel image build, both Go services, the shared library, and both interfaces.

**Benefits:** atomic cross-cutting change, one pipeline configuration, one dependency-update stream, a single checkout for developers working across the boundary.

**Rejected because:** it places three toolchains in one pipeline and couples three release cadences to one decision, including a vendor-driven kernel upgrade that carries a database migration. It also removes the ability to consume the shared substrate by tag, because a module inside the repository that contains its consumers cannot be versioned independently of them.

### Alternative B — Two Repositories, One per Domain

`identity` and `organization`, each holding its own kernel assets, service, and interface.

**Benefits:** two pipelines rather than six, and the domain boundary is visible in the repository layout.

**Rejected because:** it merges the Java kernel image build, a Go service, and a TypeScript interface inside each repository, which reproduces Alternative A's toolchain problem at half the scale without removing it. The shared library still has no home.

### Alternative C — One Repository per System

Four repositories aligned to SAD-001, SAD-002, SAD-004, and SAD-012, with the library placed in one of them.

**Benefits:** repository and system map one-to-one, which is simpler to explain.

**Rejected because:** SAD-001 spans a vendor container image and a Go service whose release cadences and toolchains differ, which is the case this topology exists to separate. Placing the library inside a system's repository also makes its version dependent on that system's release.

### Alternative D — Vendor the Shared Substrate into Each Consumer

Copy the substrate into both control services and keep them aligned by review.

**Rejected because:** the outbox dispatcher's poll interval and claim behaviour are terms in the revocation enforcement delay that STD-IAM-001 §3.4 defines. Two copies produce two enforcement intervals while both services report compliance, and no test inside either service detects the difference. ADR-GLB-010 §5.6 records this as the condition under which extraction is required rather than optional.
