import sys
import os
import pytest
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validators.common import (
    _validate_naming, _validate_metadata_schema, _validate_review_age,
    _validate_structure, _validate_cross_references, _validate_internal_links,
    _validate_quantification, _validate_content_quality
)
from validators.base import BaseValidator

class MockValidator(BaseValidator):
    def __init__(self, rel_path, filename, doc_meta, rules, all_doc_ids, content=""):
        self.rel_path = rel_path
        self.filename = filename
        self.doc_meta = doc_meta
        self.rules = rules
        self.all_doc_ids = all_doc_ids
        self.content = content
        self.errors = []
        self.disabled_rules = set()
        self.file_path = f"/fake/{rel_path}"

def test_validate_naming():
    rules = {
        'rules': {
            'metadata': {
                'filename_pattern': r'^ADR-[A-Z]+-[A-Z]+-\d{3}-.*\.md$'
            }
        }
    }
    v_good = MockValidator('05-decisions/_global/ADR-GLB-XXX-001-test.md', 'ADR-GLB-XXX-001-test.md', {}, rules, set())
    _validate_naming(v_good)
    assert len(v_good.errors) == 0

    v_bad = MockValidator('05-decisions/_global/wrong.md', 'wrong.md', {}, rules, set())
    _validate_naming(v_bad)
    assert len(v_bad.errors) == 1
    assert v_bad.errors[0][0] == 'ERROR'

def test_validate_metadata_schema():
    v = MockValidator('test.md', 'test.md', {'status': 'draft'}, {'rules': {'metadata': {'allowed_statuses': ['approved']}}}, set())
    _validate_metadata_schema(v)
    assert any('Status' in msg for sev, msg in v.errors)

def test_validate_review_age():
    v = MockValidator('test.md', 'test.md', {'last_reviewed': '2000-01-01', 'review_cycle_days': 365}, {'rules':{}}, set())
    _validate_review_age(v)
    assert len(v.errors) == 1
    assert v.errors[0][0] == 'ERROR'

def test_validate_structure():
    rules = {
        'rules': {
            'structure': {
                'required_sections': ['Introduction', 'Architecture']
            }
        }
    }
    v = MockValidator('test.md', 'test.md', {}, rules, set(), "## Introduction\n...")
    _validate_structure(v)
    assert any('Architecture' in e[1] for e in v.errors)

def test_validate_content_quality():
    rules = {
        'rules': {
            'content': {
                'min_content_length_chars': 100,
                'prohibited_words': ['just', 'basically']
            }
        }
    }
    v = MockValidator('test.md', 'test.md', {}, rules, set(), "This is basically just too short.")
    _validate_content_quality(v)
    assert len(v.errors) >= 2 # length and prohibited words

def test_validate_quantification():
    rules = {
        'rules': {
            'quantification': {
                'required_for_sections': ['Performance'],
                'metric_pattern': r'\d+\s*ms'
            }
        }
    }
    v = MockValidator('test.md', 'test.md', {}, rules, set(), "## Performance\nIt is very fast.")
    _validate_quantification(v)
    assert len(v.errors) == 1
    assert 'quantified metrics' in v.errors[0][1]

