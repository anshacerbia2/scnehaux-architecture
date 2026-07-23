from engine.validators.schema_extensions import (
    _get_concept_pattern,
    _validate_required_subsections,
    _validate_prohibited_keywords,
    _validate_recommended,
)


def test_get_concept_pattern():
    pattern = _get_concept_pattern("Security")
    assert pattern.search("### Security")
    assert pattern.search("#### Security")
    assert pattern.search("**Security**")
    assert pattern.search("- **Security**")
    assert not pattern.search("Insecurity")


def test_validate_required_subsections():
    # It yields ValidationError if missing
    errs = list(
        _validate_required_subsections(None, ["Security"], "### Performance\nFast", {})
    )
    assert len(errs) == 1
    assert "Missing required subsection 'Security'" in errs[0].message
    assert errs[0].validator == "required_subsections"
    assert errs[0].validator_value == "Security"

    # It yields nothing if present
    errs2 = list(
        _validate_required_subsections(None, ["Security"], "### Security\nGood", {})
    )
    assert len(errs2) == 0

    # It returns early if instance is not string
    errs3 = list(_validate_required_subsections(None, ["Security"], {"a": "b"}, {}))
    assert len(errs3) == 0


def test_validate_prohibited_keywords():
    # It yields ValidationError if found
    errs = list(_validate_prohibited_keywords(None, ["ADR"], "Here is an ADR.", {}))
    assert len(errs) == 1
    assert "prohibited governance boilerplate word: 'ADR'" in errs[0].message
    assert errs[0].validator == "prohibited_keywords"

    # It yields nothing if not found
    errs2 = list(_validate_prohibited_keywords(None, ["ADR"], "Here is a Waiver.", {}))
    assert len(errs2) == 0

    # It returns early if instance is not string
    errs3 = list(_validate_prohibited_keywords(None, ["ADR"], {"a": "b"}, {}))
    assert len(errs3) == 0


def test_validate_recommended():
    # Recommended does nothing natively (just passes)
    result = list(_validate_recommended(None, ["Security"], "Some text", {}))
    assert len(result) == 0
