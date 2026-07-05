import os
import glob
import yaml


def parse_metadata(filepath):
    """
    Extract the `doc_meta` YAML block from a specific markdown file.
    Returns an empty dictionary if parsing fails or the block is missing.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---")
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            return meta.get("doc_meta", {})
    except Exception:
        pass
    return {}


def generate_index(directory, layer_name):
    """
    Scan the specified architecture layer directory (e.g. `03-domain` for PAD, `04-system` for SAD)
    and generate a master `INDEX.md` cataloging all found documents and their traceability metrics.
    """
    index_path = os.path.join(directory, "INDEX.md")
    md_files = glob.glob(os.path.join(directory, "**/*.md"), recursive=True)

    docs = []
    for f in md_files:
        if os.path.basename(f) == "INDEX.md":
            continue
        meta = parse_metadata(f)
        if meta and "id" in meta:
            # Get relative path for link
            rel_path = os.path.relpath(f, directory).replace("\\", "/")
            docs.append(
                {
                    "id": meta.get("id", ""),
                    "title": meta.get("title", ""),
                    "owner": meta.get("owner", ""),
                    "status": meta.get("status", ""),
                    "link": rel_path,
                    "fulfilled_by": len(meta.get("fulfilled_by", []))
                    if meta.get("fulfilled_by")
                    else 0,
                    "parent_pad": meta.get("parent_pad", ""),
                }
            )

    # Sort by ID
    docs.sort(key=lambda x: x["id"])

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(f"# {layer_name} Layer Index\n\n")
        f.write(
            "> **Auto-generated**: This file is maintained by `scripts/generate_pad_sad_index.py`.\n\n"
        )

        if layer_name == "Platform Architecture (PAD)":
            f.write("| ID | Title | Owner | Status | Fulfilled By (SADs) |\n")
            f.write("|---|---|---|---|---|\n")
            for d in docs:
                f.write(
                    f"| [{d['id']}]({d['link']}) | {d['title']} | {d['owner']} | {d['status']} | {d['fulfilled_by']} |\n"
                )
        else:
            f.write("| ID | Title | Parent PAD | Owner | Status |\n")
            f.write("|---|---|---|---|---|\n")
            for d in docs:
                parent = d["parent_pad"]
                if isinstance(parent, list):
                    parent = ", ".join(parent)
                f.write(
                    f"| [{d['id']}]({d['link']}) | {d['title']} | {parent} | {d['owner']} | {d['status']} |\n"
                )

    print(f"Generated {index_path}")


if __name__ == "__main__":
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    generate_index(os.path.join(base, "03-domain"), "Platform Architecture (PAD)")
    generate_index(os.path.join(base, "04-system"), "Software Architecture (SAD)")
