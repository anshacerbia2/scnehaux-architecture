from engine.validators.registry import detect_doc_type, get_validator
from engine.validators.domains.adr_validator import ADRValidator
from engine.validators.domains.sad_validator import SADValidator


def test_detect_doc_type():
    assert detect_doc_type("ADR-001", "ADR-001-test.md", "") == "ADR"
    assert detect_doc_type(None, "scnehaux.sad.md", "") == "SAD"
    assert detect_doc_type(None, "scnehaux.pad.md", "") == "PAD"
    assert detect_doc_type("GDC-002", "GDC-002-test.md", "") == "GDC"
    assert detect_doc_type(None, "unknown.md", "") is None


def test_get_validator():
    assert get_validator("ADR") == ADRValidator
    assert get_validator("SAD") == SADValidator
    assert get_validator("UNKNOWN") is None
