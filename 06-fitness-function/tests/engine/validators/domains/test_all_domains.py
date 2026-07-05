from tests.conftest import make_validator
import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _global_rules():
    with open(
        os.path.join(ROOT, "00-governance", "schemas", "base.schema.json"),
        encoding="utf-8",
    ) as f:
        return json.load(f).get("x-engine-config", {})


from engine.validators.domains.adr_validator import ADRValidator
from engine.validators.domains.ead_validator import EADValidator
from engine.validators.domains.gdc_validator import GDCValidator
from engine.validators.domains.pad_validator import PADValidator
from engine.validators.domains.sad_validator import SADValidator
from engine.validators.domains.std_validator import STDValidator
from engine.validators.domains.tdd_validator import TDDValidator


def test_missing_doc_meta_for_all():
    rules = {"rules": {"metadata": {}}, "severity_levels": {}}
    for cls, fname in [
        (ADRValidator, "ADR-001.md"),
        (SADValidator, "SAD-001.md"),
        (PADValidator, "PAD-001.md"),
        (STDValidator, "STD-001.md"),
        (GDCValidator, "GDC-002.md"),
        (EADValidator, "EAD-001.md"),
        (TDDValidator, "TDD-001.md"),
    ]:
        v = make_validator(cls=cls, doc_meta={}, rules=rules, filename=fname)
        v.doc_meta = None  # Simulate truly missing metadata
        v.validate_type_specific()
        assert len(v.errors) == 0, f"{cls.__name__} should not crash on None doc_meta"
