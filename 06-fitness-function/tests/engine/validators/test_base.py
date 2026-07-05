from engine.validators.base import BaseValidator


def test_base_validator_lint_disable():
    content = "<!-- lint_disable: missing_metadata, prohibited_word -->\nSome content"
    validator = BaseValidator("dummy.md", content, {}, {}, {}, set(), {})
    assert "missing_metadata" in validator.disabled_rules
    assert "prohibited_word" in validator.disabled_rules

    # Check that error is bypassed
    validator.add_error("missing_metadata", "This should be ignored")
    assert len(validator.errors) == 0


def test_base_validator_add_error():
    rules = {
        "severity_levels": {
            "structural_integrity_violation": "CRITICAL",
            "missing_metadata": "ERROR",
            "vague_claim": "WARNING",
        }
    }
    validator = BaseValidator("dummy.md", "", {}, rules, {}, set(), {})
    validator.add_error("structural_integrity_violation", "Bad structure")
    validator.add_error("vague_claim", "Vague")

    assert len(validator.errors) == 2
    assert validator.errors[0][0] == "CRITICAL"
    assert validator.errors[1][0] == "WARNING"


def test_base_validator_execution_loop():
    rules = {
        "severity_levels": {"structural_integrity_violation": "ERROR"},
        "rules": {
            "metadata": {"allowed_statuses": ["draft"]},
            "structure": {"required_sections": []},
            "content": {"min_content_length_chars": 1},
        },
    }
    content = "---\ndoc_meta:\n  status: draft\n---\nHello World"
    doc_meta = {"status": "draft", "owner": "team", "classification": "public"}

    validator = BaseValidator("ADR-001.md", content, doc_meta, rules, {}, set(), {})
    validator.validate_type_specific = lambda: None

    errors = validator.validate()
    assert isinstance(errors, list)


def test_base_validator_default():
    validator = BaseValidator("ADR-001.md", "", {}, {"rules": {}}, {}, set(), {})
    validator.validate_type_specific()
    assert True


def test_base_validator_lint_disable_ignored_inside_code_fence():
    content = "```html\n<!-- lint_disable: missing_metadata -->\n```\nreal body"
    v = BaseValidator("x.md", content, {}, {}, {}, set(), {})
    assert "missing_metadata" not in v.disabled_rules


def test_base_validator_lint_disable_honored_with_reason():
    content = (
        "<!-- lint_disable: prohibited_word (reason: ARB waiver in ADR-GLB-009) -->"
    )
    v = BaseValidator("x.md", content, {}, {}, {}, set(), {})
    assert "prohibited_word" in v.disabled_rules
    assert v.disable_reasons["prohibited_word"] == "ARB waiver in ADR-GLB-009"


def test_base_validator_lint_disable_undocumented_has_none_reason():
    content = "<!-- lint_disable: prohibited_word -->"
    v = BaseValidator("x.md", content, {}, {}, {}, set(), {})
    assert v.disable_reasons["prohibited_word"] is None


def test_base_validator_lint_disable_cannot_silence_critical():
    rules = {"severity_levels": {"structural_integrity_violation": "CRITICAL"}}
    content = "<!-- lint_disable: structural_integrity_violation -->"
    v = BaseValidator("x.md", content, {}, rules, {}, set(), {})
    v.add_error("structural_integrity_violation", "sections out of order")
    assert any(sev == "CRITICAL" for sev, _ in v.errors), (
        "CRITICAL finding must still fire"
    )
    assert "structural_integrity_violation" in v.rejected_disables


def test_base_validator_lint_disable_honors_non_critical():
    rules = {"severity_levels": {"prohibited_word": "WARNING"}}
    content = "<!-- lint_disable: prohibited_word -->"
    v = BaseValidator("x.md", content, {}, rules, {}, set(), {})
    v.add_error("prohibited_word", "weasel word")
    assert len(v.errors) == 0


# ---------- FIX#3: inline reference validation ----------


def test_schema_validation_enum():
    schema = {
        "type": "object",
        "properties": {
            "doc_meta": {
                "type": "object",
                "properties": {"status": {"enum": ["active"]}},
            }
        },
    }
    v = BaseValidator("test.md", "content", {"status": "draft"}, {}, schema, set(), {})
    v.validate()
    assert any("Schema validation failed at doc_meta" in e[1] for e in v.errors)


def test_schema_validation_pattern():
    schema = {"type": "object", "properties": {"Context": {"pattern": "^[a-z]+$"}}}
    v = BaseValidator("test.md", "## Context\n\n123", {}, {}, schema, set(), {})
    v.validate()
    assert any("expected pattern" in e[1] for e in v.errors)


def test_schema_validation_other():
    schema = {"type": "object", "properties": {"doc_meta": {"type": "string"}}}
    v = BaseValidator("test.md", "content", {"status": "draft"}, {}, schema, set(), {})
    v.validate()
    assert any("type" in e[1] or "Schema validation failed" in e[1] for e in v.errors)


def test_convert_dates():
    import datetime

    schema = {}
    v = BaseValidator(
        "test.md",
        "content",
        {"d": datetime.date(2023, 1, 1), "l": [datetime.date(2023, 1, 2)]},
        {},
        schema,
        set(),
        {},
    )
    v.validate()
    # It shouldn't crash, the dates should be converted.
