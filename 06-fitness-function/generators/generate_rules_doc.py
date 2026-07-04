import os
import sys
import json
import re
import glob
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SCHEMAS_DIR = os.path.join(PROJECT_ROOT, '00-governance', 'schemas')
DOCS_DIR = os.path.join(PROJECT_ROOT, '00-governance')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_type(prop_def):
    if 'type' not in prop_def:
        return ""
    t = prop_def['type']
    if isinstance(t, list):
        types = []
        for type_item in t:
            if type_item == 'array' and 'items' in prop_def and 'type' in prop_def['items']:
                types.append(f"array[{prop_def['items']['type']}]")
            else:
                types.append(type_item)
        return " &#124; ".join(types)
    else:
        if t == 'array' and 'items' in prop_def and 'type' in prop_def['items']:
            return f"array[{prop_def['items']['type']}]"
        return t

def format_enum(prop_def):
    if 'enum' in prop_def:
        items = "".join([f"<li>{str(v).replace('|', '\\|')}</li>" for v in prop_def['enum']])
        return f"<ul>{items}</ul>"
    return ""

def generate_from_x_engine_config(data):
    x_config = data.get('x-engine-config', {})
    rules = x_config.get('rules', {})
    severity = x_config.get('severity_levels', {})
    
    if not rules and not severity:
        return ""
    
    lines = []
    if rules:
        lines.extend([
            "| Rule Category      | Parameter                | Enforcement / Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |",
            "| :----------------- | :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |"
        ])
        for category, params in rules.items():
            if isinstance(params, dict):
                cat_name = category.replace('_', ' ').title()
                for param, value in params.items():
                    param_name = param.replace('_', ' ').title()
                    if isinstance(value, list):
                        list_items = "".join([f"<li>`{str(v).replace('|', '\\|')}`</li>" for v in value])
                        val_str = f"<ul>{list_items}</ul>"
                    elif isinstance(value, dict):
                        val_parts = []
                        for k, v in value.items():
                            safe_k = str(k).replace('_', ' ').title()
                            if isinstance(v, list):
                                safe_v = "<ul>" + "".join([f"<li>`{str(item).replace('|', '\\|')}`</li>" for item in v]) + "</ul>"
                            else:
                                safe_v = f"`{str(v).replace('|', '\\|')}`"
                            val_parts.append(f"**{safe_k}**: {safe_v}")
                        val_str = "<br>".join(val_parts)
                    else:
                        val_str = f"`{str(value).replace('|', '\\|')}`"
                    lines.append(f"| **{cat_name}** | {param_name} | {val_str} |")
            else:
                cat_name = "Governance"
                param_name = category.replace('_', ' ').title()
                val_str = f"`{str(params).replace('|', '\\|')}`"
                lines.append(f"| **{cat_name}** | {param_name} | {val_str} |")
                
    if severity:
        if rules:
            lines.extend(["", "### Severity Levels", ""])
        lines.extend([
            "| Error Code                        | Severity (CI Action) |",
            "| :-------------------------------- | :------------------- |"
        ])
        for code, level in severity.items():
            lines.append(f"| `{code}` | **{level}** |")
            
    return "\n".join(lines)

