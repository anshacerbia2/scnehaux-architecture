"""
Scnehaux Architecture Documentation Linter — Orchestrator
Routes documents to type-specific validators.
"""

import os
import sys
import json
import logging
import argparse
import yaml
import jsonschema
from typing import Any
from engine.validators.registry import detect_doc_type, get_validator
from engine.fs.crawler import resolve_registry_with_duplicates
from engine.auditors.graph_auditor import (
    audit_traceability_graph,
    audit_duplicate_ids,
    audit_hierarchy_tiers,
    audit_orphans,
)
from engine.auditors.git_auditor import audit_version_bump
from engine.validators.global_rules import validate_draft_status
from engine.config.loader import load_schema
from engine.reporting.reporter import print_errors, build_sarif
from engine.parsing.markdown_ast import parse_frontmatter

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

logger = logging.getLogger(__name__)


def _disable_info(validator: Any) -> dict:
    """
    Capture the state of any `lint_disable` governance directives from the validator.

    This includes rules that the author successfully disabled (along with their justification)
    and CRITICAL rules that the author attempted to disable but were rejected by the engine.

    Returns:
        dict: A dictionary containing 'disabled' (mapping rule -> reason) and
              'rejected' (set of rules that could not be silenced).
    """
    return {
        "disabled": {
            r: validator.disable_reasons.get(r) for r in validator.disabled_rules
        },
        "rejected": set(getattr(validator, "rejected_disables", set())),
    }


