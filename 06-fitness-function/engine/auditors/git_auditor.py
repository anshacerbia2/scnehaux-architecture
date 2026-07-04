import subprocess
import os
import logging
from engine.parsing.markdown_ast import parse_frontmatter

logger = logging.getLogger(__name__)

def audit_version_bump(all_doc_metadata: dict, severity_levels: dict) -> list[tuple[str, str, str]]:
    """
    Enforce Git-Aware Version Bump Mandate (GDC-000 Section 2.5).
    If an 'approved' artifact is modified, its version must be incremented.
    """
    findings = []
    sev = severity_levels.get('structural_integrity_violation', 'CRITICAL')
    
    # Try to find the git root. If we are not in a git repo, skip this audit.
    try:
        git_root_cmd = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        git_root = git_root_cmd.stdout.strip()
    except Exception:
        logger.debug("Not in a git repository or git not available. Skipping git-aware version bump audit.")
        return []

    for doc_id, meta in all_doc_metadata.items():
        if not isinstance(meta, dict):
            continue
            
        status = str(meta.get('status', '')).lower()
        if status != 'approved':
            continue
            
        filepath = meta.get('_filepath', '')
        if not filepath or not os.path.exists(filepath):
            continue
            
        try:
            abs_path = os.path.abspath(filepath)
            rel_git_path = os.path.relpath(abs_path, git_root).replace('\\', '/')
            
            # Fetch the previous version of the file from HEAD
            old_content_cmd = subprocess.run(["git", "show", f"HEAD:{rel_git_path}"], capture_output=True, text=True)
            if old_content_cmd.returncode != 0:
                # File is new, no old version to compare against
                continue
                
            old_content = old_content_cmd.stdout
            old_meta, _ = parse_frontmatter(old_content)
            
            if not old_meta:
                continue
                
            # We only enforce this if the document was ALREADY approved in HEAD
            old_status = str(old_meta.get('status', '')).lower()
            if old_status != 'approved':
                continue
                
            old_version = str(old_meta.get('version', '')).strip()
            new_version = str(meta.get('version', '')).strip()
            
            if not old_version or not new_version:
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                new_content = f.read()
                
            # Normalize line endings for fair comparison
            old_normalized = old_content.replace('\r\n', '\n')
            new_normalized = new_content.replace('\r\n', '\n')
            
            if old_normalized != new_normalized:
                if old_version == new_version:
                    findings.append((sev, f"Version bump required: '{doc_id}' is approved and has been modified, but version '{new_version}' was not incremented.", filepath))
                    
        except Exception as e:
            logger.debug(f"Failed to audit git history for {filepath}: {e}")
            
    return findings
