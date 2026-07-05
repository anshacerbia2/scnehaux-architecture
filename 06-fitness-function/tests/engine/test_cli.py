import datetime
import pytest
import os
import sys
import importlib.util
from engine.cli import print_errors, lint_file, build_sarif, SCRIPT_DIR


def _write_md(
    tmp_path,
    filename,
    frontmatter_yaml,
    body="## Context & Scope\nThis is the context.",
):
    content = f"---\n{frontmatter_yaml}\n---\n{body}"
    fpath = tmp_path / filename
    fpath.write_text(content, encoding="utf-8")
    return str(fpath)


def _global_rules():
    from engine.cli import load_schema

    path = os.path.join(SCRIPT_DIR, "00-governance", "schemas", "base.schema.json")
    return load_schema(path).get("x-engine-config", {})


def test_print_errors():
    errors = [("ERROR", "Bad thing"), ("WARNING", "Not so bad")]
    errs, is_clean, has_blocking = print_errors("file.md", errors, "text")
    assert not is_clean
    assert has_blocking

    errs2, is_clean2, has_blocking2 = print_errors(
        "file.md", [("WARNING", "Only warning")], "text"
    )
    assert not is_clean2
    assert not has_blocking2

    errs3, is_clean3, has_blocking3 = print_errors("file.md", [], "text")
    assert is_clean3
    assert not has_blocking3


def test_print_errors_json_format():
    """JSON format returns without printing, preserving error data."""
    errors = [("ERROR", "Bad thing")]
    errs, is_clean, has_blocking = print_errors("file.md", errors, "json")
    assert errs == errors
    assert not is_clean
    assert has_blocking

    # No errors in JSON mode
    errs2, is_clean2, has_blocking2 = print_errors("file.md", [], "json")
    assert is_clean2
    assert not has_blocking2


def test_lint_file_draft_skip(tmp_path):
    """A fresh draft (within max_draft_age_days) should be skipped, not fail."""
    today = datetime.date.today().isoformat()
    fm = f"doc_meta:\n  id: SAD-TEST-001\n  status: draft\n  last_reviewed: {today}"
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "text")
    assert is_clean is True
    assert has_blocking is False
    assert errs == []


def test_lint_file_draft_expired(tmp_path):
    """A draft older than max_draft_age_days must produce a blocking ERROR."""
    old_date = (datetime.date.today() - datetime.timedelta(days=999)).isoformat()
    fm = f"doc_meta:\n  id: SAD-TEST-001\n  status: draft\n  last_reviewed: {old_date}"
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "text")
    assert has_blocking is True
    assert any("exceeds limit" in msg for _, msg in errs)


def test_lint_file_draft_missing_last_reviewed(tmp_path):
    """A draft without last_reviewed must produce a blocking ERROR."""
    fm = "doc_meta:\n  id: SAD-TEST-001\n  status: draft"
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "text")
    assert has_blocking is True
    assert any("missing 'last_reviewed'" in msg for _, msg in errs)


# ---------- lint_file Error Path Tests ----------


def test_lint_file_unknown_doc_type(tmp_path):
    """File with an unrecognized ID prefix must produce a blocking ERROR."""
    fm = "doc_meta:\n  id: ZZZ-999"
    fpath = _write_md(tmp_path, "ZZZ-999.md", fm)

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "text")
    assert has_blocking is True
    assert any("Unknown doc type" in msg for _, msg in errs)


def test_lint_file_missing_frontmatter(tmp_path):
    """File without YAML frontmatter must produce a blocking ERROR."""
    fpath = tmp_path / "test.md"
    fpath.write_text("# No frontmatter here", encoding="utf-8")

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(str(fpath), rules, set(), {}, "text")
    assert has_blocking is True
    assert any("frontmatter" in msg.lower() for _, msg in errs)


def test_lint_file_read_error(tmp_path):
    """Non-existent file must produce a blocking ERROR (not crash)."""
    fpath = str(tmp_path / "nonexistent.md")

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "text")
    assert has_blocking is True
    assert any("Failed to read file" in msg for _, msg in errs)


def test_lint_file_json_format(tmp_path):
    """JSON format should return errors without printing."""
    fm = "doc_meta:\n  id: ZZZ-999"
    fpath = _write_md(tmp_path, "ZZZ-999.md", fm)

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "json")
    assert isinstance(errs, list)
    assert has_blocking is True


