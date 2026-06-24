import sys
import os
import pytest
from datetime import date, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validators.gdc import GDCValidator
from validators.ead import EADValidator
from validators.std import STDValidator
from validators.pad import PADValidator
from validators.sad import SADValidator
from validators.adr import ADRValidator
from validators.tdd import TDDValidator

class MockADRValidator(ADRValidator):
    def __init__(self, doc_meta, content=""):
        self.doc_meta = doc_meta
        self.rules = {'rules': {'metadata': {'exception_info_required_fields': ['expiry_date'], 'allowed_types': ['standard', 'exception']}}}
        self.errors = []
        self.content = content
        self.all_doc_ids = set()
        self.filename = "ADR-001.md"
        self.disabled_rules = set()

def test_adr_exception_missing_info():
    v = MockADRValidator({'adr_type': 'exception'})
    v.validate_type_specific()
    assert any('missing the required' in msg for sev, msg in v.errors)

def test_adr_exception_expired():
    past = date.today() - timedelta(days=1)
    meta = {
        'adr_type': 'exception',
        'status': 'accepted',
        'exception_info': {'expiry_date': past}
    }
    v = MockADRValidator(meta)
    v.validate_type_specific()
    assert any('has expired' in msg for sev, msg in v.errors)

class MockSADValidator(SADValidator):
    def __init__(self, doc_meta, all_doc_metadata=None):
        self.doc_meta = doc_meta
        self.rules = {'rules': {'metadata': {}}}
        self.errors = []
        self.all_doc_ids = {'PAD-001'}
        self.all_doc_metadata = all_doc_metadata or {}
        self.filename = "SAD-001.md"
        self.disabled_rules = set()

def test_sad_missing_parent_pad():
    v = MockSADValidator({'status': 'draft'})
    v.validate_type_specific()
    assert any('missing required traceability' in msg for sev, msg in v.errors)

def test_sad_invalid_parent_pad():
    v = MockSADValidator({'parent_pad': 'PAD-999'})
    v.validate_type_specific()
    assert any('does not exist' in msg for sev, msg in v.errors)

def test_sad_bidirectional_traceability_fail():
    v = MockSADValidator({'id': 'SAD-001', 'parent_pad': 'PAD-001'}, all_doc_metadata={'PAD-001': {'fulfilled_by': ['SAD-999']}})
    v.validate_type_specific()
    assert any('Bidirectional traceability is broken' in msg for sev, msg in v.errors)

def test_sad_bidirectional_traceability_pass():
    v = MockSADValidator({'id': 'SAD-001', 'parent_pad': 'PAD-001'}, all_doc_metadata={'PAD-001': {'fulfilled_by': ['SAD-001']}})
    v.validate_type_specific()
    assert len(v.errors) == 0

class MockPADValidator(PADValidator):
    def __init__(self, doc_meta, all_doc_metadata=None):
        self.doc_meta = doc_meta
        self.rules = {'rules': {'metadata': {}}}
        self.errors = []
        self.all_doc_ids = {'SAD-001'}
        self.all_doc_metadata = all_doc_metadata or {}
        self.filename = "PAD-001.md"
        self.disabled_rules = set()

def test_pad_invalid_fulfilled_by():
    v = MockPADValidator({'fulfilled_by': ['SAD-999']})
    v.validate_type_specific()
    assert any('does not exist' in msg for sev, msg in v.errors)

def test_pad_bidirectional_traceability_fail():
    v = MockPADValidator({'id': 'PAD-001', 'fulfilled_by': ['SAD-001']}, all_doc_metadata={'SAD-001': {'parent_pad': 'PAD-999'}})
    v.validate_type_specific()
    assert any('Bidirectional traceability is broken' in msg for sev, msg in v.errors)

def test_pad_bidirectional_traceability_pass():
    v = MockPADValidator({'id': 'PAD-001', 'fulfilled_by': ['SAD-001']}, all_doc_metadata={'SAD-001': {'parent_pad': 'PAD-001'}})
    v.validate_type_specific()
    assert len(v.errors) == 0

class MockSTDValidator(STDValidator):
    def __init__(self, doc_meta):
        self.doc_meta = doc_meta
        self.rules = {'rules': {'metadata': {}}}
        self.errors = []
        self.filename = "STD-001.md"
        self.disabled_rules = set()

def test_std_hold_status():
    v = MockSTDValidator({'status': 'hold'})
    v.validate_type_specific()
    assert any('retirement phase' in msg for sev, msg in v.errors)

class MockGDCValidator(GDCValidator):
    def __init__(self, filename, content, rules=None):
        self.doc_meta = {'status': 'draft'}
        # Subsections are sourced from the YAML SSOT (rules.structure), matching the
        # refactored GDCValidator. The previous hardcoded-pillar mock drifted from the engine.
        self.rules = rules or {'rules': {'structure': {'required_downstream_guideline_subsections': {
            'Semantic Definitions': ['Naming Conventions', 'Taxonomy'],
            'Metadata Schema Properties': ['Allowed Lifecycle Statuses', 'Allowed Classifications'],
        }}}}
        self.errors = []
        self.filename = filename
        self.content = content
        self.disabled_rules = set()

