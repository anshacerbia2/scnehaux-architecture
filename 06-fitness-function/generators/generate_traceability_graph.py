import glob
import os
from pathlib import Path

import yaml


def parse_metadata(filepath):
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


def _path_key(path: str, base_dir: str) -> str:
    return Path(path).resolve().relative_to(Path(base_dir).resolve()).as_posix().casefold()


def discover_markdown_files(base_dir: str) -> list[str]:
    files = glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True)
    return sorted(files, key=lambda path: _path_key(path, base_dir))


def _sorted_docs(docs: dict, artifact_type: str) -> list[dict]:
    return sorted(
        (doc for doc in docs.values() if doc["type"] == artifact_type),
        key=lambda doc: doc["id"],
    )


def _parents(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return sorted(value)
    return [value]


def render_graph(docs: dict) -> str:
    out = [
        "```mermaid\n%%{init: {'theme': 'neutral'}}%%",
        "graph LR",
        "    %% EAD Layer",
    ]

    for d in _sorted_docs(docs, "EAD"):
        out.append(f"    {d['id']}[{d['id']}]:::ead")

    out.append("    %% PAD Layer")
    for d in _sorted_docs(docs, "PAD"):
        out.append(f"    {d['id']}[{d['id']}]:::pad")
        for parent in _parents(d.get("realizes_capability")):
            out.append(f"    {d['id']} -.realizes.-> {parent}")

    out.append("    %% SAD Layer")
    for d in _sorted_docs(docs, "SAD"):
        out.append(f"    {d['id']}[{d['id']}]:::sad")
        for parent in _parents(d.get("parent_pad")):
            out.append(f"    {d['id']} --> {parent}")

    out.extend(
        [
            "    classDef ead fill:#059669,stroke:#047857,color:#fff",
            "    classDef pad fill:#2563eb,stroke:#1d4ed8,color:#fff",
            "    classDef sad fill:#7c3aed,stroke:#6d28d9,color:#fff",
            "```",
        ]
    )
    return "\n".join(out)


def generate_graph():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    docs = {}
    for f in discover_markdown_files(base_dir):
        normalized = Path(f).as_posix()
        if (
            "/templates/" in normalized
            or "/scripts/" in normalized
            or Path(f).name == "README.md"
            or Path(f).name == "INDEX.md"
        ):
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

    output_path = os.path.join(base_dir, "03-domain", "TRACEABILITY.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Traceability Graph\n\n")
        f.write(render_graph(docs) + "\n")

    print(f"[OK] Generated Traceability Graph -> {output_path}")


if __name__ == "__main__":
    generate_graph()
