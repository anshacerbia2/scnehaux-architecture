---
doc_meta:
  id: ADR-GLB-009
  title: Repository Boundaries Follow Change, Release, Security, and Ownership Cohesion
  adr_type: foundational
  status: proposed
  created: 2026-08-12
  created_date: 2026-08-12
  created_by: Architecture Authority
  governed_by: [GDC-000, EAD-002, EAD-005]
---

# ADR-GLB-009: Repository Boundaries Follow Change, Release, Security, and Ownership Cohesion

## 1. Title

Repository Topology: Align Repository Boundaries to Change, Release, Security, and Ownership Cohesion Rather Than Deployable Count

## 2. Status

| Date | Status | ADR Type | Reviewers | Approver |
| :-- | :-- | :-- | :-- | :-- |
| 2026-08-12 | proposed | foundational | Architecture, Core Platform, Identity | Architecture Authority — pending |
| 2026-08-25 | proposed | foundational | Architecture, Platform Engineering, UI Platform, Notification, Scheduling | Architecture Authority — pending |

The original proposal scoped this ADR to the Identity and Organization foundation and proposed one repository per deployable unit. It never reached `accepted`, therefore it carried no architectural authority. Before ratification, the proposal is rebaselined into an enterprise repository-boundary decision that accounts for both legitimate polyrepo cases and legitimate platform-scoped monorepos.

## 3. Context

Scnehaux explicitly separates **Capability**, **Platform**, **System**, **Deployable**, **Repository**, and **Team**. These concepts are related but are not required to map one-to-one.

Repository topology is therefore not derivable from a simple rule such as:

```text
one Platform = one repository
one SAD = one repository
one deployable = one repository
```

A repository is a software-delivery and collaboration boundary. Its correct placement depends on the forces that make code safer and cheaper to change:

- how frequently code changes together
- whether changes benefit from atomic commits
- whether deployables must release independently
- whether toolchains and dependency graphs are compatible
- whether contributor access or deployment credentials require isolation
- whether one accountable team owns the lifecycle
- whether CI/test blast radius remains bounded
- whether a package is a reusable platform dependency or consumer-specific code

Two current estates demonstrate why one universal mechanical mapping is incorrect.

### 3.1 Identity and Organization Foundation

The Identity and Organization foundation includes heterogeneous deployables with materially different security and release characteristics, including vendor-coupled identity kernel assets, Go control services, Experience applications, and shared substrate. Some of these boundaries justify separate repositories because of privileged credentials, toolchain differences, vendor cadence, and independent lifecycle.

### 3.2 Notification and Scheduling Platforms

Notification and Scheduling each have two approved systems:

```text
PAD-PLT-005 Notification Platform
├─ SAD-005 Notification Runtime
└─ SAD-015 Notification Experience

PAD-PLT-011 Scheduling Platform
├─ SAD-013 Scheduling Runtime
└─ SAD-014 Scheduling Experience
```

Within each platform, Runtime and Experience have distinct deployable lifecycles, but they share one platform owner, evolve against tightly related contracts, and benefit from atomic contract changes and one local development surface. Independent deployment does not require independent repositories.

### 3.3 UI Platform as a Shared Producer

SAD-003 defines the UI Platform as reusable build-time packages consumed by downstream Experience applications. A consumer application is not part of the UI Platform merely because it imports UI Platform packages.

The currently available development source may be consumed locally while the package is evolving. That development convenience must not redefine ownership or repository boundaries.

## 4. Decision Drivers

- Preserve `Repository != Deployable != System != Platform`
- Optimize for change cohesion rather than organizational fashion
- Permit atomic Runtime/Experience contract evolution where the same platform owns both sides
- Preserve independent build, release, and deployment of deployables inside a shared repository
- Isolate repositories when privileged credentials, contributor access, vendor cadence, or incompatible toolchains require it
- Keep reusable platform packages outside consumer application ownership
- Avoid premature polyrepo coordination tax
- Avoid giant-monorepo blast radius and unrelated ownership coupling
- Keep local development productive without making local path dependencies valid production dependencies
- Make future extraction evolutionary and evidence-driven

## 5. Decision

### 5.1 Enterprise Repository Boundary Rule

Scnehaux **MUST NOT** derive repository boundaries mechanically from the number of Platforms, SADs, deployables, or teams.

A repository boundary is chosen from **change, release, security, toolchain, ownership, and operational cohesion**.

Multiple independently deployable applications **MAY** share one repository when all of the following are true:

- they belong to the same platform or tightly cohesive product boundary
- one accountable team or closely coupled team set owns their evolution
- atomic source changes materially reduce contract coordination risk
- repository access does not violate a credential or contributor-isolation boundary
- toolchains can coexist without creating disproportionate CI or dependency-management cost
- each deployable can still build, version, release, scale, and roll back independently

A deployable **SHOULD** move to a separate repository when one or more of the following becomes material:

