import pytest
import os
import sys
from pathlib import Path

from engine.cli import _validate_execution_root, main

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
    import sys
    from engine.cli import main
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr("engine.cli._validate_execution_root", lambda x: None)
    monkeypatch.setattr("engine.cli.load_json_schema_file", lambda p: {})
    
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1

def test_main_missing_blocking_severities(monkeypatch):
    import sys
    from engine.cli import main
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr("engine.cli._validate_execution_root", lambda x: None)
    monkeypatch.setattr("engine.cli.load_json_schema_file", lambda p: {
        "x-global-config": {
            "severity_levels": {"mock": {"rule": "ERROR"}}
        }
    })
    
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1

def test_main_invalid_severity_schema(monkeypatch):
    import sys
    from engine.cli import main
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr("engine.cli._validate_execution_root", lambda x: None)
    monkeypatch.setattr("engine.cli.load_json_schema_file", lambda p: {
        "x-global-config": {
            "severity_levels": {"mock": {"rule": "INVALID_SEV"}},
            "blocking_severities": ["CRITICAL"]
        }
    })
    
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
