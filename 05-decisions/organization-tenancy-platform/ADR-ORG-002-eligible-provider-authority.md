---
doc_meta:
  id: ADR-ORG-002
  title: Eligible Provider Authority, Activated for a Bounded Time and Approved by Another Provider
  adr_type: foundational
  status: accepted
  created: 2026-10-02
  created_date: 2026-10-02
  created_by: Core Platform Team
  governed_by:
    - PAD-PLT-002
---

# ADR-ORG-002: Eligible Provider Authority, Activated for a Bounded Time and Approved by Another Provider

## 1. Title

Eligible provider authority, activated for a bounded time and approved by another provider, and checked from records wherever it is used.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| :--------- | :------- | :----------- | :------------------------ | :------------------- |
| 2026-10-02 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

A provider grant (`ADR-ORG-001 §5.11`) is standing. Once made, the Principal holding it is a provider on every request until the grant is revoked, and nothing about a provider's action needs a second person. `ADR-IAM-003 §5.7` recorded what follows from that. One provider, or one compromised provider account, can do everything a provider does alone: register a production client, grant ownership, retire a Principal, adopt a client. It also placed the remedy at the activation of provider authority, where the established platforms put it, and left the decision to this record.

Two facts about the current model shape the decision:

- **The two services that check provider authority check it differently.** The Organization Control API reads its own grant record for each request (`ADR-ORG-001 §5.11`). The Identity Control API reads a `provider_scope` claim from the token, which `ADR-IAM-001 §5.6` says Organization's grant is projected into through the kernel. That projection was never built: the only writer of the kernel attribute is the identity bootstrap ceremony, so in practice `provider:identity-control` is held by one Principal, permanently, in the kernel.
- **A claim outlives its revocation until the token expires.** `ADR-ORG-001` Alternative G rejected realm roles for that reason. A time-bound activation carried in a claim would end when the token does, not when the activation does.

## 4. Decision Drivers

- **Least privilege in time.** A provider is a provider only while it needs to be [R1][R6].
- **Separation of duties.** Provider authority in production starts with a second person's approval [R2][R7].
- **Revocation takes effect at the next request,** as it already does at the Organization Control API.
- **One authority for provider grants.** `PAD-PLT-002 §3.1` places provider authority in Organization, and no second service records it.
- **No lockout.** Requiring approval must not leave a deployment with no one able to approve [R5].

## 5. Decision

### 5.1 A Provider Grant Is Eligible; Authority Is an Activation

A provider grant makes a Principal **eligible** for a scope. It confers nothing until it is **activated**, and an activation lasts at most the time it was approved for. This is Entra Privileged Identity Management's model: "an eligible assignment … requires a user to perform one or more actions to use the role", and "once activated, the user can use the role for a preconfigured period of time before they need to activate again" [R1]. Google Cloud's Privileged Access Manager models it the same way: an entitlement names "a set of principals who are allowed to request a grant", and the roles are granted "until the end of the grant duration" [R4].

An activation names:

- the grant;
- the duration asked for, at most the scope's maximum (`ORGANIZATION_PROVIDER_ACTIVATION_MAX`, default `8h`, where Entra allows one to 24 hours [R2]);
- the reason;
- who approved it, and when;
- when it ends.

It ends at the earliest of:

- the end of its duration;
- the holder ending it;
- any provider ending it, with a reason;
- the grant being revoked;
- the holder's Principal ceasing to be an active person.

**In production an activation is approved by another provider.** The approver is a Principal that holds a grant for the same scope, eligible or emergency, other than the requester. The approver does not need an active activation of its own, as an Entra approver "doesn't have to have any roles" [R2]. An unapproved request lapses after 24 hours, as Entra's does [R3].

**Outside production** a deployment may let an eligible provider activate with a reason alone (`ORGANIZATION_PROVIDER_ACTIVATION_APPROVAL`, `required` by default). A development environment often has one provider, and approval is optional per role in both Entra and Google [R2][R4].

### 5.2 Emergency Grants Are Standing, Few and Watched

A deployment in which every grant is eligible and approval is required can lock itself out: the case Entra names is that no one active remains to approve, "and tenant administration is effectively locked" [R5]. An **emergency grant** is therefore standing, as Entra assigns its emergency access accounts' role "as permanent active (not eligible)" [R5], and it is held to the same guardrails:

- **At least two in production.** Fewer is reported.
- **Every request one authorizes is reported at WARN,** with the Principal and the operation, so that use is alerted on and reviewed [R5].
- **Each is validated at least every 90 days.** One unused for longer is reported [R5].
- **An emergency grant is made and revoked like any grant,** by a provider, with a reason.

