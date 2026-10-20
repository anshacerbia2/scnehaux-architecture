---
doc_meta:
  id: ADR-UIP-REL-001
  title: Public npm Registry with Trusted Publishing for UI Platform Releases
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: proposed
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-20
  created: 2026-10-20
  created_date: 2026-10-20
  created_by: UI Platform Team
---

# Public npm Registry with Trusted Publishing for UI Platform Releases (ADR-UIP-REL-001)

> **Implementation boundary:** this proposed decision publishes nothing. It answers lien L3 of the UI Platform P0 exit (long-term package storage and signing) and, once accepted, is implemented by a release workflow in the UI repository and by revisions of STD-UIP-ENG-001 section 3.5 (3) and SAD-003 section 3.2.

---

## 1. Title

Publish `@scnx/core-ui` and `@scnx/system` to the public npm registry under the existing `@scnx` scope, through npm trusted publishing with provenance from the UI repository's GitHub Actions, on a `2.0.0` release line, until the Developer Platform supplies a registry.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                | Approver                                         |
| ---------- | -------- | ------------ | ------------------------ | ------------------------------------------------ |
| 2026-10-20 | proposed | foundational | Pending principal review | Pending Architecture Review Board (Ansha Cerbia) |

## 3. Context

SAD-003 section 3.2 names the Developer Platform as the supplier of "CI runners, package storage, provenance, and signing". No Developer Platform registry exists. Lien L3 of the P0 exit (owner: Release Lead, due before the stable release on 2026-12-04) requires long-term package storage and signing: today the verified tarballs live only as CI artifacts, which GitHub keeps for at most 90 days (UI TDD packaging R2). ROADMAP phase 3 (target 2026-11-20) needs a repeatable release pipeline and named consumer pilots, and a pilot cannot install a package that is not published.

Registry facts, 2026-10-20:

- The npm scope `@scnx` already exists. Its organization lists `@scnx/core-ui`, `@scnx/design-system`, and `@scnx/ui`, all maintained by one npm account. `@scnx/core-ui@1.0.0` was published on 2025-11-28 and is its `latest`; `@scnx/design-system` and `@scnx/ui` have versions 1.0.0 to 1.0.2. `@scnx/system` is not published.
- npm never reuses a version: "Once `package@version` has been used, you can never use it again" [R3]. The UI release contract's first stable version, `1.0.0` (STD-UIP-ENG-001 section 3.5 (3)), therefore cannot be published for `@scnx/core-ui`.
- A pre-release has "lower precedence than a normal version" [R5], so `1.0.0` satisfies `^1.0.0-beta.0`. The packed `@scnx/system` declares exactly that peer range on `@scnx/core-ui`; installed from npm, it would accept the 2025 package, which has a different API. The UI repository's semver check confirms that `^1.0.0-beta.0` resolves to `1.0.0` when both exist.
- The GitHub account `scnx` belongs to an unrelated user (created 2015). GitHub Packages scopes npm packages to the owning account or organization [R6], so it cannot host `@scnx`.

## 4. Decision Drivers

- No long-lived publishing secret held by the UI Platform team (ADR-UIP-SEC-001, drivers).
- Provenance that consumers can verify, continuing the SLSA provenance of ADR-UIP-SEC-001.
- The published bytes are the tarballs CI verified and attested, never a rebuild (UI TDD packaging R3).
- Consumers install with their normal package manager, version ranges, and no registry credential.
- No published version is ever modified or overwritten (STD-UIP-ENG-001 section 3.5 (3)).
- The package names in the release contract, fixtures, and documentation stay `@scnx/core-ui` and `@scnx/system`.

## 5. Decision