# ---------- Coverage Tests for cli.py ----------


def test_load_schema_file_not_found():
    from engine.cli import load_schema

    with pytest.raises(SystemExit) as e:
        load_schema("non_existent.json")
    assert e.value.code == 1


def test_lint_file_missing_specific_rules(tmp_path, monkeypatch):
    """File that resolves to a type without its corresponding specific rules YAML."""
    # We will temporarily remove the specific rules file for this test
    fm = "doc_meta:\n  id: SAD-TEST-001"
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    # Mock os.path.exists so it returns False ONLY for the specific schema file
    original_exists = os.path.exists

    def mock_exists(path):
        if "sad.schema.json" in path:
            return False
        return original_exists(path)

    monkeypatch.setattr(os.path, "exists", mock_exists)

    rules = _global_rules()
    errs, is_clean, has_blocking, di = lint_file(fpath, rules, set(), {}, "text")
    assert has_blocking is True
    assert any("Missing mandatory domain-specific schema" in msg for _, msg in errs)


def test_main_clean_run(tmp_path, monkeypatch):
    """main() should exit 0 when all files are clean."""
    fm = (
        "doc_meta:\n  id: SAD-TEST-001\n  parent_pad: PAD-TEST-001\n  status: draft\n  last_reviewed: "
        + datetime.date.today().isoformat()
    )
    _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    monkeypatch.setattr(sys, "argv", ["cli.py", "--target", str(tmp_path)])

    import engine.cli as linter

    def mock_lint_file(*args, **kwargs):
        return [], True, False, {}

    def mock_resolve(*args, **kwargs):
        return (
            {"SAD-TEST-001"},
            {
                "SAD-TEST-001": {
                    "parent_pad": "PAD-TEST-001",
                    "_filepath": "SAD-TEST-001.sad.md",
                }
            },
            {},
        )

    monkeypatch.setattr(linter, "lint_file", mock_lint_file)
    monkeypatch.setattr(linter, "resolve_registry_with_duplicates", mock_resolve)

    with pytest.raises(SystemExit) as e:
        linter.main()
    assert e.value.code == 0


def test_main_failing_run(tmp_path, monkeypatch):
    """main() should exit 1 when there are blocking errors."""
    fm = "doc_meta:\n  id: SAD-TEST-001"  # Missing required metadata
    _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    monkeypatch.setattr(sys, "argv", ["cli.py", "--target", str(tmp_path)])

    with pytest.raises(SystemExit) as e:
        import engine.cli as linter

        linter.main()
    assert e.value.code == 1


def test_main_json_format(tmp_path, monkeypatch):
    """main() in JSON format."""
    fm = "doc_meta:\n  id: SAD-TEST-001"
    _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    monkeypatch.setattr(
        sys, "argv", ["cli.py", "--target", str(tmp_path), "--format", "json"]
    )

    with pytest.raises(SystemExit) as e:
        import engine.cli as linter

        linter.main()
    assert e.value.code == 1


def test_main_sarif_format(tmp_path, monkeypatch):
    """main() in SARIF format."""
    fm = "doc_meta:\n  id: SAD-TEST-001"
    _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)

    monkeypatch.setattr(
        sys, "argv", ["cli.py", "--target", str(tmp_path), "--format", "sarif"]
    )

    with pytest.raises(SystemExit) as e:
        import engine.cli as linter

        linter.main()
    assert e.value.code == 1


