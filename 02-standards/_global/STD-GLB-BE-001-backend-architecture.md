---
doc_meta:
  id: STD-GLB-BE-001
  title: Backend Service Architecture Standard
  owner: Principal Software Architect
  version: 1.0.0
  status: adopted
  classification: internal
  governed_by: [EAD-005]
  review_cycle_days: 180
  created_date: 2026-08-18
  last_reviewed: 2026-08-18
---

# Backend Service Architecture Standard (STD-GLB-BE-001)

---

## 1. Objective & Scope

This standard defines the internal structure every Scnehaux backend service holds: how packages depend on one another, where input and output are permitted, where concurrency starts, and how those boundaries are asserted by a machine rather than by a reviewer.

It applies to every deployable backend service and every shared backend library in the enterprise, in any language. The rules are stated so that each can be checked against a package graph or a syntax tree.

**Out of scope:** which frameworks, routers, and drivers a service selects, owned by the technology radar and by each system's design; frontend structure, owned by the global frontend standards; and infrastructure topology, owned by `EAD-005`.

---

## 2. Design Principles

**A boundary a machine cannot read is a boundary that erodes.** Every rule below has a mechanical check. A rule that exists only in prose survives until the first delivery deadline, and its erosion is invisible in review because each individual violation looks reasonable.

**Dependencies point toward stability.** Business rules do not depend on transport, storage, or vendor. The direction is what makes storage replaceable without touching the rules that gave the data meaning.

**Input and output are visible in a signature.** A function that performs no I/O and a function that might are different kinds of thing, and the type system is where that difference belongs.

**Nothing starts by being linked.** A package that begins work on import cannot be shut down by the process that imported it, and cannot be tested without starting it.

---

## 3. Normative Rules

### Rule 1 — One Bounded Context per Deployable

A deployable service MUST correspond to exactly one bounded context as defined by `STD-GLB-008`. Modules within it MUST maintain logical separation and MUST NOT share domain entities across module boundaries.

A deployable containing two bounded contexts is prohibited. The two will be released together, and a shared release train reintroduces the coupling that decomposition removed.

### Rule 2 — Layer Direction

Packages MUST be assigned to a layer, and dependencies MUST point inward only:

```text
adapter  →  app  →  domain
```

- `domain` holds entities, value objects, aggregates, and business rules.
- `app` orchestrates use cases and owns transaction boundaries.
- `adapter` holds transport, persistence, broker, and vendor integration.

A `domain` package MUST NOT import an `app` or `adapter` package. An `app` package MUST NOT import an `adapter` package. Inversion is achieved through an interface declared by the consumer, not by the provider.

### Rule 3 — Declared Dependency Graph

Every internal edge between packages MUST be declared in a machine-readable manifest committed beside the code. An edge that is not declared MUST fail the build.

A package absent from the manifest MUST import no internal package. Test files count: an import in a test file establishes the same coupling as one in production code, and a shortcut taken in a test is the shortcut that gets copied.

The manifest MUST be reviewable in the same change as the code it constrains. A ruleset living elsewhere is a ruleset nobody reads while writing the import.

### Rule 4 — Domain Purity

A `domain` package MUST perform no input or output. Concretely, a function in a `domain` package MUST NOT accept a cancellation or deadline context, MUST NOT read a clock, MUST NOT read a source of randomness, and MUST NOT reference a driver, client, or file handle.

A cancellation context in a signature is the mechanical signal that I/O is possible, which is why it is the checked form of this rule. Time and randomness enter the domain as arguments supplied by `app`.

### Rule 5 — The Driver Is Named Once

The database driver, broker client, and every vendor SDK MUST be named in exactly one package each. Every other signature MUST carry an abstraction owned by this codebase.

A driver type appearing in a service signature makes replacing the driver a change to every signature that carries it. Naming it once makes that a change to one package.

### Rule 6 — Transactions Are Explicit

A transaction handle MUST be an explicit parameter of any function that participates in one. An ambient transaction — one retrieved from a context, a package variable, or a thread-local — is prohibited.

A function that writes inside a caller's transaction and a function that opens its own MUST be distinguishable at the call site. When they are not, a caller composes two functions and silently gets two transactions, and the atomicity it believed it had is absent.