**Validation is a use, recorded where the grant is used (2026-10-06).** Microsoft's check is a drill: "Validate that the emergency access accounts can sign in and perform administrative tasks", performed "at least every 90 days" [R5]. A request that an emergency grant authorizes proves exactly that: the holder signed in at the level a provider route requires, and the grant was in force. So each such request records the grant's last use, in the database of the API whose scope it is (§5.3). A drill is an ordinary request made on purpose, and its `X-Administrative-Reason` says so, which is what Microsoft's post-mortem review asks to tell apart: "For a planned drill to validate its suitability", "In response to an actual emergency", or "misuse or unauthorized usage" [R5].

A grant whose last use, or whose making when it was never used, is more than 90 days old is overdue. Each API reports its overdue grants in two ways: at `WARN` on a schedule, and on a route that lists every emergency grant of its scope with its last use. No other service is asked.

The first grant, made by the single-use bootstrap command (`ADR-ORG-001 §5.11`), is an emergency grant. Before any other provider exists, it is the only one that can approve.

### 5.3 Checked from Records Where It Is Used

**The Organization Control API reads the activation for each request,** as it reads the grant today. A provider is a caller with an active activation, or an emergency grant, for `provider:organization-control`.

**The Identity Control API reads a local projection.** It no longer reads a `provider_scope` claim. It registers as a projection consumer (`ADR-ORG-001 §5.7`), subscribed to the provider authority event types (`ADR-GLB-018 §5.1`), of `provider:identity-control` grants and activations, keeps them in its own database, and reads them for each request by the token's `principal_id`, as Google Cloud IAM and Kubernetes evaluate the policy the resource holds [`ADR-IAM-001` R34, R35]. Its declaration under `ADR-ORG-001 §5.7`:

| Field                     | Declaration                                                                                                                                                                |
| :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Projection                | Provider grants and activations for `provider:identity-control`: `principal_id`, kind (eligible or emergency), activation window, state                                    |
| Bootstrap                 | The consumer snapshot, then events from its frontier                                                                                                                       |
| Freshness budget          | 60 seconds                                                                                                                                                                 |
| Stale behavior            | Past the budget, activations are refused and emergency grants still honored, so an Organization outage leaves the break-glass path working                                 |
| Revocation priority       | The priority lane: an ended activation or a revoked grant is a revocation                                                                                                  |
| Maximum enforcement delay | The end of an activation's duration is evaluated locally from its recorded end, with no delay. An activation ended early or a grant revoked takes effect within the budget |
| Reconciliation target     | The consumer snapshot, compared on each sweep                                                                                                                              |

**The token carries identity and assurance only.** A provider token to either API carries `principal_id`, `subject_type` `human`, `acr` and `auth_time`, and no `provider_scope`. The Identity Control API then tells a provider from a registration owner by its records, not by the token, and keeps them apart by route as `ADR-IAM-003 §5.4` requires. `ADR-IAM-001 §5.6` and `STD-IAM-002 §3.1.1` change accordingly in the same decision.

### 5.4 The Identity Ceremony's First Provider

The identity bootstrap ceremony creates the first Principal before any Organization grant can exist (`ADR-IAM-001 §5.11`). Instead of writing a kernel attribute, it records a local emergency grant for that Principal, in the same immutable row that names the operator and the reason. That local grant is honored only until the projection delivers an emergency grant for `provider:identity-control`. From then on it is retired, and the record says when, so provider authority converges on Organization's single record.

### 5.5 What Each Activation Leaves Behind

Every request, approval, denial, activation, early end and lapse is recorded with its actor, reason and time, and the records are never rewritten. This is Entra's justification, notification and "audit history" [R1], and Google's audit logging of entitlement and grant events [R4]. Every privileged operation is already recorded under the acting `principal_id`. With activations recorded too, a review can tell which activation authorized each one.

## 6. Consequences

### Positive

- Outside an activation, a provider account confers nothing. Taking one over buys an eligibility that, in production, still needs another provider's approval.
- Every provider action in production follows a second person's decision, at activation, without a second person on each action.
- Revocation reaches the next request at both APIs: immediately at the end of an activation, and within the freshness budget for an early end.
- Provider authority has one record, Organization's, and the kernel holds none of it.

### Negative

- **Work waits on an approver.** A provider who needs authority at 03:00 needs another provider awake, or uses an emergency grant, which is reported.
- **The Identity Control API depends on the projection** for activations. Past the freshness budget only emergency grants work there.
- **The change crosses three systems.** The Organization Control API gains activations and their approval. The Identity Control API gains a consumer and replaces its claim check. The kernel's `provider_scope` attribute, and the scope that writes it, go away.
- **Emergency grants are standing authority.** They are exactly what this decision removes elsewhere, kept because the alternative is a lockout. They are few, watched and validated, and still a standing risk.

