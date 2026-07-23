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

    out = []
    out.append("```mermaid\n%%{init: {'theme': 'neutral'}}%%")
    out.append("graph LR")
    out.append("    %% EAD Layer")
    for d in docs.values():
        if d["type"] == "EAD":
            out.append(f"    {d['id']}[{d['id']}]:::ead")

    out.append("    %% PAD Layer")
    for d in docs.values():
        if d["type"] == "PAD":
            out.append(f"    {d['id']}[{d['id']}]:::pad")
            parent = d.get("realizes_capability")
            if parent:
                if isinstance(parent, list):
                    for p in parent:
                        out.append(f"    {d['id']} -.realizes.-> {p}")
                else:
                    out.append(f"    {d['id']} -.realizes.-> {parent}")

    out.append("    %% SAD Layer")
    for d in docs.values():
        if d["type"] == "SAD":
            out.append(f"    {d['id']}[{d['id']}]:::sad")
            parent = d.get("parent_pad")
            if parent:
                if isinstance(parent, list):
                    for p in parent:
                        out.append(f"    {d['id']} --> {p}")
                else:
                    out.append(f"    {d['id']} --> {parent}")

    out.append("    classDef ead fill:#059669,stroke:#047857,color:#fff")
    out.append("    classDef pad fill:#2563eb,stroke:#1d4ed8,color:#fff")
    out.append("    classDef sad fill:#7c3aed,stroke:#6d28d9,color:#fff")
    out.append("```")

    output_path = os.path.join(base_dir, "03-domain", "TRACEABILITY.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Traceability Graph\n\n")
        f.write("\n".join(out) + "\n")

    print(f"[OK] Generated Traceability Graph -> {output_path}")


if __name__ == "__main__":
    generate_graph()
