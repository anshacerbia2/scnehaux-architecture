# Contributing to Scnehaux Architecture

Welcome to the Scnehaux Architecture repository. This repo defines the governance, standards, and strategic directions for our entire engineering organization.

As a **Principal Architect / Consulting Engineer** contributing to this repository, you must adhere to the highest standard of engineering rigor.

## Core Philosophy: Zero Waste & Determinism
Every document, rule, and standard here exists to prevent entropy. We enforce a deterministic architecture:
1. **Predictability over Cleverness**: Architecture must be predictable. No implicit behaviors.
2. **Explicit Contracts**: Interfaces and boundaries must be explicit.
3. **Zero Waste**: Remove redundancy in documentation and design.

## How to Contribute

1. **Identify the Document Type**:
   - `ADR`: For recording a significant architecture decision.
   - `PAD`: For defining a domain platform capability.
   - `SAD`: For defining a specific system's architecture.
   - `STD`: For defining a mandatory engineering standard.

2. **Run the Linter Locally**:
   Before submitting a Pull Request, you MUST pass the local governance linter.
   ```bash
   python linter.py
   ```
   The linter will statically analyze your Markdown to ensure:
   - Mandatory sections are present.
   - Vague terminology ("fast", "highly scalable") is eliminated.
   - Metadata and referential links are valid.

3. **Peer Review**:
   - Submit your PR.
   - Await review from the Architecture Review Board (ARB) using the `review-score-sheet-template.md`.
   - Resolve all blocker feedback before merging.

## Modifying the Governance Rules

If you need to update the rules of the linter itself:
1. Edit `00-governance/linting-rules.yaml`.
2. Ensure you have tested the rules against existing documentation to avoid breaking the CI build.
3. For core logic changes, modify the appropriate module inside the `validators/` directory.

> **Exception Protocol**: If you must deviate from a paved road, you must submit an ADR explaining the rationale, the risk mitigation, and receive explicit approval from the ARB.
