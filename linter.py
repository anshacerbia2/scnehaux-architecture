import yaml
import re
import os
import sys

def load_rules(rules_path):
    try:
        with open(rules_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Rules file '{rules_path}' not found.")
        sys.exit(1)

def lint_file(file_path, rules):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    errors = []
    
    # Pre-process content to remove code blocks for text analysis
    # This prevents flagging prohibited words inside code examples
    text_content = re.sub(r'```[\s\S]*?```', '', content)
    text_content = re.sub(r'`[^`]*`', '', text_content)

    # 1. Metadata Validation & Semantic Parsing
    doc_id = None
    frontmatter_match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
    if not frontmatter_match:
         blockquote_meta = re.search(r'> \*\*Version\*\*', content)
         if not blockquote_meta:
             errors.append("CRITICAL: Missing YAML frontmatter or standard metadata block.")
    else:
        try:
            frontmatter_data = yaml.safe_load(frontmatter_match.group(1))
            if 'doc_meta' in frontmatter_data and 'id' in frontmatter_data['doc_meta']:
                doc_id = frontmatter_data['doc_meta']['id']
        except Exception as e:
            errors.append(f"CRITICAL: Failed to parse YAML frontmatter: {e}")

    # 2. Structural Validation (Context-Aware Mandatory Sections & Order)
    if 'structure' in rules['rules'] and doc_id:
        mandatory_sections = []
        optional_sections = []
        if doc_id.startswith('DOC-P'):
            mandatory_sections = rules['rules']['structure'].get('pad_sections', [])
            optional_sections = rules['rules']['structure'].get('pad_optional_sections', [])
        elif doc_id.startswith('DOC-S') or doc_id.startswith('APP-'):
            mandatory_sections = rules['rules']['structure'].get('sad_sections', [])
            optional_sections = rules['rules']['structure'].get('sad_optional_sections', [])
        elif doc_id.startswith('TDD-'):
            mandatory_sections = rules['rules']['structure'].get('tdd_sections', [])
            optional_sections = rules['rules']['structure'].get('tdd_optional_sections', [])
        elif doc_id.startswith('EAD-') or doc_id.startswith('DOC-E'):
            mandatory_sections = rules['rules']['structure'].get('ead_sections', [])
            optional_sections = rules['rules']['structure'].get('ead_optional_sections', [])
        elif doc_id.startswith('GDC-'):
            mandatory_sections = rules['rules']['structure'].get('gdc_sections', [])
            optional_sections = rules['rules']['structure'].get('gdc_optional_sections', [])
        elif doc_id.startswith('ADR-'):
            mandatory_sections = rules['rules']['structure'].get('adr_sections', [])
            optional_sections = rules['rules']['structure'].get('adr_optional_sections', [])
        elif doc_id.startswith('STD-'):
            mandatory_sections = rules['rules']['structure'].get('std_sections', [])
            optional_sections = rules['rules']['structure'].get('std_optional_sections', [])
        else:
             errors.append(f"WARNING: Unknown doc_meta.id prefix '{doc_id}'. Cannot apply contextual structural validation.")

        if mandatory_sections:
            found_sections = []
            found_optional = []
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                for section in mandatory_sections:
                    # Match "## 1. Title" or "## Title"
                    match = re.search(r'^##\s+(\d+\.\s+)?' + re.escape(section), line, re.IGNORECASE)
                    if match:
                        found_sections.append((i, section))
                        break
                for section in optional_sections:
                    match = re.search(r'^##\s+(\d+\.\s+)?' + re.escape(section), line, re.IGNORECASE)
                    if match:
                        found_optional.append((i, section))
                        break

            # 2a. Check Existence
            found_section_names = [name for _, name in found_sections]
            for section in mandatory_sections:
                if section not in found_section_names:
                    errors.append(f"ERROR: Missing mandatory section for {doc_id}: '{section}'")
                    
            for _, name in found_optional:
                print(f"  - [INFO] Conditional policy utilized: '{name}'")

            # 2b. Check Order
            if len(found_sections) > 1:
                expected_order = {name: i for i, name in enumerate(mandatory_sections)}
                last_idx = -1
                last_name = ""
                
                for _, name in found_sections:
                    curr_idx = expected_order.get(name)
                    if curr_idx is not None:
                        if curr_idx < last_idx:
                             errors.append(f"ERROR: Structure violation. Section '{name}' found after '{last_name}', but should be before.")
                        last_idx = curr_idx
                        last_name = name
    elif not doc_id:
         errors.append("ERROR: Cannot perform structural validation. doc_meta.id is missing.")

    # 3. Content Quality (Prohibited Words)
    if 'content' in rules['rules']:
        for word in rules['rules']['content']['prohibited_words']:
            if re.search(r'\b' + re.escape(word) + r'\b', text_content, re.IGNORECASE):
                errors.append(f"ERROR: Found prohibited word: '{word}'")

    # 4. Ambiguity Check
    if 'ambiguity_check' in rules['rules']['content']:
        pattern = rules['rules']['content']['ambiguity_check']['pattern']
        if re.search(pattern, text_content, re.IGNORECASE):
            errors.append(f"WARNING: {rules['rules']['content']['ambiguity_check']['message']}")

    if errors:
        print(f"\n[FAIL] {file_path}")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"[PASS] {file_path}")
        return True

def main():
    rules_path = '00-governance/linting-rules.yaml'
    rules = load_rules(rules_path)
    
    # Simple walker for now, can be expanded to CLI args
    target_dir = '.'
    has_errors = False
    
    print("Starting Architecture Documentation Audit...\n")
    
    for root, dirs, files in os.walk(target_dir):
        if '.git' in dirs: dirs.remove('.git') # Ignore git
        if 'node_modules' in dirs: dirs.remove('node_modules')
        
        for file in files:
            if file.endswith('.md') and file.lower() != 'readme.md' and 'templates' not in file.lower():
                # Skip the governance folder itself for now as it uses different meta structure? 
                # No, let's lint it too, it should comply!
                full_path = os.path.join(root, file)
                if not lint_file(full_path, rules):
                    has_errors = True

    if has_errors:
        sys.exit(1)
    else:
        print("\nAll checks passed! Documentation is Governance-Compliant.")

if __name__ == "__main__":
    main()
