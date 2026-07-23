from tests.conftest import make_validator
from engine.validators.metadata_rules import (
    _validate_review_age,
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
    assert v.errors[0][0] == "ERROR"


def test_review_age_no_meta():
    v = make_validator(doc_meta={})
    _validate_review_age(v)
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
            "max_draft_age_days": {
                "value": 30,
                "error_message": "Document with status '{doc_status}' has an age of {age_days} days, exceeding limit of {limit} days. Must be reviewed, finalized, or deleted."
            }
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
