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

**The Admin Portal shows the validation and offers no command (2026-10-09).** Its _Emergency access_ page reads the Identity Control API's list of its scope's emergency grants: each holder, last use or never, the number of uses, and the date validation falls due, an overdue one marked. It grants, revokes and validates nothing. The grants are Organization Control's records, validation is a drill the holder performs on purpose, and a grant no longer needed is revoked in Organization Control. Microsoft's guidance is the same practice: "Regularly conduct drills to validate the functionality of the accounts and to confirm that monitoring and alerting rules are triggered in case an account is misused", "At least every 90 days" [R5]. A button that marked a grant validated would record a validation no drill performed.

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

That last sentence was not true until §5.6 (2026-10-08). The privileged-access record named the actor, the correlation and the reason, and not the authority it acted on, so a review could not tell an emergency use from an activation, or name the activation.

### 5.6 The Privileged-Access Record Is Read and Reviewed (2026-10-08)

The Organization Control API writes one privileged-access row for each provider-scoped transaction, before the transaction runs. Until this section, no runtime role could read it, and no route served it. The review the runbooks ask for needed SQL on the migration credential. NIST requires that review: "Review and analyze system audit records [Assignment: frequency] for indications of [Assignment: inappropriate or unusual activity]" (AU-6 a.) [R9], and logging privileged functions exists so that misuse can be found: "Logging and analyzing the use of privileged functions is one way to detect such misuse" (AC-6(9)) [R9].

**What each row records.** Beside the actor, the correlation, the reason and the time, a row records:

- **the authority it acted on:** `emergency`, `activation`, `eligible` (a grant holder with nothing in force, on the activation routes) or `consumer` (a registered projection consumer);
- **the activation,** when the authority was one;
- **the Tenant,** when the access named exactly one: the Tenant a provider act is bound to, or the `{tenant_id}` in the route's path;
- **the operation:** the method and route pattern, such as `POST /v1/tenants/{tenant_id}/suspend`.

AU-3 asks a record to establish "What type of event occurred", "Where the event occurred", "Source of the event" and the "Identity of any individuals, subjects, or objects/entities associated with the event" [R9]. Google's Access Transparency entries likewise include "the affected resource and action, the time of the action, the reason for the action, and information about the accessor" [R12]. What a row does not record is the outcome. It is written before the work, so that a transaction that fails still leaves evidence. The outcome is the request log's, joined by the correlation identifier.

**Who reads it.**

- **A provider in force reads every row.** The read is a provider read with its reason, so it leaves a row of its own. A grant holder with nothing in force and a registered consumer read nothing. NIST makes reading a permission given per role: "Permitted actions are enforced by the system and include read, write, execute, append, and delete" (AU-6(7)) [R9]. Entra lets its administrator and reader roles read PIM's resource audit, and each user read their own activity in "My audit" [R10].
- **A Tenant administrator reads the provider access to its own Tenant:** the rows that name its Tenant, without the consumer rows. Neither of the vendors whose provider access matches this case keeps that record from the customer. Google's Access Transparency logs "record the actions that Google personnel take when accessing Customer Data", and the customer chooses who reads them, "by assigning a user or group the Private Logs Viewer role" [R12]. In Microsoft's Customer Lockbox, the customer approves each request, and "the actions taken in this workflow are logged" in the customer's own activity or audit log [R13]. A row that names no Tenant, such as a list across Tenants, is shown to no Tenant.
- **Nobody changes or deletes a row.** No runtime role holds `UPDATE` or `DELETE` on the record, and no maintenance step purges it. AU-9 asks to "Protect audit information and audit logging tools from unauthorized access, modification, and deletion" [R9].

**Separation of duties.** A provider may read its own rows, as Entra's "My audit" shows a user their own activity [R10]. It may not attest to them. Every review is of one provider's access, and the database refuses a review recorded by the provider whose access it reviews. That is the rule activation approval already follows (§5.1): two people, one of whom is not the subject. NIST names the concern: "Individuals or roles with privileged access to a system and who are also the subject of an audit by that system may affect the reliability of the audit information" (AU-9(4) discussion) [R9]. AC-5 asks to "Define system access authorizations to support separation of duties" [R7]. Entra allows "Members (self)" as reviewers of their own role assignments [R11]. This decision does not: a provider is the most privileged subject in the estate.

**A review is recorded.** A review names:

- the provider whose access it reviewed;
- the period, from inclusive to exclusive, which ends no later than when the review is recorded;
- the outcome: `appropriate`, or `escalated` when a use is raised as possible misuse;
- the reviewer's statement;
- the number of accesses, and of emergency accesses, the period held when the review was recorded.

Reviews are inserted and never changed. The statement is required, as Entra's access reviews can require a reviewer "to supply a reason for approval or denial" [R11], and its review history keeps the "Justification for review result provided by reviewer" [R11]. Approving is one of the actions NIST says non-repudiation covers: "creating information, sending and receiving messages, and approving information" (AU-10 discussion) [R9].

**A review is due weekly.** A provider's access is unreviewed until a review of that provider covers the instant it occurred. Seven days after the instant, it is overdue. CIS: "Conduct reviews of audit logs to detect anomalies or abnormal events that could indicate a potential threat. Conduct reviews on a weekly, or more frequent, basis" (Safeguard 8.11) [R14]. The Organization Control API reports, for each provider, the unreviewed accesses, the emergency ones among them, and the date the oldest falls due. The report is a route, and a `WARN` from the daily maintenance stage, like the emergency grant report (§5.2). Each emergency use is counted on its own, because Microsoft asks for a review "After any use of an emergency access account" [R5]. Consumer rows are not due: a consumer is a workload, reviewed through its owner (`ADR-IAM-003 §5.8`).

**The grants are reviewed separately.** Who holds provider authority is reviewed every 90 days, through the grant list (§5.2, and NIST AC-6(7) [R9]). That review asks whether a grant is still needed. This one asks what was done with it.

**The record is kept.** CIS asks to "Retain audit logs across enterprise assets for a minimum of 90 days" (Safeguard 8.10) [R14]. Entra's PIM audit keeps 30 days, and Microsoft says to route it elsewhere "to retain audit data for longer" [R10]. Neither period is long enough here. A row is needed until a review covers it, and an investigation may come after that. AU-11 leaves the period to the organization [R9], and `SAD-004 §6.5` keeps privileged-administration facts "according to security/audit policy". Until a retention standard names a period, the record is not purged.

**The list form.** Both lists take the estate's form (`STD-GLB-001` 1.3.0): `after`, `limit`, named filters and the primary key's order. The filters are the provider, the Tenant, the correlation, the authority, and a time window, `from` and `to` (`STD-GLB-001` 1.6.0). CloudTrail's lookup takes the same shape: a time window, one attribute and a page token "passed in with the same parameters that were specified in the original call" [R15].

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
- **The reviewers are providers (§5.6).** The people who review provider access also administer access. AC-5 asks to ensure "that security personnel who administer access control functions do not also administer audit functions" [R7]. The record is not administered by anyone at runtime, since no role changes or deletes it, and the review is held to a second person. Even so, a dedicated audit reviewer who holds no provider authority would be stronger. The Tenant administrator's read is the independent check in its place: the customer sees what the provider did in its Tenant.
- **A Tenant sees only what names it (§5.6).** A provider read across Tenants, or a read of a record addressed by its own identifier, such as an offboarding, records no Tenant. That access to a Tenant's data is reviewed by providers, and is not shown to the Tenant.
- **The weekly review is a workload,** for the providers who act. A week with no provider access costs nothing. A week of an incident costs a review of every provider who acted.
- **The record grows without bound** until a retention standard names a period.

### Operational

- Reported:
  - fewer than two emergency grants in production;
  - every request an emergency grant authorizes;
  - an emergency grant unused for 90 days;
  - activation requests waiting past four hours;
  - the projection past its freshness budget;
  - a provider's access unreviewed for more than seven days (§5.6).
- Runbooks required before production:
  - activation and approval;
  - emergency grant use and post-use review;
  - quarterly emergency grant validation;
  - the provider-access review (§5.6).

## 7. Compliance Impact

### Related Standards

