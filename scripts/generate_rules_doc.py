import os
import sys
import yaml
import re
import glob
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_markdown_table(data):
    if not data:
        return ""
        
    rules = data.get('rules', {})
    severity = data.get('severity_levels', {})
    
    if not rules and not severity:
        return ""
    
    lines = []
    
    if rules:
        lines.extend([
            "| Rule Category | Parameter | Enforcement / Value |",
            "| :--- | :--- | :--- |"
        ])
        
        # Dynamically traverse the YAML rules dictionary
        for category, params in rules.items():
            # Format the category name (e.g., 'content_quality' -> 'Content Quality')
            cat_name = category.replace('_', ' ').title()
            
            for param, value in params.items():
                # Format the parameter name
                param_name = param.replace('_', ' ').title()
                
                # Format the value dynamically based on its data type
                if isinstance(value, list):
                    # Format lists as HTML unordered lists for better readability in markdown tables
                    list_items = "".join([f"<li>`{str(v).replace('|', '\\|')}`</li>" for v in value])
                    val_str = f"<ul>{list_items}</ul>"
                elif isinstance(value, dict):
                    # Join nested objects with HTML line breaks
                    val_parts = []
                    for k, v in value.items():
                        safe_k = str(k).replace('_', ' ')
                        if safe_k.islower():
                            safe_k = safe_k.title()
                        if isinstance(v, list):
                            safe_v = "<ul>" + "".join([f"<li>`{str(item).replace('|', '\\|')}`</li>" for item in v]) + "</ul>"
                        else:
                            safe_v = f"`{str(v).replace('|', '\\|')}`"
                        val_parts.append(f"**{safe_k}**: {safe_v}")
                    val_str = "<br>".join(val_parts)
                else:
                    # Basic primitives
                    val_str = f"`{str(value).replace('|', '\\|')}`"
                    
                lines.append(f"| **{cat_name}** | {param_name} | {val_str} |")
                
    if severity:
        if rules:
            lines.append("") # Add spacing between tables
            lines.append("### Severity Levels")
            lines.append("")
        
        lines.extend([
            "| Error Code | Severity (CI Action) |",
            "| :--- | :--- |"
        ])
        for code, level in severity.items():
            lines.append(f"| `{code}` | **{level}** |")
            
    return "\n".join(lines)

def inject_to_markdown(md_path, table_str):
    if not os.path.exists(md_path):
        print(f"File not found: {md_path}")
        return False
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(<!-- AUTO-GENERATED-RULES:START -->)(.*?)(<!-- AUTO-GENERATED-RULES:END -->)'
    
    # Check if the placeholder exists
    if not re.search(pattern, content, flags=re.DOTALL):
        print(f"Skipping {md_path} (No placeholder found)")
        return False
    
    def replacer(match):
        return f"{match.group(1)}\n{table_str}\n{match.group(3)}"
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return True

def current_block(md_path):
    """Return the content currently between the AUTO-GENERATED markers, or None."""
    if not os.path.exists(md_path):
        return None
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'<!-- AUTO-GENERATED-RULES:START -->(.*?)<!-- AUTO-GENERATED-RULES:END -->'
    m = re.search(pattern, content, flags=re.DOTALL)
    if not m:
        return None
    return m.group(1).strip()


def process(check=False):
    """
    Generate rules tables from YAML and either inject them (check=False) or verify
    the committed docs are in sync (check=True). Returns a list of drift records
    [(doc, reason)] in check mode; an empty list means fully in sync.
    """
    success_count = 0
    drift = []
    rules_dir = os.path.join(PROJECT_ROOT, '00-governance', 'rules')
    yaml_files = sorted(glob.glob(os.path.join(rules_dir, 'linting-rules*.yaml')))

    for yaml_path in yaml_files:
        yaml_file = os.path.basename(yaml_path)
        try:
            yaml_data = load_yaml(yaml_path)
            if not yaml_data:
                continue

            config = yaml_data.get('config', {})
            md_file = config.get('target_doc')
            if not md_file:
                print(f"[SKIP] {yaml_file} has no config.target_doc declared.")
                continue

            md_path = os.path.join(PROJECT_ROOT, '00-governance', md_file)
            table_str = generate_markdown_table(yaml_data)
            if not table_str:
                continue

            if check:
                existing = current_block(md_path)
                if existing is None:
                    drift.append((md_file, "missing AUTO-GENERATED markers or file absent"))
                elif existing != table_str.strip():
                    drift.append((md_file, f"out of sync with {yaml_file}"))
            else:
                if inject_to_markdown(md_path, table_str):
                    print(f"[OK] Injected {yaml_file} -> {md_file}")
                    success_count += 1
        except Exception as e:
            print(f"Error processing {yaml_file}: {e}")

    if not check:
        print(f"\nGenerator finished. Successfully injected {success_count} files.")
    return drift


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate/verify AUTO-GENERATED rule tables in GDC docs from the YAML SSOT.")
    parser.add_argument('--check', action='store_true',
                        help="Verify docs are in sync with YAML without writing. Exit 1 on drift (for CI).")
    args = parser.parse_args()

    if args.check:
        drift = process(check=True)
        if drift:
            print("[DRIFT] Generated rule docs are out of sync with the YAML SSOT:")
            for doc, reason in drift:
                print(f"  - {doc}: {reason}")
            print("\nRun `python scripts/generate_rules_doc.py` and commit the result.")
            sys.exit(1)
        print("[OK] All generated rule docs are in sync with the YAML SSOT.")
        sys.exit(0)
    else:
        process(check=False)
