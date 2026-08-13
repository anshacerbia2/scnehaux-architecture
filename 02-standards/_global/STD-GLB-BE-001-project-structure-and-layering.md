---
doc_meta:
  id: STD-GLB-BE-001
  title: Go Project Structure and Layering Standard
  owner: Architecture Review Board
  version: 1.0.0
  status: approved
  classification: internal
  governed_by: [GDC-000]
  review_cycle_days: 365
  created_date: 2026-08-11
  last_reviewed: 2026-08-11
---

# STD-GLB-BE-001: Go Project Structure and Layering Standard

## Objective & Scope

Define the mandatory package layout, layer boundaries, and import rules for every Scnehaux-owned Go repository, so that the boundaries the enterprise architecture depends on are verified by the build rather than by review.

This standard applies to every repository whose primary language is Go, including deployable services and versioned shared libraries. It does not apply to vendored code, generated code, or repositories owned by a third party.

It defines structure and layering. Runtime behavior, persistence isolation, observability, and API shape remain with STD-GLB-002, STD-GLB-003, and STD-GLB-001.

## Design Principles

- **Checkable over conventional** — a boundary a machine cannot read is a boundary that erodes under delivery pressure
- **Concern over technical role** — one concept lives in one directory, so a change touches one place
- **Ceremony proportional to invariant** — structure is earned by what a package protects, not applied uniformly
- **Domain waits for nothing** — business rules execute without infrastructure, which makes them fast to test and cheap to trust
- **Dependencies point inward** — the innermost layer knows nothing about what surrounds it
- **One layout across repositories** — a single build rule serves every Go repository, present and future

## Normative Rules

### 1. Repository Layout

- A deployable repository MUST place each entrypoint under `cmd/<deployable-name>/`.
- Application code MUST live under `internal/`. A repository MUST NOT publish an importable surface through `pkg/` unless it is a shared library, in which case its packages live at the module root.
- `internal/` MUST be organised by concern. Top-level technical groupings such as `models`, `services`, `handlers`, or `utils` are PROHIBITED.
- Database migrations MUST live under `migrations/` and be managed by the tooling named in ADR-GLB-004.
- Technical Design Documents MUST live under `docs/designs/`.

### 2. Layers

- A concern that owns an invariant MUST be organised as `domain/`, `app/`, and `adapter/`.
- A concern that owns no invariant — a client over an external interface, a pure transformation — MUST NOT carry `domain/` or `app/`. Structuring it as a bounded context asserts something untrue about it.
- A `command` and `query` separation inside `app/` is PERMITTED where a concern carries multiple independent read paths. It MUST NOT be applied as a default.
- Nesting deeper than `internal/<concern>/<layer>/` requires a stated reason in the concern's Technical Design Document.

### 3. The Dependency Rule

- `domain/` MUST NOT import `app/` or `adapter/`, in the same concern or in any other.
- `app/` MUST NOT import `adapter/`.
- No package under `internal/<concern>/` MUST import another concern's `domain/`, `app/`, or `adapter/`. Concerns communicate through ports declared per rule 5.
- Only the composition root under `cmd/` MUST be permitted to import **more than one** concern. A package that imports one concern — including that concern's own module assembler — is unaffected by this rule.
- A concern MAY provide `internal/<concern>/module.go` that constructs its own adapters, wires them to its own `app/`, and returns the ports it publishes. This keeps `cmd/` to a list of module assemblies rather than a list of every struct in the repository.
- A concern MUST NOT hold a shared read-only type on behalf of another concern. Cross-concern references carry identifiers and declared view types, never aggregates. A concern requiring many attributes of another concern indicates a boundary in the wrong place, and is resolved by moving the boundary rather than by sharing a type.

### 4. Domain Purity

- `domain/` MUST import only the standard library and approved value-object packages that perform no input or output.
- `domain/` MUST NOT import a database driver, an HTTP package, a message-broker client, a logging implementation, a metrics client, or a configuration reader.
- A function in `domain/` MUST NOT accept `context.Context`. A domain method decides whether a transition is permitted and produces the facts that follow; it waits for nothing, so it has nothing to cancel. A signature requiring a context is performing input or output and belongs in `app/`.
- `domain/` MUST NOT read the wall clock or generate randomness directly. Both MUST be supplied by the caller, so a state machine is reproducible in a test.
- An aggregate MUST validate its own transitions. A state change accepted by a service but not by the aggregate is PROHIBITED.

