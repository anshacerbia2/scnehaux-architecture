import pytest
from datetime import date, timedelta

from validators.gdc import GDCValidator
from validators.ead import EADValidator
from validators.std import STDValidator
from validators.pad import PADValidator
from validators.sad import SADValidator
from validators.adr import ADRValidator
from validators.tdd import TDDValidator
from validators.tests.conftest import make_validator


# ---------- ADR ----------

def test_adr_exception_missing_info():
    rules = {'rules': {'metadata': {'exception_info_required_fields': ['expiry_date'], 'allowed_types': ['standard', 'exception']}}, 'severity_levels': {}}
    v = make_validator(cls=ADRValidator, doc_meta={'adr_type': 'exception'}, rules=rules, filename='ADR-001.md')
    v.validate_type_specific()
    assert any('missing the required' in msg for sev, msg in v.errors)

def test_adr_exception_expired():
    past = date.today() - timedelta(days=1)
    meta = {'adr_type': 'exception', 'status': 'accepted', 'exception_info': {'expiry_date': past}}
    rules = {'rules': {'metadata': {'exception_info_required_fields': ['expiry_date'], 'allowed_types': ['standard', 'exception']}}, 'severity_levels': {}}
    v = make_validator(cls=ADRValidator, doc_meta=meta, rules=rules, filename='ADR-001.md')
    v.validate_type_specific()
    assert any('has expired' in msg for sev, msg in v.errors)

def test_adr_invalid_type():
    rules = {'rules': {'metadata': {'exception_info_required_fields': ['expiry_date'], 'allowed_types': ['standard', 'exception']}}, 'severity_levels': {}}
    v = make_validator(cls=ADRValidator, doc_meta={'adr_type': 'invalid_type'}, rules=rules, filename='ADR-001.md')
    v.validate_type_specific()
    assert any("not in allowed list" in e[1] for e in v.errors)

def test_adr_missing_exception_block():
    rules = {'rules': {'metadata': {'exception_info_required_fields': ['expiry_date'], 'allowed_types': ['standard', 'exception']}}, 'severity_levels': {}}
    v = make_validator(cls=ADRValidator, doc_meta={'adr_type': 'exception'}, rules=rules, filename='ADR-001.md')
    v.validate_type_specific()
    assert any("missing the required 'exception_info'" in e[1] for e in v.errors)


# ---------- SAD ----------

def test_sad_missing_parent_pad():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=SADValidator, doc_meta={'status': 'draft'}, rules=rules, filename='SAD-001.md')
    v.validate_type_specific()
    assert any('missing required traceability' in msg for sev, msg in v.errors)

def test_sad_invalid_parent_pad():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=SADValidator, doc_meta={'parent_pad': 'PAD-999'}, rules=rules, all_doc_ids={'PAD-001'}, filename='SAD-001.md')
    v.validate_type_specific()
    assert any('does not exist' in msg for sev, msg in v.errors)

def test_sad_bidirectional_traceability_fail():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=SADValidator, doc_meta={'id': 'SAD-001', 'parent_pad': 'PAD-001'}, rules=rules,
        all_doc_ids={'PAD-001'}, all_doc_metadata={'PAD-001': {'fulfilled_by': ['SAD-999']}}, filename='SAD-001.md')
    v.validate_type_specific()
    assert any('Bidirectional traceability is broken' in msg for sev, msg in v.errors)

def test_sad_bidirectional_traceability_pass():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=SADValidator, doc_meta={'id': 'SAD-001', 'parent_pad': 'PAD-001'}, rules=rules,
        all_doc_ids={'PAD-001'}, all_doc_metadata={'PAD-001': {'fulfilled_by': ['SAD-001']}}, filename='SAD-001.md')
    v.validate_type_specific()
    assert len(v.errors) == 0


# ---------- PAD ----------

def test_pad_invalid_fulfilled_by():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=PADValidator, doc_meta={'fulfilled_by': ['SAD-999']}, rules=rules, all_doc_ids={'SAD-001'}, filename='PAD-001.md')
    v.validate_type_specific()
    assert any('does not exist' in msg for sev, msg in v.errors)

def test_pad_bidirectional_traceability_fail():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=PADValidator, doc_meta={'id': 'PAD-001', 'fulfilled_by': ['SAD-001']}, rules=rules,
        all_doc_ids={'SAD-001'}, all_doc_metadata={'SAD-001': {'parent_pad': 'PAD-999'}}, filename='PAD-001.md')
    v.validate_type_specific()
    assert any('Bidirectional traceability is broken' in msg for sev, msg in v.errors)

def test_pad_bidirectional_traceability_pass():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=PADValidator, doc_meta={'id': 'PAD-001', 'fulfilled_by': ['SAD-001'], 'realizes_capability': 'EAD-001'}, rules=rules,
        all_doc_ids={'SAD-001', 'EAD-001'}, all_doc_metadata={'SAD-001': {'parent_pad': 'PAD-001'}, 'EAD-001': {}}, filename='PAD-001.md')
    v.validate_type_specific()
    assert len(v.errors) == 0


# ---------- STD ----------

def test_std_hold_status():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=STDValidator, doc_meta={'status': 'hold'}, rules=rules, filename='STD-001.md')
    v.validate_type_specific()
    assert any('retirement phase' in msg for sev, msg in v.errors)


# ---------- GDC ----------