def lint_file(
    file_path: str,
    global_rules: dict,
    all_doc_ids: set,
    all_doc_metadata: dict,
    output_format: str = "text",
) -> tuple[list[tuple[str, str]], bool, bool, dict]:
    """
    Orchestrate validation for a single markdown file.
    This executes the core lifecycle: Read -> Parse Metadata -> Identify Type -> Validate.
    Returns (errors, is_clean, has_blocking, disable_info).

    # @flow: StartLint((Start lint_file)) --> Read[Read raw markdown]
    """
    try:
        rel_path = os.path.relpath(file_path, ".").replace("\\", "/")
    except ValueError:
        # Occurs on Windows if file_path and CWD are on different drives (e.g. C: vs D: in pytest temp dirs)
        rel_path = file_path.replace("\\", "/")
    filename = os.path.basename(file_path)

    # Step 1: Read the raw markdown content
    # @flow: Read --> ParseFM["<b>parse_frontmatter()</b>: Extract frontmatter metadata"]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errs, p, b = print_errors(
            file_path, [("ERROR", f"Failed to read file: {e}")], output_format
        )
        return errs, p, b, {}

    # Step 2: Parse the YAML Frontmatter to extract document metadata
    # @flow: ParseFM --> IsFMErr{"Frontmatter Parse Error?"}
    doc_meta, meta_err = parse_frontmatter(content)
    if meta_err:
        # @flow: IsFMErr -->|Yes| PrintErrFM["<b>print_errors()</b>: Hard block"]
        # @flow: PrintErrFM --> Return
        # Any failure in parsing the frontmatter is a critical block
        errs, p, b = print_errors(file_path, [("ERROR", meta_err)], output_format)
        return errs, p, b, {}

    # @flow: IsFMErr -->|No| CheckDraft{"Is status Draft?"}
    # @flow: CheckDraft -->|Yes| ValidasiDraft["<b>validate_draft_status()</b>: Validate draft duration"]
    # @flow: CheckDraft -->|No| DetectType["<b>detect_doc_type()</b>: Detect document type"]
    if doc_meta and str(doc_meta.get("status", "")).lower() == "draft":
        # Enforce max_draft_age_days even for skipped drafts
        draft_errs = validate_draft_status(doc_meta, global_rules)

        if draft_errs:
            errs, p, b = print_errors(file_path, draft_errs, output_format)
            return errs, p, b, {}

        if output_format == "text":
            logger.info("[SKIP] %s (status: draft — exempt from scoring)", file_path)
        return [], True, False, {}

    # Step 3: Detect the Document Type (SAD, PAD, ADR, etc.) based on ID or filename
    doc_id = doc_meta.get("id") if doc_meta else None
    doc_type = detect_doc_type(doc_id, filename, rel_path)
    # @flow: DetectType --> IsDocType{"Doc type known?"}

    if not doc_type:
        # @flow: IsDocType -->|No| PrintErrDoc["<b>print_errors()</b>: Hard block"]
        # @flow: PrintErrDoc --> Return
        errs, p, b = print_errors(
            file_path,
            [
                (
                    "ERROR",
                    f"Unknown doc type for '{filename}'. Missing or invalid metadata ID. Hard blocking.",
                )
            ],
            output_format,
        )
        return errs, p, b, {}

    # Step 4: Retrieve the specific validator class for this document type
    validator_cls = get_validator(doc_type)
    # @flow: IsDocType -->|Yes| GetValidator["<b>get_validator()</b>: Get specific validator class"]
    # @flow: GetValidator --> IsVal{"Validator exists?"}
    if not validator_cls:
        # @flow: IsVal -->|No| PrintErrVal["<b>print_errors()</b>: Hard block"]
        # @flow: PrintErrVal --> Return
        errs, p, b = print_errors(
            file_path,
            [
                (
                    "ERROR",
                    f"No validator implemented for doc type '{doc_type}'. Hard blocking.",
                )
            ],
            output_format,
        )
        return errs, p, b, {}

    # Step 5: Load the specific JSON schema for this document type
    specific_schema_path = os.path.join(
        SCRIPT_DIR, f"00-governance/schemas/{doc_type.lower()}.schema.json"
    )
    # @flow: IsVal -->|Yes| LoadSchemaType["<b>load_schema()</b>: Load specific JSON schema"]
    # @flow: LoadSchemaType --> IsSchema{"Schema exists?"}

    if not os.path.exists(specific_schema_path):
        # @flow: IsSchema -->|No| PrintErrSchema["<b>print_errors()</b>: Hard block"]
        # @flow: PrintErrSchema --> Return
        errs, p, b = print_errors(
            file_path,
            [
                (
                    "ERROR",
                    f"Missing mandatory domain-specific schema: '{specific_schema_path}'. Hard blocking.",
                )
            ],
            output_format,
        )
        return errs, p, b, {}

    specific_schema = load_schema(specific_schema_path)

    # Step 6: Initialize the specific validator and execute validation
    # @flow: IsSchema -->|Yes| Execute["<b>validator.validate()</b>: Initialize & Run validator engine"]
    validator = validator_cls(
        file_path,
        content,
        doc_meta or {},
        global_rules,
        specific_schema,
        all_doc_ids,
        all_doc_metadata,
    )
    errors = validator.validate()
    # @flow: Execute --> Return[Return list of errors]

    errs, p, b = print_errors(file_path, errors, output_format)
    return errs, p, b, _disable_info(validator)


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
    """
    # Force UTF-8 output regardless of the host console codepage. Windows consoles
    # default to cp1252, which crashes when findings echo unicode (arrows, em-dashes)
    # harvested from document content.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    # @flow: Main((Start CLI)) --> ParseArgs[Parse CLI arguments]
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
        "--verbose", action="store_true", help="Enable DEBUG-level logging"
    )
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # @flow: ParseArgs --> LoadGlobal["<b>load_schema()</b>: Load base schema & global rules"]
    # Step 2: Load the Global Governance Rules baseline from base schema
    base_schema_path = os.path.join(
        SCRIPT_DIR, "00-governance/schemas/base.schema.json"
    )
    base_schema = load_schema(base_schema_path)
    global_rules = base_schema.get("x-engine-config", {})

    severity_levels = global_rules.get("severity_levels", {})

    # @flow: LoadGlobal --> PreScan["<b>resolve_registry_with_duplicates()</b>: Build registry & cross-reference IDs"]
    # Step 3: Pre-scan all files to build the registry of doc IDs (cross-reference) and detect duplicates.
    all_doc_ids, all_doc_metadata, duplicate_ids = resolve_registry_with_duplicates(".")

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
        print("Starting Modular Architecture Documentation Audit (linter)...\n")
        
    # --- Tech Radar Validation Phase ---
    tech_radar_yaml = os.path.join(SCRIPT_DIR, "01-enterprise/tech-radar.yaml")
    tech_radar_schema = os.path.join(SCRIPT_DIR, "00-governance/schemas/tech-radar.schema.json")
    if os.path.exists(tech_radar_yaml) and os.path.exists(tech_radar_schema):
        try:
            with open(tech_radar_yaml, "r", encoding="utf-8") as f:
                radar_data = yaml.safe_load(f)
            with open(tech_radar_schema, "r", encoding="utf-8") as f:
                radar_schema = json.load(f)
            jsonschema.validate(instance=radar_data, schema=radar_schema)
            if args.format == "text":
                print(f"INFO: [PASS] {tech_radar_yaml}")
            pass_count += 1
            total_files += 1
        except Exception as e:
            has_blocking_errors = True
            fail_count += 1
            total_files += 1
            err_msg = str(e).split("\n")[0] if isinstance(e, jsonschema.exceptions.ValidationError) else str(e)
            if args.format == "text":
                print(f"[FAIL] {tech_radar_yaml}\n  - [ERROR] Schema validation failed: {err_msg}\n")
            results.append({"file": tech_radar_yaml, "errors": [("ERROR", f"Schema validation failed: {err_msg}")]})
    # -----------------------------------

    # @flow: PreScan --> FindTarget[Find target markdown files]
    files_to_lint: list[str] = []
    for target in args.target:
        if os.path.isfile(target):
            files_to_lint.append(target)
        else:
            for root, dirs, files in os.walk(target):
                # Exclude irrelevant directories to improve performance and prevent false positives
                dirs[:] = [
                    d
                    for d in dirs
                    if d
                    not in (
                        ".git",
                        "node_modules",
                        "__pycache__",
                        ".vscode",
                        "validators",
                    )
                ]
                for file in files:
                    files_to_lint.append(os.path.join(root, file))

    # @flow: FindTarget --> LoopFile{"Iterate per file"}
    for full_path in files_to_lint:
        # Filter 1: Only audit Markdown files
        if not full_path.lower().endswith(".md"):
            continue

        filename = os.path.basename(full_path)
        # Filter 2: Ignore root standard files like README, CHANGELOG, or index
        if filename.lower() in (
            "readme.md",
            "index.md",
            "contributing.md",
            "changelog.md",
            "maturity.md",
            "temp.md",
            "scnehaux_enterprise_architecture_refinement.md",
        ):
            continue

        # Filter 3: Ignore template and copy files (these are blueprints, not actual documentation)
        if full_path.lower().endswith(".copy.md"):
            continue
        if (
            full_path.lower().endswith(".template.md")
            or full_path.lower().endswith("-template.md")
            or "templates" in os.path.basename(os.path.dirname(full_path)).lower()
        ):
            continue

        # @flow: LoopFile -->|Valid Markdown| LintFileSub[["<b>lint_file()</b>: Validate 1 markdown document"]]
        # @flow: LintFileSub -.->|executes| StartLint
        # Execute linting for the current valid file
        file_errors, is_clean, is_blocking, disable_info = lint_file(
            full_path, global_rules, all_doc_ids, all_doc_metadata, args.format
        )
        # @flow: LintFileSub --> LoopFile

        # Track lint_disable governance
        disabled = disable_info.get("disabled", {})
        if disabled:
            disabled_usages[full_path] = disabled
            undoc = [r for r, reason in disabled.items() if not reason]
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

        if file_errors:
            results.append({"file": full_path, "errors": list(file_errors)})

        # If any file fails with a CRITICAL or ERROR, mark the entire CI job as failed
        if is_blocking:
            has_blocking_errors = True

    # @flow: LoopFile -->|Done Iterating| RepoAudit["<b>audit_*()</b>: Run repository-level audits"]
    # Step 4: Repo-level audits (only meaningful across the full registry)
    repo_findings: list[tuple[str, str, str]] = []
    repo_findings.extend(audit_duplicate_ids(duplicate_ids, severity_levels))
    repo_findings.extend(audit_hierarchy_tiers(all_doc_metadata, severity_levels))
    repo_findings.extend(audit_orphans(all_doc_metadata, severity_levels))
    repo_findings.extend(audit_version_bump(all_doc_metadata, severity_levels))
    for category, msg in audit_traceability_graph(all_doc_metadata):
        repo_findings.append(
            (severity_levels.get(category, "ERROR"), msg, "TRACEABILITY-GRAPH")
        )

    for sev, msg, pfile in repo_findings:
        results.append({"file": pfile, "errors": [(sev, msg)]})
        if sev in ("CRITICAL", "ERROR"):
            has_blocking_errors = True
            fail_count += 1
        else:
            warning_count += 1
        if args.format == "text":
            status = "[FAIL]" if sev in ("CRITICAL", "ERROR") else "[WARNING]"
            print(f"\n{status} {pfile}\n  - [{sev}] {msg}")

    # @flow: RepoAudit --> Reporter["<b>build_sarif()</b>: Generate output format (SARIF/JSON/Text)"]
    # Step 5: Final output generation and CI/CD Exit Code enforcement
    if args.format == "sarif":
        print(json.dumps(build_sarif(results), indent=2))
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
        for fpath, disabled in disabled_usages.items():
            rendered = ", ".join(
                f"{r} (reason: {reason})" if reason else f"{r} (UNDOCUMENTED)"
                for r, reason in disabled.items()
            )
            print(f"  {fpath}: {rendered}")

    if rejected_usages:
        print("\n--- Rejected Disables (CRITICAL findings cannot be silenced) ---")
        for fpath, rules in rejected_usages.items():
            print(
                f"  {fpath}: {', '.join(rules)} -> directive ignored; finding still enforced"
            )

    # @flow: Reporter --> HasBlockErr{"Has blocking errors?"}
    if has_blocking_errors:
        print(f"\n[FAIL] Audit failed with {fail_count} blocking error(s).")
        # @flow: HasBlockErr -->|Yes| ExitFail((sys.exit 1))
        sys.exit(1)  # Triggers a hard block in CI/CD pipelines
    else:
        print("\nAll checks passed! Documentation is Governance-Compliant.")
        # @flow: HasBlockErr -->|No| ExitSuccess((sys.exit 0))
        sys.exit(0)  # Triggers a successful pass in CI/CD pipelines


if __name__ == "__main__":
    main()
