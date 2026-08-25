import os
import subprocess
import builtins
from unittest.mock import mock_open
from engine.auditors.git_auditor import audit_version_bump, _resolve_base_ref


from engine.config.severity import SeverityRule


def test_audit_version_bump_and_resolve_ref(monkeypatch):
    class MockProcess:
        def __init__(self, stdout, returncode):
            self.stdout = stdout
            self.returncode = returncode

    # Mock os.environ to test SCNEHAUX_BASE_REF
    monkeypatch.setattr(os, "environ", {"SCNEHAUX_BASE_REF": "env_ref"})

    def mock_run(cmd, *args, **kwargs):
        cmd_str = " ".join(cmd)
        if "rev-parse --verify --quiet env_ref^{commit}" in cmd_str:
            return MockProcess("hash1", 0)
        if "rev-parse --show-toplevel" in cmd_str:
            return MockProcess("/repo", 0)
        if "show" in cmd_str:
            if "ADR-NEW" in cmd_str:
                return MockProcess("", 1)  # file not in git
            if "ADR-NO-META" in cmd_str:
                return MockProcess("just text", 0)
            if "ADR-DRAFT" in cmd_str:
                content = "---\ndoc_meta:\n  status: draft\n  version: 1.0.0\n---\nOld Content"
                return MockProcess(content, 0)
            if "ADR-NO-VERSION" in cmd_str:
                content = "---\ndoc_meta:\n  status: approved\n---\nOld Content"
                return MockProcess(content, 0)
            content = (
                "---\ndoc_meta:\n  status: approved\n  version: 1.0.0\n---\nOld Content"
            )
            return MockProcess(content, 0)
        return MockProcess("", 1)

    monkeypatch.setattr(subprocess, "run", mock_run)

    # Mock open
    m = mock_open(read_data="New Content")
    monkeypatch.setattr(builtins, "open", m)

    # Mock os.path.exists
    monkeypatch.setattr(os.path, "exists", lambda x: True)

    # Test cases:
    # 1. Not a dict
    # 2. Not approved status
    # 3. Missing filepath
    # 4. File new in git (returns code != 0 for show)
    # 5. Old meta None
    # 6. Old status not approved
    # 7. Old or new version missing
    # 8. Version bump not incremented
    # 9. Exception during audit

    meta = {
        "ADR-NOT-DICT": "string",
        "ADR-DRAFT-NEW": {
            "status": "draft",
            "version": "1.0.0",
            "_filepath": "/repo/a.md",
        },
        "ADR-NO-FILE": {"status": "approved", "version": "1.0.0"},
        "ADR-NEW": {
            "status": "approved",
            "version": "1.0.0",
            "_filepath": "/repo/ADR-NEW.md",
        },
        "ADR-NO-META": {
            "status": "approved",
            "version": "1.0.0",
            "_filepath": "/repo/ADR-NO-META.md",
        },
        "ADR-DRAFT": {
            "status": "approved",
            "version": "1.0.0",
            "_filepath": "/repo/ADR-DRAFT.md",
        },
        "ADR-NO-VERSION": {
            "status": "approved",
            "_filepath": "/repo/ADR-NO-VERSION.md",
        },
        "ADR-BUMP-FAIL": {
            "status": "approved",
            "version": "1.0.0",
            "_filepath": "/repo/ADR-BUMP-FAIL.md",
        },
        "ADR-CRASH": {
            "status": "approved",
            "version": "1.0.0",
            "_filepath": "/repo/ADR-CRASH.md",
        },
    }

    # Crash on the last one by making abspath throw
    orig_abspath = os.path.abspath

    def mock_abspath(p):
        if "CRASH" in p:
            raise ValueError("mock crash")
        return orig_abspath(p)

    monkeypatch.setattr(os.path, "abspath", mock_abspath)
    monkeypatch.setattr(os.path, "relpath", lambda path, start: os.path.basename(path))

    sev = {r: "CRITICAL" for r in SeverityRule}
    findings = audit_version_bump(meta, sev)

    # Version bump check disabled per user directive
    assert len(findings) == 0

    # Test fallback to HEAD when subprocess fails
    def mock_run_fail(cmd, *args, **kwargs):
        raise ValueError("git not found")

    monkeypatch.setattr(subprocess, "run", mock_run_fail)
    assert _resolve_base_ref("/repo") == "HEAD"

    # Test no git repo
    assert len(audit_version_bump(meta, sev)) == 0
