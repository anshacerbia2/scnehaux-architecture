---
doc_meta:
  id: ADR-PRV-005
  title: Deprovisioning Keeps a Recoverable Window of 30 Days, Then Destroys by Key
  adr_type: foundational
  status: proposed
  created: 2026-11-04
  created_date: 2026-11-04
  created_by: Platform Engineering
  governed_by: [PAD-PLT-017]
---

# ADR-PRV-005: Deprovisioning Keeps a Recoverable Window of 30 Days, Then Destroys by Key

## 1. Title

When Organization Control releases a Tenant, every participating platform stops its part of the Tenant from being used at once, coordinated by the provisioning service (`ADR-PRV-006 §5.5`), keeps them recoverable for 30 days, and then destroys them. For a silo or regional Tenant, destruction is the deletion of each platform's key for the Tenant, which makes every copy encrypted under it unreadable, backups included.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                                                          | Approver                         |
| :--------- | :------- | :----------- | :----------------------------------------------------------------- | :------------------------------- |
| 2026-11-04 | proposed | foundational | Architecture, Core Platform, Platform Engineering, Security, Legal | Architecture Authority (pending) |

Amended on 4 November 2026 for the cross-platform contract of `ADR-PRV-006`, before ratification, as the server agent's review asked. It returns to `proposed` until the owner approves the amended wording.

## 3. Context

Organization Control decides when a Tenant's resources may go. Its offboarding freezes access, raises obligations for each domain (export, retention, deletion of Product data), refuses release while any obligation is open or a legal hold is set, and then records and publishes the deprovisioning command (`TDD-organization-control-004` §Offboarding). Release is a provider's act. A `realized` deprovisioning does not retire the Tenant; retirement stays a separate, deliberate act. A mistaken offboarding is reversed before release, because release is "the first irreversible step" (`ADR-ORG-006`).

What happens to the resources after release has not been decided. Today nothing happens: on the development server `scripts/dev-deprovisioning.ps1` reports `realized` and builds or deletes nothing.

Two facts bound the choice:

- **Deleting a cloud key cannot be undone, and the cloud forces a wait.** AWS KMS requires a waiting period of 7 to 30 days before it deletes a key, 30 by default, and after deletion data encrypted under the key "becomes unrecoverable" [R1].
- **Destroying the key is an accepted way to erase data that cannot be overwritten.** NIST SP 800-88 Rev. 2 describes cryptographic erase as making "recovery of the decrypted target data infeasible", and notes that for cloud storage it "may be the only viable purge sanitization technique option" [R2].

## 4. Decision Drivers

- Nothing irreversible happens in the same moment as release: a mistake found in the first days can still be undone.
- After the window, Tenant data is truly gone, including from backups and snapshots the service cannot list one by one.
- A legal hold stops destruction at any point.
- The domains' own obligations (export, retention) are complete before release; this service does not repeat them.
- The same rules for every profile, with the work differing by profile.

## 5. Decision

### 5.1 Three Stages After Release

| Stage          | When                      | What happens                                                                                                                              | Reversible |
| :------------- | :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- | :--------- |
| 1. Disable     | At once, on the command   | Routing to the Tenant's resources is removed; the Tenant's database roles are disabled; the key, if any, is disabled                      | Yes        |
| 2. Recoverable | 30 days from stage 1      | Resources are kept, unused. Silo and regional: a final encrypted snapshot is taken and the key deletion is scheduled with the 30-day wait | Yes        |
| 3. Destroyed   | At the end of the 30 days | Resources are deleted; the key is deleted by the cloud at the end of its wait                                                             | No         |

The service reports the deprovisioning `realized` to Organization Control at the end of stage 1, when every participating platform has reported `disabled` and the checks of §5.3 pass. Stage 3 is complete only when every participating platform has reported `destroyed` (`ADR-PRV-006 §5.5`). Organization Control can then retire the Tenant, which is already its separate act. Stages 2 and 3 are the service's own record, shown in the panel and alerted (`SAD-021 §9.3`).

### 5.2 What Each Profile Does

Each participating platform does this for its own part of the Tenant, with its own roles and its own key (`ADR-PRV-006`).

| Profile    | Stage 1                                                  | Stage 2                                                                                      | Stage 3                                                                                                                 |
| :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `pooled`   | Configuration marked disabled; quotas set to zero        | Configuration record kept                                                                    | Configuration and quota rows deleted. Product data in shared stores is the domains' obligation, settled before release  |
| `bridge`   | Tenant schema or database role disabled; routing removed | Schema kept; a final export, encrypted with the bridge cluster's key, is kept for the window | Schema or database dropped; the export deleted                                                                          |
| `silo`     | Routing removed; database stopped; key disabled          | Final snapshot under the Tenant key; key deletion scheduled, 30-day wait                     | Instance and snapshot deleted; the cloud deletes the key, making every backup and snapshot under it unreadable [R1][R2] |
| `regional` | As silo, in the Tenant's region                          | As silo                                                                                      | As silo; the service also checks that no resource for the Tenant exists outside the region                              |

