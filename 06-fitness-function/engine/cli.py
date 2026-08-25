"""
Scnehaux Architecture Documentation Linter — Orchestrator
Routes documents to type-specific validators.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import datetime as _dt
import yaml
import jsonschema
from typing import Any, cast
import re
from pathlib import Path
from engine.auditors.dependency_scanner import audit_circular_dependencies
from engine.auditors.git_auditor import audit_version_bump
from engine.auditors.graph_auditor import (
    audit_duplicate_ids,
    audit_hierarchy_tiers,
    audit_orphans,
    audit_traceability_graph,
)
from engine.auditors.waiver_auditor import audit_waiver_expirations
from engine.config.constants import (
    GOVERNANCE_ROOT,
    BASE_SCHEMA_PATH,
    TECH_RADAR_YAML_PATH,
    TECH_RADAR_SCHEMA_PATH,
    SCHEMA_KEY_BLOCKING_SEVERITIES,
    SCHEMA_KEY_STRUCTURE_RULES,
    SCHEMA_KEY_ARTIFACT_DIRS,
    SCHEMA_KEY_IGNORED_FILES,
    SCHEMA_KEY_MAX_DIR_DEPTH,
    SCHEMA_KEY_CONTENT_RULES,
    SCHEMA_KEY_EXEMPT_STATUSES,
    SCHEMA_KEY_EXACT_MATCHES,
)
from engine.config.loader import (
    load_json_schema_file,
    parse_and_validate_global_config,
)
from engine.config.severity import SeverityRule
from engine.fs.crawler import build_metadata_registry, gather_markdown_paths
from engine.parsing.markdown_ast import parse_frontmatter
from engine.reporting.reporter import print_errors, build_sarif
from engine.validators.metadata_rules import validate_exempt_age
from engine.validators.registry import detect_doc_type, get_validator


logger = logging.getLogger(__name__)


def _merge_reference_registry(local_registry, reference_registry):
    """Merge a downstream registry with a read-only architecture reference registry."""
    local_ids, local_metadata, local_duplicates = local_registry
    reference_ids, reference_metadata, reference_duplicates = reference_registry

    duplicates = {**reference_duplicates, **local_duplicates}
    for doc_id in local_ids & reference_ids:
        duplicates[doc_id] = [
            reference_metadata[doc_id].get("_filepath", "reference"),
            local_metadata[doc_id].get("_filepath", "local"),
        ]

    metadata = {**reference_metadata, **local_metadata}
    return local_ids | reference_ids, metadata, duplicates


def _validate_execution_root(cwd: str) -> None:
    """
    Ensure the linter is executed strictly from a repository root.
    Zero-magic rule: If the CWD does not contain a repository marker, crash immediately.
    """
    path = Path(cwd)
    markers = [".git"]
    if not any((path / marker).exists() for marker in markers):
        # We use sys.exit(1) directly so the CLI terminates immediately without python traceback noise
        # This acts as a fatal error that will cancel any CI/CD pipeline PR
        logger.error(
            "FATAL: Linter must be executed from the root of a repository. "
            "No repository marker (.git) was found in the current directory: '%s'",
            cwd,
        )
        sys.exit(1)


def _disable_info(validator: Any) -> dict:
    """
    Capture the state of any `lint_disable` governance directives from the validator.

    This includes rules that the author successfully disabled (along with their justification)
    and CRITICAL rules that the author attempted to disable but were rejected by the engine.

    <pre>Args:
        - validator (Any): The instantiated validator object containing tracked disable directives.

    Returns:
        dict: A dictionary containing 'disabled' (a list of tuples: (rule_id, reason, start_line, end_line))
              and 'rejected' (set of rules that could not be silenced).
    </pre>
    """
    disabled_list = []
    for rule_id, blocks in validator.block_disables.items():
        for start_line, end_line, reason in blocks:
            disabled_list.append((rule_id, reason, start_line, end_line))

    return {
        "disabled": disabled_list,
        "rejected": set(getattr(validator, "rejected_disables", set())),
    }


def lint_file(
    file_path: str,
    global_rules: dict,
    severity_levels: dict,
    blocking_severities: tuple,
    all_doc_ids: set,
    all_doc_metadata: dict,
    output_format: str = "text",
) -> tuple[list[tuple[str, str]], bool, bool, dict]:
    """
    Orchestrate validation for a single markdown file.
    This executes the core lifecycle: Read -> Parse Metadata -> Identify Type -> Validate.

    <pre>Args:
        - file_path (str): The path to the markdown file being linted.
        - global_rules (dict): Global governance schema containing severity configurations.
        - severity_levels (dict): Pre-extracted and validated severity mappings.
        - blocking_severities (tuple): Pre-extracted, immutable tuple of blocking severities.
        - all_doc_ids (set): A set of all known document IDs across the repository.
        - all_doc_metadata (dict): Metadata mapping for cross-reference checks.
        - output_format (str, optional): Desired output format (text, json, sarif). Defaults to "text".

    Returns:
        tuple: (errors, is_clean, has_blocking, disable_info)
            - errors (list): Found violations.
            - is_clean (bool): True if no errors were found.
            - has_blocking (bool): True if blocking violations were detected.
            - disable_info (dict): Captured `lint_disable` directives.
    </pre>
    """
    # @flow-lint: StartLint(("2. Start Document Validation")) --> Read[2.1. Read raw markdown]
    filename = os.path.basename(file_path)

    # Step 1: Read the raw markdown content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        # @flow-lint: Read -->|Exception| RecordErrUnreadable["<code>Record Error</code>: Unreadable Artifact"]
        # @flow-lint: RecordErrUnreadable --> Return
        file_errors, is_clean, is_blocking = print_errors(
            file_path,
            [
                (
                    severity_levels[SeverityRule.UNREADABLE_ARTIFACT],
                    f"Failed to read file: {e}",
                )
            ],
            output_format,
            blocking_severities,
        )
        return file_errors, is_clean, is_blocking, {"disabled": {}, "rejected": set()}

    # Step 2: Parse the YAML Frontmatter to extract document metadata
    # @flow-lint: Read --> ParseFM["2.2. <b>markdown_ast.py - parse_frontmatter()</b>: Extract and parse YAML metadata block"]
    doc_meta, meta_err = parse_frontmatter(content)
    if meta_err:
        # @flow-lint: ParseFM -->|Parse Error| RecordErrFM["<code>Record Error</code>: Corrupt Frontmatter"]
        # @flow-lint: RecordErrFM --> Return
        # Fatal syntax error in frontmatter means we cannot even determine doc type
        file_errors, is_clean, is_blocking = print_errors(
            file_path,
            [(severity_levels[SeverityRule.CORRUPT_FRONTMATTER], meta_err)],
            output_format,
            blocking_severities,
        )
        return file_errors, is_clean, is_blocking, {"disabled": {}, "rejected": set()}

    # @flow-lint: ParseFM -->|Yes| CheckExempt{"2.3. Is document exempt?"}
    # @flow-lint: CheckExempt -->|Yes| ValidateExemptAge["2.4. <b>metadata_rules.py - validate_exempt_age()</b>: Validate exempt duration"]
    # @flow-lint: CheckExempt -->|No| DetectType["2.6. <b>registry.py - detect_doc_type()</b>: Detect document type"]

    # Step 3: Validate exempt status and age
    exempt_statuses_config = global_rules.get(SCHEMA_KEY_CONTENT_RULES, {}).get(
        SCHEMA_KEY_EXEMPT_STATUSES, []
    )
    exempt_statuses = [
        cfg.get("status", "").lower()
        for cfg in exempt_statuses_config
        if isinstance(cfg, dict) and cfg.get("status")
    ]

    # Satisfy static type checkers (Pylance/MyPy) since parse_frontmatter is now guaranteed to return a dict here
    doc_meta = cast(dict, doc_meta)

    doc_status = str(doc_meta.get("status", "")).lower()

    if doc_status in exempt_statuses:
        # Enforce max age limits for exempt statuses
        violation_severity = severity_levels[SeverityRule.DRAFT_STATUS_VIOLATION]
        try:
            exempt_errs = validate_exempt_age(
                doc_meta, doc_status, violation_severity, global_rules
            )
        except ValueError as e:
            logger.error("FATAL: %s", str(e))
            sys.exit(1)

        # @flow-lint: ValidateExemptAge --> IsExemptErr{"2.5. Is Exempt Age Expired?"}
        if exempt_errs:
            # @flow-lint: IsExemptErr -->|Yes| RecordErrExemptAge["<code>Record Error</code>: Exempt Age Violation"]
            # @flow-lint: RecordErrExemptAge --> Return
            # Short-circuit logic for exempt docs (only minimal compliance required)
            file_errors, is_clean, is_blocking = print_errors(
                file_path, exempt_errs, output_format, blocking_severities
            )
            return (
                file_errors,
                is_clean,
                is_blocking,
                {"disabled": {}, "rejected": set()},
            )

        # @flow-lint: IsExemptErr -->|No| RecordInfoExempt["<code>Record Info</code>: Exempt Document Skipped"]
        # @flow-lint: RecordInfoExempt --> Return
        # Record the exemption as an INFO warning so it's tracked in compliance reports, not counted as PASS
        file_errors, is_clean, is_blocking = print_errors(
            file_path,
            [
                (
                    severity_levels[SeverityRule.EXEMPT_DOCUMENT_SKIPPED],
                    f"Document validation skipped due to exempt status: '{doc_status}'",
                )
            ],
            output_format,
            blocking_severities,
        )
        return file_errors, is_clean, is_blocking, {"disabled": {}, "rejected": set()}

    # Step 4: Detect the Document Type (SAD, PAD, ADR, etc.) based on metadata ID
    meta_id = doc_meta.get("id")
    doc_type = detect_doc_type(meta_id, global_rules)
    # @flow-lint: DetectType --> IsDocType{"2.7. Doc type known?"}

    if not doc_type:
        # @flow-lint: IsDocType -->|No| RecordErrDocType["<code>Record Error</code>: Unknown Document Type"]
        # @flow-lint: RecordErrDocType --> Return
        file_errors, is_clean, is_blocking = print_errors(
            file_path,
            [
                (
                    severity_levels[SeverityRule.UNKNOWN_DOCUMENT_TYPE],
                    f"Unknown doc type for '{filename}'. Missing or invalid metadata ID. Hard blocking.",
                )
            ],
            output_format,
            blocking_severities,
        )
        return file_errors, is_clean, is_blocking, {"disabled": {}, "rejected": set()}

    # Step 5: Retrieve the specific domain validator for this document type
    validator_cls = get_validator(doc_type)
    # @flow-lint: IsDocType -->|Yes| GetValidator["2.8. <b>registry.py - get_validator()</b>: Get specific domain validator"]
    # @flow-lint: GetValidator --> IsVal{"2.9. Validator exists?"}
    if not validator_cls:
        # @flow-lint: IsVal -->|No| RecordErrMissingVal["<code>Record Error</code>: Missing Validator"]
        # @flow-lint: RecordErrMissingVal --> Return
        file_errors, is_clean, is_blocking = print_errors(
            file_path,
            [
                (
                    severity_levels[SeverityRule.MISSING_VALIDATOR],
                    f"No validator implemented for doc type '{doc_type}'. Hard blocking.",
                )
            ],
            output_format,
            blocking_severities,
        )
        return file_errors, is_clean, is_blocking, {"disabled": {}, "rejected": set()}

    # Step 6: Load the specific JSON schema for this document type
    domain_schema_path = os.path.join(
        GOVERNANCE_ROOT, "00-governance", "schemas", f"{doc_type.lower()}.schema.json"
    )
    # @flow-lint: IsVal -->|Yes| LoadSchemaType["2.10. <b>loader.py - load_json_schema_file()</b>: Load specific domainJSON schema"]
    # @flow-lint: LoadSchemaType --> IsSchema{"2.11. Schema exists?"}

    try:
        domain_schema = load_json_schema_file(domain_schema_path)
    except (FileNotFoundError, ValueError) as e:
        # @flow-lint: IsSchema -->|No| ExitFailSchema((sys.exit 1))
        logger.error("FATAL: %s", str(e))
        sys.exit(1)

    # Step 7: Initialize the specific validator and execute validation
    # @flow-lint: IsSchema -->|Yes| Execute(("2.12. <b>base.py - validate()</b>: Initialize & Run validator engine"))
    validator = validator_cls(
        file_path,
        content,
        doc_meta or {},
        global_rules,
        domain_schema,
        all_doc_ids,
        all_doc_metadata,
        severity_levels,
        blocking_severities,
    )
    errors = validator.validate()
    # @flow-lint: Execute --> Return[2.13. Return list of errors]

    file_errors, is_clean, is_blocking = print_errors(
        file_path, errors, output_format, blocking_severities
    )
    return file_errors, is_clean, is_blocking, _disable_info(validator)


def main() -> None:
    """
    Main entrypoint for the Linter engine.

    Execution phases:
    1. Parse CLI arguments and configure logging.
    2. Load global governance schemas (`base.schema.json`).
    3. Perform a fast pre-scan of the repository to build a global cross-reference registry
       and detect ID duplicates.
    4. Traverse the file tree and invoke `lint_file` for each valid markdown document.
    5. Execute repository-level audits (e.g., orphan detection, circular dependency checks).
    6. Aggregate results into the requested format (text, json, sarif) and exit with code 1
       if any CRITICAL or ERROR violations are found, else exit 0.

    <pre>Args:
        None (Arguments are parsed directly from sys.argv).

    Returns:
        None

    Raises:
        SystemExit: Code 1 on blocking violations or fatal runtime errors; Code 0 otherwise.
    </pre>
    """
    # Force UTF-8 output regardless of the host console codepage. Windows consoles
    # default to cp1252, which crashes when findings echo unicode (arrows, em-dashes)
    # harvested from document content.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    # @flow: Main(("1. Start CLI<br><b>cli.py - main()</b>")) --> ParseArgs[1.1. Parse CLI arguments]
    # Step 1: Parse CLI Arguments
    parser = argparse.ArgumentParser(description="Scnehaux Architecture Linter")
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--target",
        nargs="+",
        default=["."],
        help="Target directories or files to lint (default: current directory)",
    )
    parser.add_argument(
        "--reference-root",
        help="Optional governance repository root used to resolve cross-repository architecture IDs",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable DEBUG-level logging"
    )

    parser.add_argument(
        "--break-glass",
        action="store_true",
        help="Force exit 0 for Sev-1 incidents (bypasses all blocking errors, triggers audit alert)",
    )
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # @flow: ParseArgs --> LoadGlobal["1.2. <b>loader.py - load_json_schema_file()</b>: Load base schema (global rules)"]
    # @flow: LoadGlobal --> CheckGlobalRules{"Valid global rules?"}
    # @flow: CheckGlobalRules -->|No| ExitFailGlobal((sys.exit 1))
    # Step 2: Load the Global Governance Rules baseline from base schema

    try:
        base_schema = load_json_schema_file(BASE_SCHEMA_PATH)
        # @flow: CheckGlobalRules -->|Yes| IsConfigValid{"Valid Global Config & Severity? </br> <b>loader.py - (validate_global_config_structure, validate_severity_schema, validate_blocking_severities)</b>"}
        # @flow: IsConfigValid -->|No| ExitFailConfig((sys.exit 1))
        global_rules, severity_levels, blocking_severities = (
            parse_and_validate_global_config(base_schema)
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logger.error("FATAL: %s", str(e))
        sys.exit(1)

    std_dirs = global_rules.get(SCHEMA_KEY_STRUCTURE_RULES, {}).get(
        SCHEMA_KEY_ARTIFACT_DIRS, {}
    )
    allowed_root_dirs = set(std_dirs.values()) if std_dirs else None

    ignored_config = global_rules.get(SCHEMA_KEY_STRUCTURE_RULES, {}).get(
        SCHEMA_KEY_IGNORED_FILES, {}
    )
    if ignored_config:
        ignored_files_lower = {
            f.lower() for f in ignored_config.get(SCHEMA_KEY_EXACT_MATCHES, [])
        }
        ignored_patterns = [
            re.compile(p, re.IGNORECASE) for p in ignored_config.get("patterns", [])
        ]
    else:
        ignored_files_lower = set()
        ignored_patterns = []

    max_dir_depth = global_rules.get(SCHEMA_KEY_STRUCTURE_RULES, {}).get(
        SCHEMA_KEY_MAX_DIR_DEPTH, 3
    )

    # Validate that the Current Working Directory (CWD) is a valid repository root
    cwd = os.getcwd()
    # @flow: IsConfigValid -->|Yes| CheckCwd["1.3. <b>_validate_execution_root()</b>: Valid CWD?"]
    # @flow: CheckCwd -->|No| ExitFailCwd((sys.exit 1))
    _validate_execution_root(cwd)

    # @flow: CheckCwd -->|Yes| PreScan[["1.4. <b>crawler.py - build_metadata_registry()</b>: Collect Document Metadata from all files & validate unique IDs"]]
    # @flow: PreScan -->|executes| StartRegistry
    # @flow: StartRegistry(("Start")) --> GatherDocs["<b>crawler.py - gather_markdown_paths()</b>: Enforce boundary & collect markdown paths within governed boundaries"]
    # @flow: GatherDocs -->|File Error: Outside Repo / Unauthorized / Cross-Drive| ExitFailPreScan((sys.exit 1))
    # @flow: GatherDocs -->|Valid File Path| CheckRegIgnore{"Is Ignored File?"}
    # @flow: CheckRegIgnore -->|"Yes (Skip)"| GatherDocs
    # @flow: CheckRegIgnore -->|"No (Keep)"| LoopRegFile{"Iterate file paths to build Registry"}
    # @flow: LoopRegFile -->|Valid Markdown| ParseYamlReg["<b>markdown_ast.py - parse_frontmatter()</b>: Extract and parse YAML metadata block"]
    # @flow: ParseYamlReg -->|Parse Error| LoopRegFile
    # @flow: ParseYamlReg -->|Success| CheckDups{"Is Document ID already registered?"}
    # @flow: CheckDups -->|Yes| RecordDup["Store Duplicate in Registry"]
    # @flow: CheckDups -->|No| RecordReg["Store Metadata in Registry"]
    # @flow: RecordDup --> LoopRegFile
    # @flow: RecordReg --> LoopRegFile
    # @flow: LoopRegFile -->|Done Iterating| ReturnRegistry[Return Metadata Registry and Duplicate Records]
    # Step 3: Pre-scan the ENTIRE repository to collect `doc_meta` (YAML frontmatter) from all Markdown files.
    # This builds a globally complete metadata registry used for cross-reference resolution,
    # and strictly validates that every Architecture ID is unique (detects and prevents duplicates).
    # CRITICAL: We scan the repository root (TARGET_REPO_ROOT) unconditionally to ensure no file is missed.

    # TARGET_REPO_ROOT is strictly defined by the CWD. No magic tree climbing, no arguments.
    TARGET_REPO_ROOT = cwd

    try:
        local_registry = build_metadata_registry(
            TARGET_REPO_ROOT,
            TARGET_REPO_ROOT,
            allowed_root_dirs,
            ignored_files_lower,
            ignored_patterns,
        )
        local_doc_ids, local_doc_metadata, duplicate_ids = local_registry
        all_doc_ids, all_doc_metadata = local_doc_ids, local_doc_metadata

        if args.reference_root:
            reference_root = os.path.abspath(args.reference_root)
            _validate_execution_root(reference_root)
            reference_registry = build_metadata_registry(
                reference_root,
                reference_root,
                allowed_root_dirs,
                ignored_files_lower,
                ignored_patterns,
            )
            all_doc_ids, all_doc_metadata, duplicate_ids = _merge_reference_registry(
                local_registry, reference_registry
            )
    except ValueError as e:
        logger.error("FATAL: %s", str(e))
        sys.exit(1)

    has_blocking_errors = False
    results: list[dict] = []
    disabled_usages: dict[str, dict] = {}
    undocumented_disables: dict[str, list] = {}
    rejected_usages: dict[str, list] = {}
    total_files = 0
    pass_count = 0
    warning_count = 0
    fail_count = 0

    if args.format == "text":
        print("Starting Modular Architecture Artifact Audit (linter)...\n")

    # @flow: ReturnRegistry --> ValidateTechRadar["1.5. <b>jsonschema.validate()</b>: Validate Tech Radar data against its JSON Schema"]
    # Phase: Independent YAML Validation
    # Strictly validates the parsed `tech-radar.yaml` data structure against `tech-radar.schema.json`.
    # This happens prior to the main Markdown linting loop.
    if os.path.exists(TECH_RADAR_YAML_PATH) and os.path.exists(TECH_RADAR_SCHEMA_PATH):
        try:
            with open(TECH_RADAR_YAML_PATH, "r", encoding="utf-8") as f:
                radar_data = yaml.safe_load(f)
            with open(TECH_RADAR_SCHEMA_PATH, "r", encoding="utf-8") as f:
                radar_schema = json.load(f)
            jsonschema.validate(instance=radar_data, schema=radar_schema)
            if args.format == "text":
                print(f"INFO: [PASS] {TECH_RADAR_YAML_PATH}")
            pass_count += 1
            total_files += 1
        except Exception as e:
            # @flow: ValidateTechRadar -->|Validation Error| RecordErrRadar["<code>Record Error</code>: Tech Radar Schema Violation"]
            # @flow: RecordErrRadar --> FindTarget
            # Resolve severity dynamically from global schema
            severity = severity_levels[SeverityRule.STRUCTURAL_INTEGRITY_VIOLATION]
            err_msg = (
                str(e).split("\n")[0]
                if isinstance(e, jsonschema.exceptions.ValidationError)
                else str(e)
            )

            radar_errors = [(severity, f"Schema validation failed: {err_msg}")]
            radar_has_blocking = False

            _, _, has_blocking = print_errors(
                TECH_RADAR_YAML_PATH,
                radar_errors,
                args.format,
                tuple(global_rules[SCHEMA_KEY_BLOCKING_SEVERITIES]),
            )
            if has_blocking:
                radar_has_blocking = True

            if args.format in ("json", "sarif"):
                results.append(
                    {
                        "file": TECH_RADAR_YAML_PATH,
                        "errors": radar_errors,
                    }
                )

            if radar_has_blocking:
                has_blocking_errors = True
                fail_count += 1
            else:
                pass_count += 1

            total_files += 1

    # @flow: ValidateTechRadar --> FindTarget["1.6. <b>crawler.py - gather_markdown_paths()</b>: Gather markdown paths from CLI target arguments"]
    try:
        files_to_lint = gather_markdown_paths(
            args.target,
            TARGET_REPO_ROOT,
            allowed_root_dirs,
            ignored_files_lower,
            ignored_patterns,
        )
    except ValueError as e:
        # @flow: FindTarget -->|File Error: Outside Repo / Unauthorized / Cross-Drive| ExitFailFindTarget((sys.exit 1))
        logger.error("FATAL: %s", str(e))
        sys.exit(1)

    # @flow: FindTarget --> |Valid File Path| CheckFilter{"Is ignored file?"}
    # @flow: CheckFilter -->|"Yes (Skip)"| FindTarget
    # @flow: CheckFilter -->|"No (Keep)"| LoopFile{"1.7. Iterate file paths"}
    for full_path in files_to_lint:
        # @flow: LoopFile --> CheckDepth{"Exceeds maximum directory depth?"}
        # @flow: CheckDepth -->|Yes| RecordDepthError["<code>Record Error</code>: Directory Depth Violation"]
        # @flow: RecordDepthError --> LoopFile
        # Rule: Enforce Max Directory Depth
        try:
            rel_path_os = os.path.relpath(full_path, ".")
            parts = [p for p in rel_path_os.split(os.sep) if p and p != "."]
            if len(parts) > max_dir_depth:
                err_msg = f"Directory depth violation: {len(parts)} levels deep (Max is {max_dir_depth}). Flatten the folder structure."
                severity = severity_levels[SeverityRule.STRUCTURAL_INTEGRITY_VIOLATION]
                depth_errors = [(severity, err_msg)]
                _, _, is_blocking = print_errors(
                    full_path,
                    depth_errors,
                    args.format,
                    tuple(global_rules[SCHEMA_KEY_BLOCKING_SEVERITIES]),
                )

                if is_blocking:
                    has_blocking_errors = True
                    fail_count += 1
                else:
                    pass_count += 1

                total_files += 1

                if args.format in ("json", "sarif"):
                    results.append({"file": full_path, "errors": depth_errors})
                continue
        except ValueError:
            # Dead code: fs/crawler.py already strictly blocks cross-drive paths with sys.exit(1).
            # This ValueError will mathematically never be triggered here.
            pass

        # @flow: CheckDepth -->|No| LintFileSub[["1.8. <b>lint_file()</b>: Validate markdown document against base schema and specific domain schema"]]
        # @flow: LintFileSub -->|executes| StartLinting(("Start Linting"))
        # Execute linting for the current valid file
        file_errors, is_clean, is_blocking, disable_info = lint_file(
            full_path,
            global_rules,
            severity_levels,
            blocking_severities,
            all_doc_ids,
            all_doc_metadata,
            args.format,
        )
        # @flow: LintFileSub --> LoopFile

        # Track lint_disable governance
        disabled = disable_info.get("disabled", [])
        if disabled:
            disabled_usages[full_path] = disabled
            undoc = [r for r, reason, _, _ in disabled if not reason]
            if undoc:
                undocumented_disables[full_path] = undoc
        rejected = disable_info.get("rejected", set())
        if rejected:
            rejected_usages[full_path] = sorted(rejected)

        # Track statistics
        total_files += 1
        if is_blocking:
            fail_count += 1
        elif not is_clean:
            warning_count += 1
        else:
            pass_count += 1

        if file_errors and args.format != "text":
            results.append({"file": full_path, "errors": list(file_errors)})

        # If any file fails with a CRITICAL or ERROR, mark the entire CI job as failed
        if is_blocking:
            has_blocking_errors = True

    # @flow: LoopFile -->|Done Iterating| RepoAudit["1.9. <b>audit_*()</b>: Run repository-level audits"]
    # Step 4: Repo-level audits (only meaningful across the full registry)
    repo_findings: list[tuple[str, str, str]] = []
    repo_findings.extend(audit_duplicate_ids(duplicate_ids, severity_levels))
    repo_findings.extend(audit_hierarchy_tiers(local_doc_metadata, severity_levels))
    repo_findings.extend(audit_orphans(local_doc_metadata, severity_levels))
    repo_findings.extend(audit_version_bump(local_doc_metadata, severity_levels))

    for fpath, sev, msg in audit_waiver_expirations(
        local_doc_metadata, severity_levels
    ):
        repo_findings.append((sev, msg, fpath))

    for fpath, sev, msg in audit_circular_dependencies(
        local_doc_metadata, severity_levels
    ):
        repo_findings.append((sev, msg, fpath))

    for category, msg in audit_traceability_graph(local_doc_metadata):
        repo_findings.append((severity_levels[category], msg, "TRACEABILITY-GRAPH"))

    for sev, msg, pfile in repo_findings:
        if sev in blocking_severities:
            has_blocking_errors = True
            fail_count += 1
        else:
            warning_count += 1
        if args.format == "text":
            status = "[FAIL]" if sev in blocking_severities else "[WARNING]"
            print(f"\n{status} {pfile}\n  - [{sev}] {msg}")
        else:
            results.append({"file": pfile, "errors": [(sev, msg)]})

    # @flow: RepoAudit --> Reporter["1.10. <b>build_sarif()</b>: Generate output format (SARIF/JSON/Text)"]
    # Step 5: Final output generation and CI/CD Exit Code enforcement
    if args.format == "sarif":
        print(json.dumps(build_sarif(results, blocking_severities), indent=2))
        sys.exit(1 if has_blocking_errors else 0)

    if args.format == "json":
        json_output = [
            {
                "file": r["file"],
                "errors": [{"severity": s, "message": m} for s, m in r["errors"]],
            }
            for r in results
        ]
        print(json.dumps(json_output, indent=2))
        sys.exit(1 if has_blocking_errors else 0)

    # Print summary statistics
    print("\n--- Audit Summary ---")
    print(f"  Total files scanned: {total_files}")
    print(f"  Passed:   {pass_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Failed:   {fail_count}")

    if disabled_usages:
        print("\n--- Lint Disable Usage ---")
        for fpath, disabled_list in disabled_usages.items():
            rendered = ", ".join(
                f"{r} [L{start}-{end if end != float('inf') else 'EOF'}] (reason: {reason})"
                if reason
                else f"{r} [L{start}-{end if end != float('inf') else 'EOF'}] (UNDOCUMENTED)"
                for r, reason, start, end in disabled_list
            )
            print(f"  {fpath}: {rendered}")

    if rejected_usages:
        print("\n--- Rejected Disables (CRITICAL findings cannot be silenced) ---")
        for fpath, rules in rejected_usages.items():
            print(
                f"  {fpath}: {', '.join(rules)} -> directive ignored; finding still enforced"
            )

    # @flow: Reporter --> HasBlockErr{"1.11. Has blocking errors?"}
    if has_blocking_errors:
        if args.break_glass:
            print(
                f"\n[CRITICAL WARNING] Audit failed with {fail_count} blocking error(s), but --break-glass was used."
            )
            print(
                "ALERT: Bypassing CI/CD block for Sev-1 incident. This action is being logged and reported to the Architecture Authority."
            )

            # --- Break-Glass Audit Trail (C3 fix) ---
            # Write a persistent, structured audit event so the claim above is truthful.
            _invoker = (
                os.environ.get("GITHUB_ACTOR")
                or os.environ.get("USER")
                or os.environ.get("USERNAME")
                or "unknown"
            )
            try:
                _invoker = (
                    subprocess.check_output(
                        ["git", "config", "user.email"],
                        text=True,
                        stderr=subprocess.DEVNULL,
                    ).strip()
                    or _invoker
                )
            except Exception:
                pass

            _audit_event = {
                "event": "break-glass-bypass",
                "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                "invoker": _invoker,
                "blocking_errors": fail_count,
                "ci_run": os.environ.get("GITHUB_RUN_ID", "local"),
                "ref": os.environ.get("GITHUB_REF", "unknown"),
            }

            _audit_path = os.path.join(cwd, "break-glass-audit.log")
            try:
                with open(_audit_path, "a", encoding="utf-8") as _af:
                    _af.write(json.dumps(_audit_event) + "\n")
                logger.warning("Break-glass audit event written to %s", _audit_path)
            except Exception as _write_err:
                logger.error("Failed to write break-glass audit log: %s", _write_err)
            # --- End Audit Trail ---

            # @flow: HasBlockErr -->|Break Glass| ExitSuccess((sys.exit 0))
            sys.exit(0)
        else:
            print(f"\n[FAIL] Audit failed with {fail_count} blocking error(s).")
            # @flow: HasBlockErr -->|Yes| ExitFail((sys.exit 1))
            sys.exit(1)  # Triggers a hard block in CI/CD pipelines
    else:
        print("\nAll checks passed! Documentation is Governance-Compliant.")
        # @flow: HasBlockErr -->|No| ExitSuccess((sys.exit 0))
        sys.exit(0)  # Triggers a successful pass in CI/CD pipelines


if __name__ == "__main__":
    main()
