---
doc_meta:
  id: ADR-IAM-012
  title: Identity Experience Uses Local Components Until the UI Platform Ships Them
  adr_type: exception
  status: accepted
  created: 2026-10-20
  created_date: 2026-10-20
  created_by: Identity Experience Team
  governed_by: [PAD-PLT-001]
  exception_info:
    approved_by: Domain Lead (Tier 2, GDC-004 §4.2), on the owner's approval of 2026-10-20
    expiry_date: '2027-04-20'
    risk_classification: low
    exception_reason: The UI Platform has not released `@scnx/system` or `@scnx/core-ui`, so identity-experience builds on a local package that mirrors their APIs and token names.
---

# ADR-IAM-012: Identity Experience Uses Local Components Until the UI Platform Ships Them

## 1. Title

Identity Experience Uses Local Components Until the UI Platform Ships Them.

## 2. Status

| Date       | Status   | ADR Type  | Reviewers                 | Approver                             |
| ---------- | -------- | --------- | ------------------------- | ------------------------------------ |
| 2026-10-20 | accepted | exception | Architecture Review Board | Domain Lead (Tier 2, `GDC-004 §4.2`) |

The owner approved the recommendation on 2026-10-20. This waiver expires on **2027-04-20**, six months
after approval, within the 365-day cap of `GDC-004 §4.2` and `GDC-010 §2.3.4`.

## 3. Context

`SAD-002` makes the UI Platform the source of identity-experience's tokens and primitives. §4.5:
"Identity Experience uses approved design tokens, primitives, accessibility helpers, and theming
contracts". §10 rejects an "external component-library bypass of UI Platform without an approved
exception". `STD-GLB-FE-005 §3.5` makes an application a consumer of the platform's published
stylesheets.

The UI Platform has not released `@scnx/system` or `@scnx/core-ui`. The owner chose on 2026-10-01 to
keep the applications' own components until the UI Platform resumes, and to build first and record
the exception afterwards. identity-experience therefore builds on `packages/ui`, a local stand-in
(its `ROADMAP.md`, "Open: the UI Platform exception"):

- it mirrors the platform's component APIs and its `--ds-*` token names;
- the applications import it through one entry point;
- its README maps each component to its platform counterpart;
- its contrast pairs and axe checks pass at WCAG 2.2 AA in both themes.

Until now this departure was open in the ROADMAP, with no record that bounds it. `GDC-000 §2.11`
permits an exception only when it is "formally documented (typically as ADRs), bounded by an
expiration date, and approved by the Architecture Authority", and says "Permanent waivers are
prohibited".

## 4. Decision Drivers

- **The governance already prescribes the form.** `GDC-004 §4.2` asks for "a dedicated local project
  Exception ADR detailing the deviation, the specific standard rule being bypassed, and the
  mitigation strategies implemented". A frontend stack deviation is Tier 2, approved by the Domain
  Lead, and expires within 365 days. `STD-UIP-TKN-002 §4` asks that an exception record "the
  consumer, reason, owner, affected token, expected duration, and migration path".
- **Accepting a risk is a recorded choice with a plan.** NIST names "accepting risk with appropriate
  justification or rationale" as a risk response, and "if the risk response is to mitigate the risk,
  and the mitigation cannot be completed immediately, a plan of action and milestones entry is
  generated" [R1]. Non-federal organizations "can help reduce risk by documenting and tracking
  planned remediations" [R2].
- **Exceptions are tracked and reviewed.** "Organizations should closely track and monitor all
  exceptions to maintenance plans", and "All exceptions to maintenance plans should be reviewed
  regularly to determine if the maintenance plan can be implemented now" [R3]. The source is about
  patching; its rule on exceptions is general.
- **The departure must stay cheap to end.** The local package is built so that its exit is a
  re-export, not a redesign.

## 5. Decision

### 5.1 The Waiver

identity-experience MAY use its local component package `packages/ui` in place of `@scnx/system` and
`@scnx/core-ui` until this waiver expires on 2027-04-20.

