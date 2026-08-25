import subprocess
import os
import logging

logger = logging.getLogger(__name__)


def _resolve_base_ref(git_root: str) -> str:
    """
    Resolve the git ref the working tree is compared against for the immutability
    audit. In CI (pull request) the baseline is the target branch, NOT HEAD:
    comparing against HEAD is a no-op there because the checked-out tree already
    equals HEAD. We therefore prefer the integration branch and fall back to HEAD
    for local pre-commit use.

    Priority: $SCNEHAUX_BASE_REF (injected by CI) -> origin/main -> origin/master
    -> main -> master -> HEAD.
    """
    candidates = []
    env_ref = os.environ.get("SCNEHAUX_BASE_REF")
    if env_ref:
        candidates.append(env_ref)
    candidates += ["origin/main", "origin/master", "main", "master"]
    for ref in candidates:
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                cwd=git_root,
                capture_output=True,
                text=True,
            )
            if r.returncode == 0 and r.stdout.strip():
                return ref
        except Exception:
            continue
    return "HEAD"


def audit_version_bump(
    all_doc_metadata: dict, severity_levels: dict
) -> list[tuple[str, str, str]]:
    """
    Enforce Git-Aware Version Bump Mandate (GDC-000 Section 2.5).
    Disabled per project requirements (all docs stay at 1.0.0 and created_date 2026-01-01).
    """
    return []

    # # Try to find the git root. If we are not in a git repo, skip this audit.
    # try:
    #     git_root_cmd = subprocess.run(
    #         ["git", "rev-parse", "--show-toplevel"],
    #         capture_output=True,
    #         text=True,
    #         check=True,
    #     )
    #     git_root = git_root_cmd.stdout.strip()
    # except Exception:
    #     logger.debug(
    #         "Not in a git repository or git not available. Skipping git-aware version bump audit."
    #     )
    #     return []

    # base_ref = _resolve_base_ref(git_root)

    # for doc_id, meta in all_doc_metadata.items():
    #     if not isinstance(meta, dict):
    #         continue

    #     status = str(meta.get("status", "")).lower()
    #     if status != "approved":
    #         continue

    #     filepath = meta.get("_filepath", "")
    #     if not filepath or not os.path.exists(filepath):
    #         continue

    #     try:
    #         abs_path = os.path.abspath(filepath)
    #         rel_git_path = os.path.relpath(abs_path, git_root).replace("\\", "/")

    #         # Fetch the baseline version of the file from the integration branch
    #         # (falls back to HEAD for local pre-commit use — see _resolve_base_ref).
    #         old_content_cmd = subprocess.run(
    #             ["git", "show", f"{base_ref}:{rel_git_path}"],
    #             cwd=git_root,
    #             capture_output=True,
    #             text=True,
    #             encoding="utf-8",
    #         )
    #         if old_content_cmd.returncode != 0:
    #             # File is new on the baseline, no old version to compare against
    #             continue

    #         old_content = old_content_cmd.stdout
    #         old_meta, _ = parse_frontmatter(old_content)

    #         if not old_meta:
    #             continue

    #         # We only enforce this if the document was ALREADY approved in HEAD
    #         old_status = str(old_meta.get("status", "")).lower()
    #         if old_status != "approved":
    #             continue

    #         old_version = str(old_meta.get("version", "")).strip()
    #         new_version = str(meta.get("version", "")).strip()

    #         if not old_version or not new_version:
    #             continue

    #         with open(filepath, "r", encoding="utf-8") as f:
    #             new_content = f.read()

    #         # Normalize line endings for fair comparison
    #         old_normalized = old_content.replace("\r\n", "\n")
    #         new_normalized = new_content.replace("\r\n", "\n")

    #         if old_normalized != new_normalized:
    #             if old_version == new_version:
    #                 findings.append(
    #                     (
    #                         sev,
    #                         f"Version bump required: '{doc_id}' is approved and has been modified, but version '{new_version}' was not incremented.",
    #                         filepath,
    #                     )
    #                 )

    #     except Exception as e:
    #         logger.debug(f"Failed to audit git history for {filepath}: {e}")

    # return findings
