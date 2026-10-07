---
doc_meta:
  id: ADR-ORG-006
  title: A Mistaken Offboarding Is Reversed Before Release
  adr_type: foundational
  status: accepted
  created: 2026-10-07
  created_date: 2026-10-07
  created_by: Core Platform Team
---

# ADR-ORG-006: A Mistaken Offboarding Is Reversed Before Release

## 1. Title

A Mistaken Offboarding Is Reversed Before Release.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-10-07 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

Offboarding runs in four stages: freeze, obligations, release, retired
(`TDD-organization-control-004`). Its design calls the first reversible:

- "freezing is reversible and immediate, release is neither";
- "An operator who begins offboarding by mistake has stopped access, which is reversible, and has
  destroyed nothing".

Nothing reverses it. The stage machine runs forward only, and no transition returns a Tenant from
`offboarding`. A Tenant offboarded by mistake therefore stays without access, every Membership
suspended, until someone retires it. Organization Experience records the gap rather than calling
the freeze reversible (`TDD-organization-experience-003` 1.2.0).

## 4. Decision Drivers

- **Platforms stop access first and destroy later, and reverse only in between:**
  - Entra holds a deleted user "in a suspended state for 30 days. During that 30-day window, the
    user account can be restored, along with all its properties". After that, deletion "can't be
    stopped" [R1].
  - Google Workspace restores a deleted user "up to 20 days after deleting it. After 20 days, the
    data is gone" [R2].
  - AWS: during the 90-day post-closure period an account can be reopened, and after it "you can
    no longer reopen it" [R3].
  - A Microsoft 365 subscription passes through Expired and Disabled before Deleted. Deleted "can't
    be reactivated" [R4].
- **A restore puts back what the action removed, and only that:**
  - Google: "If the user was previously suspended … they'll show as a suspended user" [R2].
  - AWS restores access, but "Some resources and subscriptions are not restored to a running state
    automatically" [R3].
- **Release is the first irreversible step here.** It begins deprovisioning, and from there the
  data an obligation exists for may be gone (`TDD-organization-control-004`).

## 5. Decision

### 5.1 An Offboarding Is Cancelled Before Release, Not After

`POST /v1/offboardings/{id}/cancel` is a provider command, with its reason and the Tenant's
`expected_version`.

| Stage                | Cancellation                     |
| :------------------- | :------------------------------- |
| `freeze`             | Accepted                         |
| `obligations`        | Accepted                         |
| `release`, `retired` | Refused: release is irreversible |

The offboarding ends in a terminal `cancelled` stage, recorded with who cancelled it, why, and when.
It is never deleted.

### 5.2 Cancellation Restores What the Offboarding Removed, and Nothing Else

- **The Tenant** returns to the status it held when the offboarding began, `active` or
  `suspended`, recorded at the start. A suspension in force before offboarding stays in force
  ([R2]).
- **The Memberships the freeze suspended are restored.** Those suspended before the offboarding
  stay suspended. This means the freeze must record which Memberships it suspended.
- **Nothing else is undone.**
  - Obligations already completed keep their record. Open obligations are closed as cancelled with
    the offboarding.
  - An export that already ran stays run. A restore does not replay side effects [R3].
- **Revocation runs as the transitions themselves.**
  - Each restored Membership and the Tenant publish their ordinary restore events, with the
    Tenant's security version incremented as a restore always does.
  - Access returns at every consumer by the same path it was stopped, and is shown by its evidence
    (`ADR-ORG-004 §5.2`).

## 6. Consequences

### Positive

- A mistaken offboarding is undone by one recorded command instead of a hand repair, while nothing
  has been destroyed.
- What the design always said of the freeze, that it is reversible, becomes true.

### Negative

- **The freeze records which Memberships it suspended.** That is a column or a table of its own.
- **Cancellation restores many Memberships at once**, publishing an event for each. It is bounded
  by the Tenant's size, as the freeze was.

### Operational

- A cancelled offboarding is reported like any other privileged command, with its reason.
- A cancellation soon after a beginning is worth a review, because it means one of them was a
  mistake.

## 7. Compliance Impact

### Related Standards

- `TDD-organization-control-004`: the `cancelled` stage, the freeze record, the cancel command.
- `TDD-organization-experience-003`: the reversal offered in the freeze and obligations stages.
- `ADR-ORG-004`: the restored access shown by its evidence.

### Compliance Status

Compliant once the command is served and Organization Experience offers it before release.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — No Reversal; Retire and Re-Create

**Rejected because:** re-creating gives the Tenant a new identity, and every Membership, invitation
and external reference to it is lost. That is the opposite of "destroyed nothing".

### Alternative B — Reversal at Any Stage

**Rejected because:** after release, deprovisioning has begun and the data an obligation existed
for may be gone. Each platform above stops reversal at its irreversible step [R1][R2][R3][R4].

### Alternative C — Restore Every Suspended Membership

**Rejected because:** it would restore Memberships suspended for their own reasons before the
offboarding began. A restore returns what the action removed and nothing more [R2].

## 9. References

### Informative

- **[R1]** Microsoft, _Restore or remove a recently deleted user_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/entra/fundamentals/users-restore>. "After you delete a user, the
  account remains in a suspended state for 30 days. During that 30-day window, the user account can
  be restored, along with all its properties." / "After that 30-day window passes, the permanent
  deletion process automatically starts and can't be stopped."
- **[R2]** Google Workspace Admin Help, _Restore a recently deleted user_, accessed 2026-10-07.
  <https://knowledge.workspace.google.com/admin/users/restore-a-recently-deleted-user?hl=en>. "You can
  restore a user account (including administrator accounts) up to 20 days after deleting it. After
  20 days, the data is gone and you can't restore it." / "If the user was previously suspended or
  had their data transferred, they'll show as a suspended user."
- **[R3]** Amazon Web Services, _Close an AWS account_ §Post-closure period, and _Reopen a closed AWS
  account_, accessed 2026-10-07.
  <https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-closing.html#post-closure-period>,
  <https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-reopening.html>. "The
  post-closure period is 90 days … After the post-closure period, AWS permanently closes your AWS
  account, and you can no longer reopen it." / "Some resources and subscriptions are not restored to
  a running state automatically."
- **[R4]** Microsoft, _What happens to my data and access when my Microsoft 365 for business
  subscription ends?_, accessed 2026-10-07.
  <https://learn.microsoft.com/en-us/microsoft-365/commerce/subscriptions/what-if-my-subscription-expires?view=o365-worldwide>.
  "When your subscription ends, it goes through multiple lifecycle statuses before it gets deleted.
  This gives you, as the admin, time to reactivate the subscription"; for Deleted: "Subscription
  can't be reactivated".