| Field (`STD-UIP-TKN-002 §4`) | Value                                                                                          |
| :--------------------------- | :--------------------------------------------------------------------------------------------- |
| Consumer                     | identity-experience: the Account application, the Admin Portal and the Developer Console       |
| Reason                       | The UI Platform has not released its primitives (the owner's decision of 2026-10-01 defers it) |
| Owner                        | Identity Experience Team                                                                       |
| Affected tokens              | Every `--ds-*` token, defined locally with the platform's names                                |
| Expected duration            | Until `@scnx/system` and `@scnx/core-ui` are released, and at most until 2027-04-20            |
| Migration path               | `packages/ui`'s entry point re-exports the platform packages, and the local copies are deleted |

### 5.2 The Rules It Bypasses

- `SAD-002 §4.5`, "uses approved design tokens, primitives, accessibility helpers, and theming
  contracts", and `SAD-002 §10`, the rejected "external component-library bypass of UI Platform
  without an approved exception". This ADR is that exception.
- `STD-GLB-FE-005 §3.5`, CSS delivery through the UI Platform's published aggregate stylesheet.

### 5.3 The Mitigations, Which Hold While It Lasts

- **Mirrored APIs and token names.** Each component keeps its platform counterpart's API, and every
  token keeps its `--ds-*` name.
- **One entry point.** Applications import components only through `packages/ui`'s entry point, so
  the exit changes one file.
- **Accessibility does not wait.** The contrast test and the axe checks run in CI at WCAG 2.2 AA in
  both themes (`STD-GLB-FE-009`). No security control is bypassed.

### 5.4 Exit and Review

- **Exit criterion.** `@scnx/system` and `@scnx/core-ui` are released, and the entry point re-exports
  them. The waiver is then `deprecated` (`GDC-010 §2.4.3`, scenario A).
- **Review before expiry.** If the UI Platform has not released them by 2027-04-20, the team submits a
  new Exception ADR that supersedes this one (`GDC-010 §2.4.3`, scenario C), or the CI waiver check
  blocks the repository.

## 6. Consequences

### Positive

- The departure is recorded, bounded and owned, so `SAD-002 §10` is met.
- The exit is a re-export of one entry point.

### Negative

- Two copies of the visual language exist, here and in organization-experience (`ADR-ORG-008`), and
  can drift until the platform ships.
- The local components do not receive the UI Platform's own release evidence.

### Operational

- The CI waiver check warns 30 days before 2027-04-20 and fails after it (`GDC-010 §2.2`).
- identity-experience's `ROADMAP.md` records this ADR and its expiry; `packages/ui/README` cites it.

## 7. Compliance Impact

### Related Standards

- `SAD-002 §4.5` and `§10`.
- `STD-GLB-FE-005 §3.5`.
- `STD-UIP-TKN-002 §4`.
- `GDC-000 §2.11`, `GDC-004 §4.2`, `GDC-010 §2.3.4` and `§2.4.3`.

### Compliance Status

Non-compliant with the rules in §5.2, by this approved, time-boxed exception.

### Required Waivers

This ADR is the waiver.

## 8. Alternatives Considered

### Alternative A: Copy SAD-012's Open-Ended "Until UI Platform Ships" Into SAD-002

- **Pros**: one sentence, no expiry to track.
- **Cons**: it has no expiry, so it is the permanent waiver `GDC-000 §2.11` prohibits, and it leaves
  the departure from `STD-GLB-FE-005 §3.5` unrecorded.
- **Why Rejected**: it fails the governance this repository enforces.

### Alternative B: Leave It Open in the ROADMAP

- **Pros**: no document to write.
- **Cons**: it fails `SAD-002 §10` as written, and nothing makes anyone review it.
- **Why Rejected**: an untracked exception is the case NIST warns about [R3].

### Alternative C: Stop Building Until the UI Platform Ships

- **Pros**: no departure at all.
- **Cons**: it stops the identity experience for a dependency the owner has deferred.
- **Why Rejected**: the owner decided to build first.

## 9. References

### Normative

- **[R1]** NIST SP 800-53 Rev. 5, RA-7 _Risk Response_, guidance, accessed 2026-10-20. NIST OSCAL
  catalog,
  <https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json>.
  "Organizations have many options for responding to risk including mitigating risk by implementing
  new controls or strengthening existing controls, accepting risk with appropriate justification or
  rationale, sharing or transferring risk, or avoiding risk"; "if the risk response is to mitigate
  the risk, and the mitigation cannot be completed immediately, a plan of action and milestones
  entry is generated."
- **[R2]** NIST SP 800-53 Rev. 5, PM-4 _Plan of Action and Milestones Process_, guidance, same
  catalog, accessed 2026-10-20. "While plans of action and milestones are required for federal
  organizations, other types of organizations can help reduce risk by documenting and tracking
  planned remediations."
- **[R3]** NIST SP 800-40 Rev. 4, _Guide to Enterprise Patch Management Planning_, §3.5.5 "Exceptions
  to Maintenance Plans", accessed 2026-10-20.
  <https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-40r4.pdf>. "Organizations
  should closely track and monitor all exceptions to maintenance plans"; "All exceptions to
  maintenance plans should be reviewed regularly to determine if the maintenance plan can be
  implemented now."

### Informative

- Internal: `GDC-000 §2.11`, `GDC-004 §4.2`, `GDC-010 §2.4.3`, `STD-UIP-TKN-002 §4`, quoted above.
  TOGAF's time-limited "dispensation" is the enterprise-architecture term for the same record; its
  text could not be retrieved on 2026-10-20, so it is not quoted.
