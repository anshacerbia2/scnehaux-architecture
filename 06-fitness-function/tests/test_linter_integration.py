from engine.validators.base import BaseValidator
from engine.cli import deep_update, print_errors


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
        'severity_levels': {
            'structural_integrity_violation': 'CRITICAL',
            'missing_metadata': 'ERROR',
            'vague_claim': 'WARNING'
        }
    }
    validator = BaseValidator("dummy.md", "", {}, rules, {}, set(), {})
    validator.add_error("structural_integrity_violation", "Bad structure")
    validator.add_error("vague_claim", "Vague")

    assert len(validator.errors) == 2
    assert validator.errors[0][0] == "CRITICAL"
    assert validator.errors[1][0] == "WARNING"


def test_deep_update():
    d1 = {'a': 1, 'b': {'c': 2}}
    d2 = {'b': {'d': 3}, 'e': 4}
    res = deep_update(d1, d2)
    assert res == {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}

def test_deep_update_nested_lists():
    """Lists are extended with unique elements, avoiding duplicates."""
    d1 = {'a': [1, 2]}
    d2 = {'a': [2, 3, 4]}
    res = deep_update(d1, d2)
    assert res == {'a': [1, 2, 3, 4]}

def test_deep_update_empty_dicts():
    assert deep_update({}, {'a': 1}) == {'a': 1}
    assert deep_update({'a': 1}, {}) == {'a': 1}

def test_print_errors():
    errors = [('ERROR', 'Bad thing'), ('WARNING', 'Not so bad')]
    errs, is_clean, has_blocking = print_errors("file.md", errors, "text")
    assert not is_clean
    assert has_blocking

    errs2, is_clean2, has_blocking2 = print_errors("file.md", [('WARNING', 'Only warning')], "text")
    assert not is_clean2
    assert not has_blocking2

    errs3, is_clean3, has_blocking3 = print_errors("file.md", [], "text")
    assert is_clean3
    assert not has_blocking3

def test_print_errors_json_format():
    """JSON format returns without printing, preserving error data."""
    errors = [('ERROR', 'Bad thing')]
    errs, is_clean, has_blocking = print_errors("file.md", errors, "json")
    assert errs == errors
    assert not is_clean
    assert has_blocking

    # No errors in JSON mode
    errs2, is_clean2, has_blocking2 = print_errors("file.md", [], "json")
    assert is_clean2
    assert not has_blocking2

def test_base_validator_execution_loop():
    rules = {
        'severity_levels': {'structural_integrity_violation': 'ERROR'},
        'rules': {
            'metadata': {'allowed_statuses': ['draft']},
            'structure': {'required_sections': []},
            'content': {'min_content_length_chars': 1}
        }
    }
    content = "---\ndoc_meta:\n  status: draft\n---\nHello World"
    doc_meta = {'status': 'draft', 'owner': 'team', 'classification': 'public'}

    validator = BaseValidator("ADR-001.md", content, doc_meta, rules, {}, set(), {})
    validator.validate_type_specific = lambda: None

    errors = validator.validate()
    assert isinstance(errors, list)

def test_base_validator_default():
    validator = BaseValidator("ADR-001.md", "", {}, {'rules': {}}, {}, set(), {})
    validator.validate_type_specific()
    assert True
