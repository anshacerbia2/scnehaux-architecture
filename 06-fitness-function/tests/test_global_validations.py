import pytest
from datetime import date

from engine.validators.global_rules import (
    _validate_naming, _validate_review_age,
    _validate_structure, _validate_cross_references, _validate_internal_links,
    _validate_quantification, _validate_content_quality, _validate_technology_hold,
    _validate_nfr_taxonomy
)
from engine.validators.base import BaseValidator
from tests.conftest import make_validator


def test_validate_naming():
    rules = {
        'rules': {
            'metadata': {
                'filename_pattern': r'^ADR-[A-Z]+-[A-Z]+-\d{3}-.*\.md$'
            }
        },
        'severity_levels': {},
    }
    v_good = make_validator(file_path='/fake/ADR-GLB-XXX-001-test.md', rules=rules, filename='ADR-GLB-XXX-001-test.md')
    _validate_naming(v_good)
    assert len(v_good.errors) == 0

    v_bad = make_validator(file_path='/fake/wrong.md', rules=rules, filename='wrong.md')
    _validate_naming(v_bad)
    assert len(v_bad.errors) == 1
    assert v_bad.errors[0][0] == 'ERROR'

def test_validate_review_age():
    rules = {'rules': {}, 'severity_levels': {}}
    v = make_validator(doc_meta={'last_reviewed': '2000-01-01', 'review_cycle_days': 365}, rules=rules)
    _validate_review_age(v)
    assert len(v.errors) == 1
    assert v.errors[0][0] == 'ERROR'

