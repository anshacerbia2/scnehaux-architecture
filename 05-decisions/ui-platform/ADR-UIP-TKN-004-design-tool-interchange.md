---
doc_meta:
  id: ADR-UIP-TKN-004
  title: Design-Tool Interchange through a DTCG Profile of the Token Build
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-23
  created: 2026-10-23
  created_date: 2026-10-23
  created_by: UI Platform Team
---

# Design-Tool Interchange through a DTCG Profile of the Token Build (ADR-UIP-TKN-004)

> **Implementation boundary:** the token build of `@scnx/system` emits the profile (UI repository, TDD tokens FG1-FG6). The bridge that builds styles and components in a design file is a separate implementation that must meet item 4 before it is used.

---

## 1. Title

Give design files (Figma) the UI Platform's tokens as a generated, one-way profile of the token build in the Design Tokens Format Module 2025.10, and build every design-file asset from that profile and the published design-system reference, never from values typed into the design tool.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver                                 |
| ---------- | -------- | ------------ | ------------------------- | ---------------------------------------- |
| 2026-10-23 | accepted | foundational | Architecture Review Board | Ansha Cerbia (Architecture Review Board) |

Accepted under the rule Ansha Cerbia stated on 2026-10-22 (ADR-UIP-CMP-001, section 2): a decision based on best practice and battle-tested, referenced solutions is approved directly. On 2026-10-23 Ansha Cerbia chose the free path for Figma ("yes pake jalur gratis") and asked that the Figma work be documented ("jgn lupa terkait figma masuk ke docs").

## 3. Context

STD-UIP-TKN-001 makes DTCG 2025.10 the interchange target, and ADR-UIP-TKN-003 records that mapping to Figma "requires explicit converters and tests". ADR-UIP-CMP-001 rejected design files as the source of component contracts because they sit "outside the repository and its gates". On 2026-10-23 the platform had a design-system reference for its visual identity (materials, the 4 · 8 · 12 · 16 · 24 radius ladder, ink and Scnx Blue), and no path from the tokens to a design file other than retyping 412 colors per mode.

Constraints measured on 2026-10-23:

- Figma's variable import reads DTCG JSON, "A new mode will be created for each file you import", keeps only tokens present in every file with one type, and accepts colors in sRGB or HSL only [R1]. Variables are colors, numbers, strings, and booleans [R6]; shadows, durations, and typography composites cannot be variables.
- Modes depend on the plan [R1]. The organization's Figma team is on the Starter plan with a View seat; Starter's MCP server allowance is "Up to 20 per month" [R3]. The Variables REST API "is available to full members of Enterprise orgs" [R4].
- The palette is Display P3; the gate measures four display paths, srgb-clip among them, and PG6 bounds the sRGB-clipped rendering within 0.02 OKLab of the gamut-mapped one.
- FigCraft, an MIT plugin with a local MCP server, was proposed as the bridge. At its latest commit `94d0ab90b58d7e9efd3e2b42e93d7d604b290c8d` (2026-06-03) it converts a color only when the value is a hex string and passes any other value to Figma unchanged, so DTCG 2025.10 color objects are not converted; it reads no code syntax from token files; and it infers variable scopes from words in the path, so `icon` and `shadow` tokens receive fill scopes [R5].

## 4. Decision Drivers

- One source: TKN-008 forbids hand-edited values in code; a design file must not reintroduce them.
- What a designer picks must be what the gate measured, in every theme and mode.
- Developers read code syntax in Dev Mode; it must equal the CSS custom property.
- The path must work on the current Starter plan, gain modes and libraries on a paid plan without rework, and not depend on a metered service.
- A tool with write access to design files is supply chain: its source is reviewed and pinned.

## 5. Decision

1. **The repository is the only source.** A Figma file is a consumer of the token contract and of the design-system reference. Nothing is synchronized back. A change proposed in Figma becomes a pull request to the token source or the reference, gated like any other change.
2. **The token build emits a design-tool profile** (TDD tokens FG1-FG6) as package exports of `@scnx/system`: `tokens/figma/<theme>.<mode>.color.tokens.json` (every Tier-2 color of one mode, identical key sets across modes, DTCG 2025.10 `srgb` color objects with `hex`, sRGB-clipped so each value equals the srgb-clip path the gate measured) and `tokens/figma/<theme>.dimension.tokens.json` (the Tier-2 dimension domain in pixels). Every token carries `$extensions["com.scnehaux.ui"]` with its CSS name and WEB code syntax `var(--ds-…)`. Groups follow the canonical path, so variables are named `color/neutral/surface/canvas/default`.
3. **Variables reach Figma by its native import or by a bridge.** One color collection holds a mode per color file (every theme and mode: Light, Dark, Achromatic light, Achromatic dark), and one dimension collection holds a mode per theme, so a frame switches theme and mode with one mode picker. On a plan without modes only the light mode of the `industrial` theme (named `default` until 2026-10-25) is filled; the other modes are added, from the same files, once the plan allows them.
4. **A bridge is any tool that writes to a design file through the Figma Plugin API, and it must:**
   1. read the profile files unmodified, DTCG 2025.10 color objects included;
   2. set each variable's WEB code syntax from `$extensions["com.scnehaux.ui"].codeSyntax`;
   3. set scopes from the Tier-2 grammar, never from words in a name: surface `FRAME_FILL`, `SHAPE_FILL`; text `TEXT_FILL`; icon `SHAPE_FILL`, `STROKE_COLOR`; border `STROKE_COLOR`; shadow `EFFECT_COLOR`; radius `CORNER_RADIUS`; spacing `GAP`; border width `STROKE_FLOAT`; z-index none [R6];
   4. build text styles, effect styles (the materials), and components from the token JSON and the design-system reference, bound to the variables;
   5. run from reviewed source pinned to a commit, locally or through the official MCP server, with no personal access token stored in a repository;
   6. be idempotent: find assets by name, update them in place, and never delete an asset it did not create.
