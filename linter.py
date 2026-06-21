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
from validators.scanner import resolve_all_doc_ids
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

def lint_file(file_path, global_rules, all_doc_ids, output_format="text"):
    """
    Orchestrate validation for a single markdown file.
    This executes the core lifecycle: Read -> Parse Metadata -> Identify Type -> Merge Rules -> Validate.
    """
    rel_path = os.path.relpath(file_path, '.').replace('\\', '/')
    filename = os.path.basename(file_path)
    
    # Step 1: Read the raw markdown content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errs, p, b = print_errors(file_path, [('ERROR', f"Failed to read file: {e}")], output_format)
        return errs, p, b, set()
    
    # Step 2: Parse the YAML Frontmatter to extract document metadata
    doc_meta, meta_err = parse_frontmatter(content)
    if meta_err:
        # Any failure in parsing the frontmatter is a critical block
        errs, p, b = print_errors(file_path, [('ERROR', meta_err)], output_format)
        return errs, p, b, set()
        
    if doc_meta and str(doc_meta.get('status', '')).lower() == 'draft':
        if output_format == 'text':
            print(f"[SKIP] {file_path} (status: draft — exempt from scoring)")
        return [], True, False, set()
    
    # Step 3: Detect the Document Type (SAD, PAD, ADR, etc.) based on ID or filename
    doc_id = doc_meta.get('id') if doc_meta else None
    doc_type = detect_doc_type(doc_id, filename, rel_path)
    
    if not doc_type:
        errs, p, b = print_errors(file_path, [
            ('ERROR', f"Unknown doc type for '{filename}'. Missing or invalid metadata ID. Hard blocking.")
        ], output_format)
        return errs, p, b, set()
    
    # Step 4: Retrieve the specific validator class for this document type
    validator_cls = get_validator(doc_type)
    if not validator_cls:
        errs, p, b = print_errors(file_path, [
            ('ERROR', f"No validator implemented for doc type '{doc_type}'. Hard blocking.")
        ], output_format)
        return errs, p, b, set()

    # Step 5: Build the final rule context by merging Global Rules with Specific Rules
    merged_rules = copy.deepcopy(global_rules)
    specific_rules_path = os.path.join(SCRIPT_DIR, f"00-governance/rules/linting-rules-{doc_type.lower()}.yaml")
    
    if not os.path.exists(specific_rules_path):
        errs, p, b = print_errors(file_path, [
            ('ERROR', f"Missing mandatory domain-specific linting rules: '{specific_rules_path}'. Hard blocking.")
        ], output_format)
        return errs, p, b, set()
        
    specific_rules = load_rules(specific_rules_path)
    if specific_rules and 'rules' in specific_rules:
        # Inject doc-specific rules (like allowed ADR statuses) into the global ruleset
        merged_rules['rules'] = deep_update(merged_rules.get('rules', {}), specific_rules['rules'])

    # Step 6: Initialize the specific validator and execute validation
    validator = validator_cls(file_path, content, doc_meta or {}, merged_rules, all_doc_ids)
    errors = validator.validate()
    
    errs, p, b = print_errors(file_path, errors, output_format)
    return errs, p, b, validator.disabled_rules

def main():
    """
    Main entrypoint for the Linter engine.
    Parses arguments, traverses the directory tree, and enforces exit codes.
    """
    # Step 1: Parse CLI Arguments
    parser = argparse.ArgumentParser(description='Scnehaux Architecture Linter')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--target', default='.', help='Target directory or file to lint (default: current directory)')
    args = parser.parse_args()

    # Step 2: Load the Global Governance Rules baseline
    global_rules_path = os.path.join(SCRIPT_DIR, '00-governance/rules/linting-rules.yaml')
    global_rules = load_rules(global_rules_path)
    
    # Step 3: Pre-scan all files to extract the `doc_meta.id` from the YAML frontmatter.
    # Output: Set of all document IDs (used for cross-reference validation).
    all_doc_ids = resolve_all_doc_ids('.')
    
    has_blocking_errors = False
    json_output = []
    disabled_usages = {}
    total_files = 0
    pass_count = 0
    warning_count = 0
    fail_count = 0
    
    if args.format == 'text':
        print("Starting Modular Architecture Documentation Audit (linter)...\n")
        
    if os.path.isfile(args.target):
        files_to_lint = [args.target]
    else:
        files_to_lint = []
        for root, dirs, files in os.walk(args.target):
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
        file_errors, passed, is_blocking, disabled_rules = lint_file(full_path, global_rules, all_doc_ids, args.format)
        
        if disabled_rules:
            disabled_usages[full_path] = list(disabled_rules)
            
        # Track statistics
        total_files += 1
        if is_blocking:
            fail_count += 1
        elif not passed:
            warning_count += 1
        else:
            pass_count += 1
            
        # If JSON formatting is requested, aggregate the output
        if args.format == 'json' and file_errors:
            json_output.append({
                "file": full_path,
                "errors": [{"severity": sev, "message": msg} for sev, msg in file_errors]
            })

        # If any file fails with a CRITICAL or ERROR, mark the entire CI job as failed
        if is_blocking:
            has_blocking_errors = True
    
    # Step 5: Final output generation and CI/CD Exit Code enforcement
    if args.format == 'json':
        print(json.dumps(json_output, indent=2))
        sys.exit(1 if has_blocking_errors else 0)

    # Print summary statistics
    print(f"\n--- Audit Summary ---")
    print(f"  Total files scanned: {total_files}")
    print(f"  Passed:   {pass_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Failed:   {fail_count}")

    if disabled_usages and args.format == 'text':
        print(f"\n--- Lint Disable Usage ---")
        for fpath, rules in disabled_usages.items():
            print(f"  {fpath}: {', '.join(rules)}")

    if has_blocking_errors:
        print(f"\n[FAIL] Audit failed with {fail_count} blocking error(s).")
        sys.exit(1) # Triggers a hard block in CI/CD pipelines
    else:
        print("\nAll checks passed! Documentation is Governance-Compliant.")
        sys.exit(0) # Triggers a successful pass in CI/CD pipelines

if __name__ == "__main__":
    main()