1. **Registry:** the public npm registry, under the `@scnx` scope. Before the first publish, the Release Lead confirms that the `@scnx` organization and its maintainer account belong to Scnehaux and enables two-factor authentication for every member.
2. **Publishing identity:** npm trusted publishing [R1]. Each package on npmjs.com trusts exactly one publisher: the UI repository's release workflow on a GitHub-hosted runner. No npm token is created or stored. Every publish carries npm provenance, "signed by Sigstore public good servers and logged in a public transparency ledger" [R2].
3. **Release workflow:** started by a person, it runs in a GitHub environment whose required reviewer is the Release Lead. It downloads the tarballs of one CI run on `main`, checks their digests against that run's evidence packet and attestations, and publishes those files unchanged. A failed check publishes nothing.
4. **Channels:** a pre-release is published with `--tag beta`; `latest` moves only on a stable release. npm sets `latest` on every publish "unless the `--tag` option is used" [R4], so the workflow always passes `--tag`.
5. **Version line:** the UI Platform continues on a new major version: pre-releases are `2.0.0-beta.N`, and `2.0.0` is the first stable release, for both packages in lockstep. Version `1.x` of `@scnx/core-ui` stays the 2025 package. This replaces `1.0.0-beta.N` and `1.0.0` in STD-UIP-ENG-001 section 3.5 (3) by a revision of that standard after this decision is accepted.
6. **Earlier packages:** `@scnx/core-ui@1.0.0`, `@scnx/design-system`, and `@scnx/ui` are deprecated with `npm deprecate` and a message naming `@scnx/system@2` and `@scnx/core-ui@2`. They are not unpublished: registry data is immutable [R3], and a deprecation leaves existing installs working.
7. **Long-term storage:** the registry keeps every published tarball; the release record of each release (UI TDD packaging RC6) records the registry integrity value, the provenance, and the evidence-packet digest. Builds of `main` that are not released keep the 90-day CI retention.
8. **Successor:** when the Developer Platform supplies a registry, a successor decision moves publishing there; the package names and versions continue.

## 6. Consequences

### Positive (Pros)

- Lien L3 has a concrete answer before the stable date: durable storage, signed provenance, and no stored secret.
- Pilots install `@scnx/system@beta` with no registry credential and normal ranges.
- The `2.0.0` line can never resolve to the 2025 packages.

### Negative (Cons)

- Every published version is public and permanent, like the attestations of ADR-UIP-SEC-001; the UI repository is already public, so no new information is exposed.
- A new major version for a package whose `2.0.0` is its first stable release can confuse readers; the release notes explain it.
- Publishing depends on npm and Sigstore availability.
- The decision relies on an npm account the UI Platform team does not administer as an organization; item 1 makes that explicit.

### Operational

- The npm organization owner configures trusted publishing per package and the GitHub environment reviewer once; both are repository and registry settings, outside the code.
- A failed publish is retried by rerunning the workflow; npm rejects a version that was already published, so a retry cannot overwrite one.

## 7. Compliance Impact

Answers lien L3 (P0 exit review, decision D3) and ADR-UIP-SEC-001 item 6 for package storage; ADR-UIP-SEC-001 stays in force for SBOMs, gates, and build attestations. After acceptance: STD-UIP-ENG-001 section 3.5 (3) is revised to the `2.0.0` line; SAD-003 section 3.2 names the public npm registry as the interim package storage; the Technology Radar gains `npm-trusted-publishing` as a `trial` entry pending ARB. No waiver is requested.

## 8. Alternatives Considered

- **GitHub Packages npm registry:** packages must be scoped to the owning GitHub account or organization [R6], and the `scnx` account belongs to someone else, so every package would be renamed. Installing even a public package needs an access token [R7], a classic personal access token only [R7], so every consumer and CI job would hold a credential.
- **Wait for the Developer Platform registry:** keeps SAD-003 unchanged, but no pilot can install a package before the phase 3 target, and L3 stays open with no date.
- **GitHub Releases holding the tarballs:** durable and attested, but consumers install by URL, with no version ranges or dist-tags, and `@scnx/system`'s peer on `@scnx/core-ui` cannot be resolved by range.
- **Keep the `1.0.0-beta.N` line on npm:** the first stable `1.0.0` cannot be published [R3], and `^1.0.0-beta.N` already resolves to the 2025 package [R5].
- **A new scope (for example, `@scnehaux`):** avoids the version collision, but renames both packages across the contract, fixtures, and documentation, and leaves the `@scnx` packages without a successor to point to.
- **Publishing with a stored npm automation token:** works on any runner, but a long-lived write token can be "compromised, accidentally exposed in logs, or require manual rotation" [R1].