def test_main_with_lint_disable_and_duplicates(tmp_path, monkeypatch):
    """Cover cli.py printing blocks for lint_disable, rejected disables, and duplicate IDs."""
    fm1 = (
        "doc_meta:\n  id: SAD-TEST-001\n  parent_pad: PAD-001\n  status: draft\n  last_reviewed: "
        + datetime.date.today().isoformat()
    )
    content1 = (
        "---\n"
        + fm1
        + "\n---\n<!-- lint_disable: structural_integrity_violation -->\n## Context"
    )
    fpath1 = tmp_path / "SAD-TEST-001.sad.md"
    fpath1.write_text(content1, encoding="utf-8")

    # Duplicate ID to trigger duplicate check
    fm2 = (
        "doc_meta:\n  id: SAD-TEST-001\n  parent_pad: PAD-001\n  status: draft\n  last_reviewed: "
        + datetime.date.today().isoformat()
    )
    content2 = (
        "---\n"
        + fm2
        + "\n---\n<!-- lint_disable: structural_integrity_violation (reason: ARB waiver) -->\n## Context"
    )
    fpath2 = tmp_path / "SAD-TEST-001-dupe.sad.md"
    fpath2.write_text(content2, encoding="utf-8")

    # Add --verbose to cover the verbose block too
    monkeypatch.setattr(sys, "argv", ["cli.py", "--target", str(tmp_path), "--verbose"])

    import engine.cli as linter

    def mock_resolve(*args):
        # Force a duplicate ID to ensure line 278 is hit
        return (
            {"SAD-TEST-001"},
            {"SAD-TEST-001": {}},
            {"SAD-TEST-001": ["file1.md", "file2.md"]},
        )

    monkeypatch.setattr(linter, "resolve_registry_with_duplicates", mock_resolve)

    with pytest.raises(SystemExit) as e:
        linter.main()

    # SAD-TEST-001 duplicate will trigger an ERROR and thus exit 1
    assert e.value.code == 1


def test_build_sarif_maps_levels():
    results = [
        {
            "file": "./a.md",
            "errors": [("CRITICAL", "c"), ("ERROR", "e"), ("WARNING", "w")],
        }
    ]
    doc = build_sarif(results)
    assert doc["version"] == "2.1.0"
    levels = [r["level"] for r in doc["runs"][0]["results"]]
    assert levels.count("error") == 2 and levels.count("warning") == 1
    assert (
        doc["runs"][0]["results"][0]["locations"][0]["physicalLocation"][
            "artifactLocation"
        ]["uri"]
        == "a.md"
    )


def test_build_sarif_empty_results():
    doc = build_sarif([])
    assert doc["version"] == "2.1.0"
    assert doc["runs"][0]["results"] == []


# ---------- FIX#4: non-destructive generator --check ----------


def _load_generator():
    gen_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "generators", "generate_rules_doc.py"
        )
    )
    spec = importlib.util.spec_from_file_location("genrules", gen_path)
    assert spec is not None and spec.loader is not None, "Failed to load spec"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_generator_check_non_destructive():
    gen = _load_generator()
    drift = gen.process(check=True)
    assert isinstance(drift, list)  # returns drift records, writes nothing


def test_lint_file_no_validator(tmp_path, monkeypatch):
    import engine.cli as linter

    fm = "doc_meta:\n  id: SAD-TEST-001"
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)
    monkeypatch.setattr(linter, "get_validator", lambda x: None)
    rules = _global_rules()
    errs, p, b, di = linter.lint_file(fpath, rules, set(), {}, "text")
    assert any("No validator implemented" in msg for _, msg in errs)


def test_main_with_file_target(tmp_path, monkeypatch):
    import sys
    from engine.cli import main

    fm = (
        "doc_meta:\n  id: SAD-TEST-001\n  parent_pad: PAD-TEST-001\n  status: draft\n  last_reviewed: "
        + datetime.date.today().isoformat()
    )
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm)
    monkeypatch.setattr(sys, "argv", ["cli.py", "--target", str(fpath)])

    # Also test stream reconfigure exception coverage
    class FakeStream:
        def reconfigure(self, **kwargs):
            raise AttributeError("mocked")

        def write(self, msg):
            pass

        def flush(self):
            pass

    monkeypatch.setattr(sys, "stdout", FakeStream())

    try:
        main()
    except SystemExit as e:
        assert e.code == 1


def test_lint_file_with_disables_and_warnings(tmp_path):
    fm = "doc_meta:\n  id: SAD-TEST-001\n  parent_pad: PAD-TEST-001\n  status: active"
    body = "<!-- lint_disable: rule1 -->\n<!-- lint_disable: rule2 (reason: reason) -->\n<!-- lint_disable: structural_integrity_violation -->"
    fpath = _write_md(tmp_path, "SAD-TEST-001.sad.md", fm, body)
    from engine.cli import lint_file

    rules = _global_rules()
    errs, p, b, di = lint_file(fpath, rules, set(), {}, "text")
    assert "rule1" in di["disabled"]
    assert not di["disabled"]["rule1"]  # no reason
    assert di["disabled"]["rule2"] == "reason"
