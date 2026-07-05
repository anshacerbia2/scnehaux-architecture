import os
import logging
from engine.parsing.markdown_ast import parse_frontmatter

logger = logging.getLogger(__name__)


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
        dirs[:] = [
            d
            for d in dirs
            if d not in (".git", "__pycache__", "node_modules", ".vscode", "validators")
        ]
        for file in files:
            if not file.endswith(".md"):
                continue
            path = os.path.join(root, file)
            norm_path = path.replace("\\", "/")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                doc_meta, _ = parse_frontmatter(content)
                if doc_meta:
                    doc_id = doc_meta.get("id")
                    if doc_id:
                        if doc_id in ids:
                            # Collision: a doc ID must be globally unique (SSOT).
                            duplicates.setdefault(
                                doc_id, [first_seen_path[doc_id]]
                            ).append(norm_path)
                        else:
                            ids.add(doc_id)
                            # Inject the resolved path so repo-level auditors (git_auditor
                            # version-bump, graph_auditor hierarchy/orphan reporting) can
                            # locate the artifact on disk. Without this the immutability
                            # audit silently skips every document.
                            doc_meta["_filepath"] = norm_path
                            metadata_registry[doc_id] = doc_meta
                            first_seen_path[doc_id] = norm_path
            except Exception as e:
                # Malformed files are handled by the main linter loop; log here for diagnostics.
                logger.debug("Scanner skipping '%s': %s", path, e)
                continue
    return ids, metadata_registry, duplicates


def resolve_all_doc_registry(target_dir):
    """
    Backward-compatible wrapper returning (set of doc_ids, dict id -> doc_meta).
    Use resolve_registry_with_duplicates() when duplicate detection is required.
    """
    ids, metadata_registry, _ = resolve_registry_with_duplicates(target_dir)
    return ids, metadata_registry