- [ADR-ORG-001](ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) §5.7 and §5.11: projection consumers and provider grants.
- [ADR-IAM-001](../identity-access-platform/ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.6 and §5.11: the provider scope's projection, and the bootstrap ceremony.
- [ADR-IAM-003](../identity-access-platform/ADR-IAM-003-client-registration-ownership.md) §5.4 and §5.7: authority separated by route, and two-person control placed at activation.
- STD-IAM-002 §3.1.1: the provider-scope form.
- [STD-GLB-001](../../02-standards/_global/STD-GLB-001-api-design.md) 1.5.0: the list form and its time window, which the privileged-access lists take (§5.6).

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

### Alternative F — The Record Read Only with SQL on the Migration Credential (§5.6)

**Benefits:** no runtime role can read the evidence, so no compromised runtime credential discloses it.

**Rejected because:** the review then needs the most powerful credential in the deployment, the one that owns every table. Nothing records the review, and nothing reports one that is overdue. A Tenant cannot see what a provider did in it at all.

### Alternative G — A Dedicated Audit-Reviewer Authority (§5.6)

**Benefits:** the people who review provider access would hold no provider authority, which is AC-5's separation of access administration from audit [R7], and Entra's Security Reader.

**Rejected for now because:** no such population exists in this estate, and a new kind of grant would need its own grant, activation and review. The review is held to a second provider instead, and the Tenant administrator's read gives a check from outside the providers. Revisit it once a security team that is not the provider team operates the platform.

### Alternative H — A Provider Reviews Its Own Access (§5.6)

**Benefits:** a provider with no peer available can still record a review, as Entra's "Members (self)" reviewers do [R11].

**Rejected because:** an attestation by its own subject is the case AU-9(4)'s discussion warns about [R9]. Production already requires two providers to approve an activation (§5.1), so a second reviewer exists wherever activations do.

## 9. References

### Normative

- **[R6]** NIST SP 800-53 Rev. 5, AC-2(6) Dynamic Privilege Management. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Implement [organization-defined dynamic privilege management capabilities]": privileges decided at runtime, so that they can be revoked at once.
- **[R7]** NIST SP 800-53 Rev. 5, AC-5 Separation of Duties. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. "Identify and document [organization-defined duties of individuals]" and "Define system access authorizations to support separation of duties". The discussion: "Separation of duties includes dividing mission or business functions and support functions among different individuals or roles, conducting system support functions with different individuals, and ensuring that security personnel who administer access control functions do not also administer audit functions." Discussion quoted from NIST's OSCAL catalog, accessed 2026-10-08.
- **[R9]** NIST SP 800-53 Rev. 5, from NIST's OSCAL catalog, <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>, accessed 2026-10-08. The catalog renders each parameter by its label, such as "[Assignment: frequency]".
  - AU-3: "Ensure that audit records contain information that establishes the following:" "What type of event occurred;" "When the event occurred;" "Where the event occurred;" "Source of the event;" "Outcome of the event; and" "Identity of any individuals, subjects, or objects/entities associated with the event."
  - AU-6 a.: "Review and analyze system audit records [Assignment: frequency] for indications of [Assignment: inappropriate or unusual activity] and the potential impact of the inappropriate or unusual activity;"
  - AU-6(7) Permitted Actions: "Specify the permitted actions for each [Selection (one or more): system process; role; user] associated with the review, analysis, and reporting of audit record information." Discussion: "Permitted actions are enforced by the system and include read, write, execute, append, and delete."
  - AU-9 a.: "Protect audit information and audit logging tools from unauthorized access, modification, and deletion; and"
  - AU-9(4) Access by Subset of Privileged Users: "Authorize access to management of audit logging functionality to only [Assignment: subset of privileged users or roles]." Discussion: "Individuals or roles with privileged access to a system and who are also the subject of an audit by that system may affect the reliability of the audit information by inhibiting audit activities or modifying audit records."
  - AU-10 discussion: "Types of individual actions covered by non-repudiation include creating information, sending and receiving messages, and approving information."
  - AU-11: "Retain audit records for [Assignment: time period] to provide support for after-the-fact investigations of incidents and to meet regulatory and organizational information retention requirements."
  - AC-6(7) (a): "Review [Assignment: frequency] the privileges assigned to [Assignment: roles and classes] to validate the need for such privileges; and"
  - AC-6(9): "Log the execution of privileged functions." Discussion: "Logging and analyzing the use of privileged functions is one way to detect such misuse and, in doing so, help mitigate the risk from insider threats and the advanced persistent threat."

### Informative

- **[R1]** Microsoft, _What is Privileged Identity Management?_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure>. Eligible and active assignments, just-in-time and time-bound access, approval to activate, justification, notifications, access reviews and audit history.
- **[R2]** Microsoft, _Configure Microsoft Entra role settings in PIM_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings>. Activation maximum duration "from one to 24 hours"; "Require approval for activation of an eligible assignment. The approver doesn't have to have any roles … We recommend that you select at least two approvers."
- **[R3]** Microsoft, _Approve requests for Azure resource roles in PIM_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-resource-roles-approval-workflow>. "If a request isn't approved within 24 hours, then the eligible user must resubmit a new request."
- **[R4]** Google Cloud, _Privileged Access Manager overview_, accessed 2026-10-02. <https://docs.cloud.google.com/iam/docs/pam-overview>. Entitlements, eligible principals, grant requests, optional approval, maximum grant duration, justification, and audit logging of entitlement and grant events.
- **[R5]** Microsoft, _Manage emergency access admin accounts_, accessed 2026-10-06. <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access>. At least two emergency access accounts; their role "permanent active (not eligible)"; every use alerted on and reviewed; the lockout when approval is required and no one active can approve. Validation: "Validate that the emergency access accounts can sign in and perform administrative tasks", "At least every 90 days"; the post-mortem asks whether a use was "For a planned drill to validate its suitability", "In response to an actual emergency where no administrator could use their regular accounts", or "As a result of misuse or unauthorized usage of the account". And: "Regularly conduct drills to validate the functionality of the accounts and to confirm that monitoring and alerting rules are triggered in case an account is misused" (accessed 2026-10-09). "After any use of an emergency access account, conduct a review to determine whether the use was authorized and whether the actions taken were appropriate."
- **[R10]** Microsoft, _View audit history for Microsoft Entra roles in PIM_, accessed 2026-10-08. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-use-audit-log>. "Data is available for the past 30 days." "If you want to retain audit data for longer than the default retention period, you can use Diagnostic Settings in Azure Monitor to route it to an Azure storage account or Log Analytics." The resource audit is read after signing in "as a Global Administrator, Global Reader, Privileged Role Administrator, Security Administrator, or Security Reader"; "Use the My audit blade to view your role activity for Microsoft Entra role assignment and PIM policy management."; "Filter the history using a predefined date or custom range."
- **[R11]** Microsoft, _Create an access review of Azure resource and Microsoft Entra roles in PIM_, <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-create-roles-and-resource-roles-review>; _Create an access review of groups and applications_, <https://learn.microsoft.com/en-us/entra/id-governance/create-access-review>; _Download review history_, <https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-downloadable-review-history>; accessed 2026-10-08. "Members (self) - Use this option to have the users review their own role assignments." "Justification required: Select this checkbox to require the reviewer to supply a reason for approval or denial." The review history's "Justification" field is the "Justification for review result provided by reviewer".
- **[R12]** Google Cloud, _Access Transparency overview_, <https://cloud.google.com/assured-workloads/access-transparency/docs/overview>, and _Understanding and using Access Transparency logs_, <https://cloud.google.com/assured-workloads/access-transparency/docs/reading-logs>, accessed 2026-10-08. "Access Transparency logs record the actions that Google personnel take when accessing Customer Data. Access Transparency log entries include details such as the affected resource and action, the time of the action, the reason for the action, and information about the accessor." "After you've configured Access Transparency for your Google Cloud organization, you can set controls for who can access the Access Transparency logs by assigning a user or group the Private Logs Viewer role."
- **[R13]** Microsoft, _Customer Lockbox for Microsoft Azure_, accessed 2026-10-08. <https://learn.microsoft.com/en-us/azure/security/fundamentals/customer-lockbox-overview>. "Customer Lockbox for Microsoft Azure provides an interface for your organization to review and approve or reject customer data access requests." "For auditing purposes, the actions taken in this workflow are logged in Customer Lockbox request logs." "The auditing logs for Customer Lockbox for Azure are written to the activity logs for subscription-scoped requests and to the Microsoft Entra audit log for tenant-scoped requests."
- **[R14]** Center for Internet Security, _CIS Controls Assessment Specification v8.1_, Controls 8, accessed 2026-10-08. <https://cas.docs.cisecurity.org/en/latest/source/Controls8/>. Safeguard 8.10: "Retain audit logs across enterprise assets for a minimum of 90 days." Safeguard 8.11: "Conduct reviews of audit logs to detect anomalies or abnormal events that could indicate a potential threat. Conduct reviews on a weekly, or more frequent, basis." The safeguard text on cisecurity.org's control pages is loaded by script; this is CIS's own specification of it.
- **[R15]** Amazon Web Services, _LookupEvents_, AWS CloudTrail API Reference, accessed 2026-10-08. <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_LookupEvents.html>. StartTime: "Specifies that only events that occur after or at the specified time are returned." EndTime: "Specifies that only events that occur before or at the specified time are returned." NextToken: "This token must be passed in with the same parameters that were specified in the original call."
