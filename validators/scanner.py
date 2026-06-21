import os
import re
import yaml

def resolve_all_doc_ids(target_dir):
    """
    Scan the target directory to build a unique registry (set) of all document IDs.
    
    Algorithm:
    1. Initialize an empty Python `set` to store unique document IDs.
    2. Traverse the directory tree recursively using `os.walk`.
    3. Exclude irrelevant directories ('.git', '__pycache__', 'node_modules', '.vscode', 'validators') to optimize scanning speed.
    4. Filter files to strictly process only those with a '.md' (Markdown) extension.
    5. Open and read the entire raw content of each valid '.md' file into memory.
    6. Extract only the YAML frontmatter block at the top of the file using a regular expression.
    7. Parse the extracted YAML frontmatter string into a Python dictionary.
    8. Read the `id` value located specifically inside the `doc_meta` block.
    9. Append the extracted ID to the `ids` set.
    10. Silently ignore any parsing errors or malformed files (the main linter loop handles these later).
    11. Return the populated `ids` set.
    """
    ids = set()
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', '.vscode', 'validators')]
        for file in files:
            if not file.endswith('.md'): continue
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
                if fm:
                    data = yaml.safe_load(fm.group(1))
                    if data and 'doc_meta' in data:
                        doc_id = data['doc_meta'].get('id')
                        if doc_id: ids.add(doc_id)
            except Exception:
                # Intentionally silent: malformed files are handled by the main linter loop.
                continue
    return ids
