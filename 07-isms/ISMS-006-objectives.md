---
doc_meta:
  id: ISMS-006
  title: Information Security Objectives
  owner: ISMS Owner
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-012, ISMS-002]
  review_cycle_days: 180
  created_date: 2026-11-03
  last_reviewed: 2026-11-03
  isms_record: objectives
  iso_clauses: ['6.2', '9.1']
  annex_a_controls: []
---

# Information Security Objectives

## Purpose & Scope

This record sets the measurable information security objectives of the ISMS defined in [ISMS-001](ISMS-001-scope-and-context.md), consistent with the policy in [ISMS-002](ISMS-002-policy-and-roles.md). For each objective it states the measure, the target, the date, the role that monitors it, the actions that achieve it, and the latest result.

The objectives cover what runs today: the development environment, the repositories and their CI. Objectives for production availability and for customer-facing service levels are added when staging is built.

## ISO/IEC 27001 Mapping

Edition: ISO/IEC 27001:2022. This record answers:

| Clause | Title                                                        | Where in this record                                                                     |
| :----- | :----------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| 6.2    | Information security objectives and planning to achieve them | [The objectives](#the-objectives)                                                        |
| 9.1    | Monitoring, measurement, analysis and evaluation             | [The objectives](#the-objectives), [How results are measured](#how-results-are-measured) |

No text of the standard is reproduced.

## Record

### The objectives

Results are for the period 20 October to 2 November 2026 unless stated. "Met" means the latest result reaches the target.

| ID  | Objective                                                     | Measure                                                                                                                                                                                         | Target                                                                | By                   | Monitored by                 | Actions            | Latest result                                                                                                                                                                                                                                                                                                                                                                                                               |
| :-- | :------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------- | :------------------- | :--------------------------- | :----------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| O1  | Fix exposed vulnerabilities in time                           | Of the daily image scans that fail on a fixable High or Critical finding, the share fixed or given a recorded exception within 3 days                                                           | 100%                                                                  | Every month          | Information Security Officer | T1, T3, T4         | **Not met: 2 of 3.** identity-control and organization-control failed on 28 October and were fixed on 30 October. identity-kernel failed on 26 October and was fixed on 31 October (NC-1 in [ISMS-008](ISMS-008-nonconformity-log.md))                                                                                                                                                                                      |
| O2  | See every failed scheduled check quickly                      | Share of failed scheduled workflow runs that alert the Information Security Officer within 1 working day                                                                                        | 100%                                                                  | From 1 December 2026 | Information Security Officer | T4                 | **Not measured.** No alert exists yet; a failed run shows only to someone who opens it                                                                                                                                                                                                                                                                                                                                      |
| O3  | Treat risks on time                                           | Treatment actions in [ISMS-005](ISMS-005-risk-treatment-and-soa.md) completed by their target date, as a share of those due                                                                     | At least 90% each quarter; 100% of production gates before production | Each quarter         | ISMS Owner                   | ISMS-005 T1 to T45 | **No action due yet** (the first, T2, is due 15 November 2026). T25, T30 and T31 completed early on 3 November 2026                                                                                                                                                                                                                                                                                                         |
| O4  | Keep data recoverable                                         | Share of `deploy-dev` runs on `main` that pass end to end, in identity-kernel, identity-control and organization-control. The restore drill is the last step, so a pass includes a passed drill | 100%                                                                  | Every month          | ISMS Owner                   | T11, T29           | **Not met: 55 of 62.** Six runs failed and one was cancelled, all from 20 to 22 October 2026; every run since 22 October has passed. Whether a failure was in the drill or an earlier step is not yet recorded ([IC deploy-dev](https://github.com/anshacerbia2/identity-control/actions/workflows/deploy-dev.yml), [OC deploy-dev](https://github.com/anshacerbia2/organization-control/actions/workflows/deploy-dev.yml)) |
| O5  | Keep secrets out of public repositories                       | Secrets found in tracked files or history                                                                                                                                                       | 0                                                                     | Every month          | Information Security Officer | T5, T23            | **Met, by a manual check** of the seven code repositories on 31 October 2026. Automatic scanning is T5                                                                                                                                                                                                                                                                                                                      |
| O6  | Have a second person check each change                        | Share of merges to `main` approved by a person other than the author                                                                                                                            | 100%                                                                  | Before production    | ISMS Owner                   | T19, T42           | **Not met: 0%.** There is no second maintainer yet (R23)                                                                                                                                                                                                                                                                                                                                                                    |
| O7  | Make a changed approved document effective only once approved | Approved documents changed and merged before their approval was recorded ([GDC-000 §2.6.7](../00-governance/GDC-000-governance-policy.md))                                                      | 0                                                                     | Every quarter        | Architecture Authority       | T42                | **Not met: 1** on 1 November 2026 (NC-2). Every change since has been ratified before or at its merge                                                                                                                                                                                                                                                                                                                       |
| O8  | Keep the ISMS records current                                 | ISMS records past their review date                                                                                                                                                             | 0                                                                     | Every quarter        | ISMS Owner                   | —                  | **Met: 0 of 8**                                                                                                                                                                                                                                                                                                                                                                                                             |

### How results are measured

- **Sources.** O1, O2 and O4 come from GitHub Actions run history. O3 and O8 come from the ISMS records. O5 comes from the secret scan once T5 is built, and by hand until then. O6 and O7 come from pull request history.
- **When.** The monitoring role updates the latest result at each review of this record, and before each management review (T36). From 3 November 2026, a result that misses its target by its date is a nonconformity and is entered in [ISMS-008](ISMS-008-nonconformity-log.md). The results above come from before the objectives were set; those that broke an existing rule are already there (NC-1, NC-2).
- **Evaluation.** The ISMS Owner reports the results to Top Management at the management review. Top Management decides whether an objective, its target or its actions change.

## Review & Change Control

- **Reviewer and approver:** the ISMS Owner reviews; Top Management approves ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)).
- **Cadence:** every 180 days at most; the latest results are updated every quarter. The next review is due by 2 May 2027.
- **Early review when:** staging or production is built; the policy or the risk register changes in a way that affects an objective; an objective is missed twice in a row; after an incident, a nonconformity, an audit finding or a management review decision.

## Open Gaps

| Gap                                                                | Treatment                         |
| :----------------------------------------------------------------- | :-------------------------------- |
| O2 cannot be measured until a failed scheduled run raises an alert | T4                                |
| O5 is measured by hand                                             | T5                                |
| No objective yet for production availability or service levels     | Added when staging is built (T17) |

## References

- **[R1]** ISO/IEC 27001:2022. Cited by clause number and title only.
- **[R2]** [ISMS-004 Risk Register](ISMS-004-risk-register.md) and [ISMS-005 Treatment Plan](ISMS-005-risk-treatment-and-soa.md).
- **[R3]** GitHub Actions run history of identity-kernel, identity-control and organization-control, read on 3 November 2026.
