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
  last_reviewed: 2026-10-27
  created: 2026-10-24
  created_date: 2026-10-24
  created_by: UI Platform Team
---

# Design Reference Repository for the Visual Target (ADR-UIP-VIS-002)

> **Implementation boundary:** this decision changes no package. SAD-003 2.4.0 added the repository to its document topology (section 2.1), and 2.7.0 describes its revision-2 layout; ui-platform PLAN cites the reference by path; `anshacerbia2/scnehaux-design` carries the layout and labels below (#26 and #27).

---

## 1. Title

Keep the visual target of the platform, the Scnehaux UI component reference and the product concepts, as files in one repository, `anshacerbia2/scnehaux-design`, that every person and coding agent can read; the repository is a reference, never a second source of rules, contracts, or values.

## 2. Status

| Date       | Status                | ADR Type     | Reviewers                 | Approver                  |
| ---------- | --------------------- | ------------ | ------------------------- | ------------------------- |
| 2026-10-24 | accepted              | foundational | Architecture Review Board | Architecture Review Board |
| 2026-10-26 | accepted (revision 2) | foundational | Architecture Review Board | Architecture Review Board |
| 2026-10-27 | accepted (revision 3) | foundational | Architecture Review Board | Architecture Review Board |

Accepted under the rule the owner stated on 2026-10-22 (ADR-UIP-CMP-001, section 2). On 2026-10-24 the owner chose the separate repository ("oke gas a"), asked for one folder per design and the default theme only ("dibikin per folder ya designnya, bikin yg default aja"; that theme is `scnx-platform` since 2026-10-26, ADR-UIP-VIS-001 item 7), and asked that the architecture, plan, and roadmap be aligned with it ("lo adjust keseluruhan docs terkait").

Revision 2 was decided by the owner on 2026-10-26 with ADR-UIP-VIS-001 revision 4: a brand book belongs to a theme, not to a product ("brandbook artinya per theme kan bukan lagi per product"), so the repository holds one design per theme, each with its brand book, and what every theme shares once.

Revision 3 was decided by the owner on 2026-10-27, accepting the recommendation of the documentation and design agents ("gw ikut rekomen lo", as their request for this revision records it): the documentation site's design has its source in the site's own repository, `anshacerbia2/ui-platform-docs`. The site had outgrown its first drawings in `scnx-platform/`, and two places describing one site's pages and behaviour would drift.

### Revision history

- **Revision 1 (2026-10-24):** the repository, `design-system/` with the brand book `README.md` and a hand-made snapshot of each theme's tokens in `design-system/themes/<theme-id>/`, and product boards in `concepts/<group>/`.
- **Revision 2 (2026-10-26):** one folder per theme's design (`scnx-platform/`, `scnx-saas/`), each with its brand book, and the shared brand page `brand/Brand.html`; earlier concepts in `others/`, and `concepts/` as redirects only; tokens synced byte for byte from the package's own emitter at a pinned ui-platform commit, in place of the hand-made snapshot (items 1, 2, and 4).
- **Revision 3 (2026-10-27):** the documentation site's design moves to `anshacerbia2/ui-platform-docs`; the site's first drawings in `scnx-platform/` stay as history and no longer follow it; the brand books stay here and current, and the site reads its theme's brand book (items 1 and 6).

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

1. **The reference.** `anshacerbia2/scnehaux-design` holds the visual target:
   - `brand/Brand.html`: what every theme shares, written once (the name and the mark, the voice and copy rules, the icon grammar, and how themes, products, and brand books relate). The mark's check stays Scnx Blue in every theme, because it is artwork, not a token.
   - One folder per shipped theme's design, each with its brand book: `scnx-platform/` (the platform: IAM, AI runtime, organization, and the documentation site; `Brand-Book.html`) and `scnx-saas/` (the SaaS products; its HTML brand book follows, and until then its rules are `design-system/README.md`). `scnx-platform/` also keeps, as history, the first drawings of the documentation site (`Docs-Landing.html`, `Docs-Home.html`, `Docs-Button.html`, `square.css`, `square.js`, and `SCROLL.md`); they no longer follow the site, and `square.css` and `square.js` still draw the brand pages.
   - `design-system/`: `components/<Name>/` cards with `preview.html` and `README.md`, shared by every theme, `components/bundle.css`, assets, fonts, a viewer, and `vendor/scnx-system/` (item 2).
   - `others/`: every earlier concept, kept for reference; `concepts/` holds redirect stubs only, so links already shared keep working.

   A brand book belongs to a theme, not to a product: every product on one theme reads that theme's brand book, and a product that needs a different look gets a new theme, a new folder, and a new brand book. A product may keep thin notes (its terms, domain patterns, and the hooks it sets) that add to its theme's brand book and never change its rules. The documentation site's own design (its pages, its chrome: the nav strip, the sheets, the ruler scrollbar, the reveal, and the glide, and their behaviour) is `anshacerbia2/ui-platform-docs`, written in TDD-ui-platform-docs-001: decisions D13 to D19 and its Annex A, "Scroll Behaviour" (`docs/designs/TDD-ui-platform-docs-001-documentation-site.md#annex-a-scroll-behaviour`); the site is built on the `scnx-platform` theme and follows that theme's brand book. The reference is non-normative. Where a card and a component specification disagree, the specification governs until a pull request changes it; where the reference's values and `@scnx/system` disagree, the package wins and the reference is regenerated.

2. **Layers.** Scnehaux UI is the design system; a theme supplies only values. Rules and components are shared, and components are design-agnostic. A theme's values come from `@scnx/system` only: `scripts/sync-tokens.mjs` downloads the ui-platform commit pinned in `scripts/sync-tokens.json`, runs the package's own emitter (`packages/design-system/scripts/tokens/emit.mjs`), and copies `tokens/css/<theme-id>.css`, `tokens/json/<theme-id>.json`, and `fonts/` byte for byte into `design-system/vendor/scnx-system/`, at the package's published paths; `SOURCE.json` records the commit and a SHA-256 of every file, the emitter's dependencies are pinned to that commit's lockfile, and a check fails on a stale copy. Pages link those files and never restate a value. The component cards still use the earlier hand-made snapshot, `design-system/themes/default/`, until they are re-rendered from the package. `scnx-platform` is the theme the platform ships as its default and `scnx-saas` the second (ADR-UIP-VIS-001 item 7); another theme maps Tier-2 values, never rules, and never below the guarded floors (ADR-UIP-VIS-001 items 6 and 7).
3. **The brand books' status.** A section of the brand page or a theme's brand book that restates ADR-UIP-VIS-001 cites it and adds nothing binding. Content voice, the motion signature, the icon grammar, and logo usage are guidance: they bind a component only after an ADR or STD revision records them. Each page states this.
4. **Producers.** The vendored tokens are produced by the package's emitter at the pinned commit (item 2) and are never edited by hand. Component renders are produced in the repository from the theme's tokens and `bundle.css` with a headless browser, by a script the repository holds. A theme's live pages (`scnx-platform/`) are hand-authored HTML that link the vendored tokens, with their still frames committed beside them. Concept boards are edited as `.dc.html`; their `.html` and `.png` are produced by the design tool's runtime outside the repository and committed with their source in the same pull request. That producer cannot run from the repository; a board that must change without the tool is first converted to a plain-HTML source.
5. **Change flow.** A design change lands in the repository by pull request first; a canvas is republished from the merged files, never the reverse.
6. **Consumers.** ui-platform PLAN rows cite cards by path; ui-platform-docs reads the brand book of its theme (`scnx-platform/Brand-Book.html`), not the documentation boards; Product repositories read the reference; no package or build depends on it.

## 6. Consequences

### Positive

- Local agents and reviewers build to the same target the owner sees.
- The reference cannot silently become a rulebook: its status and its producers are written down.

### Negative

- A second place to keep in step: the sync pin must move, and the card renders be regenerated, when `@scnx/system` changes values (ui-platform PLAN row I6); the sync check makes a stale copy visible, not automatic.
- The emitter's command line, output paths, and dependencies become an interface the reference depends on; ui-platform states a change to them in its pull request.
- Concept boards still depend on one tool to regenerate their pages.

### Operational Impact

- Each value change in `@scnx/system` that a page or card shows is followed by a pull request in the reference that moves the sync pin and regenerates the renders.

### Security Impact

- The repository is public; it holds designs and synthetic data only, no credentials or customer data (SAD-003 section 5.3).

## 7. Compliance Impact

SAD-003 2.4.0 lists the repository in section 2.1 with its authority boundary, and lists ADR-UIP-TKN-004, ADR-UIP-VIS-001, and this decision among the UI authorities of section 2; SAD-003 2.7.0 describes the revision-2 layout. Revision 3 needs no SAD-003 change: section 2.1 describes the reference's layout and the documentation site's repository without naming the documentation boards as the site's target. No waiver is requested.

## 8. Alternatives Considered

- **Keep the canvases as the only copy:** unreachable for any agent or person without the owner's account.
- **Inside ui-platform:** its documentation gate admits Markdown only within the documentation boundary, and product concepts (IAM, consoles, SaaS) are not UI Platform artifacts.
- **Inside ui-platform-docs:** the site documents the published packages; product concepts and the token snapshot do not belong to it.
- **Figma as the source:** ADR-UIP-TKN-004 makes a design file a consumer of the contract, and the team's Figma plan holds one mode per collection; a file is not reviewable as a diff.

## 9. References

Retrieved 2026-10-24.

- [R1] SAD-003 2.3.0, section 2.1: "The UI Platform uses one normative design hierarchy and one deliberately small project-repository execution set"; "The project repository must not introduce a second architecture source of truth"; section 4.2: "Generated files have one producer and are never hand-edited". Supports the context and items 1, 3, and 4.
- [R2] `anshacerbia2/scnehaux-design` pull requests #1 (export), #2 (design system and theme separated), and #3 (static pages and GitHub Pages). Supports the context and item 2.
- [R3] `anshacerbia2/scnehaux-design` pull requests #26 (two designs, one per theme; tokens synced from the package's emitter) and #27 (the shared brand page; proposal revision 3), merged at `a446b2a`, retrieved 2026-10-26: `README.md` ("There are two designs, one per theme, each in its own folder with its own brand book"), `scripts/sync-tokens.mjs`, and `scripts/sync-tokens.json`. Supports revision 2 and items 1, 2, and 4.
- [R4] `anshacerbia2/scnehaux-design` commit `4e7115c` ("Square chrome superseded by the site; the brand book stays current", branch `docs/square-superseded`, on `main`), retrieved 2026-10-27: `scnx-platform/README.md`, `SCROLL.md`, `square.css`, and `square.js` marked as history. `anshacerbia2/ui-platform-docs` pull request #19 (branch `refactor/cdd-foundation`, head `c371309`, open when retrieved on 2026-10-27): commit `05c086c` first added the site's scroll behaviour as `docs/designs/SCROLL.md`, and commit `c371309` moved it into TDD-ui-platform-docs-001 as Annex A, "Scroll Behaviour", because the central governance linter admits only governed document types under `docs/`; the TDD holds decisions D13 to D19. Supports revision 3 and items 1 and 6.
