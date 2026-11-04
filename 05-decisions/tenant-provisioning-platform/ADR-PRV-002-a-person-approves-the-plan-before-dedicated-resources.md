---
doc_meta:
  id: ADR-PRV-002
  title: A Person Approves the Plan Before Any Dedicated Resource Is Created
  adr_type: foundational
  status: accepted
  created: 2026-11-04
  created_date: 2026-11-04
  created_by: Platform Engineering
  governed_by: [PAD-PLT-017]
---

# ADR-PRV-002: A Person Approves the Plan Before Any Dedicated Resource Is Created

## 1. Title

A bridge, silo or regional Tenant is built only after a second person approves the exact plan the provisioning service computed for it. The approval is recorded by the provisioning service, beside the plan it approves. A pooled Tenant needs no approval.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                            | Approver               |
| :--------- | :------- | :----------- | :------------------------------------------------------------------- | :--------------------- |
| 2026-11-04 | accepted | foundational | Architecture, Core Platform, Platform Engineering, Security, Product | Architecture Authority |

The owner approved this decision on 4 November 2026, after the design was merged in scnehaux-architecture #146 and ratified there.

## 3. Context

A pooled Tenant adds configuration and quota rows to shared infrastructure. It costs almost nothing and creates no resource. A bridge, silo or regional Tenant creates resources that cost money every month and that a contract usually names: a dedicated schema or database, a per-Tenant encryption key, a region (`PAD-PLT-017 §3.4`). Creating one by mistake, or for a customer whose contract does not cover it, is a cost and a contract problem that no technical check catches.

Organization Control records the desired state: who the Tenant is and which isolation profile it needs. It does not own infrastructure or its cost (`PAD-PLT-002 §1.2`). The person creating the Tenant therefore cannot see what will be built or what it will cost. Only the provisioning service can, once it has computed its plan (`ADR-PRV-003`).

Organization Control already requires a second person for privileged acts: an eligible provider grant confers authority only while an activation approved by another provider lasts, and self-approval is refused (`ADR-ORG-002`).

## 4. Decision Drivers

- No dedicated resource is created without a person deciding it should be.
- The approver sees what will actually be built and an estimate of its cost, not only a profile name.
- What runs is exactly what was approved.
- The person who requested the Tenant does not approve it.
- A pooled Tenant stays fully automatic.
- An approval nobody gives does not leave a request open forever.

## 5. Decision

### 5.1 What Needs Approval

| Profile                     | Approval before build | Why                                                            |
| :-------------------------- | :-------------------- | :------------------------------------------------------------- |
| `pooled`                    | No                    | Configuration and quotas only; no new resource, no cost        |
| `bridge`                    | Yes                   | A schema or database in a shared cluster; storage cost         |
| `silo`                      | Yes                   | Dedicated database and key; monthly cost; contract terms       |
| `regional`                  | Yes                   | As silo, in a named region; residency terms                    |
| Any profile, deprovisioning | See `ADR-PRV-005`     | Release is already a provider decision in Organization Control |

### 5.2 The Approver Approves a Plan

1. The service computes the plan for the request and saves it unchanged (`ADR-PRV-003 §5.3`).
2. It records the plan's hash, the resources it creates, the region, and a monthly cost estimate.
3. It reports progress to Organization Control with the stage `awaiting_approval` and an `expected_by` 7 days ahead (`ADR-PRV-001 §5.4`).
4. An approver opens the request in the provisioning panel (`SAD-021 §5.5`), reads the plan summary, and approves or rejects it. Both need a reason; approval also needs the contract or order reference that covers the cost.
5. On approval the service applies the saved plan whose hash was approved, and nothing else [R1]. If that apply fails because the infrastructure changed after planning, the service plans again and asks for approval again.
6. On rejection, or when 7 days pass with no decision, the service reports `failed` with the cause `approval_rejected` or `approval_expired`. A new attempt is a retry in Organization Control, which creates a new request and a new plan.

### 5.3 Who Approves