def test_gdc_guideline_interface():
    # Neither required parent section present -> one missing_section error per parent (2).
    v = MockGDCValidator('EAD-007-guideline.md', "## Introduction")
    v.validate_type_specific()
    assert len(v.errors) == 2

    good_content = (
        "## Semantic Definitions\n"
        "### Naming Conventions\n### Taxonomy\n"
        "## Metadata Schema Properties\n"
        "### Allowed Lifecycle Statuses\n### Allowed Classifications\n"
    )
    v_good = MockGDCValidator('EAD-007-guideline.md', good_content)
    v_good.validate_type_specific()
    assert len(v_good.errors) == 0

def test_gdc_missing_subsection():
    content = (
        "## Semantic Definitions\n### Naming Conventions\n"  # 'Taxonomy' missing
        "## Metadata Schema Properties\n### Allowed Lifecycle Statuses\n### Allowed Classifications\n"
    )
    v = MockGDCValidator('EAD-007-guideline.md', content)
    v.validate_type_specific()
    assert any("missing mandatory subsection 'Taxonomy'" in m for _, m in v.errors)

def test_gdc_subsection_out_of_order():
    content = (
        "## Semantic Definitions\n### Taxonomy\n### Naming Conventions\n"  # reversed
        "## Metadata Schema Properties\n### Allowed Lifecycle Statuses\n### Allowed Classifications\n"
    )
    v = MockGDCValidator('EAD-007-guideline.md', content)
    v.validate_type_specific()
    assert any('out of order' in m for _, m in v.errors)

def test_gdc_non_guideline_file_skipped():
    # Only '*-guideline.md' files are subject to the downstream interface check.
    v = MockGDCValidator('GDC-001-compliance-engine.md', "## Anything")
    v.validate_type_specific()
    assert len(v.errors) == 0

def test_ead_mandatory_sections_resolution():
    # dict branch: resolve by EAD id embedded in filename
    rules = {'rules': {'structure': {'required_sections': {
        'EAD-001': ['Business Capabilities'], 'EAD-002': ['Data Domains']}}}}
    v = EADValidator('EAD-001-business.md', '', {'id': 'EAD-001'}, rules, set())
    assert v.mandatory_sections == ['Business Capabilities']
    # no matching template -> fallback empty list
    v2 = EADValidator('EAD-099-other.md', '', {'id': 'EAD-099'}, rules, set())
    assert v2.mandatory_sections == []
    # list branch: returned as-is
    rules2 = {'rules': {'structure': {'required_sections': ['A', 'B']}}}
    v3 = EADValidator('EAD-001.md', '', {}, rules2, set())
    assert v3.mandatory_sections == ['A', 'B']

def test_missing_doc_meta_for_all():
    v1 = MockADRValidator(None)
    v1.validate_type_specific()
    assert len(v1.errors) == 0
    
    v2 = MockSADValidator(None)
    v2.validate_type_specific()
    assert len(v2.errors) == 0
    
    v3 = MockPADValidator(None)
    v3.validate_type_specific()
    assert len(v3.errors) == 0
    
    v4 = MockSTDValidator(None)
    v4.validate_type_specific()
    assert len(v4.errors) == 0
    
    v5 = MockGDCValidator('EAD.md', '')
    v5.doc_meta = None
    v5.validate_type_specific()
    assert len(v5.errors) == 0
    
    v6 = EADValidator('EAD.md', '', None, {}, set())
    v6.validate_type_specific()
    assert len(v6.errors) == 0
    
    v7 = TDDValidator('TDD.md', '', None, {}, set(), {})
    v7.validate_type_specific()
    assert len(v7.errors) == 0

class MockTDDValidator(TDDValidator):
    def __init__(self, doc_meta):
        self.doc_meta = doc_meta
        self.rules = {'rules': {'metadata': {}}}
        self.errors = []
        self.all_doc_ids = {'SAD-001'}
        self.all_doc_metadata = {}
        self.filename = "TDD-001.md"
        self.disabled_rules = set()

def test_tdd_missing_parent_sad():
    v = MockTDDValidator({'status': 'draft'})
    v.validate_type_specific()
    assert any('missing required traceability' in msg for sev, msg in v.errors)

def test_tdd_invalid_parent_sad():
    v = MockTDDValidator({'parent_sad': 'SAD-999'})
    v.validate_type_specific()
    assert any('does not exist' in msg for sev, msg in v.errors)

def test_tdd_valid_parent_sad():
    v = MockTDDValidator({'parent_sad': 'SAD-001'})
    v.validate_type_specific()
    assert len(v.errors) == 0

def test_adr_invalid_type():
    v = MockADRValidator({'adr_type': 'invalid_type'})
    v.validate_type_specific()
    assert any("not in allowed list" in e[1] for e in v.errors)

def test_adr_missing_exception_block():
    v = MockADRValidator({'adr_type': 'exception'}) # without exception_info
    v.validate_type_specific()
    assert any("missing the required 'exception_info'" in e[1] for e in v.errors)
