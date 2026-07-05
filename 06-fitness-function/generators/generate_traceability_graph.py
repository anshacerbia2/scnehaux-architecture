import os
import glob
import yaml


def parse_metadata(filepath):
    """
    Safely extract the `doc_meta` YAML block from a specific markdown file.
    Returns None if parsing fails or the block is missing.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---")
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            if meta and "doc_meta" in meta:
                return meta["doc_meta"]
    except Exception:
        pass
    return None


def generate_graph():
    """
    Crawl all architecture documents to extract `parent_pad` and `realizes_capability` linkages.
    Generates a Mermaid.js flowchart mapping the hierarchical relationships (SAD -> PAD -> EAD).
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    md_files = glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True)

    docs = {}
    for f in md_files:
        if "templates" in f or "scripts" in f or "README" in f or "INDEX" in f:
            continue
        meta = parse_metadata(f)
        if meta and "id" in meta:
            doc_id = meta["id"]
            docs[doc_id] = {
                "id": doc_id,
                "type": doc_id.split("-")[0],
                "parent_pad": meta.get("parent_pad"),
                "realizes_capability": meta.get("realizes_capability"),
                "governed_by": meta.get("governed_by", []),
            }

    print("```mermaid")
    print("graph TD")
    print("    %% EAD Layer")
    for d in docs.values():
        if d["type"] == "EAD":
            print(f"    {d['id']}[{d['id']}]:::ead")

    print("    %% PAD Layer")
    for d in docs.values():
        if d["type"] == "PAD":
            print(f"    {d['id']}[{d['id']}]:::pad")
            parent = d.get("realizes_capability")
            if parent:
                if isinstance(parent, list):
                    for p in parent:
                        print(f"    {d['id']} -.realizes.-> {p}")
                else:
                    print(f"    {d['id']} -.realizes.-> {parent}")

    print("    %% SAD Layer")
    for d in docs.values():
        if d["type"] == "SAD":
            print(f"    {d['id']}[{d['id']}]:::sad")
            parent = d.get("parent_pad")
            if parent:
                if isinstance(parent, list):
                    for p in parent:
                        print(f"    {d['id']} --> {p}")
                else:
                    print(f"    {d['id']} --> {parent}")

    print("    classDef ead fill:#059669,stroke:#047857,color:#fff")
    print("    classDef pad fill:#2563eb,stroke:#1d4ed8,color:#fff")
    print("    classDef sad fill:#7c3aed,stroke:#6d28d9,color:#fff")
    print("```")


if __name__ == "__main__":
    generate_graph()
