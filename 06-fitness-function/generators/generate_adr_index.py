import os
import yaml
import re

def parse_frontmatter(content):
    match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except:
            pass
    return None

def generate_index():
    adr_dir = os.path.join(os.path.dirname(__file__), '..', '05-decisions')
    adrs = []

    for root, _, files in os.walk(adr_dir):
        for file in files:
            if file.endswith('.md') and file.upper() != 'INDEX.md':
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, adr_dir).replace('\\', '/')
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_meta = parse_frontmatter(content)
                if doc_meta and 'doc_meta' in doc_meta:
                    meta = doc_meta['doc_meta']
                    adrs.append({
                        'id': meta.get('id', 'N/A'),
                        'title': meta.get('title', file),
                        'type': meta.get('adr_type', 'N/A'),
                        'status': meta.get('status', 'N/A'),
                        'created': meta.get('created', 'N/A'),
                        'expiry': meta.get('expiry_date', 'N/A'),
                        'path': rel_path
                    })

    # Sort by ID
    adrs.sort(key=lambda x: x['id'])

    index_content = [
        "# Architectural Decision Records (ADR) Index",
        "",
        "This is the authoritative index of all Architectural Decision Records within the Scnehaux enterprise.",
        "",
        "| ID | Title | Type | Status | Created | Expiry Date |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for adr in adrs:
        id_link = f"[{adr['id']}]({adr['path']})"
        title = adr['title'].replace('|', '\\|') # Escape pipes for markdown table
        index_content.append(
            f"| {id_link} | {title} | {adr['type']} | {adr['status']} | {adr['created']} | {adr['expiry']} |"
        )

    index_path = os.path.join(adr_dir, 'INDEX.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_content) + '\n')
    
    print(f"Generated ADR Index at {index_path} with {len(adrs)} records.")

if __name__ == "__main__":
    generate_index()
