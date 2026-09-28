from datetime import date

from engine.auditors.authorization_auditor import (
    audit_replacement_lineage,
    audit_standard_authorization,
)

SEV = {"unauthorized_major_revision": "ERROR"}
LINEAGE_SEV = {"decision_lineage_violation": "ERROR"}
TODAY = date(2026, 9, 28)


def _std(status="proposed", version="2.0.0", authorized_by=None):
    meta = {"status": status, "version": version, "_filepath": "STD-X-001.md"}
    if authorized_by is not None:
        meta["authorized_by"] = authorized_by
    return meta


def _adr(status="proposed", authorizes=None):
    meta = {"status": status, "_filepath": "ADR-X-001.md"}
    if authorizes is not None:
        meta["authorizes"] = authorizes
    return meta


def _run(meta, legacy=None):
    return audit_standard_authorization(meta, SEV, legacy_entries=legacy, today=TODAY)


def test_proposed_std_with_proposed_adr_is_clean():
    meta = {
        "STD-X-001": _std(authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(authorizes=["STD-X-001"]),
    }
    assert _run(meta) == []


def test_major_revision_without_authorized_by_fails():
    findings = _run({"STD-X-001": _std(authorized_by=None)})
    assert len(findings) == 1
    assert findings[0][0] == "ERROR"
    assert "declares no 'authorized_by'" in findings[0][1]


def test_first_major_version_needs_no_authorization():
    assert _run({"STD-X-001": _std(version="1.4.0")}) == []


def test_unparseable_version_is_left_to_metadata_rules():
    assert _run({"STD-X-001": _std(version="draft")}) == []


def test_active_std_requires_accepted_adr_in_same_commit():
    meta = {
        "STD-X-001": _std(status="approved", authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(status="proposed", authorizes=["STD-X-001"]),
    }
    findings = _run(meta)
    assert len(findings) == 1
    assert (
        "holds authority only when every authorizing ADR is 'accepted'"
        in findings[0][1]
    )


def test_simultaneous_promotion_is_clean():
    meta = {
        "STD-X-001": _std(status="approved", authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(status="accepted", authorizes=["STD-X-001"]),
    }
    assert _run(meta) == []


def test_proposed_std_rejects_rejected_adr():
    meta = {
        "STD-X-001": _std(authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(status="rejected", authorizes=["STD-X-001"]),
    }
    findings = _run(meta)
    assert len(findings) == 1
    assert "'proposed' or 'accepted' ADR" in findings[0][1]


def test_deprecated_std_skips_status_and_presence_checks():
    meta = {
        "STD-X-001": _std(status="deprecated", authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(status="superseded", authorizes=["STD-X-001"]),
        "STD-X-002": _std(status="deprecated", version="3.0.0"),
    }
    assert _run(meta) == []


def test_unresolved_authorizer_fails():
    findings = _run({"STD-X-001": _std(authorized_by=["ADR-MISSING-001"])})
    assert len(findings) == 1
    assert "is not an ADR in this repository" in findings[0][1]


def test_non_adr_authorizer_fails():
    meta = {
        "STD-X-001": _std(authorized_by=["PAD-X-001"]),
        "PAD-X-001": {"status": "approved"},
    }
    findings = _run(meta)
    assert len(findings) == 1
    assert "is not an ADR in this repository" in findings[0][1]


def test_missing_backlink_on_adr_fails():
    meta = {
        "STD-X-001": _std(authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(authorizes=[]),
    }
    findings = _run(meta)
    assert len(findings) == 1
    assert "does not list STD 'STD-X-001' in 'authorizes'" in findings[0][1]


def test_adr_authorizing_std_that_does_not_point_back_fails():
    meta = {
        "STD-X-001": _std(version="1.0.0"),
        "ADR-X-001": _adr(authorizes=["STD-X-001"]),
    }
    findings = _run(meta)
    assert len(findings) == 1
    assert "does not name it in 'authorized_by'" in findings[0][1]


def test_adr_authorizing_unknown_std_fails():
    findings = _run({"ADR-X-001": _adr(authorizes=["STD-MISSING-001"])})
    assert len(findings) == 1
    assert "is not an STD in this repository" in findings[0][1]


def test_legacy_allowance_warns_until_expiry():
    legacy = [{"id": "STD-X-001", "expires": "2026-12-31", "reason": "predates field"}]
    findings = _run({"STD-X-001": _std(status="approved")}, legacy)
    assert len(findings) == 1
    assert findings[0][0] == "WARNING"
    assert "legacy debt until 2026-12-31: predates field" in findings[0][1]


def test_expired_legacy_allowance_fails():
    legacy = [{"id": "STD-X-001", "expires": "2026-09-01", "reason": "predates field"}]
    findings = _run({"STD-X-001": _std(status="approved")}, legacy)
    assert len(findings) == 1
    assert findings[0][0] == "ERROR"
    assert "expired on 2026-09-01" in findings[0][1]


def test_legacy_allowance_with_invalid_date_fails():
    legacy = [{"id": "STD-X-001", "expires": "soon"}]
    findings = _run({"STD-X-001": _std(status="approved")}, legacy)
    assert len(findings) == 1
    assert findings[0][0] == "ERROR"
    assert "no valid 'expires' date" in findings[0][1]


def test_obsolete_and_unknown_legacy_entries_warn():
    legacy = [
        {"id": "STD-X-001", "expires": "2026-12-31"},
        {"id": "STD-GONE-001", "expires": "2026-12-31"},
    ]
    meta = {
        "STD-X-001": _std(authorized_by=["ADR-X-001"]),
        "ADR-X-001": _adr(authorizes=["STD-X-001"]),
    }
    findings = _run(meta, legacy)
    assert len(findings) == 2
    assert all(sev == "WARNING" for sev, _, _ in findings)
    assert any("is obsolete" in msg for _, msg, _ in findings)
    assert any("does not match any STD" in msg for _, msg, _ in findings)


def test_registry_resolves_references_outside_the_lint_target():
    local = {"STD-X-001": _std(authorized_by=["ADR-X-001"])}
    registry = dict(local, **{"ADR-X-001": _adr(authorizes=["STD-X-001"])})
    assert (
        audit_standard_authorization(local, SEV, registry=registry, today=TODAY) == []
    )


def test_non_dict_metadata_and_default_date_are_tolerated():
    assert audit_standard_authorization({"STD-X-001": "not a dict"}, SEV) == []


def _replacement(status, supersedes):
    return {"adr_type": "replacement", "status": status, "supersedes": supersedes}


def _lineage(meta):
    return audit_replacement_lineage(meta, LINEAGE_SEV)


def test_proposed_replacement_keeps_original_accepted():
    meta = {
        "ADR-NEW-001": _replacement("proposed", ["ADR-OLD-001"]),
        "ADR-OLD-001": {"status": "accepted"},
    }
    assert _lineage(meta) == []


def test_proposed_replacement_rejects_early_supersession():
    meta = {
        "ADR-NEW-001": _replacement("proposed", ["ADR-OLD-001"]),
        "ADR-OLD-001": {"status": "superseded", "superseded_by": ["ADR-NEW-001"]},
    }
    findings = _lineage(meta)
    assert any("must stay 'accepted' until ratification" in m for _, m, _ in findings)
    assert any("must be an accepted replacement ADR" in m for _, m, _ in findings)


def test_ratified_replacement_is_clean():
    meta = {
        "ADR-NEW-001": _replacement("accepted", ["ADR-OLD-001"]),
        "ADR-OLD-001": {"status": "superseded", "superseded_by": ["ADR-NEW-001"]},
    }
    assert _lineage(meta) == []


def test_accepted_replacement_requires_superseded_original():
    meta = {
        "ADR-NEW-001": _replacement("accepted", ["ADR-OLD-001"]),
        "ADR-OLD-001": {"status": "accepted"},
    }
    findings = _lineage(meta)
    assert len(findings) == 1
    assert "must be 'superseded'" in findings[0][1]


def test_replacement_of_unknown_adr_fails():
    findings = _lineage({"ADR-NEW-001": _replacement("proposed", ["ADR-GONE-001"])})
    assert len(findings) == 1
    assert "is not an ADR in this repository" in findings[0][1]


def test_superseded_without_replacement_fails():
    findings = _lineage({"ADR-OLD-001": {"status": "superseded"}})
    assert len(findings) == 1
    assert "names no replacement" in findings[0][1]


def test_superseded_by_non_replacement_fails():
    meta = {
        "ADR-OLD-001": {"status": "superseded", "superseded_by": ["ADR-X-001"]},
        "ADR-X-001": {"adr_type": "foundational", "status": "accepted"},
    }
    findings = _lineage(meta)
    assert len(findings) == 1
    assert "must be an accepted replacement ADR" in findings[0][1]


def test_lineage_ignores_non_adr_and_non_dict():
    assert _lineage({"STD-X-001": {"status": "superseded"}, "ADR-Y-001": "bad"}) == []