### 5. Port Ownership

- Inside one deployable, an interface MUST be declared by the package that consumes it and implemented by the package that satisfies it. `app/` declares, `adapter/` implements.
- Across deployables, the contract MUST be owned by the provider, per EAD-004. A consumer MUST NOT declare its own version of a contract another system publishes.
- A port MUST expose a view type owned by its declaring package. It MUST NOT expose an aggregate, a repository, a transaction handle, or a driver type.

### 6. Transactions and the Unit of Work

- A transaction MUST be opened by `app/`, never by `domain/` and never by a transport handler.
- A domain mutation and the domain events it produces MUST commit in one transaction. Publishing outside the transaction that produced the fact is PROHIBITED.
- A transaction MUST NOT span two aggregates unless the second is an append-only technical record such as an outbox row.

The unit of work MUST be expressed as a callback that receives an explicit transaction handle:

```go
func (s *Service) Revoke(ctx context.Context, id id.UUID, reason string) error {
    return s.tx.InTx(ctx, func(ctx context.Context, tx db.Tx) error {
        m, err := s.repo.LoadForUpdate(ctx, tx, id)   // adapter, through a port
        if err != nil {
            return err
        }
        if err := m.Revoke(reason); err != nil {      // domain, no context, no I/O
            return err
        }
        if err := s.repo.Save(ctx, tx, m); err != nil {
            return err
        }
        return outbox.Append(ctx, tx, m.Events()...)  // requires the handle
    })
}
```

The callback receives a derived context and MUST propagate it. That context carries a
marker recording that a transaction is open, so a service opening a second one on the
same call path is refused rather than silently acquiring a second connection and losing
atomicity between the two.

The marker is a fact, not a handle: it grants no capability, cannot run a query, and its
only reader is the nesting guard. It therefore does not reintroduce the implicit
transaction the rule below prohibits.

- The transaction handle MUST appear in the signature of every function that participates in a transaction.
- Carrying the transaction implicitly inside `context.Context` is PROHIBITED. An implicit transaction removes the compile-time guarantee that a publication cannot occur outside one, makes participation unreadable from a signature, and converts a build failure into a runtime failure discovered under load.
- The transaction handle type MUST be the substrate type `db.Tx`. A package other than the substrate's own adapter MUST NOT name a driver type directly, so the driver is named in one place rather than in every service signature.
- A port accepting a transaction handle MUST accept it as a parameter rather than storing it, because a stored handle outlives the transaction that produced it.

### 7. Concurrency and Lifecycle

Layering answers where a background worker belongs, and the answer follows from the same rule as an HTTP handler. A loop driven by a clock, a broker, or a queue is an inbound driver: it decides *when* work happens, never *what* the work is. It is therefore a driving adapter.

```text
adapter/   the loop, the ticker, the broker subscription, the claim
   │       decides when
   ▼
app/       one iteration of work, inside its own transaction
   │       decides what
   ▼
domain/    the transition and the facts that follow
```

- A worker loop MUST live in `adapter/`. Each iteration MUST call `app/` and MUST NOT reach into `domain/` directly.
- `app/` MUST NOT start a goroutine. A service method returns when its work is done or its context is cancelled.
- `domain/` MUST NOT start a goroutine, reference a channel, or take a lock.

#### Ownership

- Every goroutine MUST have a named owner that can stop it and can wait for it to finish. A bare `go f()` outside a supervised runner is PROHIBITED.
- A goroutine MUST terminate when its context is cancelled. A worker that ignores cancellation delays every shutdown behind its longest sleep.
- A request handler MUST NOT spawn a goroutine that outlives the request, because its context is already cancelled and its failure has no caller to report to.
- Per-request fan-out MUST be bounded. An unbounded spawn converts a traffic spike into memory exhaustion.

#### Startup and Shutdown

- The composition root MUST own the root context, the signal handler, and the wait group. A concern MUST NOT install a signal handler.
- Shutdown MUST proceed in order: stop accepting new work, cancel the root context, wait for workers within a bounded deadline, then exit. A worker still running at the deadline MUST be reported by name, so a hung shutdown names its cause instead of appearing as a slow process.
- In-flight work MUST be allowed to finish or MUST be left in a state the next start can resume. A worker that neither completes nor records its position loses the work silently.
- A deployable MUST report readiness separately from liveness, and MUST report not-ready as soon as shutdown begins so the load balancer stops sending work before the process stops accepting it.

