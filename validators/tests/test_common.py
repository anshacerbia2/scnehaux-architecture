import pytest
from datetime import date

from validators.common import (
    _validate_naming, _validate_metadata_schema, _validate_review_age,
    _validate_structure, _validate_cross_references, _validate_internal_links,
    _validate_quantification, _validate_content_quality, _validate_technology_hold,
)
from validators.base import BaseValidator
from validators.tests.conftest import make_validator


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

def test_validate_metadata_schema():
    rules = {'rules': {'metadata': {'allowed_statuses': ['approved']}}, 'severity_levels': {}}
    v = make_validator(doc_meta={'status': 'draft'}, rules=rules)
    _validate_metadata_schema(v)
    assert any('Status' in msg for sev, msg in v.errors)

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
                'required_sections': ['Introduction', 'Architecture']
            }
        },
        'severity_levels': {},
    }
    v = make_validator(rules=rules, content="## Introduction\n...")
    _validate_structure(v)
    assert any('Architecture' in e[1] for e in v.errors)

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

def test_metadata_no_meta():
    v = make_validator(doc_meta={})
    _validate_metadata_schema(v)
    # Empty dict (no fields) should not crash
    assert isinstance(v.errors, list)

def test_review_age_no_meta():
    v = make_validator(doc_meta={})
    _validate_review_age(v)
    assert len(v.errors) == 0

def test_cross_references_no_meta():
    v = make_validator(doc_meta={})
    _validate_cross_references(v)
    assert len(v.errors) == 0

def test_metadata_missing_title_and_owner():
    rules = {'rules': {'metadata': {'required_fields': ['title', 'owner']}}, 'severity_levels': {}}
    v = make_validator(doc_meta={'status': 'draft'}, rules=rules)
    _validate_metadata_schema(v)
    assert len(v.errors) == 2

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
    v = make_validator(rules=rules, content="## Domain Model\nWe define Bounded Contexts and Domain Events here.")
    _validate_quantification(v)
    assert len(v.errors) == 0
    # A genuinely absent keyword is still flagged.
    v2 = make_validator(rules=rules, content="## Domain Model\nNo relevant content at all.")
    _validate_quantification(v2)
    assert any('Bounded Context' in e[1] for e in v2.errors)

def test_recommended_keyword_warns_not_blocks():
    rules = {
        'severity_levels': {'recommended_keyword_missing': 'WARNING'},
        'rules': {'content': {'recommended_section_keywords': {'Domain Model': ['Domain Event']}}, 'quantification': {}}
    }
    v = make_validator(rules=rules, content="## Domain Model\nOnly bounded contexts here.")
    _validate_quantification(v)
    assert any('Domain Event' in msg and sev == 'WARNING' for sev, msg in v.errors)

def test_technology_hold_skips_non_deployable_types():
    """The tech-radar HOLD check should be a no-op for GDC/EAD/PAD/STD/ADR docs."""
    from validators.gdc import GDCValidator
    rules = {'rules': {}, 'severity_levels': {}}
    v = make_validator(cls=GDCValidator, rules=rules, content="We use MongoDB here.")
def test_naming_missing_pattern():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(rules=rules)
    _validate_naming(v)
    assert len(v.errors) == 0

def test_structure_missing_config():
    rules = {'rules': {}, 'severity_levels': {}}
    v = make_validator(rules=rules)
    _validate_structure(v)
    assert len(v.errors) == 0

def test_cross_references_no_all_doc_ids():
    v = make_validator(doc_meta={'parent_pad': 'PAD-001'})
    _validate_cross_references(v)
    assert len(v.errors) > 0

def test_technology_hold_exception(tmp_path, monkeypatch):
    from validators.sad import SADValidator
    rules = {'rules': {}, 'severity_levels': {}}
    v = make_validator(cls=SADValidator, rules=rules, content="MongoDB is used here.")
    
    # Create a mock tech-radar.yaml
    radar_dir = tmp_path / "01-enterprise"
    radar_dir.mkdir(parents=True, exist_ok=True)
    radar_file = radar_dir / "tech-radar.yaml"
    radar_file.write_text("technology_radar:\n  hold:\n    - MongoDB\n    - AngularJS\n", encoding='utf-8')
    
    # Mock os.path.join so it finds our tmp_path radar
    import os
    original_join = os.path.join
    original_dirname = os.path.dirname
    def mock_join(*args):
        if 'tech-radar.yaml' in args:
            return str(radar_file)
        return original_join(*args)
    monkeypatch.setattr(os.path, 'join', mock_join)

    _validate_technology_hold(v)
    assert any('MongoDB' in msg for sev, msg in v.errors)
def test_metadata_schema_invalid():
    v = make_validator(doc_meta={'id': 123}) # int instead of str
    _validate_metadata_schema(v)
    assert any('Schema validation failed' in msg for sev, msg in v.errors)

def test_metadata_schema_bad_classification():
    rules = {'rules': {'metadata': {'allowed_classifications': ['internal']}}}
    v = make_validator(doc_meta={'id': 'A-001', 'classification': 'public'}, rules=rules)
    _validate_metadata_schema(v)
    assert any('is not in allowed list' in msg for sev, msg in v.errors)

def test_internal_links_skip_http():
    v = make_validator(content="[link](http://example.com) [anchor](#anchor) [mail](mailto:a@b.com)")
    _validate_internal_links(v)
    assert len(v.errors) == 0

def test_internal_links_empty_file_part():
    v = make_validator(content="[link](#) [link](  )")
    _validate_internal_links(v)
    assert len(v.errors) == 0

def test_structure_out_of_order():
    v = make_validator(content="## B\n\nSome text here to meet min length requirement so it doesnt fail on length.\n\n## A\n\nSome text here to meet min length requirement so it doesnt fail on length.\n\n")
    v.rules = {'rules': {'structure': {'required_sections': {'A': 'desc', 'B': 'desc'}, 'min_content_length_chars': 10}}}
    _validate_structure(v)
    assert any('violating expected order' in msg for sev, msg in v.errors)

def test_structure_unrecognized():
    v = make_validator(content="## A\n\ntext text text text text text text text text text\n\n## C\n\ntext text text text text text text text text text\n\n")
    v.rules = {'rules': {'structure': {'required_sections': {'A': 'desc'}, 'optional_sections': ['B'], 'min_content_length_chars': 10}}}
    _validate_structure(v)
    assert any('Unrecognized section' in msg for sev, msg in v.errors)