### 5.3 What "Realized" Means for a Deprovisioning

The service reports `realized` only when every check passes:

- no route resolves to the Tenant's resources;
- the Tenant's database role cannot connect;
- for silo and regional, the key is disabled and its deletion is scheduled, and the final snapshot exists;
- the service's record of stage 2 has an end date.

Any failed check is reported `failed` with the cause `health_check_failed`. A provider can then send the deprovisioning again from Organization Control, as today (`TDD-organization-control-004` §Sending a Failed Deprovisioning Again).

### 5.4 Who Decides, and How a Mistake Is Undone

- **Release is the approval.** It is already a provider's act in Organization Control, possible only with no open obligation and no legal hold. The service adds no second approval before stage 1, because stage 1 is reversible.
- **Destruction needs no new approval, but it can be stopped.** At the end of the window the service destroys without asking. During the window, a provider holding `provider:provisioning` can **hold** destruction, with a reason, from the provisioning panel. A hold stops the clock until it is lifted. A legal hold recorded in Organization Control holds it too: the service checks the offboarding's legal-hold flag before stage 3.
- **Undoing within the window.** Restoring a released Tenant is not a path Organization Control has: `retired` is terminal, and release cannot be cancelled (`ADR-ORG-006`). A mistaken release found within the window is therefore handled as an incident: the hold stops destruction, the key deletion is cancelled, and the data is recovered into a new Tenant through a provisioning request. This is a runbook (`SAD-021 §9.3`), not a button.

### 5.5 Records Kept After Destruction

The service keeps its request records, approvals and the audit of each stage for 7 years, the audit-log period of `STD-GLB-007`. They hold identifiers, not Tenant data. Destroying a Tenant never deletes them.

## 6. Consequences

### Positive

- A mistaken release can be undone for 30 days.
- After 30 days, silo and regional data is unreadable everywhere, including backups the service never listed.
- Organization Control's release and retirement rules are unchanged.

### Negative

- Resources cost money for 30 days after release.
- Pooled and bridge Tenants have no per-Tenant key, so their destruction depends on deleting rows, schemas and exports, and on the shared store's backup retention expiring. Their data in shared backups lives until those backups expire.
- Undoing a release is a manual incident procedure, not a product feature.

### Operational

- Alerts on a destruction overdue past its window, and on a hold older than 30 days.
- The service's daily drift run also lists resources of retired Tenants that still exist.

## 7. Compliance Impact

### Related Standards and Artifacts

- `STD-GLB-007` — retention and deletion.
- `ADR-ORG-006` — release as the first irreversible step in Organization Control.
- `TDD-organization-control-004` — offboarding, obligations, legal hold, deprovisioning outcome.
- `ISMS-005` — A.8.10 information deletion, A.5.33 protection of records.

### Compliance Status

Proposed. The owner confirmed the 30-day window on 4 November 2026. The period a pooled or bridge Tenant's data stays in shared backups is stated in customer terms (`ISMS-005` T48).

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Delete Everything at Release

**Benefits:** no cost after release; simplest.

**Rejected because:** a mistake found the next day could not be undone, and Organization Control already treats release as irreversible only because it is the last check.

### Alternative B — Archive Indefinitely

**Benefits:** nothing is ever lost.

**Rejected because:** keeping a former customer's data with no purpose conflicts with retention limits in `STD-GLB-007` and with what customers expect.

### Alternative C — Delete Each Backup and Snapshot One by One

**Benefits:** no reliance on key deletion.

**Rejected as the method for silo and regional because:** the service cannot prove it found every copy; deleting the key makes every copy unreadable whether it was found or not [R2]. It is still how pooled and bridge data is removed, because they have no Tenant key.

### Alternative D — A Second Approval Before Destruction

**Benefits:** a person confirms the irreversible step.

**Rejected because:** release was already approved, and the window plus the hold give a person the chance to stop it. A required approval would leave destruction waiting on a person indefinitely.

## 9. References

### Normative

- **[R2]** NIST SP 800-88 Rev. 2, _Guidelines for Media Sanitization_, September 2025, accessed 2026-11-04. <https://csrc.nist.gov/pubs/sp/800/88/r2/final>. Cryptographic erase: "A purge sanitization technique in which key sanitization is applied to one or more keys providing confidentiality protections for the encrypted target data, making recovery of the decrypted target data infeasible"; §3.1.2: "For an ISM that takes the form of logical/virtual storage (e.g., cloud storage), cryptographic erase may be the only viable purge sanitization technique option." Supports §5.2 and Alternative C.

### Informative

- **[R1]** AWS, _Delete an AWS KMS key_, AWS KMS Developer Guide, accessed 2026-11-04. <https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html>. "Because it is destructive and potentially dangerous to delete a KMS key, AWS KMS requires you to set a waiting period of 7 – 30 days. The default waiting period is 30 days"; "After a KMS key is deleted, you can no longer decrypt the data that was encrypted under that KMS key, which means that data becomes unrecoverable." The page lists exceptions for multi-Region replica keys and imported key material, which this design does not use. Supports §5.1 and §5.2.
