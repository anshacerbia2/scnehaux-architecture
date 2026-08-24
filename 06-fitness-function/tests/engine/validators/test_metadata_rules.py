from tests.conftest import make_validator
from engine.validators.metadata_rules import (
    _validate_review_age,
    _validate_approved_version_stability,
    _validate_cross_references,
    _validate_technologies_whitelist,
    validate_exempt_age,
)
from engine.config.severity import SeverityRule
import datetime


def test_validate_review_age():
    rules = {"rules": {}, "severity_levels": {}}
    v = make_validator(
        doc_meta={"last_reviewed": "2000-01-01", "review_cycle_days": 365}, rules=rules
    )
    _validate_review_age(v)
    assert len(v.errors) == 1
    assert v.errors[0][0] == "WARNING"


def test_review_age_no_meta():
    v = make_validator(doc_meta={})
    _validate_review_age(v)
    assert len(v.errors) == 0


def test_baseline_status_at_major_version_zero_is_refused():
    """GDC-000 Section 2.6 item 6, in both baseline-bearing statuses.

    An artifact cannot be the blueprint other teams build against while carrying the version
    Semantic Versioning reserves for "anything may change at any time".
    """
    rules = {"rules": {}, "severity_levels": {}}

    for status in ("approved", "deprecated"):
        v = make_validator(doc_meta={"status": status, "version": "0.4.0"}, rules=rules)
        _validate_approved_version_stability(v)
        assert len(v.errors) == 1, f"{status} at 0.4.0 was accepted"
        assert "major version zero" in v.errors[0][1]


def test_pre_baseline_statuses_may_sit_at_major_version_zero():
    """The other half of the rule, and the half that makes it a rule rather than a ban.

    `0.y.z` is exactly the right version for an artifact that is recognized or under review
    and not yet a baseline. A check that flagged those too would push every chartered SAD to
    1.0.0 and destroy the signal it is trying to protect.
    """
    rules = {"rules": {}, "severity_levels": {}}

    for status in ("chartered", "draft", "proposed"):
        v = make_validator(doc_meta={"status": status, "version": "0.1.0"}, rules=rules)
        _validate_approved_version_stability(v)
        assert len(v.errors) == 0, f"{status} at 0.1.0 was refused"


def test_stable_versions_and_unversioned_artifacts_pass():
    rules = {"rules": {}, "severity_levels": {}}

    v = make_validator(doc_meta={"status": "approved", "version": "1.0.0"}, rules=rules)
    _validate_approved_version_stability(v)
    assert len(v.errors) == 0

    # A ten-major-version artifact must not be caught by a naive "starts with 0" test.
    v = make_validator(doc_meta={"status": "approved", "version": "10.2.3"}, rules=rules)
    _validate_approved_version_stability(v)
    assert len(v.errors) == 0

    # ADRs are immutable snapshots rather than versioned artifacts per GDC-000 Section 2.6
    # item 4, so an approved one carries no version and there is nothing to check.
    v = make_validator(doc_meta={"status": "approved"}, rules=rules)
    _validate_approved_version_stability(v)
    assert len(v.errors) == 0


def test_version_stability_no_meta():
    v = make_validator(doc_meta={})
    _validate_approved_version_stability(v)
    assert len(v.errors) == 0


def test_validate_cross_references():
    rules = {"rules": {}, "severity_levels": {}}
    # Test invalid cross reference IDs
    v2 = make_validator(
        doc_meta={
            "status": "draft",
            "parent_pad": "PAD-999",
            "governed_by": ["GDC-999"],
        },
        rules=rules,
        all_doc_ids={"PAD-001"},
    )
    _validate_cross_references(v2)
    assert any("not found in this repository" in e[1] for e in v2.errors)

    # Test valid
    v3 = make_validator(
        doc_meta={"status": "draft", "parent_pad": "PAD-001", "governed_by": "GDC-002"},
        rules=rules,
        all_doc_ids={"PAD-001", "GDC-002"},
    )
    _validate_cross_references(v3)
    assert len(v3.errors) == 0


def test_cross_references_no_meta():
    v = make_validator(doc_meta={})
    _validate_cross_references(v)
    assert len(v.errors) == 0


def test_validate_exempt_age():
    global_rules = {
        "content_rules": {
            "exempt_statuses": [
                {
                    "status": "draft",
                    "depend_on": "created_date",
                    "max_age_days": 30,
                    "error_message": "Document with status '{doc_status}' has an age of {age_days} days (since {depend_on}), exceeding limit of {limit} days."
                }
            ]
        },
        "severity_levels": {SeverityRule.DRAFT_STATUS_VIOLATION: "WARNING"}
    }
    
    # Missing created_date
    errs = validate_exempt_age({}, "draft", "WARNING", global_rules)
    assert len(errs) == 1
    assert "missing 'created_date'" in errs[0][1]

    # Exceeds max draft age
    old_date = (datetime.date.today() - datetime.timedelta(days=35)).isoformat()
    errs2 = validate_exempt_age({"created_date": old_date}, "draft", "WARNING", global_rules)
    assert len(errs2) == 1
    assert "exceeding limit of 30 days" in errs2[0][1]

    # Within max draft age
    fresh_date = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
    errs3 = validate_exempt_age({"created_date": fresh_date}, "draft", "WARNING", global_rules)
    assert len(errs3) == 0


def test_validate_exempt_age_missing_config():
    global_rules = {"content_rules": {}}
    fresh_date = datetime.date.today().isoformat()
    # Missing config gracefully returns empty list (no validation performed)
    errs = validate_exempt_age({"created_date": fresh_date}, "draft", "WARNING", global_rules)
    assert len(errs) == 0


def test_validate_technologies_whitelist():
    rules = {
        "severity_levels": {
            "technology_hold_violation": "CRITICAL",
            "unapproved_technology": "ERROR",
        }
    }
    
    # 1. No doc_meta / no technologies
    v1 = make_validator(doc_meta={}, rules=rules)
    v1.doc_type_name = "SAD"
    _validate_technologies_whitelist(v1)
    assert len(v1.errors) == 0

    # 2. Technologies whitelist check with tech on hold and unapproved tech
    v2 = make_validator(
        doc_meta={
            "technologies": [
                {"name": "UnknownTechName123"},
                "invalid_non_dict_tech",
            ]
        },
        rules=rules,
    )
    v2.doc_type_name = "SAD"
    _validate_technologies_whitelist(v2)
    assert len(v2.errors) >= 1
    assert any("not defined in the Enterprise Tech Radar" in e[1] for e in v2.errors)


    # 3. Technologies whitelist check with 'base' property
    v3 = make_validator(
        doc_meta={
            "technologies": [
                {"name": "postgresql", "base": "jquery"}  # jquery is on HOLD in tech-radar
            ]
        },
        rules=rules,
    )
    v3.doc_type_name = "SAD"
    _validate_technologies_whitelist(v3)
    assert any("technology on HOLD" in e[1] for e in v3.errors)


def test_validate_technologies_whitelist_missing_tech_radar(monkeypatch, tmp_path):
    rules = {
        "severity_levels": {
            "technology_hold_violation": "CRITICAL",
            "unapproved_technology": "ERROR",
        }
    }
    v = make_validator(doc_meta={"technologies": [{"name": "postgresql"}]}, rules=rules)
    v.doc_type_name = "SAD"

    # Mock os.path.exists to return False for tech_radar_path (line 140)
    monkeypatch.setattr("os.path.exists", lambda path: False)
    _validate_technologies_whitelist(v)
    assert len(v.errors) == 0




