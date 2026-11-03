---
doc_meta:
  id: ISMS-008
  title: Nonconformity and Corrective Action Log
  owner: ISMS Owner
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-012, ISMS-001]
  review_cycle_days: 90
  created_date: 2026-11-03
  last_reviewed: 2026-11-03
  isms_record: nonconformity-log
  iso_clauses: ['10.1', '10.2']
  annex_a_controls: ['A.5.27']
---

# Nonconformity and Corrective Action Log

## Purpose & Scope

This log records each nonconformity found inside the scope of [ISMS-001](ISMS-001-scope-and-context.md): what happened, the immediate reaction, the root cause, the corrective action, and the review of whether that action worked. A nonconformity is a case where the ISMS, a standard, a decision or a record in these repositories was not followed, or an objective in [ISMS-006](ISMS-006-objectives.md) was missed by its date.

Security incidents are handled under the incident management record (T27, planned). When an incident also shows a nonconformity, it is entered here as well, and each entry links the other.

## ISO/IEC 27001 Mapping

Edition: ISO/IEC 27001:2022. This record answers:

| Clause or control | Title                                        | Where in this record                                                         |
| :---------------- | :------------------------------------------- | :--------------------------------------------------------------------------- |
| 10.1              | Continual improvement                        | [Lessons kept](#lessons-kept)                                                |
| 10.2              | Nonconformity and corrective action          | [The log](#the-log) and each entry                                           |
| A.5.27            | Learning from information security incidents | Each entry's root cause and corrective action; [Lessons kept](#lessons-kept) |

No text of the standard is reproduced.

## Record

### How an entry is made

1. Whoever finds a nonconformity tells the ISMS Owner, who opens an entry in a pull request within 5 working days.
2. The entry records the reaction (stop the harm, correct the result), then the root cause: why it happened, not only what happened.
3. The corrective action removes the cause. It is a treatment action in [ISMS-005](ISMS-005-risk-treatment-and-soa.md), or a change made in the same pull request.
4. An entry closes only after its effectiveness review shows the cause did not recur. Until then its status is `open` or `corrected` (the result is fixed and the cause is not yet removed).
5. If the root cause is a new or larger risk, the risk register ([ISMS-004](ISMS-004-risk-register.md)) is updated in the same pull request.

### The log

| ID   | Found           | Summary                                                                                  | Status      | Corrective action                        | Effectiveness review by |
| :--- | :-------------- | :--------------------------------------------------------------------------------------- | :---------- | :--------------------------------------- | :---------------------- |
| NC-1 | 31 October 2026 | identity-kernel's daily image scan failed unread for 6 days; the remediation time passed | `corrected` | T4                                       | 31 December 2026        |
| NC-2 | 1 November 2026 | ISMS records were merged before the guideline that governs them was ratified             | `corrected` | Explicit ratification question; T42, T19 | 30 January 2027         |
| NC-3 | 1 November 2026 | A person's name appeared in four public repositories                                     | `corrected` | T18                                      | 31 December 2026        |

#### NC-1: a failed daily scan went unread

- **What happened.** identity-kernel's scheduled image scan failed every day from 26 to 31 October 2026 on fixable findings in the proxy image (curl) and the Caddy build (go-jose). Nobody read the failures. They were found on 31 October 2026, during the evidence review for the ISMS, and fixed the same day ([identity-kernel #78](https://github.com/anshacerbia2/identity-kernel/pull/78)), 5 days after the first failure. The scans of identity-control and organization-control also failed from 28 October 2026 and were fixed on 30 October 2026, within the time, because someone happened to look.
- **Requirement not met.** The remediation time for a finding in an exposed image ([STD-GLB-009 §Container Images](../02-standards/_global/STD-GLB-009-platform-engineering.md#container-images-140), rule 8).
- **Immediate reaction.** The proxy's curl was upgraded, go-jose was replaced in the Caddy build, and the two Keycloak findings that wait for a release (guava, OpenJDK) were given recorded exceptions that expire on 30 November 2026 (R22, T3).
- **Root cause.** A failed scheduled workflow alerts nobody. GitHub shows the failure only to someone who opens the Actions tab, and no role was given the task of looking (R21).
- **Corrective action.** T4: every scheduled workflow alerts the Information Security Officer when it fails, in every repository, by 30 November 2026. It is a production gate in each repository's ROADMAP.
- **Effectiveness review.** By 31 December 2026: check that each failed scheduled run in December reached the Information Security Officer within 1 working day (objective O2), and that no exposed-image finding passed its remediation time (O1).

#### NC-2: records merged before their guideline was ratified

- **What happened.** On 1 November 2026, ISMS-001 to ISMS-003 ([#141](https://github.com/anshacerbia2/scnehaux-architecture/pull/141)) and ISMS-004 and ISMS-005 ([#142](https://github.com/anshacerbia2/scnehaux-architecture/pull/142)) were merged while GDC-012 and its changes to GDC-000, GDC-001 and GDC-005 ([#140](https://github.com/anshacerbia2/scnehaux-architecture/pull/140)) still carried a "Pending ratification" note. The records were therefore built on rules that were not yet in force.
- **Requirement not met.** A changed approved artifact takes effect only when the human authority approves the exact commit; a merge or a passing CI run is not approval ([GDC-000 §2.6.7](../00-governance/GDC-000-governance-policy.md), rule 7).
- **Immediate reaction.** The same day, the owner, as Architecture Authority, Top Management and ISMS Owner, ratified the four guidelines at commit `900baea` and approved ISMS-001 to ISMS-005 at commit `328cc9d`. The ratification is recorded in [#143](https://github.com/anshacerbia2/scnehaux-architecture/pull/143), which removed the pending notes and set the records to `approved`. The ratified rules were the ones the records had followed, so no record needed changing.
- **Root cause.** Ratification was asked for in the text of a pull request description and a chat reply. The reply was "merged", which is not a ratification, and nothing stops a merge without one. With one maintainer, no second approval would catch it either (R23).
- **Corrective action.** (1) Ratification is now asked as one explicit question that names the exact commit, before or at the merge; [#144](https://github.com/anshacerbia2/scnehaux-architecture/pull/144) was ratified that way on 3 November 2026, before its merge. (2) T42: verify the ruleset of every repository and check it in CI, by 15 December 2026. (3) T19: a second person's approval on `main` before production.
- **Effectiveness review.** By 30 January 2027, at the review of the risk register: no change to an approved document merged without a recorded ratification since 1 November 2026 (objective O7).

#### NC-3: a person's name in public repositories

- **What happened.** On 1 November 2026, while adding the ISMS production gates, a person's name was found in ui-platform's ROADMAP. A search of all repositories then found it in four: ui-platform (the ROADMAP and two review records), this repository (the approver column and prose of 20 decision records, and the tech radar), identity-control (test data) and organization-control (an example path). An earlier case, the development server named after a person, had been corrected on 31 October 2026 ([#139](https://github.com/anshacerbia2/scnehaux-architecture/pull/139)).
- **Requirement not met.** The repositories are public, so records and code name roles, never people ([ISMS-001 §Internal and external issues](ISMS-001-scope-and-context.md#internal-and-external-issues); [ISMS-002](ISMS-002-policy-and-roles.md)).
- **Immediate reaction.** Each occurrence was replaced by the role: [ui-platform #147](https://github.com/anshacerbia2/ui-platform/pull/147) on 1 November 2026; [#144](https://github.com/anshacerbia2/scnehaux-architecture/pull/144), [identity-control #126](https://github.com/anshacerbia2/identity-control/pull/126) and [organization-control #86](https://github.com/anshacerbia2/organization-control/pull/86) on 3 November 2026. The account name in repository links stays, as it is the repositories' address. Git history still holds the earlier text.
- **Root cause.** The rule was written down only when the ISMS started. Before then, decision records were written with the approver's name, as a common template does. The linter's check for personal identifiers runs on ISMS records only, so nothing else was checked (R17).
- **Corrective action.** T18, by 31 December 2026: review the public content of every repository, and extend the personal-identifier check beyond ISMS records.
- **Effectiveness review.** By 31 December 2026: a search of every in-scope repository finds no person's name outside the account name.

### Lessons kept

- A check that nobody reads does not operate. Every scheduled check needs someone it alerts (NC-1).
- An approval asked for in prose is easily answered with something else. Ask one question that names the commit (NC-2).
- A rule that only some files are checked against is followed only in those files (NC-3).

## Review & Change Control

- **Reviewer and approver:** the Information Security Officer reviews; the ISMS Owner approves ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)).
- **Cadence:** every 90 days at most. The next review is due by 1 February 2027, and each open entry is checked on its effectiveness review date.
- **Early review when:** a nonconformity is found; an effectiveness review is due; after an incident, an audit finding or a management review decision.

## Open Gaps

| Gap                                                             | Treatment |
| :-------------------------------------------------------------- | :-------- |
| No incident management record to link incidents to entries here | T27       |
| No internal audit yet, the usual source of nonconformities      | T36       |

## References

- **[R1]** ISO/IEC 27001:2022. Cited by clause and control number and title only.
- **[R2]** [GDC-000 Governance Policy](../00-governance/GDC-000-governance-policy.md), §2.6.7.
- **[R3]** [STD-GLB-009 Platform Engineering](../02-standards/_global/STD-GLB-009-platform-engineering.md), §Container Images.
