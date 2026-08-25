from engine.auditors.graph_auditor import (
    audit_hierarchy_tiers,
    audit_orphans,
    audit_traceability_graph,
)


def test_audit_hierarchy_tiers():
    meta = {
        "TDD-001": {"parent_sad": "PAD-001", "_filepath": "TDD-001.md"},
        "SAD-001": {"parent_pad": "EAD-001", "_filepath": "SAD-001.md"},
        "PAD-001": {"governed_by": ["STD-001"], "_filepath": "PAD-001.md"},
        "ADR-001": {"governed_by": ["SAD-001"], "_filepath": "ADR-001.md"},
    }
    sev = {"structural_integrity_violation": "CRITICAL"}
    findings = audit_hierarchy_tiers(meta, sev)

    assert len(findings) == 4
    assert any("TDD 'TDD-001' must attach to a SAD" in msg for sev, msg, f in findings)
    assert any("SAD 'SAD-001' must attach to a PAD" in msg for sev, msg, f in findings)
    assert any("PAD 'PAD-001' must attach to an EAD" in msg for sev, msg, f in findings)
    assert any(
        "ADR 'ADR-001' cannot attach to 'SAD-001'" in msg for sev, msg, f in findings
    )


def test_audit_orphans():
    meta = {
        "TDD-002": {"_filepath": "TDD-002.md"},
        "SAD-002": {"_filepath": "SAD-002.md"},
        "PAD-002": {"_filepath": "PAD-002.md"},
    }
    sev = {"traceability_violation": "ERROR"}
    findings = audit_orphans(meta, sev)

    assert len(findings) == 3
    assert any(
        "TDD 'TDD-002' must declare a 'parent_sad'" in msg for sev, msg, f in findings
    )
    assert any(
        "SAD 'SAD-002' must declare a 'parent_pad'" in msg for sev, msg, f in findings
    )
    assert any(
        "PAD 'PAD-002' must declare 'governed_by'" in msg for sev, msg, f in findings
    )


def test_audit_hierarchy_tiers_accepts_multiple_sad_parents():
    meta = {
        "TDD-foundation-001": {
            "parent_sad": ["SAD-001", "SAD-004"],
            "_filepath": "docs/designs/TDD-foundation-001.md",
        }
    }
    sev = {"structural_integrity_violation": "CRITICAL"}

    assert audit_hierarchy_tiers(meta, sev) == []


def test_audit_traceability_graph_cycle_detected():
    meta = {
        "SAD-001": {"parent_pad": "PAD-001"},
        "PAD-001": {"governed_by": "SAD-001"},
    }
    errs = audit_traceability_graph(meta)
    assert any("Circular" in m for _, m in errs)


def test_audit_traceability_graph_self_reference():
    meta = {"GDC-000": {"governed_by": ["GDC-000"]}}
    assert audit_traceability_graph(meta) == []


def test_audit_traceability_graph_acyclic_clean():
    meta = {
        "SAD-001": {"parent_pad": "PAD-001"},
        "PAD-001": {"governed_by": "EAD-001"},
        "EAD-001": {},
    }
    assert audit_traceability_graph(meta) == []


def test_audit_hierarchy_and_orphans_non_dict():
    meta = {"INVALID_KEY": "not_a_dict_metadata"}
    sev = {
        "structural_integrity_violation": "CRITICAL",
        "traceability_violation": "ERROR",
    }
    assert audit_hierarchy_tiers(meta, sev) == []
    assert audit_orphans(meta, sev) == []
