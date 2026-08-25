---
doc_meta:
  id: ADR-GLB-008
  title: ADR-GLB-008 Go Project Structure and Layer Enforcement
  adr_type: foundational
  status: accepted
  created: 2026-08-11
  created_date: 2026-08-11
  created_by: Architecture Authority
  governed_by: [GDC-000]
---

# ADR-GLB-008: Go Project Structure and Layer Enforcement

## 1. Title

Adopt a vertical-slice package layout with three machine-enforced layers for every Scnehaux-owned Go repository.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                             | Approver               |
| :--------- | :------- | :----------- | :------------------------------------ | :--------------------- |
| 2026-08-11 | accepted | foundational | Architecture, Core Platform, Identity | Architecture Authority |

## 3. Context

Go is the primary server-side language under EAD-005 §5.3, and three of the six control-plane repositories are written in it. The enterprise has ten frontend standards and none for Go, so every repository has been free to invent its own layout.

The consequence is already visible. An existing Go implementation applies a four-level layout — `internal/<context>/application/{command,query}` — unevenly: some contexts carry every level, others omit two. A prescribed structure that teams follow where it fits and skip where it does not conveys nothing, because its presence stops being information.

The same implementation demonstrates the cost of unenforced boundaries. ADR-GLB-007 established domain-driven boundaries and ADR-GLB-001 established the modular monolith, yet Tenant, Membership, credential, and business permission state converged into one aggregate over time. The boundaries were documented and reviewed; they were not checkable by a machine, and they eroded under delivery pressure.

Two properties of the current architecture make layout a governance concern rather than a matter of taste:

- Every boundary control the architecture depends on is asserted in continuous integration. Import analysis, grant assertion, and credential isolation all read structure. A layout that varies per repository cannot be read.
- Domain logic must be testable without a database. The revocation state machine, the Tenant lifecycle, and the Principal mapping transitions are the highest-value tests in the estate, and each becomes slow and fragile if reaching them requires a running PostgreSQL.

## 4. Decision Drivers

- Boundaries the architecture relies on must be verifiable by tooling rather than by review.
- Domain invariants must be exercisable in unit tests with no infrastructure.
- One layout across repositories so a single continuous-integration rule serves all of them.
- Ceremony proportional to the concern; a two-file adapter must not carry the structure of a bounded context.
- Engineers must not spend a decision on layout at the start of every package.
- Portability of the pattern to future Go repositories without amendment.

## 5. Decision

### 5.1 Vertical Slices, Not Global Layers

Every Scnehaux-owned Go repository SHALL organise `internal/` by concern rather than by technical role:

```text
internal/<concern>/        permitted
internal/{models,services,handlers}/    prohibited
```

A change to one concept SHALL touch one directory.

### 5.2 Three Layers

A concern that owns an invariant SHALL be organised as:

```text
internal/<concern>/
├── domain/     aggregates, value objects, state machines, invariants
├── app/        orchestration, transaction boundaries, declared ports
└── adapter/    persistence, external clients, transport
```

Four levels are rejected. A `command` and `query` split inside `app/` is permitted only where a concern carries enough read paths to justify it, and is not a default.

A concern that owns no invariant — a client over an external interface, for example — SHALL have no `domain/` and no `app/`. It is an adapter, and structuring it as a bounded context would state something untrue about it.

### 5.3 The Dependency Rule

```text
adapter/  ──►  app/  ──►  domain/
```

Dependencies SHALL point inward. `domain/` SHALL NOT import `app/` or `adapter/`. `app/` SHALL NOT import `adapter/`.

`domain/` SHALL import only the standard library and approved value-object packages that perform no input or output. It SHALL NOT import a database driver, an HTTP package, a message client, or a logging implementation.

### 5.4 Context Is an I/O Signal

A function in `domain/` SHALL NOT accept `context.Context`.

A domain method decides whether a transition is permitted and produces the facts that follow from it. It waits for nothing, so it has nothing to cancel. A domain signature that needs a context is performing input or output and belongs in `app/`.

This rule is a cheaper and more precise test than an import list, because it catches the intent before the dependency arrives.

### 5.5 Port Ownership Depends on the Boundary

Two boundaries, two opposite rules, and conflating them is a known and expensive error:

| Boundary              | Contract owner                                                            | Reason                                                                      |
| :-------------------- | :------------------------------------------------------------------------ | :-------------------------------------------------------------------------- |
| Inside one deployable | The **consumer**. `app/` declares the interface, `adapter/` implements it | Dependency inversion; `app/` becomes testable against a fake                |
| Between deployables   | The **provider**, per EAD-004 §6.3                                        | A contract owned by each consumer becomes a different contract per consumer |

### 5.6 Composition Root and Module Assembly

Only `cmd/<deployable>/` SHALL import more than one concern, and it is the only location aware of every concern.

A concern MAY assemble itself. `internal/<concern>/module.go` constructs that concern's own adapters, wires them to its own `app/`, and returns the ports it publishes. It imports one concern, so the rule above does not restrict it.

That keeps the composition root a list of module assemblies rather than a list of every struct in the repository, which is what stops it from growing with the concern count.

### 5.7 Unit of Work

A transaction SHALL be expressed as a callback receiving an explicit handle, and the handle SHALL appear in the signature of every function participating in it.

Carrying the transaction implicitly inside `context.Context` is rejected. The substrate deliberately requires a handle so that publishing outside a domain transaction does not compile; an implicit transaction deletes that guarantee, makes participation unreadable from a signature, and converts a build failure into a runtime failure found under load.

The handle type SHALL be the substrate type rather than the driver type, so the driver is named in one package instead of in every service signature.

### 5.8 Goroutine Ownership

A loop driven by a clock, a broker, or a queue decides _when_ work happens and never _what_ the work is. It is an inbound driver and SHALL live in `adapter/`, calling `app/` once per iteration. `app/` and `domain/` SHALL NOT start a goroutine.

Every goroutine SHALL have a named owner able to stop it and wait for it. The composition root SHALL own the root context, the signal handler, and shutdown ordering.

Layering that governs structure while leaving execution unstated produces exactly one outcome: every worker is written differently, and shutdown is discovered to be broken during the first incident that requires it.

### 5.9 Persistence and Migration Toolchain

Scnehaux-owned Go repositories SHALL use `pgx` for PostgreSQL access, `sqlc` for generated type-safe queries, and Atlas for schema migration under ADR-GLB-004. An object-relational mapper SHALL NOT be introduced, because a generated query surface preserves the schema as the authority and an object-relational mapper inverts that.

### 5.10 Patterns Deliberately Not Adopted

Recorded so their absence reads as a decision rather than an omission:

- **Event sourcing.** State tables remain the source of truth; the transactional outbox guarantees delivery of accepted facts. Domain events plus an outbox are routinely mistaken for event sourcing, and the two have different recovery, migration, and query properties.
- **A generic repository over a type parameter.** It erases the aggregate-specific methods that carry the invariants.
- **A command or mediator bus.** Direct method calls keep the call graph readable and the stack trace useful.
- **Global read-model separation.** A read model is introduced where one is genuinely needed, such as a projection publisher, and not as a layout rule.

## 6. Consequences

### Positive

- The layer boundary becomes a continuous-integration assertion rather than a review convention, which is the property the previous implementation lacked when its boundaries eroded.
- Domain invariants are unit-testable with no database, so the highest-value tests are also the fastest.
- One import rule covers every Go repository, present and future.
- A new engineer reads one standard rather than inferring a layout from the surrounding files.
- Extracting a concern into its own deployable becomes a wiring change, because its ports are already declared and its domain already carries no infrastructure.

### Negative

- Three directories for a concern holding four files is real ceremony, and the smallest concerns feel over-structured.
- An interface declared in `app/` and implemented in `adapter/` adds one indirection that a direct call would not need.
- Engineers arriving from layouts that place repository interfaces in the domain layer will need to adjust.

### Operational

- The import-boundary check becomes a required build step in every Go repository.
- A repository adopting this layout after the fact requires a mechanical move, and the check is enabled in the same change.

### Tradeoffs

Ceremony is accepted in exchange for enforceability. A flat package per concern reads better and cannot be checked; the deciding criterion here is whether a machine can tell the layers apart, and in a flat package it cannot.

## 7. Compliance Impact

### Related Standards