#### Failure

- A worker loop MUST recover from a panic in one iteration, record it with its correlation identifier, increment a counter, and continue. A panic that kills the process removes every other worker in it.
- A worker MUST NOT exit silently. Termination other than by context cancellation MUST be logged and counted, because a dispatcher that stopped and a dispatcher with nothing to do look identical from outside.
- Backoff on repeated failure MUST be bounded and MUST carry jitter, so a dependency recovering does not receive every worker at the same instant.

### 8. Errors

- An error crossing a layer boundary MUST carry a typed classification, not only a message. Callers MUST NOT match on error text.
- `domain/` MUST return errors describing a refused transition or a violated invariant. It MUST NOT return an error carrying an HTTP status, a SQL state, or a transport concern.
- Translation into an RFC 7807 problem document per STD-GLB-001 MUST occur in `adapter/`.

### 9. Persistence

- PostgreSQL access MUST use `pgx`. Queries MUST be generated by `sqlc` from checked-in SQL, so the schema remains the authority.
- An object-relational mapper MUST NOT be introduced. A generated query surface preserves the schema as the authority; an object-relational mapper inverts that relationship.
- Generated code MUST live in a directory named so that it is excluded from review-required paths and from coverage targets.
- A repository implementation MUST return aggregates, not rows. Mapping from generated row types to aggregates MUST occur in `adapter/`.

### 10. Configuration and Wiring

- Configuration MUST be read once, at the composition root, and injected. A package MUST NOT read an environment variable directly.
- A package MUST NOT hold package-level mutable state other than for a documented process-wide concern such as identifier sequencing.
- An adapter MUST be constructed with its dependencies rather than resolving them internally.

### 11. Testing

- `domain/` tests MUST run with no database, no network, and no container.
- `app/` tests MUST run against fakes implementing its declared ports.
- Tests requiring infrastructure MUST be separated by build tag so the unit suite remains runnable on any workstation.
- Test files MUST live beside the code they exercise.

### 12. Naming

- A directory MUST NOT be named for a Go reserved word. `interface/` is PROHIBITED; use `transport/` or `adapter/`.
- A package name MUST be a singular lowercase word without underscores. Stutter such as `membership.MembershipService` MUST be avoided.
- A concern directory MUST be named for the concept it owns, not for the technology it uses.

## Exceptions

Deviation from this standard requires formal exception approval under GDC-000, with a stated reason, a named owner, an expiry date, and the boundary check that will be disabled as a result.

A disabled boundary check is the material cost of any deviation here, because every rule in this standard exists to keep one automated assertion meaningful. A request that does not name which check it disables has not been assessed.

## Enforcement Mechanism

- **Import boundary analysis** over the Go package graph, executed in continuous integration and failing the build. It asserts rules 3 and 4 by resolving imports rather than by matching text, so an import introduced through an alias, a blank identifier, or a test file is detected on the same basis as a direct one.
- **Domain purity check** asserting that no exported or unexported function in a `domain/` package accepts `context.Context`, and that no `domain/` package imports a denied module path.
- **Composition root check** asserting that exactly one package per deployable imports more than one concern.
- **Layout check** asserting that every concern containing a `domain/` also contains `app/`, and that no path nests deeper than the permitted depth without a recorded reason.
- **Naming check** rejecting reserved-word directories and underscore package names.
- **Generated-code boundary** asserting that generated query code is confined to its designated directory and is not edited by hand.
- **Test tier check** asserting that the unit suite completes with no database, no network, and no container available.
- **Transaction handle check** asserting that no package other than the substrate's own adapter names a driver transaction type, and that no repository port stores a handle in a struct field.
- **Goroutine ownership check** asserting that the `go` statement appears in no package under `domain/` or `app/`, and that every occurrence in `adapter/` is inside a supervised runner rather than a bare call.
- **Shutdown test** asserting that cancelling the root context terminates every worker within the bounded deadline, and that a worker exceeding it is reported by name.
- **Worker resilience test** asserting that a panic in one iteration is recovered, counted, and followed by a further iteration, and that termination other than by cancellation is logged and counted.
