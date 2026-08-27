import os
import re
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_FILE = os.path.join(ROOT_DIR, "00-governance", "GDC-001-fitness-functions.md")

COMMENTS = {
    "auditors": "# (External environment validators)",
    "config": "# (Engine configuration & environment variables)",
    "fs": "# (File system utilities & workspace traversal)",
    "parsing": "# (Data extraction from raw files)",
    "reporting": "# (CLI output formatting & CI/CD error logs)",
    "validators": "# (The core policy sandbox)",
    "domains": "# (Federated domain-specific triad scripts)",
    "global_rules.py": "# (Foundational Python rules for all documents)",
    "cli.py": "# (The Master Fitness Function Entrypoint)",
    "engine": "# (Core automated execution logic)",
    "generators": "# (Dynamic docs and topography autobuilders)",
    "scripts": "# (Git hooks and manual CI/CD utilities)",
    "tests": "# (High-coverage pytest suite)",
}


def tracked_paths() -> list[tuple[str, ...]]:
    result = subprocess.run(
        ["git", "-C", ROOT_DIR, "ls-files", "--cached", "--", "06-fitness-function"],
        check=True,
        capture_output=True,
        text=True,
    )

    prefix = "06-fitness-function/"
    paths = []
    for raw in result.stdout.splitlines():
        normalized = raw.replace("\\", "/")
        if not normalized.startswith(prefix):
            continue

        parts = tuple(part for part in normalized[len(prefix) :].split("/") if part)
        if not parts:
            continue
        if parts[-1] == "__init__.py":
            continue
        if any(
            part.startswith(".") or part == "__pycache__" or part.endswith(".egg-info")
            for part in parts
        ):
            continue
        paths.append(parts)

    return sorted(
        set(paths),
        key=lambda parts: tuple(part.casefold() for part in parts),
    )


def build_path_tree(paths: list[tuple[str, ...]]) -> dict:
    tree = {}
    for parts in paths:
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
    return tree


def render_tree(tree: dict, prefix: str = "") -> list[str]:
    lines = []
    items = sorted(tree.items(), key=lambda item: item[0].casefold())

    for idx, (item, children) in enumerate(items):
        is_last = idx == len(items) - 1
        connector = "└── " if is_last else "├── "
        is_dir = bool(children)
        comment = COMMENTS.get(item, "")

        base_str = (
            f"{prefix}{connector}{item}/" if is_dir else f"{prefix}{connector}{item}"
        )

        if comment:
            clean_len = len(
                base_str.replace("│", "")
                .replace("├", "")
                .replace("─", "")
                .replace("└", "")
            )
            pad = max(1, 26 - clean_len)
            lines.append(f"│   {base_str}{' ' * pad}{comment}")
        else:
            lines.append(f"│   {base_str}")

        if is_dir:
            extension = "    " if is_last else "│   "
            lines.extend(render_tree(children, prefix + extension))

    return lines


def generate_markdown_from_paths(paths: list[tuple[str, ...]]) -> str:
    tree_lines = ["```text", "scnehaux-architecture/", "└── 06-fitness-function/"]
    tree_lines.extend(render_tree(build_path_tree(paths), "    "))
    tree_lines.append("```")
    return "\n".join(tree_lines)


def generate_markdown() -> str:
    return generate_markdown_from_paths(tracked_paths())


def update_document():
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"<!-- BEGIN_ENGINE_TOPOGRAPHY -->.*?<!-- END_ENGINE_TOPOGRAPHY -->",
        f"<!-- BEGIN_ENGINE_TOPOGRAPHY -->\n{generate_markdown()}\n<!-- END_ENGINE_TOPOGRAPHY -->",
        content,
        flags=re.DOTALL,
    )

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("[OK] Generated Engine Topography -> GDC-001-fitness-functions.md")


if __name__ == "__main__":
    update_document()
