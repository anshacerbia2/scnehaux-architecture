---
doc_meta:
  id: ADR-GLB-FE-011
  title: Rspack-Based Toolchains for Federated Applications
  adr_type: replacement
  status: accepted
  created: 2026-09-28
  created_date: 2026-09-28
  created_by: UI Platform Architecture
  governed_by: [EAD-005]
  supersedes: [ADR-GLB-FE-002]
---

# ADR-GLB-FE-011: Rspack-Based Toolchains for Federated Applications

## 1. Title

Replace ADR-GLB-FE-002 with a build toolchain decision that names the compiler family for federated applications and keeps Webpack out of new repositories.

## 2. Status

| Date       | Status   | ADR Type    | Reviewers                   | Approver                                 |
| ---------- | -------- | ----------- | --------------------------- | ---------------------------------------- |
| 2026-09-29 | accepted | replacement | Principal 1 and Principal 2 | Ansha Cerbia (Architecture Review Board) |

## 3. Context

ADR-GLB-FE-002 requires Rsbuild for every micro-frontend host and remote and prohibits Webpack for new repositories. The existing federated applications compile with `@rspack/core` and its Module Federation plugin directly, not through Rsbuild. The replacement Module Federation decision (ADR-GLB-FE-012) states the federation contract by runtime behavior and needs a toolchain rule that does not contradict it.

The production status of every frontend governed by ADR-GLB-FE-002 cannot be established from the architecture repository. Approved Experience systems SAD-002, SAD-012, SAD-014, and SAD-015 are React frontends with no recorded deployment evidence either way. GDC-010 section 2.4.2 therefore required a replacement ADR; acceptance of this record supersedes ADR-GLB-FE-002.

## 4. Decision Drivers

- One compiler family for federation hosts and remotes, so shared-module behavior is tested once.
- No new Webpack repositories, as already decided.
- Room for the Rsbuild wrapper or direct Rspack configuration, which produce the same federation runtime.
- A toolchain rule that the host and remote fixtures in ADR-GLB-FE-012 can verify.

## 5. Decision

This decision is conditional on a separately authorized choice to use Module Federation. It does not adopt Module Federation, change its Technology Radar ring, or permit broad rollout. While Module Federation remains `assess`, only bounded evaluation and explicitly approved SAD scopes may use it.

1. **Federated applications.** When an owning SAD and accepted decision authorize Module Federation for a bounded scope, its hosts and remotes compile with an Rspack-based toolchain: Rsbuild, or `@rspack/core` with its Module Federation plugin. The owning SAD records which one. Mixing compiler families inside one federation requires a fixture that proves the ADR-GLB-FE-012 contract across them.
2. **Non-federated single-page applications, internal tools, and libraries.** Vite or an Rspack-based toolchain is permitted. A published library may use another bundler when its SAD records it and its packed-consumer tests pass.
3. **Server-rendered applications** use their meta-framework compiler, as in ADR-GLB-FE-003.
4. **Webpack** is prohibited for new repositories. Existing Webpack repositories migrate when they are next re-platformed; no new federation host or remote may be introduced on Webpack.

## 6. Consequences

- **Positive:** the existing Rspack federation configuration is compliant without a wrapper migration.
- **Positive:** the federation fixtures test one compiler family.
- **Negative:** the Platform Team maintains presets for Rsbuild, direct Rspack, and Vite.
- **Operational:** a SAD that introduces federation records its toolchain before its first release.
- **Governance:** Rspack is the conditional implementation rule for an authorized federation; it is not evidence that federation has advanced beyond `assess`.

## 7. Compliance Impact

Supersedes ADR-GLB-FE-002 on ratification. Related decisions: ADR-GLB-FE-003 and ADR-GLB-FE-012. Related standards: STD-GLB-FE-001 and STD-GLB-FE-007. No waiver is requested.

## 8. Alternatives Considered

- Keep the Rsbuild-only mandate: rejected because it forces a wrapper migration on applications that already use the same compiler and federation runtime.
- Bundler-neutral federation: rejected because it would admit Webpack for new federated repositories, which the enterprise already prohibits, and would multiply the fixtures needed to prove shared-module behavior.
