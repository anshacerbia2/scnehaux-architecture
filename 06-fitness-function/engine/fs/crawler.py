import os
import logging
from engine.config.constants import EXCLUDED_DIRS
from engine.parsing.markdown_ast import parse_frontmatter

logger = logging.getLogger(__name__)


def gather_markdown_files(target_dirs, repo_root=None, allowed_root_dirs=None):
    """
    Scans and deduplicates Markdown file paths from target directories.
    Deduplication here applies strictly to file paths (to handle overlapping input directories), 
    NOT to document IDs. Enforces Fail-Closed security by strictly checking `allowed_root_dirs` 
    and bypassing deeply nested exclusions. If `repo_root` is provided, it guarantees that only 
    directories explicitly within the repository boundary are scanned; any external paths will 
    trigger a hard crash.

    <pre>Args:
        - target_dirs (str | list): Target paths/files to scan.
        - repo_root (str, optional): Repository root for boundary validation.
        - allowed_root_dirs (set, optional): Whitelisted top-level directories. External paths 
          trigger a hard crash.

    Returns:
        list: Valid Markdown file paths.

    Raises:
        SystemExit: If path traversal (e.g., `../`) or unauthorized directories are detected.
    </pre>
    """

    if isinstance(target_dirs, str):
        target_dirs = [target_dirs]

    files_to_lint = []
    repo_root_abs = os.path.abspath(repo_root) if repo_root else None

    for target in target_dirs:
        if allowed_root_dirs and repo_root:
            abs_target = os.path.abspath(target)
            try:
                rel_to_root = os.path.relpath(abs_target, repo_root_abs)
                # CASE 3: Path Traversal Attack (Outside Repo)
                # Input: target_dirs = ["../other-repo/secret.md"]
                # Logic: os.path.relpath detects the ".." prefix. Fails closed (HARD CRASH) to prevent bypass.
                if rel_to_root.startswith(".."):
                    import sys

                    print(
                        f"CRITICAL: Target '{target}' is outside the repository boundary. Execution blocked to prevent validation bypass.",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                # CASE 2 & 5: Specific Internal Directory (Valid vs Unauthorized)
                # Input: target_dirs = ["00-governance/designs"] (Valid) or ["docs/api"] (Unauthorized)
                # Logic: Validates if the path starts with an allowed directory. If not, Fails closed.
                if rel_to_root != ".":
                    is_allowed = False
                    norm_rel = os.path.normpath(rel_to_root)
                    for allowed in allowed_root_dirs:
                        allowed_path = os.path.normpath(allowed)
                        if norm_rel == allowed_path or norm_rel.startswith(
                            allowed_path + os.sep
                        ):
                            is_allowed = True
                            break
                    if not is_allowed:
                        import sys

                        print(
                            f"CRITICAL: Target '{target}' is not in allowed artifact directories. Execution blocked to prevent validation bypass.",
                            file=sys.stderr,
                        )
                        sys.exit(1)
            # CASE 4: Cross-Drive Traversal (Windows Specific)
            # Input: target_dirs = ["C:/malicious.md"], repo_root = "D:/repo"
            # Logic: os.path.relpath throws ValueError because C: and D: do not intersect. Fails closed.
            except ValueError:
                import sys

                print(
                    f"CRITICAL: Target '{target}' is on a different drive than the repository. Execution blocked to prevent validation bypass.",
                    file=sys.stderr,
                )
                sys.exit(1)

        if os.path.isfile(target):
            if target.lower().endswith(".md"):
                files_to_lint.append(target)
        else:
            for root, dirs, files in os.walk(target):
                # CASE 1: Full Repository Scan (Default target = ".")
                # Logic: Because it's at the root, it STERILIZES the directory tree by aggressively pruning
                # folders like "src" or "node_modules", only entering allowed_root_dirs like "00-governance".
                if (
                    allowed_root_dirs
                    and repo_root
                    and os.path.abspath(root) == repo_root_abs
                ):
                    allowed_first_levels = set(
                        os.path.normpath(d).split(os.sep)[0] for d in allowed_root_dirs
                    )
                    dirs[:] = [d for d in dirs if d in allowed_first_levels]
                    files[:] = []  # Sterilize root
                else:
                    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

                if allowed_root_dirs and repo_root:
                    rel_root = os.path.relpath(os.path.abspath(root), repo_root_abs)
                    if rel_root != ".":
                        is_allowed = False
                        norm_rel = os.path.normpath(rel_root)
                        for allowed in allowed_root_dirs:
                            allowed_path = os.path.normpath(allowed)
                            if norm_rel == allowed_path or norm_rel.startswith(
                                allowed_path + os.sep
                            ):
                                is_allowed = True
                                break
                        if not is_allowed:
                            files[:] = []

                for file in files:
                    if file.lower().endswith(".md"):
                        files_to_lint.append(os.path.join(root, file))

    # Deduplicate file paths while preserving order (to keep determinism).
    # This prevents scanning the exact same file twice if `target_dirs` contains overlapping directories.
    # Note: This does NOT deduplicate document IDs. Two different files with the same ID will still pass through.
    seen = set()
    unique_files = []
    for f in files_to_lint:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    return unique_files


def build_metadata_registry(target_dirs, repo_root=None, allowed_root_dirs=None):
    """
    Builds a central registry of architecture documents by parsing YAML frontmatter. Enforces the 
    SSOT (Single Source of Truth) invariant by detecting duplicate IDs.
    **Note**: This phase strictly GATHERS data by calling `gather_markdown_files`. We then call 
    `parse_frontmatter` but intentionally IGNORE any parsing errors (e.g., missing `doc_meta` or 
    invalid YAML). This is because this phase is NOT for structural validation, its sole purpose 
    is to build a registry to detect duplicate IDs. All other metadata validation is delegated to 
    the main engine.

    <pre>Args:
        - target_dirs (str | list): Target directories to scan.
        - allowed_root_dirs (set, optional): Whitelisted root directories for boundary enforcement.

    Returns:
        tuple: (unique_ids, registry, duplicates)
            - unique_ids (set): Discovered document IDs.
            - registry (dict): Maps `doc_id` to its metadata (includes `_filepath`).
            - duplicates (dict): Maps duplicated `doc_id` to conflicting file paths.

    Raises:
        SystemExit: Inherited from `gather_markdown_files` if path traversal (e.g., `../`) or 
        unauthorized directories are detected.
    </pre>
    """
    if isinstance(target_dirs, str):
        target_dirs = [target_dirs]

    ids = set()
    metadata_registry = {}
    first_seen_path = {}
    duplicates = {}

    files_to_lint = gather_markdown_files(target_dirs, repo_root, allowed_root_dirs)

    for path in files_to_lint:
        norm_path = path.replace("\\", "/")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            doc_meta, _ = parse_frontmatter(content)
            if doc_meta:
                doc_id = doc_meta.get("id")
                if doc_id:
                    if doc_id in ids:
                        duplicates.setdefault(doc_id, [first_seen_path[doc_id]]).append(
                            norm_path
                        )
                    else:
                        ids.add(doc_id)
                        doc_meta["_filepath"] = norm_path
                        metadata_registry[doc_id] = doc_meta
                        first_seen_path[doc_id] = norm_path
        except Exception as e:
            logger.debug("Scanner skipping '%s': %s", path, e)
            continue

    return ids, metadata_registry, duplicates
