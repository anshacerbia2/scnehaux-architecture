import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_FILE = os.path.join(ROOT_DIR, "00-governance", "GDC-001-fitness-functions.md")
FITNESS_DIR = os.path.join(ROOT_DIR, "06-fitness-function")

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


def build_tree(dir_path, prefix=""):
    """
    Recursively build a visual directory tree structure for the topography diagram.
    Appends high-level explanatory comments to specific engine directories.
    """
    lines = []
    items = sorted(os.listdir(dir_path))
    # Filter out pycache, hidden, and init
    items = [
        i
        for i in items
        if not i.startswith("__") and not i.startswith(".") and i != "__init__.py"
    ]

    for idx, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = idx == len(items) - 1
        connector = "└── " if is_last else "├── "

        comment = COMMENTS.get(item, "")

        # Format the item text
        base_str = (
            f"{prefix}{connector}{item}/"
            if os.path.isdir(path)
            else f"{prefix}{connector}{item}"
        )

        if comment:
            # Calculate padding to align comments nicely (approx col 35)
            # Remove unicode tree lines length from calc to approximate alignment
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

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            lines.extend(build_tree(path, prefix + extension))

    return lines


def generate_markdown():
    """
    Generate the complete topography markdown text block wrapped in a code fence.
    """
    tree_lines = ["```text", "scnehaux-architecture/", "└── 06-fitness-function/"]
    tree_lines.extend(build_tree(FITNESS_DIR, "    "))
    tree_lines.append("```")
    return "\n".join(tree_lines)


def update_document():
    """
    Inject the generated engine topography into the target Governance document (GDC-001)
    using the BEGIN_ENGINE_TOPOGRAPHY and END_ENGINE_TOPOGRAPHY marker tags.
    """
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
