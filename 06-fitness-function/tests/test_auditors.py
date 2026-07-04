import pytest
from engine.auditors.graph_auditor import audit_hierarchy_tiers, audit_orphans
from engine.auditors.git_auditor import audit_version_bump

def test_audit_hierarchy_tiers():
    meta = {
        'TDD-001': {'parent_sad': 'PAD-001', '_filepath': 'TDD-001.md'},
        'SAD-001': {'parent_pad': 'EAD-001', '_filepath': 'SAD-001.md'},
        'PAD-001': {'governed_by': ['STD-001'], '_filepath': 'PAD-001.md'},
        'ADR-001': {'governed_by': ['SAD-001'], '_filepath': 'ADR-001.md'}
    }
    sev = {'structural_integrity_violation': 'CRITICAL'}
    findings = audit_hierarchy_tiers(meta, sev)
    
    assert len(findings) == 4
    assert any("TDD 'TDD-001' must attach to a SAD" in msg for sev, msg, f in findings)
    assert any("SAD 'SAD-001' must attach to a PAD" in msg for sev, msg, f in findings)
    assert any("PAD 'PAD-001' must attach to an EAD" in msg for sev, msg, f in findings)
    assert any("ADR 'ADR-001' cannot attach to 'SAD-001'" in msg for sev, msg, f in findings)

def test_audit_orphans():
    meta = {
        'TDD-002': {'_filepath': 'TDD-002.md'},
        'SAD-002': {'_filepath': 'SAD-002.md'},
        'PAD-002': {'_filepath': 'PAD-002.md'},
    }
    sev = {'traceability_violation': 'ERROR'}
    findings = audit_orphans(meta, sev)
    
    assert len(findings) == 3
    assert any("TDD 'TDD-002' must declare a 'parent_sad'" in msg for sev, msg, f in findings)
    assert any("SAD 'SAD-002' must declare a 'parent_pad'" in msg for sev, msg, f in findings)
    assert any("PAD 'PAD-002' must declare 'governed_by'" in msg for sev, msg, f in findings)

def test_audit_version_bump(monkeypatch):
    import subprocess
    
    class MockProcess:
        def __init__(self, stdout, returncode):
            self.stdout = stdout
            self.returncode = returncode
            
    def mock_run(cmd, *args, **kwargs):
        if "rev-parse" in cmd:
            return MockProcess("/repo", 0)
        if "show" in cmd:
            content = "---\ndoc_meta:\n  status: approved\n  version: 1.0.0\n---\nOld Content"
            return MockProcess(content, 0)
        return MockProcess("", 1)
        
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    # Mock open
    import builtins
    from unittest.mock import mock_open
    m = mock_open(read_data="New Content")
    monkeypatch.setattr(builtins, "open", m)
    
    # Mock os.path.exists
    import os
    monkeypatch.setattr(os.path, "exists", lambda x: True)
    
    meta = {
        'ADR-100': {
            'status': 'approved',
            'version': '1.0.0',
            '_filepath': '/repo/ADR-100.md'
        }
    }
    
    sev = {'structural_integrity_violation': 'CRITICAL'}
    findings = audit_version_bump(meta, sev)
    
    assert len(findings) == 1
    assert "Version bump required" in findings[0][1]
