"""
Scnehaux Architecture Documentation Linter — Orchestrator
Routes documents to type-specific validators.
"""
import os
import sys
import yaml
import json
import argparse
from validators.factory import detect_doc_type, get_validator
from validators.scanner import resolve_registry_with_duplicates
from validators.traceability import audit_traceability_graph
from validators.utils import parse_frontmatter
import copy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def deep_update(d, u):
    """
    Recursively merge two dictionaries.
    This is used to overlay specific document rules (e.g., SAD, PAD)
    on top of the global governance rules.
    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def load_rules(rules_path):
    """
    Load and parse a YAML ruleset file.
    Terminates the program if the file cannot be found.
    """
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Rules file '{rules_path}' not found.")
        sys.exit(1)

def print_errors(file_path, errors, output_format="text"):
    """
    Format and aggregate errors for a specific file.
    Determines if the file contains any "blocking" errors (CRITICAL or ERROR).
    WARNINGs will be flagged but are considered non-blocking for CI.
    """
    has_blocking = any(sev in ('CRITICAL', 'ERROR') for sev, _ in errors)
    has_warnings = any(sev == 'WARNING' for sev, _ in errors)

    # If JSON output is requested, do not print to stdout yet, just return the state.
    if output_format == "json":
        return errors, not has_blocking, has_blocking

    # If there are no errors, mark as PASS
    if not errors:
        print(f"[PASS] {file_path}")
        return errors, True, False

    # Print the formatted failure/warning message to stdout
    status_str = "[FAIL]" if has_blocking else "[WARNING]"
    print(f"\n{status_str} {file_path}")
    for sev, msg in errors:
        print(f"  - [{sev}] {msg}")

    return errors, not has_blocking and not has_warnings, has_blocking

def _disable_info(validator):
    """Capture lint_disable governance state from a validator for the CI audit."""
    return {
        'disabled': {r: validator.disable_reasons.get(r) for r in validator.disabled_rules},
        'rejected': set(getattr(validator, 'rejected_disables', set())),
    }

def lint_file(file_path, global_rules, all_doc_ids, all_doc_metadata, output_format="text"):
    """
    Orchestrate validation for a single markdown file.
    This executes the core lifecycle: Read -> Parse Metadata -> Identify Type -> Merge Rules -> Validate.
    Returns (errors, passed, is_blocking, disable_info).
    """
    rel_path = os.path.relpath(file_path, '.').replace('\\', '/')
    filename = os.path.basename(file_path)

    # Step 1: Read the raw markdown content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errs, p, b = print_errors(file_path, [('ERROR', f"Failed to read file: {e}")], output_format)
        return errs, p, b, {}

    # Step 2: Parse the YAML Frontmatter to extract document metadata
    doc_meta, meta_err = parse_frontmatter(content)
    if meta_err:
        # Any failure in parsing the frontmatter is a critical block
        errs, p, b = print_errors(file_path, [('ERROR', meta_err)], output_format)
        return errs, p, b, {}

    if doc_meta and str(doc_meta.get('status', '')).lower() == 'draft':
        # Enforce max_draft_age_days even for skipped drafts
        draft_errs = []
        last_reviewed_raw = doc_meta.get('last_reviewed')
        if not last_reviewed_raw:
            draft_errs.append(('ERROR', "Draft document is missing 'last_reviewed' date to track draft age. Drafts cannot evade governance indefinitely."))
        else:
            import datetime
            from validators.utils import parse_date
            last_reviewed = parse_date(last_reviewed_raw)
            if last_reviewed:
                age_days = (datetime.date.today() - last_reviewed).days
                max_draft_age = global_rules.get('rules', {}).get('governance', {}).get('max_draft_age_days', 30)
                if age_days > max_draft_age:
                    draft_errs.append(('ERROR', f"Draft document age of {age_days} days exceeds limit of {max_draft_age} days. Must be reviewed, finalized, or deleted."))

        if draft_errs:
            errs, p, b = print_errors(file_path, draft_errs, output_format)
            return errs, p, b, {}

        if output_format == 'text':
            print(f"[SKIP] {file_path} (status: draft — exempt from scoring)")
        return [], True, False, {}

    # Step 3: Detect the Document Type (SAD, PAD, ADR, etc.) based on ID or filename
    doc_id = doc_meta.get('id') if doc_meta else None
    doc_type = detect_doc_type(doc_id, filename, rel_path)

    if not doc_type:
        errs, p, b = print_errors(file_path, [
            ('ERROR', f"Unknown doc type for '{filename}'. Missing or invalid metadata ID. Hard blocking.")
        ], output_format)
        return errs, p, b, {}

    # Step 4: Retrieve the specific validator class for this document type
    validator_cls = get_validator(doc_type)
    if not validator_cls:
        errs, p, b = print_errors(file_path, [
            ('ERROR', f"No validator implemented for doc type '{doc_type}'. Hard blocking.")
        ], output_format)
        return errs, p, b, {}

    # Step 5: Build the final rule context by merging Global Rules with Specific Rules
    merged_rules = copy.deepcopy(global_rules)
    specific_rules_path = os.path.join(SCRIPT_DIR, f"00-governance/rules/linting-rules-{doc_type.lower()}.yaml")

    if not os.path.exists(specific_rules_path):
        errs, p, b = print_errors(file_path, [
            ('ERROR', f"Missing mandatory domain-specific linting rules: '{specific_rules_path}'. Hard blocking.")
        ], output_format)
        return errs, p, b, {}

    specific_rules = load_rules(specific_rules_path)
    if specific_rules and 'rules' in specific_rules:
        # Inject doc-specific rules (like allowed ADR statuses) into the global ruleset
        merged_rules['rules'] = deep_update(merged_rules.get('rules', {}), specific_rules['rules'])

    # Step 6: Initialize the specific validator and execute validation
    validator = validator_cls(file_path, content, doc_meta or {}, merged_rules, all_doc_ids, all_doc_metadata)
    errors = validator.validate()

    errs, p, b = print_errors(file_path, errors, output_format)
    return errs, p, b, _disable_info(validator)

def build_sarif(results):
    """
    Convert aggregated results into a SARIF 2.1.0 document so violations surface as
    inline annotations on GitHub PRs (via code-scanning upload).
    `results` is a list of {"file": path, "errors": [(severity, message), ...]}.
    """
    level_map = {'CRITICAL': 'error', 'ERROR': 'error', 'WARNING': 'warning'}
    sarif_results = []
    for item in results:
        uri = item['file'].replace('\\', '/')
        if uri.startswith('./'):
            uri = uri[2:]
        for sev, msg in item['errors']:
            sarif_results.append({
                "ruleId": f"scnehaux/{sev.lower()}",
                "level": level_map.get(sev, 'warning'),
                "message": {"text": msg},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": uri},
                        "region": {"startLine": 1}
                    }
                }]
            })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "Scnehaux Architecture Linter",
                "informationUri": "https://github.com/scnehaux/scnehaux-architecture",
                "rules": []
            }},
            "results": sarif_results
        }]
    }

def main():
    """
    Main entrypoint for the Linter engine.
    Parses arguments, traverses the directory tree, runs per-file and repo-level
    audits, and enforces exit codes for CI/CD.
    """
    # Step 1: Parse CLI Arguments
    parser = argparse.ArgumentParser(description='Scnehaux Architecture Linter')
    parser.add_argument('--format', choices=['text', 'json', 'sarif'], default='text', help='Output format')
    parser.add_argument('--target', nargs='+', default=['.'], help='Target directories or files to lint (default: current directory)')
    args = parser.parse_args()

    # Step 2: Load the Global Governance Rules baseline
    global_rules_path = os.path.join(SCRIPT_DIR, '00-governance/rules/linting-rules.yaml')
    global_rules = load_rules(global_rules_path)
    severity_levels = global_rules.get('severity_levels', {})

    # Step 3: Pre-scan all files to build the registry of doc IDs (cross-reference) and detect duplicates.
    all_doc_ids, all_doc_metadata, duplicate_ids = resolve_registry_with_duplicates('.')

    has_blocking_errors = False
    results = []                 # [{"file", "errors": [(sev,msg)]}]
    disabled_usages = {}
    undocumented_disables = {}
    rejected_usages = {}
    total_files = 0
    pass_count = 0
    warning_count = 0
    fail_count = 0

    if args.format == 'text':
        print("Starting Modular Architecture Documentation Audit (linter)...\n")

    files_to_lint = []
    for target in args.target:
        if os.path.isfile(target):
            files_to_lint.append(target)
        else:
            for root, dirs, files in os.walk(target):
                # Exclude irrelevant directories to improve performance and prevent false positives
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.vscode', 'validators')]
                for file in files:
                    files_to_lint.append(os.path.join(root, file))

    for full_path in files_to_lint:
        # Filter 1: Only audit Markdown files
        if not full_path.lower().endswith('.md'): continue

        filename = os.path.basename(full_path)
        # Filter 2: Ignore root standard files like README or index
        if filename.lower() in ('readme.md', 'index.md', 'contributing.md'): continue

        # Filter 3: Ignore template and copy files (these are blueprints, not actual documentation)
        if full_path.lower().endswith('.copy.md'): continue
        if full_path.lower().endswith('.template.md') or full_path.lower().endswith('-template.md') or 'templates' in os.path.basename(os.path.dirname(full_path)).lower(): continue

        # Execute linting for the current valid file
        file_errors, passed, is_blocking, disable_info = lint_file(full_path, global_rules, all_doc_ids, all_doc_metadata, args.format)

        # Track lint_disable governance
        disabled = disable_info.get('disabled', {})
        if disabled:
            disabled_usages[full_path] = disabled
            undoc = [r for r, reason in disabled.items() if not reason]
            if undoc:
                undocumented_disables[full_path] = undoc
        rejected = disable_info.get('rejected', set())
        if rejected:
            rejected_usages[full_path] = sorted(rejected)

        # Track statistics
        total_files += 1
        if is_blocking:
            fail_count += 1
        elif not passed:
            warning_count += 1
        else:
            pass_count += 1

        if file_errors:
            results.append({"file": full_path, "errors": list(file_errors)})

        # If any file fails with a CRITICAL or ERROR, mark the entire CI job as failed
        if is_blocking:
            has_blocking_errors = True

    # Step 4: Repo-level audits (only meaningful across the full registry)
    repo_findings = []  # (severity, message, pseudo_file)
    for dup_id, paths in sorted(duplicate_ids.items()):
        sev = severity_levels.get('duplicate_id', 'ERROR')
        repo_findings.append((sev,
            f"Duplicate document ID '{dup_id}' declared in multiple files: {', '.join(paths)}. "
            "Document IDs must be globally unique (SSOT).", paths[-1]))
    for category, msg in audit_traceability_graph(all_doc_metadata):
        repo_findings.append((severity_levels.get(category, 'ERROR'), msg, 'TRACEABILITY-GRAPH'))

    for sev, msg, pfile in repo_findings:
        results.append({"file": pfile, "errors": [(sev, msg)]})
        if sev in ('CRITICAL', 'ERROR'):
            has_blocking_errors = True
            fail_count += 1
        else:
            warning_count += 1
        if args.format == 'text':
            status = "[FAIL]" if sev in ('CRITICAL', 'ERROR') else "[WARNING]"
            print(f"\n{status} {pfile}\n  - [{sev}] {msg}")

    # Step 5: Final output generation and CI/CD Exit Code enforcement
    if args.format == 'sarif':
        print(json.dumps(build_sarif(results), indent=2))
        sys.exit(1 if has_blocking_errors else 0)

    if args.format == 'json':
        json_output = [
            {"file": r["file"], "errors": [{"severity": s, "message": m} for s, m in r["errors"]]}
            for r in results
        ]
        print(json.dumps(json_output, indent=2))
        sys.exit(1 if has_blocking_errors else 0)

    # Print summary statistics
    print(f"\n--- Audit Summary ---")
    print(f"  Total files scanned: {total_files}")
    print(f"  Passed:   {pass_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Failed:   {fail_count}")

    if disabled_usages:
        print(f"\n--- Lint Disable Usage ---")
        for fpath, disabled in disabled_usages.items():
            rendered = ', '.join(
                f"{r} (reason: {reason})" if reason else f"{r} (UNDOCUMENTED)"
                for r, reason in disabled.items()
            )
            print(f"  {fpath}: {rendered}")

    if rejected_usages:
        print(f"\n--- Rejected Disables (CRITICAL findings cannot be silenced) ---")
        for fpath, rules in rejected_usages.items():
            print(f"  {fpath}: {', '.join(rules)} -> directive ignored; finding still enforced")

    if has_blocking_errors:
        print(f"\n[FAIL] Audit failed with {fail_count} blocking error(s).")
        sys.exit(1) # Triggers a hard block in CI/CD pipelines
    else:
        print("\nAll checks passed! Documentation is Governance-Compliant.")
        sys.exit(0) # Triggers a successful pass in CI/CD pipelines

if __name__ == "__main__":
    main()
