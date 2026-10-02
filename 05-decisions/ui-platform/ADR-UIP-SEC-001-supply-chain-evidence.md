---
doc_meta:
  id: ADR-UIP-SEC-001
  title: Supply-Chain Evidence with CycloneDX SBOMs and SLSA Build L2 Attestations
  adr_type: foundational
  owner: Principal UI/UX Architect
  status: accepted
  classification: public
  governed_by: [PAD-PLT-003]
  review_cycle_days: 180
  last_reviewed: 2026-10-02
  created: 2026-10-02
  created_date: 2026-10-02
  created_by: UI Platform Team
---

# Supply-Chain Evidence with CycloneDX SBOMs and SLSA Build L2 Attestations (ADR-UIP-SEC-001)

> **Sequence note:** the UI repository implemented this decision before this record existed (ui-platform pull request #35, merge commit `84f0e2d`, TDD packaging decision record V1–V6). The documentation order PAD → SAD → ADR → STD → TDD was not followed for the provenance service; this record and the SAD-003 revision close that gap, and both remain proposed until approved.

---

## 1. Title

Describe every UI Platform tarball with a CycloneDX 1.7 SBOM, gate the dependency graph on advisories and licenses, and sign build provenance at SLSA Build Level 2 through GitHub artifact attestations until the Developer Platform supplies provenance and signing.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                               | Approver                                         |
| ---------- | -------- | ------------ | --------------------------------------- | ------------------------------------------------ |
| 2026-10-02 | proposed | foundational | Pending principal review                | Pending Architecture Review Board (Ansha Cerbia) |
| 2026-10-02 | accepted | foundational | Architecture Review Board (decision D2) | Ansha Cerbia (Architecture Review Board)         |

## 3. Context

SAD-003 section 7 controls a compromised dependency with a "frozen lockfile, SBOM, applicable advisory gate, provenance" and artifact substitution with a "content digest and producer provenance". SAD-003 section 3.2 names the Developer Platform as the supplier of "CI runners, package storage, provenance, and signing". STD-GLB-FE-006 section 3.10 requires an audit of the lockfile-resolved graph, including the resolved React, React DOM, `react-server-dom-*`, and meta-framework versions, on every CI run.

The Developer Platform provides no provenance or signing service yet; which one it will provide is an open question in the UI repository's packaging TDD. PLAN P0 row 10 nevertheless requires SBOM and provenance gates before the P0 exit review. The UI repository is public on GitHub.

## 4. Decision Drivers

- SBOM and provenance in standards-based formats that any consumer can verify, as NIST SSDF PS.3.2 asks ("preferably using standards-based formats").
- Provenance a consumer can verify cryptographically: SLSA describes Build L1 provenance as "trivial to bypass or forge".
- No long-lived signing key held by the UI Platform team.
- No secret, Product data, or private information sent to a third party.
- A clean path to the Developer Platform's service when it exists.

## 5. Decision

1. **SBOM:** every packed tarball gets a CycloneDX 1.7 JSON SBOM (ECMA-424 2nd edition), validated offline against the official 1.7.2 schema. It records the NTIA minimum elements and the CISA 2025 draft additions (component hash, license, tool name, generation context). Peer dependencies are external components with a version range; copied assets carry a provenance record.
2. **Dependency gates:** CI fails on a high or critical advisory in any resolved graph (workspace and every consumer fixture) and on any lockfile package without a declared SPDX license. Exceptions are CISA VEX `not_affected` statements with an expiry, never for React-family or meta-framework advisories (STD-GLB-FE-006 section 3.10).
3. **Provenance (interim):** on every push to `main`, GitHub artifact attestations sign SLSA build provenance for each tarball and attest each SBOM, which "provides SLSA v1.0 Build Level 2". Consumers verify with `gh attestation verify`. Pull requests are not attested.
4. **Third-party data flow:** because the repository is public, each attestation is signed through the Sigstore Public Good Instance and written to its "immutable transparency log that is publicly readable on the internet". The entry contains the artifact digests and the repository, workflow, ref, and commit identity, all of which are already public. Nothing else is sent: no secret, Product data, or personal data.
5. **Isolation:** only the attesting job holds `id-token: write` and `attestations: write`; it downloads the verified tarballs and installs no dependency, so the OIDC token never reaches dependency code.
6. **Successor:** when the Developer Platform supplies provenance and signing, a successor decision moves signing there; the SBOM and gates are unchanged.

## 6. Consequences

### Positive (Pros)

- Every tarball has a verifiable origin: the signing identity is the `main` branch of the CI workflow, and a modified tarball fails verification.
- Consumers receive machine-readable SBOMs in an Ecma standard format.
- Known-vulnerable dependencies in the workspace and in the resolved consumer graphs block CI; the first run removed ten high-severity advisories.

### Negative (Cons)

- Transparency-log entries are permanent and public; they cannot be removed if the repository later becomes private.
- Verification depends on GitHub and Sigstore availability.
- A new advisory in a development tool can block an unrelated change.

### Operational

- A daily scheduled CI run catches advisories published between changes.
- A Sigstore or GitHub attestation outage blocks only the attesting job; the release owner may record a time-bound exception under GDC-004 rather than skip it.

## 7. Compliance Impact

Implements the SBOM, advisory-gate, and provenance controls of SAD-003 section 7 and STD-GLB-FE-006 section 3.10 for the UI Platform. Supports NIST SSDF PW.4.4, PO.3.2, RV.2.2, PS.2.1, and PS.3.2. Revises SAD-003 sections 3.2, 5.3, and 7 (pending ratification). Adds `cyclonedx` and `github-artifact-attestations` to the Technology Radar as `trial` entries pending ARB. No waiver is requested.

## 8. Alternatives Considered

- **Unsigned SLSA provenance (Build L1):** no third-party service, but SLSA calls L1 provenance "trivial to bypass or forge", and SSDF PS.3.2 asks for a way to "verify provenance data integrity".
- **npm `publish --provenance`:** also Sigstore-backed, but it needs a registry publication, which is out of scope until the Developer Platform registry decision.
- **A team-held signing key (for example, cosign with a stored key):** no public log, but the team must store, rotate, and revoke a long-lived secret.
- **Wait for the Developer Platform:** keeps SAD-003 section 3.2 unchanged, but leaves PLAN row 10 without provenance evidence for an unknown period.
- **SPDX instead of CycloneDX:** equally standard (ISO/IEC 5962:2021). CycloneDX is chosen because its 1.7 schema models peers as external components with version ranges and carries VEX in the same ecosystem; SPDX remains a substitute.
- **SLSA Build L3 (isolated reusable workflow):** stronger, but needs a separate reusable workflow; deferred.

## 9. References

- NIST SP 800-218, Secure Software Development Framework 1.1: <https://doi.org/10.6028/NIST.SP.800-218>. PS.3.2: "Collect, safeguard, maintain, and share provenance data for all components of each software release (e.g., in a software bill of materials [SBOM])"; Example 3: "provide a way for recipients to verify provenance data integrity".
- SLSA, Build: Track Basics: <https://github.com/slsa-framework/slsa/blob/82b296d49e4c8301e7db565f23620ffe89092a0c/spec/build-track-basics.md>. Build L1 "is trivial to bypass or forge"; Build L2 is "Signed provenance, generated by a hosted build platform".
- GitHub Docs, Artifact attestations (`github/docs` commit `0b8c768bf0d5a13560ec82fd3daa414137e2e436`): "Artifact attestations by itself provides SLSA v1.0 Build Level 2"; for public repositories the Sigstore bundle "is also written to an immutable transparency log that is publicly readable on the internet".
- Ecma International, ECMA-424 2nd edition (December 2025), CycloneDX v1.7: <https://ecma-international.org/publications-and-standards/standards/ecma-424/>.
- NTIA, The Minimum Elements For a Software Bill of Materials (2021); CISA, 2025 Minimum Elements for a Software Bill of Materials (public comment draft, August 2025); CISA, Minimum Requirements for VEX (April 2023).
- UI repository: TDD packaging decision record V1–V6 (`docs/designs/TDD-ui-platform-packaging-001-build-and-package-contract.md`), pull requests #34 and #35.
