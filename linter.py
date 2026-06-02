"""
Scnehaux Architecture Documentation Linter — Orchestrator
Routes documents to type-specific validators.
"""
import os
import sys
import yaml
import json
import argparse
from validators import detect_doc_type, get_validator
from validators.base import resolve_all_doc_ids, parse_frontmatter

def load_rules(rules_path):
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Rules file '{rules_path}' not found.")
        sys.exit(1)

def print_errors(file_path, errors, output_format="text"):
    has_blocking = any(sev in ('CRITICAL', 'ERROR') for sev, _ in errors)
    
    if output_format == "json":
        return errors, not has_blocking, has_blocking
        
    if not errors:
        print(f"[PASS] {file_path}")
        return errors, True, False

    status_str = "[FAIL]" if has_blocking else "[WARNING]"
    print(f"\n{status_str} {file_path}")
    for sev, msg in errors:
        print(f"  - [{sev}] {msg}")
    
    return errors, not has_blocking, has_blocking

def lint_file(file_path, rules, all_doc_ids, output_format="text"):
    """Orchestrate validation for a single file."""
    rel_path = os.path.relpath(file_path, '.').replace('\\', '/')
    filename = os.path.basename(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return print_errors(file_path, [('ERROR', f"Failed to read file: {e}")], output_format)
    
    doc_meta, meta_err = parse_frontmatter(content)
    if meta_err:
        # Frontmatter issues are errors
        return print_errors(file_path, [('ERROR', meta_err)], output_format)
    
    doc_id = doc_meta.get('id') if doc_meta else None
    doc_type = detect_doc_type(doc_id, filename, rel_path)
    
    if not doc_type:
        return print_errors(file_path, [
            ('WARNING', f"Unknown doc type for '{filename}'. Contextual validation skipped.")
        ], output_format)
    
    validator_cls = get_validator(doc_type)
    if not validator_cls:
        return print_errors(file_path, [
            ('WARNING', f"No validator implemented for doc type '{doc_type}'.")
        ], output_format)

    validator = validator_cls(file_path, content, doc_meta or {}, rules, all_doc_ids)
    errors = validator.validate()
    
    return print_errors(file_path, errors, output_format)

def main():
    parser = argparse.ArgumentParser(description='Scnehaux Architecture Linter')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    args = parser.parse_args()

    rules_path = '00-governance/linting-rules.yaml'
    rules = load_rules(rules_path)
    
    # Pre-scan all document IDs for cross-reference validation
    all_doc_ids = resolve_all_doc_ids('.')
    
    has_blocking_errors = False
    json_output = []
    
    if args.format == 'text':
        print("Starting Modular Architecture Documentation Audit (linter)...\n")
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.vscode', 'validators')]
        for file in files:
            if not file.endswith('.md'): continue
            if file.lower() in ('readme.md', 'index.md', 'contributing.md'): continue
            if 'copy' in file.lower(): continue
            if 'templates' in file.lower() or 'templates' in root.lower(): continue
            
            full_path = os.path.join(root, file)
            file_errors, passed, is_blocking = lint_file(full_path, rules, all_doc_ids, args.format)
            
            if args.format == 'json' and file_errors:
                json_output.append({
                    "file": full_path,
                    "errors": [{"severity": sev, "message": msg} for sev, msg in file_errors]
                })

            if is_blocking:
                has_blocking_errors = True
    
    if args.format == 'json':
        print(json.dumps(json_output, indent=2))
        sys.exit(1 if has_blocking_errors else 0)

    if has_blocking_errors:
        print("\n[FAIL] Audit failed with blocking errors.")
        sys.exit(1)
    else:
        print("\nAll checks passed! Documentation is Governance-Compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main()
