---
doc_meta:
  id: ADR-IAM-003
  title: Client Registration Ownership and the Developer Console's Authority
  adr_type: foundational
  status: accepted
  created: 2026-10-01
  created_date: 2026-10-01
  created_by: Identity Platform Team
---

# ADR-IAM-003: Client Registration Ownership and the Developer Console's Authority

## 1. Title

Client Registration Ownership and the Developer Console's Authority.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

The Identity Control Service registers every protocol client and protected resource, holds their public keys, and reconciles them against the identity kernel (`ADR-IAM-001 §5.12`, `§5.13`). Every one of its routes requires a provider-scope token naming `provider:identity-control` (`STD-IAM-002 §3.1.1`), so only a provider can register a client, rotate its key or change its redirect URIs.

`SAD-002` gives application teams a Developer Console for that work, and `TDD-identity-experience-004` designs it: registration, redirect URIs, audiences, the lifetime class, and the client's key rotation, with approval required for a production client. Nothing decides which team may act on which registration. Until something does, the console could only be used by providers, and an application team rotating its own key waits on an operator, which is how keys reach their expiry.

Three facts bound the choice:

- The Identity Control Service is the registration authority, and the kernel is not to become a second one (`ADR-IAM-001 §5.6`, `§5.7`).
- A token carries no role (`STD-IAM-002 §3.2`), and the resource that holds a grant checks its own record (`STD-IAM-002 §3.1.1`, `ADR-ORG-001 §5.11`).
- The Software Catalog, which would say which team owns which Application, is unchartered. A registration's `application_ref` is entered administratively and proves nothing about who owns it.

## 4. Decision Drivers

- **Least privilege.** A team manages its own clients and nothing else [R2].
- **Separation of duties.** The person who proposes a change to a production client's trust configuration does not also approve it [R1].
- **Bounded, attributable authority.** Every grant names a Principal, a target, who granted it and why, and ends when the person does [R3].
- **No new kernel authority and no role in a token.**
- **A path to grouping.** When the Software Catalog exists, ownership moves to the Application without redesign.

## 5. Decision

### 5.1 A Registration Has Owners

The Identity Control Service records the owners of each registration: active human Principals, each granted by a provider with a reason, in an insert-only history that names who granted and who revoked. This is the model Microsoft Entra uses, where owners assigned to an application can manage that application and only that one [R4][R5], and the one Okta reaches with an administrator role constrained to a set of applications [R6].

- **An owner is a person.** A workload, and a Principal that is not active, holds no ownership.
- **Ownership ends with the person.** A Principal retired, quarantined or disabled confers nothing from the next request, and its ownerships are reported for reassignment.
- **A production registration keeps at least two owners**, so one departure does not orphan it. Removing the second-to-last owner of a production registration is refused.
- **Ownership is reviewed at least quarterly** by the owners, as account reviews are required at a defined frequency [R3]. A registration with no active owner is reported.

### 5.2 What an Owner May Do

| Action                                                                         | Owner                                          | Provider                                       |
| :----------------------------------------------------------------------------- | :--------------------------------------------- | :--------------------------------------------- |
| Read the registration, its keys and its findings                               | yes                                            | yes                                            |
| Rotate to a new public key; revoke a key                                       | yes                                            | yes                                            |
| Suspend the client, which is reversible                                        | yes                                            | yes                                            |
| Restore a suspended client                                                     | yes                                            | yes                                            |
| Propose a redirect URI, audience or lifetime-class change                      | yes                                            | yes                                            |
| Apply that change to a non-production registration                             | yes                                            | yes                                            |
| Apply that change to a production registration                                 | approved by a provider other than the proposer | approved by a provider other than the proposer |
| Change the profile or audience class; retire; adopt; grant or revoke ownership | no                                             | yes                                            |

Key rotation needs no approval. It is the operation the console exists to make routine, it changes no trust relationship, and a rotation that waits for someone is a rotation that waits until the key expires. Suspension is offered to owners because a team that finds its key leaked contains the client first and asks afterwards. Retirement, which deletes the client, stays a provider's.

**A production change is a proposal until a second person approves it** [R1]. The proposal records the configuration, the proposer, the reason and the validated preview, and the approver sees the same preview. A provider proposing a production change does not approve their own. Whether a deployment is production is the deployment's setting, not the request's.