def test_validate_internal_links(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    file_path = repo_dir / "target.md"
    file_path.write_text("Hello")
    
    v = MockValidator('source.md', 'source.md', {}, {}, set(), f"Link: [Target](./target.md)")
    v.file_path = str(repo_dir / "source.md")
    
    _validate_internal_links(v)
    assert len(v.errors) == 0
    
    v_bad = MockValidator('source.md', 'source.md', {}, {}, set(), f"Link: [Bad](./missing.md)")
    v_bad.file_path = str(repo_dir / "source.md")
    _validate_internal_links(v_bad)
    assert len(v_bad.errors) == 1

def test_validate_cross_references():
    rules = {
        'rules': {
            'traceability': {
                'required_traceability_links': {
                    'SAD': ['parent_pad', 'governed_by']
                }
            }
        }
    }
    # Test invalid cross reference IDs
    v2 = MockValidator('SAD-001.md', 'SAD-001.md', {
        'status': 'draft',
        'parent_pad': 'PAD-999',
        'governed_by': ['GDC-999']
    }, rules, {'PAD-001'})
    _validate_cross_references(v2)
    assert any("not found in this repository" in e[1] for e in v2.errors)
    
    # Test valid
    v3 = MockValidator('SAD-001.md', 'SAD-001.md', {
        'status': 'draft',
        'parent_pad': 'PAD-001',
        'governed_by': 'GDC-001'
    }, rules, {'PAD-001', 'GDC-001'})
    _validate_cross_references(v3)
    _validate_cross_references(v3)
    assert len(v3.errors) == 0

def test_naming_all_branches():
    # Since logic is unified, we just test that filename_pattern is checked correctly.
    rules = {
        'rules': {
            'metadata': {
                'filename_pattern': r'^GDC-\d{3}-.*\.md$'
            }
        }
    }
    def check_name(path, filename, expect_err):
        v = MockValidator(path, filename, {}, rules, set())
        _validate_naming(v)
        if expect_err:
            assert len(v.errors) == 1
        else:
            assert len(v.errors) == 0

    check_name('00-governance/invalid.md', 'invalid.md', True)
    check_name('00-governance/GDC-001-test.md', 'GDC-001-test.md', False)

def test_metadata_no_meta():
    v = MockValidator('test.md', 'test.md', None, {}, set())
    _validate_metadata_schema(v)
    assert len(v.errors) == 0

def test_review_age_no_meta():
    v = MockValidator('test.md', 'test.md', None, {}, set())
    _validate_review_age(v)
    assert len(v.errors) == 0

def test_cross_references_no_meta():
    v = MockValidator('test.md', 'test.md', None, {}, set())
    _validate_cross_references(v)
    assert len(v.errors) == 0
def test_metadata_missing_title_and_owner():
    rules = {'rules': {'metadata': {'required_fields': ['title', 'owner']}}}
    v = MockValidator('test.md', 'test.md', {'status': 'draft'}, rules, set())
    _validate_metadata_schema(v)
    assert len(v.errors) == 2

def test_ambiguity_check():
    rules = {'rules': {'content': {'ambiguity_check': {'pattern': 'probably', 'message': 'Too ambiguous'}}}}
    v = MockValidator('test.md', 'test.md', {}, rules, set(), "It will probably work.")
    from validators.common import _validate_content_quality
    _validate_content_quality(v)
    assert len(v.errors) == 1

def test_quantification_keywords():
    rules = {
        'rules': {
            'content': {
                'required_section_keywords': {'Architecture': ['database']},
                'prohibited_section_keywords': {'Architecture': ['legacy']}
            }
        }
    }
    v = MockValidator('test.md', 'test.md', {}, rules, set(), "## Architecture\nThis is a legacy system without db.")
    from validators.common import _validate_quantification
    _validate_quantification(v)
    assert any('missing mandatory keyword' in e[1] for e in v.errors)
    assert any('prohibited governance boilerplate' in e[1] for e in v.errors)

def test_required_keyword_suffix_tolerant():
    # Plural / inflected forms of a required keyword satisfy the check.
    rules = {'rules': {'content': {'required_section_keywords': {'Domain Model': ['Bounded Context', 'Domain Event']}}}}
    from validators.common import _validate_quantification
    v = MockValidator('x.md', 'x.md', {}, rules, set(), "## Domain Model\nWe define Bounded Contexts and Domain Events here.")
    _validate_quantification(v)
    assert len(v.errors) == 0
    # A genuinely absent keyword is still flagged.
    v2 = MockValidator('x.md', 'x.md', {}, rules, set(), "## Domain Model\nNo relevant content at all.")
    _validate_quantification(v2)
    assert any('Bounded Context' in e[1] for e in v2.errors)

def test_recommended_keyword_warns_not_blocks():
    # A missing RECOMMENDED keyword is surfaced as a non-blocking WARNING, not an ERROR.
    rules = {
        'severity_levels': {'recommended_keyword_missing': 'WARNING'},
        'rules': {'content': {'recommended_section_keywords': {'Domain Model': ['Domain Event']}}}
    }
    from validators.common import _validate_quantification
    v = MockValidator('x.md', 'x.md', {}, rules, set(), "## Domain Model\nOnly bounded contexts here.")
    _validate_quantification(v)
    assert any('Domain Event' in msg and sev == 'WARNING' for sev, msg in v.errors)