def test_gdc_guideline_interface():
    rules = {'rules': {'structure': {'required_downstream_guideline_subsections': {
        'Semantic Definitions': ['Naming Conventions', 'Taxonomy'],
        'Metadata Schema Properties': ['Allowed Lifecycle Statuses', 'Allowed Classifications'],
    }}}, 'severity_levels': {}}
    # Neither required parent section present -> one missing_section error per parent (2).
    v = make_validator(cls=GDCValidator, doc_meta={'status': 'draft'}, content="## Introduction", rules=rules, filename='EAD-007-guideline.md')
    v.validate_type_specific()
    assert len(v.errors) == 2

    good_content = (
        "## Semantic Definitions\n"
        "### Naming Conventions\n### Taxonomy\n"
        "## Metadata Schema Properties\n"
        "### Allowed Lifecycle Statuses\n### Allowed Classifications\n"
    )
    v_good = make_validator(cls=GDCValidator, doc_meta={'status': 'draft'}, content=good_content, rules=rules, filename='EAD-007-guideline.md')
    v_good.validate_type_specific()
    assert len(v_good.errors) == 0

def test_gdc_missing_subsection():
    rules = {'rules': {'structure': {'required_downstream_guideline_subsections': {
        'Semantic Definitions': ['Naming Conventions', 'Taxonomy'],
        'Metadata Schema Properties': ['Allowed Lifecycle Statuses', 'Allowed Classifications'],
    }}}, 'severity_levels': {}}
    content = (
        "## Semantic Definitions\n### Naming Conventions\n"  # 'Taxonomy' missing
        "## Metadata Schema Properties\n### Allowed Lifecycle Statuses\n### Allowed Classifications\n"
    )
    v = make_validator(cls=GDCValidator, doc_meta={'status': 'draft'}, content=content, rules=rules, filename='EAD-007-guideline.md')
    v.validate_type_specific()
    assert any("missing mandatory subsection 'Taxonomy'" in m for _, m in v.errors)

def test_gdc_subsection_out_of_order():
    rules = {'rules': {'structure': {'required_downstream_guideline_subsections': {
        'Semantic Definitions': ['Naming Conventions', 'Taxonomy'],
        'Metadata Schema Properties': ['Allowed Lifecycle Statuses', 'Allowed Classifications'],
    }}}, 'severity_levels': {}}
    content = (
        "## Semantic Definitions\n### Taxonomy\n### Naming Conventions\n"  # reversed
        "## Metadata Schema Properties\n### Allowed Lifecycle Statuses\n### Allowed Classifications\n"
    )
    v = make_validator(cls=GDCValidator, doc_meta={'status': 'draft'}, content=content, rules=rules, filename='EAD-007-guideline.md')
    v.validate_type_specific()
    assert any('out of order' in m for _, m in v.errors)

def test_gdc_non_guideline_file_skipped():
    rules = {'rules': {'structure': {'required_downstream_guideline_subsections': {
        'Semantic Definitions': ['Naming Conventions', 'Taxonomy'],
    }}}, 'severity_levels': {}}
    v = make_validator(cls=GDCValidator, doc_meta={'status': 'draft'}, content="## Anything", rules=rules, filename='GDC-002-compliance-engine.md')
    v.validate_type_specific()
    assert len(v.errors) == 0


# ---------- EAD ----------

def test_ead_mandatory_sections_resolution():
    # dict branch: resolve by EAD id embedded in filename
    rules = {'rules': {'structure': {'required_sections': {
        'EAD-001': ['Business Capabilities'], 'EAD-002': ['Data Domains']}}}, 'severity_levels': {}}
    v = make_validator(cls=EADValidator, doc_meta={'id': 'EAD-001'}, rules=rules, filename='EAD-001-business.md')
    assert v.mandatory_sections == ['Business Capabilities']
    # no matching template -> fallback empty list
    v2 = make_validator(cls=EADValidator, doc_meta={'id': 'EAD-099'}, rules=rules, filename='EAD-099-other.md')
    assert v2.mandatory_sections == []
    # list branch: returned as-is
    rules2 = {'rules': {'structure': {'required_sections': ['A', 'B']}}, 'severity_levels': {}}
    v3 = make_validator(cls=EADValidator, doc_meta={}, rules=rules2, filename='EAD-001.md')
    assert v3.mandatory_sections == ['A', 'B']


# ---------- TDD ----------

def test_tdd_missing_parent_sad():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=TDDValidator, doc_meta={'status': 'draft'}, rules=rules, all_doc_ids={'SAD-001'}, filename='TDD-001.md')
    v.validate_type_specific()
    assert any('missing required traceability' in msg for sev, msg in v.errors)

def test_tdd_invalid_parent_sad():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=TDDValidator, doc_meta={'parent_sad': 'SAD-999'}, rules=rules, all_doc_ids={'SAD-001'}, filename='TDD-001.md')
    v.validate_type_specific()
    assert any('does not exist' in msg for sev, msg in v.errors)

def test_tdd_valid_parent_sad():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    v = make_validator(cls=TDDValidator, doc_meta={'parent_sad': 'SAD-001'}, rules=rules, all_doc_ids={'SAD-001'}, filename='TDD-001.md')
    v.validate_type_specific()
    assert len(v.errors) == 0


# ---------- Missing doc_meta for all validators ----------

def test_missing_doc_meta_for_all():
    rules = {'rules': {'metadata': {}}, 'severity_levels': {}}
    for cls, fname in [
        (ADRValidator, 'ADR-001.md'), (SADValidator, 'SAD-001.md'),
        (PADValidator, 'PAD-001.md'), (STDValidator, 'STD-001.md'),
        (GDCValidator, 'GDC-002.md'), (EADValidator, 'EAD-001.md'),
        (TDDValidator, 'TDD-001.md'),
    ]:
        v = make_validator(cls=cls, doc_meta={}, rules=rules, filename=fname)
        v.doc_meta = None  # Simulate truly missing metadata
        v.validate_type_specific()
        assert len(v.errors) == 0, f"{cls.__name__} should not crash on None doc_meta"
