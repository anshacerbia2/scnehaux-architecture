import sys
import os
import pytest
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pydantic import ValidationError
from validators.schema import DocMeta, ExceptionInfo

def test_docmeta_valid_minimal():
    meta = DocMeta(id="ADR-001")
    assert meta.id == "ADR-001"
    assert meta.version is None

def test_docmeta_valid_full():
    data = {
        "id": "ADR-001",
        "title": "Use PostgreSQL",
        "owner": "Data Team",
        "version": "1.2.3",
        "status": "proposed",
        "classification": "public",
        "review_cycle_days": 180,
        "last_reviewed": date(2026, 1, 1),
        "exception_info": {
            "approved_by": "John Doe",
            "expiry_date": date(2026, 12, 31),
            "risk_classification": "medium",
            "exception_reason": "Temporary bridge"
        },
        "parent_pad": "PAD-001",
        "parent_sad": ["SAD-001", "SAD-002"],
        "governed_by": "GDC-001",
        "fulfilled_by": "SAD-003",
        "adr_type": "exception"
    }
    meta = DocMeta(**data)
    assert meta.id == "ADR-001"
    assert meta.version == "1.2.3"
    assert meta.status == "proposed"
    assert meta.parent_sad == ["SAD-001", "SAD-002"]
    assert isinstance(meta.exception_info, ExceptionInfo)

def test_docmeta_invalid_semver():
    with pytest.raises(ValidationError) as exc_info:
        DocMeta(version="1.0")
    assert "not in valid semver format" in str(exc_info.value)

def test_docmeta_invalid_status():
    with pytest.raises(ValidationError):
        DocMeta(status="invalid_status")

def test_docmeta_invalid_classification():
    with pytest.raises(ValidationError):
        DocMeta(classification="top_secret")

def test_exceptioninfo_missing_fields():
    data = {
        "approved_by": "John Doe",
        # missing expiry_date
        "risk_classification": "medium",
        "exception_reason": "Temporary bridge"
    }
    with pytest.raises(ValidationError):
        ExceptionInfo(**data)

def test_docmeta_version_none():
    meta = DocMeta(id="ADR-001", version=None)
    assert meta.version is None
