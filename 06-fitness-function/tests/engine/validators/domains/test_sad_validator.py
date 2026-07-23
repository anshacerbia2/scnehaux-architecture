from tests.conftest import make_validator
import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _global_rules():
    with open(
        os.path.join(ROOT, "00-governance", "schemas", "base.schema.json"),
        encoding="utf-8",
    ) as f:
        return json.load(f).get("x-global-config", {})


from engine.validators.domains.sad_validator import SADValidator


def test_sad_missing_parent_pad():
    rules = {"rules": {"metadata": {}}, "severity_levels": {}}
    v = make_validator(
        cls=SADValidator,
        doc_meta={"status": "draft"},
        rules=rules,
        filename="SAD-001.md",
    )
    v.validate_type_specific()
    assert any("missing required traceability" in msg for sev, msg in v.errors)


def test_sad_invalid_parent_pad():
    rules = {"rules": {"metadata": {}}, "severity_levels": {}}
    v = make_validator(
        cls=SADValidator,
        doc_meta={"parent_pad": "PAD-999"},
        rules=rules,
        all_doc_ids={"PAD-001"},
        filename="SAD-001.md",
    )
    v.validate_type_specific()
    assert any("does not exist" in msg for sev, msg in v.errors)


def test_sad_bidirectional_traceability_fail():
    rules = {"rules": {"metadata": {}}, "severity_levels": {}}
    v = make_validator(
        cls=SADValidator,
        doc_meta={"id": "SAD-001", "parent_pad": "PAD-001"},
        rules=rules,
        all_doc_ids={"PAD-001"},
        all_doc_metadata={"PAD-001": {"fulfilled_by": ["SAD-999"]}},
        filename="SAD-001.md",
    )
    v.validate_type_specific()
    assert any("Bidirectional traceability is broken" in msg for sev, msg in v.errors)


def test_sad_bidirectional_traceability_pass():
    rules = {"rules": {"metadata": {}}, "severity_levels": {}}
    v = make_validator(
        cls=SADValidator,
        doc_meta={"id": "SAD-001", "parent_pad": "PAD-001"},
        rules=rules,
        all_doc_ids={"PAD-001"},
        all_doc_metadata={"PAD-001": {"fulfilled_by": ["SAD-001"]}},
        filename="SAD-001.md",
    )
    v.validate_type_specific()
    assert len(v.errors) == 0


# ---------- PAD ----------
