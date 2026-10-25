---
doc_meta:
  id: ADR-UIP-VIS-002
  title: Design Reference Repository for the Visual Target
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-25
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: UI Platform Team
---

# Design Reference Repository for the Visual Target (ADR-UIP-VIS-002)

> **Implementation boundary:** this decision changes no package. SAD-003 2.4.0 adds the repository to its document topology (section 2.1); ui-platform PLAN cites the reference by path; `anshacerbia2/scnehaux-design` carries the layout and labels below.

---

## 1. Title

Keep the visual target of the platform, the Scnehaux UI component reference and the product concepts, as files in one repository, `anshacerbia2/scnehaux-design`, that every person and coding agent can read; the repository is a reference, never a second source of rules, contracts, or values.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                                 |
| ---------- | -------- | ------------ | ------------------------- | ---------------------------------------- |
| 2026-10-24 | accepted | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |

Accepted under the rule Ansha Cerbia stated on 2026-10-22 (ADR-UIP-CMP-001, section 2). On 2026-10-24 Ansha Cerbia chose the separate repository ("oke gas a"), asked for one folder per design and the default theme only ("dibikin per folder ya designnya, bikin yg default aja"; that theme is `industrial` since 2026-10-25, ADR-UIP-VIS-001 item 7), and asked that the architecture, plan, and roadmap be aligned with it ("lo adjust keseluruhan docs terkait").

## 3. Context

Until 2026-10-24 the designs existed only as two private canvases in Claude: the Scnehaux UI design-system reference (42 component cards and a cover, built from ADR-UIP-VIS-001) and "Platform Dashboard Concepts" (ten product boards). A canvas opens only in its owner's signed-in account, so the coding agent working on the owner's machine could not read the target it was building to. On 2026-10-24 both were exported, byte for byte, to `anshacerbia2/scnehaux-design` (#1 to #3), with renders and a GitHub Pages site.

Three facts make that repository an architecture question rather than a convenience:

- SAD-003 section 2.1 keeps "one deliberately small project-repository execution set" and says the project repository "must not introduce a second architecture source of truth" [R1]. The new repository was not in that set.
- The exported brand book restates ADR-UIP-VIS-001 (materials, the ladder, ink and blue, the stage, type voice) and adds sections that no ADR or STD holds: content voice, the motion signature "the rise", the icon grammar, and logo usage.
- The concept boards are design-canvas sources (`.dc.html`) whose static pages and images are produced by the design tool's runtime, which the repository does not contain. SAD-003 section 4.2 asks that generated files have one producer and never be edited by hand [R1].

## 4. Decision Drivers

- One readable place: the target a component or screen is built to must be reachable by every person and agent that builds it, without the owner's account.
- One authority per fact: rules stay in ADRs and STDs, component contracts in specifications (ADR-UIP-CMP-001), values in `@scnx/system` (ADR-UIP-TKN-004 item 1).
- Reviewable change: a design changes by pull request, as code does.
- Honest generation: a generated file names its producer, and a producer the repository cannot run is stated, not hidden.

## 5. Decision

1. **The reference.** `anshacerbia2/scnehaux-design` holds the visual target: `design-system/` (the brand book `README.md`, `components/<Name>/` cards with `preview.html` and `README.md`, `components/bundle.css`, assets, fonts, and a viewer) and `concepts/<group>/` (one folder per group of product boards). It is non-normative. Where a card and a component specification disagree, the specification governs until a pull request changes it; where the reference's values and `@scnx/system` disagree, the package wins and the reference is regenerated.
2. **Layers.** Scnehaux UI is the design system; a theme supplies only colour values. Rules, structure, and components are shared; each theme is `design-system/themes/<theme-id>/` with a snapshot of its tokens and its renders. `industrial` is the theme the platform ships with (named `default` until 2026-10-25, ADR-UIP-VIS-001 item 7); another theme is a sibling folder that changes colours, never rules or structure (ADR-UIP-VIS-001 items 6 and 7).
3. **The brand book's status.** A section that restates ADR-UIP-VIS-001 cites it and adds nothing binding. Content voice, the motion signature, the icon grammar, and logo usage are guidance: they bind a component only after an ADR or STD revision records them. The brand book states this at its top.
4. **Producers.** Component renders are produced in the repository from `tokens.css` and `bundle.css` with a headless browser, by a script the repository holds. Concept boards are edited as `.dc.html`; their `.html` and `.png` are produced by the design tool's runtime outside the repository and committed with their source in the same pull request. That producer cannot run from the repository; a board that must change without the tool is first converted to a plain-HTML source.
5. **Change flow.** A design change lands in the repository by pull request first; a canvas is republished from the merged files, never the reverse.
6. **Consumers.** ui-platform PLAN rows cite cards by path; ui-platform-docs and Product repositories read the reference; no package or build depends on it.

## 6. Consequences

### Positive

- Local agents and reviewers build to the same target the owner sees.
- The reference cannot silently become a rulebook: its status and its producers are written down.

### Negative

- A second place to keep in step: the token snapshot and card renders must be regenerated when `@scnx/system` changes values (ui-platform PLAN row I6).
- Concept boards still depend on one tool to regenerate their pages.

### Operational Impact

- Each value change in `@scnx/system` that a card shows is followed by a regeneration pull request in the reference.

### Security Impact

- The repository is public; it holds designs and synthetic data only, no credentials or customer data (SAD-003 section 5.3).

## 7. Compliance Impact

SAD-003 2.4.0 lists the repository in section 2.1 with its authority boundary, and lists ADR-UIP-TKN-004, ADR-UIP-VIS-001, and this decision among the UI authorities of section 2. No waiver is requested.

## 8. Alternatives Considered

- **Keep the canvases as the only copy:** unreachable for any agent or person without the owner's account.
- **Inside ui-platform:** its documentation gate admits Markdown only within the documentation boundary, and product concepts (IAM, consoles, SaaS) are not UI Platform artifacts.
- **Inside ui-platform-docs:** the site documents the published packages; product concepts and the token snapshot do not belong to it.
- **Figma as the source:** ADR-UIP-TKN-004 makes a design file a consumer of the contract, and the team's Figma plan holds one mode per collection; a file is not reviewable as a diff.

## 9. References

Retrieved 2026-10-24.

- [R1] SAD-003 2.3.0, section 2.1: "The UI Platform uses one normative design hierarchy and one deliberately small project-repository execution set"; "The project repository must not introduce a second architecture source of truth"; section 4.2: "Generated files have one producer and are never hand-edited". Supports the context and items 1, 3, and 4.
- [R2] `anshacerbia2/scnehaux-design` pull requests #1 (export), #2 (design system and theme separated), and #3 (static pages and GitHub Pages). Supports the context and item 2.
