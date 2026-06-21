import os
import yaml
import re
import glob

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
                        safe_k = str(k).replace('_', ' ').title()
                        safe_v = str(v).replace('|', '\\|')
                        val_parts.append(f"**{safe_k}**: `{safe_v}`")
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

if __name__ == "__main__":
    success_count = 0
    rules_dir = os.path.join(PROJECT_ROOT, '00-governance', 'rules')
    yaml_files = glob.glob(os.path.join(rules_dir, 'linting-rules*.yaml'))
    
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
            if table_str:
                if inject_to_markdown(md_path, table_str):
                    print(f"[OK] Injected {yaml_file} -> {md_file}")
                    success_count += 1
        except Exception as e:
            print(f"Error processing {yaml_file}: {e}")

    print(f"\nGenerator finished. Successfully injected {success_count} files.")