Recording *that* a transaction is open, in order to refuse opening a second one, is permitted. Such a marker MUST grant no capability and MUST NOT be usable to execute a statement; a marker that yields a usable handle is an ambient transaction under another name.

### Rule 7 — Concurrency Belongs to a Driving Adapter

A `domain` or `app` package MUST NOT start a goroutine, thread, or task. Worker loops, pollers, dispatchers, and consumers MUST live in a driving adapter, and MUST be constructed and started by the composition root.

A loop started inside business logic cannot be stopped by the process that owns the lifecycle, and it cannot be tested without starting it.

### Rule 8 — Configuration Is Read at the Composition Root

Configuration MUST be read once at process start, in the composition root, and passed down as explicit arguments. A package MUST NOT read an environment variable, a configuration file, or a flag at any other point, and MUST NOT hold configuration in a package-level variable.

A required setting that is absent MUST fail startup. A process that starts without a setting it needs and reports healthy is worse than one that never starts.

### Rule 9 — One Error Taxonomy, One Wire Representation

A service MUST define its errors as a closed taxonomy, and the transport representation MUST be produced in exactly one place. A handler MUST NOT construct an error body directly.

Redaction MUST be applied by the serializer rather than by each caller. A rule every caller must remember is a rule one caller forgets, and the forgotten instance is in the error path nobody exercises.

### Rule 10 — Concurrency Is Verified Under a Race Detector

Every test suite MUST run under the language's race or data-race detector in continuous integration, and the detector MUST be verified capable of reporting at least once rather than assumed armed.

A detector that reports nothing because it is not enabled is indistinguishable from correct code.

### Rule 11 — No Work on Import

A package MUST NOT perform work as a side effect of being linked: no network call, no file access, no goroutine, and no mutable global initialised from the environment.

A dependency graph is not an execution order. Work that happens because a package was imported executes in an order the author of the composition root did not choose.

### Rule 12 — Naming

- A directory name MUST NOT be a reserved word of the implementation language.
- A package name MUST NOT contain an underscore or an uppercase letter.
- A directory name MUST equal the name of the package it contains.

A package whose directory and name disagree is imported under one name and referenced under another, and every reader pays that cost on every file.

---

## 4. Exceptions

**Rule 4** does not apply to a package outside the `domain` layer. A package in `app` or `adapter` accepts a cancellation context, reads a clock, and performs I/O by design.

**Rule 5** permits exactly the package that owns the abstraction to name the underlying driver, and permits its test double to do the same. The exception list is enumerated in the Rule 3 manifest so that its growth is visible in a diff.

**Rule 7** does not apply to a driving adapter or to a composition root, which is where loops are placed rather than removed.

**Rule 10** permits a suite to omit the detector when the language provides none. It does not permit omitting it because the suite is slow.

**Rule 12** permits a generated package to carry the naming imposed by its generator, provided the generated directory is excluded from hand-written code paths.

No other deviation exists. Rules 1, 2, 3, 6, 8, 9, and 11 apply unconditionally, because each describes a property whose partial application provides none of its benefit: a dependency graph enforced in most packages is not acyclic, and a transaction explicit in most call paths is not composable.

---

## 5. Enforcement Mechanism

1. **Package graph audit (Rules 1, 2, 3, 5, 12)**: a build step reads the resolved package graph from the toolchain rather than matching text, so an import introduced through an alias, a blank identifier, or a test file is detected on the same basis as a direct one. An undeclared internal edge, a denied driver import outside its exception list, or a reserved directory name blocks the build.
2. **Syntax audit (Rules 4, 7, 11)**: the same step parses each file in a constrained package and reports a cancellation context in a pure signature, a goroutine started outside a driving adapter, and work performed during package initialisation.
3. **Compilation audit (Rule 6)**: the transaction handle is a required parameter, so a call that omits it fails to compile. This is asserted by a compilation test rather than by inspection, because a rule the compiler enforces needs no reviewer.
4. **Race detector gate (Rule 10)**: the test suite runs under the detector on every push, and the detector's capability to report is proven by a deliberate unsynchronised write in a throwaway module.
5. **Every gate must be able to fail**: each rule above carries a fixture that violates it, and the audit's own test suite asserts that the rule rejects that fixture. A gate that has never rejected anything is indistinguishable from no gate.