def test_validate_structure():
    rules = {
        'rules': {
            'structure': {
                'min_content_length_chars': 100
            }
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Introduction\nToo short.")
    _validate_structure(v)
    assert any('content length' in e[1] for e in v.errors)

def test_validate_content_quality():
    rules = {
        'rules': {
            'content': {
                'min_content_length_chars': 100,
                'prohibited_words': ['just', 'basically']
            }
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="This is basically just too short.")
    _validate_content_quality(v)
    # Exactly 2 errors: one for 'just', one for 'basically'
    prohibited_errors = [e for e in v.errors if 'prohibited word' in e[1].lower()]
    assert len(prohibited_errors) == 2

def test_validate_quantification():
    rules = {
        'rules': {
            'quantification': {
                'required_for_sections': ['Performance'],
                'metric_pattern': r'\d+\s*ms'
            },
            'content': {},
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Performance\nIt is very fast.")
    _validate_quantification(v)
    assert len(v.errors) == 1
    assert 'quantified metrics' in v.errors[0][1]

def test_validate_internal_links(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    file_path = repo_dir / "target.md"
    file_path.write_text("Hello")

    v = make_validator(file_path=str(repo_dir / "source.md"), content="Link: [Target](./target.md)")
    _validate_internal_links(v)
    assert len(v.errors) == 0

    v_bad = make_validator(file_path=str(repo_dir / "source.md"), content="Link: [Bad](./missing.md)")
    _validate_internal_links(v_bad)
    assert len(v_bad.errors) == 1

def test_validate_cross_references():
    rules = {'rules': {}, 'severity_levels': {}}
    # Test invalid cross reference IDs
    v2 = make_validator(
        doc_meta={'status': 'draft', 'parent_pad': 'PAD-999', 'governed_by': ['GDC-999']},
        rules=rules, all_doc_ids={'PAD-001'},
    )
    _validate_cross_references(v2)
    assert any("not found in this repository" in e[1] for e in v2.errors)

    # Test valid
    v3 = make_validator(
        doc_meta={'status': 'draft', 'parent_pad': 'PAD-001', 'governed_by': 'GDC-002'},
        rules=rules, all_doc_ids={'PAD-001', 'GDC-002'},
    )
    _validate_cross_references(v3)
    assert len(v3.errors) == 0

def test_naming_all_branches():
    rules = {
        'rules': {'metadata': {'filename_pattern': r'^GDC-\d{3}-.*\.md$'}},
        'severity_levels': {},
    }
    def check_name(filename, expect_err):
        v = make_validator(file_path=f'/fake/{filename}', rules=rules, filename=filename)
        _validate_naming(v)
        assert len(v.errors) == (1 if expect_err else 0)

    check_name('invalid.md', True)
    check_name('GDC-002-test.md', False)

def test_review_age_no_meta():
    v = make_validator(doc_meta={})
    _validate_review_age(v)
    assert len(v.errors) == 0

def test_cross_references_no_meta():
    v = make_validator(doc_meta={})
    _validate_cross_references(v)
    assert len(v.errors) == 0

def test_ambiguity_check():
    rules = {'rules': {'content': {'ambiguity_check': {'pattern': 'probably', 'message': 'Too ambiguous'}}}, 'severity_levels': {}}
    v = make_validator(rules=rules, content="It will probably work.")
    _validate_content_quality(v)
    assert len(v.errors) == 1

def test_quantification_keywords():
    rules = {
        'rules': {
            'content': {
                'required_section_keywords': {'Architecture': ['database']},
                'prohibited_section_keywords': {'Architecture': ['legacy']}
            },
            'quantification': {},
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Architecture\nThis is a legacy system without db.")
    v_bad = make_validator(file_path='/fake/wrong.md', rules=rules, filename='wrong.md')
    _validate_naming(v_bad)
    assert len(v_bad.errors) == 1
    assert v_bad.errors[0][0] == 'ERROR'

def test_validate_review_age():
    rules = {'rules': {}, 'severity_levels': {}}
    v = make_validator(doc_meta={'last_reviewed': '2000-01-01', 'review_cycle_days': 365}, rules=rules)
    _validate_review_age(v)
    assert len(v.errors) == 1
    assert v.errors[0][0] == 'ERROR'

def test_validate_structure():
    rules = {
        'rules': {
            'structure': {
                'min_content_length_chars': 100
            }
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Introduction\nToo short.")
    _validate_structure(v)
    assert any('content length' in e[1] for e in v.errors)

def test_validate_content_quality():
    rules = {
        'rules': {
            'content': {
                'min_content_length_chars': 100,
                'prohibited_words': ['just', 'basically']
            }
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="This is basically just too short.")
    _validate_content_quality(v)
    # Exactly 2 errors: one for 'just', one for 'basically'
    prohibited_errors = [e for e in v.errors if 'prohibited word' in e[1].lower()]
    assert len(prohibited_errors) == 2

def test_validate_quantification():
    rules = {
        'rules': {
            'quantification': {
                'required_for_sections': ['Performance'],
                'metric_pattern': r'\d+\s*ms'
            },
            'content': {},
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Performance\nIt is very fast.")
    _validate_quantification(v)
    assert len(v.errors) == 1
    assert 'quantified metrics' in v.errors[0][1]

def test_validate_internal_links(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    file_path = repo_dir / "target.md"
    file_path.write_text("Hello")

    v = make_validator(file_path=str(repo_dir / "source.md"), content="Link: [Target](./target.md)")
    _validate_internal_links(v)
    assert len(v.errors) == 0

    v_bad = make_validator(file_path=str(repo_dir / "source.md"), content="Link: [Bad](./missing.md)")
    _validate_internal_links(v_bad)
    assert len(v_bad.errors) == 1

def test_validate_cross_references():
    rules = {'rules': {}, 'severity_levels': {}}
    # Test invalid cross reference IDs
    v2 = make_validator(
        doc_meta={'status': 'draft', 'parent_pad': 'PAD-999', 'governed_by': ['GDC-999']},
        rules=rules, all_doc_ids={'PAD-001'},
    )
    _validate_cross_references(v2)
    assert any("not found in this repository" in e[1] for e in v2.errors)

    # Test valid
    v3 = make_validator(
        doc_meta={'status': 'draft', 'parent_pad': 'PAD-001', 'governed_by': 'GDC-002'},
        rules=rules, all_doc_ids={'PAD-001', 'GDC-002'},
    )
    _validate_cross_references(v3)
    assert len(v3.errors) == 0

def test_naming_all_branches():
    rules = {
        'rules': {'metadata': {'filename_pattern': r'^GDC-\d{3}-.*\.md$'}},
        'severity_levels': {},
    }
    def check_name(filename, expect_err):
        v = make_validator(file_path=f'/fake/{filename}', rules=rules, filename=filename)
        _validate_naming(v)
        assert len(v.errors) == (1 if expect_err else 0)

    check_name('invalid.md', True)
    check_name('GDC-002-test.md', False)

def test_review_age_no_meta():
    v = make_validator(doc_meta={})
    _validate_review_age(v)
    assert len(v.errors) == 0

def test_cross_references_no_meta():
    v = make_validator(doc_meta={})
    _validate_cross_references(v)
    assert len(v.errors) == 0

def test_ambiguity_check():
    rules = {'rules': {'content': {'ambiguity_check': {'pattern': 'probably', 'message': 'Too ambiguous'}}}, 'severity_levels': {}}
    v = make_validator(rules=rules, content="It will probably work.")
    _validate_content_quality(v)
    assert len(v.errors) == 1

def test_quantification_keywords():
    rules = {
        'rules': {
            'content': {
                'required_section_keywords': {'Architecture': ['database']},
                'prohibited_section_keywords': {'Architecture': ['legacy']}
            },
            'quantification': {},
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Architecture\nThis is a legacy system without db.")
    _validate_quantification(v)
    assert any('missing mandatory keyword' in e[1] for e in v.errors)
    assert any('prohibited governance boilerplate' in e[1] for e in v.errors)

def test_required_keyword_suffix_tolerant():
    rules = {'rules': {'content': {'required_section_keywords': {'Domain Model': ['Bounded Context', 'Domain Event']}}, 'quantification': {}}, 'severity_levels': {}}
    from engine.validators.domains.sad_validator import SADValidator
    v = make_validator(content="[link](#) [link](  )")
    _validate_internal_links(v)
    assert len(v.errors) == 0

def test_validate_nfr_taxonomy():
    rules = {
        'rules': {
            'quantification': {
                'aws_waf_pillars': ['Security', 'Reliability']
            }
        },
        'severity_levels': {'structural_integrity_violation': 'ERROR'},
    }
    content = "## Non-Functional Requirements\n### Security\nGood.\n### Invalid Pillar\nBad."
    v = make_validator(rules=rules, content=content)
    _validate_nfr_taxonomy(v)
    assert len(v.errors) == 1
    assert "not a recognized AWS WAF Pillar" in v.errors[0][1]
