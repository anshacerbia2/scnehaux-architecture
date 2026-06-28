# Changelog

All notable changes to the Scnehaux Architecture Documentation Governance engine will be documented in this file.

## [1.2.0] - 2026-06-24
### Added
- **Rule Schema Validation (`D-02`)**: Pydantic schema enforcing the exact shape of `linting-rules.yaml` to prevent misconfiguration.
- **Traceability Graph Validations**: Advanced checks for bidirectional traceability (`parent_pad` <-> `fulfilled_by`) and acyclic dependencies.
- **SARIF Support**: New `--format sarif` output mode for integration into GitHub Code Scanning (showing lint warnings inline).
- **Draft Expiry Enforcement (`D-04`)**: Drafts older than `max_draft_age_days` now trigger a CRITICAL blocking error.
- **Cross-Platform Pre-commit Hook (`D-10`)**: `scripts/install-hooks.py` now detects Windows and generates a PowerShell hook or Bash hook accordingly.
- **Container Healthcheck**: `Dockerfile` now runs as a non-root `linteruser` and includes a `HEALTHCHECK`.

### Changed
- **Tech Radar Extraction (`D-01`)**: Extracted and centralized technology hold violation checks into `validators/common.py`.
- **Linter Orchestrator Refactor (`D-08`)**: Eliminated raw `print()` loops in favor of structured `logging`.
- **Test Infrastructure Revamp (`D-03`, `D-09`)**: Eliminated `sys.path.append` hacks, introduced `pyproject.toml`, and created a robust `conftest.py` with `make_validator` to prevent mock bypassing. Achieved 95% test coverage.
- **CI Pipelines (`D-06`)**: Updated GitHub actions with concurrency, python matrix, caching, and `governance_ref` inputs.

## [1.1.0] - 2026-06-15
### Added
- Initial modularization of domain validators (`ADR`, `SAD`, `PAD`, `EAD`, `STD`, `GDC`, `TDD`).
- Governance rules abstracted into `00-governance/rules/linting-rules.yaml`.
- Inline citation validations and ambiguity keyword checks.

## [1.0.0] - 2026-05-10
### Added
- Initial Docs-as-Code linting engine.
