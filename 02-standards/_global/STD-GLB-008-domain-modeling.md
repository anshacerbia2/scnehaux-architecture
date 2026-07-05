---
doc_meta:
  id: STD-GLB-008
  title: Enterprise Domain Modeling Standard
  owner: Principal Software Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-22
---

# Enterprise Domain Modeling Standard (STD-GLB-008)

---

## 1. Objective & Scope

This standard establishes the mandatory patterns, structural constraints, and lifecycle rules for modeling domain logic across all applications within the Scnehaux enterprise.

It defines Bounded Context boundaries, Aggregate invariants, entity separation, Value Object properties, and transactional boundaries. These rules prevent domain pollution, enforce logical segregation, and ensure that data mutations remain consistent.

---

## 2. Design Principles

Domain models must align with bounded contexts derived from business capabilities. Aggregate boundaries enforce transactional consistency, and domain events decouple cross-context communication to prevent monolithic coupling.

## 3. Normative Rules

### Bounded Context & Domain Isolation Rules

To prevent logical domain leakage and facilitate clean service boundaries:

- **Strict Bounded Context Alignment**: Every microservice or module within a Modular Monolith must correspond to exactly one Bounded Context (e.g. Identity, Core HR, Payroll, Time & Attendance).
- **Ubiquitous Language Enforcement**: Domain models, database schema columns, API request fields, and code variables must utilize the naming conventions defined in the domain dictionary. Alternate synonyms or colloquial translations are prohibited.
- **Upstream/Downstream Integration Patterns**:
  - _Anti-Corruption Layer (ACL)_: A downstream context consuming data from an legacy external system must translate incoming payloads using a dedicated ACL module. The downstream domain logic must never reference external schemas directly.
  - _Shared Kernel Restrictions_: Shared kernels are restricted strictly to utility libraries (e.g. date formatters, encryption utils). Shared core domain entities across different Bounded Contexts are prohibited.

---

### Aggregate Boundaries & Rules

Aggregates represent transactional boundaries containing clusters of associated entities and value objects.

- **Single Root Ingress**: External references must point exclusively to the Aggregate Root. Downstream consumers are prohibited from holding direct reference structures to internal child entities.
- **Transactional Isolation**: A single application transaction must mutate exactly one Aggregate instance. If a business workflow spans multiple aggregates, consistency must be coordinated asynchronously using Domain Events and Saga/Choreography orchestration patterns.
- **Aggregate Reference by Identifier**: Aggregates must reference other aggregates strictly by their primary key identifiers (IDs). Deep nesting of external Aggregate objects within another Aggregate instance is prohibited.
- **Resource Constraints**: Aggregates must be designed to remain memory-bounded:
  - An aggregate must not contain more than `1000 child records` (such as historical line items). High-volume child records must be modeled as independent aggregates referenced by identifier.

#### Aggregate Consistency Boundaries & Write Isolation Rules

To enforce domain integrity and prevent transaction deadlocks under load, services must map write boundaries explicitly:

1.  **IAM Domain Consistency Mapping**:
    - **User Aggregate Boundary**: Encompasses the `User` root entity, `Credential` records (e.g. password hashes), and `Session` metadata. Mutating these records in a single database transaction block is permitted.
    - **Isolation Constraint**: The User aggregate transaction must not modify the state of the `Tenant`, `Role`, or `Permission` aggregates.
    - **Cross-Aggregate Association**: Users associate with Roles and Tenants strictly via identifier references (`RoleID`, `TenantID`). Modifying User roles must change only the identifier reference stored in the User aggregate.
2.  **State Synchronization Rules**:
    - **Tenant Deactivation Flow**: If a Tenant state changes to inactive, the Tenant aggregate must not update User login statuses in the database. Instead, the Tenant aggregate publishes a `TenantDeactivatedEvent`. The Identity service handles this event asynchronously to invalidate associated User sessions in the background.
    - **Verification Gates**: Check-time constraints (e.g., verifying user permissions) must evaluate references dynamically at the API gateway or service middleware using cached permission lists, rather than joining tables during write transactions.

---

### Invariant Protection & Entity Validation

Domain models must protect business rules (invariants) actively at memory boundaries.

- **Zero-Public-Mutators Invariant**: Aggregate state changes must proceed strictly through descriptive domain methods (e.g. `employee.TerminateEmployment(reason, date)`) rather than generic public property setters. Setting fields directly from controllers is prohibited.
- **Value Object Immutability**: Value Objects (e.g. `Address`, `Money`, `TaxRate`) must have no identity and must be fully immutable. Modifying a Value Object requires replacing the entire instance.
- **Atomic Initialization**: Entities must validate their structural rules during creation. Constructing an entity in an invalid state (e.g. creating an `EmploymentContract` with a negative salary value) must throw an validation error immediately.

---

### Domain Events & Domain Services

- **Domain Event Emission**: State mutations that trigger downstream reactions must publish a local Domain Event (e.g., `EmploymentTerminatedEvent`).
- **Transactional Outbox Integration**: Domain events must be appended to the local transaction outbox table inside the same transaction block that updates the aggregate state.
- **Domain Services Scope**: Business logic that does not naturally belong to a single Aggregate (e.g., executing cross-aggregate payroll checks) must be isolated within a Domain Service. Domain Services must be stateless and must not maintain internal operational variables.

---

## 4. Exceptions

None. All domain modeling constraints apply universally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

1. **Static Analysis AST Inspections**: Build verification checks must run AST parsers to flag public field setter methods inside Aggregate files.
2. **Architecture Review Audits**: Pull requests introducing cross-aggregate database mutations in a single transaction block must trigger security and architectural reviews.
3. **Exception Waivers**: Deviations from these domain modeling parameters require an approved Architectural Decision Record (ADR) and approval by the Architecture Review Board.
