import os
import re
import yaml

def resolve_registry_with_duplicates(target_dir):
    """
    Scan the target directory to build a registry of document IDs, their metadata,
    AND a map of any duplicate IDs (which violate the SSOT uniqueness invariant).
    Returns:
        tuple: (set of doc_ids, dict mapping doc_id -> doc_meta, dict mapping
                duplicated doc_id -> list of conflicting file paths)
    """
    ids = set()
    metadata_registry = {}
    first_seen_path = {}
    duplicates = {}
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', '.vscode', 'validators')]
        for file in files:
            if not file.endswith('.md'): continue
            path = os.path.join(root, file)
            norm_path = path.replace('\\', '/')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
                if fm:
                    data = yaml.safe_load(fm.group(1))
                    if data and 'doc_meta' in data:
                        doc_id = data['doc_meta'].get('id')
                        if doc_id:
                            if doc_id in ids:
                                # Collision: a doc ID must be globally unique (SSOT).
                                duplicates.setdefault(doc_id, [first_seen_path[doc_id]]).append(norm_path)
                            else:
                                ids.add(doc_id)
                                metadata_registry[doc_id] = data['doc_meta']
                                first_seen_path[doc_id] = norm_path
            except Exception:
                # Intentionally silent: malformed files are handled by the main linter loop.
                continue
    return ids, metadata_registry, duplicates

def resolve_all_doc_registry(target_dir):
    """
    Backward-compatible wrapper returning (set of doc_ids, dict id -> doc_meta).
    Use resolve_registry_with_duplicates() when duplicate detection is required.
    """
    ids, metadata_registry, _ = resolve_registry_with_duplicates(target_dir)
    return ids, metadata_registry

def resolve_all_doc_ids(target_dir):
    """
    Wrapper for backward compatibility. Returns only the set of IDs.
    """
    ids, _ = resolve_all_doc_registry(target_dir)
    return ids
