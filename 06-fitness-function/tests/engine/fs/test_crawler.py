import pytest
from unittest.mock import patch
from engine.fs.crawler import build_metadata_registry, gather_markdown_files


def test_build_metadata_registry_basic(tmp_path):
    """
    Validates the basic metadata extraction flow from Markdown files.
    Ensures that YAML frontmatter is parsed correctly to build a registry,
    and explicitly verifies that exclusions like 'node_modules' are enforced.
    """
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

    ids, registry, dupes = build_metadata_registry(str(repo_dir))

    assert "ADR-001" in ids
    assert "ADR-002" not in ids
    assert not dupes
    assert registry["ADR-001"]["id"] == "ADR-001"


def test_duplicate_id_detection(tmp_path):
    """
    Validates the Single Source of Truth (SSOT) invariant mechanism.
    Ensures that if multiple Markdown files declare the same architecture ID,
    they are correctly flagged and captured in the duplicates registry.
    """
    d = tmp_path / "repo"
    d.mkdir()
    (d / "a.md").write_text("---\ndoc_meta:\n  id: ADR-001\n---\nA")
    (d / "b.md").write_text("---\ndoc_meta:\n  id: ADR-001\n---\nB")
    (d / "c.md").write_text("---\ndoc_meta:\n  id: ADR-002\n---\nC")
    ids, meta, dupes = build_metadata_registry(str(d))
    assert "ADR-001" in dupes and len(dupes["ADR-001"]) == 2
    assert "ADR-002" not in dupes
    assert "ADR-002" in ids


def test_gather_markdown_files_valueerror_relpath():
    """
    Validates the security mechanism handling cross-drive path traversals.
    Ensures that when os.path.relpath throws a ValueError due to mismatched drives
    (e.g., on Windows), the system performs a Fail-Closed hard crash (SystemExit).
    """
    with patch("os.path.relpath", side_effect=ValueError):
        with pytest.raises(SystemExit):
            gather_markdown_files(
                "C:\\some\\file.md", "D:\\repo", allowed_root_dirs={"allowed"}
            )


def test_gather_markdown_files_target_str():
    """
    Validates the type coercion mechanism for the target_dirs argument.
    Ensures that passing a single string path is correctly converted into a list
    before path evaluation continues.
    """
    # Pass a non-existent file just to trigger the string-to-list conversion
    files = gather_markdown_files("some_target.md", "repo_root")
    assert isinstance(files, list)


def test_gather_markdown_files_skipped_targets(tmp_path):
    """
    Validates strict boundary enforcement against unauthorized internal directories.
    Ensures that targets not explicitly present in the allowed_root_dirs list
    trigger a Fail-Closed hard crash (SystemExit).
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    allowed = repo / "allowed_dir"
    allowed.mkdir()
    (allowed / "file1.md").write_text("# Allowed")

    disallowed = repo / "disallowed_dir"
    disallowed.mkdir()
    (disallowed / "file2.md").write_text("# Disallowed")

    with pytest.raises(SystemExit):
        gather_markdown_files(
            [str(allowed), str(disallowed)],
            repo_root=str(repo),
            allowed_root_dirs={"allowed_dir"},
        )


def test_gather_markdown_files_outside_repo(tmp_path):
    """
    Validates boundary enforcement against external path traversal attacks.
    Ensures that targets located outside the designated repo_root boundary
    (e.g., ../) trigger a Fail-Closed hard crash (SystemExit).
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    outside = tmp_path / "outside_dir"
    outside.mkdir()
    (outside / "file.md").write_text("# Outside")

    with pytest.raises(SystemExit):
        gather_markdown_files(
            [str(outside)], repo_root=str(repo), allowed_root_dirs={"allowed"}
        )


def test_crawler_handles_exception_during_read():
    """
    Validates graceful error handling during file read operations.
    Ensures that if a PermissionError occurs while extracting metadata,
    it safely bypasses the unreadable file without crashing the crawler.
    """
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [("some_dir", [], ["test.md"])]
        with patch(
            "builtins.open", side_effect=PermissionError("Mocked Permission Error")
        ):
            ids, metadata, duplicates = build_metadata_registry("some_dir", "some_dir")
            assert len(ids) == 0
            assert len(metadata) == 0
            assert len(duplicates) == 0
