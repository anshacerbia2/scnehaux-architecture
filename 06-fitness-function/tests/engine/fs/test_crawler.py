from engine.fs.crawler import resolve_all_doc_registry, resolve_registry_with_duplicates


def test_resolve_all_doc_registry(tmp_path):
    repo_dir = tmp_path / "scnehaux"
    repo_dir.mkdir()

    valid_md = repo_dir / "ADR-001.md"
    valid_md.write_text("---\ndoc_meta:\n  id: ADR-001\n---\nBody")

    no_meta_md = repo_dir / "README.md"
    no_meta_md.write_text("# Hello")

    node_mod = repo_dir / "node_modules"
    node_mod.mkdir()
    ignored_md = node_mod / "ADR-002.md"
    ignored_md.write_text("---\ndoc_meta:\n  id: ADR-002\n---\nBody")

    ids, registry = resolve_all_doc_registry(str(repo_dir))

    assert "ADR-001" in ids
    assert "ADR-002" not in ids
    assert registry["ADR-001"]["id"] == "ADR-001"


def test_duplicate_id_detection(tmp_path):
    d = tmp_path / "repo"
    d.mkdir()
    (d / "a.md").write_text("---\ndoc_meta:\n  id: ADR-001\n---\nA")
    (d / "b.md").write_text("---\ndoc_meta:\n  id: ADR-001\n---\nB")
    (d / "c.md").write_text("---\ndoc_meta:\n  id: ADR-002\n---\nC")
    ids, meta, dupes = resolve_registry_with_duplicates(str(d))
    assert "ADR-001" in dupes and len(dupes["ADR-001"]) == 2
    assert "ADR-002" not in dupes
    assert "ADR-002" in ids


# ---------- ADD#2: traceability graph ----------