### 5.3 Creating a Registration

A provider grants a Principal **application developer** standing, with a reason, as Entra's Application Developer role grants the ability to create registrations once self-service is restricted [R4]. Such a Principal creates non-production registrations and becomes their first owner. An application developer's production registration is created only by approval: the developer proposes it, naming at least two owners, and a provider other than the proposer approves it.

**A provider creates a registration directly**, in production too, as Entra's Application Administrator "can create and manage all aspects of … application registrations" [R4]. The role carries no approval of its own; Entra adds a second person, where an organization wants one, when the role is activated (§5.7) [R8]. A provider is already the privileged administrator of the registration authority, and its direct creation is recorded under its `principal_id`. A provider's direct creation in production is reported each time, so a review sees every one. §5.7 records where two-person control over providers belongs instead.

### 5.4 Where Authority Is Checked, and the Token

The Identity Control Service holds ownership and application-developer grants and reads them for each request, by the token's `principal_id` and the registration the request names, as Organization Control reads its provider grants (`ADR-ORG-001 §5.11`). Nothing is projected into the kernel, and no claim or role names an owner.

The token is the `privileged` class in a third form, `STD-IAM-002 §3.1.1`'s **`resource-scoped`** form: `principal_id`, `subject_type` `human`, `acr` and `auth_time`, no `tenant_id`, and an authority the resource looks up rather than reads. A token that also carries `provider_scope` naming `provider:identity-control` is a provider's, and is served as one.

**The two authorities are separated by route, not by trust in the caller.** A route a provider alone may call refuses an owner token before any record is read, and an owner route reads the ownership of the registration it names, never of one the body names. Organization Control learned this when a consumer token that added a reason header reached its provider routes, before each route checked the caller's authority (organization-control ROADMAP item 17a).

### 5.5 Not the Kernel's Fine-Grained Permissions

Keycloak can grant an administrator permission over individual clients [R7]. That would put the ownership decision in the kernel, where the Identity Control Service does not record it, and send owners to the Admin Console, which `ADR-IAM-001 §5.7` keeps away from controller-owned configuration. Ownership is a registration fact and lives with the registration.

### 5.6 From Registration to Application

When the Software Catalog exists and says which team owns an Application, ownership moves from the registration to the Application: every registration of the Application has the Application's owners. The rules above do not change, only the scope of a grant, as an Entra custom role is assigned to one application or to all of them [R4].

### 5.7 Two-Person Control Over Providers Belongs at Activation

Requiring a second provider to approve each of a provider's registrations is not how the established platforms constrain their own administrators. Entra puts the second person at the moment administrative authority is activated: Privileged Identity Management can "require approval for activation of an eligible assignment", recommending "at least two approvers" [R8], after which the administrator acts without approval per action. NIST SP 800-53 AC-5 asks an organization to identify the duties it separates and to define access authorizations that support the separation [R1]. It does not ask for every privileged action to be approved by a second person.

So provider authority, not each registration, is where two-person control is added: a provider grant that is eligible rather than standing, activated for a bounded time with another provider's approval. That changes how Organization Control and the Identity Control Service hold provider authority (`ADR-ORG-001 §5.11`), and `ADR-ORG-002` decides it. A provider grant becomes eligible, and it is activated for a bounded time with another provider's approval. Until that is built, providers are few, every grant is recorded with its reason, and a provider's direct production registration is reported.

## 6. Consequences

### Positive

- An application team rotates, revokes and contains its own client without an operator.
- Every production trust change has two people on record.
- Ownership is a record with a history, ending with the person, rather than a role in a token or a permission in the kernel.

### Negative

- The Identity Control Service accepts two forms of privileged token, and its routes must keep them apart.
- Owners and proposals are new tables, routes and review work.
- Until the Software Catalog exists, ownership is granted registration by registration.
- A single provider can register a production client alone, and Entra notes that an application administrator can add credentials to an application and use them to impersonate it [R4]. A compromised provider account is therefore a production client takeover until two-person control at activation (§5.7) exists. Reporting every direct production registration makes it visible, not prevented.

### Operational

- Registrations without an active owner, ownerships held by an inactive Principal, and overdue reviews are reported.
- Proposals waiting for approval past a threshold are reported.
- Every production registration a provider creates directly is reported, with the provider and the client.

