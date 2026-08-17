---
doc_meta:
  id: ADR-ORG-001
  title: ADR-ORG-001 Separate Organization Authority and Keycloak Projection
  adr_type: foundational
  status: accepted
  created: 2026-08-18
  created_date: 2026-08-18
  created_by: Enterprise Architect
  governed_by: [PAD-PLT-002]
---

# ADR-ORG-001: Separating Organization Authority from its Keycloak Projection

---

## 1. Title

Separating Organization Authority from its Keycloak Projection

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-08-18 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

Two systems need the same facts about who belongs to which Tenant, and only one of them can own those facts.

The Organization & Tenancy Control application is the authority for Organization, Subscriber Account, Client Account, Tenant, Workspace, and Membership. The identity kernel needs a projection of the active Membership context in order to put it into a token, because a protected resource verifies tokens locally and cannot call an authority per request.

That leaves one question with two plausible answers and very different consequences: does the Organization authority write the projection into Keycloak itself, or does it publish a fact that the Identity Control Service applies?

Writing directly is shorter. It removes a hop, removes an event, and removes the eventual-consistency window. It also requires the Organization authority to hold the Keycloak administration credential, which is the most powerful credential in the estate: it can create a Principal, reset an authenticator, and read or alter any client registration.

A related failure has already been recorded in this domain. Five concepts — Organization, Subscriber Account, Client Account, Tenant, and Workspace — were treated as interchangeable in an earlier model, and collapsing any two of them produced an authorization boundary that could not be expressed. A Subscriber Account pays; a Tenant isolates data; a Workspace organises collaboration. A control that assumes those are the same object cannot state what it protects.

## 4. Decision Drivers

**Credential blast radius.** A credential held by one process can be used by that process. Granting Keycloak administration to the Organization authority means a defect anywhere in Tenant lifecycle, invitation handling, or Membership mutation is a path to authenticator reset for every Principal in the enterprise. Containment is achieved by not holding the credential, and by nothing weaker.

**One writer per store.** Keycloak's user, group, and client objects are already written by the Identity Control Service, which owns the Principal creation path. A second writer produces two reconciliation loops over one store, each repairing toward its own view, and the two will disagree during any partition.

**Authority must be reconstructable.** `EAD-003` makes each domain the sole source of truth for its data and permits other domains to obtain it only through the owner's API or published events. A projection is a cache. If a projection can be promoted into authority — because whoever wrote it was also the authority — then the authoritative record has no single location and cannot be restored from one.

**Enforcement is a security property with a stated bound.** Revocation must reach the kernel within a budget. A published event with a durable outbox has a measurable, monitorable delay. A synchronous cross-domain write has an availability coupling instead: the Membership transaction cannot commit while Keycloak is unreachable, so a revocation fails rather than being delayed.

## 5. Decision

### 5.1 Tenant Offboarding and Retirement Coordination

Tenant offboarding is a coordinated sequence owned by the Organization authority and executed by consumers.

Entering offboarding MUST increment the Tenant security version and publish a Tenant security event. That event, not the offboarding lifecycle events, is the enforcement input: consumers act on the security version and ignore lifecycle progress, so a slow offboarding workflow cannot delay containment.

Retirement MUST NOT delete Membership history. `STD-GLB-007` requires hard deletion for a right-to-erasure request against personal data; an offboarded Tenant is a commercial state change and not an erasure request, and discarding the Membership record would remove the evidence of who had access and when.

### 5.2 Five Concepts Remain Distinct

Organization, Subscriber Account, Client Account, Tenant, and Workspace are five separate entities with five separate lifecycles. No design may collapse, alias, or derive one from another.

| Concept | What it is | What it is not |
| :-- | :-- | :-- |
| Organization | The legal or operational entity | An isolation boundary |
| Subscriber Account | The commercial relationship that pays | The data boundary |
| Client Account | The party a service is delivered to | The paying party |
| Tenant | The data isolation boundary | The billing unit |
| Workspace | The collaboration container inside a Tenant | A Tenant |

A single identifier standing for two of these is prohibited. The reason is that an authorization decision names exactly one of them, and a control written against a conflated identifier cannot state which boundary it enforces.

### 5.3 Organization Is the Sole Authority for Membership

Membership state, its version, and the Tenant security version are authoritative in the Organization Database and nowhere else. Every other representation is a projection with a stated staleness bound.

A projection MUST NOT be promoted into authority. Reconciliation repairs in one direction: from the Organization authority toward the projection.

### 5.4 Organization Never Writes to Keycloak

The Organization & Tenancy Control application MUST NOT write to Keycloak through any interface, and MUST NOT write to the Keycloak database at all.

The prohibition MUST be structural rather than procedural. The application holds no Keycloak administration credential, and its deployment has no network route to the Keycloak administration endpoint. A rule enforced by a credential nobody issued cannot be broken by a code change, which a rule enforced by review can.

Reads are prohibited on the same basis. A read path becomes a dependency, and a dependency on Keycloak availability inside a Membership transaction reintroduces the availability coupling this decision removes.

### 5.5 Propagation Is Through the Outbox and the Broker Only

A Membership or Tenant state change and its outbox append MUST commit in one transaction. The dispatcher publishes; the Identity Control Service consumes idempotently and applies the projection through the supported Keycloak administration interface.

The Identity Control Service is the only process holding the Keycloak administration credential, so it is the only process that can apply a projection. That is the same containment argument as §5.4 read from the other side.

Consumers requiring the authoritative set for reconciliation MUST obtain it through the Organization authority's published snapshot contract. A privileged read path, a replica, or a direct database connection MUST NOT be created for that purpose.

