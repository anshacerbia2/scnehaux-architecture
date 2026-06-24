import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validators.scanner import resolve_all_doc_ids, resolve_all_doc_registry

def test_resolve_all_doc_ids(tmp_path):
    # Setup mock repository
    repo_dir = tmp_path / "scnehaux"
    repo_dir.mkdir()
    
    # Create valid markdown file
    valid_md = repo_dir / "ADR-001.md"
    valid_md.write_text("---\ndoc_meta:\n  id: ADR-001\n---\nBody")
    
    # Create valid markdown file without frontmatter
    no_meta_md = repo_dir / "README.md"
    no_meta_md.write_text("# Hello")
    
    # Create node_modules file that should be ignored
    node_mod = repo_dir / "node_modules"
    node_mod.mkdir()
    ignored_md = node_mod / "ADR-002.md"
    ignored_md.write_text("---\ndoc_meta:\n  id: ADR-002\n---\nBody")

    ids, registry = resolve_all_doc_registry(str(repo_dir))
    
    assert "ADR-001" in ids
    assert "ADR-002" not in ids
    assert registry["ADR-001"]["id"] == "ADR-001"
    
    # Also test the backward compatible wrapper
    ids_wrapper = resolve_all_doc_ids(str(repo_dir))
    assert "ADR-001" in ids_wrapper