## 7. Compliance Impact

### Related Standards

- [ADR-IAM-001](ADR-IAM-001-adopt-keycloak-identity-kernel.md) §5.6, §5.7, §5.12, §5.13 — the registration authority, no kernel authority, keys, and the lifecycle.
- STD-IAM-002 §3.1.1 — the `resource-scoped` privileged form.
- [ADR-ORG-001](../organization-tenancy-platform/ADR-ORG-001-separate-organization-authority-and-keycloak-projection.md) §5.11 — a resource checks the grants it holds.
- SAD-002 — the Developer Console.

### Compliance Status

Compliant. `STD-IAM-002 §3.1.1` gains the `resource-scoped` form in the same change.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Owners per Application

**Benefits:** one owner list for every client of an Application, which is how teams think.

**Rejected for now because:** `application_ref` is entered administratively and the Software Catalog that would make it trustworthy is unchartered, so an Application-scoped grant would hang on a string anyone registering a client could type. §5.6 adopts it once the catalog exists.

### Alternative B — Developer Authority from Organization Membership

**Benefits:** reuses Organization's roles and its lifecycle.

**Rejected because:** a client registration belongs to the platform, not to a Tenant, so a Tenant role is the wrong boundary, and Organization holds no fact about who owns a client.

### Alternative C — The Kernel's Fine-Grained Admin Permissions

**Benefits:** supported by the pinned kernel [R7], with nothing to build.

**Rejected because:** of §5.5. The decision would live where the registration authority does not record it, and owners would work in the Admin Console.

### Alternative D — Providers Only

**Benefits:** the status quo; one authority.

**Rejected because:** every key rotation waits on an operator, and the Developer Console has no user it can serve.

### Alternative E — Every Production Registration by Approval, a Provider's Too

**Benefits:** no single person creates a production client; separation of duties at the level of each registration.

**Rejected because:** it is not how the platforms the decision follows constrain their administrators. Entra's Application Administrator creates registrations directly [R4], and its two-person control is approval at role activation [R8]. Per-registration approval would also route every workload and every adoption through a second person, so a deployment that registers a client waits on one, and a lone operator during an incident cannot register a replacement client. §5.7 places the control at activation instead, where it constrains everything a provider does, not only registration.

## 9. References

### Normative

- **[R1]** NIST SP 800-53 Rev. 5, _Security and Privacy Controls for Information Systems and Organizations_, AC-5 Separation of Duties. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. Divide functions among different individuals or roles to reduce the risk of abuse of authorized privilege: "Identify and document [organization-defined duties of individuals]" and "Define system access authorizations to support separation of duties".
- **[R2]** NIST SP 800-53 Rev. 5, AC-6 Least Privilege. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>.
- **[R3]** NIST SP 800-53 Rev. 5, AC-2 Account Management, (j) review at a defined frequency. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>.

### Informative

- **[R4]** Microsoft, _Delegate application management administrator permissions_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/delegate-app-roles>. Owners manage a specific application; the Application Developer role grants creation once self-service is restricted; a custom role can be scoped to a single app registration or to all. "Application Administrator: Users in this role can create and manage all aspects of enterprise applications, application registrations, and application proxy settings", and "can add credentials to an application and use those credentials to impersonate the application's identity".
- **[R5]** Microsoft, _Assign enterprise application owners_, accessed 2026-10-01. <https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/assign-app-owners>. Owners can manage only the applications they own.
- **[R6]** Okta, _Custom admin roles_ and _Create a resource set_, accessed 2026-10-01. <https://help.okta.com/en-us/content/topics/security/custom-admin-role/custom-admin-roles.htm>, <https://help.okta.com/en-us/content/topics/security/custom-admin-role/create-resource-set.htm>. An administrator role constrained to a set of applications.
- **[R7]** Keycloak, _Server Administration Guide_ 26.7.5, fine-grained admin permissions. <https://www.keycloak.org/docs/26.7.5/server_admin/index.html>. Permissions over individual resources, such as a client.
- **[R8]** Microsoft, _Configure Microsoft Entra role settings in PIM_, accessed 2026-10-02. <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings>. "Require approval for activation of an eligible assignment … We recommend that you select at least two approvers."
