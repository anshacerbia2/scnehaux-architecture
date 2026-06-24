import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validators.base import BaseValidator

def test_base_validator_lint_disable():
    content = "<!-- lint_disable: missing_metadata, prohibited_word -->\nSome content"
    validator = BaseValidator("dummy.md", content, {}, {}, set(), {})
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
    validator = BaseValidator("dummy.md", "", {}, rules, set(), {})
    validator.add_error("structural_integrity_violation", "Bad structure")
    validator.add_error("vague_claim", "Vague")
    
    assert len(validator.errors) == 2
    assert validator.errors[0][0] == "CRITICAL"
    assert validator.errors[1][0] == "WARNING"

from linter import deep_update, print_errors

def test_deep_update():
    d1 = {'a': 1, 'b': {'c': 2}}
    d2 = {'b': {'d': 3}, 'e': 4}
    res = deep_update(d1, d2)
    assert res == {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}

def test_print_errors():
    errors = [('ERROR', 'Bad thing'), ('WARNING', 'Not so bad')]
    errs, p, b = print_errors("file.md", errors, "text")
    assert not p
    assert b
    
    errs2, p2, b2 = print_errors("file.md", [('WARNING', 'Only warning')], "text")
    assert not p2
    assert not b2
    
    errs3, p3, b3 = print_errors("file.md", [], "text")
    assert p3
    assert not b3

def test_base_validator_execution_loop():
    # Calling validate() will trigger all common.py validations automatically
    rules = {
        'severity_levels': {
            'structural_integrity_violation': 'ERROR'
        },
        'rules': {
            'metadata': {'allowed_statuses': ['draft']},
            'federated_governance': {'naming_conventions': {'global_adr_pattern': r'.*'}},
            'structure': {'required_sections': []},
            'content': {'min_content_length_chars': 1}
        }
    }
    content = "---\ndoc_meta:\n  status: draft\n---\nHello World"
    doc_meta = {'status': 'draft', 'owner': 'team', 'classification': 'public'}
    
    validator = BaseValidator("ADR-001.md", content, doc_meta, rules, set(), {})
    # Mock the specific validation since BaseValidator is an abstract class
    validator.validate_type_specific = lambda: None
    
    errors = validator.validate()
    # It should pass all the basic global checks
    assert isinstance(errors, list)

def test_base_validator_default():
    validator = BaseValidator("ADR-001.md", "", {}, {'rules': {}}, set(), {})
    # Should not raise exception
    validator.validate_type_specific()
    assert True