- [STD-GLB-BE-001 — Go Project Structure and Layering](../../02-standards/_global/STD-GLB-BE-001-project-structure-and-layering.md)
- [ADR-GLB-001 — Modular Monolith](ADR-GLB-001-modular-monolith.md)
- [ADR-GLB-004 — Atlas Schema Governance](ADR-GLB-004-atlas-schema.md)
- [ADR-GLB-007 — Domain-Driven Design Boundaries](ADR-GLB-007-ddd-boundaries.md)
- [STD-GLB-002 — Enterprise Database and Persistence](../../02-standards/_global/STD-GLB-002-database.md)

### Compliance Status

Accepted and authoritative. It applies to every Scnehaux-owned Go repository from its acceptance date. Existing repositories adopt it at their next structural change rather than through a dedicated migration.

### Required Waivers

None. A repository unable to satisfy a rule follows the exception process in GDC-000.

## 8. Alternatives Considered

### Alternative A — Flat package per concern

All files for a concern in one package, layered by file name rather than by directory.

**Benefits:** the most readable option; no interface indirection; no ceremony for small concerns; idiomatic in much of the Go ecosystem and in the standard library itself.

**Rejected because:** it is not checkable. Import analysis operates on packages, so a rule stating that domain code must not import a database driver cannot be expressed when domain code and the driver live in one package. The architecture this project rests on is built from machine-checked boundaries, and this option removes the only handle a machine has.

### Alternative B — Four layers with a command and query split

`internal/<concern>/application/{command,query}/`, matching the existing reference implementation.

**Benefits:** familiar to the current team; scales when a concern carries many read paths; makes write and read intent visible in the path.

**Rejected as a default because:** the reference implementation applies it unevenly across its own contexts, which is the observable outcome of a structure deeper than most concerns need. Four directories before the first file is disproportionate for a concern with eight files. The split remains available where a concern earns it.

### Alternative C — Global technical layers

`internal/{domain,application,infrastructure}/` with concerns nested inside each.

**Benefits:** the layer boundary is visible at the top level and is equally checkable.

**Rejected because:** it scatters one concept across three top-level directories, so a change to Membership touches three distant places and a reviewer cannot see the concept whole. It also makes extraction into a separate deployable a three-way move rather than a directory move.

### Alternative D — Standard Go Project Layout

The community layout with `pkg/`, `api/`, `configs/`, and `build/`.

**Benefits:** widely recognised; ready-made answers for auxiliary directories.

**Rejected because:** `pkg/` publishes an importable surface these repositories do not offer, and the layout is organised by artifact type rather than by concern. It is a convention for open-source distribution, and these are closed control-plane services whose sharing boundary is a versioned module.

### Alternative E — A shared kernel of cross-concern types

A package of read-only types that concerns may import directly, removing the mapping between a port's view type and a consumer's own representation.

**Benefits:** removes mapping code where one concern needs another's data; fewer types to keep aligned; a smaller diff for a field added on both sides.

**Rejected because:** it is the mechanism by which the boundary erosion this architecture exists to prevent becomes policy. The previous implementation did not merge Tenant, Membership, credential, and permission through a decision; it merged them because importing a neighbouring type was cheaper than declaring a port, one commit at a time. A shared kernel makes that the sanctioned path.

Every type in such a package is co-owned by two domains, and EAD-001 §6.1 prohibits co-ownership of an authoritative capability. The pattern as Evans defines it is not a bag of shared structs either: it is a deliberately shared subset of the model carrying an explicit joint-ownership and coordination obligation, and he identifies it as the highest-coupling integration option available.

The cost it removes is also smaller than it appears. At a boundary drawn correctly, a concern needs another concern's **identifier**, not its aggregate: `Membership` holds a `TenantID`, which requires no import and no mapping. A concern needing many attributes of another concern is reporting a misplaced boundary, and the response is to move the boundary rather than to share the type.

Value objects with no domain meaning — identifiers, event types, money, time — remain shared through the substrate library, which already carries an explicit prohibition on domain concepts.

### Alternative F — No prescribed layout

Each repository chooses.

**Benefits:** zero adoption cost; each team optimises locally.

**Rejected because:** it is the current state, and it produces a different layout per repository and no possible shared enforcement. It also spends a decision at the start of every package on a question with no local answer.