def generate_from_json_schema(data):
    definitions = data.get('definitions', {})
    if not definitions:
        return ""
        
    lines = [
        "| Rule Category | Parameter | Enforcement / Value |",
        "| :--- | :--- | :--- |"
    ]
    
    for def_key, def_val in definitions.items():
        category_name = def_val.get('title', def_key.replace('_', ' ').title())
        
        if "Metadata" in category_name:
            if 'required' in def_val:
                reqs = []
                for req in def_val['required']:
                    t = format_type(def_val.get('properties', {}).get(req, {}))
                    reqs.append(f"<li>{req} ({t})</li>" if t else f"<li>{req}</li>")
                val_str = "<ul>" + "".join(reqs) + "</ul>"
                lines.append(f"| **{category_name}** | {category_name} | {val_str} |")
                
            if 'properties' in def_val:
                for prop_name, prop_val in def_val['properties'].items():
                    title = prop_val.get('title', prop_name)
                    if 'required' in prop_val and 'properties' in prop_val:
                        reqs = []
                        for req in prop_val['required']:
                            t = format_type(prop_val['properties'].get(req, {}))
                            reqs.append(f"<li>{req} ({t})</li>" if t else f"<li>{req}</li>")
                        val_str = "<ul>" + "".join(reqs) + "</ul>"
                        lines.append(f"| **{category_name}** | {title} | {val_str} |")
                        
                    if 'properties' in prop_val:
                        for sub_prop_name, sub_prop_val in prop_val['properties'].items():
                            if 'enum' in sub_prop_val:
                                sub_title = sub_prop_val.get('title', sub_prop_name)
                                enum_str = format_enum(sub_prop_val)
                                lines.append(f"| **{category_name}** | {sub_title} | {enum_str} |")

                    if 'allOf' in prop_val:
                        for cond_block in prop_val['allOf']:
                            if 'if' in cond_block and 'then' in cond_block:
                                then_block = cond_block['then']
                                if 'required' in then_block and 'properties' in then_block:
                                    for req in then_block['required']:
                                        req_prop = then_block['properties'].get(req, {})
                                        if 'required' in req_prop:
                                            sub_reqs = []
                                            for sub_req in req_prop['required']:
                                                t = format_type(req_prop.get('properties', {}).get(sub_req, {}))
                                                sub_reqs.append(f"<li>{sub_req} ({t})</li>" if t else f"<li>{sub_req}</li>")
                                            val_str = "<ul>" + "".join(sub_reqs) + "</ul>"
                                            req_title = f"{req} Required Fields"
                                            lines.append(f"| **{category_name}** | {req_title} | {val_str} |")

        elif "Structural" in category_name:
            x_titles = def_val.get('x-titles', {})
            for list_type in ['required', 'recommended']:
                if list_type in def_val:
                    p_name = x_titles.get(list_type, list_type.title() + " Sections")
                    items = "".join([f"<li>{v}</li>" for v in def_val[list_type]])
                    val_str = f"<ul>{items}</ul>"
                    lines.append(f"| **{category_name}** | {p_name} | {val_str} |")
            
            if 'allOf' in def_val:
                for cond_block in def_val['allOf']:
                    if 'if' in cond_block and 'then' in cond_block:
                        for list_type in ['required', 'recommended']:
                            if list_type in cond_block['then']:
                                x_titles_then = cond_block['then'].get('x-titles', {})
                                p_name = x_titles_then.get(list_type, list_type.title() + " Sections")
                                items = "".join([f"<li>{v}</li>" for v in cond_block['then'][list_type]])
                                val_str = f"<ul>{items}</ul>"
                                lines.append(f"| **{category_name}** | {p_name} | {val_str} |")

        elif "Content" in category_name:
            if 'properties' in def_val:
                def extract_rows(node, default_title_req, default_title_rec, default_title_proh, condition_text=""):
                    groups = { 'required': {}, 'recommended': {}, 'prohibited': {} }
                    if not isinstance(node, dict): return groups
                            
                    x_titles = node.get('x-titles', {})
                    t_req = x_titles.get('required', default_title_req)
                    t_rec = x_titles.get('recommended', default_title_rec)
                    t_proh = x_titles.get('prohibited_keywords', default_title_proh)
                    
                    if 'pattern' in node:
                        match = re.search(r'\[\\\\s\\\\S\]\\\*(.*?)\[\\\\s\\\\S\]\\\*', node['pattern'])
                        if not match:
                            match = re.search(r'\[\\s\\S\]\*(.*?)\[\\s\\S\]\*', node['pattern'])
                        if match:
                            groups['required'].setdefault(t_req + condition_text, []).append(match.group(1))
                            
                    if 'recommended' in node and isinstance(node['recommended'], list):
                        for k in node['recommended']:
                            groups['recommended'].setdefault(t_rec + condition_text, []).append(k)
                            
                    if 'prohibited_keywords' in node and isinstance(node['prohibited_keywords'], list):
                        for k in node['prohibited_keywords']:
                            groups['prohibited'].setdefault(t_proh + condition_text, []).append(k)

                    child_nodes = []
                    if 'allOf' in node and isinstance(node['allOf'], list):
                        child_nodes.extend(node['allOf'])
                    if 'if' in node: child_nodes.append(node['if'])
                    if 'then' in node: child_nodes.append(node['then'])
                        
                    for child in child_nodes:
                        child_groups = extract_rows(child, t_req, t_rec, t_proh, condition_text)
                        for g_type in groups:
                            for title, kws in child_groups[g_type].items():
                                groups[g_type].setdefault(title, []).extend(kws)
                    return groups
                
                for prop_name, prop_val in def_val['properties'].items():
                    groups = extract_rows(prop_val, prop_name + " (Required)", prop_name + " (Recommended)", prop_name + " (Prohibited)")
                    for g_type, titles in groups.items():
                        for title, kws in titles.items():
                            unique_kws = list(dict.fromkeys(kws))
                            if unique_kws:
                                val_str = "<ul>" + "".join([f"<li>{k}</li>" for k in unique_kws]) + "</ul>"
                                lines.append(f"| **{category_name}** | {title} | {val_str} |")

    return "\n".join(lines)