### Operational

- Reported:
  - fewer than two emergency grants in production;
  - every request an emergency grant authorizes;
  - an emergency grant unused for 90 days;
  - activation requests waiting past four hours;
  - the projection past its freshness budget.
- Runbooks required before production:
  - activation and approval;
  - emergency grant use and post-use review;
  - quarterly emergency grant validation.

## 7. Compliance Impact

### Related Standards

- [ADR-ORG-001](ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) §5.7 and §5.11: projection consumers and provider grants.
- [ADR-IAM-001](../identity-access-platform/ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.6 and §5.11: the provider scope's projection, and the bootstrap ceremony.
- [ADR-IAM-003](../identity-access-platform/ADR-IAM-003-client-registration-ownership.md) §5.4 and §5.7: authority separated by route, and two-person control placed at activation.
- STD-IAM-002 §3.1.1: the provider-scope form.

### Compliance Status

Compliant once `ADR-IAM-001 §5.6` and `STD-IAM-002 §3.1.1` are amended in the same change.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Standing Grants, Reported

**Benefits:** nothing to build beyond the report `ADR-IAM-003 §5.3` already adds.

**Rejected because:** it makes misuse visible after the fact and prevents none of it. A compromised provider account remains a provider until someone notices.

### Alternative B — Carry the Activation in the Token, Projected into the Kernel

**Benefits:** it is the path `ADR-IAM-001 §5.6` describes, and a resource reads authority from the token alone.

**Rejected because:** an activation ended early, or a grant revoked, would keep authorizing until each token carrying it expires. Each activation would also be a kernel write, and a failed one leaves a claim behind. `ADR-ORG-001` Alternative G rejected realm roles for the same staleness.

### Alternative C — The Identity Control API Records Its Own Provider Grants

**Benefits:** no projection and no dependency on Organization's availability.

**Rejected because:** `PAD-PLT-002 §3.1` places provider authority in Organization. Two services recording grants for the same people is two authorities, and the review of who is a provider would have to read both.

### Alternative D — Ask the Organization Control API on Each Request

**Benefits:** the freshest possible decision and no local copy.

**Rejected because:** `ADR-ORG-001` Alternative E rejects a synchronous Tenancy decision on every request. It is a runtime dependency on every privileged call, and an Organization outage would take the emergency path down with it.

### Alternative E — Approval for Each Privileged Action

**Benefits:** a second person on every action.

**Rejected because:** it is not how the platforms this decision follows constrain their administrators (`ADR-IAM-003` Alternative E). It would also put a second person in front of routine work such as key rotation and incident containment, which then waits.

## 9. References

### Normative

- **[R6]** NIST SP 800-53 Rev. 5, AC-2(6) Dynamic Privilege Management. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Implement [organization-defined dynamic privilege management capabilities]": privileges decided at runtime, so that they can be revoked at once.
- **[R7]** NIST SP 800-53 Rev. 5, AC-5 Separation of Duties. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Identify and document [organization-defined duties of individuals]" and "Define system access authorizations to support separation of duties".

### Informative

- **[R1]** Microsoft, _What is Privileged Identity Management?_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure>. Eligible and active assignments, just-in-time and time-bound access, approval to activate, justification, notifications, access reviews and audit history.
- **[R2]** Microsoft, _Configure Microsoft Entra role settings in PIM_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings>. Activation maximum duration "from one to 24 hours"; "Require approval for activation of an eligible assignment. The approver doesn't have to have any roles … We recommend that you select at least two approvers."
- **[R3]** Microsoft, _Approve requests for Azure resource roles in PIM_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-resource-roles-approval-workflow>. "If a request isn't approved within 24 hours, then the eligible user must resubmit a new request."
- **[R4]** Google Cloud, _Privileged Access Manager overview_, accessed 2026-10-02. <https://docs.cloud.google.com/iam/docs/pam-overview>. Entitlements, eligible principals, grant requests, optional approval, maximum grant duration, justification, and audit logging of entitlement and grant events.
- **[R5]** Microsoft, _Manage emergency access admin accounts_, accessed 2026-10-06. <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access>. At least two emergency access accounts; their role "permanent active (not eligible)"; every use alerted on and reviewed; the lockout when approval is required and no one active can approve. Validation: "Validate that the emergency access accounts can sign in and perform administrative tasks", "At least every 90 days"; the post-mortem asks whether a use was "For a planned drill to validate its suitability", "In response to an actual emergency where no administrator could use their regular accounts", or "As a result of misuse or unauthorized usage of the account".