### 5.6 Membership Confers Context and Tenancy Administration Only

A Membership establishes a contextual relationship between a Principal and a Tenant or Workspace, and it carries tenancy-administrative authority within that scope. It carries nothing else.

A Membership MUST NOT convey a Product permission, a commercial Entitlement, or a business role. Those are owned by the Product domain and by the Billing Platform respectively, per the `EAD-001` glossary, which binds Permission to the Identity Platform and Entitlement to Billing.

The projection carried into Keycloak is therefore context and not authorization: Tenant identity, Workspace identity, Membership status, and versions. A protected resource combines that context with its own authorization decision. A valid token remains an authenticated identity and never an authorization decision.

## 6. Consequences

### Positive

- **Credential containment**: the Keycloak administration credential exists in one process. A defect in Tenant lifecycle, invitation handling, or Membership mutation cannot reach an authenticator.
- **One writer per store**: Keycloak has a single writer, so there is one reconciliation loop and one repair direction.
- **Restorable authority**: the authoritative Membership record has one location and can be rebuilt from it after any projection loss.
- **Measurable enforcement**: propagation delay is a monitored number rather than an availability coupling. A broker outage delays enforcement; it does not fail a revocation transaction.
- **Expressible controls**: keeping the five concepts distinct lets a control name the boundary it protects.

### Negative

- **Eventual consistency**: a Membership change is visible in a token only after propagation. Every consumer therefore declares a staleness bound and a behaviour when it is exceeded.
- **More moving parts**: an outbox, a dispatcher, a broker, a consumer, and a reconciler exist where a direct write would have been one call.
- **Two failure surfaces**: the projection can drift, so drift detection and repair are mandatory rather than optional.

### Tradeoffs

We trade immediate projection consistency and a smaller component count for credential containment, a single writer per store, and an authority that can be restored from one place.

### Operational Impact

Requires monitoring propagation delay, unresolved consumer operations, and projection drift findings. A drift finding of the `extra` class — a context projected that the Organization authority does not grant — is escalated as a potential privilege escalation rather than repaired silently, because reaching that state requires either a defect in the propagation path or a write outside it.

### Security Impact

The most powerful credential in the estate is held by one process with a narrow role set. Organization holds none. Enforcement of a revocation is bounded by a published figure that names both the propagation budget and the token lifetime class it assumed.

### Scalability Impact

Membership mutation throughput is bounded by the Organization Database rather than by Keycloak administration API capacity. The projection applies asynchronously with its own concurrency, so a Membership batch cannot exhaust the administration endpoint that authentication depends on.

## 7. Compliance Impact

### Related Standards

- [Enterprise Data Ownership & Topology (EAD-003)](../../01-enterprise/EAD-003-enterprise-data-ownership-and-topology.md) — sole source of truth, no cross-domain database access
- [Enterprise Security Architecture (EAD-006)](../../01-enterprise/EAD-006-enterprise-security-architecture.md) — least privilege, blast-radius containment
- [Enterprise Transactional Outbox (ADR-GLB-003)](../_global/ADR-GLB-003-transactional-outbox.md) — the propagation mechanism this decision depends on
- [Token and Verification Profile (STD-IAM-002)](../../02-standards/identity-access/STD-IAM-002-token-and-verification-profile.md) — the claim profile the projection feeds, and the lifetime class that bounds enforcement
- [Data Classification, Governance & Retention (STD-GLB-007)](../../02-standards/_global/STD-GLB-007-data-governance.md) — retention of Membership history through offboarding

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Organization Writes the Projection Directly to Keycloak

- **Pros**: removes the outbox, the broker, the consumer, and the eventual-consistency window. Fewer components and immediate projection consistency.
- **Cons**: requires the Organization authority to hold the Keycloak administration credential, making every defect in Tenant, invitation, or Membership code a path to authenticator reset for every Principal. Produces a second writer over one store, so two reconciliation loops repair toward two views. Couples Membership commit availability to Keycloak availability, which converts a revocation into a failure rather than a delay.
- **Why Rejected**: the credential blast radius alone is disqualifying, and it cannot be mitigated by review because the capability follows the credential rather than the code.

### Alternative B: Keycloak Holds Membership Authority

- **Pros**: one store, no projection, no drift, no reconciliation.
- **Cons**: Membership carries versions, effective dates, invitation provenance, and offboarding state that a directory does not model. Reconstructing authority would require restoring the identity kernel, coupling two independent recovery objectives. Exiting the vendor would become an authority migration rather than a credential migration.
- **Why Rejected**: `EAD-003` places authority with the owning domain, and a vendor directory holding enterprise authority makes vendor replacement a data-ownership problem.

### Alternative C: A Shared Database Between Organization and Identity Control

- **Pros**: no propagation delay, no event contract, and both services read one consistent state.
- **Cons**: the strongest and least reversible form of coupling, prohibited outright by `EAD-003 §6.5`. Either domain's schema change becomes the other's deployment.
- **Why Rejected**: prohibited by enterprise policy, and the policy exists because this is the precise mechanism by which decomposed services re-fuse.

### Alternative D: Synchronous API Call from Organization to Identity Control

- **Pros**: keeps the Keycloak credential contained in Identity Control while removing the broker.
- **Cons**: the Membership transaction either commits before the call, reintroducing the dual-write inconsistency the outbox exists to prevent, or holds a transaction open across a network call to another domain. Availability of the Membership write becomes dependent on Identity Control being reachable.
- **Why Rejected**: contains the credential and reintroduces the dual-write problem. The outbox achieves containment without the coupling.
