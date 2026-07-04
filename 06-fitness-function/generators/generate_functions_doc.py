import os
import sys
import ast
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ENGINE_DIR = os.path.join(PROJECT_ROOT, 'engine')

def extract_functions(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    tree = ast.parse(content)
    functions = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # Only document functions that sound like validators
            if node.name.startswith('_validate_') or node.name == 'validate_type_specific':
                docstring = ast.get_docstring(node)
                if docstring:
                    # Clean up docstring
                    desc = " ".join(line.strip() for line in docstring.split("\n") if line.strip())
                else:
                    desc = "*(No docstring provided)*"
                    
                functions.append({
                    'name': node.name,
                    'description': desc,
                    'line': node.lineno
                })
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name.startswith('_validate_') or item.name == 'validate_type_specific':
                        docstring = ast.get_docstring(item)
                        if docstring:
                            desc = " ".join(line.strip() for line in docstring.split("\n") if line.strip())
                        else:
                            desc = "*(No docstring provided)*"
                        functions.append({
                            'name': f"{node.name}.{item.name}",
                            'description': desc,
                            'line': item.lineno
                        })
    return sorted(functions, key=lambda x: x['name'])

def generate_markdown_table(all_funcs):
    if not all_funcs:
        return "*No validation functions documented yet.*"
        
    lines = [
        "| Module / Function | Description |",
        "| :--- | :--- |"
    ]
    
    for module, funcs in all_funcs.items():
        if not funcs:
            continue
        for f in funcs:
            name = f['name']
            desc = f['description']
            # Escape pipes just in case
            desc = desc.replace('|', '\\|')
            lines.append(f"| `{module}` <br> **{name}** | {desc} |")
            
    return "\n".join(lines)

def inject_to_markdown(md_path, table_str):
    if not os.path.exists(md_path):
        print(f"File not found: {md_path}")
        return False
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(<!-- AUTO-GENERATED-FUNCTIONS:START -->)(.*?)(<!-- AUTO-GENERATED-FUNCTIONS:END -->)'
    
    if not re.search(pattern, content, flags=re.DOTALL):
        print(f"Skipping {md_path} (No placeholder found)")
        return False
    
    def replacer(match):
        return f"{match.group(1)}\n{table_str}\n{match.group(3)}"
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return True

def main():
    target_md = os.path.join(os.path.dirname(PROJECT_ROOT), '00-governance', 'GDC-001-fitness-functions.md')
    
    modules_to_scan = [
        ('core/global_validations.py', os.path.join(ENGINE_DIR, 'core', 'global_validations.py')),
        ('validators/domains/adr_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'adr_validator.py')),
        ('validators/domains/sad_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'sad_validator.py')),
        ('validators/domains/pad_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'pad_validator.py')),
        ('validators/domains/ead_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'ead_validator.py')),
        ('validators/domains/std_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'std_validator.py')),
        ('validators/domains/tdd_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'tdd_validator.py')),
        ('validators/domains/gdc_validator.py', os.path.join(ENGINE_DIR, 'validators', 'domains', 'gdc_validator.py')),
    ]
    
    all_funcs = {}
    
    for mod_name, path in modules_to_scan:
        if os.path.exists(path):
            funcs = extract_functions(path)
            if funcs:
                all_funcs[mod_name] = funcs
                
    table_str = generate_markdown_table(all_funcs)
    
    if inject_to_markdown(target_md, table_str):
        print(f"[OK] Injected python function documentation into {target_md}")
    else:
        print("[FAIL] Failed to inject documentation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
