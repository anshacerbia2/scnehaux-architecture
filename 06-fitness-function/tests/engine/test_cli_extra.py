import pytest
import sys

from engine.cli import _merge_reference_registry, _validate_execution_root, main


def test_merge_reference_registry_resolves_cross_repo_ids_and_duplicates():
    local = (
        {"TDD-service-001", "SAD-001"},
        {
            "TDD-service-001": {"_filepath": "docs/designs/TDD-service-001.md"},
            "SAD-001": {"_filepath": "docs/designs/SAD-001.md"},
        },
        {},
    )
    reference = (
        {"SAD-001", "PAD-PLT-001"},
        {
            "SAD-001": {"_filepath": "04-system/SAD-001.md"},
            "PAD-PLT-001": {"_filepath": "03-domain/PAD-PLT-001.md"},
        },
        {},
    )

    ids, metadata, duplicates = _merge_reference_registry(local, reference)

    assert ids == {"TDD-service-001", "SAD-001", "PAD-PLT-001"}
    assert metadata["PAD-PLT-001"]["_filepath"].startswith("03-domain")
    assert duplicates["SAD-001"] == [
        "04-system/SAD-001.md",
        "docs/designs/SAD-001.md",
    ]


def test_validate_execution_root_fails_without_git(tmp_path, monkeypatch):
    # tmp_path does not have a .git folder
    with pytest.raises(SystemExit) as exc_info:
        _validate_execution_root(str(tmp_path))
    assert exc_info.value.code == 1


def test_validate_execution_root_passes_with_git(tmp_path):
    # Create a fake .git directory
    (tmp_path / ".git").mkdir()
    # Should not raise SystemExit
    _validate_execution_root(str(tmp_path))
    assert True


def test_main_missing_global_config(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr("engine.cli._validate_execution_root", lambda x: None)
    monkeypatch.setattr("engine.cli.load_json_schema_file", lambda p: {})

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1


def test_main_missing_blocking_severities(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr("engine.cli._validate_execution_root", lambda x: None)
    monkeypatch.setattr(
        "engine.cli.load_json_schema_file",
        lambda p: {"x-global-config": {"severity_levels": {"mock": {"rule": "ERROR"}}}},
    )

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1


def test_main_invalid_severity_schema(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr("engine.cli._validate_execution_root", lambda x: None)
    monkeypatch.setattr(
        "engine.cli.load_json_schema_file",
        lambda p: {
            "x-global-config": {
                "severity_levels": {"mock": {"rule": "INVALID_SEV"}},
                "blocking_severities": ["CRITICAL"],
            }
        },
    )

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1


def test_main_break_glass(tmp_path, monkeypatch):

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()

    monkeypatch.setattr(
        sys, "argv", ["cli.py", "--break-glass", "--target", str(tmp_path)]
    )
    monkeypatch.setattr(
        "engine.cli.gather_markdown_paths",
        lambda *args, **kwargs: [str(tmp_path / "doc.md")],
    )

    # Mock lint_file returning a blocking error
    def mock_lint(*args, **kwargs):
        return (
            [("CRITICAL", "blocking error")],
            False,
            True,
            {
                "disabled": [("mock_rule", "reason", 10, 20)],
                "rejected": {"CRITICAL_RULE"},
            },
        )

    monkeypatch.setattr("engine.cli.lint_file", mock_lint)

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert (tmp_path / "break-glass-audit.log").exists()


def test_main_json_and_sarif_format(tmp_path, monkeypatch):

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()

    monkeypatch.setattr(
        "engine.cli.gather_markdown_paths",
        lambda *args, **kwargs: [str(tmp_path / "doc.md")],
    )

    def mock_lint(*args, **kwargs):
        return (
            [],
            True,
            False,
            {"disabled": {}, "rejected": set()},
        )

    monkeypatch.setattr("engine.cli.lint_file", mock_lint)

    # Test json format exit 0
    monkeypatch.setattr(
        sys, "argv", ["cli.py", "--format", "json", "--target", str(tmp_path)]
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0

    # Test sarif format exit 0
    monkeypatch.setattr(
        sys, "argv", ["cli.py", "--format", "sarif", "--target", str(tmp_path)]
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