5. **Components in Figma map back to code** through Code Connect to their `@scnx/system` entries once a bridge has built them.

## 6. Consequences

### Positive

- A designer's palette is the product's palette in every theme and mode, and Dev Mode shows the property a developer writes.
- The profile is plain DTCG: Figma's import, a first-party plugin, or a patched third-party plugin can read it, so the bridge stays replaceable.
- The free plan works today (one mode); a paid plan adds modes and libraries with the same files.

### Negative

- Figma holds sRGB values; P3 displays show slightly less chroma in a design file than in the product (bounded by PG6).
- Shadows, motion, and typography need a bridge; the native import alone yields colors and dimensions.
- The first-party bridge is code to own; FigCraft at `94d0ab9` fails items 4.1 to 4.3 and would need a maintained fork, so on 2026-10-23 Ansha Cerbia chose Figma with the repository's plugin ("ya gw rasa figma saja").

### Operational Impact

- The files change only with a token-build change and ship with each release; a design file is refreshed by importing the files of the release it targets.

### Security Impact

- Bridges have write access to every file of the signed-in account. Item 4.5 keeps their source reviewed and pinned and keeps tokens out of repositories.

## 7. Compliance Impact

No standard changes. STD-UIP-TKN-001's DTCG target is unchanged: the profile is an output of the Sass source, not the canonical DTCG source. TDD tokens records FG1-FG6. ADR-UIP-CMP-001's rejection of design files as a source stands.

## 8. Alternatives Considered

- **Two-way synchronization (Tokens Studio with GitHub sync):** designers could edit tokens in Figma, but a second editable source would bypass the palette engine and the gate, which TKN-008 and ADR-UIP-CMP-001 rule out.
- **The Variables REST API from CI:** automatic, but available only to full members of Enterprise organizations [R4].
- **The official Figma MCP server as the only writer:** first party, but metered at up to 20 calls a month on Starter [R3], too few to build a library.
- **FigCraft as the bridge:** item 4 is the bar; at `94d0ab9` it does not meet 4.1 to 4.3 [R5], and it has had no commit since 2026-06-03.
- **Gamut-mapped instead of clipped sRGB:** closer to the P3 hue, but a value no gate measured.
- **Hex strings instead of DTCG 2025.10 color objects:** what FigCraft reads, but not the format the standard targets.

## 9. References

Retrieved 2026-10-23.

- [R1] Figma Help Center, "Modes for variables", article 15343816063383: <https://help.figma.com/hc/en-us/articles/15343816063383-Modes-for-variables>. "Design tokens must be in a JSON file and follow the Design Tokens Community Group (DTCG) format"; "A new mode will be created for each file you import"; only tokens present in all imported files with a supported type, value, and one type are created; supported color spaces are HSL and sRGB; "The number of modes you can create per variable collection depends on your plan." Supports the context and items 2 and 3.
- [R2] Design Tokens Community Group, Design Tokens Format Module 2025.10, Color module (28 October 2025): <https://www.designtokens.org/tr/2025.10/color/>. A color `$value` is `{ colorSpace, components, alpha?, hex? }`; `srgb` components are `[red, green, blue]` in 0-1; `hex` is an optional six-digit fallback. Supports item 2.
- [R3] Figma, "Rate limits and access", Figma MCP server: <https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/>. Starter plan, or View or Collab seat: "Up to 20 per month". Supports the context and the alternatives.
- [R4] Figma, REST API, Variables endpoints: <https://developers.figma.com/docs/rest-api/variables-endpoints>. "This API is available to full members of Enterprise orgs"; POST requires "edit access to the file" and the `file_variables:write` scope. Supports the alternatives.
- [R5] DivikWu/figcraft at commit `94d0ab90b58d7e9efd3e2b42e93d7d604b290c8d` (MIT): `packages/adapter-figma/src/adapters/variable-mapper.ts`, `dtcgValueToFigma` (`case 'color'`: `if (typeof value === 'string') return hexToFigmaRgba(value); return value as VariableValue;`) and `inferScopes` (scopes from `lower.includes('surface' | 'border' | 'text' …)`); `packages/core-mcp/src/dtcg.ts`, `parseDtcg`. Supports the context, item 4, and the alternatives.
- [R6] Figma, Plugin API, `VariableScope`: <https://developers.figma.com/docs/plugins/api/VariableScope>. COLOR scopes `ALL_FILLS`, `FRAME_FILL`, `SHAPE_FILL`, `TEXT_FILL`, `STROKE_COLOR`, `EFFECT_COLOR`; FLOAT scopes include `CORNER_RADIUS`, `WIDTH_HEIGHT`, `GAP`, `STROKE_FLOAT`; "`ALL_SCOPES` is a special scope that means that the variable is shown in the picker for all fields." Supports item 4.3.

In-repository evidence (2026-10-23): ui-platform pull request #109, `packages/design-system/scripts/tokens/figma.mjs` and its tests (per-mode key-set parity, PG6 bound, code syntax, pixel dimensions), and the repository's Figma plugin (`packages/design-system/figma-plugin/`, `scripts/figma/plan.mjs`), a first-party bridge meeting item 4.1-4.3 and 4.5-4.6 for variables, text styles, and effect styles, tested against a Plugin API double; components (item 4.4) follow.