- contributor access must be isolated
- deployment credentials or privileged build secrets must be isolated
- vendor-driven or security-driven release cadence is independent
- accountable ownership diverges
- toolchain or dependency lifecycle creates sustained pipeline interference
- repository test/build blast radius materially slows unrelated delivery
- the deployable becomes a reusable producer consumed by multiple independent platforms and requires an independent release lifecycle

Repository consolidation or extraction is an evolutionary architecture action, not an architectural failure.

### 5.2 Notification Platform Topology

The Notification Platform uses **one platform-scoped repository** containing independently deployable Runtime and Experience applications.

```text
scnehaux-notification-platform/
├─ apps/
│  ├─ runtime/          # SAD-005
│  └─ experience/       # SAD-015
├─ packages/
│  └─ contracts/        # platform-internal source contracts/generated clients where justified
├─ deploy/
└─ ...
```

Binding rules:

- Runtime and Experience remain separate deployables
- Runtime remains Notification authority
- Experience remains a browser-facing Go BFF + compiled React application
- Experience may depend only on published Runtime contracts, never Runtime internal packages
- a shared repository does not permit direct database, broker, secret-store, or provider coupling from Experience
- CI must support path-aware validation while preserving repository-wide architecture and contract gates
- release/version identifiers are per deployable unless a later decision explicitly adopts lockstep releases

### 5.3 Scheduling Platform Topology

The Scheduling Platform uses **one platform-scoped repository** containing independently deployable Runtime and Experience applications.

```text
scnehaux-scheduling-platform/
├─ apps/
│  ├─ runtime/          # SAD-013
│  └─ experience/       # SAD-014
├─ packages/
│  └─ contracts/        # platform-internal source contracts/generated clients where justified
├─ deploy/
└─ ...
```

Binding rules:

- Runtime and Experience remain separate deployables
- Runtime remains Scheduling authority
- Experience remains a browser-facing Go BFF + compiled React application
- Experience may depend only on published Runtime contracts, never Runtime internal packages
- recurrence, occurrence, dispatch, replay, and quota authority remain behind Runtime contracts
- CI must support independent deployable build/release while retaining repository-wide contract gates
- release/version identifiers are per deployable unless a later decision explicitly adopts lockstep releases

### 5.4 UI Platform and Consumer Experience Boundary

Notification Experience and Scheduling Experience **MUST NOT** be placed inside the UI Platform repository merely because they consume UI Platform packages.

The dependency direction is:

```text
UI Platform packages
        ↓
Notification Experience
Scheduling Experience
other consumer Experiences
```

not:

```text
UI Platform repository
├─ UI Platform packages
├─ Notification application
├─ Scheduling application
└─ every future product Experience
```

The UI Platform is a reusable producer. Consumer Experiences remain owned by their respective platforms.

The current local source location of the UI Platform is an implementation detail and may be transitional. This ADR does not require immediate extraction of UI Platform packages into a new repository.

### 5.5 Local Development and Released Dependency Policy

During local development, a consumer repository **MAY** resolve an actively developed UI Platform package through an explicit local-development mechanism such as:

- a local filesystem dependency
- `pnpm link`
- a local package proxy or equivalent developer-tooling mechanism
- a workspace reference when producer and consumer legitimately share the same workspace

These mechanisms are development-only conveniences.

A released or production-built consumer artifact **MUST NOT** depend on:

- an absolute developer filesystem path
- a branch-floating dependency
- an unversioned local symlink
- another repository's internal source tree

Production/released consumers must resolve an immutable, versioned package artifact through the governed package-distribution mechanism when that release path is operational.

### 5.6 Repository Co-location Does Not Relax Architecture Boundaries

Source co-location does not create privileged architectural access.

Within a platform-scoped repository:

- no deployable imports another deployable's internal packages
- cross-system calls use governed published contracts
- Runtime persistence remains private to Runtime
- broker topology remains private to the owning Runtime
- Experience cannot bypass Runtime authorization because source code is nearby
- architecture fitness functions must enforce forbidden dependency directions

The repository is a collaboration boundary, not a domain-authority boundary.

### 5.7 Identity and Organization Remain a Valid Polyrepo Case

This ADR does not force existing Identity and Organization repositories into a monorepo.

Their heterogeneous toolchains, privileged credential boundaries, vendor/security cadence, and independent lifecycle remain valid reasons for repository separation.

Future consolidation is permitted only when the criteria in §5.1 are satisfied and the governing decision is updated according to GDC-010.

### 5.8 Evolution Triggers

Notification or Scheduling Runtime/Experience may be split into separate repositories later when evidence shows a sustained need, including:

- distinct accountable teams
- materially independent release cadence
- incompatible build/security pipelines
- contributor-access isolation
- CI blast radius that materially degrades delivery
- independent external consumption that requires separate source/release governance

