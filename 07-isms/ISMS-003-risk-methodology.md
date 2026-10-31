---
doc_meta:
  id: ISMS-003
  title: Information Security Risk Methodology
  owner: Top Management
  version: 1.0.0
  status: approved
  classification: public
  governed_by: [GDC-012, ISMS-001]
  review_cycle_days: 365
  created_date: 2026-11-01
  last_reviewed: 2026-11-01
  isms_record: risk-methodology
  iso_clauses: ['6.1.1', '6.1.2', '6.1.3', '8.2', '8.3']
  annex_a_controls: []
---

# Information Security Risk Methodology

## Purpose & Scope

This record is how Scnehaux finds, rates, decides on and treats information security risk inside the scope of [ISMS-001](ISMS-001-scope-and-context.md). It sets the scales, the acceptance criteria and who may accept what, so that two assessments of the same risk give the same answer. The risk register and the risk treatment plan with the Statement of Applicability, each a record of its own kind ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)), apply it.

Vulnerabilities in container images and dependencies have their own clock, set by [STD-GLB-009 §Container Images](../02-standards/_global/STD-GLB-009-platform-engineering.md#container-images-140). A finding fixed within that clock does not enter the register. A finding that carries a dated exception does, when the exception is taken.

## ISO/IEC 27001 Mapping

Edition: ISO/IEC 27001:2022. This record answers:

| Clause | Title                                | Where in this record                                                                              |
| :----- | :----------------------------------- | :------------------------------------------------------------------------------------------------ |
| 6.1.1  | General                              | [Risks and opportunities of the ISMS itself](#risks-and-opportunities-of-the-isms-itself)         |
| 6.1.2  | Information security risk assessment | [Scales](#scales), [Acceptance criteria](#acceptance-criteria), [The assessment](#the-assessment) |
| 6.1.3  | Information security risk treatment  | [Treatment](#treatment)                                                                           |
| 8.2    | Information security risk assessment | [When assessments run](#when-assessments-run)                                                     |
| 8.3    | Information security risk treatment  | [When assessments run](#when-assessments-run), [Treatment](#treatment)                            |

No text of the standard is reproduced.

## Record

### Risks and opportunities of the ISMS itself

The ISMS can fail to work as intended. These are tracked in the risk register like any other risk:

- **Key person.** One person holds most ISMS roles ([ISMS-002](ISMS-002-policy-and-roles.md#roles)); absence stalls approvals and recovery.
- **Records that describe instead of operate.** A record can say a control exists when nothing enforces it. The SoA therefore marks a control `implemented` only with linked evidence that a script, CI job or code enforces it ([GDC-012 §2.3.6](../00-governance/GDC-012-isms-guideline.md#236-control-status-vocabulary)).
- **Unread signals.** A failing scheduled check that nobody reads lets a deadline pass. In October 2026 a daily image scan failed for five days before it was read, and a 3-day remediation time passed.

The opportunity: because the platform is not in production yet, a control built now costs less than one retrofitted later. Treatment favours building the control into the system over writing a procedure around it.

### Scales

**Likelihood**, over the next 12 months, given the controls already in place:

| Score | Level          | Meaning                                                                    |
| :---- | :------------- | :------------------------------------------------------------------------- |
| 1     | Rare           | Not expected; would need several independent failures                      |
| 2     | Unlikely       | Could happen; no sign it has, or of anyone trying                          |
| 3     | Possible       | Has happened elsewhere in similar systems, or the precondition exists here |
| 4     | Likely         | Has happened here before, or is expected without treatment                 |
| 5     | Almost certain | Is happening, or will at the next occurrence of a routine event            |

**Impact**, the worst credible outcome, taking the highest of the four columns:

| Score | Level      | Tenants and people                                                                       | Platform                                               | Legal and contractual                            | Recovery                            |
| :---- | :--------- | :--------------------------------------------------------------------------------------- | :----------------------------------------------------- | :----------------------------------------------- | :---------------------------------- |
| 1     | Negligible | No tenant or personal data affected                                                      | A development-only inconvenience                       | None                                             | Minutes, no data lost               |
| 2     | Minor      | Development or test data only                                                            | One service degraded in development                    | None                                             | Hours                               |
| 3     | Moderate   | Personal data of a few people exposed or altered, or one tenant's service lost for hours | Trust in one service lost until rebuilt                | A notification may be required                   | A day or more, some data re-entered |
| 4     | Major      | One tenant's data exposed to another, or many people's personal data                     | A signing key or privileged access compromised         | Notification to a regulator or customer required | Days; evidence or records lost      |
| 5     | Severe     | Many tenants' data exposed or lost                                                       | The whole platform's trust lost (all tokens forgeable) | Regulatory action or contract termination likely | Weeks, or not recoverable           |

Until production exists, a risk is rated twice: **now** (development) and **at production** if nothing changes. The register shows both; the production rating decides whether a treatment is a production gate.

**Risk level** is likelihood × impact:

| Level     | Score    |
| :-------- | :------- |
| Low       | 1 to 4   |
| Medium    | 5 to 9   |
| High      | 10 to 16 |
| Very high | 20 to 25 |

### Acceptance criteria

| Risk level (after treatment) | Who may accept it                                                                                   | Review of the acceptance           |
| :--------------------------- | :-------------------------------------------------------------------------------------------------- | :--------------------------------- |
| Low                          | The risk owner                                                                                      | At the register's scheduled review |
| Medium                       | The risk owner, with the ISMS Owner's agreement                                                     | Within 180 days                    |
| High                         | Top Management only, with a dated treatment plan                                                    | Within 90 days                     |
| Very high                    | Not acceptable; MUST be treated. Top Management may accept for at most 30 days while treatment runs | Within 30 days                     |

A risk rated High or Very high **at production** MUST have a treatment that is a production gate in the owning repository's ROADMAP.

Top Management approved these values on 1 November 2026, with this record.

### The assessment

1. **Identify.** Start from the assets: services, data stores, keys and credentials, pipelines, hosts, suppliers and people (the asset inventory, planned). For each, ask what could break its confidentiality, integrity or availability. Sources:
   - design reviews of a standard, decision or design (a SAD's security section);
   - scanner findings with an exception, upstream advisories, and threat intelligence;
   - incidents, near misses, nonconformities and audit findings;
   - supplier changes and the review of the supplier register;
   - the "Known pitfalls" and "Never do" sections of runbooks, which record failures already met.
2. **Analyse.** Name the existing controls and link their evidence. Rate likelihood and impact on the scales above, now and at production. Write one line of rationale for each rating, so a later assessor can see why.
3. **Evaluate.** Compare the level with the acceptance criteria. Decide: treat, or accept with the role and the review date the criteria require.
4. **Record.** One row per risk in the risk register, with a risk owner role. A risk is described at the level needed to manage it, never how to exploit it ([GDC-012 §2.1](../00-governance/GDC-012-isms-guideline.md#21-publication-rules)).

**Consistency.** Every assessment uses these scales, unchanged, until this record changes them. A change of scale is a major version of this record and triggers a re-rating of the whole register, so results stay comparable over time.

### Treatment

For each risk to be treated, choose one or more options:

| Option | Meaning                                                            |
| :----- | :----------------------------------------------------------------- |
| Modify | Add or improve a control, preferably one that code or CI enforces  |
| Avoid  | Stop the activity or remove the asset                              |
| Share  | Move part of the risk to a supplier or insurer, under an agreement |
| Retain | Accept it, within the acceptance criteria                          |

Every chosen control is compared with ISO/IEC 27001:2022 Annex A, so no necessary control is missed. The Statement of Applicability lists all 93 Annex A controls, whether each applies and why, its control status and its evidence. Each treatment action has an owner role, a target date and the residual rating expected. The risk owner approves the plan and accepts the residual risk within their authority.

### When assessments run

- **Scheduled:** the whole register at least every 90 days ([GDC-012 §2.3.2](../00-governance/GDC-012-isms-guideline.md#232-taxonomy)).
- **On change:** before a new environment, service or supplier is used; when a standard or decision that a control relies on changes; when an exception's review date arrives.
- **On events:** after an incident, a nonconformity or an audit finding.

Each assessment is a pull request to the register, so its date, its author and what changed are in Git history. Treatment progress is reviewed at the same times, and a completed action moves its control's status in the SoA, with the evidence linked.

## Review & Change Control

- **Reviewer and approver:** the ISMS Owner reviews; Top Management approves.
- **Cadence:** every 365 days at most.
- **Early review when:** production is built (the double rating ends); the scales prove unable to separate risks that clearly differ; a management review or audit finding asks for it.

## Open Gaps

| Gap                                                                        | Treatment                                                      |
| :------------------------------------------------------------------------- | :------------------------------------------------------------- |
| The asset inventory the identification step starts from does not exist yet | Asset and script inventory record (planned)                    |
| No alert on a failed scheduled check                                       | Recorded as a risk and a treatment action in the risk register |

## References

- **[R1]** ISO/IEC 27001:2022. Cited by clause number and title only.
- **[R2]** [GDC-012 ISMS Guideline](../00-governance/GDC-012-isms-guideline.md).
- **[R3]** [STD-GLB-009 §Container Images](../02-standards/_global/STD-GLB-009-platform-engineering.md#container-images-140), for the vulnerability remediation clock based on CISA BOD 26-04.