- **A provider holding the `provider:provisioning` scope, in force.** The scope is a provider grant recorded by Organization Control, eligible and activated as `ADR-ORG-002` requires, and projected to the provisioning service as `provider:identity-control` is projected to identity-control (`ADR-ORG-002 §5.3`). The provisioning service enforces it.
- **Not the requester.** The service refuses an approval by the principal that requested the Tenant. Organization Control adds `requested_by` to each item of the outstanding-request read for this check (`SAD-004 §7.5`, Phase 2).
- **The Platform Engineering lead holds it.** The owner decided this on 4 November 2026 (`SAD-021 §15`, question 2). The grant is recorded by role, never by a person's name in any document. A second holder may be added by the same decision path; the requester rule above still applies to every holder.

### 5.4 Where Approval Is Recorded

The approval is the provisioning service's record, in its own database, in an insert-only table kept 7 years, the audit-log period of `STD-GLB-007`. Each row holds the request, the plan hash, the decision, the approver's `principal_id`, the reason, the contract reference and the time. Each decision also emits an audit event.

Organization Control records only what it owns: the request's progress stage and, at the end, `realized` or `failed`. It does not hold a copy of the approval.

### 5.5 Before Phase 2

Until the approval gate, the progress report and the panel are built (Phase 2, `SAD-021 §13`), the service builds pooled Tenants only. It reports a bridge, silo or regional request `failed` with the cause `profile_not_supported`. No non-pooled Tenant is created before Phase 2 is complete.

## 6. Consequences

### Positive

- No dedicated resource exists without a recorded decision by a second person.
- The approver decides on the real plan and its cost.
- The approval and the plan are stored together, so an auditor can see what was approved and that it is what ran.

### Negative

- A non-pooled Tenant waits for a person, up to 7 days.
- The scope `provider:provisioning` needs an activation surface. Activation of a scope other than `provider:organization-control` is not built in any console today (the open item on `provider:identity-control` activation). Phase 2 depends on it.
- While one person holds most roles (`ISMS-004` R19), a second approver may not exist. Then no non-pooled Tenant can be built, which is the intended result.

### Operational

- Requests waiting for approval are shown in the panel and alerted at 24 hours and at 6 days (`SAD-021 §9.3`).
- Approvals are reviewed in the provider access review, as other provider acts are.

## 7. Compliance Impact

### Related Standards and Artifacts

- `ADR-ORG-002` — eligible provider authority and self-approval refusal.
- `STD-GLB-007` — 7-year audit retention.
- `ISMS-005` — A.5.3 segregation of duties and A.8.32 change management.

### Compliance Status

Accepted.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Approve in Organization Control Before the Request Is Sent

**Benefits:** one approval model, in the system that already has eligible grants.

**Rejected because:** the approver would approve a profile name, not a plan or a cost. Organization Control does not own infrastructure (`PAD-PLT-002 §1.2`) and cannot compute either.

### Alternative B — Approve a Pull Request in a Repository of Declared Resources

**Benefits:** review tools and history come with the repository, as `STD-GLB-009` §Internal Developer Platform (IDP) Interfaces describes for team resources.

**Rejected because:** a Tenant is created at run time by a customer journey, not by a team's change. A pull request per Tenant would put customer names and resource identifiers in a repository, and the approval would sit outside the service that enforces it.

### Alternative C — No Approval; Limit Cost with Quotas

**Benefits:** fully automatic for every profile.

**Rejected because:** a quota limits how much, not whether a contract covers it. The owner's brief requires a person to approve because of cost and contract terms.

### Alternative D — Approve in a Ticketing Tool

**Benefits:** familiar to operators.

**Rejected because:** the service could not enforce it, and the record would not be bound to the plan that ran.

## 9. References

### Informative

- **[R1]** OpenTofu, _Command: plan_ and _Command: apply_, accessed 2026-11-04. <https://opentofu.org/docs/cli/commands/plan/>, <https://opentofu.org/docs/cli/commands/apply/>. "You can use the optional `-out=FILE` option to save the generated plan to a file on disk, which you can later execute by passing the file to `tofu apply` as an extra argument"; "When you pass a saved plan file to `tofu apply`, OpenTofu takes the actions in the saved plan without prompting you for confirmation." Supports §5.2: the approved plan is the one applied.