## 9. References

Retrieved 2026-10-20.

Informative:

- [R1] npm Docs, Trusted publishing for npm packages, `content/packages-and-modules/securing-your-code/trusted-publishers.mdx` at npm/documentation commit `4e8e03b978033529bf8f50d74305b29939eb022c`: <https://github.com/npm/documentation/blob/4e8e03b978033529bf8f50d74305b29939eb022c/content/packages-and-modules/securing-your-code/trusted-publishers.mdx>. Trusted publishing works "using OpenID Connect (OIDC) authentication, eliminating the need for long-lived npm tokens"; "each publish uses short-lived, cryptographically-signed tokens that are specific to your workflow and cannot be extracted or reused"; long-lived write tokens "can be compromised, accidentally exposed in logs, or require manual rotation"; it supports "GitHub Actions (GitHub-hosted runners)", and "Self-hosted runners are not currently supported". Supports items 2 and 3.
- [R2] npm Docs, Generating provenance statements, same commit: <https://github.com/npm/documentation/blob/4e8e03b978033529bf8f50d74305b29939eb022c/content/packages-and-modules/securing-your-code/generating-provenance-statements.mdx>. "When an npm package is published with provenance, it is signed by Sigstore public good servers and logged in a public transparency ledger"; "you must build your package with a supported cloud CI/CD provider using a cloud-hosted runner"; the `repository` in `package.json` must be public and match "(case-sensitive) where you are publishing with provenance from". Supports item 2.
- [R3] npm Docs, npm Unpublish Policy, `content/policies/unpublish.mdx`, same commit: <https://github.com/npm/documentation/blob/4e8e03b978033529bf8f50d74305b29939eb022c/content/policies/unpublish.mdx>. "Registry data is immutable, meaning once published, a package cannot change"; "Once `package@version` has been used, you can never use it again. You must publish a new version even if you unpublished the old one." Supports items 5 and 6.
- [R4] npm Docs, `npm dist-tag` (CLI v11), same commit: <https://github.com/npm/documentation/blob/4e8e03b978033529bf8f50d74305b29939eb022c/content/cli/v11/commands/npm-dist-tag.mdx>. "Publishing a package sets the `latest` tag to the published version unless the `--tag` option is used"; "Typically, projects only use the `latest` tag for stable release versions, and use other tags for unstable versions such as prereleases." Supports item 4.
- [R5] Semantic Versioning 2.0.0, item 11, at commit `f99d5485190a47c0863949e7da810a5553e0ed4d` (STD-UIP-ENG-001 [1]): "When major, minor, and patch are equal, a pre-release version has lower precedence than a normal version: Example: 1.0.0-alpha < 1.0.0." Supports item 5.
- [R6] GitHub Docs, Working with the npm registry, at github/docs commit `666463860bec200da6c8db9cb9334e7335d9b753`: <https://github.com/github/docs/blob/666463860bec200da6c8db9cb9334e7335d9b753/content/packages/working-with-a-github-packages-registry/working-with-the-npm-registry.md>. GitHub Packages "only supports scoped npm packages"; publishing to the "My-org" organization requires the name `@my-org/test`. Supports the first alternative.
- [R7] GitHub Docs, reusables `package_registry/authenticate-packages` and `package_registry/packages-classic-pat-only`, same commit: "You need an access token to publish, install, and delete private, internal, and public packages"; GitHub Packages "only supports authentication using a personal access token (classic)". Supports the first alternative.

In-repository and registry evidence (2026-10-20): the npm registry metadata of `@scnx/core-ui`, `@scnx/design-system`, and `@scnx/ui` and the `@scnx` organization's package list; the GitHub account `scnx` (user, created 2015-04-24); `@scnx/system`'s packed peer range `^1.0.0-beta.0` on `@scnx/core-ui`, which the `semver` package resolves to `1.0.0` when both exist.
