import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validators.factory import detect_doc_type, get_validator
from validators.adr import ADRValidator
from validators.sad import SADValidator

def test_detect_doc_type():
    assert detect_doc_type('ADR-001', 'ADR-001-test.md', '') == 'ADR'
    assert detect_doc_type(None, 'scnehaux.sad.md', '') == 'SAD'
    assert detect_doc_type(None, 'scnehaux.pad.md', '') == 'PAD'
    assert detect_doc_type('GDC-001', 'GDC-001-test.md', '') == 'GDC'
    assert detect_doc_type(None, 'unknown.md', '') is None

def test_get_validator():
    assert get_validator('ADR') == ADRValidator
    assert get_validator('SAD') == SADValidator
    assert get_validator('UNKNOWN') is None