Likewise, repositories may be consolidated when separation no longer protects a meaningful boundary.

A future change that reverses a binding topology selected by this accepted ADR requires a new Replacement ADR under GDC-010.

## 6. Consequences

### Positive

- Runtime and Experience contract changes can be atomic within Notification and Scheduling
- independent deployment is preserved without paying unnecessary cross-repository coordination cost
- repository topology matches platform cohesion without conflating Platform with Repository
- UI Platform stays reusable and does not become a dumping ground for consumer applications
- local development can use actively evolving UI packages without forcing premature registry releases
- production dependency provenance remains immutable and versioned
- Identity/Organization retain stronger isolation where their security and toolchain constraints justify it
- future extraction remains evolutionary and evidence-driven

### Negative

- a platform repository contains more than one deployable and therefore requires path-aware CI
- Go and frontend build concerns coexist inside Notification/Scheduling repositories
- repository-level permissions cannot distinguish Runtime and Experience contributors as strongly as separate repositories
- atomic source changes can tempt developers to violate Runtime/Experience boundaries unless fitness functions enforce dependency direction
- local cross-repository UI development requires explicit linking/tooling until the package release path is stable

### Operational

- each deployable has its own build target, image/artifact identity, deployment manifest, release metadata, and rollback path
- repository-wide CI retains architecture, contract, secret, and dependency-boundary checks
- path-aware jobs may skip unrelated expensive tests but cannot skip shared contract or architecture gates
- local UI Platform linkage is documented as developer setup, never as a production dependency
- repository templates should standardize CODEOWNERS, CI, dependency scanning, release metadata, and Renovate/Dependabot policy

## 7. Compliance Impact

### Related Standards and Artifacts

- GDC-010 — ADR lifecycle and replacement rules
- EAD-002 — System, deployable, and architecture-boundary distinctions
- EAD-005 — simplest sufficient platform/runtime and evolutionary delivery principles
- SAD-003 — Scnehaux UI Platform
- PAD-PLT-005 — Notification Platform
- SAD-005 — Notification Runtime
- SAD-015 — Notification Experience
- PAD-PLT-011 — Scheduling Platform
- SAD-013 — Scheduling Runtime
- SAD-014 — Scheduling Experience
- ADR-GLB-008 — Go project structure and layer enforcement

### Compliance Status

Proposed.

No implementation repository should be created from this topology until the ADR is accepted.

SAD-003 currently describes local downstream consumption primarily through a shared pnpm workspace. If this ADR is accepted, SAD-003 must be aligned so that local cross-repository development is also a governed supported path while production consumption remains versioned package-based.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — One Repository per Deployable

```text
notification-runtime
notification-experience
scheduling-runtime
scheduling-experience
```

**Benefits**

- strongest repository-level access isolation
- smallest CI and dependency surface per repository
- independent repository history and release administration

**Rejected for Notification/Scheduling now because**

- Runtime and Experience are owned and evolved as cohesive platform pairs
- contract evolution becomes cross-repository coordination without a current security or ownership requirement
- four pipelines and four repository-governance surfaces add overhead without corresponding architectural isolation value
- independent deployment is achievable inside a platform-scoped repository

This remains valid for deployables whose security, ownership, vendor cadence, or toolchain constraints meet §5.1 split criteria.

### Alternative B — One Platform-Scoped Repository per Platform

```text
scnehaux-notification-platform
scnehaux-scheduling-platform
```

Each repository contains Runtime and Experience as independent deployables.

**Selected** because it best balances atomic contract evolution, platform ownership, independent deployment, local developer experience, and future extraction cost.

### Alternative C — One Giant Scnehaux Application Monorepo

```text
scnehaux-platforms/
├─ identity
├─ organization
├─ notification
├─ scheduling
├─ ui-platform
└─ ...
```

**Benefits**

- maximum atomic change capability
- one checkout
- centralized tooling

**Rejected because**

- unrelated platform ownership and security boundaries become repository-global
- CI and dependency blast radius grows with every platform
- privileged Identity concerns become unnecessarily co-located
- release and contribution policy becomes coupled across unrelated capabilities

### Alternative D — Put Notification/Scheduling Experience Inside the UI Platform Repository

**Benefits**

- UI components and consumers can change atomically
- simplest local consumption while UI packages are unstable

**Rejected because**

- a shared producer would own domain-specific consumer applications
- UI Platform release lifecycle would become coupled to Notification/Scheduling product changes
- the repository would accumulate every future Experience consumer
- package dependency direction would be confused with application ownership

### Alternative E — Require Registry Publication for Every Local UI Change

**Benefits**

- local and production dependency paths are identical
- every consumed UI revision is versioned

**Rejected as the only development path because**

- it creates needless publish/version churn while the UI Platform is still actively evolving
- it slows cross-repository local development without improving production integrity

Versioned immutable package consumption remains mandatory for released artifacts; local linking is allowed only for development.
