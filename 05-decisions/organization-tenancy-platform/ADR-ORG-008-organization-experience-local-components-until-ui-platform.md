---
doc_meta:
  id: ADR-ORG-008
  title: Organization Experience Uses Local Components Until the UI Platform Ships Them
  adr_type: exception
  status: accepted
  created: 2026-10-20
  created_date: 2026-10-20
  created_by: Organization Platform Team
  governed_by: [PAD-PLT-002]
  exception_info:
    approved_by: Domain Lead (Tier 2, GDC-004 §4.2), on the owner's approval of 2026-10-20
    expiry_date: '2027-04-20'
    risk_classification: low
    exception_reason: The UI Platform has not released `@scnx/system` or `@scnx/core-ui`, so organization-experience builds on local components copied from identity-experience, with the same APIs and token names.
---

# ADR-ORG-008: Organization Experience Uses Local Components Until the UI Platform Ships Them

## 1. Title

Organization Experience Uses Local Components Until the UI Platform Ships Them.

## 2. Status

| Date       | Status   | ADR Type  | Reviewers                 | Approver                             |
| ---------- | -------- | --------- | ------------------------- | ------------------------------------ |
| 2026-10-20 | accepted | exception | Architecture Review Board | Domain Lead (Tier 2, `GDC-004 §4.2`) |

The owner approved the recommendation on 2026-10-20. This waiver expires on **2027-04-20**, six months
after approval, within the 365-day cap of `GDC-004 §4.2` and `GDC-010 §2.3.4`.

## 3. Context

`SAD-012 §1` (Constraint) makes the UI Platform packages the design-system dependency, and `§7.3`
makes the UI Platform the build-time source of tokens, primitives and components. Until 1.4.0, §7.3
also allowed the application its own component package "until UI Platform ships its primitives".
That allowance has no end date, so it is the permanent waiver `GDC-000 §2.11` prohibits: an exception
must be "formally documented (typically as ADRs), bounded by an expiration date, and approved by the
Architecture Authority". `STD-GLB-FE-005 §3.5` makes an application a consumer of the platform's
published stylesheets.

The UI Platform has not released `@scnx/system` or `@scnx/core-ui`, and the owner decided on
2026-10-01 to keep the applications' own components until it resumes. organization-experience
copied identity-experience's components, at identity-experience commit
`c723e417c0eee97db6b1d5b6dab608fe6a406ac2`, under `apps/admin/src/ui/`, behind one entry point (its
`ROADMAP.md`, "Visual language"):

- every `--ds-*` token keeps the same name and value, in both schemes;
- the components keep identity-experience's APIs, which mirror the platform's (`ADR-IAM-012`);
- the contrast test, with this application's own pairs, and axe pass at WCAG 2.2 AA in both themes.

## 4. Decision Drivers

- **The governance already prescribes the form.** `GDC-004 §4.2` asks for "a dedicated local project
  Exception ADR detailing the deviation, the specific standard rule being bypassed, and the
  mitigation strategies implemented", Tier 2 for a frontend stack, approved by the Domain Lead,
  expiring within 365 days. `STD-UIP-TKN-002 §4` asks that it record "the consumer, reason, owner,
  affected token, expected duration, and migration path".
- **One exception per consuming system.** Each system has its own SAD, and `GDC-004 §4.2` asks for a
  local project Exception ADR. identity-experience's is `ADR-IAM-012`.
- **Accepting a risk is a recorded choice with a plan.** NIST names "accepting risk with appropriate
  justification or rationale" as a risk response, with "a plan of action and milestones" when the
  mitigation cannot be completed immediately [R1], and asks that exceptions be tracked and reviewed
  regularly [R2][R3].

## 5. Decision

### 5.1 The Waiver

organization-experience MAY use its local components under `apps/admin/src/ui/` in place of
`@scnx/system` and `@scnx/core-ui` until this waiver expires on 2027-04-20.

| Field (`STD-UIP-TKN-002 §4`) | Value                                                                                            |
| :--------------------------- | :----------------------------------------------------------------------------------------------- |
| Consumer                     | organization-experience: the administration console                                              |
| Reason                       | The UI Platform has not released its primitives (the owner's decision of 2026-10-01 defers it)   |
| Owner                        | Organization Platform Team                                                                       |
| Affected tokens              | Every `--ds-*` token, defined locally with the platform's names and identity-experience's values |
| Expected duration            | Until `@scnx/system` and `@scnx/core-ui` are released, and at most until 2027-04-20              |
| Migration path               | `apps/admin/src/ui/index.ts` re-exports the platform packages, and the copies are deleted        |

### 5.2 The Rules It Bypasses

- `SAD-012 §1` (Constraint) and `§7.3`: the UI Platform packages as the design-system dependency.
  §7.3 now cites this ADR in place of its open-ended allowance (`SAD-012` 1.4.0).
- `STD-GLB-FE-005 §3.5`, CSS delivery through the UI Platform's published aggregate stylesheet.

### 5.3 The Mitigations, Which Hold While It Lasts

- **The same APIs and token names as identity-experience,** which mirror the platform's.
- **One entry point,** `apps/admin/src/ui/index.ts`, so the exit changes one file.
- **Accessibility does not wait.** The contrast test and axe run in CI at WCAG 2.2 AA in both themes
  (`STD-GLB-FE-009`). No security control is bypassed.

### 5.4 Exit and Review

- **Exit criterion.** `@scnx/system` and `@scnx/core-ui` are released, and the entry point re-exports
  them. The waiver is then `deprecated` (`GDC-010 §2.4.3`, scenario A).
- **Review before expiry.** If they are not released by 2027-04-20, a new Exception ADR supersedes
  this one (`GDC-010 §2.4.3`, scenario C), or the CI waiver check blocks the repository.

## 6. Consequences

### Positive

- `SAD-012 §7.3` no longer carries a permanent waiver.
- The exit is a re-export of one entry point.

### Negative

- The copy can drift from identity-experience's until the platform ships.
- The local components do not receive the UI Platform's own release evidence.

### Operational

- The CI waiver check warns 30 days before 2027-04-20 and fails after it (`GDC-010 §2.2`).
- organization-experience's `ROADMAP.md` records this ADR; the `apps/admin/src/ui/index.ts` header
  cites it.

## 7. Compliance Impact

### Related Standards

- `SAD-012 §1` and `§7.3`.
- `STD-GLB-FE-005 §3.5`.
- `STD-UIP-TKN-002 §4`.
- `GDC-000 §2.11`, `GDC-004 §4.2`, `GDC-010 §2.3.4` and `§2.4.3`.
- `ADR-IAM-012`, the same exception for identity-experience.

### Compliance Status

Non-compliant with the rules in §5.2, by this approved, time-boxed exception.

### Required Waivers

This ADR is the waiver.

## 8. Alternatives Considered

### Alternative A: Keep SAD-012 §7.3's "Until UI Platform Ships"

- **Pros**: already written.
- **Cons**: no expiry, so it is a permanent waiver (`GDC-000 §2.11`), and it is inconsistent with
  `SAD-002 §10`.
- **Why Rejected**: it fails the governance this repository enforces.

### Alternative B: One Shared Exception for Both Experiences

- **Pros**: one document.
- **Cons**: `GDC-004 §4.2` asks for a local project Exception ADR, and each system has its own SAD,
  owner and exit.
- **Why Rejected**: two systems, two records.

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