def generate_markdown_table(data):
    if 'x-engine-config' in data:
        return generate_from_x_engine_config(data)
    else:
        return generate_from_json_schema(data)

def current_block(md_path):
    if not os.path.exists(md_path):
        return None
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern_rules = r'<!-- AUTO-GENERATED-RULES:START -->(.*?)<!-- AUTO-GENERATED-RULES:END -->'
    pattern_schema = r'<!-- AUTO-GENERATED-SCHEMA:START -->(.*?)<!-- AUTO-GENERATED-SCHEMA:END -->'
    
    m = re.search(pattern_rules, content, flags=re.DOTALL)
    if not m:
        m = re.search(pattern_schema, content, flags=re.DOTALL)
        
    if not m:
        return None
    return m.group(1).strip()

def inject_to_markdown(md_path, table_str):
    if not os.path.exists(md_path):
        return False
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern_rules = r'(<!-- AUTO-GENERATED-RULES:START -->)(.*?)(<!-- AUTO-GENERATED-RULES:END -->)'
    pattern_schema = r'(<!-- AUTO-GENERATED-SCHEMA:START -->)(.*?)(<!-- AUTO-GENERATED-SCHEMA:END -->)'
    
    if re.search(pattern_rules, content, flags=re.DOTALL):
        pattern = pattern_rules
    elif re.search(pattern_schema, content, flags=re.DOTALL):
        pattern = pattern_schema
    else:
        return False
    
    def replacer(match):
        return f"{match.group(1)}\n\n{table_str}\n\n{match.group(3)}"
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return True

def process(check=False):
    success_count = 0
    drift = []
    schema_files = sorted(glob.glob(os.path.join(SCHEMAS_DIR, '*.schema.json')))
    
    for schema_path in schema_files:
        schema_file = os.path.basename(schema_path)
        try:
            json_data = load_json(schema_path)
            if not json_data:
                continue

            if 'x-engine-config' in json_data:
                md_file = json_data['x-engine-config'].get('config', {}).get('target_doc')
            else:
                md_file = json_data.get('config', {}).get('target_doc')

            if not md_file:
                print(f"[SKIP] {schema_file} has no config.target_doc declared.")
                continue

            md_path = os.path.join(DOCS_DIR, md_file)
            table_str = generate_markdown_table(json_data)
            if not table_str:
                print(f"[SKIP] {schema_file} generated an empty table.")
                continue

            if check:
                existing = current_block(md_path)
                if existing is None:
                    drift.append((md_file, "missing AUTO-GENERATED markers or file absent"))
                elif existing != table_str.strip():
                    drift.append((md_file, f"out of sync with {schema_file}"))
            else:
                if inject_to_markdown(md_path, table_str):
                    print(f"[OK] Injected {schema_file} -> {md_file}")
                    success_count += 1
                else:
                    print(f"[FAIL] Failed to inject {schema_file} -> {md_file} (Missing markers)")
        except Exception as e:
            print(f"Error processing {schema_file}: {e}")

    if not check:
        print(f"\nGenerator finished. Successfully injected {success_count} files.")
    return drift

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate/verify AUTO-GENERATED rule tables in GDC docs from the JSON Schema SSOT.")
    parser.add_argument('--check', action='store_true',
                        help="Verify docs are in sync with JSON Schema without writing. Exit 1 on drift (for CI).")
    args = parser.parse_args()

    if args.check:
        drift = process(check=True)
        if drift:
            print("[DRIFT] Generated rule docs are out of sync with the JSON Schema SSOT:")
            for doc, reason in drift:
                print(f"  - {doc}: {reason}")
            print("\nRun `python scripts/generate_rules_doc.py` and commit the result.")
            sys.exit(1)
        print("[OK] All generated rule docs are in sync with the JSON Schema SSOT.")
        sys.exit(0)
    else:
        process(check=False)
