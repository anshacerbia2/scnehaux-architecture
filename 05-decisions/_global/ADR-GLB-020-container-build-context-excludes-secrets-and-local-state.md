---
doc_meta:
  id: ADR-GLB-020
  title: ADR-GLB-020 A Container Build Context Excludes Secrets, Key Material and Local State
  adr_type: foundational
  status: accepted
  created: 2026-10-21
  created_date: 2026-10-21
  created_by: Architecture Authority
  governed_by:
    - GDC-000
  authorizes: [STD-GLB-009]
---

# ADR-GLB-020: A Container Build Context Excludes Secrets, Key Material and Local State

## 1. Title

A container build context excludes secrets, key material and local state.

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver               |
| :--------- | :------- | :----------- | :------------------------ | :--------------------- |
| 2026-10-21 | accepted | foundational | Architecture Review Board | Architecture Authority |

GDC-005 makes a governance artifact accepted when it is reviewed and merged by pull request. The owner's merge of the pull request that adds this decision is that act.

## 3. Context

`STD-GLB-009` §Container Images governs how every Scnehaux image is built, pinned, scanned and excepted. It says nothing about what the builder may read. A build that runs `COPY . .` copies everything in its context into a layer, and a layer is part of the image.

Facts that bound the choice:

- **The context is everything the build can read.** Docker: "The build context is the set of files that your build can access", and "Build instructions such as COPY and ADD can refer to any of the files and directories in the context" [R1].
- **A `.dockerignore` file takes paths out of the context.** "If this file exists, the files and directories that match patterns in the files are removed from the build context before it's sent to the builder" [R1].
- **Docker says a secret in a build argument or environment variable persists.** "Build arguments and environment variables are inappropriate for passing secrets to your build, because they persist in the final image" [R2]. Docker says this of those two channels. A secret file copied into a layer persists in the same way; that is this decision's inference, not Docker's words.
- **The estate's workspaces hold material a build must never see.** deploy-dev checks sibling repositories out into the workspace (`.kernel/`, `.identity/`, `.experience/`). The kernel's checkout holds its realm signing keystore, and every stack keeps key rings in `keys/` directories and local values in `.env` files.
- **Two repositories already do this.** identity-control and organization-control carry a `.dockerignore` that excludes `.kernel/`, `keys/`, `.env`, `*.pem` and `.git`. identity-kernel builds images and has none.

## 4. Decision Drivers

- A key or a token must not reach a layer, a registry or a scan report by accident.
- The rule must be checkable by a file's presence and content.
- It must cost a repository one file and no change to how it builds.
- Where a source is silent, the conservative option wins.

## 5. Decision

### 5.1 Every Image Build Has a `.dockerignore`, and It Excludes Three Kinds of Path

`STD-GLB-009` §Container Images rule 12 requires it as a MUST. The file sits in the root of the build context and excludes:

- **Secrets and key material:** `.env` and `**/.env`, every `keys/` directory, `*.pem` and `**/*.pem`, a Compose override that holds a server's values, a local token file, and any other file that holds a credential.
- **Local state:** sibling checkouts a workflow places in the workspace, a proof's or the image scan's working directory, coverage, test and build output, and local databases and volumes.
- **Version control and CI metadata:** `.git` and `.github`.

Docker's documents do not name `.git`, local state or CI metadata. They are excluded as the conservative choice: the history in `.git` holds every earlier version of every file, including any a secret was once committed in, and a build reads none of the three.

### 5.2 It Is Not the Way to Pass a Secret to a Build

A build that needs a secret uses a secret mount or an SSH mount, which "expose secrets to your builds securely" [R2]. The `.dockerignore` only keeps unrelated secrets out of the context.

### 5.3 A Repository MAY Use an Allow-List

A repository may exclude everything with `*` and re-include only what its build reads. It MUST still list the three kinds above where its file does not exclude them by that means.

### 5.4 CI Checks It

`STD-GLB-009` §5 item 9: CI fails when the file is missing, or when a path of one of the three kinds is not matched by it.

## 6. Consequences

### Positive

- A secret, a key ring or a sibling checkout cannot reach a layer through a broad `COPY`.
- A build cannot fail because the builder cannot read a file only its owner may read.
- The rule is one file and one CI check per repository.

### Negative

- A repository without the file, such as identity-kernel, adds it, and its CI gains a check.
- A pattern list can miss a new kind of local file; the allow-list form in §5.3 closes that for a repository that chooses it.

### Operational

- `STD-GLB-009` states the rule and its check. Each repository's ROADMAP records its own `.dockerignore`.

## 7. Compliance Impact

### Related Standards

- `STD-GLB-009` 3.0.0, §Container Images rule 12 and §5 item 9, which this decision authorizes.
- [ADR-IAM-002](../identity-access-platform/ADR-IAM-002-token-signing.md): authorizes the 2.0.0 revision of the same standard, for a different rule.

### Compliance Status

identity-control and organization-control comply. identity-kernel does not yet: it builds images and has no `.dockerignore`, tracked as an identity-kernel ROADMAP item. No production exists (`SAD-001` §9.1 and `SAD-004` §10.3 record the development server alone).

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A — Rule 12 as a SHOULD

**Benefits:** no repository fails CI on adoption.

**Rejected because:** a rule that may be skipped is skipped by exactly the repository whose workspace holds a keystore. The check in §5.4 could not fail a build, and the harm, a key in a layer, is not undone by a later fix: the image and its registry copies stay.

### Alternative B — No rule: rely on scanning and on not copying secrets

**Benefits:** nothing new to maintain.

**Rejected because:** the scan of `STD-GLB-009` rule 3 finds vulnerable packages, and a secret scanner finds a secret only after it is in an image. OWASP lists tools "to detect secrets in images" [R3], which is detection after the fact, and its rule is to use Docker secrets so as to avoid "the exposure of sensitive data in container images or in runtime commands" [R3]. Neither stops a file entering a layer.

### Alternative C — Pass every secret through Docker secrets and ignore the context

**Benefits:** follows OWASP's rule exactly.

**Rejected because:** it covers a secret the build needs, not a file the build never asked for. A key ring in the context is copied by `COPY . .` whether or not any secret mount exists. §5.2 keeps this rule and adds the exclusion.

## 9. References

### Informative

- **[R1]** Docker, _Build context_, §What is a build context? and §.dockerignore files, accessed 2026-10-21. <https://docs.docker.com/build/concepts/context/>. "The build context is the set of files that your build can access."; "Build instructions such as COPY and ADD can refer to any of the files and directories in the context."; "You can use a .dockerignore file to exclude files or directories from the build context."; "If this file exists, the files and directories that match patterns in the files are removed from the build context before it's sent to the builder."
- **[R2]** Docker, _Build secrets_, accessed 2026-10-21. <https://docs.docker.com/build/building/secrets/>. "A build secret is any piece of sensitive information, such as a password or API token, consumed as part of your application's build process."; "Build arguments and environment variables are inappropriate for passing secrets to your build, because they persist in the final image. Instead, you should use secret mounts or SSH mounts, which expose secrets to your builds securely."
- **[R3]** OWASP, _Docker Security Cheat Sheet_, §RULE #12 - Utilize Docker Secrets for Sensitive Data Management and §Container scanning, accessed 2026-10-21. <https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html>. "Using Docker Secrets helps in avoiding the exposure of sensitive data in container images or in runtime commands."; "To detect secrets in images: ggshield (open source and free option available) Gitleaks (open source) TruffleHog (open source)". The cheat sheet does not mention `.dockerignore`. The CIS Docker Benchmark is not cited: it was not fetched.
