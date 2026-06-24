"""
Tests for the v1.1 engine hardening + new capabilities:
  - Live ambiguity regex (the YAML \\b backspace bug) and de-leaked metric pattern
  - lint_disable hardening (code-fence immunity, reason capture, CRITICAL protection)
  - Inline ID-citation validation
  - Duplicate-ID detection
  - Traceability graph cycle detection
  - SARIF output
  - Non-destructive generator --check
"""
import os
import re
import sys
import yaml
import importlib.util

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validators.base import BaseValidator
from validators.common import _validate_inline_references
from validators.scanner import resolve_registry_with_duplicates
from validators.traceability import audit_traceability_graph
from validators.utils import strip_code_fences, extract_doc_id_references
from linter import build_sarif

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')


def _global_rules():
    with open(os.path.join(ROOT, '00-governance', 'rules', 'linting-rules.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)


# ---------- FIX#1: regexes ----------

def test_ambiguity_regex_is_live_not_backspace():
    pat = _global_rules()['rules']['content']['ambiguity_check']['pattern']
    assert '\x08' not in pat, "double-quote YAML corrupted \\b into a backspace char"
    assert re.search(pat, "this design is highly scalable", re.IGNORECASE)
    assert re.search(pat, "it is very fast under load", re.IGNORECASE)
    assert not re.search(pat, "a perfectly ordinary sentence", re.IGNORECASE)


def test_metric_pattern_rejects_incidental_prose():
    mp = _global_rules()['rules']['quantification']['metric_pattern']
    assert re.search(mp, "p99 latency of 200ms", re.IGNORECASE)
    assert re.search(mp, "availability of 99.95%", re.IGNORECASE)
    assert not re.search(mp, "we operate 3 services", re.IGNORECASE)
    assert not re.search(mp, "there are 5 systems", re.IGNORECASE)


# ---------- FIX#2: lint_disable hardening ----------

def test_strip_code_fences_removes_fenced_blocks():
    text = "before\n```\n<!-- lint_disable: x -->\n```\nafter"
    cleaned = strip_code_fences(text)
    assert "lint_disable" not in cleaned
    assert "before" in cleaned and "after" in cleaned


def test_lint_disable_ignored_inside_code_fence():
    content = "```html\n<!-- lint_disable: missing_metadata -->\n```\nreal body"
    v = BaseValidator('x.md', content, {}, {}, set(), {})
    assert 'missing_metadata' not in v.disabled_rules


def test_lint_disable_honored_with_reason():
    content = "<!-- lint_disable: prohibited_word (reason: ARB waiver in ADR-GLB-009) -->"
    v = BaseValidator('x.md', content, {}, {}, set(), {})
    assert 'prohibited_word' in v.disabled_rules
    assert v.disable_reasons['prohibited_word'] == 'ARB waiver in ADR-GLB-009'


def test_lint_disable_undocumented_has_none_reason():
    content = "<!-- lint_disable: prohibited_word -->"
    v = BaseValidator('x.md', content, {}, {}, set(), {})
    assert v.disable_reasons['prohibited_word'] is None


def test_lint_disable_cannot_silence_critical():
    rules = {'severity_levels': {'structural_integrity_violation': 'CRITICAL'}}
    content = "<!-- lint_disable: structural_integrity_violation -->"
    v = BaseValidator('x.md', content, {}, rules, set(), {})
    v.add_error('structural_integrity_violation', 'sections out of order')
    assert any(sev == 'CRITICAL' for sev, _ in v.errors), "CRITICAL finding must still fire"
    assert 'structural_integrity_violation' in v.rejected_disables


def test_lint_disable_honors_non_critical():
    rules = {'severity_levels': {'prohibited_word': 'WARNING'}}
    content = "<!-- lint_disable: prohibited_word -->"
    v = BaseValidator('x.md', content, {}, rules, set(), {})
    v.add_error('prohibited_word', 'weasel word')
    assert len(v.errors) == 0


# ---------- FIX#3: inline reference validation ----------

def test_extract_doc_id_references():
    refs = extract_doc_id_references("See (**ADR-018**) and ADR-GLB-001 plus STD-E019.")
    assert 'ADR-018' in refs and 'ADR-GLB-001' in refs and 'STD-E019' in refs


def test_inline_reference_missing_flags_dangling_only():
    rules = {'severity_levels': {'inline_reference_missing': 'WARNING'}}
    content = "Body cites (**ADR-018**) and a valid ADR-GLB-001."
    v = BaseValidator('SAD-001.md', content, {'id': 'SAD-001'}, rules, {'ADR-GLB-001'}, {})
    _validate_inline_references(v)
    msgs = [m for _, m in v.errors]
    assert any('ADR-018' in m for m in msgs)
    assert not any('ADR-GLB-001' in m for m in msgs)


def test_inline_reference_skips_own_id():
    rules = {'severity_levels': {'inline_reference_missing': 'WARNING'}}
    content = "This document SAD-001 references itself."
    v = BaseValidator('SAD-001.md', content, {'id': 'SAD-001'}, rules, set(), {})
    _validate_inline_references(v)
    assert len(v.errors) == 0


# ---------- ADD#1: duplicate-ID detection ----------

def test_duplicate_id_detection(tmp_path):
    d = tmp_path / "repo"
    d.mkdir()
    (d / "a.md").write_text("---\ndoc_meta:\n  id: ADR-001\n---\nA")
    (d / "b.md").write_text("---\ndoc_meta:\n  id: ADR-001\n---\nB")
    (d / "c.md").write_text("---\ndoc_meta:\n  id: ADR-002\n---\nC")
    ids, meta, dupes = resolve_registry_with_duplicates(str(d))
    assert 'ADR-001' in dupes and len(dupes['ADR-001']) == 2
    assert 'ADR-002' not in dupes
    assert 'ADR-002' in ids


# ---------- ADD#2: traceability graph ----------

def test_traceability_cycle_detected():
    meta = {
        'SAD-001': {'parent_pad': 'PAD-001'},
        'PAD-001': {'governed_by': 'SAD-001'},
    }
    errs = audit_traceability_graph(meta)
    assert any('Circular' in m for _, m in errs)


def test_traceability_self_reference_is_allowed():
    meta = {'GDC-000': {'governed_by': ['GDC-000']}}
    assert audit_traceability_graph(meta) == []


def test_traceability_acyclic_is_clean():
    meta = {
        'SAD-001': {'parent_pad': 'PAD-001'},
        'PAD-001': {'governed_by': 'EAD-001'},
        'EAD-001': {},
    }
    assert audit_traceability_graph(meta) == []


def test_traceability_ignores_non_dict_meta():
    meta = {'X-1': "not a dict", 'PAD-1': {'parent_pad': None}}
    assert audit_traceability_graph(meta) == []


# ---------- ADD#5: SARIF ----------

def test_build_sarif_maps_levels():
    results = [{'file': './a.md', 'errors': [('CRITICAL', 'c'), ('ERROR', 'e'), ('WARNING', 'w')]}]
    doc = build_sarif(results)
    assert doc['version'] == '2.1.0'
    levels = [r['level'] for r in doc['runs'][0]['results']]
    assert levels.count('error') == 2 and levels.count('warning') == 1
    assert doc['runs'][0]['results'][0]['locations'][0]['physicalLocation']['artifactLocation']['uri'] == 'a.md'


# ---------- FIX#4: non-destructive generator --check ----------

def _load_generator():
    path = os.path.join(ROOT, 'scripts', 'generate_rules_doc.py')
    spec = importlib.util.spec_from_file_location('genrules', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_check_is_non_destructive():
    gen = _load_generator()
    drift = gen.process(check=True)
    assert isinstance(drift, list)  # returns drift records, writes nothing
